from mathics.version import __version__  # noqa used in loading to check consistency.

from mathics.builtin.base import Builtin
from mathics.core.rules import BuiltinRule
from mathics.core.symbols import strip_context, SymbolTrue, SymbolFalse, SymbolNull
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation

from time import time
from collections import defaultdict
from typing import Callable


def traced_do_replace(self, expression, vars, options, evaluation):
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


class TraceBuiltins(Builtin):
    """
    <dl>
    <dt>'TraceBuiltins[$expr$]'
        <dd>Print the list of the called builtin names, count and time spend in their apply method. Returns the result of $expr$.
    </dl>

    >> TraceBuiltins[Graphics3D[Tetrahedron[]]]
     : count     ms Builtin name
     : ...
     = -Graphics3D-

    The default is sorting the builtin names by calls count.
    >> TraceBuiltins[Times[x, x], SortBy->"count"]
     : count     ms Builtin name
     : ...
     = x^2

    But you can also sort by name, or time.

    The default is sorting the builtin names by type.
    >> TraceBuiltins[Plus @@ {1, x, x x}, SortBy->"name"]
     : count     ms Builtin name
     : ...
     = 1 + x + x^2
    """

    options = {
        "SortBy": "count",
    }

    messages = {
        "wsort": '`1` must be one of the following: "count", "name", "time"',
    }

    traced_definitions: Evaluation = None
    definitions_copy: Definitions
    do_replace_copy: Callable

    function_stats: "defauldict" = defaultdict(
        lambda: {"count": 0, "elapsed_milliseconds": 0.0}
    )

    @staticmethod
    def dump_tracing_stats(sort_by: str, evaluation) -> None:
        if sort_by not in ("count", "name", "time"):
            sort_by = "count"
            evaluation.message("TraceBuiltins", "wsort", sort_by)
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

    def apply(self, expr, evaluation, options={}):
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
    <dl>
    <dt>'$TraceBuiltins'
        <dd>Setting this enable/disable tracing. It defaults to False.
    </dl>

    >> $TraceBuiltins = True
     = True
    Now tracing is enabled.
    >> x
     = x
    You can print it with 'PrintTrace[]' and clear it with 'ClearTrace[]'.
    >> PrintTrace[]
     : count     ms Builtin name
     : ...
     = Null

    >> $TraceBuiltins = False
     = False

    It can't be set to a non-boolean.
    >> $TraceBuiltins = x
     : Set::wrsym: Symbol $TraceBuiltins is Protected.
     = x
    """

    name = "$TraceBuiltins"
    value = SymbolFalse

    def apply_get(self, evaluation):
        "%(name)s"

        return self.value

    def apply_set_true(self, evaluation):
        "%(name)s = True"

        self.value = SymbolTrue
        TraceBuiltins.enable_trace(evaluation)

        return SymbolTrue

    def apply_set_false(self, evaluation):
        "%(name)s = False"

        self.value = SymbolFalse
        TraceBuiltins.disable_trace(evaluation)

        return SymbolFalse


class PrintTrace(Builtin):
    """
    <dl>
    <dt>'PrintTrace[]'
        <dd>Print the builtin trace.
    </dl>

    If '$TraceBuiltins' was never set to 'True', this will print an empty list.
    >> PrintTrace[]
     : count     ms Builtin name
     = Null

    >> $TraceBuiltins = True

    >> PrintTrace[]
     : count     ms Builtin name
     : ...
     = Null

    #> $TraceBuiltins = False
    """

    def apply(self, evaluation):
        "%(name)s[]"

        TraceBuiltins.dump_tracing_stats(
            sort_by="count",
            evaluation=evaluation,
        )

        return SymbolNull
