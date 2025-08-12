# -*- coding: utf-8 -*-
# FIXME: rewrite this and split up to
# have eval functions for mathics.builtin.arithmetic.
# Those other functions that remain, e.g tracing functions
# put somewhere else.

"""
arithmetic-related evaluation functions.

Many of these depend on the evaluation context. Conversions to SymPy are
used just as a last resource.
"""

from typing import Callable, List, Optional, Tuple

import mpmath
import sympy

# Note: it is important *not* use: from mathics.eval.tracing import run_sympy
# but instead import the module and access below as tracing.run_sympy.
# This allows us change where tracing.run_sympy points at runtime.
import mathics.eval.tracing as tracing
from mathics.core.atoms import (
    NUMERICAL_CONSTANTS,
    Complex,
    Integer,
    Integer0,
    Integer1,
    IntegerM1,
    Number,
    Rational,
    Real,
)
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement
from mathics.core.number import FP_MANTISA_BINARY_DIGITS, SpecialValueError, min_prec
from mathics.core.symbols import Atom, Symbol, SymbolPlus, SymbolTimes
from mathics.core.systemsymbols import SymbolComplexInfinity, SymbolI, SymbolLog
from mathics.eval.numeric import eval_Power_number, eval_RealSign, to_inexact_value

RationalMOneHalf = Rational(-1, 2)
RealM0p5 = Real(-0.5)
RealOne = Real(1.0)


# This cache might not be used that much.
def run_mpmath(
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
            result_mp = tracing.run_mpmath(mpmath_function, *mpmath_args)
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

        return run_mpmath(mpmath_function, tuple(float_args), FP_MANTISA_BINARY_DIGITS)
    else:
        mpmath_args = [x.to_mpmath(prec) for x in args]
        if None in mpmath_args:
            return
        return run_mpmath(mpmath_function, tuple(mpmath_args), prec)


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


def eval_inverse_number(n: Number) -> Optional[Number]:
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


def eval_negate_number(n: Number) -> Number:
    """
    Changes the sign of n
    """
    if isinstance(n, Integer):
        return Integer(-n.value)
    if isinstance(n, Rational):
        n_num, n_den = n.value.as_numer_denom()
        return Rational(-n_num, n_den)
    # Otherwise, multiply by -1:
    return eval_multiply_numbers(IntegerM1, n)


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
    if isinstance(expr, Atom):
        return False

    head, elements = expr.head, expr.elements

    if head in (SymbolPlus, SymbolTimes):
        return all(test_arithmetic_expr(term, only_real) for term in elements)
    if expr.has_form("Power", 2):
        base, exponent = elements
        if only_real:
            if isinstance(exponent, Integer):
                return test_arithmetic_expr(base)
        return all(test_arithmetic_expr(item, only_real) for item in elements)
    if expr.has_form("Exp", 1):
        return test_arithmetic_expr(elements[0], only_real)
    if head is SymbolLog:
        if len(elements) > 2:
            return False
        if len(elements) == 2:
            base = elements[0]
            if only_real and eval_RealSign(base) is not Integer1:
                return False
            elif not test_arithmetic_expr(base):
                return False
        return test_arithmetic_expr(elements[-1], only_real)
    if expr.has_form("Sqrt", 1):
        radicand = elements[0]
        if only_real:
            return eval_RealSign(radicand) in (Integer0, Integer1)
        return test_arithmetic_expr(radicand, only_real)
    return False


def test_negative_arithmetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a negative value.
    """
    return eval_RealSign(expr) is IntegerM1


def test_nonnegative_arithmetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a nonnegative number
    """
    return eval_RealSign(expr) in (Integer0, Integer1)


def test_nonpositive_arithetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a nonnegative number
    """
    return eval_RealSign(expr) in (Integer0, IntegerM1)


def test_positive_arithmetic_expr(expr: BaseElement) -> bool:
    """
    Check if the expression is an arithmetic expression
    representing a positive value.
    """
    return eval_RealSign(expr) is Integer1


def test_zero_arithmetic_expr(expr: BaseElement, numeric: bool = False) -> bool:
    """
    return True if expr evaluates to a number compatible
    with 0
    """
    if numeric:
        if isinstance(expr, Complex):
            if abs(expr.real.value) + abs(expr.imag.value) < 2.0e-10:
                return True
        if isinstance(expr, Number):
            if abs(expr.value) < 1e-10:
                return True
        expr = to_inexact_value(expr)

    return eval_RealSign(expr) is Integer0
