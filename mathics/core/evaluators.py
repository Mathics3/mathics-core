# cython: language_level=3
# -*- coding: utf-8 -*-

"""
This module contains basic low-level functions that combines an Expression
with an Evaluation objects to produce a new Expression following generic
algorithms.


"""

import sympy
from typing import Optional
from mathics.core.atoms import Number
from mathics.core.symbols import Atom, BaseElement
from mathics.core.systemsymbols import SymbolMachinePrecision, SymbolN
from mathics.core.number import get_precision, PrecisionValueError
from mathics.core.expression import Expression
from mathics.core.evaluation import Evaluation
from mathics.core.convert import from_sympy

from mathics.core.attributes import (
    n_hold_all,
    n_hold_first,
    n_hold_rest,
)


# FIXME: Add the two-argument form N[expr, n]
def apply_N(
    expression: BaseElement,
    evaluation: Evaluation,
    prec: BaseElement = SymbolMachinePrecision,
) -> BaseElement:
    """
    Equivalent to Expression(SymbolN, expression).evaluate(evaluation)
    """
    evaluated_expression = expression.evaluate(evaluation)
    result = apply_nvalues(evaluated_expression, prec, evaluation)
    if result is None:
        return expression
    if isinstance(result, Number):
        return result
    return result.evaluate(evaluation)


def apply_nvalues(
    expr: BaseElement, prec: BaseElement, evaluation: Evaluation
) -> Optional[BaseElement]:
    """
    Looks for the numeric value of ```expr`` with precision ``prec`` by appling NValues rules
    stored in ``evaluation.definitions``.
    If `prec` can not be evaluated as a number, returns None, otherwise, returns an expression.
    """

    # The first step is to determine the precision goal
    try:
        # Here ``get_precision`` is called with ``show_messages``
        # set to ``False`` to avoid show the same warnings repeatedly.
        d = get_precision(prec, evaluation, show_messages=False)
    except PrecisionValueError:
        # We can ensure that the function always return an expression if
        # the exception was captured by the caller.
        return
    # If the expression is a number, just round it to the required
    # precision
    if isinstance(expr, Number):
        return expr.round(d)

    # If expr is a List, or a Rule (or maybe expressions with heads for
    # which we are sure do not have NValues or special attributes)
    # just apply `apply_nvalues` to each leaf and return the new list.
    if expr.get_head_name() in ("System`List", "System`Rule"):
        leaves = expr.leaves

        # FIXME: incorporate these lines into Expression call
        result = Expression(expr.head)
        newleaves = [apply_nvalues(leaf, prec, evaluation) for leaf in expr.leaves]
        result.elements = tuple(
            newleaf if newleaf else leaf for leaf, newleaf in zip(leaves, newleaves)
        )
        result._build_elements_properties()
        return result

    # Special case for the Root builtin
    # This should be implemented as an NValue
    if expr.has_form("Root", 2):
        return from_sympy(sympy.N(expr.to_sympy(), d))

    # Here we look for the NValues associated to the
    # lookup_name of the expression.
    # If a rule is found and successfuly applied,
    # reevaluate the result and apply `apply_nvalues` again.
    # This should be implemented as a loop instead of
    # recursively.
    name = expr.get_lookup_name()
    if name != "":
        nexpr = Expression(SymbolN, expr, prec)
        result = evaluation.definitions.get_value(
            name, "System`NValues", nexpr, evaluation
        )
        if result is not None:
            if not result.sameQ(nexpr):
                result = result.evaluate(evaluation)
                result = apply_nvalues(result, prec, evaluation)
            return result

    # If we are here, is because there are not NValues that matches
    # to the expression. In such a case, if we arrive to an atomic expression,
    # just return it.
    if isinstance(expr, Atom):
        return expr
    else:
        # Otherwise, look at the attributes, determine over which leaves
        # we need to apply `apply_nvalues`, and rebuild the expression with
        # the results.
        attributes = expr.head.get_attributes(evaluation.definitions)
        head = expr.head
        leaves = expr.get_mutable_elements()
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

        newhead = apply_nvalues(head, prec, evaluation)
        head = head if newhead is None else newhead

        for index in eval_range:
            newleaf = apply_nvalues(leaves[index], prec, evaluation)
            if newleaf:
                leaves[index] = newleaf

        # FIXME: incorporate these 3 lines into Expression call
        result = Expression(head)
        result.elements = tuple(leaves)
        result._build_elements_properties()
        return result


# TODO:  Revisit - can this be simplified? Is some broader framework this fits into?


# comment mmatera: Other methods that I would like to have here, as non-member methods are
# ``numerify``, ``evaluation``, ``_rewrite_apply_eval_step``, ``format`` and ``boxes_to_*`` that in the current implementation
# requires to introduce local imports.
# This also would make easier to test and profile classes that store Expression-like objects and methods that produce the evaluation.
