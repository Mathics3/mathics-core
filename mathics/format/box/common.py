"""
Util functions for box processing.
"""

from typing import Tuple

from mathics.builtin.box.expression import BoxExpression
from mathics.builtin.options import filter_non_default_values, options_to_rules
from mathics.core.element import BaseElement


def elements_to_expressions(
    self: BoxExpression, elements: Tuple[BaseElement], options: dict
) -> Tuple[BaseElement]:
    """
    Return a tuple of Mathics3 normal atoms or expressions.
    """
    opts = sorted(options_to_rules(options, filter_non_default_values(self)))
    expr_elements = [
        elem.to_expression() if isinstance(elem, BoxExpression) else elem
        for elem in elements
    ]
    return tuple(expr_elements + opts)
