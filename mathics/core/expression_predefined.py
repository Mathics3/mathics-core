"""
Module for defining constant compound Mathics3 expressions.
"""

import math
from typing import Final

from sympy import I, S

from mathics.core.atoms import (
    MATHICS3_COMPLEX_I,
    MATHICS3_COMPLEX_I_NEG,
    Integer1,
    IntegerM1,
)
from mathics.core.element import BaseElement, ElementsProperties
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolDirectedInfinity


class PredefinedExpression(Expression):
    """
    (Compound) constant Mathics3 Expressions.
    """

    def __init__(
        self,
        head: BaseElement,
        *elements: BaseElement,
        sympy=None,
        value=None,
    ):
        elements_properties = ElementsProperties(True, True, True)
        super().__init__(head, *elements, elements_properties=elements_properties)
        if sympy is not None:
            self._sympy = sympy
        if value is not None:
            self.value = value


MATHICS3_COMPLEX_INFINITY: Final = PredefinedExpression(SymbolDirectedInfinity)
MATHICS3_INFINITY: Final = PredefinedExpression(
    SymbolDirectedInfinity, Integer1, value=math.inf, sympy=S.Infinity
)
MATHICS3_NEG_INFINITY: Final = PredefinedExpression(
    SymbolDirectedInfinity, IntegerM1, value=-math.inf, sympy=S.NegativeInfinity
)
MATHICS3_I_INFINITY: Final = PredefinedExpression(
    SymbolDirectedInfinity, MATHICS3_COMPLEX_I, sympy=S.ComplexInfinity
)
MATHICS3_I_NEG_INFINITY: Final = PredefinedExpression(
    SymbolDirectedInfinity, MATHICS3_COMPLEX_I_NEG, sympy=-I
)
