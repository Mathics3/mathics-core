# -*- coding: utf-8 -*-
"""
File related evaluation functions.
"""

from typing import Callable, Literal, Optional

from mathics_scanner import TranslateError

import mathics
import mathics.core.parser
import mathics.core.streams
from mathics.core.builtin import MessageException
from mathics.core.evaluation import Evaluation
from mathics.core.parser.feed import MathicsFileLineFeeder
from mathics.core.read import MathicsOpen
from mathics.core.symbols import SymbolNull
from mathics.core.systemsymbols import SymbolFailed, SymbolPath
from mathics.core.util import canonic_filename

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
    print(f"%5d: {text}" % line_number, end="")


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
        evaluation.message("General", "noopen", path)
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
