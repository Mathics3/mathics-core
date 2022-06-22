# -*- coding: utf-8 -*-

import mpmath
import sympy
from functools import lru_cache
from mathics.core.atoms import (
    Complex,
    MachineReal,
    PrecisionReal,
)


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
