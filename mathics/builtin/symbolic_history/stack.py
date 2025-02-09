# from mathics.core.atoms import Integer2
from mathics.core.attributes import A_HOLD_ALL, A_HOLD_FIRST, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression

# from mathics.core.systemsymbols import SymbolTrace
from mathics.eval.symbolic_history.stack import eval_Stack, eval_Trace


class Stack(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Stack.html</url>

    <dl>
      <dt>'Stack[]'
      <dd>Print Mathics3 stack trace of evalutations leading to this point.
    </dl>

    >> f[g[1, Print[Stack[]] ; 2]]
     = {f[g[1, Print[Stack[]] ; 2]], g[1, Print[Stack[]] ; 2], Print[Stack[]] ; 2, CompoundExpression, Print[Stack[]]}


    The actual 'Stack[0]' call is hidden from the output; so when \
    run on its own, nothing appears.

    >> Stack[]
     = {}
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    summary_text = "print Mathics3 function stacktrace"

    def eval(self, evaluation: Evaluation) -> ListExpression:
        "Stack[]"

        return eval_Stack()


class Trace(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Trace.html</url>

    <dl>
      <dt>'Trace'[$expr$]
      <dd>generate a list of all expressions used in the evaluation of $expr$.
    </dl>

    >> Trace[1 + 2]
     = {1 + 2, 3}
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "list intermediary expressions in an evaluation"

    def eval(self, expr, evaluation: Evaluation) -> ListExpression:
        "Trace[expr__]"

        # n = len(expr.elements)
        # if n > 2:
        #     evaluation.message("Trace", "nonopt", TraceSymbol, Integer2
        #                        Expression[TraceSymbol]
        #     return
        return eval_Trace(expr, evaluation)
