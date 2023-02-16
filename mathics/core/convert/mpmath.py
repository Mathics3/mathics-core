# -*- coding: utf-8 -*-

from functools import lru_cache
from typing import Optional, Union

import mpmath
import sympy

from mathics.core.atoms import (
    Complex,
    Integer1,
    IntegerM1,
    MachineReal,
    MachineReal0,
    PrecisionReal,
)
from mathics.core.expression import Expression
from mathics.core.symbols import Atom
from mathics.core.systemsymbols import (
    SymbolComplexInfinity,
    SymbolDirectedInfinity,
    SymbolIndeterminate,
)


@lru_cache(maxsize=1024)
def from_mpmath(
    value: Union[mpmath.mpf, mpmath.mpc],
    precision: Optional[int] = None,
) -> Atom:
    """
    Converts mpf or mpc to Number.
    The optional parameter `precision` represents
    the binary precision.
    """
    if mpmath.isnan(value):
        return SymbolIndeterminate
    if isinstance(value, mpmath.mpf):
        if mpmath.isinf(value):
            direction = Integer1 if value > 0 else IntegerM1
            return Expression(SymbolDirectedInfinity, direction)
        if precision is None:
            return MachineReal(float(value))
        # If the error if of the order of the number, the number
        # is compatible with 0.
        if precision < 1:
            return MachineReal0
        # HACK: use str here to prevent loss of precision
        return PrecisionReal(sympy.Float(str(value), precision=precision - 1))
    elif isinstance(value, mpmath.mpc):
        if mpmath.isinf(value):
            return SymbolComplexInfinity
        if value.imag == 0.0:
            return from_mpmath(value.real, precision=precision)
        real = from_mpmath(value.real, precision=precision)
        imag = from_mpmath(value.imag, precision=precision)
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
