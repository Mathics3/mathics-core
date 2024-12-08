# -*- coding: utf-8 -*-

"""
File and Stream Operations
"""

import io
import os.path as osp
import tempfile
from io import BytesIO

# We use the below import for access to variables that may change
# at runtime.
import mathics.eval.files_io.files as io_files
from mathics.core.atoms import Integer, String, SymbolString
from mathics.core.attributes import A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import (
    Builtin,
    InfixOperator,
    MessageException,
    Predefined,
    PrefixOperator,
)
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import BoxError, Expression
from mathics.core.list import ListExpression
from mathics.core.streams import Stream, path_search, stream_manager
from mathics.core.symbols import Symbol, SymbolFullForm, SymbolNull, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolEndOfFile,
    SymbolExpression,
    SymbolFailed,
    SymbolHold,
    SymbolHoldExpression,
    SymbolInputForm,
    SymbolInputStream,
    SymbolOutputForm,
    SymbolOutputStream,
)
from mathics.eval.directories import TMP_DIR
from mathics.eval.files_io.files import eval_Get, eval_Read
from mathics.eval.files_io.read import (
    MathicsOpen,
    channel_to_stream,
    close_stream,
    parse_read_options,
    read_name_and_stream,
)
from mathics.eval.makeboxes import do_format, format_element


