# -*- coding: utf-8 -*-
# cython: language_level=3

"""
File and Stream Operations
"""

import io
import os
import tempfile

from io import BytesIO
import os.path as osp


from mathics_scanner import TranslateError

import mathics
from mathics.builtin.base import Builtin, Predefined, BinaryOperator, PrefixOperator
from mathics.builtin.base import MessageException

from mathics.core import read
from mathics.core.atoms import (
    Integer,
    String,
    SymbolString,
)
from mathics.core.attributes import protected, read_protected
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.expression import BoxError, Expression
from mathics.core.formatter import format_element, do_format
from mathics.core.parser import MathicsFileLineFeeder, parse
from mathics.core.read import (
    channel_to_stream,
    close_stream,
    MathicsOpen,
    read_get_separators,
    read_name_and_stream_from_channel,
    read_from_stream,
    READ_TYPES,
    SymbolEndOfFile,
)
from mathics.core.streams import (
    path_search,
    stream_manager,
)
from mathics.core.symbols import Symbol, SymbolNull, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolReal,
    SymbolFailed,
    SymbolHold,
    SymbolOutputForm,
)


INITIAL_DIR = os.getcwd()
DIRECTORY_STACK = [INITIAL_DIR]

INPUT_VAR = ""

TMP_DIR = tempfile.gettempdir()

SymbolInputStream = Symbol("InputStream")
SymbolOutputStream = Symbol("OutputStream")
SymbolPath = Symbol("$Path")

# TODO: Improve docs for these Read[] arguments.

# ## FIXME: All of this is related to Read[]
# ## it can be moved somewhere else.


class Input_(Predefined):
    """
    <dl>
    <dt>'$Input'
      <dd>is the name of the stream from which input is currently being read.
    </dl>

    >> $Input
     = #<--#
    """

    attributes = protected | read_protected
    name = "$Input"
    summary_text = "the name of the current input stream"

    def evaluate(self, evaluation):
        global INPUT_VAR
        return String(INPUT_VAR)


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

    def apply_empty(self, evaluation, options):
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
            return self.apply_path(path, evaluation, options)
        else:
            evaluation.message("OpenRead", "argx")
            return

    def apply_path(self, path, evaluation, options):
        "%(name)s[path_?NotOptionQ, OptionsPattern[]]"

        # Options
        # BinaryFormat
        mode = self.mode
        if options["System`BinaryFormat"] is SymbolTrue:
            if not self.mode.endswith("b"):
                mode += "b"

        if not (isinstance(path, String) and len(path.to_python()) > 2):
            evaluation.message(self.__class__.__name__, "fstr", path)
            return

        path_string = path.get_string_value()

        tmp, is_temporary_file = path_search(path_string)
        if tmp is None:
            if mode in ["r", "rb"]:
                evaluation.message("General", "noopen", path)
                return
        else:
            path_string = tmp

        try:
            encoding = self.get_option(options, "CharacterEncoding", evaluation)
            if not isinstance(encoding, String):
                return

            opener = MathicsOpen(
                path_string,
                mode=mode,
                encoding=encoding.get_string_value(),
                is_temporary_file=is_temporary_file,
            )
            opener.__enter__(is_temporary_file=is_temporary_file)
            n = opener.n
        except IOError:
            evaluation.message("General", "noopen", path)
            return
        except MessageException as e:
            e.message(evaluation)
            return

        return Expression(Symbol(self.stream_type), path, Integer(n))


class Character(Builtin):
    """
    <dl>
      <dt>'Character'
      <dd>is a data type for 'Read'.
    </dl>
    """

    summary_text = "single character, returned as a one‐character string"


