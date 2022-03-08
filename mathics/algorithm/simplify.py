# -*- coding: utf-8 -*-

"""
Algorithms for simplifying expressions.
"""

from mathics.core.symbols import Atom
from mathics.core.atoms import Number
from mathics.core.expression import Expression


def default_complexity_function(x) -> int:
    """
    Evaluates the complexity of an expression. Each atom
    counts 1, except for numbers that counts 1 each 5 characters
    in its decimal expansion.
    """
    if isinstance(x, Number):
        result = 1 + int(len(str(x)) / 2)
    elif isinstance(x, Expression):
        result = default_complexity_function(x.get_head())
        result = result + sum(default_complexity_function(e) for e in x.elements)
    else:
        result = 1
    #    print(x, result)
    return result
