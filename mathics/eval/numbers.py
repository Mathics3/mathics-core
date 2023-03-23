from typing import Optional

import mpmath
import sympy

from mathics.core.atoms import Complex, MachineReal, PrecisionReal
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.number import MACHINE_PRECISION_VALUE, ZERO_MACHINE_ACCURACY, dps
from mathics.core.symbols import SymbolPlus


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
            return float(dps(z.get_precision()))
        z_f = z.to_python()
        log10_z = mpmath.log((-z_f if z_f < 0 else z_f), 10)
        return dps(z.get_precision()) - log10_z

    if isinstance(z, Complex):
        acc_real = eval_Accuracy(z.real)
        acc_imag = eval_Accuracy(z.imag)
        if acc_real is None:
            return acc_imag
        if acc_imag is None:
            return acc_real

        return -mpmath.log(10 ** (-2 * acc_real) + 10 ** (-2 * acc_imag), 10.0) * 0.5

    if isinstance(z, Expression):
        elem_accuracies = (eval_Accuracy(z_elem) for z_elem in z.elements)
        return min((acc for acc in elem_accuracies if acc is not None), default=None)
    return None


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
        return float(dps(z.get_precision()))

    if isinstance(z, Complex):
        prec_real = eval_Precision(z.real)
        prec_imag = eval_Precision(z.imag)
        if prec_real is None or prec_imag == prec_real:
            return prec_imag
        if prec_imag is None:
            return prec_real
        # both numbers have different precision.
        # Evaluate the accuracy and add the log of
        # the module.
        acc = eval_Accuracy(z)
        abs_sq = z.real.value**2 + z.imag.value**2
        return acc + mpmath.log(abs_sq, 10.0) * 0.5

    if isinstance(z, Expression):
        elem_prec = (eval_Precision(z_elem) for z_elem in z.elements)
        return min((prec for prec in elem_prec if prec is not None), default=None)

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