class Close(Builtin):
    """
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

    #> Close["abc"]
     : abc is not open.
     = Close[abc]

    #> Clear[file]
    """

    summary_text = "close a stream"
    messages = {
        "closex": "`1`.",
    }

    def apply(self, channel, evaluation):
        "Close[channel_]"

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
    <dl>
    <dt>'EndOfFile'
      <dd>is returned by 'Read' when the end of an input stream is reached.
    </dl>
    """

    summary_text = "end of the file"


class Expression_(Builtin):
    """
    <dl>
      <dt>'Expression'
      <dd>is a data type for 'Read'.
    </dl>

    For information about underlying data structure Expression (a kind of M-expression) that is central in evaluation, see: <url>https://mathics-development-guide.readthedocs.io/en/latest/extending/code-overview/ast.html</url>
    """

    summary_text = "WL expression"
    name = "Expression"


class FilePrint(Builtin):
    """
    <dl>
    <dt>'FilePrint[$file$]'
      <dd>prints the raw contents of $file$.
    </dl>

    #> exp = Sin[1];
    #> FilePrint[exp]
     : File specification Sin[1] is not a string of one or more characters.
     = FilePrint[Sin[1]]

    #> FilePrint["somenonexistantpath_h47sdmk^&h4"]
     : Cannot open somenonexistantpath_h47sdmk^&h4.
     = FilePrint[somenonexistantpath_h47sdmk^&h4]

    #> FilePrint[""]
     : File specification  is not a string of one or more characters.
     = FilePrint[]
    """

    summary_text = "display the contents of a file"
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

    def apply(self, path, evaluation, options):
        "FilePrint[path_ OptionsPattern[FilePrint]]"
        pypath = path.to_python()
        if not (
            isinstance(pypath, str)
            and pypath[0] == pypath[-1] == '"'
            and len(pypath) > 2
        ):
            evaluation.message("FilePrint", "fstr", path)
            return
        pypath, is_temporary_file = path_search(pypath[1:-1])

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


class Number_(Builtin):
    """
    <dl>
    <dt>'Number'
      <dd>is a data type for 'Read'.
    </dl>
    """

    summary_text = "exact or approximate number in Fortran‐like notation"
    name = "Number"


class Get(PrefixOperator):
    r"""
    <dl>
      <dt>'<<$name$'
      <dd>reads a file and evaluates each expression, returning only the last one.

      <dt>'Get[$name$, Trace->True]'
      <dd>Runs Get tracing each line before it is evaluated.
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

    #> Get["SomeTypoPackage`"]
     : Cannot open SomeTypoPackage`.
     = $Failed

    ## Parser Tests
    #> Hold[<< ~/some_example/dir/] // FullForm
     = Hold[Get["~/some_example/dir/"]]
    #> Hold[<<`/.\-_:$*~?] // FullForm
     = Hold[Get["`/.\\\\-_:$*~?"]]
    """
    summary_text = "read in a file and evaluate commands in it"
    operator = "<<"
    precedence = 720
    options = {
        "Trace": "False",
    }

    def apply(self, path, evaluation, options):
        "Get[path_String, OptionsPattern[Get]]"

        def check_options(options):
            # Options
            # TODO Proper error messages

            result = {}
            trace_get = evaluation.parse("Settings`$TraceGet")
            if (
                options["System`Trace"].to_python()
                or trace_get.evaluate(evaluation) is SymbolTrue
            ):
                import builtins

                result["TraceFn"] = builtins.print
            else:
                result["TraceFn"] = None

            return result

        py_options = check_options(options)
        trace_fn = py_options["TraceFn"]
        result = None
        pypath = path.get_string_value()
        definitions = evaluation.definitions
        mathics.core.streams.PATH_VAR = SymbolPath.evaluate(evaluation).to_python(
            string_quotes=False
        )
        try:
            if trace_fn:
                trace_fn(pypath)
            with MathicsOpen(pypath, "r") as f:
                feeder = MathicsFileLineFeeder(f, trace_fn)
                while not feeder.empty():
                    try:
                        query = parse(definitions, feeder)
                    except TranslateError:
                        return SymbolNull
                    finally:
                        feeder.send_messages(evaluation)
                    if query is None:  # blank line / comment
                        continue
                    result = query.evaluate(evaluation)
        except IOError:
            evaluation.message("General", "noopen", path)
            return SymbolFailed
        except MessageException as e:
            e.message(evaluation)
            return SymbolFailed
        return result

    def apply_default(self, filename, evaluation):
        "Get[filename_]"
        expr = to_expression("Get", filename)
        evaluation.message("General", "stream", filename)
        return expr


class InputFileName_(Predefined):
    """
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
        return String(read.INPUTFILE_VAR)


