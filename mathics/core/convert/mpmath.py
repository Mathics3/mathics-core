# -*- coding: utf-8 -*-

from functools import lru_cache
from typing import Optional, Union

import mpmath
import sympy

from mathics.core.atoms import Complex, MachineReal, MachineReal0, PrecisionReal
from mathics.core.number import LOG2_10
from mathics.core.symbols import Atom


@lru_cache(maxsize=1024)
def from_mpmath(
    value: Union[mpmath.mpf, mpmath.mpc],
    prec: Optional[float] = None,
    acc: Optional[float] = None,
) -> Atom:
    "Converts mpf or mpc to Number."
    if mpmath.isnan(value):
        return SymbolIndeterminate
    if isinstance(value, mpmath.mpf):
        if mpmath.isinf(value):
            direction = Integer1 if value > 0 else IntegerM1
            return Expression(SymbolDirectedInfinity, direction)
        # if accuracy is given, override
        # prec:
        if acc is not None:
            prec = acc
            if value != 0.0:
                offset = mpmath.log(-value if value < 0.0 else value, 10)
                prec += offset
        if prec is None:
            return MachineReal(float(value))
        # If the error if of the order of the number, the number
        # is compatible with 0.
        if prec < 1.0:
            return MachineReal0
        # HACK: use str here to prevent loss of precision.
        #
        # sympy.Float internally works with (rounded) binary precision
        # instead of decimal precision. Let's use it to avoid rounding errors.
        # TODO: avoid the irrelevant conversion
        return PrecisionReal(sympy.Float(str(value), precision=(LOG2_10 * prec + 2)))
    elif isinstance(value, mpmath.mpc):
        if mpmath.isinf(value):
            return SymbolComplexInfinity
        if value.imag == 0.0:
            return from_mpmath(value.real, prec, acc)
        real = from_mpmath(value.real, prec, acc)
        imag = from_mpmath(value.imag, prec, acc)
        return Complex(real, imag)
    else:
        raise TypeError(type(value))


def to_mpmath_matrix(data, **kwargs):
    """
    Convert a Mathics matrix to one that can be used by mpmath.
    None is returned if we can't convert to a mpmath matrix.
    """

    def mpmath_matrix_data(m):
        if not m.has_form("List", None):
            return None
        if not all(element.has_form("List", None) for element in m.elements):
            return None
        return [[str(item) for item in row.elements] for row in m.elements]

    if not isinstance(data, list):
        data = mpmath_matrix_data(data)
    try:
        return mpmath.matrix(data)
    except (TypeError, AssertionError, ValueError):
        return None
