"""
Evaluation routines for builtins in mathics.builtin.associations.modifying
"""

from typing import Optional

from mathics.core.atoms.associations import Association
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.core.rules import is_rule
from mathics.core.symbols import Symbol


def eval_AssociateTo(
    a: BaseElement, expr: BaseElement, evaluation: Evaluation
) -> Optional[Association]:
    """AssociateTo[a_, expr_]"""

    # FIXME we should check if a is protected. And readible? And Writeable?
    if isinstance(a, Symbol):
        assoc_value = a.evaluate(evaluation)
    else:
        assoc_value = expr

    if not isinstance(assoc_value, Association):
        evaluation.message("AssociateTo", "invak", assoc_value)
        return

    if is_rule(expr):
        changed = Association([expr])
    elif isinstance(expr, ListExpression):
        changed = Association(expr.elements)
    else:
        changed = expr

    if not isinstance(changed, Association):
        evaluation.message("AssociateTo", "invlb", expr)
        return

    assoc_value.update(changed.collection)
    return assoc_value