class InputStream(Builtin):
    """
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

    summary_text = "an input stream"


class OpenRead(_OpenAction):
    """
    <dl>
      <dt>'OpenRead["file"]'
      <dd>opens a file and returns an 'InputStream'.
    </dl>

    >> OpenRead["ExampleData/EinsteinSzilLetter.txt"]
     = InputStream[...]
    #> Close[%];

    S> Close[OpenRead["https://raw.githubusercontent.com/Mathics3/mathics-core/master/README.rst"]];

    #> OpenRead[]
     : OpenRead called with 0 arguments; 1 argument is expected.
     = OpenRead[]

    #> OpenRead[y]
     : File specification y is not a string of one or more characters.
     = OpenRead[y]

    #> OpenRead[""]
     : File specification  is not a string of one or more characters.
     = OpenRead[]

    #> OpenRead["MathicsNonExampleFile"]
     : Cannot open MathicsNonExampleFile.
     = OpenRead[MathicsNonExampleFile]

    #> OpenRead["ExampleData/EinsteinSzilLetter.txt", BinaryFormat -> True]
     = InputStream[...]
    #> Close[%];
    """

    summary_text = "open a file for reading"
    mode = "r"
    stream_type = "InputStream"


class OpenWrite(_OpenAction):
    """
    <dl>
    <dt>'OpenWrite["file"]'
      <dd>opens a file and returns an OutputStream.
    </dl>

    >> OpenWrite[]
     = OutputStream[...]
    #> DeleteFile[Close[%]];

    #> OpenWrite[BinaryFormat -> True]
     = OutputStream[...]
    #> DeleteFile[Close[%]];
    """

    summary_text = (
        "send an output stream to a file, wiping out the previous contents of the file"
    )
    mode = "w"
    stream_type = "OutputStream"


class OpenAppend(_OpenAction):
    """
    <dl>
    <dt>'OpenAppend["file"]'
      <dd>opens a file and returns an OutputStream to which writes are appended.
    </dl>

    >> OpenAppend[]
     = OutputStream[...]
    #> DeleteFile[Close[%]];

    #> appendFile = OpenAppend["MathicsNonExampleFile"]
     = OutputStream[MathicsNonExampleFile, ...]

    #> Close[appendFile]
     = MathicsNonExampleFile
    #> DeleteFile["MathicsNonExampleFile"]
    """

    summary_text = (
        "open an output stream to a file, appending to what was already in the file"
    )
    mode = "a"
    stream_type = "OutputStream"


class Put(BinaryOperator):
    """
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

    summary_text = "write an expression to a file"
    operator = ">>"
    precedence = 30

    def apply(self, exprs, filename, evaluation):
        "Put[exprs___, filename_String]"
        instream = to_expression("OpenWrite", filename).evaluate(evaluation)
        if len(instream.elements) == 2:
            name, n = instream.elements
        else:
            return  # opening failed
        result = self.apply_input(exprs, name, n, evaluation)
        instream_number = instream.elements[1].value
        py_instream = stream_manager.lookup_stream(instream_number)

        close_stream(py_instream, instream_number)
        return result

    def apply_input(self, exprs, name, n, evaluation):
        "Put[exprs___, OutputStream[name_, n_]]"
        stream = stream_manager.lookup_stream(n.get_int_value())

        if stream is None or stream.io.closed:
            evaluation.message("Put", "openx", to_expression("OutputSteam", name, n))
            return

        text = [
            evaluation.format_output(to_expression("InputForm", expr))
            for expr in exprs.get_sequence()
        ]
        text = "\n".join(text) + "\n"
        text.encode("utf-8")

        stream.io.write(text)

        return SymbolNull

    def apply_default(self, exprs, filename, evaluation):
        "Put[exprs___, filename_]"
        expr = to_expression("Put", exprs, filename)
        evaluation.message("General", "stream", filename)
        return expr


class PutAppend(BinaryOperator):
    """
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
    #> DeleteFile["factorials"];

    ## writing to dir
    #> x >>> /var/
     : Cannot open /var/.
     = x >>> /var/

    ## writing to read only file
    #> x >>> /proc/uptime
     : Cannot open /proc/uptime.
     = x >>> /proc/uptime
    """

    summary_text = "append an expression to a file"
    operator = ">>>"
    precedence = 30

    def apply(self, exprs, filename, evaluation):
        "PutAppend[exprs___, filename_String]"
        instream = to_expression("OpenAppend", filename).evaluate(evaluation)
        if len(instream.elements) == 2:
            name, n = instream.elements
        else:
            return  # opening failed
        result = self.apply_input(exprs, name, n, evaluation)
        to_expression("Close", instream).evaluate(evaluation)
        return result

    def apply_input(self, exprs, name, n, evaluation):
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

    def apply_default(self, exprs, filename, evaluation):
        "PutAppend[exprs___, filename_]"
        expr = to_expression("PutAppend", exprs, filename)
        evaluation.message("General", "stream", filename)
        return expr


