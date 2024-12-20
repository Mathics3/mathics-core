# -*- coding: utf-8 -*-
"""
Tracing and Profiling

The 'Trace' builtins provide a Mathics3-oriented trace of what is \
getting evaluated and where the time is spent in evaluation.

With this, it may be possible for both users and implementers to follow \
how Mathics3 arrives at its results, or guide how to speed up expression \
evaluation.

Python <url>:CProfile:https://docs.python.org/3/library/profile.html</url> \
profiling is available via 'PythonCProfileEvaluation'.
"""


import cProfile
import pstats
import sys
from collections import defaultdict
from io import StringIO
from time import time
from typing import Callable

import mathics.eval.trace
import mathics.eval.tracing
from mathics.core.attributes import A_HOLD_ALL, A_HOLD_ALL_COMPLETE, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.convert.python import from_bool, from_python
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import FunctionApplyRule
from mathics.core.symbols import SymbolFalse, SymbolNull, SymbolTrue, strip_context


def traced_apply_function(
    self, expression, vars, options: dict, evaluation: Evaluation
):
    if options and self.check_options:
        if not self.check_options(options, evaluation):
            return None
    vars_noctx = dict(((strip_context(s), vars[s]) for s in vars))
    if self.pass_expression:
        vars_noctx["expression"] = expression
    builtin_name = self.function.__qualname__.split(".")[0]
    stat = TraceBuiltins.function_stats[builtin_name]
    t_start = time()

    stat["count"] += 1
    if options:
        result = self.function(evaluation=evaluation, options=options, **vars_noctx)
    else:
        result = self.function(evaluation=evaluation, **vars_noctx)
    t_end = time()
    elapsed = (t_end - t_start) * 1000
    stat["elapsed_milliseconds"] += elapsed
    return result


class _TraceBase(Builtin):
    options = {
        "SortBy": '"count"',
    }

    messages = {
        "wsort": '`1` must be one of the following: "count", "name", "time"',
    }


class ClearTrace(Builtin):
    """
    ## <url>:trace native symbol:</url>

    <dl>
      <dt>'ClearTrace[]'
      <dd>Clear the statistics collected for Built-in Functions
    </dl>

    First, set up Builtin-function tracing:
    >> $TraceBuiltins = True
     = True

    Dump Builtin-Function statistics gathered in running that assignment:
    >> PrintTrace[]

    >> ClearTrace[]

    #> $TraceBuiltins = False
    = False
    """

    summary_text = "clear any statistics collected for Built-in functions"

    def eval(self, evaluation: Evaluation):
        "%(name)s[]"

        TraceBuiltins.function_stats: "defaultdict" = defaultdict(
            lambda: {"count": 0, "elapsed_milliseconds": 0.0}
        )

        return SymbolNull


class PrintTrace(_TraceBase):
    """
    ## <url>:trace native symbol:</url>

    <dl>
      <dt>'PrintTrace[]'
      <dd>Print statistics collected for Built-in Functions
    </dl>

    Sort Options:

    <ul>
      <li>count
      <li>name
      <li>time
    </ul>

    Note that in a browser the information only appears in a console.


    Note: before '$TraceBuiltins' is set to 'True', 'PrintTrace[]' will print an empty
    list.
    >> PrintTrace[] (* See console log *)

    >> $TraceBuiltins = True
     = True

    >> PrintTrace[SortBy -> "time"]

    #> $TraceBuiltins = False
     = False
    """

    summary_text = "print statistics collected for Built-in functions"

    def eval(self, evaluation, options={}):
        "%(name)s[OptionsPattern[%(name)s]]"

        TraceBuiltins.dump_tracing_stats(
            sort_by=self.get_option(options, "SortBy", evaluation).get_string_value(),
            evaluation=evaluation,
        )

        return SymbolNull


class Stacktrace(_TraceBase):
    """
    ## <url>:trace native symbol:</url>

    <dl>
      <dt>'Stacktrace[]'
      <dd>Print Mathics3 stack trace of evalutations leading to this point
    </dl>

    To show the Mathics3 evaluation stack at the \
    point where expression $expr$ is evaluated, wrap $expr$ inside '{$expr$ Stacktrace[]}[1]]' \
    or something similar.

    Here is a complete example. To show the evaluation stack when computing a homegrown \
    factorial function:

    >> F[0] := {1, Stacktrace[]}[[1]]; F[n_] := n * F[n-1]
     = None

    >> F[3] (* See console log *)
      = None

    The actual 'Stacktrace[0]' call is hidden from the output; so when \
    run on its own, nothing appears.

    >> Stacktrace[]
     = None

    #> Clear[F]
    """

    summary_text = "print Mathics3 function stacktrace"

    def eval(self, evaluation: Evaluation):
        "Stacktrace[]"

        # Use longer-form resolve call
        # so a debugger can change this.
        mathics.eval.trace.eval_Stacktrace()
        return SymbolNull


