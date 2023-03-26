# -*- coding: utf-8 -*-

from functools import lru_cache
from typing import Optional, Union

import mpmath
import sympy

from mathics.core.atoms import (
    Complex,
    Integer0,
    Integer1,
    IntegerM1,
    MachineReal,
    MachineReal0,
    PrecisionReal,
)
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolDirectedInfinity, SymbolIndeterminate

ExpressionInfinity = Expression(SymbolDirectedInfinity, Integer1)
ExpressionMInfinity = Expression(SymbolDirectedInfinity, IntegerM1)
ExpressionIInfinity = Expression(SymbolDirectedInfinity, Complex(Integer0, Integer1))
ExpressionMIInfinity = Expression(SymbolDirectedInfinity, Complex(Integer0, IntegerM1))

ExpressionComplexInfinity = Expression(SymbolDirectedInfinity)


@lru_cache(maxsize=1024)
def from_mpmath(
    value: Union[mpmath.mpf, mpmath.mpc],
    precision: Optional[int] = None,
) -> BaseElement:
    """
    Converts mpf or mpc to Number.
    The optional parameter `precision` represents
    the binary precision.
    """
    if mpmath.isnan(value):
        return SymbolIndeterminate
    if isinstance(value, mpmath.mpf):
        if mpmath.isinf(value):
            return ExpressionInfinity if value > 0 else ExpressionMInfinity
        if precision is None:
            return MachineReal(float(value))
        # If the error if of the order of the number, the number
        # is compatible with 0.
        if precision < 1:
            return MachineReal0
        # HACK: use str here to prevent loss of precision
        return PrecisionReal(sympy.Float(str(value), precision=precision - 1))
    elif isinstance(value, mpmath.mpc):
        if value.imag == 0.0:
            return from_mpmath(value.real, precision=precision)
        val_re, val_im = value.real, value.imag
        if mpmath.isinf(val_re):
            if mpmath.isinf(val_im):
                return ExpressionComplexInfinity
            return ExpressionInfinity if val_re > 0 else ExpressionMInfinity
        elif mpmath.isinf(val_im):
            return ExpressionIInfinity if val_im > 0 else ExpressionMIInfinity
        real = from_mpmath(val_re, precision=precision)
        imag = from_mpmath(val_im, precision=precision)
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
