"""
Debugging
"""

from mathics.core.atoms import Integer
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.rules import Rule
from mathics.core.systemsymbols import SymbolOut
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

    def eval(self, expr: BaseElement, evaluation: Evaluation):
        "Dialog[expr_]"
        definitions = evaluation.definitions
        definitions.add_rule(
            "Out", Rule(Expression(SymbolOut, Integer(definitions.get_line_no())), expr)
        )

        return eval_Dialog(evaluation)
