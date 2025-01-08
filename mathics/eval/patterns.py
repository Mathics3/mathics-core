from typing import Optional as OptionalType

from mathics.core.atoms import Integer
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.pattern import BasePattern, StopGenerator
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolDefault


class _StopGeneratorMatchQ(StopGenerator):
    pass


class Matcher:
    def __init__(self, form, evaluation):
        if isinstance(form, BasePattern):
            self.form = form
        else:
            self.form = BasePattern.create(form, evaluation=evaluation)

    def match(self, expr, evaluation: Evaluation):
        def yield_func(vars, rest):
            raise _StopGeneratorMatchQ(True)

        try:
            self.form.match(
                expr,
                {"yield_func": yield_func, "vars_dict": {}, "evaluation": evaluation},
            )
        except _StopGeneratorMatchQ:
            return True
        return False


def get_default_value(
    name: str,
    evaluation: Evaluation,
    k: OptionalType[int] = None,
    n: OptionalType[int] = None,
):
    """
    Get the default value associated to a name, and optionally,
    to a position in the expression.
    """
    pos = []
    if k is not None:
        pos.append(k)
    if n is not None:
        pos.append(n)
    for pos_len in reversed(range(len(pos) + 1)):
        # Try patterns from specific to general
        defaultexpr = Expression(
            SymbolDefault, Symbol(name), *[Integer(index) for index in pos[:pos_len]]
        )
        try:
            result = evaluation.definitions.get_value(
                name, "System`DefaultValues", defaultexpr, evaluation
            )
        except ValueError:
            continue

        if result.sameQ(defaultexpr):
            result = result.evaluate(evaluation)
        return result
    return None


def match(expr, form, evaluation: Evaluation):
    return Matcher(form, evaluation).match(expr, evaluation)
