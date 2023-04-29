# -*- coding: utf-8 -*-

"""
helper functions for arithmetic evaluation, which do not
depend on the evaluation context. Conversions to Sympy are
used just as a last resource.
"""

from functools import lru_cache
from typing import Callable, List, Optional, Tuple

import mpmath
import sympy

from mathics.core.atoms import (
    Complex,
    Integer,
    Integer0,
    Integer1,
    Integer2,
    IntegerM1,
    Number,
    Rational,
    RationalOneHalf,
    Real,
)
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement, ElementsProperties
from mathics.core.expression import Expression
from mathics.core.number import FP_MANTISA_BINARY_DIGITS, SpecialValueError, min_prec
from mathics.core.symbols import Symbol, SymbolPlus, SymbolPower, SymbolTimes
from mathics.core.systemsymbols import SymbolComplexInfinity, SymbolIndeterminate

RationalMOneHalf = Rational(-1, 2)


# This cache might not be used that much.
@lru_cache()
def call_mpmath(
    mpmath_function: Callable, mpmath_args: tuple, precision: int
) -> Optional[BaseElement]:
    """
    A wrapper that calls
       mpmath_function(mpmath_args *mpmathargs)
    setting precision to the parameter ``precision``.

    The result is cached.
    """
    with mpmath.workprec(precision):
        try:
            result_mp = mpmath_function(*mpmath_args)
            if precision != FP_MANTISA_BINARY_DIGITS:
                return from_mpmath(result_mp, precision)
            return from_mpmath(result_mp)
        except ValueError as exc:
            text = str(exc)
            if text == "gamma function pole":
                return SymbolComplexInfinity
            else:
                raise
        except ZeroDivisionError:
            return
        except SpecialValueError as exc:
            return Symbol(exc.name)


def eval_Abs(expr: BaseElement) -> Optional[BaseElement]:
    """
    if expr is a number, return the absolute value.
    """
    if isinstance(expr, (Integer, Rational, Real)):
        if expr.value >= 0:
            return expr
        return eval_multiply_numbers(*[IntegerM1, expr])
    if isinstance(expr, Complex):
        re, im = expr.real, expr.imag
        sqabs = eval_add_numbers(
            eval_multiply_numbers(re, re), eval_multiply_numbers(im, im)
        )
        return Expression(SymbolPower, sqabs, RationalOneHalf)
    return None


def eval_Sign(expr: BaseElement) -> Optional[BaseElement]:
    """
    if expr is a number, return its sign.
    """
    if isinstance(expr, (Integer, Rational, Real)):
        if expr.value > 0:
            return Integer1
        elif expr.value == 0:
            return Integer0
        else:
            return IntegerM1

    if isinstance(expr, Complex):
        re, im = expr.real, expr.imag
        sqabs = eval_add_numbers(eval_Times(re, re), eval_Times(im, im))
        norm = Expression(SymbolPower, sqabs, RationalMOneHalf)
        result = eval_Times(expr, norm)
        if result is None:
            return Expression(SymbolTimes, expr, norm)
        return result
    return None


def eval_mpmath_function(
    mpmath_function: Callable, *args: Number, prec: Optional[int] = None
) -> Optional[Number]:
    """
    Call the mpmath function `mpmath_function` with the arguments `args`
    working with precision `prec`. If `prec` is `None`, work with machine
    precision.

    Return a Mathics Number or None if the evaluation failed.
    """
    if prec is None:
        # if any argument has machine precision then the entire calculation
        # is done with machine precision.
        float_args = [arg.round().get_float_value(permit_complex=True) for arg in args]
        if None in float_args:
            return

        return call_mpmath(mpmath_function, tuple(float_args), FP_MANTISA_BINARY_DIGITS)
    else:
        with mpmath.workprec(prec):
            # to_mpmath seems to require that the precision is set from outside
            mpmath_args = [x.to_mpmath() for x in args]
            if None in mpmath_args:
                return
            return call_mpmath(mpmath_function, tuple(mpmath_args), prec)


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


def eval_Times(*items: BaseElement) -> BaseElement:
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
        else:
            item = item
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
    items_elements = items
    if len(elements) == len(items_elements) and all(
        elem.sameQ(item) for elem, item in zip(elements, items_elements)
    ):
        return None
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


def eval_multiply_numbers(*numbers: Number) -> BaseElement:
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


def segregate_numbers(
    *elements: BaseElement,
) -> Tuple[List[Number], List[BaseElement]]:
    """
    From a list of elements, produce two lists, one with the numeric items
    and the other with the remaining
    """
    items = {True: [], False: []}
    for element in elements:
        items[isinstance(element, Number)].append(element)
    return items[True], items[False]


# Note: we return:
#  Tuple[List[Number], List[BaseElement]]
#             ^^^^^
# But the mypy type checking system can't
# look into the loop and its condition and
# prove that the return type is List[Number].
# So we use the weaker type assertion
# which is the one on elements: List[BaseElement].
def segregate_numbers_from_sorted_list(
    *elements: BaseElement,
) -> Tuple[List[BaseElement], List[BaseElement]]:
    """
    From a list of elements, produce two lists, one with the numeric items
    and the other with the remaining. Different from `segregate_numbers`,
    this function assumes that elements are sorted with the numbers at
    the beginning.
    """
    for pos, element in enumerate(elements):
        if not isinstance(element, Number):
            return list(elements[:pos]), list(elements[pos:])
    return list(elements), []
