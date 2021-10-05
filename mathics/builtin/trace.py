from mathics.version import __version__  # noqa used in loading to check consistency.

from mathics.builtin.base import Builtin
from mathics.core.rules import BuiltinRule
from mathics.core.symbols import strip_context
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation

from time import time
from collections import defaultdict


function_stats: "defauldict" = defaultdict(
    lambda: {"count": 0, "elapsed_milliseconds": 0.0}
)


def traced_do_replace(self, expression, vars, options, evaluation):
    if options and self.check_options:
        if not self.check_options(options, evaluation):
            return None
    vars_noctx = dict(((strip_context(s), vars[s]) for s in vars))
    if self.pass_expression:
        vars_noctx["expression"] = expression
    builtin_name = self.function.__qualname__.split(".")[0]
    stat = function_stats[builtin_name]
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
     : count msecs  Builtin name
     : ...
     = -Graphics3D-
    """

    custom_evaluation: Evaluation = None

    def dump_tracing_stats(self):
        print("count msecs  Builtin name")

        for name, statistic in sorted(
            function_stats.items(),
            key=lambda tup: tup[1]["count"],
            reverse=True,
        ):
            print(
                "%5d %6g %s"
                % (statistic["count"], int(statistic["elapsed_milliseconds"]), name)
            )

    def apply(self, expr, evaluation):
        "TraceBuiltins[expr_]"

        # Reset function_stats
        function_stats = defaultdict(lambda: {"count": 0, "elapsed_milliseconds": 0.0})

        if TraceBuiltins.custom_evaluation is None:
            do_replace_copy = BuiltinRule.do_replace

            # Replaces do_replace by the custom one
            BuiltinRule.do_replace = traced_do_replace

            # Create new definitions uses the new do_replace
            definitions = Definitions(add_builtin=True)
            TraceBuiltins.custom_evaluation = Evaluation(definitions=definitions)

            result = expr.evaluate(TraceBuiltins.custom_evaluation)

            # Reverts do_replace to what it was
            BuiltinRule.do_replace = do_replace_copy
        else:
            result = expr.evaluate(TraceBuiltins.custom_evaluation)

        self.dump_tracing_stats()

        return result