class TraceBuiltins(_TraceBase):
    """
    ## <url>:trace native symbol:</url>

    <dl>
      <dt>'TraceBuiltins[$expr$]'
      <dd>Evaluate $expr$ and then print a list of the Built-in Functions called \
          in evaluating $expr$ along with the number of times is each called, \
          and combined elapsed time in milliseconds spent in each.
    </dl>

    Sort Options:

    <ul>
      <li>count
      <li>name
      <li>time
    </ul>


    >> TraceBuiltins[Graphics3D[Tetrahedron[]]] (* See console log *)
     = -Graphics3D-

    By default, the output is sorted by the name:
    >> TraceBuiltins[Times[x, x]] (* See console log *)
     = x ^ 2

    By default, the output is sorted by the number of calls of the builtin from \
    highest to lowest:
    >> TraceBuiltins[Times[x, x], SortBy->"count"] (* See console log *)
     = x ^ 2

    You can have results ordered by name, or time.

    Trace an expression and list the result by time from highest to lowest.
    >> TraceBuiltins[Times[x, x], SortBy->"time"] (* See console log *)
     = x ^ 2
    """

    definitions_copy: Definitions
    apply_function_copy: Callable

    function_stats: "defaultdict" = defaultdict(
        lambda: {"count": 0, "elapsed_milliseconds": 0.0}
    )

    summary_text = (
        "evaluate an expression and print statistics on Built-in functions called"
    )

    traced_definitions: Evaluation = None

    @staticmethod
    def dump_tracing_stats(sort_by: str, evaluation) -> None:
        if sort_by not in ("count", "name", "time"):
            evaluation.message("TraceBuiltins", "wsort", sort_by)
            sort_by = "count"
            print()

        def sort_by_count(tup: tuple):
            return tup[1]["count"]

        def sort_by_time(tup: tuple):
            return tup[1]["elapsed_milliseconds"]

        def sort_by_name(tup: tuple):
            return tup[0]

        print("count     ms Builtin name")

        if sort_by == "count":
            inverse = True
            sort_fn = sort_by_count
        elif sort_by == "time":
            inverse = True
            sort_fn = sort_by_time
        else:
            inverse = False
            sort_fn = sort_by_name

        for name, statistic in sorted(
            TraceBuiltins.function_stats.items(),
            key=sort_fn,
            reverse=inverse,
        ):
            print(
                "%5d %6g %s"
                % (statistic["count"], int(statistic["elapsed_milliseconds"]), name)
            )

    @staticmethod
    def enable_trace(evaluation) -> None:
        if TraceBuiltins.traced_definitions is None:
            TraceBuiltins.apply_function_copy = FunctionApplyRule.apply_function
            TraceBuiltins.definitions_copy = evaluation.definitions

            # Replaces apply_function by the custom one
            FunctionApplyRule.apply_function = traced_apply_function
            # Create new definitions uses the new apply_function
            evaluation.definitions = Definitions(add_builtin=True)
        else:
            evaluation.definitions = TraceBuiltins.definitions_copy

    @staticmethod
    def disable_trace(evaluation) -> None:
        FunctionApplyRule.apply_function = TraceBuiltins.apply_function_copy
        evaluation.definitions = TraceBuiltins.definitions_copy

    def eval(self, expr, evaluation, options={}):
        "%(name)s[expr_, OptionsPattern[%(name)s]]"

        # Reset function_stats
        TraceBuiltins.function_stats = defaultdict(
            lambda: {"count": 0, "elapsed_milliseconds": 0.0}
        )

        self.enable_trace(evaluation)
        result = expr.evaluate(evaluation)
        self.disable_trace(evaluation)

        self.dump_tracing_stats(
            sort_by=self.get_option(options, "SortBy", evaluation).get_string_value(),
            evaluation=evaluation,
        )

        return result


# The convention is to use the name of the variable without the "$" as
# the class name, but it is already taken by the builtin `TraceBuiltins`
class TraceBuiltinsVariable(Builtin):
    """
    ## <url>:trace native symbol:</url>

    <dl>
      <dt>'$TraceBuiltins'
      <dd>A Boolean Built-in variable when True collects function evaluation statistics.
    </dl>

    Setting this variable True will enable statistics collection for Built-in \
    functions that are evaluated.
    In contrast to 'TraceBuiltins[]' statistics are accumulated and over several \
    inputs,and are not shown after each input is evaluated.

    By default, this setting is False.

    >> $TraceBuiltins = True
     = True

    ## We shouldn't let this enabled.
    #> $TraceBuiltins = False
     = False

    Tracing is enabled, so the expressions entered and evaluated will have statistics \
    collected for the evaluations.
    >> x
     = x

    To print the statistics collected, use 'PrintTrace[]':
    X> PrintTrace[]

    To  clear statistics collected use 'ClearTrace[]':
    X> ClearTrace[]

    '$TraceBuiltins'  cannot be set to a non-boolean value.
    >> $TraceBuiltins = x
     : x should be True or False.
     = x
    """

    name = "$TraceBuiltins"

    messages = {"bool": "`1` should be True or False."}

    value = SymbolFalse

    summary_text = "enable or disable Built-in function evaluation statistics"

    def eval_get(self, evaluation: Evaluation):
        "%(name)s"

        return self.value

    def eval_set(self, value, evaluation: Evaluation):
        "%(name)s = value_"

        if value is SymbolTrue:
            self.value = SymbolTrue
            TraceBuiltins.enable_trace(evaluation)
        elif value is SymbolFalse:
            self.value = SymbolFalse
            TraceBuiltins.disable_trace(evaluation)
        else:
            evaluation.message("$TraceBuiltins", "bool", value)

        return value