class Read(Builtin):
    """
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

    ## Malformed InputString
    #> Read[InputStream[String], {Word, Number}]
     = Read[InputStream[String], {Word, Number}]

    ## Correctly formed InputString but not open
    #> Read[InputStream[String, -1], {Word, Number}]
     : InputStream[String, -1] is not open.
     = Read[InputStream[String, -1], {Word, Number}]

    ## Reading Strings
    >> stream = StringToStream["abc123"];
    >> Read[stream, String]
     = abc123
    #> Read[stream, String]
     = EndOfFile
    #> Close[stream];

    ## Reading Words
    >> stream = StringToStream["abc 123"];
    >> Read[stream, Word]
     = abc
    >> Read[stream, Word]
     = 123
    #> Read[stream, Word]
     = EndOfFile
    #> Close[stream];
    #> stream = StringToStream[""];
    #> Read[stream, Word]
     = EndOfFile
    #> Read[stream, Word]
     = EndOfFile
    #> Close[stream];

    ## Number
    >> stream = StringToStream["123, 4"];
    >> Read[stream, Number]
     = 123
    >> Read[stream, Number]
     = 4
    #> Read[stream, Number]
     = EndOfFile
    #> Close[stream];
    #> stream = StringToStream["123xyz 321"];
    #> Read[stream, Number]
     = 123
    #> Quiet[Read[stream, Number]]
     = $Failed

    ## Real
    #> stream = StringToStream["123, 4abc"];
    #> Read[stream, Real]
     = 123.
    #> Read[stream, Real]
     = 4.
    #> Quiet[Read[stream, Number]]
     = $Failed

    #> Close[stream];
    #> stream = StringToStream["1.523E-19"]; Read[stream, Real]
     = 1.523×10^-19
    #> Close[stream];
    #> stream = StringToStream["-1.523e19"]; Read[stream, Real]
     = -1.523×10^19
    #> Close[stream];
    #> stream = StringToStream["3*^10"]; Read[stream, Real]
     = 3.×10^10
    #> Close[stream];
    #> stream = StringToStream["3.*^10"]; Read[stream, Real]
     = 3.×10^10
    #> Close[stream];

    ## Expression
    #> stream = StringToStream["x + y Sin[z]"]; Read[stream, Expression]
     = x + y Sin[z]
    #> Close[stream];
    ## #> stream = Quiet[StringToStream["Sin[1 123"]; Read[stream, Expression]]
    ##  = $Failed

    ## HoldExpression:
    >> stream = StringToStream["2+2\\n2+3"];

    'Read' with a 'Hold[Expression]' returns the expression it reads unevaluated so it can be later inspected and evaluated:

    >> Read[stream, Hold[Expression]]
     = Hold[2 + 2]

    >> Read[stream, Expression]
     = 5
    >> Close[stream];

    Reading a comment however will return the empy list:
    >> stream = StringToStream["(* ::Package:: *)"];

    >> Read[stream, Hold[Expression]]
     = {}

    >> Close[stream];

    ## Multiple types
    >> stream = StringToStream["123 abc"];
    >> Read[stream, {Number, Word}]
     = {123, abc}
    #> Read[stream, {Number, Word}]
     = EndOfFile
    #> lose[stream];

    #> stream = StringToStream["123 abc"];
    #> Quiet[Read[stream, {Word, Number}]]
     = $Failed
    #> Close[stream];

    #> stream = StringToStream["123 123"];  Read[stream, {Real, Number}]
     = {123., 123}
    #> Close[stream];

    #> Quiet[Read[stream, {Real}]]
     = Read[InputStream[String, ...], {Real}]

    Multiple lines:
    >> stream = StringToStream["\\"Tengo una\\nvaca lechera.\\""]; Read[stream]
     = Tengo una
     . vaca lechera.

    """

    summary_text = "read an object of the specified type from a stream"
    messages = {
        "openx": "`1` is not open.",
        "readf": "`1` is not a valid format specification.",
        "readn": "Invalid real number found when reading from `1`.",
        "readt": "Invalid input found when reading `1` from `2`.",
        "intnm": (
            "Non-negative machine-sized integer expected at " "position 3 in `1`."
        ),
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

    def check_options(self, options):
        # Options
        # TODO Proper error messages

        result = {}
        keys = list(options.keys())

        # AnchoredSearch
        if "System`AnchoredSearch" in keys:
            anchored_search = options["System`AnchoredSearch"].to_python()
            assert anchored_search in [True, False]
            result["AnchoredSearch"] = anchored_search

        # IgnoreCase
        if "System`IgnoreCase" in keys:
            ignore_case = options["System`IgnoreCase"].to_python()
            assert ignore_case in [True, False]
            result["IgnoreCase"] = ignore_case

        # WordSearch
        if "System`WordSearch" in keys:
            word_search = options["System`WordSearch"].to_python()
            assert word_search in [True, False]
            result["WordSearch"] = word_search

        # RecordSeparators
        if "System`RecordSeparators" in keys:
            record_separators = options["System`RecordSeparators"].to_python()
            assert isinstance(record_separators, list)
            assert all(
                isinstance(s, str) and s[0] == s[-1] == '"' for s in record_separators
            )
            record_separators = [s[1:-1] for s in record_separators]
            result["RecordSeparators"] = record_separators

        # WordSeparators
        if "System`WordSeparators" in keys:
            word_separators = options["System`WordSeparators"].to_python()
            assert isinstance(word_separators, list)
            assert all(
                isinstance(s, str) and s[0] == s[-1] == '"' for s in word_separators
            )
            word_separators = [s[1:-1] for s in word_separators]
            result["WordSeparators"] = word_separators

        # NullRecords
        if "System`NullRecords" in keys:
            null_records = options["System`NullRecords"].to_python()
            assert null_records in [True, False]
            result["NullRecords"] = null_records

        # NullWords
        if "System`NullWords" in keys:
            null_words = options["System`NullWords"].to_python()
            assert null_words in [True, False]
            result["NullWords"] = null_words

        # TokenWords
        if "System`TokenWords" in keys:
            token_words = options["System`TokenWords"].to_python()
            assert token_words == []
            result["TokenWords"] = token_words

        return result

    def apply(self, channel, types, evaluation, options):
        "Read[channel_, types_, OptionsPattern[Read]]"

        name, n, stream = read_name_and_stream_from_channel(channel, evaluation)
        if name is None:
            return

        # Wrap types in a list (if it isn't already one)
        if types.has_form("List", None):
            types = types.elements
        else:
            types = (types,)

        # TODO: look for a better implementation handling "Hold[Expression]".
        #
        types = (
            Symbol("HoldExpression")
            if (
                typ.get_head_name() == "System`Hold"
                and typ.elements[0].get_name() == "System`Expression"
            )
            else typ
            for typ in types
        )
        types = to_mathics_list(*types)

        for typ in types.elements:
            if typ not in READ_TYPES:
                evaluation.message("Read", "readf", typ)
                return SymbolFailed

        record_separators, word_separators = read_get_separators(options)

        name = name.to_python()

        result = []

        read_word = read_from_stream(stream, word_separators, evaluation.message)
        read_record = read_from_stream(stream, record_separators, evaluation.message)
        read_number = read_from_stream(
            stream,
            word_separators + record_separators,
            evaluation.message,
            ["+", "-", "."] + [str(i) for i in range(10)],
        )
        read_real = read_from_stream(
            stream,
            word_separators + record_separators,
            evaluation.message,
            ["+", "-", ".", "e", "E", "^", "*"] + [str(i) for i in range(10)],
        )

        from mathics.core.expression import BaseElement
        from mathics_scanner.errors import IncompleteSyntaxError, InvalidSyntaxError
        from mathics.core.parser import MathicsMultiLineFeeder, parse

        for typ in types.elements:
            try:
                if typ is Symbol("Byte"):
                    tmp = stream.io.read(1)
                    if tmp == "":
                        raise EOFError
                    result.append(ord(tmp))
                elif typ is Symbol("Character"):
                    tmp = stream.io.read(1)
                    if tmp == "":
                        raise EOFError
                    result.append(tmp)
                elif typ is Symbol("Expression") or typ is Symbol("HoldExpression"):
                    tmp = next(read_record)
                    while True:
                        try:
                            feeder = MathicsMultiLineFeeder(tmp)
                            expr = parse(evaluation.definitions, feeder)
                            break
                        except (IncompleteSyntaxError, InvalidSyntaxError):
                            try:
                                nextline = next(read_record)
                                tmp = tmp + "\n" + nextline
                            except EOFError:
                                expr = SymbolEndOfFile
                                break
                        except Exception as e:
                            print(e)

                    if expr is SymbolEndOfFile:
                        evaluation.message(
                            "Read", "readt", tmp, to_expression("InputSteam", name, n)
                        )
                        return SymbolFailed
                    elif isinstance(expr, BaseElement):
                        if typ is Symbol("HoldExpression"):
                            expr = Expression(SymbolHold, expr)
                        result.append(expr)
                    # else:
                    #  TODO: Supposedly we can't get here
                    # what code should we put here?

                elif typ is Symbol("Number"):
                    tmp = next(read_number)
                    try:
                        tmp = int(tmp)
                    except ValueError:
                        try:
                            tmp = float(tmp)
                        except ValueError:
                            evaluation.message(
                                "Read", "readn", to_expression("InputSteam", name, n)
                            )
                            return SymbolFailed
                    result.append(tmp)

                elif typ is SymbolReal:
                    tmp = next(read_real)
                    tmp = tmp.replace("*^", "E")
                    try:
                        tmp = float(tmp)
                    except ValueError:
                        evaluation.message(
                            "Read", "readn", to_expression("InputSteam", name, n)
                        )
                        return SymbolFailed
                    result.append(tmp)
                elif typ is Symbol("Record"):
                    result.append(next(read_record))
                elif typ is Symbol("String"):
                    tmp = stream.io.readline()
                    if len(tmp) == 0:
                        raise EOFError
                    result.append(tmp.rstrip("\n"))
                elif typ is Symbol("Word"):
                    result.append(next(read_word))

            except EOFError:
                return SymbolEndOfFile
            except UnicodeDecodeError:
                evaluation.message("General", "ucdec")

        if isinstance(result, Symbol):
            return result
        if len(result) == 1:
            return from_python(*result)

        return from_python(result)

    def apply_nostream(self, arg1, arg2, evaluation):
        "Read[arg1_, arg2_]"
        evaluation.message("General", "stream", arg1)
        return


class ReadList(Read):
    """
    <dl>
    <dt>'ReadList["$file$"]'
      <dd>Reads all the expressions until the end of file.
    <dt>'ReadList["$file$", $type$]'
      <dd>Reads objects of a specified type until the end of file.
    <dt>'ReadList["$file$", {$type1$, $type2$, ...}]'
      <dd>Reads a sequence of specified types until the end of file.
    </dl>

    >> ReadList[StringToStream["a 1 b 2"], {Word, Number}]
     = {{a, 1}, {b, 2}}

    >> stream = StringToStream["\\"abc123\\""];
    >> ReadList[stream]
     = {abc123}
    >> InputForm[%]
     = {"abc123"}

    #> ReadList[stream, "Invalid"]
     : Invalid is not a valid format specification.
     = ReadList[..., Invalid]
    #> Close[stream];


    #> ReadList[StringToStream["a 1 b 2"], {Word, Number}, 1]
     = {{a, 1}}
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
    summary_text = "read a sequence of elements from a file, and put them in a WL list"
    rules = {
        "ReadList[stream_]": "ReadList[stream, Expression]",
    }

    options = {
        "NullRecords": "False",
        "NullWords": "False",
        "RecordSeparators": '{"\r\n", "\n", "\r"}',
        "TokenWords": "{}",
        "WordSeparators": '{" ", "\t"}',
    }

    def apply(self, channel, types, evaluation, options):
        "ReadList[channel_, types_, OptionsPattern[ReadList]]"

        # Options
        # TODO: Implement extra options
        # py_options = self.check_options(options)
        # null_records = py_options['NullRecords']
        # null_words = py_options['NullWords']
        # record_separators = py_options['RecordSeparators']
        # token_words = py_options['TokenWords']
        # word_separators = py_options['WordSeparators']

        result = []
        while True:
            tmp = super(ReadList, self).apply(channel, types, evaluation, options)

            if tmp is None:
                return

            if tmp is SymbolFailed:
                return

            if tmp is SymbolEndOfFile:
                break
            result.append(tmp)
        return from_python(result)

    def apply_m(self, channel, types, m, evaluation, options):
        "ReadList[channel_, types_, m_, OptionsPattern[ReadList]]"

        # Options
        # TODO: Implement extra options
        # py_options = self.check_options(options)
        # null_records = py_options['NullRecords']
        # null_words = py_options['NullWords']
        # record_separators = py_options['RecordSeparators']
        # token_words = py_options['TokenWords']
        # word_separators = py_options['WordSeparators']

        py_m = m.get_int_value()
        if py_m < 0:
            evaluation.message(
                "ReadList", "intnm", to_expression("ReadList", channel, types, m)
            )
            return

        result = []
        for i in range(py_m):
            tmp = super(ReadList, self).apply(channel, types, evaluation, options)

            if tmp is SymbolFailed:
                return

            if tmp.to_python() == "EndOfFile":
                break
            result.append(tmp)
        return from_python(result)


class StreamPosition(Builtin):
    """
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

    def apply_input(self, name, n, evaluation):
        "StreamPosition[InputStream[name_, n_]]"
        stream = stream_manager.lookup_stream(n.get_int_value())

        if stream is None or stream.io is None or stream.io.closed:
            evaluation.message("General", "openx", name)
            return

        return Integer(stream.io.tell())

    def apply_output(self, name, n, evaluation):
        "StreamPosition[OutputStream[name_, n_]]"
        self.input_apply(name, n, evaluation)

    def apply_default(self, stream, evaluation):
        "StreamPosition[stream_]"
        evaluation.message("General", "stream", stream)
        return


class SetStreamPosition(Builtin):
    """
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

    #> SetStreamPosition[stream, -5]
     : Invalid I/O Seek.
     = 10

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

    def apply_input(self, name, n, m, evaluation):
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

    def apply_output(self, name, n, m, evaluation):
        "SetStreamPosition[OutputStream[name_, n_], m_]"
        return self.apply_input(name, n, m, evaluation)

    def apply_default(self, stream, evaluation):
        "SetStreamPosition[stream_]"
        evaluation.message("General", "stream", stream)
        return


class Skip(Read):
    """
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
    #> Skip[stream, Word]
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

    def apply(self, name, n, types, m, evaluation, options):
        "Skip[InputStream[name_, n_], types_, m_, OptionsPattern[Skip]]"

        channel = to_expression("InputStream", name, n)

        # Options
        # TODO Implement extra options
        # py_options = self.check_options(options)
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
                to_expression("Skip", to_expression("InputStream", name, n), types, m),
            )
            return
        for i in range(py_m):
            result = super(Skip, self).apply(channel, types, evaluation, options)
            if result is SymbolEndOfFile:
                return result
        return SymbolNull


