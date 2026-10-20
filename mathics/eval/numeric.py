# -*- coding: utf-8 -*-

"""
arithmetic-related evaluation functions and eval functions for mathics.builtin.numeric.

Many of these depend on the evaluation context. Conversions to SymPy are
used just as a last resource.
"""

import math
from typing import Callable, Optional

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
    PrecisionReal,
    Rational,
    RationalOneHalf,
    Real,
)
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.number import (
    FP_MANTISA_BINARY_DIGITS,
    MIN_STORED_BITS,
    SpecialValueError,
    is_inexact,
    is_machine_precision,
    is_zero,
    min_prec,
    prec as number_prec,
)
from mathics.core.symbols import Atom, Symbol, SymbolPlus, SymbolPower, SymbolTimes
from mathics.core.systemsymbols import (
    SymbolAbs,
    SymbolComplexInfinity,
    SymbolDirectedInfinity,
    SymbolExp,
    SymbolI,
    SymbolIndeterminate,
    SymbolLog,
    SymbolPlus,
    SymbolPower,
    SymbolRealSign,
    SymbolSign,
    SymbolSqrt,
    SymbolTimes,
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
    if expr.has_form(SymbolPower, 2):
        base, exp = expr.elements
        if is_zero(exp):
            return Integer1
        if test_arithmetic_expr(expr):
            abs_base = eval_Abs(base)
            if abs_base is None:
                abs_base = Expression(SymbolAbs, base)
            return Expression(SymbolPower, abs_base, exp)
    if expr.has_form(SymbolExp, 1):
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

    if not is_inexact(exp):
        exp_sp = exp.to_sympy()
        if exp_sp is None:
            return None
        return from_sympy(sympy.Exp(exp_sp))

    prec = exp.precision
    if prec is not None:
        if is_machine_precision(exp):
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
    if is_zero(expr):
        return Integer0
    if isinstance(expr, (Integer, Rational, Real)):
        return Integer1 if expr.value > 0 else IntegerM1
    if expr in NUMERICAL_CONSTANTS:
        return Integer1
    if expr.has_form(SymbolAbs, 1):
        arg = expr.elements[0]
        if is_zero(arg):
            return Integer0
        if isinstance(arg, Number):
            return Integer1
        # Try evaluating to an inexact number
        arg_inexact = to_inexact_value(arg)
        if arg_inexact is None:
            return None
        if is_zero(arg_inexact):
            return Integer0
        if isinstance(arg_inexact, Number):
            return Integer1
        return None
    if expr.has_form(SymbolSqrt, 1):
        inner_sign = eval_Sign(expr.elements[0])
        return inner_sign if inner_sign in (Integer0, Integer1) else None
    if expr.has_form(SymbolExp, 1):
        return Integer1 if test_arithmetic_expr(expr.elements[0]) else None
    if expr.has_form(SymbolLog, 1) or expr.has_form(SymbolDirectedInfinity, 1):
        return eval_RealSign(eval_add_numbers(expr.elements[0], IntegerM1))
    if expr.has_form(SymbolTimes, None):
        sign = 1
        for factor in expr.elements:
            factor_sign = eval_RealSign(factor)
            if factor_sign in (None, Integer0):
                return factor_sign
            if factor_sign is IntegerM1:
                sign = -sign
        return Integer1 if sign == 1 else IntegerM1
    if expr.has_form(SymbolPower, 2):
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
    if expr.has_form(SymbolPlus, None):
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


def eval_Sign(expr: Number) -> Optional[BaseElement]:
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
            if n.is_inexact:
                return eval_multiply_numbers(n, eval_Power_number(abs_sq, RealM0p5))
            if test_zero_arithmetic_expr(criteria, numeric=True):
                return n
            return eval_multiply_numbers(n, eval_Power_number(abs_sq, RationalMOneHalf))
        if isinstance(n, Atom):
            return None
        if n.has_form(SymbolAbs, 1):
            inner_sign = eval_Sign(n.elements[0])
            if inner_sign is Integer0:
                return Integer0
            if isinstance(inner_sign, Number):
                return Integer1

        if n.has_form(SymbolExp, 1):
            exponent = n.elements[0]
            if isinstance(exponent, Complex):
                return Expression(SymbolExp, exponent.imag)
            return None
        if n.has_form(SymbolDirectedInfinity, 1):
            return eval_Sign(n.elements[0])
        if n.has_form(SymbolPower, 2):
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

        # Try with Sympy
        try:
            abs_expr = from_sympy(abs(n.to_sympy()))
        except Exception:
            # SymPy conversion failed; fall back.
            return None

        if is_zero(abs_expr):
            return abs_expr
        if abs_expr is Integer1:
            return n
        # Failed to reduce the absolute value:
        if abs_expr.has_form(SymbolAbs, 1):
            return None
        return n / abs_expr

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

    Return a Mathics3 Number or None if the evaluation failed.
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
    if base.is_inexact or exp.is_inexact:
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
        if result.has_form(SymbolPower, 2):
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
        is_machine_precision = base.is_machine_precision or exp.is_machine_precision
        if is_machine_precision:
            number = mpmath.power(base.to_mpmath(), exp.to_mpmath())
            return from_mpmath(number)
        else:
            with mpmath.workprec(prec):
                number = mpmath.power(base.to_mpmath(), exp.to_mpmath())
                return from_mpmath(number, prec)


def _combine_digits(digits: list[float]) -> float:
    """
    Given the precisions (or accuracies) of some numbers in decimal
    digits, returns the precision (or accuracy) of a result whose
    relative (or absolute) error is the sum of their errors:
    ``-Log10[Total[10^-digits]]``.
    """
    least = min(digits)
    return least - math.log10(math.fsum(10.0 ** (least - d) for d in digits))


def _exact_or_precision_reals(
    numbers: tuple[Number, ...], allow_zeros: bool = False
) -> bool:
    """
    True if ``numbers`` has a PrecisionReal, and every other element is an
    exact real number or a PrecisionReal. A PrecisionReal zero is allowed
    only if ``allow_zeros`` is True. Sums and products of these numbers get
    a real-valued precision.
    """
    has_precision_real = False
    for number in numbers:
        if isinstance(number, PrecisionReal):
            if number.is_zero and not allow_zeros:
                return False
            has_precision_real = True
        elif not isinstance(number, (Integer, Rational)):
            return False
    return has_precision_real


def _log10_abs(x: mpmath.mpf) -> float:
    return float(mpmath.log10(abs(x)))


def _stored_bits(numbers) -> int:
    """
    The working precision for ``numbers``: the most bits any of their
    PrecisionReals keeps, and at least MIN_STORED_BITS.
    """
    return max(
        [MIN_STORED_BITS]
        + [
            number.extended_value._prec + 1
            for number in numbers
            if isinstance(number, PrecisionReal)
        ]
    )


def _full_mpmath(number: Number) -> mpmath.mpf:
    """The value of ``number`` with all the bits it keeps."""
    if isinstance(number, PrecisionReal):
        return mpmath.mpf(number.extended_value)
    return number.to_mpmath()


def _precision_real(
    value: mpmath.mpf, precision10: float, accuracy10: float
) -> PrecisionReal:
    """
    Returns ``value`` as a PrecisionReal with ``precision10`` decimal
    digits of precision. If no digit is left, the result is a zero with
    ``accuracy10`` digits of accuracy, as in WMA.
    """
    if value == 0 or precision10 <= 0:
        return PrecisionReal(
            sympy.Float(0, precision=number_prec(math.ceil(accuracy10))), accuracy10
        )
    # The binary precision is rounded up, so that all the digits shown are
    # kept; a low precision keeps more bits of the value, as in WMA.
    return PrecisionReal.from_value(value, precision10)


def eval_mpmath_function_by_condition(
    mpmath_function: Callable,
    condition_numbers: Callable[..., tuple[mpmath.mpf, ...]],
    *args: Number,
    has_poles: bool = False,
    bound: Optional[float] = None,
) -> Optional[BaseElement]:
    """
    Applies ``mpmath_function`` to ``args``, when they are exact real
    numbers or PrecisionReals and the value is a real number. As in WMA,
    the relative error of each argument is multiplied by its factor in
    ``condition_numbers``, and these errors add up. Returns None otherwise,
    or if no argument adds an error.

    Where the factor does not exist, the error is how much f changes within
    the error of its single argument (see ``_change_within``): for a zero
    argument, which has no relative error; at an end of the domain, like
    ArcCos[1.`20], where f'[x] is infinite; and where the value is 0.

    As in WMA, a function with poles (``has_poles``) gives ComplexInfinity
    when no digit is left, as Tan[1.5707963`5]; and a function bounded by
    ``bound`` has an error no larger than that, as Sin[1.`20*^30].
    """
    if len(args) == 1 and isinstance(args[0], PrecisionReal) and args[0].is_zero:
        accuracy10 = args[0].precision10
        if accuracy10 < 1:
            return None
        change = _change_within(
            mpmath_function, mpmath.mpf(0), mpmath.mpf(10) ** -accuracy10, accuracy10
        )
        if change is None:
            return None
        return _value_with_error(*change, has_poles, bound)

    if not _exact_or_precision_reals(args):
        return None
    input_bits = _stored_bits(args)
    with mpmath.workprec(input_bits + 10):
        values = [_full_mpmath(arg) for arg in args]
        value = mpmath_function(*values)
        if not isinstance(value, mpmath.mpf) or not mpmath.isfinite(value):
            return None
        try:
            factors = condition_numbers(*values, value) if value != 0 else None
        except ZeroDivisionError:
            factors = None
        if factors is not None and not all(mpmath.isfinite(f) for f in factors):
            factors = None

    if factors is None:
        if len(args) != 1 or args[0].precision10 < 1:
            return None
        x = values[0]
        digits = args[0].precision10 - _log10_abs(x)
        change = _change_within(
            mpmath_function, x, abs(x) * 10 ** -args[0].precision10, digits
        )
        if change is None:
            return None
        return _value_with_error(*change, has_poles, bound)

    digits = [
        arg.precision10 - _log10_abs(factor)
        for arg, factor in zip(args, factors)
        if isinstance(arg, PrecisionReal) and factor != 0
    ]
    if not digits:
        return None
    precision10 = _combine_digits(digits)
    if precision10 <= 0 and has_poles:
        return SymbolComplexInfinity
    needed_bits = number_prec(max(1, math.ceil(precision10)))
    if needed_bits > input_bits:
        # The result has more digits than the arguments, as in Sqrt.
        with mpmath.workprec(needed_bits + 10):
            value = mpmath_function(*(_full_mpmath(arg) for arg in args))
    accuracy10 = precision10 - _log10_abs(value)
    if precision10 <= 0 and bound is not None:
        accuracy10 = max(accuracy10, -math.log10(bound))
    return _precision_real(value, precision10, accuracy10)


def _change_within(
    mpmath_function: Callable, x: mpmath.mpf, delta: mpmath.mpf, digits: float
) -> Optional[tuple[mpmath.mpf, mpmath.mpf]]:
    """
    The value of f at ``x``, and how much f changes within ``delta`` of it,
    with ``x`` known to ``digits`` digits of accuracy. So Sin[0``20] is
    0``20, Cos[0``20] is 1 with precision 40.301, since Cos changes by only
    (10^-20)^2 / 2, and ArcCos[1.`20] is 0``9.849, since ArcCos changes by
    Sqrt[2 10^-20].

    The smaller change of the two sides is taken: where f is continuous they
    agree, and a branch cut, as for ArcCot at 0, jumps on one side only. A
    side where f has no real value, as above 1 for ArcCos, is left out.
    Returns None if f has no real value at x or on either side.
    """
    # Enough digits for a change of second order.
    with mpmath.workprec(number_prec(math.ceil(2 * max(digits, 1)) + 20)):
        x = mpmath.mpf(x)
        try:
            value = mpmath_function(x)
        except (ZeroDivisionError, ValueError):
            return None
        if not isinstance(value, mpmath.mpf) or not mpmath.isfinite(value):
            return None
        changes = []
        for side in (x + delta, x - delta):
            try:
                other = mpmath_function(side)
            except (ZeroDivisionError, ValueError):
                continue
            if isinstance(other, mpmath.mpf) and mpmath.isfinite(other):
                changes.append(abs(other - value))
        if not changes or min(changes) == 0:
            return None
        return value, min(changes)


def _value_with_error(
    value: mpmath.mpf, error: mpmath.mpf, has_poles: bool, bound: Optional[float]
) -> BaseElement:
    """``value`` with the absolute error ``error``."""
    accuracy10 = -_log10_abs(error)
    if bound is not None:
        accuracy10 = max(accuracy10, -math.log10(bound))
    if value == 0:
        return _precision_real(value, 0, accuracy10)
    precision10 = _log10_abs(value) + accuracy10
    if precision10 <= 0 and has_poles:
        return SymbolComplexInfinity
    return _precision_real(value, precision10, accuracy10)


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

    if any(is_machine_precision(number) for number in numbers):
        terms = (item.to_mpmath() for item in numbers)
        number = mpmath.fsum(terms)
        return from_mpmath(number)

    if _exact_or_precision_reals(numbers, allow_zeros=True):
        # As in WMA, the absolute errors of the terms add up. For a zero,
        # precision10 is its accuracy.
        precision_reals = [
            number for number in numbers if isinstance(number, PrecisionReal)
        ]
        accuracy10 = _combine_digits(
            [
                (
                    number.precision10
                    if number.is_zero
                    else number.precision10 - _log10_abs(_full_mpmath(number))
                )
                for number in precision_reals
            ]
        )
        with mpmath.workprec(_stored_bits(numbers)):
            number = mpmath.fsum(_full_mpmath(item) for item in numbers)
        if number == 0:
            return _precision_real(number, 0, accuracy10)
        return _precision_real(number, accuracy10 + _log10_abs(number), accuracy10)

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

    if any(is_machine_precision(number) for number in numbers):
        factors = (item.to_mpmath() for item in numbers)
        number = mpmath.fprod(factors)
        return from_mpmath(number)

    if _exact_or_precision_reals(numbers, allow_zeros=True):
        if any(number is Integer0 for number in numbers):
            # As in WMA, an exact zero gives an exact zero.
            return Integer0
        zeros = [number for number in numbers if number.is_zero]
        if zeros:
            return _multiply_by_zeros(zeros, numbers)

    if _exact_or_precision_reals(numbers):
        # As in WMA, the relative errors of the factors add up.
        precision_reals = [
            number for number in numbers if isinstance(number, PrecisionReal)
        ]
        precision10 = _combine_digits(
            [number.precision10 for number in precision_reals]
        )
        with mpmath.workprec(_stored_bits(numbers)):
            number = mpmath.fprod(_full_mpmath(item) for item in numbers)
        if number != 0:
            return _precision_real(number, precision10, 0)

    prec = min_prec(*numbers)
    if prec is not None:
        with mpmath.workprec(prec):
            factors = (item.to_mpmath() for item in numbers)
            number = mpmath.fprod(factors)
            return from_mpmath(number, prec)
    else:
        return from_sympy(sympy.Mul(*(item.to_sympy() for item in numbers)))


def _multiply_by_zeros(zeros: list[Number], numbers: tuple[Number, ...]) -> Number:
    """
    The product of ``numbers``, where ``zeros`` are the PrecisionReal zeros
    among them: as in WMA, a zero whose absolute error is that of the
    zeros, times the other factors.
    """
    accuracy10 = math.fsum(zero.precision10 for zero in zeros)
    others = [number for number in numbers if not number.is_zero]
    if others:
        with mpmath.workprec(53):
            accuracy10 -= _log10_abs(mpmath.fprod(item.to_mpmath() for item in others))
    return _precision_real(mpmath.mpf(0), 0, accuracy10)


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
) -> tuple[list[Number], list[BaseElement]]:
    """
    From a list of elements, produce two lists, one with the numeric items
    and the other with the remaining
    """
    items = {True: [], False: []}
    for element in elements:
        items[isinstance(element, Number)].append(element)
    return items[True], items[False]


# Note: we return:
#  tuple[list[Number], list[BaseElement]]
#             ^^^^^
# But the mypy type checking system can't
# look into the loop and its condition and
# prove that the return type is list[Number].
# So we use the weaker type assertion
# which is the one on elements: list[BaseElement].
def segregate_numbers_from_sorted_list(
    *elements: BaseElement,
) -> tuple[list[BaseElement], list[BaseElement]]:
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
    if expr.has_form(SymbolPower, 2):
        base, exponent = elements
        if only_real:
            if isinstance(exponent, Integer):
                return test_arithmetic_expr(base)
        return all(test_arithmetic_expr(item, only_real) for item in elements)
    if expr.has_form(SymbolExp, 1):
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
    if expr.has_form(SymbolSqrt, 1):
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


def to_inexact_value(expr: BaseElement) -> Optional[BaseElement]:
    """
    Converts an expression into an inexact expression.
    Replaces numerical constants by their numerical approximation,
    and then multiplies the expression by Real(1.)
    """
    if is_inexact(expr) is None:
        # Not a number and not an Expression, so leave as is.
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
