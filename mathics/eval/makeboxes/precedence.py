from typing import Dict, Optional

from mathics.core.atoms import Integer, Real, String
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRowBox

builtins_precedence: Dict[Symbol, int] = {}


def compare_precedence(
    element: BaseElement, precedence: Optional[int] = None
) -> Optional[int]:
    """
    compare the precedence of the element regarding a precedence value.
    If both precedences are equal, return 0. If precedence of the
    first element is higher, return 1, otherwise -1.
    If precedences cannot be compared, return None.
    """
    while element.has_form("HoldForm", 1):
        element = element.elements[0]

    if precedence is None:
        return None
    if element.has_form(("Infix", "Prefix", "Postfix"), 3, None):
        element_prec = element.elements[2].value
    elif element.has_form("PrecedenceForm", 2):
        element_prec = element.elements[1].value
    # For negative values, ensure that the element_precedence is at least the precedence. (Fixes #332)
    elif isinstance(element, (Integer, Real)) and element.value < 0:
        element_prec = precedence
    else:
        element_prec = builtins_precedence.get(element.get_head_name())

    if element_prec is None:
        return None
    return 0 if element_prec == precedence else (1 if element_prec > precedence else -1)


def parenthesize(
    precedence: Optional[int],
    element: Expression,
    element_boxes,
    when_equal: bool,
) -> Expression:
    """
    "Determines if ``element_boxes`` needs to be surrounded with parenthesis.
    This is done based on ``precedence`` and the computed preceence of
    ``element``.  The adjusted ListExpression is returned.

    If when_equal is True, parentheses will be added if the two
    precedence values are equal.
    """
    cmp = compare_precedence(element, precedence)
    if cmp is not None and (cmp == -1 or cmp == 0 and when_equal):
        return Expression(
            SymbolRowBox,
            ListExpression(String("("), element_boxes, String(")")),
        )
    return element_boxes
