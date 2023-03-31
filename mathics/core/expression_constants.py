from typing import Tuple

from mathics.core.atoms import (
    MATHICS3_COMPLEX_I,
    MATHICS3_COMPLEX_I_NEG,
    Complex,
    Integer,
    Integer0,
    Integer1,
    IntegerM1,
    String,
)
from mathics.core.element import BaseElement, ElementsProperties
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolDirectedInfinity


class ConstantExpression(Expression):
    def __init__(
        self,
        head: BaseElement,
        *elements: Tuple[BaseElement],
    ):
        elements_properties = ElementsProperties(True, True, True)
        super().__init__(head, *elements, elements_properties=elements_properties)

    def evaluate(self, evaluation: Evaluation):
        return self


MATHICS3_COMPLEX_INFINITY = ConstantExpression(SymbolDirectedInfinity)
MATHICS3_INFINITY = ConstantExpression(SymbolDirectedInfinity, Integer1)
MATHICS3_NEG_INFINITY = ConstantExpression(SymbolDirectedInfinity, IntegerM1)
MATHICS3_I_INFINITY = ConstantExpression(SymbolDirectedInfinity, MATHICS3_COMPLEX_I)
MATHICS3_I_NEG_INFINITY = ConstantExpression(
    SymbolDirectedInfinity, MATHICS3_COMPLEX_I_NEG
)