class Find(Read):
    """
    <dl>
    <dt>'Find[$stream$, $text$]'
      <dd>find the first line in $stream$ that contains $text$.
    </dl>

    >> stream = OpenRead["ExampleData/EinsteinSzilLetter.txt"];
    >> Find[stream, "uranium"]
     = in manuscript, leads me to expect that the element uranium may be turned into
    >> Find[stream, "uranium"]
     = become possible to set up a nuclear chain reaction in a large mass of uranium,
    >> Close[stream]
     = ...

    >> stream = OpenRead["ExampleData/EinsteinSzilLetter.txt"];
    >> Find[stream, {"energy", "power"} ]
     = a new and important source of energy in the immediate future. Certain aspects
    >> Find[stream, {"energy", "power"} ]
     = by which vast amounts of power and large quantities of new radium-like
    >> Close[stream]
     = ...
    """

    options = {
        "AnchoredSearch": "False",
        "IgnoreCase": "False",
        "WordSearch": "False",
        "RecordSeparators": '{"\r\n", "\n", "\r"}',
        "WordSeparators": '{" ", "\t"}',
    }
    summary_text = "find the next occurrence of a string"

    def apply(self, name, n, text, evaluation, options):
        "Find[InputStream[name_, n_], text_, OptionsPattern[Find]]"

        # Options
        # TODO Implement extra options
        # py_options = self.check_options(options)
        # anchored_search = py_options['AnchoredSearch']
        # ignore_case = py_options['IgnoreCase']
        # word_search = py_options['WordSearch']
        # record_separators = py_options['RecordSeparators']
        # word_separators = py_options['WordSeparators']

        py_text = text.to_python()

        channel = to_expression("InputStream", name, n)

        if not isinstance(py_text, list):
            py_text = [py_text]

        if not all(isinstance(t, str) and t[0] == t[-1] == '"' for t in py_text):
            evaluation.message("Find", "unknown", to_expression("Find", channel, text))
            return

        py_text = [t[1:-1] for t in py_text]

        while True:
            tmp = super(Find, self).apply(
                channel, Symbol("Record"), evaluation, options
            )
            py_tmp = tmp.to_python()[1:-1]

            if py_tmp == "System`EndOfFile":
                evaluation.message(
                    "Find", "notfound", to_expression("Find", channel, text)
                )
                return SymbolFailed

            for t in py_text:
                if py_tmp.find(t) != -1:
                    return from_python(py_tmp)


