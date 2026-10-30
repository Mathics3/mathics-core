# -*- coding: utf-8 -*-
"""
Implementation of number-handling functions.
"""

import math
from functools import cache
from typing import Optional

import mpmath
import sympy

# Note: it is important *not* use: from mathics.eval.tracing import run_sympy
# but instead import the module and access below as tracing.run_sympy.
# This allows us change where tracing.run_sympy points at runtime.
import mathics.eval.tracing as tracing
from mathics.core.atoms import Complex, MachineReal, PrecisionReal
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.number import MACHINE_PRECISION_VALUE, ZERO_MACHINE_ACCURACY
from mathics.core.symbols import SymbolPlus


def check_finite_decimal(denominator):
    # The rational number is a finite decimal if the denominator has the form 2^a * 5^b
    while denominator % 5 == 0:
        denominator = denominator / 5

    while denominator % 2 == 0:
        denominator = denominator / 2

    return True if denominator == 1 else False


def rational_digits(
    numerator: int, denominator: int, base: int
) -> tuple[list[int], list[int], int]:
    """
    The base-`base` digits of the positive rational numerator/denominator,
    in the form RealDigits gives them: ``(digits, period, exponent)``, where
    the number is 0.d1 d2 ... dk (p1 ... pm)(p1 ... pm)... times
    base^exponent, d1 is not 0 and the pre-period d1 ... dk is as short as
    possible. ``period`` is empty when the expansion terminates.
    """
    integer_part, remainder = divmod(numerator, denominator)
    integer_digits = []
    while integer_part:
        integer_part, digit = divmod(integer_part, base)
        integer_digits.insert(0, digit)

    # Long division; the expansion repeats from the first remainder seen
    # again.
    fraction_digits = []
    position = {}
    while remainder and remainder not in position:
        position[remainder] = len(fraction_digits)
        digit, remainder = divmod(remainder * base, denominator)
        fraction_digits.append(digit)
    if remainder:
        start = position[remainder]
        digits = integer_digits + fraction_digits[:start]
        period = fraction_digits[start:]
    else:
        digits = integer_digits + fraction_digits
        period = []

    exponent = len(integer_digits)
    if not integer_digits:
        # Leading zeros go into the exponent; past the pre-period they
        # rotate the period.
        while digits and digits[0] == 0:
            digits.pop(0)
            exponent -= 1
        if not digits:
            while period[0] == 0:
                period = period[1:] + period[:1]
                exponent -= 1

    # The shortest pre-period: 20/3 is 0.(6) 10^1, not 0.6(6) 10^1.
    while period and digits and digits[-1] == period[-1]:
        period = [digits.pop()] + period[:-1]
    return digits, period, exponent


