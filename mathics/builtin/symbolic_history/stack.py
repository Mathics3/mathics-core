from mathics.core.attributes import A_HOLD_FIRST, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.eval.symbolic_history.stack import eval_Stack


class Stack(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Stack.html</url>

    <dl>
      <dt>'Stack[]'
      <dd>Print Mathics3 stack trace of evalutations leading to this point
    </dl>

    To show the Mathics3 evaluation stack at the \
    point where expression $expr$ is evaluated, wrap $expr$ inside '{$expr$ Stacktrace[]}[1]]' \
    or something similar.

    Here is a complete example. To show the evaluation stack when computing a homegrown \
    factorial function:

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
