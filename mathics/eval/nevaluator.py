# cython: language_level=3
# -*- coding: utf-8 -*-

"""
This module contains basic low-level functions that combines an Expression
with an Evaluation objects to produce a new Expression following generic
algorithms.


"""

from typing import Optional

import sympy

from mathics.core.atoms import Number
from mathics.core.attributes import A_N_HOLD_ALL, A_N_HOLD_FIRST, A_N_HOLD_REST
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.number import PrecisionValueError, get_precision
from mathics.core.symbols import Atom
from mathics.core.systemsymbols import SymbolMachinePrecision, SymbolN


# FIXME: Add the two-argument form N[expr, n]
def eval_N(
    expression: BaseElement,
    evaluation: Evaluation,
    prec: BaseElement = SymbolMachinePrecision,
) -> BaseElement:
    """
    Equivalent to Expression(SymbolN, expression).evaluate(evaluation)
    """
    evaluated_expression = expression.evaluate(evaluation)
    result = eval_NValues(evaluated_expression, prec, evaluation)
    if result is None:
        return expression
    if isinstance(result, Number):
        return result
    return result.evaluate(evaluation)


def eval_NValues(
    expr: BaseElement, prec: BaseElement, evaluation: Evaluation
) -> Optional[BaseElement]:
    """
    Looks for the numeric value of ```expr`` with precision ``prec`` by applying NValues rules
    stored in ``evaluation.definitions``.
    If ``prec`` can not be evaluated as a number, returns None, otherwise, returns an expression.
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
    # just apply `eval_NValues` to each element and return the new list.
    if expr.get_head_name() in ("System`List", "System`Rule"):
        elements = expr.elements

        # FIXME: incorporate these lines into Expression call
        result = Expression(expr.head)
        new_elements = [
            eval_NValues(element, prec, evaluation) for element in expr.elements
        ]
        result.elements = tuple(
            new_element if new_element else element
            for element, new_element in zip(elements, new_elements)
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
    # reevaluate the result and apply `eval_NValues` again.
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
                result = eval_NValues(result, prec, evaluation)
                return result

    # If we are here, is because there are not NValues that matches
    # to the expression. In such a case, if we arrive to an atomic expression,
    # just return it.
    if isinstance(expr, Atom):
        return expr
    else:
        # Otherwise, look at the attributes, determine over which elements
        # we need to apply `eval_NValues`, and rebuild the expression with
        # the results.
        attributes = expr.head.get_attributes(evaluation.definitions)
        head = expr.head
        elements = expr.get_mutable_elements()
        if A_N_HOLD_ALL & attributes:
            eval_range = ()
        elif A_N_HOLD_FIRST & attributes:
            eval_range = range(1, len(elements))
        elif A_N_HOLD_REST & attributes:
            if len(expr.elements) > 0:
                eval_range = (0,)
            else:
                eval_range = ()
        else:
            eval_range = range(len(elements))

        newhead = eval_NValues(head, prec, evaluation)
        head = head if newhead is None else newhead

        for index in eval_range:
            new_element = eval_NValues(elements[index], prec, evaluation)
            if new_element:
                elements[index] = new_element

        # FIXME: incorporate these 3 lines into Expression call
        result = Expression(head)
        result.elements = elements
        result._build_elements_properties()
        return result


# TODO:  Revisit - can this be simplified? Is some broader framework this fits into?


# comment mmatera: Other methods that I would like to have here, as non-member methods are