class OutputStream(Builtin):
    """
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
    <dl>
      <dt>'StringToStream[$string$]'
      <dd>converts a $string$ to an open input stream.
    </dl>

    >> strm = StringToStream["abc 123"]
     = InputStream[String, ...]

    #> Read[strm, Word]
     = abc

    #> Read[strm, Number]
     = 123

    #> Close[strm]
     = String
    """

    summary_text = "open an input stream for reading from a string"

    def apply(self, string, evaluation):
        "StringToStream[string_]"
        pystring = string.to_python()[1:-1]
        fp = io.StringIO(str(pystring))

        name = Symbol("String")
        stream = stream_manager.add(pystring, io=fp)
        return to_expression("InputStream", name, Integer(stream.n))


class Streams(Builtin):
    """
    <dl>
      <dt>'Streams[]'
      <dd>returns a list of all open streams.
    </dl>

    >> Streams[]
     = ...

    >> Streams["stdout"]
     = ...

    #> OpenWrite[]
     = ...
    #> Streams[%[[1]]]
     = {OutputStream[...]}

    #> Streams["some_nonexistant_name"]
     = {}
    """

    summary_text = "list currently open streams"

    def apply(self, evaluation):
        "Streams[]"
        return self.apply_name(None, evaluation)

    def apply_name(self, name, evaluation):
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
    <dl>
      <dt>'Record'
      <dd>is a data type for 'Read'.
    </dl>
    """

    summary_text = "sequence of characters delimited by record separators"


class Word(Builtin):
    """
    <dl>
      <dt>'Word'
      <dd>is a data type for 'Read'.
    </dl>
    """

    summary_text = "sequence of characters delimited by word separators"


class Write(Builtin):
    """
    <dl>
      <dt>'Write[$channel$, $expr1$, $expr2$, ...]'
      <dd>writes the expressions to the output channel followed by a newline.
    </dl>

    >> stream = OpenWrite[]
     = ...
    >> Write[stream, 10 x + 15 y ^ 2]
    >> Write[stream, 3 Sin[z]]
    >> Close[stream];
    >> stream = OpenRead[%];
    >> ReadList[stream]
     = {10 x + 15 y ^ 2, 3 Sin[z]}
    #> DeleteFile[Close[stream]];
    """

    summary_text = "write a sequence of expressions to a stream, ending the output with a newline (line feed)"

    def apply(self, channel, expr, evaluation):
        "Write[channel_, expr___]"

        strm = channel_to_stream(channel)

        if strm is None:
            return

        n = strm.elements[1].get_int_value()
        stream = stream_manager.lookup_stream(n)

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

    #> DeleteFile[pathname];
    >> stream = OpenWrite[];
    >> WriteString[stream, "This is a test 1", "This is also a test 2"]
    >> pathname = Close[stream]
     = ...
    >> FilePrint[%]
     | This is a test 1This is also a test 2

    #> DeleteFile[pathname];
    #> stream = OpenWrite[];
    #> WriteString[stream, 100, 1 + x + y, Sin[x  + y]]
    #> pathname = Close[stream]
     = ...
    #> FilePrint[%]
     | 1001 + x + ySin[x + y]

    #> DeleteFile[pathname];
    #> stream = OpenWrite[];
    #> WriteString[stream]
    #> pathame = Close[stream]
     = ...
    #> FilePrint[%]

    #> WriteString[%%, abc]
    #> Streams[%%%][[1]]
     = ...
    #> pathname = Close[%];
    #> FilePrint[%]
     | abc
    #> DeleteFile[pathname];
    #> Clear[pathname];

    """

    summary_text = "write a sequence of strings to a stream, with no extra newlines"
    messages = {
        "strml": ("`1` is not a string, stream, " "or list of strings and streams."),
        "writex": "`1`.",
    }

    def apply(self, channel, expr, evaluation):
        "WriteString[channel_, expr___]"
        strm = channel_to_stream(channel, "w")

        if strm is None:
            return

        stream = stream_manager.lookup_stream(strm.elements[1].get_int_value())

        if stream is None or stream.io is None or stream.io.closed:
            return None

        exprs = []
        for expri in expr.get_sequence():
            result = format_element(expri, evaluation, SymbolOutputForm)
            try:
                result = result.boxes_to_text(evaluation=evaluation)
            except BoxError:
                return evaluation.message(
                    "General",
                    "notboxes",
                    to_expression("FullForm", result).evaluate(evaluation),
                )
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
