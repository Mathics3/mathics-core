# -*- coding: utf-8 -*-

import mpmath
import sympy
from functools import lru_cache
from mathics.core.atoms import (
    Complex,
    MachineReal,
    PrecisionReal,
)
from mathics.core.symbols import SymbolList


@lru_cache(maxsize=1024)
def from_mpmath(value, prec=None):
    "Converts mpf or mpc to Number."
    if isinstance(value, mpmath.mpf):
        if prec is None:
            return MachineReal(float(value))
        else:
            # HACK: use str here to prevent loss of precision
            return PrecisionReal(sympy.Float(str(value), prec))
    elif isinstance(value, mpmath.mpc):
        if value.imag == 0.0:
            return from_mpmath(value.real, prec)
        real = from_mpmath(value.real, prec)
        imag = from_mpmath(value.imag, prec)
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