class TraceEvaluation(Builtin):
    """
    ## <url>:trace native symbol:</url>

    <dl>
      <dt>'TraceEvaluation[$expr$]'
      <dd>Evaluate $expr$ and print each step of the evaluation.
    </dl>

    The 'ShowTimeBySteps' option prints the elapsed time before an evaluation occurs.

    >> TraceEvaluation[(x + x)^2]
     | ...
     = ...

    >> TraceEvaluation[(x + x)^2, ShowTimeBySteps->True]
     | ...
     = ...
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    options = {
        "System`ShowTimeBySteps": "False",
    }
    summary_text = "trace expression evaluation"

    def eval(self, expr, evaluation: Evaluation, options: dict):
        "TraceEvaluation[expr_, OptionsPattern[]]"

        curr_trace_evaluation = evaluation.definitions.trace_evaluation
        curr_time_by_steps = evaluation.definitions.timing_trace_evaluation

        old_evaluation_call_hook = mathics.eval.tracing.trace_evaluate_on_call
        old_evaluation_return_hook = mathics.eval.tracing.trace_evaluate_on_return

        mathics.eval.tracing.trace_evaluate_on_call = (
            mathics.eval.tracing.print_evaluate
        )

        mathics.eval.tracing.trace_evaluate_on_return = (
            mathics.eval.tracing.print_evaluate
        )

        evaluation.definitions.trace_evaluation = True
        evaluation.definitions.timing_trace_evaluation = (
            options["System`ShowTimeBySteps"] is SymbolTrue
        )
        try:
            result = expr.evaluate(evaluation)
            return result
        except Exception:
            raise
        finally:
            evaluation.definitions.trace_evaluation = curr_trace_evaluation
            evaluation.definitions.timing_trace_evaluation = curr_time_by_steps

            mathics.eval.tracing.trace_evaluate_on_call = old_evaluation_call_hook
            mathics.eval.tracing.trace_evaluate_on_return = old_evaluation_return_hook


class TraceEvaluationVariable(Builtin):
    """
    ## <url>:trace native symbol:</url>

    <dl>
      <dt>'$TraceEvaluation'
      <dd>A Boolean variable which when set True traces Expression evaluation calls and returns.
    </dl>

    >> $TraceEvaluation = True
     | ...
     = True

    >> a + a
     | ...
     = 2 a

    Setting it to 'False' again recovers the normal behaviour:
    >> $TraceEvaluation = False
     | ...
     = False
    >> $TraceEvaluation
     = False

    >> a + a
     = 2 a
    '$TraceEvaluation' cannot be set to a non-boolean value.
    >> $TraceEvaluation = x
     : x should be True or False.
     = x
    """

    name = "$TraceEvaluation"

    messages = {"bool": "`1` should be True or False."}

    value = SymbolFalse

    summary_text = "enable or disable displaying the steps to get the result"

    def eval_get(self, evaluation: Evaluation):
        "%(name)s"
        return from_bool(evaluation.definitions.trace_evaluation)

    def eval_set(self, value, evaluation: Evaluation):
        "%(name)s = value_"
        if value is SymbolTrue:
            evaluation.definitions.trace_evaluation = True
        elif value is SymbolFalse:
            evaluation.definitions.trace_evaluation = False
        else:
            evaluation.message("$TraceEvaluation", "bool", value)

        return value


class PythonCProfileEvaluation(Builtin):
    """
    <url>:Python:https://docs.python.org/3/library/profile.html</url>

    <dl>
      <dt>'PythonProfileEvaluation[$expr$]'
      <dd>profile $expr$ with the Python's cProfiler.
    </dl>

    ## This produces an error in the LaTeX documentation.
    ## >> PythonCProfileEvaluation[a + b + 1]
    ##  = ...
    """

    attributes = A_HOLD_ALL_COMPLETE | A_PROTECTED
    summary_text = "profile the internal evaluation of an expression"

    def eval(self, expr: Expression, evaluation: Evaluation):
        "PythonCProfileEvaluation[expr_]"
        profile_result = SymbolNull
        textstream = StringIO()
        if sys.version_info >= (3, 8):
            with cProfile.Profile() as pr:
                result = expr.evaluate(evaluation)
                stats = pstats.Stats(pr, stream=textstream)
            stats.strip_dirs().sort_stats(-1).print_stats()
            # TODO: convert the string (or the statistics)
            # into something like a WL Table, by splitting the
            # rows and the columns. By now, just a string
            # is returned.
            profile_result = from_python(textstream.getvalue())
        else:
            result = expr.evaluate(evaluation)
        return ListExpression(result, profile_result)
