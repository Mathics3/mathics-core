# -*- coding: utf-8 -*-
"""
File related evaluation functions.
"""

import os
from typing import Callable, Literal, Optional

from mathics_scanner.errors import (
    IncompleteSyntaxError,
    InvalidSyntaxError,
    SyntaxError,
)
from mathics_scanner.location import ContainerKind

import mathics
import mathics.core.parser
import mathics.core.streams
from mathics.core.atoms import Integer, String
from mathics.core.builtin import MessageException
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import BaseElement, Expression
from mathics.core.parser import MathicsFileLineFeeder, MathicsMultiLineFeeder
from mathics.core.parser.util import parse_incrementally_by_line
from mathics.core.streams import path_search, stream_manager
from mathics.core.symbols import Symbol, SymbolNull
from mathics.core.systemsymbols import (
    SymbolEndOfFile,
    SymbolExpression,
    SymbolFailed,
    SymbolHold,
    SymbolHoldExpression,
    SymbolPath,
    SymbolReal,
    SymbolWord,
)
from mathics.core.util import canonic_filename
from mathics.eval.files_io.read import (
    READ_TYPES,
    MathicsOpen,
    close_stream,
    read_from_stream,
    read_get_separators,
)

# Python representation of $InputFileName.  On Windows platforms, we
# canonicalize this to its Posix equivalent name.
# FIXME: Remove this as a module-level variable and instead
#        define it in a session definitions object.
#        With this, multiple sessions will have separate
#        $InputFilename
INPUT_VAR: str = ""

DEFAULT_TRACE_FN: Literal[None] = None


def print_line_number_and_text(line_number: int, text: str):
    """Prints a line number an text on that line with it.
    This is used as the default trace function in Get[]
    """
    if line_number == 0:
        print(f"Reading file: {text}")
    else:
        print("%5d: %s" % (line_number, text.rstrip()))


GET_PRINT_FN: Callable = print_line_number_and_text


def get_file_time(file) -> float:
    """Return the last time that a file was accessed"""
    try:
        return os.stat(file).st_mtime
    except OSError:
        return 0


def set_input_var(input_string: str):
    """
    Allow INPUT_VAR to get set, e.g. from main program.
    """
    global INPUT_VAR
    INPUT_VAR = canonic_filename(input_string)


def eval_Close(obj, evaluation: Evaluation):
    """
    Closes a stream or socket `obj` which can be an 'InputStream' or
    'OutputStream' object, or `SocketObject`. If there is only one
    stream with a particular name, `obj` can be the string name, the
    file path, of `obj`.
    """

    n = name = None
    if obj.has_form(("InputStream", "OutputStream"), 2):
        [name, n] = obj.elements
        stream = stream_manager.lookup_stream(n.value)
    elif isinstance(obj, String):
        stream, channel = stream_manager.get_stream_and_channel_by_name(obj.value)
        if stream is None:
            if channel == -1:
                evaluation.message("General", "openx", obj)
            return
        close_stream(stream, channel)
        return obj
    else:
        stream = None

    if stream is None or stream.io is None or stream.io.closed:
        evaluation.message("General", "openx", obj)
        return

    if n is not None:
        close_stream(stream, n.value)
    return name


def eval_Get(
    path: str, evaluation: Evaluation, trace_fn: Optional[Callable] = DEFAULT_TRACE_FN
):
    """
    Reads a file and evaluates each expression, returning only the last one.
    """

    path = canonic_filename(path)
    result = None
    definitions = evaluation.definitions

    # Wrap actual evaluation to handle setting $Input
    # and $InputFileName
    # store input paths of calling context

    global INPUT_VAR
    outer_input_var = INPUT_VAR
    outer_inputfile = definitions.get_inputfile()

    # Set a new input path.
    INPUT_VAR = path
    definitions.set_inputfile(INPUT_VAR)

    mathics.core.streams.PATH_VAR = SymbolPath.evaluate(evaluation).to_python(
        string_quotes=False
    )
    if trace_fn is not None:
        trace_fn(0, path + "\n")
    try:
        with MathicsOpen(path, "r") as f:
            feeder = MathicsFileLineFeeder(f, trace_fn)
            while not feeder.empty():
                try:
                    # Note: we use mathics.core.parser.parse
                    # so that tracing/debugging can intercept parse()
                    query = mathics.core.parser.parse(definitions, feeder)
                except SyntaxError:
                    return SymbolNull
                finally:
                    feeder.send_messages(evaluation)
                if query is None:  # blank line / comment
                    continue
                result = query.evaluate(evaluation)
    except IOError:
        evaluation.message("Get", "noopen", path)
        return SymbolFailed
    except MessageException as e:
        e.message(evaluation)
        return SymbolFailed
    finally:
        # Whether we had an exception or not, restore the input path
        # and the state of definitions prior to calling Get.
        INPUT_VAR = outer_input_var
        definitions.set_inputfile(outer_inputfile)
    return result


