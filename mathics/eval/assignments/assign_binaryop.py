"""
evaluation functions associated with the mathics.builtin.assign_binary_op
module.
"""

from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolSet


def eval_inplace_op(
    self, x, operator, increment, returns_updated_value: bool, evaluation: Evaluation
):
    """
    Perform: Set[x, operator[x, increment]]

    For example if operator is + and increment is 1, perform x += 1

    If returns_updated_value is True, return the value after performing
    the update operation. Otherwise return the value before it was
    modified.
    """
    value_before_update = x.evaluate(evaluation)
    if x == value_before_update:
        evaluation.message(self.__class__.__name__, "rvalue", x)
        return

    updated_value = Expression(
        SymbolSet, x, Expression(operator, x, increment).evaluate(evaluation)
    ).evaluate(evaluation)
    return updated_value if returns_updated_value else value_before_update
