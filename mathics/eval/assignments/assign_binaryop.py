from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolSet


def eval_inplace_op(
    self, x, operator, increment, return_before_value: bool, evaluation: Evaluation
):
    """
    Perform: Set[x, operator[x, increment]]

    For example if operator is + and increment is 1, perform x += 1
    """
    before_value = x.evaluate(evaluation)
    if x == before_value:
        evaluation.message(self.__class__.__name__, "rvalue", x)
        return

    after_value = Expression(
        SymbolSet, x, Expression(operator, x, increment).evaluate(evaluation)
    ).evaluate(evaluation)
    return before_value if return_before_value else after_value
