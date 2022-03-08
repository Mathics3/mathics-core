# -*- coding: utf-8 -*-

"""
Algorithms for simplifying expressions and evaluate complexity.
"""

from mathics.core.atoms import Number
from mathics.core.expression import Expression


def default_complexity_function(expr: Expression) -> int:
    """
    Evaluates the complexity of an expression. Each atom
    counts 1, except for numbers that counts 1 each 5 characters
    in its decimal expansion.
    """
    # TODO: write this in an iterative form instead a recursive one.
    if isinstance(expr, Number):
        # This can be improved in several ways...
        return int(len(str(expr).strip())) + 1
    elif isinstance(expr, Expression):
        return default_complexity_function(expr.get_head()) + +sum(
            default_complexity_function(e) for e in expr.elements
        )
    else:
        return 1
