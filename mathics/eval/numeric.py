# -*- coding: utf-8 -*-

"""
arithmetic-related evaluation functions and eval functions for mathics.builtin.numeric.

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
    RationalOneHalf,
    Real,
)
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.number import FP_MANTISA_BINARY_DIGITS, SpecialValueError, min_prec
from mathics.core.symbols import Atom, Symbol, SymbolPlus, SymbolPower, SymbolTimes
from mathics.core.systemsymbols import (
    SymbolAbs,
    SymbolComplexInfinity,
    SymbolExp,
    SymbolI,
    SymbolIndeterminate,
    SymbolLog,
    SymbolRealSign,
    SymbolSign,
    SymbolSqrt,
)

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


def eval_Abs(expr: BaseElement) -> Optional[BaseElement]:
    """
    if expr is a number, return the absolute value.
    """

    if isinstance(expr, Number):
        return eval_Abs_number(expr)
    if expr.has_form("Power", 2):
        base, exp = expr.elements
        if exp.is_zero:
            return Integer1
        if test_arithmetic_expr(expr):
            abs_base = eval_Abs(base)
            if abs_base is None:
                abs_base = Expression(SymbolAbs, base)
            return Expression(SymbolPower, abs_base, exp)
    if expr.has_form("Exp", 1):
        exp = expr.elements[0]
        if isinstance(exp, (Integer, Real, Rational)):
            return expr
        if isinstance(exp, Complex):
            return Expression(SymbolExp, exp.real)
    if expr.get_head() is SymbolTimes:
        factors = []
        rest = []
        for x in expr.elements:
            factor = eval_Abs(x)
            if factor:
                factors.append(factor)
            else:
                rest.append(x)
        if factors:
            return Expression(SymbolTimes, eval_multiply_numbers(*factors), *rest)
    if test_nonnegative_arithmetic_expr(expr):
        return expr
    if test_negative_arithmetic_expr(expr):
        return eval_multiply_numbers(IntegerM1, expr)
    return None


def eval_Abs_number(n: Number) -> Number:
    """
    Evals the absolute value of a number
    """
    if isinstance(n, (Real, Integer)):
        n_val = n.value
        if n_val >= 0:
            return n
        return eval_negate_number(n)
    if isinstance(n, Rational):
        n_num, n_den = n.value.as_numer_denom()
        if n_num >= 0:
            return n
        return Rational(-n_num, n_den)
    if isinstance(n, Complex):
        if n.real.is_zero:
            return eval_Abs_number(n.imag)
        sq_comp = tuple((eval_multiply_numbers(x, x) for x in (n.real, n.imag)))
        sq_abs = eval_add_numbers(*sq_comp)
        result = eval_Power_number(sq_abs, RationalOneHalf) or Expression(
            SymbolPower, sq_abs, RationalOneHalf
        )
        return result


def eval_Exp(exp: BaseElement) -> BaseElement:
    """
    Eval E^exp
    """
    # If both base and exponent are exact quantities,
    # use sympy.

    if not exp.is_inexact():
        exp_sp = exp.to_sympy()
        if exp_sp is None:
            return None
        return from_sympy(sympy.Exp(exp_sp))

    prec = exp.get_precision()
    if prec is not None:
        if exp.is_machine_precision():
            number = mpmath.exp(exp.to_mpmath())
            result = from_mpmath(number)
            return result
        else:
            with mpmath.workprec(prec):
                number = mpmath.exp(exp.to_mpmath())
                return from_mpmath(number, prec)


def eval_RealSign(expr: BaseElement) -> Optional[Integer]:
    """
    If the argument is a real algebraic expression,
    return the sign of the expression.
    """
    if expr.is_zero:
        return Integer0
    if isinstance(expr, (Integer, Rational, Real)):
        return Integer1 if expr.value > 0 else IntegerM1
    if expr in NUMERICAL_CONSTANTS:
        return Integer1
    if expr.has_form("Abs", 1):
        arg = expr.elements[0]
        arg_sign = eval_Sign(arg)
        if arg_sign is None:
            return None
        if arg_sign.is_zero:
            return Integer0
        if isinstance(arg_sign, Number):
            return Integer1
        return None
    if expr.has_form("Sqrt", 1):
        return Integer1 if eval_Sign(expr.elements[0]) is Integer1 else None
    if expr.has_form("Exp", 1):
        return Integer1 if test_arithmetic_expr(expr.elements[0]) else None
    if expr.has_form("Log", 1) or expr.has_form("DirectedInfinity", 1):
        return eval_RealSign(eval_add_numbers(expr.elements[0], IntegerM1))
    if expr.has_form("Times", None):
        sign = 1
        for factor in expr.elements:
            factor_sign = eval_RealSign(factor)
            if factor_sign in (None, Integer0):
                return factor_sign
            if factor_sign is IntegerM1:
                sign = -sign
        return Integer1 if sign == 1 else IntegerM1
    if expr.has_form("Power", 2):
        base, exp = expr.elements
        base_sign = eval_RealSign(base)
        if base_sign is None:
            return None
        if base_sign is Integer0:
            if eval_RealSign(exp) in (IntegerM1, Integer0, None):
                return None
            return Integer0
        # The exponent must represent a real number to continue:
        if not test_arithmetic_expr(exp):
            return None
        # At this point, the exponent is a real number, so if the base
        # is 1, does not matter its value:
        if base_sign is Integer1:
            return Integer1
        if base_sign is IntegerM1:
            if not isinstance(base, Integer):
                return None
            if isinstance(exp, Integer):
                return base_sign if (exp.value % 2 == 1) else Integer1
        return None
    if expr.has_form("Plus", None):
        signed = {Integer1: [], IntegerM1: []}
        for term in expr.elements:
            rsign = eval_RealSign(term)
            if rsign is Integer0:
                continue
            elif rsign is None:
                return None
            signed[rsign].append(term)
        if len(signed[IntegerM1]) == 0:
            return Integer0 if len(signed[Integer1]) == 0 else Integer1
        if len(signed[Integer1]) == 0:
            return IntegerM1
        # Try to explicitly add the numbers:
        try_add = eval_add_numbers(*(term for term in expr.elements))
        if try_add is not None and not try_add.sameQ(expr):
            return eval_RealSign(try_add)
        # Now, try to convert to inexact values:
        try_add = eval_add_numbers(*(to_inexact_value(term) for term in expr.elements))
        if try_add is not None and try_add is not expr:
            return eval_RealSign(try_add)


def eval_Sign(expr: BaseElement) -> Optional[BaseElement]:
    """
    if expr is a number, return its sign.
    """

    def eval_complex_sign(n: BaseElement) -> Optional[BaseElement]:
        if isinstance(n, Complex):
            abs_sq = eval_add_numbers(
                *(eval_multiply_numbers(x, x) for x in (n.real, n.imag))
            )
            criteria = eval_add_numbers(abs_sq, IntegerM1)
            if test_zero_arithmetic_expr(criteria):
                return n
            if n.is_inexact():
                return eval_multiply_numbers(n, eval_Power_number(abs_sq, RealM0p5))
            if test_zero_arithmetic_expr(criteria, numeric=True):
                return n
            return eval_multiply_numbers(n, eval_Power_number(abs_sq, RationalMOneHalf))
        if isinstance(n, Atom):
            return None
        if n.has_form("Abs", 1):
            inner_sign = eval_Sign(n.elements[0])
            if inner_sign is Integer0:
                return Integer0
            if isinstance(inner_sign, Number):
                return Integer1

        if n.has_form("Exp", 1):
            exponent = n.elements[0]
            if isinstance(exponent, Complex):
                return Expression(SymbolExp, exponent.imag)
            return None
        if n.has_form("DirectedInfinity", 1):
            return eval_Sign(n.elements[0])
        if n.has_form("Power", 2):
            base, exponent = expr.elements
            base_rsign = eval_RealSign(base)
            if exponent.is_zero:
                return SymbolIndeterminate if base_rsign is Integer0 else Integer1
            if test_arithmetic_expr(exponent):
                base_sign = eval_Sign(base) or Expression(SymbolSign, base)
                return eval_Power_number(base_sign, exponent)
            if isinstance(exponent, Complex):
                if base_rsign is Integer1:
                    exp_im = exponent.imag
                    return eval_Power_number(base, Complex(Integer0, exp_im))

                if test_arithmetic_expr(base):
                    eval_Power_number(base_sign, exponent)
                    base_sign = eval_Sign(base)
                return eval_Power_number(base_sign, exponent)
        if n.head is SymbolTimes:
            signs = []
            for factor in expr.elements:
                factor_sign = eval_Sign(factor)
                if factor_sign in (None, Integer0):
                    return factor_sign
                if factor_sign is not Integer1:
                    signs.append(factor_sign)
            return Integer1 if len(signs) == 0 else eval_multiply_numbers(*signs)

        try_inexact = to_inexact_value(n)
        if try_inexact:
            return eval_Sign(try_inexact)
        return None

    sign = eval_RealSign(expr)
    return sign or eval_complex_sign(expr)


def eval_UnitStep(expr: BaseElement) -> Optional[Integer]:
    """
    return 0 if x < 0 and 1 for x >= 0 for a single element.
    We will use the result of eval_Realsign() changing
    0 to 1 and -1 to 0.
    """
    result = eval_RealSign(expr)
    if result is None:
        return None
    return Integer1 if result in (Integer1, Integer0) else Integer0


def eval_UnitStep_multidimensional(expr: BaseElement) -> Optional[Integer]:
    """
    Multidimensional unit step function which is 1 only if none of
    the elements of expr are negative.
    """

    for element in expr.elements:
        result = eval_RealSign(element)
        if result is None:
            return None
        if result is not Integer1:
            return Integer0
    return Integer1


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


def eval_Power_number(base: Number, exp: Number) -> Optional[Number]:
    """
    Eval base^exp for `base` and `exp` two numbers. If the expression
    remains the same, return None.
    """
    # If both base and exponent are exact quantities,
    # use sympy.
    # If base or exp are inexact quantities, use
    # the inexact routine.
    if base.is_inexact() or exp.is_inexact():
        return eval_Power_inexact(base, exp)

    # Trivial special cases
    if exp is Integer1:
        return base
    if exp is Integer0:
        return Integer1
    if base is Integer1:
        return Integer1

    def eval_Power_sympy() -> Optional[Number]:
        """
        Tries to compute x^p using sympy rules.
        If the answer is again x^p, return None.
        """
        # This function is called just if useful native rules
        # are available.
        result = from_sympy(sympy.Pow(base.to_sympy(), exp.to_sympy()))
        if result.has_form("Power", 2):
            # If the expression didn´t change, return None
            if result.elements[0].sameQ(base):
                return None
        return result

    # Rational exponent
    if isinstance(exp, Rational):
        exp_p, exp_q = exp.value.as_numer_denom()
        if abs(exp_p) > exp_q:
            exp_int, exp_num = divmod(exp_p, exp_q)
            exp_rem = Rational(exp_num, exp_q)
            factor_1 = eval_Power_number(base, Integer(exp_int))
            factor_2 = eval_Power_number(base, exp_rem) or Expression(
                SymbolPower, base, exp_rem
            )
            if factor_1 is Integer1:
                return factor_2
            return Expression(SymbolTimes, factor_1, factor_2)

    # Integer base
    if isinstance(base, Integer):
        base_value = base.value
        if base_value == -1:
            if isinstance(exp, Rational):
                if exp.sameQ(RationalOneHalf):
                    return SymbolI
                return None
            return eval_Power_sympy()
        elif base_value < 0:
            neg_base = eval_negate_number(base)
            candidate = eval_Power_number(neg_base, exp)
            if candidate is None:
                return None
            sign_factor = eval_Power_number(IntegerM1, exp)
            if candidate is Integer1:
                return sign_factor
            return Expression(SymbolTimes, candidate, sign_factor)

    # Rational base
    if isinstance(base, Rational):
        # If the exponent is an Integer or Rational negative value
        # restate as a positive power
        if (
            isinstance(exp, Integer)
            and exp.value < 0
            or isinstance(exp, Rational)
            and exp.value.p < 0
        ):
            base, exp = eval_inverse_number(base), eval_negate_number(exp)
            return eval_Power_number(base, exp) or Expression(SymbolPower, base, exp)

        p, q = (Integer(u) for u in base.value.as_numer_denom())
        p_eval, q_eval = (eval_Power_number(u, exp) for u in (p, q))
        # If neither p^exp or q^exp produced a new result,
        # leave it alone
        if q_eval is None and p_eval is None:
            return None
        # if q^exp == 1: return p_eval
        # (should not happen)
        if q_eval is Integer1:
            return p_eval
        if isinstance(q_eval, Integer):
            if isinstance(p_eval, Integer):
                return Rational(p_eval.value, q_eval.value)

        if p_eval is None:
            p_eval = Expression(SymbolPower, p, exp)

        if q_eval is None:
            q_eval = Expression(SymbolPower, q, exp)
        return Expression(
            SymbolTimes, p_eval, Expression(SymbolPower, q_eval, IntegerM1)
        )
    # Pure imaginary base case
    elif isinstance(base, Complex) and base.real.is_zero:
        base = base.imag
        if base.value < 0:
            base = eval_negate_number(base)
            phase = Expression(
                SymbolPower,
                IntegerM1,
                eval_multiply_numbers(IntegerM1, RationalOneHalf, exp),
            )
        else:
            phase = Expression(
                SymbolPower, IntegerM1, eval_multiply_numbers(RationalOneHalf, exp)
            )
        real_factor = eval_Power_number(base, exp)

        if real_factor is None:
            return None
        return Expression(SymbolTimes, real_factor, phase)

    # Generic case
    return eval_Power_sympy()


def eval_Power_inexact(base: Number, exp: Number) -> BaseElement:
    """
    Eval base^exp for `base` and `exp` inexact numbers
    """
    # If both base and exponent are exact quantities,
    # use sympy.
    prec = min_prec(base, exp)
    if prec is not None:
        is_machine_precision = base.is_machine_precision() or exp.is_machine_precision()
        if is_machine_precision:
            number = mpmath.power(base.to_mpmath(), exp.to_mpmath())
            return from_mpmath(number)
        else:
            with mpmath.workprec(prec):
                number = mpmath.power(base.to_mpmath(), exp.to_mpmath())
                return from_mpmath(number, prec)


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


EVAL_TO_INEXACT_DISPATCH = {
    SymbolPlus: eval_add_numbers,
    SymbolTimes: eval_multiply_numbers,
    SymbolPower: eval_Power_number,
    SymbolExp: eval_Exp,
    SymbolSqrt: (lambda x: eval_Power_number(x, RationalOneHalf)),
    SymbolAbs: eval_Abs,
    SymbolSign: eval_Sign,
    SymbolRealSign: eval_RealSign,
}


def to_inexact_value(expr: BaseElement) -> BaseElement:
    """
    Converts an expression into an inexact expression.
    Replaces numerical constants by their numerical approximation,
    and then multiplies the expression by Real(1.)
    """
    if expr.is_inexact():
        return expr
    if isinstance(expr, Number):
        return expr.round()
    if expr is SymbolI:
        return Complex(Integer0, RealOne)
    if isinstance(expr, Symbol):
        return NUMERICAL_CONSTANTS.get(expr, None)

    if isinstance(expr, Expression):
        try:
            head = expr.head
            elements = tuple(to_inexact_value(element) for element in expr.elements)
            return EVAL_TO_INEXACT_DISPATCH[head](*elements)
        except Exception:
            pass
    return None
