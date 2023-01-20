from typing import Optional

import mpmath
import sympy

from mathics.core.atoms import Complex, MachineReal, PrecisionReal, Real
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.number import dps, machine_precision
from mathics.core.symbols import SymbolPlus

MACHINE_PRECISION_VALUE = machine_precision * mpmath.log(2, 10.0)


def eval_accuracy(z: BaseElement) -> Optional[float]:
    """
    Determine the accuracy of an expression expr.
    If z is a Real value, returns the difference between
    the number of significant decimal figures (Precision) and
    log_10(z).

    For example,
    ```
    12.345`2
    ```
    which is equivalent to 12.`2  has an accuracy of
    ```
    0.908509 == 2. -  log(10, 12.345)
    ```

    If the expression contains Real values, returns
    the minimal accuracy of all the numbers in the expression.

    Otherwise returns None, representing infinite accuracy.
    """
    if isinstance(z, Real):
        if z.is_zero:
            # WMA returns 323.607 ~ $MachinePrecision - Log[10, 2.225073*^-308]
            # i.e. the accuracy for the smallest positive double precision value.
            return dps(z.get_precision())
        z_f = z.to_python()
        log10_z = mpmath.log((-z_f if z_f < 0 else z_f), 10)
        return dps(z.get_precision()) - log10_z

    if isinstance(z, Complex):
        acc_real = eval_accuracy(z.real)
        acc_imag = eval_accuracy(z.imag)
        if acc_real is None:
            return acc_imag
        if acc_imag is None:
            return acc_real
        return min(acc_real, acc_imag)

    if isinstance(z, Expression):
        elem_accuracies = (eval_accuracy(z_elem) for z_elem in z.elements)
        try:
            return min(acc for acc in elem_accuracies if acc is not None)
        except ValueError:
            pass
    return None


def eval_precision(z: BaseElement) -> Optional[float]:
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

    Otherwise returns None, representing infinite precision.
    """

    if isinstance(z, MachineReal):
        return MACHINE_PRECISION_VALUE

    if isinstance(z, PrecisionReal):
        if z.is_zero:
            return MACHINE_PRECISION_VALUE
        return float(dps(z.get_precision()))

    if isinstance(z, Complex):
        prec_real = eval_precision(z.real)
        prec_imag = eval_precision(z.imag)
        if prec_real is None:
            return prec_imag
        if prec_imag is None:
            return prec_real
        return min(prec_real, prec_imag)

    if isinstance(z, Expression):
        elem_prec = (eval_precision(z_elem) for z_elem in z.elements)
        candidates = tuple((prec for prec in elem_prec if prec is not None))
        result = min(candidates)
        return result

    return None


def cancel(expr):
    if expr.has_form("Plus", None):
        return Expression(SymbolPlus, *[cancel(element) for element in expr.elements])
    else:
        try:
            result = expr.to_sympy()
            if result is None:
                return None

            # result = sympy.powsimp(result, deep=True)
            result = sympy.cancel(result)

            # cancel factors out rationals, so we factor them again
            result = sympy_factor(result)

            return from_sympy(result)
        except sympy.PolynomialError:
            # e.g. for non-commutative expressions
            return expr


def sympy_factor(expr_sympy):
    try:
        result = sympy.together(expr_sympy)
        result = sympy.factor(result)
    except sympy.PolynomialError:
        return expr_sympy
    return result