def leading_exponent(numerator: int, denominator: int, base: int) -> int:
    """
    The exponent e with base^(e-1) <= numerator/denominator < base^e, for
    a positive rational numerator/denominator.
    """

    def at_least(k: int) -> bool:
        # numerator/denominator >= base^k
        if k >= 0:
            return numerator >= denominator * base**k
        return numerator * base**-k >= denominator

    e = int((math.log(numerator) - math.log(denominator)) // math.log(base)) + 1
    while not at_least(e - 1):
        e -= 1
    while at_least(e):
        e += 1
    return e


def truncated_digits(
    numerator: int, denominator: int, base: int, length: int, top: int
) -> list[int]:
    """
    The `length` base-`base` digits of the non-negative rational
    numerator/denominator, starting with the coefficient of base^top,
    cut off rather than rounded.
    """
    shift = length - 1 - top
    if shift >= 0:
        value = numerator * base**shift // denominator
    else:
        value = numerator // (denominator * base**-shift)
    value %= base**length
    digits = []
    for _ in range(length):
        value, digit = divmod(value, base)
        digits.append(digit)
    digits.reverse()
    return digits


def real_digits_truncated(
    x: BaseElement,
    base: int,
    length: int,
    position: Optional[int],
    evaluation,
) -> Optional[tuple[list[int], int]]:
    """
    The `length` base-`base` digits of the absolute value of the exact
    numeric expression x and the exponent, as
    RealDigits[x, base, length, position] gives them; without a position
    the digits start with the leading one.

    As in WMA the digits are cut off, not rounded: RealDigits[1 - 10^-100,
    10, 5] is {{9, 9, 9, 9, 9}, 0}. Rationals are worked out exactly.
    Anything else is evaluated with N at a growing precision, until both
    ends of the interval the value lies in have the same digits, giving
    up to $MaxExtraPrecision digits more than are needed. If they still
    differ, the value lies on (or too close to tell from) the boundary
    between two digit strings, and like WMA we take the boundary:
    RealDigits[(Sqrt[2] + Sqrt[3])^2 - 2 Sqrt[6], 10, 3] is
    {{5, 0, 0}, 1}.

    When x is not real, or is 0 or too close to 0 to find its leading
    digit, a message is given and None is returned, like WMA does.
    """
    from mathics.core.atoms import Complex, Integer, PrecisionReal, Rational
    from mathics.eval.nevaluator import eval_N, get_max_extra_precision

    def exact(numerator: int, denominator: int) -> tuple[list[int], int]:
        if numerator == 0:
            exponent = 0
        else:
            exponent = leading_exponent(numerator, denominator, base)
        top = exponent - 1 if position is None else position
        return (
            truncated_digits(numerator, denominator, base, length, top),
            top + 1,
        )

    if isinstance(x, Integer):
        return exact(abs(x.value), 1)
    if isinstance(x, Rational):
        numerator, denominator = x.value.as_numer_denom()
        return exact(abs(int(numerator)), int(denominator))

    base_digits10 = math.log10(base)
    max_extra = get_max_extra_precision(evaluation)
    # How many base-`base` digits, counted from the leading one, are needed.
    needed = length
    extra = 10.0
    while True:
        # Below machine precision N gives a machine real; we need the
        # precision it has.
        precision = max(needed * base_digits10 + extra, 20.0)
        value = eval_N(x, evaluation, Integer(math.ceil(precision)))
        if isinstance(value, (Integer, Rational)):
            return real_digits_truncated(value, base, length, position, evaluation)
        if not isinstance(value, PrecisionReal):
            if isinstance(value, Complex):
                evaluation.message("RealDigits", "realx", x)
            return None
        # The value is within one unit in its last-but-one significant
        # digit of x.
        numerator, denominator = (
            int(n) for n in sympy.Rational(abs(value.value)).as_numer_denom()
        )
        scale = 10 ** max(0, math.floor(value.precision10) - 1)
        low = (numerator * (scale - 1), denominator * scale)
        high = (numerator * (scale + 1), denominator * scale)
        if not value.is_zero and low[0] > 0:
            exponent = leading_exponent(*high, base)
            top = exponent - 1 if position is None else position
            # The last digit wanted, the coefficient of
            # base^(top - length + 1), is this many digits from the leading
            # one, the coefficient of base^(exponent - 1).
            reach = exponent - top + length - 1
            if reach > needed:
                needed = reach
                continue
            low_result = exact(*low)
            high_result = exact(*high)
            if low_result == high_result:
                return high_result
            if extra >= max_extra:
                return high_result
        elif extra >= max_extra:
            # Not even the leading digit can be found: x is 0, or too
            # close to 0 to tell.
            evaluation.message("RealDigits", "fnumx", x)
            return None
        extra = min(2 * extra, max(max_extra, 10.0))


def convert_float_base(x, base, precision=10):
    length_of_int = 0 if x == 0 else int(mpmath.log(x, base))
    # iexps = list(range(length_of_int, -1, -1))

    def convert_int(x, base, exponents):
        out = []
        for e in range(0, exponents + 1):
            d = x % base
            out.append(d)
            x = x / base
            if x == 0:
                break
        out.reverse()
        return out

    def convert_float(x, base, exponents):
        out = []
        for e in range(0, exponents):
            d = int(x * base)
            out.append(d)
            x = (x * base) - d
            if x == 0:
                break
        return out

    int_part = convert_int(int(x), base, length_of_int)
    if isinstance(x, (float, sympy.Float)):
        # fexps = list(range(-1, -int(precision + 1), -1))
        real_part = convert_float(x - int(x), base, precision + 1)
        return int_part + real_part
    elif isinstance(x, int):
        return int_part
    else:
        raise TypeError(x)


def eval_Accuracy(z: BaseElement) -> Optional[float]:
    """
    Determine the accuracy of an expression expr.
    If z is a Real value, returns a Python float value
    representing the difference between the number of
    significant decimal figures (Precision) and log_10(z).

    For example,
    ```
    12.345`2
    ```
    which is equivalent to 12.`2  has an accuracy of:
    ```
    0.908509 == 2. -  log(10, 12.345)
    ```

    If the expression contains Real values, returns
    the minimal accuracy of all the numbers in the expression.

    Otherwise returns None, representing infinite accuracy.
    """
    if isinstance(z, MachineReal):
        if z.is_zero:
            return ZERO_MACHINE_ACCURACY
        z_f = z.to_python()
        log10_z = mpmath.log((-z_f if z_f < 0 else z_f), 10)
        return MACHINE_PRECISION_VALUE - log10_z

    if isinstance(z, PrecisionReal):
        if z.is_zero:
            return z.precision10
        log10_z = mpmath.log(abs(mpmath.mpf(z.extended_value)), 10)
        return z.precision10 - log10_z

    if isinstance(z, Complex):
        acc_real = eval_Accuracy(z.real)
        acc_imag = eval_Accuracy(z.imag)
        if acc_real is None:
            return acc_imag
        if acc_imag is None:
            return acc_real

        # As in WMA, the errors of the parts add in quadrature.
        least = min(acc_real, acc_imag)
        return least - 0.5 * math.log10(
            10.0 ** (2 * (least - acc_real)) + 10.0 ** (2 * (least - acc_imag))
        )

    if isinstance(z, Expression):
        elem_accuracies = (eval_Accuracy(z_elem) for z_elem in z.elements)
        return min((acc for acc in elem_accuracies if acc is not None), default=None)
    return None


def has_machine_number(z: BaseElement) -> bool:
    """Does ``z`` contain a machine-precision number?"""
    if isinstance(z, MachineReal):
        return True
    if isinstance(z, Complex):
        return has_machine_number(z.real) or has_machine_number(z.imag)
    if isinstance(z, Expression):
        return has_machine_number(z.head) or any(
            has_machine_number(element) for element in z.elements
        )
    return False


def eval_Precision(z: BaseElement) -> Optional[float]:
    """
    Determine the precision of an expression expr.
    If z is a Real value, returns the number of significant
    decimal figures of z. For example,
    ```
    12.345`2
    ```
    which is equivalent to 12.`2  has a precision of 2.

    If the expression contains Real values, returns
    the minimal accuracy of all the numbers in the expression.

    If z is PrecisionReal(0.), the precision is 0. In that case,
    the field "precision" is interpreted as "accuracy".

    Otherwise returns None, representing infinite precision.
    """

    if isinstance(z, MachineReal):
        return MACHINE_PRECISION_VALUE

    if isinstance(z, PrecisionReal):
        if z.is_zero:
            return 0.0
        return z.precision10

    if isinstance(z, Complex):
        if z.is_machine_precision:
            return MACHINE_PRECISION_VALUE
        acc = eval_Accuracy(z)
        if acc is None:
            return None
        # As in WMA, the accuracy plus the log of the modulus, to which an
        # exact part also counts: Precision[1.`20 + 3 I] is 20.5.
        with mpmath.workprec(53):
            modulus = abs(z.to_mpmath())
            if modulus == 0:
                return 0.0
            return acc + float(mpmath.log10(modulus))

    if isinstance(z, Expression):
        elem_prec = (eval_Precision(z_elem) for z_elem in z.elements)
        return min((prec for prec in elem_prec if prec is not None), default=None)

    return None


def cancel(expr):
    if expr.has_form(SymbolPlus, None):
        return Expression(SymbolPlus, *[cancel(element) for element in expr.elements])
    else:
        try:
            result = expr.to_sympy()
            # If the expression cannot be handled by SymPy, just return it.
            if result is None:
                return expr

            # result = sympy.powsimp(result, deep=True)
            result = tracing.run_sympy(sympy.cancel, result)

            # cancel factors out rationals, so we factor them again
            result = sympy_factor(result)

            return from_sympy(result)
        except sympy.PolynomialError:
            # e.g. for non-commutative expressions
            return expr


@cache
def log_n_b(py_n, py_b) -> int:
    return (
        int(mpmath.floor(mpmath.log(py_n, py_b))) + 1 if py_n != 0 and py_n != 1 else 1
    )


def sympy_factor(expr_sympy):
    try:
        result = sympy.together(expr_sympy)
        result = sympy.factor(result)
    except sympy.PolynomialError:
        return expr_sympy
    return result
