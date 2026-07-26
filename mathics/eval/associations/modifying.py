"""
Evaluation routines for builtins in mathics.builtin.associations.modifying
"""

from typing import Optional

from mathics.core.atoms.associations import Association
from mathics.core.attributes import A_PROTECTED
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import is_rule
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolAssociation


def eval_AssociateTo(
    a: BaseElement, expr: BaseElement, evaluation: Evaluation
) -> Optional[Association]:
    """AssociateTo[a_, expr_]"""

    # FIXME: we should test for Readable? And Writable?
    attributes = 0
    if isinstance(a, Symbol):
        assoc_value = a.evaluate(evaluation)
        attributes = evaluation.definitions.get_attributes(a.name)
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

    if (attributes & A_PROTECTED) or isinstance(a, Expression):
        evaluation.message("Set", "write", SymbolAssociation, a)
        return

    if not isinstance(changed, Association):
        evaluation.message("AssociateTo", "invlb", expr)
        return

    assoc_value.update(changed.collection)
    return assoc_value


def eval_KeyDropFrom(
    a: BaseElement, key: BaseElement, evaluation: Evaluation
) -> Optional[Association]:
    """KeyDropFrom[a_, key_]"""

    # FIXME: we should test for Readable? And Writable?
    attributes = 0
    if isinstance(a, Symbol):
        assoc_value = a.evaluate(evaluation)
        attributes = evaluation.definitions.get_attributes(a.name)
    else:
        assoc_value = a

    if (attributes & A_PROTECTED) or isinstance(a, Expression):
        evaluation.message("Set", "write", SymbolAssociation, a)
        return

    if not isinstance(assoc_value, Association):
        # If it's not an association, we might just return it or handle errors.
        return a

    if isinstance(key, ListExpression):
        keys = key.elements
    else:
        keys = [key]
    for key in keys:
        assoc_value.pop(key)
    return assoc_value
