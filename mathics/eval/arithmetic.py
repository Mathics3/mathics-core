# -*- coding: utf-8 -*-

"""
arithmetic-related evaluation functions.

Many of these do do depend on the evaluation context. Conversions to Sympy are
used just as a last resource.
"""

from functools import lru_cache
from typing import Callable, List, Optional, Tuple

import mpmath
import sympy

from mathics.core.atoms import (
    NUMERICAL_CONSTANTS,
    Complex,
    Integer,
    Integer0,
    Integer1,
    Integer2,
    IntegerM1,
    MachineReal,
    Number,
    Rational,
    RationalOneHalf,
    Real,
)
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement, ElementsProperties
from mathics.core.expression import Expression
from mathics.core.number import (
    FP_MANTISA_BINARY_DIGITS,
    MAX_MACHINE_NUMBER,
    MIN_MACHINE_NUMBER,
    SpecialValueError,
    min_prec,
)
from mathics.core.rules import Rule
from mathics.core.symbols import Atom, Symbol, SymbolPlus, SymbolPower, SymbolTimes
from mathics.core.systemsymbols import (
    SymbolComplexInfinity,
    SymbolI,
    SymbolIndeterminate,
    SymbolLog,
)

RationalMOneHalf = Rational(-1, 2)
RealOne = Real(1.0)


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


def test_arithmetic_expr(expr: BaseElement, only_real: bool = True) -> bool:
    """
    Check if an expression `expr` is an arithmetic expression
    composed only by numbers and arithmetic operations.
    If only_real is set to True, then `I` is not considered a number.
    """
    if isinstance(expr, (Integer, Rational, Real)):
        return True
    if expr in NUMERICAL_CONSTANTS:
        return True
    if isinstance(expr, Complex) or expr is SymbolI:
        return not only_real
    if isinstance(expr, Symbol):
        return False

    head, elements = expr.head, expr.elements

    if head in (SymbolPlus, SymbolTimes):
        return all(test_arithmetic_expr(term, only_real) for term in elements)
    if expr.has_form("Exp", 1):
        return test_arithmetic_expr(elements[0], only_real)
    if head is SymbolLog:
        if len(elements) > 2:
            return False
        if len(elements) == 2:
            base = elements[0]
            if not test_positive_arithmetic_expr(base):
                return False
        return test_arithmetic_expr(elements[-1], only_real)
    if expr.has_form("Power", 2):
        base, exponent = elements
        if only_real:
            if isinstance(exponent, Integer):
                return test_arithmetic_expr(base)
        return all(test_arithmetic_expr(item, only_real) for item in elements)
    return False


def test_negative_arithmetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a negative value.
    """
    if isinstance(expr, (Integer, Rational, Real)):
        return expr.value < 0

    expr = eval_multiply_numbers(IntegerM1, expr)
    return test_positive_arithmetic_expr(expr)


def test_nonnegative_arithmetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a nonnegative number
    """
    if test_zero_arithmetic_expr(expr) or test_positive_arithmetic_expr(expr):
        return True


def test_nonpositive_arithetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a nonnegative number
    """
    if test_zero_arithmetic_expr(expr) or test_negative_arithmetic_expr(expr):
        return True
    return False


def test_positive_arithmetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a positive value.
    """
    if isinstance(expr, (Integer, Rational, Real)):
        return expr.value > 0
    if expr in NUMERICAL_CONSTANTS:
        return True
    if isinstance(expr, Atom):
        return False

    head, elements = expr.get_head(), expr.elements
    if head is SymbolPlus:
        positive_nonpositive_terms = {True: [], False: []}
        for term in elements:
            positive_nonpositive_terms[test_positive_arithmetic_expr(term)].append(term)

        if len(positive_nonpositive_terms[False]) == 0:
            return True
        if len(positive_nonpositive_terms[True]) == 0:
            return False

        pos, neg = (
            eval_add_numbers(*items) for items in positive_nonpositive_terms.values()
        )
        if neg.is_zero:
            return True
        if not test_arithmetic_expr(neg):
            return False

        total = eval_add_numbers(pos, neg)
        # Check positivity of the evaluated expression
        if isinstance(total, (Integer, Rational, Real)):
            return total.value > 0
        if isinstance(total, Complex):
            return False
        if total.sameQ(expr):
            return False
        return test_positive_arithmetic_expr(total)

    if head is SymbolTimes:
        nonpositive_factors = tuple(
            (item for item in elements if not test_positive_arithmetic_expr(item))
        )
        if len(nonpositive_factors) == 0:
            return True
        evaluated_expr = eval_multiply_numbers(*nonpositive_factors)
        if evaluated_expr.sameQ(expr):
            return False
        return test_positive_arithmetic_expr(evaluated_expr)
    if expr.has_form("Power", 2):
        base, exponent = elements
        if isinstance(exponent, Integer) and exponent.value % 2 == 0:
            return test_arithmetic_expr(base)
        return test_arithmetic_expr(exponent) and test_positive_arithmetic_expr(base)
    if expr.has_form("Exp", 1):
        return test_arithmetic_expr(exponent, only_real=True)
    if head is SymbolLog:
        if len(elements) > 2:
            return False
        if len(elements) == 2:
            if not test_positive_arithmetic_expr(elements[0]):
                return False
        arg = elements[-1]
        return test_positive_arithmetic_expr(eval_add_numbers(arg, IntegerM1))
    if head.has_form("Abs", 1):
        return True
    if head.has_form("DirectedInfinity", 1):
        return test_positive_arithmetic_expr(elements[0])

    return False


def test_zero_arithmetic_expr(expr: BaseElement, numeric: bool = False) -> bool:
    """
    return True if expr evaluates to a number compatible
    with 0
    """

    def is_numeric_zero(z: Number):
        if isinstance(z, Complex):
            if abs(z.real.value) + abs(z.imag.value) < 2.0e-10:
                return True
        if isinstance(z, Number):
            if abs(z.value) < 1e-10:
                return True
        return False

    if expr.is_zero:
        return True
    if numeric:
        if is_numeric_zero(expr):
            return True
        expr = to_inexact_value(expr)
    if expr.has_form("Times", None):
        if any(
            test_zero_arithmetic_expr(element, numeric=numeric)
            for element in expr.elements
        ) and not any(
            element.has_form("DirectedInfinity", None) for element in expr.elements
        ):
            return True
    if expr.has_form("Power", 2):
        base, exp = expr.elements
        if test_zero_arithmetic_expr(base, numeric):
            return test_nonnegative_arithmetic_expr(exp)
        if base.has_form("DirectedInfinity", None):
            return test_positive_arithmetic_expr(exp)
    if expr.has_form("Plus", None):
        result = eval_add_numbers(*expr.elements)
        if numeric:
            if isinstance(result, complex):
                if abs(result.real.value) + abs(result.imag.value) < 2.0e-10:
                    return True
            if isinstance(result, Number):
                if abs(result.value) < 1e-10:
                    return True
        return result.is_zero
    return False


def to_inexact_value(expr: BaseElement) -> BaseElement:
    """
    Converts an expression into an inexact expression.
    Replaces numerical constants by their numerical approximation,
    and then multiplies the expression by Real(1.)
    """
    if expr.is_inexact():
        return expr

    if isinstance(expr, Expression):
        for const, value in NUMERICAL_CONSTANTS.items():
            expr, success = expr.do_apply_rule(Rule(const, value))

    return eval_multiply_numbers(RealOne, expr)