class Input_(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/$Input.html</url>

    <dl>
      <dt>'$Input'
      <dd>is the name of the stream from which input is currently being read.
    </dl>

    >> $Input
     = #<--#
    """

    attributes = A_PROTECTED | A_READ_PROTECTED
    name = "$Input"
    summary_text = "the name of the current input stream"

    def evaluate(self, evaluation: Evaluation) -> String:
        return String(io_files.INPUT_VAR)


class _OpenAction(Builtin):
    # BinaryFormat: 'False',
    # CharacterEncoding :> Automatic,
    # DOSTextFormat :> True,
    # FormatType -> InputForm,
    # NumberMarks :> $NumberMarks,
    # PageHeight -> 22, PageWidth -> 78,
    # TotalHeight -> Infinity,
    # TotalWidth -> Infinity

    options = {
        "BinaryFormat": "False",
        "CharacterEncoding": "$CharacterEncoding",
    }

    messages = {
        "argx": "OpenRead called with 0 arguments; 1 argument is expected.",
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
    }

    mode = "r"  # A default; this is changed in subclassing.

    def eval_empty(self, evaluation: Evaluation, options: dict):
        "%(name)s[OptionsPattern[]]"

        if isinstance(self, (OpenWrite, OpenAppend)):
            # We use delete=False because we write to the name *after*
            # tfms.close() is done. In other words we are using
            # NamedTempararyFile to get a unique name and ensure that
            # no one else uses it.
            # In Close[] we will explicitly remove the name from the
            # filesystem.
            tmpf = tempfile.NamedTemporaryFile(dir=TMP_DIR, delete=False)
            path = String(tmpf.name)
            tmpf.close()
            return self.eval_name(path, evaluation, options)
        else:
            evaluation.message("OpenRead", "argx")
            return

    def eval_name(self, name, evaluation: Evaluation, options: dict):
        "%(name)s[name_?NotOptionQ, OptionsPattern[]]"

        # Options
        # BinaryFormat
        mode = self.mode
        if options["System`BinaryFormat"] is SymbolTrue:
            if not self.mode.endswith("b"):
                mode += "b"

        if not (isinstance(name, String) and len(name.to_python()) > 2):
            evaluation.message(self.__class__.__name__, "fstr", name)
            return

        name_string = name.get_string_value()

        tmp, is_temporary_file = path_search(name_string)
        if tmp is None:
            if mode in ["r", "rb"]:
                evaluation.message("General", "noopen", name)
                return
            path_string = name_string
        else:
            path_string = tmp

        try:
            encoding = self.get_option(options, "CharacterEncoding", evaluation)
            if not isinstance(encoding, String):
                return

            opener = MathicsOpen(
                path_string,
                mode=mode,
                name=name_string,
                encoding=encoding.value,
                is_temporary_file=is_temporary_file,
            )
            opener.__enter__(is_temporary_file=is_temporary_file)
            n = opener.n
        except IOError:
            evaluation.message("General", "noopen", name)
            return
        except MessageException as e:
            e.message(evaluation)
            return

        return Expression(Symbol(self.stream_type), name, Integer(n))


class Character(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Character.html</url>

    <dl>
      <dt>'Character'
      <dd>is a data type for 'Read'.
    </dl>
    """

    summary_text = "single character, returned as a one‐character string"


class Close(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Close.html</url>

    <dl>
      <dt>'Close[$stream$]'
      <dd>closes an input or output stream.
    </dl>

    >> Close[StringToStream["123abc"]]
     = String

    >> file=Close[OpenWrite[]]
     = ...

    Closing a file doesn't delete it from the filesystem
    >> DeleteFile[file];

    #> Clear[file]
    """

    summary_text = "close a stream"
    messages = {
        "closex": "`1`.",
    }

    def eval(self, channel, evaluation: Evaluation):
        "Close[channel_]"

        n = name = None
        if channel.has_form(("InputStream", "OutputStream"), 2):
            [name, n] = channel.elements
            py_n = n.get_int_value()
            stream = stream_manager.lookup_stream(py_n)
        else:
            stream = None

        if stream is None or stream.io is None or stream.io.closed:
            evaluation.message("General", "openx", channel)
            return

        close_stream(stream, n.value)
        return name


class EndOfFile(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/EndOfFile.html</url>

    <dl>
      <dt>'EndOfFile'
      <dd>is returned by 'Read' when the end of an input stream is reached.
    </dl>
    """

    summary_text = "end of the file"


class Expression_(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Expression.html</url>

    <dl>
      <dt>'Expression'
      <dd>is a data type for 'Read'.
    </dl>

    For information about underlying data structure Expression (a kind of \
    M-expression) that is central in evaluation, see: \
    <url>
    :AST, M-Expression, General List same thing:
    https://mathics-development-guide.readthedocs.io/en/latest/extending/code-overview/ast.html</url>.
    """

    name = "Expression"
    summary_text = "WL expression"


class FilePrint(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/FilePrint.html</url>

    <dl>
      <dt>'FilePrint[$file$]'
      <dd>prints the raw contents of $file$.
    </dl>

    """

    messages = {
        "fstr": (
            "File specification `1` is not a string of " "one or more characters."
        ),
    }

    options = {
        "CharacterEncoding": "$CharacterEncoding",
        "RecordSeparators": '{"\r\n", "\n", "\r"}',
        "WordSeparators": '{" ", "\t"}',
    }
    summary_text = "display the contents of a file"

    def eval(self, path, evaluation: Evaluation, options: dict):
        "FilePrint[path_, OptionsPattern[FilePrint]]"
        pypath = path.to_python()
        if not (
            isinstance(pypath, str)
            and pypath[0] == pypath[-1] == '"'
            and len(pypath) > 2
        ):
            evaluation.message("FilePrint", "fstr", path)
            return
        pypath, _ = path_search(pypath[1:-1])

        # Options
        record_separators = options["System`RecordSeparators"].to_python()
        assert isinstance(record_separators, list)
        assert all(
            isinstance(s, str) and s[0] == s[-1] == '"' for s in record_separators
        )
        record_separators = [s[1:-1] for s in record_separators]

        if pypath is None:
            evaluation.message("General", "noopen", path)
            return

        if not osp.isfile(pypath):
            return SymbolFailed

        try:
            with MathicsOpen(pypath, "r") as f:
                result = f.read()
        except IOError:
            evaluation.message("General", "noopen", path)
            return
        except MessageException as e:
            e.message(evaluation)
            return

        result = [result]
        for sep in record_separators:
            result = [item for res in result for item in res.split(sep)]

        if result[-1] == "":
            result = result[:-1]

        for res in result:
            evaluation.print_out(String(res))

        return SymbolNull


class Get(PrefixOperator):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/Get.html</url>

    <dl>
      <dt>'<<$name$'
      <dd>reads a file and evaluates each expression, returning only the last one.

      <dt>'Get[$name$, Trace->True]'
      <dd>Runs Get tracing each line before it is evaluated.

     'Settings`$TraceGet' can be also used to trace lines on all 'Get[]' calls.
    </dl>


    S> filename = $TemporaryDirectory <> "/example_file";
    S> Put[x + y, filename]
    S> Get[filename]
     = x + y

    S> filename = $TemporaryDirectory <> "/example_file";
    S> Put[x + y, 2x^2 + 4z!, Cos[x] + I Sin[x], filename]
    S> Get[filename]
     = Cos[x] + I Sin[x]
    S> DeleteFile[filename]

    ## TODO: Requires EndPackage implemented
    ## 'Get' can also load packages:
    ## >> << "VectorAnalysis`"
    """

    operator = "<<"
    options = {
        "Trace": "False",
    }
    summary_text = "read in a file and evaluate commands in it"

    def eval(self, path: String, evaluation: Evaluation, options: dict):
        "Get[path_String, OptionsPattern[Get]]"

        # Make sure to pick up copy from module each time instead of using
        # use "from ... import DEFAULT_TRACE_FN" which will not pick
        # up run-time changes made to the module function.
        trace_fn = io_files.DEFAULT_TRACE_FN

        trace_get = evaluation.parse("Settings`$TraceGet")
        if (
            options["System`Trace"].to_python()
            or trace_get.evaluate(evaluation) is SymbolTrue
        ):
            trace_fn = io_files.GET_PRINT_FN

        # perform the actual evaluation
        return eval_Get(path.value, evaluation, trace_fn)


class InputFileName_(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/$InputFileName.html</url>

    <dl>
      <dt>'$InputFileName'
      <dd>is the name of the file from which input is currently being read.
    </dl>

    While in interactive mode, '$InputFileName' is "".
    X> $InputFileName
    """

    summary_text = (
        "the full absolute path to the file from which input is currently being sought"
    )
    name = "$InputFileName"

    def evaluate(self, evaluation):
        return String(evaluation.definitions.get_inputfile())


class InputStream(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/InputStream.html</url>

    <dl>
      <dt>'InputStream[$name$, $n$]'
      <dd>represents an input stream for functions such as 'Read' or 'Find'.
    </dl>

    'StringToStream' opens an input stream:

    >> stream = StringToStream["Mathics is cool!"]
     = ...
    >> Close[stream]
     = String
    """

    messages = {
        "intpm": "Positive machine-sized integer expected at position 2 of `1`",
    }
    summary_text = "an input stream"


class Number_(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Number.html</url>

    <dl>
    <dt>'Number'
      <dd>is a data type for 'Read'.
    </dl>
    """

    name = "Number"
    summary_text = "exact or approximate number in Fortran‐like notation"


class OpenRead(_OpenAction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/OpenRead.html</url>

    <dl>
      <dt>'OpenRead["file"]'
      <dd>opens a file and returns an 'InputStream'.
    </dl>

    >> OpenRead["ExampleData/EinsteinSzilLetter.txt", CharacterEncoding->"UTF8"]
     = InputStream[...]

    The stream must be closed after using it to release the resource:
    >> Close[%];
    """

    summary_text = "open a file for reading"
    mode = "r"
    stream_type = "InputStream"


class OpenWrite(_OpenAction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/OpenWrite.html</url>

    <dl>
      <dt>'OpenWrite["file"]'
      <dd>opens a file and returns an OutputStream.
    </dl>

    >> OpenWrite[]
     = OutputStream[...]
    >> DeleteFile[Close[%]];
    """

    summary_text = (
        "send an output stream to a file, wiping out the previous contents of the file"
    )
    mode = "w"
    stream_type = "OutputStream"


class OpenAppend(_OpenAction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/OpenAppend.html</url>

    <dl>
    <dt>'OpenAppend["file"]'
      <dd>opens a file and returns an OutputStream to which writes are appended.
    </dl>

    >> OpenAppend[]
     = OutputStream[...]
    >> DeleteFile[Close[%]];

    """

    mode = "a"
    stream_type = "OutputStream"
    summary_text = (
        "open an output stream to a file, appending to what was already in the file"
    )


class Put(InfixOperator):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Put.html</url>

    <dl>
      <dt>'$expr$ >> $filename$'
      <dd>write $expr$ to a file.
    <dt>'Put[$expr1$, $expr2$, ..., $filename$]'
      <dd>write a sequence of expressions to a file.
    </dl>

    ## Note a lot of these tests are:
    ## * a bit fragile, somewhat
    ## * somewhat OS dependent,
    ## * can leave crap in the filesystem
    ## * put in a pytest
    ##
    ## For these reasons this should be done a a pure test
    ## rather than intermingled with the doc system.

    S> Put[40!, fortyfactorial]
     : fortyfactorial is not string, InputStream[], or OutputStream[]
     = 815915283247897734345611269596115894272000000000 >> fortyfactorial
    ## FIXME: final line should be
    ## = Put[815915283247897734345611269596115894272000000000, fortyfactorial]

    S> filename = $TemporaryDirectory <> "/fortyfactorial";
    S> Put[40!, filename]
    S> FilePrint[filename]
     | 815915283247897734345611269596115894272000000000
    S> Get[filename]
     = 815915283247897734345611269596115894272000000000
    S> DeleteFile[filename]

    S> filename = $TemporaryDirectory <> "/fiftyfactorial";
    S> Put[10!, 20!, 30!, filename]
    S> FilePrint[filename]
     | 3628800
     | 2432902008176640000
     | 265252859812191058636308480000000

    S> DeleteFile[filename]
     =

    S> filename = $TemporaryDirectory <> "/example_file";
    S> Put[x + y, 2x^2 + 4z!, Cos[x] + I Sin[x], filename]
    S> FilePrint[filename]
     | x + y
     | 2*x^2 + 4*z!
     | Cos[x] + I*Sin[x]
    S> DeleteFile[filename]
    """

    operator = ">>"
    summary_text = "write an expression to a file"

    def eval(self, exprs, filename, evaluation):
        "Put[exprs___, filename_String]"
        instream = to_expression("OpenWrite", filename).evaluate(evaluation)
        if len(instream.elements) == 2:
            name, n = instream.elements
        else:
            return  # opening failed
        result = self.eval_input(exprs, name, n, evaluation)
        instream_number = instream.elements[1].value
        py_instream = stream_manager.lookup_stream(instream_number)

        close_stream(py_instream, instream_number)
        return result

    def eval_input(self, exprs, name, n, evaluation):
        "Put[exprs___, OutputStream[name_, n_]]"
        stream = stream_manager.lookup_stream(n.get_int_value())

        if stream is None or stream.io.closed:
            evaluation.message("Put", "openx", to_expression("OutputSteam", name, n))
            return

        # In Mathics-server, evaluation.format_output is modified.
        # Let's avoid to use it if we want a front-end independent result.
        # Eventually, we are going to replace this by a `MakeBoxes` call.
        def do_format_output(expr, evaluation):
            try:
                boxed_expr = format_element(expr, evaluation, SymbolInputForm)
            except BoxError:
                boxed_expr = format_element(expr, evaluation, SymbolFullForm)

            return boxed_expr.boxes_to_text()

        text = [do_format_output(expr, evaluation) for expr in exprs.get_sequence()]
        text = "\n".join(text) + "\n"
        text.encode("utf-8")

        stream.io.write(text)

        return SymbolNull

    def eval_default(self, exprs, filename, evaluation):
        "Put[exprs___, filename_]"
        expr = to_expression("Put", exprs, filename)
        evaluation.message("Put", "stream", filename)
        return expr


class PutAppend(InfixOperator):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/PutAppend.html</url>

    <dl>
      <dt>'$expr$ >>> $filename$'
      <dd>append $expr$ to a file.

      <dt>'PutAppend[$expr1$, $expr2$, ..., $"filename"$]'
      <dd>write a sequence of expressions to a file.
    </dl>

    >> Put[50!, "factorials"]
    >> FilePrint["factorials"]
     | 30414093201713378043612608166064768844377641568960512000000000000

    >> PutAppend[10!, 20!, 30!, "factorials"]
    >> FilePrint["factorials"]
     | 30414093201713378043612608166064768844377641568960512000000000000
     | 3628800
     | 2432902008176640000
     | 265252859812191058636308480000000

    >> 60! >>> "factorials"
    >> FilePrint["factorials"]
     | 30414093201713378043612608166064768844377641568960512000000000000
     | 3628800
     | 2432902008176640000
     | 265252859812191058636308480000000
     | 8320987112741390144276341183223364380754172606361245952449277696409600000000000000

    >> "string" >>> factorials
    >> FilePrint["factorials"]
     | 30414093201713378043612608166064768844377641568960512000000000000
     | 3628800
     | 2432902008176640000
     | 265252859812191058636308480000000
     | 8320987112741390144276341183223364380754172606361245952449277696409600000000000000
     | "string"
    >> DeleteFile["factorials"];
    """

    operator = ">>>"
    summary_text = "append an expression to a file"

    def eval(self, exprs, filename, evaluation):
        "PutAppend[exprs___, filename_String]"
        instream = to_expression("OpenAppend", filename).evaluate(evaluation)
        if len(instream.elements) == 2:
            name, n = instream.elements
        else:
            return  # opening failed
        result = self.eval_input(exprs, name, n, evaluation)
        to_expression("Close", instream).evaluate(evaluation)
        return result

    def eval_input(self, exprs, name, n, evaluation):
        "PutAppend[exprs___, OutputStream[name_, n_]]"
        stream = stream_manager.lookup_stream(n.get_int_value())

        if stream is None or stream.io.closed:
            evaluation.message("Put", "openx", to_expression("OutputSteam", name, n))
            return

        text = [
            str(do_format(e, evaluation, SymbolOutputForm).__str__())
            for e in exprs.get_sequence()
        ]
        text = "\n".join(text) + "\n"
        text.encode("ascii")

        stream.io.write(text)

        return SymbolNull

    def eval_default(self, exprs, filename, evaluation):
        "PutAppend[exprs___, filename_]"
        expr = to_expression("PutAppend", exprs, filename)
        evaluation.message("PutAppend", "stream", filename)
        return expr


def validate_read_type(name: str, typ, evaluation: Evaluation):
    """
    Validate a Read option type, and give a message if
    the type is invalid. For Expession[Hold], we convert it to
    SymbolHoldExpression, String names are like "Byte" are
    converted to Symbols in the return.
    """
    if hasattr(typ, "head") and typ.head == SymbolHold:
        if not hasattr(typ, "elements"):
            evaluation.message(name, "readf", typ)
            return None

        if typ.elements[0] != SymbolExpression:
            evaluation.message(name, "readf", typ.elements[0])
            return None

        return SymbolHoldExpression

    if isinstance(typ, String):
        typ = Symbol(typ.value)
    elif not isinstance(typ, Symbol):
        evaluation.message(name, "readf", typ)
        return None

    if typ.short_name not in (
        "Byte",
        "Character",
        "Expression",
        "Number",
        "Real",
        "Record",
        "String",
        "Word",
    ):
        evaluation.message(name, "readf", typ)
        return None

    return typ


class Read(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Read.html</url>

    <dl>
      <dt>'Read[$stream$]'
      <dd>reads the input stream and returns one expression.

      <dt>'Read[$stream$, $type$]'
      <dd>reads the input stream and returns an object of the given type.

      <dt>'Read[$stream$, $type$]'
      <dd>reads the input stream and returns an object of the given type.

      <dt>'Read[$stream$, Hold[Expression]]'
      <dd>reads the input stream for an Expression and puts it inside 'Hold'.

    </dl>

    $type$ is one of:
    <ul>
      <li>Byte
      <li>Character
      <li>Expression
      <li>HoldExpression
      <li>Number
      <li>Real
      <li>Record
      <li>String
      <li>Word
    </ul>


    ## Reading Strings
    >> stream = StringToStream["abc123"];
    >> Read[stream, String]
     = abc123
    >> Read[stream, String]
     = EndOfFile
    #> Close[stream];

    ## Reading Words
    >> stream = StringToStream["abc 123"];
    >> Read[stream, Word]
     = abc
    >> Read[stream, Word]
     = 123
    >> Read[stream, Word]
     = EndOfFile
    #> Close[stream];
    ## Number
    >> stream = StringToStream["123, 4"];
    >> Read[stream, Number]
     = 123
    >> Read[stream, Number]
     = 4
    >> Read[stream, Number]
     = EndOfFile
    #> Close[stream];


    ## HoldExpression:
    >> stream = StringToStream["2+2\\n2+3"];

    'Read' with a 'Hold[Expression]' returns the expression it reads unevaluated so it can be later inspected and evaluated:

    >> Read[stream, Hold[Expression]]
     = Hold[2 + 2]

    >> Read[stream, Expression]
     = 5
    #> Close[stream];

    Reading a comment, a non-expression, will return 'Hold[Null]'
    >> stream = StringToStream["(* ::Package:: *)"];

    >> Read[stream, Hold[Expression]]
     = Hold[Null]

    #> Close[stream];

    ## Multiple types
    >> stream = StringToStream["123 abc"];
    >> Read[stream, {Number, Word}]
     = {123, abc}
    >> Read[stream, {Number, Word}]
     = EndOfFile
    #> Close[stream];

    Multiple lines:
    >> stream = StringToStream["\\"Tengo una\\nvaca lechera.\\""]; Read[stream]
     = Tengo una
     . vaca lechera.

    """

    messages = {
        "openx": "`1` is not open.",
        "noopen": "Cannot open `1`.",
        "readf": "`1` is not a valid format specification.",
        "readn": "Invalid real number found when reading from `1`.",
        "readt": "Invalid input found when reading `1` from `2`.",
    }

    rules = {
        "Read[stream_]": "Read[stream, Expression]",
    }

    options = {
        "NullRecords": "False",
        "NullWords": "False",
        "RecordSeparators": '{"\r\n", "\n", "\r"}',
        "TokenWords": "{}",
        "WordSeparators": '{" ", "\t"}',
    }
    summary_text = "read an object of the specified type from a stream"

    def eval(self, stream, types, evaluation: Evaluation, options: dict):
        "Read[stream_, types_, OptionsPattern[Read]]"

        # FIXME: we don't handle SocketObjects yet?
        if isinstance(stream, Expression) and stream.head is SymbolInputStream:
            is_valid_stream = True
        else:
            is_valid_stream = isinstance(stream, (String, InputStream))

        if not is_valid_stream:
            evaluation.message("Read", "stream", stream)
            return

        name, n, stream = read_name_and_stream(stream, evaluation)

        if name is None:
            return
        elif name == SymbolFailed:
            return SymbolFailed

        # FIXME: DRY better with ReadList[].
        # Validate types parameter and store the
        # result into tuple checked_types.
        if isinstance(types, ListExpression):
            checked_types = []  # will be converted to tuple at the end
            for typ in types:
                new_type = validate_read_type("Read", typ, evaluation)
                if new_type is None:
                    return
                checked_types.append(new_type)
            checked_types = tuple(checked_types)
        else:
            new_type = validate_read_type("Read", types, evaluation)
            if new_type is None:
                return
            checked_types = (new_type,)

        result = eval_Read("Read", n, checked_types, stream, evaluation, options)
        if isinstance(result, list):
            if isinstance(types, ListExpression):
                assert len(result) == len(
                    types.elements
                ), "internal error: eval_Read() should have a return for each type"
            else:
                assert (
                    len(result) == 1
                ), f"internal error: eval_Read() should return at most 1 element; got {result}"
                return result[0]

        return from_python(result)


class ReadList(Read):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ReadList.html</url>

    <dl>
      <dt>'ReadList["$file$"]'
      <dd>Reads all the expressions until the end of file.

      <dt>'ReadList["$file$", $type$]'
      <dd>Reads objects of a specified type until the end of file.

      <dt>'ReadList["$file$", {$type1$, $type2$, ...}]'
      <dd>Reads a sequence of specified types until the end of file.
    </dl>

    To read all the numbers in a file and return a list of them:
    >> ReadList["ExampleData/numbers.txt", Number]
     = {11.1, 22.2, 33.3, 44.4, 55.5, 66.6}

    (Use <url>:'FilePrint[]':
    /doc/reference-of-built-in-symbols/inputoutput-files-and-filesystem/file-and-stream-operations/fileprint/</url>\
    to get the raw data for the examples above and below.)

    This does the same, but groups the numbers in to a pairs:
    >> ReadList["ExampleData/numbers.txt", {Number, Number}]
     = {{11.1, 22.2}, {33.3, 44.4}, {55.5, 66.6}}

    Now let us read and put blocks of 3 numbers in its own list:
    >> ReadList["ExampleData/numbers.txt", Table[Number, {3}]]
     = {{11.1, 22.2, 33.3}, {44.4, 55.5, 66.6}}

    ## 'ReadList' can handle number using Fortan-like "E" notation:
    ## >> ReadList["ExampleData/bignum.txt", Number]
    ## == {{0.000045, 78000, 250, -8.9}}

    Like <url>:'Read[]':
    /doc/reference-of-built-in-symbols/inputoutput-files-and-filesystem/file-and-stream-operations/read/</url>, \
      'ReadList' handles types of objects other than numbers.
    We can read a list of characters in a file putting each character as an item in a list:

    >> ReadList["ExampleData/strings.txt", Character]
     = ...

    And now, here are the integer codes corresponding to each of the bytes in the file:
    >> ReadList["ExampleData/strings.txt", Byte]
     = {72, 101, 114, 101, 32, 105, 115, 32, 116, 101, 120, 116, 46, 10, 65, 110, 100, 32, 109, 111, 114, 101, 32, 116, 101, 120, 116, 46, 10}

    But the data can also be read by "words":

    >> ReadList["ExampleData/strings.txt", Word]
     = {Here, is, text., And, more, text.}

    The above uses the default value which is space of some sort., However you can \
    set your own value:

    >> ReadList["ExampleData/strings.txt", Word, WordSeparators -> {"e", "."}]
     = {H, r,  is t, xt, And mor,  t, xt}

    See <url>
    :WordSeparators:
    https://reference.wolfram.com/language/ref/WordSeprators.html</url> \
    for more information.

    Reading by records uses the separators found in
    >> ReadList["ExampleData/strings.txt", Record]
     = {Here is text., And more text.}

    See <url>
    :RecordSeparators:
    https://reference.wolfram.com/language/ref/RecordSeprators.html</url> \
    works analgously for records as 'WordSeparators' does for words.

    To allow both periods and newlines as record separators:

    >> ReadList["ExampleData/sentences.txt", Record, RecordSeparators -> {".", "\\n"}]
    = {Here is text,  And more, And a second line}

    See also <url>
    :Reading Textual Data:
      https://reference.wolfram.com/language/tutorial/FilesStreamsAndExternalOperations.html#3333</url>.
    """

    # TODO
    """
    #> ReadList[StringToStream["a 1 b 2"], {Word, Number}, -1]
     : Non-negative machine-sized integer expected at position 3 in ReadList[InputStream[String, ...], {Word, Number}, -1].
     = ReadList[InputStream[String, ...], {Word, Number}, -1]
    """

    # TODO: Expression type
    """
    #> ReadList[StringToStream["123 45 x y"], Expression]
     = {5535 x y}
    """

    # TODO: Accept newlines in input
    """
    >> ReadList[StringToStream["123\nabc"]]
     = {123, abc}
    >> InputForm[%]
     = {123, abc}
    """
    messages = {
        "opstl": "Value of option `1` should be a string or a list of strings.",
        "readf": "`1` is not a valid format specification.",
    }
    options = {
        "NullRecords": "False",
        "NullWords": "False",
        "RecordSeparators": '{"\r\n", "\n", "\r"}',
        "TokenWords": "{}",
        "WordSeparators": '{" ", "\t"}',
    }
    rules = {
        "ReadList[stream_]": "ReadList[stream, Expression]",
    }
    summary_text = "read a sequence of elements from a file, and put them in a WL list"

    def eval(self, file, types, evaluation: Evaluation, options: dict):
        "ReadList[file_, types_, OptionsPattern[ReadList]]"

        py_options = parse_read_options(options)
        # Options
        # TODO: Implement extra options
        # null_records = py_options['NullRecords']
        # null_words = py_options['NullWords']
        # record_separators = py_options['RecordSeparators']
        # token_words = py_options['TokenWords']
        # word_separators = py_options['WordSeparators']

        result = []

        # FIXME: DRY better with Read[].
        # Validate types parameter and store the
        # result into tuple checked_types.
        if isinstance(types, ListExpression):
            checked_types = []  # will be converted to tuple at the end
            for typ in types:
                new_type = validate_read_type("ReadList", typ, evaluation)
                if new_type is None:
                    return
                checked_types.append(new_type)
            checked_types = tuple(checked_types)
        else:
            new_type = validate_read_type("ReadList", types, evaluation)
            if new_type is None:
                return
            checked_types = (new_type,)

        name, n, stream = read_name_and_stream(file, evaluation)

        if name is None:
            return
        elif name == SymbolFailed:
            return SymbolFailed

        while True:
            next_elt = eval_Read(
                "ReadList", n, checked_types, stream, evaluation, options
            )

            if next_elt is None:
                return

            if next_elt is SymbolFailed:
                return

            if next_elt is SymbolEndOfFile:
                break

            if isinstance(next_elt, list) and py_options["TokenWords"]:
                # FIXME: This might not be correct in all cases.
                # we probably need a more positive way to indicate whether next_elt
                # was returned from TokenWord parsing or not.
                result += next_elt
            else:
                result.append(next_elt)
        return from_python(result)

    def eval_n(self, file, types, n: Integer, evaluation: Evaluation, options: dict):
        "ReadList[file_, types_, n_Integer, OptionsPattern[ReadList]]"

        # Options
        # TODO: Implement extra options
        # py_options = parse_read_options(options)
        # null_records = py_options['NullRecords']
        # null_words = py_options['NullWords']
        # record_separators = py_options['RecordSeparators']
        # token_words = py_options['TokenWords']
        # word_separators = py_options['WordSeparators']

        py_n = n.get_int_value()
        if py_n < 0:
            evaluation.message(
                "ReadList", "intnm", to_expression("ReadList", file, types, m)
            )
            return

        result = []
        for i in range(py_n):
            tmp = super(ReadList, self).eval(file, types, evaluation, options)

            if tmp is SymbolFailed:
                return

            if tmp.to_python() == "EndOfFile":
                break
            result.append(tmp)
        return from_python(result)


class StreamPosition(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/StreamPosition.html</url>

    <dl>
      <dt>'StreamPosition[$stream$]'
      <dd>returns the current position in a stream as an integer.
    </dl>

    >> stream = StringToStream["Mathics is cool!"]
     = ...

    >> Read[stream, Word]
     = Mathics

    >> StreamPosition[stream]
     = 7
    """

    summary_text = "find the position of the current point in an open stream"

    def eval_input(self, name, n, evaluation):
        "StreamPosition[InputStream[name_, n_]]"
        stream = stream_manager.lookup_stream(n.get_int_value())

        if stream is None or stream.io is None or stream.io.closed:
            evaluation.message("General", "openx", name)
            return

        return Integer(stream.io.tell())

    def eval_output(self, name, n, evaluation):
        "StreamPosition[OutputStream[name_, n_]]"
        self.input_apply(name, n, evaluation)

    def eval_default(self, stream, evaluation):
        "StreamPosition[stream_]"
        evaluation.message("General", "stream", stream)
        return


class SetStreamPosition(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SetStreamPosition.html</url>

    <dl>
    <dt>'SetStreamPosition[$stream$, $n$]'
      <dd>sets the current position in a stream.
    </dl>

    >> stream = StringToStream["Mathics is cool!"]
     = ...

    >> SetStreamPosition[stream, 8]
     = 8

    >> Read[stream, Word]
     = is

    >> SetStreamPosition[stream, Infinity]
     = 16
    """

    # TODO: Seeks beyond stream should return stmrng message
    """
    #> SetStreamPosition[stream, 40]
     = ERROR_MESSAGE_HERE
    """
    messages = {
        "int": "Integer expected at position 2 in `1`.",
        "stmrng": (
            "Cannot set the current point in stream `1` to position `2`. The "
            "requested position exceeds the number of characters in the file"
        ),
        "seek": "Invalid I/O Seek.",
    }
    summary_text = "set the position of the current point in an open stream"

    def eval_input(self, name, n, m, evaluation):
        "SetStreamPosition[InputStream[name_, n_], m_]"
        stream = stream_manager.lookup_stream(n.get_int_value())

        if stream is None or stream.io is None or stream.io.closed:
            evaluation.message("General", "openx", name)
            return

        if not stream.io.seekable:
            raise NotImplementedError

        seekpos = m.to_python()
        if not (isinstance(seekpos, int) or seekpos == float("inf")):
            evaluation.message(
                "SetStreamPosition", "stmrng", to_expression("InputStream", name, n), m
            )
            return

        try:
            if seekpos == float("inf"):
                stream.io.seek(0, 2)
            else:
                if seekpos < 0:
                    stream.io.seek(seekpos, 2)
                else:
                    stream.io.seek(seekpos)
        except IOError:
            evaluation.message("SetStreamPosition", "seek")

        return Integer(stream.io.tell())

    def eval_output(self, name, n, m, evaluation):
        "SetStreamPosition[OutputStream[name_, n_], m_]"
        return self.eval_input(name, n, m, evaluation)

    def eval_default(self, stream, evaluation):
        "SetStreamPosition[stream_]"
        evaluation.message("General", "stream", stream)
        return


class Skip(Read):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Skip.html</url>

    <dl>
      <dt>'Skip[$stream$, $type$]'
      <dd>skips ahead in an input steream by one object of the specified $type$.

      <dt>'Skip[$stream$, $type$, $n$]'
      <dd>skips ahead in an input steream by $n$ objects of the specified $type$.
    </dl>

    >> stream = StringToStream["a b c d"];
    >> Read[stream, Word]
     = a
    >> Skip[stream, Word]
    >> Read[stream, Word]
     = c
    #> Close[stream];

    >> stream = StringToStream["a b c d"];
    >> Read[stream, Word]
     = a
    >> Skip[stream, Word, 2]
    >> Read[stream, Word]
     = d
    >> Skip[stream, Word]
     = EndOfFile
    #> Close[stream];
    """

    messages = {
        "intm": "Non-negative machine-sized integer expected at position 3 in `1`",
    }

    options = {
        "AnchoredSearch": "False",
        "IgnoreCase": "False",
        "WordSearch": "False",
        "RecordSeparators": '{"\r\n", "\n", "\r"}',
        "WordSeparators": '{" ", "\t"}',
    }

    rules = {
        "Skip[InputStream[name_, n_], types_]": "Skip[InputStream[name, n], types, 1]",
    }
    summary_text = "skip over an object of the specified type in an input stream"

    def eval(self, name, n, typ, m, evaluation: Evaluation, options: dict):
        "Skip[InputStream[name_, n_], typ_, m_, OptionsPattern[Skip]]"

        stream = to_expression("InputStream", name, n)

        # Options
        # TODO Implement extra options
        # py_options = parse_read_options(options)
        # null_records = py_options['NullRecords']
        # null_words = py_options['NullWords']
        # record_separators = py_options['RecordSeparators']
        # token_words = py_options['TokenWords']
        # word_separators = py_options['WordSeparators']

        py_m = m.to_python()
        if not (isinstance(py_m, int) and py_m > 0):
            evaluation.message(
                "Skip",
                "intm",
                to_expression("Skip", to_expression("InputStream", name, n), typ, m),
            )
            return
        for i in range(py_m):
            result = super(Skip, self).eval(stream, typ, evaluation, options)
            if result is SymbolEndOfFile:
                return result
        return SymbolNull


class Find(Read):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Find.html</url>

    <dl>
      <dt>'Find[$stream$, $text$]'
      <dd>find the first line in $stream$ that contains $text$.
    </dl>

    >> stream = OpenRead["ExampleData/EinsteinSzilLetter.txt", CharacterEncoding->"UTF8"];
    >> Find[stream, "uranium"]
     = in manuscript, leads me to expect that the element uranium may be turned into
    >> Find[stream, "uranium"]
     = become possible to set up a nuclear chain reaction in a large mass of uranium,
    #> Close[stream]
     = ...

    >> stream = OpenRead["ExampleData/EinsteinSzilLetter.txt", CharacterEncoding->"UTF8"];
    >> Find[stream, {"energy", "power"} ]
     = a new and important source of energy in the immediate future. Certain aspects
    >> Find[stream, {"energy", "power"} ]
     = by which vast amounts of power and large quantities of new radium-like
    #> Close[stream]
     = ...
    """

    rules = {}

    options = {
        "AnchoredSearch": "False",
        "IgnoreCase": "False",
        "WordSearch": "False",
        "RecordSeparators": '{"\r\n", "\n", "\r"}',
        "WordSeparators": '{" ", "\t"}',
    }
    summary_text = "find the next occurrence of a string"

    def eval(self, name, n, text, evaluation: Evaluation, options: dict):
        "Find[InputStream[name_, n_], text_, OptionsPattern[Find]]"

        # Options
        # TODO Implement extra options
        # py_options = parse_read_options(options)
        # anchored_search = py_options['AnchoredSearch']
        # ignore_case = py_options['IgnoreCase']
        # word_search = py_options['WordSearch']
        # record_separators = py_options['RecordSeparators']
        # word_separators = py_options['WordSeparators']

        py_text = text.to_python()

        stream = to_expression("InputStream", name, n)

        if not isinstance(py_text, list):
            py_text = [py_text]

        if not all(isinstance(t, str) and t[0] == t[-1] == '"' for t in py_text):
            evaluation.message("Find", "unknown", to_expression("Find", stream, text))
            return

        py_text = [t[1:-1] for t in py_text]

        while True:
            tmp = super(Find, self).eval(stream, Symbol("Record"), evaluation, options)
            py_tmp = tmp.to_python()[1:-1]

            if py_tmp == "System`EndOfFile":
                evaluation.message(
                    "Find", "notfound", to_expression("Find", stream, text)
                )
                return SymbolFailed

            for t in py_text:
                if py_tmp.find(t) != -1:
                    return from_python(py_tmp)


class OutputStream(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/OutputStream.html</url>

    <dl>
      <dt>'OutputStream[$name$, $n$]'
      <dd>represents an output stream.
    </dl>

    By default, the list of Streams normally 'OutputStream' entries for 'stderr' and 'stdout'
    >> Streams[]
     = ...
    """

    summary_text = "an output stream"


class StringToStream(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/StringToStream.html</url>

    <dl>
      <dt>'StringToStream[$string$]'
      <dd>converts a $string$ to an open input stream.
    </dl>

    >> strm = StringToStream["abc 123"]
     = InputStream[String, ...]

    The stream must be closed after using it, to release the resource:
    >> Close[strm];
    """

    summary_text = "open an input stream for reading from a string"

    def eval(self, string, evaluation):
        "StringToStream[string_]"
        pystring = string.to_python()[1:-1]
        fp = io.StringIO(str(pystring))

        name_symbol = SymbolString
        stream = stream_manager.add(pystring, io=fp)
        return to_expression("InputStream", name_symbol, Integer(stream.n))


class Streams(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Streams.html</url>

    <dl>
      <dt>'Streams[]'
      <dd>returns a list of all open streams.
    </dl>

    >> Streams[]
     = ...

    >> Streams["stdout"]
     = ...
    """

    summary_text = "list currently open streams"

    def eval(self, evaluation):
        "Streams[]"
        return self.eval_name(None, evaluation)

    def eval_name(self, name, evaluation):
        "Streams[name_String]"
        result = []
        for stream in stream_manager.STREAMS.values():
            if stream is None or stream.io.closed:
                continue
            if isinstance(stream.io, io.StringIO):
                head = SymbolInputStream
                _name = SymbolString
            else:
                mode = stream.mode
                if mode in ["r", "rb"]:
                    head = SymbolInputStream
                elif mode in ["w", "a", "wb", "ab"]:
                    head = SymbolOutputStream
                else:
                    raise ValueError("Unknown mode {0}".format(mode))
                _name = String(stream.name)
            expr = Expression(head, _name, Integer(stream.n))
            if name is None or _name == name:
                result.append(expr)
        return to_mathics_list(*result)


class Record(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Record.html</url>

    <dl>
      <dt>'Record'
      <dd>is a data type for 'Read'.
    </dl>
    """

    summary_text = "sequence of characters delimited by record separators"


class Word(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Word.html</url>

    <dl>
      <dt>'Word'
      <dd>is a data type for 'Read'.
    </dl>
    """

    summary_text = "sequence of characters delimited by word separators"


class Write(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Write.html</url>

    <dl>
      <dt>'Write[$channel$, $expr1$, $expr2$, ...]'
      <dd>writes the expressions to the output channel followed by a newline.
    </dl>

    >> stream = OpenWrite[]
     = ...
    >> Write[stream, 10 x + 15 y ^ 2]
    >> Write[stream, 3 Sin[z]]
    The stream must be closed in order to use the file again:
    >> Close[stream];
    >> stream = OpenRead[%];
    >> ReadList[stream]
     = {10 x + 15 y ^ 2, 3 Sin[z]}
    >> DeleteFile[Close[stream]];
    """

    summary_text = "write a sequence of expressions to a stream, ending the output with a newline (line feed)"

    def eval(self, channel, expr, evaluation):
        "Write[channel_, expr___]"

        stream = None
        if isinstance(channel, String):
            stream = {"stdout": 1, "stderr": 2}.get(channel.value, None)

        if stream is None:
            strm = channel_to_stream(channel, "w")
            if strm is None:
                return
            stream = stream_manager.lookup_stream(strm.elements[1].get_int_value())

        if stream is None or stream.io is None or stream.io.closed:
            evaluation.message("General", "openx", channel)
            return SymbolNull

        expr = expr.get_sequence()
        expr = to_expression("Row", to_mathics_list(*expr))

        evaluation.format = "text"
        text = evaluation.format_output(expr)
        stream.io.write(str(text) + "\n")
        return SymbolNull


class WriteString(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/WriteString.html</url>

    <dl>
      <dt>'WriteString[$stream$, $str1, $str2$, ... ]'
      <dd>writes the strings to the output stream.
    </dl>

    >> stream = OpenWrite[];
    >> WriteString[stream, "This is a test 1"]
    >> WriteString[stream, "This is also a test 2"]
    >> pathname = Close[stream];
    >> FilePrint[%]
     | This is a test 1This is also a test 2

    >> DeleteFile[pathname];
    >> stream = OpenWrite[];
    >> WriteString[stream, "This is a test 1", "This is also a test 2"]
    >> pathname = Close[stream]
     = ...
    >> FilePrint[%]
     | This is a test 1This is also a test 2

    >> DeleteFile[pathname];


    If stream is the string "stdout" or "stderr", writes to the system standard output/ standard error channel:
    >> WriteString["stdout", "Hola"]
    """

    summary_text = "write a sequence of strings to a stream, with no extra newlines"
    messages = {
        "strml": ("`1` is not a string, stream, or list of strings and streams."),
        "writex": "`1`.",
        "noimp": ("List of strings and streams not implemented yet: `1`"),
    }

    def eval(self, channel, expr, evaluation: Evaluation):
        """WriteString[channel_, expr___]"""

        if isinstance(channel, String):
            stream = stream_manager.get_stream_by_name(channel.value)
        elif isinstance(channel, Stream):
            stream = channel
        elif isinstance(channel, ListExpression):
            evaluation.message("WriteString", "noimp", channel)
            return
        elif isinstance(channel, Expression) and channel.head == SymbolOutputStream:
            stream_expr = channel_to_stream(channel, "w")
            if stream_expr is None:
                return
            stream = stream_manager.lookup_stream(
                stream_expr.elements[1].get_int_value()
            )
        else:
            evaluation.message("WriteString", "strml", channel)
            return

        if stream is None or stream.io is None or stream.io.closed:
            return None

        exprs = []
        for expri in expr.get_sequence():
            result = format_element(expri, evaluation, SymbolOutputForm)
            try:
                result = result.boxes_to_text(evaluation=evaluation)
            except BoxError:
                evaluation.message(
                    "General",
                    "notboxes",
                    to_expression("FullForm", result).evaluate(evaluation),
                )
                return
            exprs.append(result)
        line = "".join(exprs)
        if type(stream) is BytesIO:
            line = line.encode("utf8")
        stream.io.write(line)
        try:
            stream.io.flush()
        except IOError as err:
            evaluation.message("WriteString", "writex", err.strerror)
        return SymbolNull
