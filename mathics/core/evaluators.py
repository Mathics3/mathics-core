# cython: language_level=3
# -*- coding: utf-8 -*-

"""
This module contains basic low-level functions that combines an Expression
with an Evaluation objects to produce a new Expression following generic
algorithms.


"""

import sympy

from mathics.core.atoms import Number
from mathics.core.systemsymbols import SymbolMachinePrecision, SymbolN
from mathics.core.number import get_precision, PrecisionValueError
from mathics.core.expression import Expression
from mathics.core.convert import from_sympy

from mathics.core.attributes import (
    n_hold_all,
    n_hold_first,
    n_hold_rest,
)


def eval_N(expression, evaluation, prec=SymbolMachinePrecision):
    """
    Equivalent to Expression("N", expression).evaluate(evaluation)
    """
    evaluated_expression = expression.evaluate(evaluation)
    result = apply_N(evaluated_expression, prec, evaluation)
    if result is None:
        return expression
    if isinstance(result, Number):
        return result
    return result.evaluate(evaluation)


def apply_N(expr, prec, evaluation):
    """
    Applies Nvalues until reach a fixed point.
    """
    try:
        # Here ``get_precision`` is called with ``show_messages``
        # set to ``False`` to avoid show the same warnings repeatedly.
        d = get_precision(prec, evaluation, show_messages=False)
    except PrecisionValueError:
        return

    if isinstance(expr, Number):
        return expr.round(d)

    if expr.get_head_name() in ("System`List", "System`Rule"):
        leaves = expr.leaves
        result = Expression(expr.head)
        newleaves = [apply_N(leaf, prec, evaluation) for leaf in expr.leaves]
        result._leaves = tuple(
            newleaf if newleaf else leaf for leaf, newleaf in zip(leaves, newleaves)
        )
        return result

    # Special case for the Root builtin
    if expr.has_form("Root", 2):
        return from_sympy(sympy.N(expr.to_sympy(), d))

    name = expr.get_lookup_name()
    if name != "":
        nexpr = Expression(SymbolN, expr, prec)
        result = evaluation.definitions.get_value(
            name, "System`NValues", nexpr, evaluation
        )
        if result is not None:
            if not result.sameQ(nexpr):
                result = result.evaluate(evaluation)
                result = apply_N(result, prec, evaluation)
            return result

    if expr.is_atom():
        return expr
    else:
        attributes = expr.head.get_attributes(evaluation.definitions)
        head = expr.head
        leaves = expr.get_mutable_leaves()
        if n_hold_all & attributes:
            eval_range = ()
        elif n_hold_first & attributes:
            eval_range = range(1, len(leaves))
        elif n_hold_rest & attributes:
            if len(expr.leaves) > 0:
                eval_range = (0,)
            else:
                eval_range = ()
        else:
            eval_range = range(len(leaves))

        newhead = apply_N(head, prec, evaluation)
        head = head if newhead is None else newhead

        for index in eval_range:
            newleaf = apply_N(leaves[index], prec, evaluation)
            if newleaf:
                leaves[index] = newleaf

        result = Expression(head)
        result._leaves = tuple(leaves)
        return result


# comment mmatera: Other methods that I would like to have here, as non-member methods are
# ``numerify``, ``evaluation``, ``evaluation_next``, ``format`` and ``boxes_to_*`` that in the current implementation
# requires to introduce local imports.
# This also would make easier to test and profile classes that store Expression-like objects and methods that produce the evaluation.