def eval_Open(
    name: String,
    mode: str,
    stream_type,
    encoding: Optional[str],
    evaluation: Evaluation,
):
    path = name.value
    tmp, is_temporary_file = path_search(path)
    if tmp is None:
        if mode in ["r", "rb"]:
            evaluation.message("General", "noopen", name)
            return SymbolFailed
    else:
        path = tmp

    try:
        opener = MathicsOpen(
            path,
            mode=mode,
            name=name.value,
            encoding=encoding,
            is_temporary_file=is_temporary_file,
        )
        opener.__enter__(is_temporary_file=is_temporary_file)
        n = opener.n
    except IOError:
        evaluation.message("General", "noopen", name)
        return SymbolFailed
    except MessageException as e:
        e.message(evaluation)
        return

    return Expression(Symbol(stream_type), name, Integer(n))


def eval_Read(
    name: str, n: int, types: tuple, stream, evaluation: Evaluation, options: dict
):
    """
    Evaluation method for Read[] and ReadList[]. `name` will be either "Read" or
    "ReadList" and is used in error messages
    """
    types = to_mathics_list(*types)

    for typ in types.elements:
        if typ not in READ_TYPES:
            evaluation.message(name, "readf", typ)
            return SymbolFailed

    separators = read_get_separators(options, evaluation)
    if separators is None:
        return

    record_separators, token_words, word_separators = separators

    # name = name.to_python()

    result = []

    read_word = read_from_stream(
        stream, word_separators + record_separators, token_words, evaluation.message
    )
    read_record = read_from_stream(
        stream, record_separators, token_words, evaluation.message
    )
    read_number = read_from_stream(
        stream,
        word_separators + record_separators,
        token_words,
        evaluation.message,
        ["+", "-", "."] + [str(i) for i in range(10)],
    )
    read_real = read_from_stream(
        stream,
        word_separators + record_separators,
        token_words,
        evaluation.message,
        ["+", "-", ".", "e", "E", "^", "*"] + [str(i) for i in range(10)],
    )

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
            elif typ in (SymbolExpression, SymbolHoldExpression):
                tmp = next(read_record)
                assert isinstance(tmp, str)
                while True:
                    try:
                        feeder = MathicsMultiLineFeeder(tmp, [], ContainerKind.STREAM)
                        expr = parse_incrementally_by_line(
                            evaluation.definitions, feeder
                        )
                        break
                    except (IncompleteSyntaxError, InvalidSyntaxError):
                        try:
                            nextline = next(read_record)
                            assert isinstance(nextline, str)
                            tmp = tmp + "\n" + nextline
                        except EOFError:
                            expr = SymbolEndOfFile
                            break
                    except Exception as e:
                        print(e)

                if expr is None:
                    result.append(None)
                elif expr is SymbolEndOfFile:
                    evaluation.message(name, "readt", tmp, String(stream.name))
                    return SymbolFailed
                elif isinstance(expr, BaseElement):
                    if typ is SymbolHoldExpression:
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
                            name, "readn", to_expression("InputSteam", name, n)
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
                        name, "readn", to_expression("InputSteam", name, n)
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
            elif typ is SymbolWord:
                # next() for word tokens can return one or two words:
                # the next word in the list and a following TokenWord
                # match.  Therefore, test for this and do list-like
                # appending here.

                # THINK ABOUT: We might need to reconsider/refactor
                # other cases to allow for multiple words as well. And
                # for uniformity, we may want to redo the generators to
                # always return *lists* instead instead of either a
                # word or a list (which is always at most two words?)
                words = next(read_word)
                if not isinstance(words, list):
                    words = [words]
                result += words

        except EOFError:
            return SymbolEndOfFile
        except UnicodeDecodeError:
            evaluation.message(name, "ucdec")

    if isinstance(result, Symbol):
        return result
    if isinstance(result, list):
        result_len = len(result)
        if result_len == 0:
            if SymbolHoldExpression in types:
                return Expression(SymbolHold, SymbolNull)
        elif result_len == 2 and SymbolWord in types:
            return [from_python(part) for part in result]
        elif result_len == 1:
            result = result[0]
            if SymbolHoldExpression in types:
                if hasattr(result, "head") and result.head is SymbolHold:
                    return from_python(result)
                else:
                    return Expression(SymbolHold, from_python(result))

    return from_python(result)
