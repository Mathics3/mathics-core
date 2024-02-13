# -*- coding: utf-8 -*-
# cython: language_level=3

"""
files-related evaluation functions
"""

import os.path as osp

from mathics_scanner import TranslateError

import mathics
from mathics.core.builtin import MessageException
from mathics.core.evaluation import Evaluation
from mathics.core.parser import MathicsFileLineFeeder, parse
from mathics.core.read import MathicsOpen
from mathics.core.symbols import Symbol, SymbolFullForm, SymbolNull, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolFailed,
    SymbolHold,
    SymbolInputForm,
    SymbolOutputForm,
    SymbolReal,
)

SymbolPath = Symbol("$Path")


# Reads a file and evaluates each expression, returning only the last one.
def eval_Get_inner(self, path, evaluation: Evaluation, options: dict):
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
