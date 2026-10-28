# -*- coding: utf-8 -*-
"""
SetPrecision and SetAccuracy.

As in WMA, an inexact number keeps its binary value: SetPrecision[0.1, 20]
is 0.1000000000000000055511..., not 0.1 with more zeros.
"""

import math
from typing import Callable, Final, Optional

import mpmath
import sympy

from mathics.core.atoms import (
    Complex,
    Integer,
    Integer0,
    MachineReal,
    Number,
    PrecisionReal,
    Rational,
)
from mathics.core.attributes import A_CONSTANT
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.number import prec as number_prec
from mathics.core.symbols import Atom, Symbol, SymbolList, SymbolPower
from mathics.eval.nevaluator import eval_N

# The precision or accuracy to set: a number of digits, Infinity (the
# exact value), or None for MachinePrecision.
Target = Optional[float]

LOG10_2: Final[float] = math.log10(2)


def eval_SetPrecision(
    expr: BaseElement, precision: Target, evaluation: Evaluation
) -> BaseElement:
    """
    ``expr`` with each number set to ``precision`` digits, and each numeric
    constant, like Pi, evaluated to that precision.
    """
    return _map_numbers(expr, precision, evaluation, set_accuracy=False)


def eval_SetAccuracy(
    expr: BaseElement, accuracy: float, evaluation: Evaluation
) -> BaseElement:
    """
    ``expr`` with each number set to ``accuracy`` digits of accuracy, and
    each numeric constant, like Pi, evaluated to that accuracy.
    """
    return _map_numbers(expr, accuracy, evaluation, set_accuracy=True)


def _map_numbers(
    expr: BaseElement, target: Target, evaluation: Evaluation, set_accuracy: bool
) -> BaseElement:
    if isinstance(expr, Complex):
        return _set_complex(expr, target, set_accuracy)
    if isinstance(expr, Number):
        if set_accuracy:
            return _set_real_accuracy(expr, target)
        return _set_real_precision(expr, target)
    if isinstance(expr, Symbol):
        return _set_constant(expr, target, evaluation, set_accuracy)
    if isinstance(expr, Atom):
        return expr
    head = _map_numbers(expr.head, target, evaluation, set_accuracy)
    elements = [
        _map_numbers(element, target, evaluation, set_accuracy)
        for element in expr.elements
    ]
    if expr.has_form(SymbolPower, 2) and isinstance(
        expr.elements[1], (Integer, Rational)
    ):
        # As in WMA, an exact exponent stays exact: SetPrecision[Sqrt[2], 20]
        # is Sqrt of 2 with 20 digits.
        elements[1] = expr.elements[1]
    if head is SymbolList:
        return ListExpression(*elements)
    return Expression(head, *elements)


def _set_constant(
    symbol: Symbol, target: Target, evaluation: Evaluation, set_accuracy: bool
) -> BaseElement:
    """A numeric constant, like Pi, evaluated for ``target``."""
    if target == math.inf:
        return symbol
    if not A_CONSTANT & symbol.get_attributes(evaluation.definitions):
        return symbol
    if target is None:
        value = eval_N(symbol, evaluation)
    elif set_accuracy:
        # Enough digits for the accuracy, for a constant that is not huge.
        value = eval_N(symbol, evaluation, MachineReal(max(target, 0.0) + 20))
    else:
        value = eval_N(symbol, evaluation, MachineReal(max(target, 1.0) + 20))
    if not isinstance(value, Number):
        return symbol
    return _map_numbers(value, target, evaluation, set_accuracy)


def _exact(x: Number) -> Number:
    """The exact value of ``x``: for an inexact number, its binary value."""
    if x.is_inexact:
        return from_sympy(sympy.Rational(x.value))
    return x


def _to_mpmath(x: Number, bits: int) -> mpmath.mpf:
    """The value of ``x``, exact if it is inexact, else with ``bits`` bits."""
    if isinstance(x, PrecisionReal):
        value = x.extended_value
        with mpmath.workprec(max(bits, value._prec + 1)):
            return mpmath.mpf(value)
    with mpmath.workprec(bits):
        return x.to_mpmath()


def _with_precision(value: mpmath.mpf, precision10: float) -> PrecisionReal:
    return PrecisionReal.from_value(value, precision10)


def _zero(accuracy10: float) -> PrecisionReal:
    bits = number_prec(max(1, math.ceil(accuracy10)))
    return PrecisionReal(sympy.Float(0, precision=bits), accuracy10)


def _set_real_precision(x: Number, precision10: Target) -> Number:
    if precision10 == math.inf:
        return _exact(x)
    if x.is_zero:
        # As in WMA, SetPrecision[0., 20] is an exact 0.
        return Integer0
    if precision10 is None:
        return MachineReal(float(x.to_mpmath()))
    value = _to_mpmath(x, number_prec(max(1, math.ceil(precision10))) + 10)
    if precision10 <= 0:
        return _zero(precision10 - float(mpmath.log10(abs(value))))
    return _with_precision(value, precision10)


def _set_real_accuracy(x: Number, accuracy10: Target) -> Number:
    if accuracy10 == math.inf:
        return _exact(x)
    if x.is_zero:
        return _zero(accuracy10)
    # A first value, to find the magnitude of x.
    log10_x = float(mpmath.log10(abs(_to_mpmath(x, 53))))
    precision10 = accuracy10 + log10_x
    if precision10 <= 0:
        return _zero(accuracy10)
    value = _to_mpmath(x, number_prec(math.ceil(precision10)) + 10)
    return _with_precision(value, precision10)


def _set_complex(z: Complex, target: Target, set_accuracy: bool) -> BaseElement:
    """
    As in WMA, the parts of z get the same accuracy, such that z has the
    precision or accuracy ``target``.
    """
    parts = (z.real, z.imag)
    if target is None or target == math.inf:
        set_part: Callable[[Number, Target], Number] = (
            _set_real_accuracy if set_accuracy else _set_real_precision
        )
        real, imag = (set_part(part, target) for part in parts)
        return _complex(real, imag)

    with mpmath.workprec(53):
        log10_abs = float(mpmath.log10(abs(mpmath.mpc(*map(_float_value, parts)))))
    if set_accuracy:
        # Exact zeros become inexact ones, so both parts count.
        accuracy10 = target + LOG10_2 / 2
        real, imag = (_set_real_accuracy(part, accuracy10) for part in parts)
        return _complex(real, imag)

    counted = [part for part in parts if not (part.is_zero and not part.is_inexact)]
    accuracy10 = target - log10_abs + math.log10(len(counted)) / 2
    real, imag = (_set_part_accuracy(part, accuracy10) for part in parts)
    return _complex(real, imag)


def _set_part_accuracy(part: Number, accuracy10: float) -> Number:
    """A part of a complex number under SetPrecision."""
    if part.is_zero:
        # As in WMA, an arbitrary-precision zero gets the accuracy, while an
        # exact or a machine zero becomes an exact 0.
        return _zero(accuracy10) if isinstance(part, PrecisionReal) else Integer0
    return _set_real_accuracy(part, accuracy10)


def _float_value(x: Number) -> float:
    return float(x.to_mpmath()) if x.is_inexact else float(x.value)


def _complex(real: Number, imag: Number) -> Number:
    """real + imag I, which is real if imag is an exact 0."""
    if imag is Integer0:
        return real
    return Complex(real, imag)
