"""
Debugging
"""

from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation
from mathics.eval.debug_tuning.dialog import eval_Dialog


class Dialog(Builtin):
    r"""
    <url>:WMA link: https://reference.wolfram.com/language/ref/Dialog.html</url>

    <dl>
      <dt>'Dialog[]'
      <dd>Enters a \Mathics3 shell in the context that the call appears in a \Mathics3 expression.
    </dl>
    """

    attributes = A_HOLD_ALL | A_PROTECTED
    summary_text = "enter Mathics3 REPL shell in the context of the call"

    def eval(self, evaluation: Evaluation):
        "Dialog[]"
        return eval_Dialog(evaluation)
