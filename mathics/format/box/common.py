"""
Utility functions for box processing.
"""

from mathics.builtin.box.expression import BoxExpression
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.eval.options import filter_non_default_values, options_to_rules


def elements_to_expressions(
    self: BoxExpression, elements: tuple[BaseElement | Expression], options: dict
) -> tuple[BaseElement | Expression, ...]:
    """
    Return a tuple of Mathics3 normal atoms or expressions.
    """
    opts = sorted(options_to_rules(options, filter_non_default_values(self)))
    expr_elements: list[BaseElement | Expression] = [
        elem.to_expression() if isinstance(elem, BoxExpression) else elem
        for elem in elements
    ]
    return tuple(expr_elements + opts)
