# -*- coding: utf-8 -*-

"""
evaluation function for builtins in mathics.builtin.arithfns.basic

Many of these depend on the evaluation context. Conversions to SymPy are
used just as a last resource.
"""

from typing import Optional

import mpmath
import sympy

# Note: it is important *not* use: from mathics.eval.tracing import run_sympy
# but instead import the module and access below as tracing.run_sympy.
# This allows us change where tracing.run_sympy points at runtime.
from mathics.core.atoms import (
    Integer,
    Integer0,
    Integer1,
    Integer2,
    IntegerM1,
    Number,
    Rational,
    Real,
)
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement, ElementsProperties
from mathics.core.expression import Expression
from mathics.core.number import min_prec
from mathics.core.symbols import SymbolPlus, SymbolPower, SymbolTimes
from mathics.core.systemsymbols import SymbolIndeterminate
from mathics.eval.arithmetic import (
    eval_Power_number,
    segregate_numbers_from_sorted_list,
)

RationalMOneHalf = Rational(-1, 2)
RealM0p5 = Real(-0.5)
RealOne = Real(1.0)


def eval_Plus(*items: BaseElement) -> BaseElement:
    "evaluate Plus for general elements"
    numbers, items_tuple = segregate_numbers_from_sorted_list(*items)
    elements = []
    last_item = last_count = None
    number = eval_add_numbers(*numbers) if numbers else Integer0

    # This reduces common factors
    # TODO: Check if it possible to avoid the conversions back and forward to sympy.
    def append_last():
        if last_item is not None:
            if last_count == 1:
                elements.append(last_item)
            else:
                if last_item.has_form("Times", None):
                    elements.append(
                        Expression(
                            SymbolTimes, from_sympy(last_count), *last_item.elements
                        )
                    )
                else:
                    elements.append(
                        Expression(SymbolTimes, from_sympy(last_count), last_item)
                    )

    for item in items_tuple:
        count = rest = None
        if item.has_form("Times", None):
            for element in item.elements:
                if isinstance(element, Number):
                    count = element.to_sympy()
                    rest = item.get_mutable_elements()
                    rest.remove(element)
                    if len(rest) == 1:
                        rest = rest[0]
                    else:
                        rest.sort()
                        rest = Expression(SymbolTimes, *rest)
                    break
        if count is None:
            count = sympy.Integer(1)
            rest = item
        if last_item is not None and last_item == rest:
            last_count = last_count + count
        else:
            append_last()
            last_item = rest
            last_count = count
    append_last()

    # now elements contains the symbolic terms which can not be simplified.
    # by collecting common symbolic factors.
    if not elements:
        return number

    if number is not Integer0:
        elements.insert(0, number)
    elif len(elements) == 1:
        return elements[0]

    elements.sort()
    return Expression(
        SymbolPlus,
        *elements,
        elements_properties=ElementsProperties(False, False, True),
    )


def eval_Times(*items: BaseElement) -> Optional[BaseElement]:
    elements = []
    numbers = []
    # find numbers and simplify Times -> Power
    numbers, symbolic_items = segregate_numbers_from_sorted_list(*(items))
    # This loop handles factors representing infinite quantities,
    # and factors which are powers of the same basis.

    for item in symbolic_items:
        if item is SymbolIndeterminate:
            return item
        # Process powers
        if elements:
            previous_elem = elements[-1]
            if item == previous_elem:
                elements[-1] = Expression(SymbolPower, previous_elem, Integer2)
                continue
            elif item.has_form("Power", 2):
                base, exp = item.elements
                if previous_elem.has_form("Power", 2) and base.sameQ(
                    previous_elem.elements[0]
                ):
                    exp = eval_Plus(exp, previous_elem.elements[1])
                    elements[-1] = Expression(
                        SymbolPower,
                        base,
                        exp,
                    )
                    continue
                if base.sameQ(previous_elem):
                    exp = eval_Plus(Integer1, exp)
                    elements[-1] = Expression(
                        SymbolPower,
                        base,
                        exp,
                    )
                    continue
            elif previous_elem.has_form("Power", 2) and previous_elem.elements[0].sameQ(
                item
            ):
                exp = eval_Plus(Integer1, previous_elem.elements[1])
                elements[-1] = Expression(
                    SymbolPower,
                    item,
                    exp,
                )
                continue

        # Otherwise, just append the element...
        elements.append(item)

    number = eval_multiply_numbers(*numbers) if numbers else Integer1

    if len(elements) == 0 or number is Integer0:
        return number

    if number is IntegerM1 and elements and elements[0].has_form("Plus", None):
        elements[0] = Expression(
            elements[0].get_head(),
            *[
                Expression(SymbolTimes, IntegerM1, element)
                for element in elements[0].elements
            ],
        )
        number = Integer1

    if number is not Integer1:
        elements.insert(0, number)

    if len(elements) == 1:
        return elements[0]

    elements = sorted(elements)

    return Expression(
        SymbolTimes,
        *elements,
        elements_properties=ElementsProperties(False, False, True),
    )


def eval_add_numbers(
    *numbers: Number,
) -> BaseElement:
    """
    Add the elements in ``numbers``.
    """
    if len(numbers) == 0:
        return Integer0
    if len(numbers) == 1:
        return numbers[0]

    is_machine_precision = any(number.is_machine_precision() for number in numbers)
    if is_machine_precision:
        terms = (item.to_mpmath() for item in numbers)
        number = mpmath.fsum(terms)
        return from_mpmath(number)

    prec = min_prec(*numbers)
    if prec is not None:
        # For a sum, what is relevant is the minimum accuracy of the terms
        with mpmath.workprec(prec):
            terms = (item.to_mpmath() for item in numbers)
            number = mpmath.fsum(terms)
            return from_mpmath(number, precision=prec)
    else:
        return from_sympy(sum(item.to_sympy() for item in numbers))


def eval_inverse_number(n: Number) -> Number:
    """
    Eval 1/n
    """
    if isinstance(n, Integer):
        n_value = n.value
        if n_value == 1 or n_value == -1:
            return n
        return Rational(-1, -n_value) if n_value < 0 else Rational(1, n_value)
    if isinstance(n, Rational):
        n_num, n_den = n.value.as_numer_denom()
        if n_num < 0:
            n_num, n_den = -n_num, -n_den
        if n_num == 1:
            return Integer(n_den)
        return Rational(n_den, n_num)
    # Otherwise, use power....
    return eval_Power_number(n, IntegerM1)


def eval_multiply_numbers(*numbers: Number) -> Number:
    """
    Multiply the elements in ``numbers``.
    """
    if len(numbers) == 0:
        return Integer1
    if len(numbers) == 1:
        return numbers[0]

    is_machine_precision = any(number.is_machine_precision() for number in numbers)
    if is_machine_precision:
        factors = (item.to_mpmath() for item in numbers)
        number = mpmath.fprod(factors)
        return from_mpmath(number)

    prec = min_prec(*numbers)
    if prec is not None:
        with mpmath.workprec(prec):
            factors = (item.to_mpmath() for item in numbers)
            number = mpmath.fprod(factors)
            return from_mpmath(number, prec)
    else:
        return from_sympy(sympy.Mul(*(item.to_sympy() for item in numbers)))
