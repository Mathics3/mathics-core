# -*- coding: utf-8 -*-
"""
Tracing Built-in Functions

Built-in Function Tracing provides one high-level way understand what is \
getting evaluated and where the time is spent in evaluation.

With this, it may be possible for both users and implementers to follow \
how Mathics3 arrives at its results, or guide how to speed up expression \
evaluation.
"""


from collections import defaultdict
from time import time
from typing import Callable

from mathics.builtin.base import Builtin
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED
from mathics.core.convert.python import from_bool
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.rules import BuiltinRule
from mathics.core.symbols import SymbolFalse, SymbolNull, SymbolTrue, strip_context


def traced_do_replace(self, expression, vars, options: dict, evaluation: Evaluation):
    if options and self.check_options:
        if not self.check_options(options, evaluation):
            return None
    vars_noctx = dict(((strip_context(s), vars[s]) for s in vars))
    if self.pass_expression:
        vars_noctx["expression"] = expression
    builtin_name = self.function.__qualname__.split(".")[0]
    stat = TraceBuiltins.function_stats[builtin_name]
    ts = time()

    stat["count"] += 1
    if options:
        result = self.function(evaluation=evaluation, options=options, **vars_noctx)
    else:
        result = self.function(evaluation=evaluation, **vars_noctx)
    te = time()
    elapsed = (te - ts) * 1000
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


    If '$TraceBuiltins' was never set to 'True', this will print an empty list.
    >> PrintTrace[]

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


    >> TraceBuiltins[Graphics3D[Tetrahedron[]]]
     = -Graphics3D-

    By default, the output is sorted by the number of calls of the builtin from highest to lowest:
    >> TraceBuiltins[Times[x, x], SortBy->"count"]
     = x ^ 2

    You can have results ordered by name, or time.

    Trace an expression and list the result by time from highest to lowest.
    >> TraceBuiltins[Times[x, x], SortBy->"time"]
     = x ^ 2
    """

    definitions_copy: Definitions
    do_replace_copy: Callable

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

        print("count     ms Builtin name")

        if sort_by == "count":
            inverse = True
            sort_fn = lambda tup: tup[1]["count"]
        elif sort_by == "time":
            inverse = True
            sort_fn = lambda tup: tup[1]["elapsed_milliseconds"]
        else:
            inverse = False
            sort_fn = lambda tup: tup[0]

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
            TraceBuiltins.do_replace_copy = BuiltinRule.do_replace
            TraceBuiltins.definitions_copy = evaluation.definitions

            # Replaces do_replace by the custom one
            BuiltinRule.do_replace = traced_do_replace
            # Create new definitions uses the new do_replace
            evaluation.definitions = Definitions(add_builtin=True)
        else:
            evaluation.definitions = TraceBuiltins.definitions_copy

    @staticmethod
    def disable_trace(evaluation) -> None:
        BuiltinRule.do_replace = TraceBuiltins.do_replace_copy
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

    Setting this variable True will enable statistics collection for Built-in functions that are evaluated.
    In contrast to 'TraceBuiltins[]' statistics are accumulated and over several inputs, and are not shown after each input is evaluated.
    By default this setting is False.

    >> $TraceBuiltins = True
     = True

    ## We shouldn't let this enabled.
    #> $TraceBuiltins = False
     = False

    Tracing is enabled, so the expressions entered and evaluated will have statistics collected for the evaluations.
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
    summary_text = "trace the succesive evaluations"

    def eval(self, expr, evaluation: Evaluation, options: dict):
        "TraceEvaluation[expr_, OptionsPattern[]]"
        curr_trace_evaluation = evaluation.definitions.trace_evaluation
        curr_time_by_steps = evaluation.definitions.timing_trace_evaluation
        evaluation.definitions.trace_evaluation = True
        evaluation.definitions.timing_trace_evaluation = (
            options["System`ShowTimeBySteps"] is SymbolTrue
        )
        result = expr.evaluate(evaluation)
        evaluation.definitions.trace_evaluation = curr_trace_evaluation
        evaluation.definitions.timing_trace_evaluation = curr_time_by_steps
        return result


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
