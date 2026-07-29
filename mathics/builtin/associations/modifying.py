"""
Modifying Associations
"""

from typing import Optional

from mathics.core.atoms.associations import Association
from mathics.core.attributes import A_HOLD_FIRST, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.eval.associations.modifying import eval_AssociateTo, eval_KeyDropFrom


class AssociateTo(Builtin):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/AssociateTo.html</url>

    <dl>
      <dt>'AssociateTo'[$a$, $key$ -> $val$]
      <dd>Adds key-value pair $key$ -> $val$ to $a$.

    </dl>

    Create an association
    >> assoc = Association[{a -> 1, b -> 2, c -> 3}]
     = <|a ⇾ 1, b ⇾ 2, c ⇾ 3|>

    Change the value associated with key $a$:
    >> AssociateTo[assoc, a -> 10]
     = <|a ⇾ 10, b ⇾ 2, c ⇾ 3|>

    Add key $d$ rather than change it since it is not already in $a$:
    >> AssociateTo[assoc, d->4]
     = <|a ⇾ 10, b ⇾ 2, c ⇾ 3, d ⇾ 4|>

    Change and add keys using several keys-value pairs:
    >> AssociateTo[assoc, {d -> 5, e-> f}]
     = <|a ⇾ 10, b ⇾ 2, c ⇾ 3, d ⇾ 5, e ⇾ f|>
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = 2

    summary_text = "update an Association"

    def eval(
        self, a: BaseElement, expr: BaseElement, evaluation: Evaluation
    ) -> Optional[Association]:
        """AssociateTo[a_, expr_]"""

        return eval_AssociateTo(a, expr, evaluation)


class KeyDropFrom(Builtin):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/KeyDropFrom.html</url>

    <dl>
      <dt>'KeyDropFrom'[$a$, $key$]
      <dd>Removes key pair from association $a$.

    </dl>

    >> assoc = <|a ⇾ 1, b ⇾ 2|>
     = <|a ⇾ 1, b ⇾ 2|>
    >> KeyDropFrom[assoc, a]
     = <|b ⇾ 2|>

    >> KeyDropFrom[assoc, {b, d}]
     = <||>
    """

    attributes = A_HOLD_FIRST | A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = 2

    summary_text = "remove a key from an Association"

    def eval(
        self, a: BaseElement, key: BaseElement, evaluation: Evaluation
    ) -> Optional[Association]:
        """KeyDropFrom[a_, key_]"""

        return eval_KeyDropFrom(a, key, evaluation)
