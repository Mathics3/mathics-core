# -*- coding: utf-8 -*-
"""
File related evaluation functions.
"""

from typing import Callable, Literal, Optional

from mathics_scanner import TranslateError
from mathics_scanner.errors import IncompleteSyntaxError, InvalidSyntaxError

import mathics
import mathics.core.parser
import mathics.core.streams
from mathics.core.builtin import MessageException
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import BaseElement, Expression
from mathics.core.parser import MathicsFileLineFeeder, MathicsMultiLineFeeder, parse
from mathics.core.symbols import Symbol, SymbolNull
from mathics.core.systemsymbols import (
    SymbolEndOfFile,
    SymbolFailed,
    SymbolHold,
    SymbolHoldExpression,
    SymbolPath,
    SymbolReal,
)
from mathics.core.util import canonic_filename
from mathics.eval.files_io.read import (
    READ_TYPES,
    MathicsOpen,
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


def set_input_var(input_string: str):
    """
    Allow INPUT_VAR to get set, e.g. from main program.
    """
    global INPUT_VAR
    INPUT_VAR = canonic_filename(input_string)


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
                except TranslateError:
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


def eval_Read(name: str, n: int, types, stream, evaluation: Evaluation, options: dict):
    # Wrap types in a list (if it isn't already one)
    if types.has_form("List", None):
        types = types.elements
    else:
        types = (types,)

    # TODO: look for a better implementation handling "Hold[Expression]".
    #
    types = (
        (
            SymbolHoldExpression
            if (
                typ.get_head_name() == "System`Hold"
                and typ.elements[0].get_name() == "System`Expression"
            )
            else typ
        )
        for typ in types
    )
    types = to_mathics_list(*types)

    for typ in types.elements:
        if typ not in READ_TYPES:
            evaluation.message("Read", "readf", typ)
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
            elif typ is Symbol("Expression") or typ is SymbolHoldExpression:
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
