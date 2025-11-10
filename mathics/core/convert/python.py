# -*- coding: utf-8 -*-
"""
Conversions between Python and Mathics3
"""

import numpy
from typing import Any

from mathics.core.atoms import Complex, Integer, NumericArray, Rational, Real, String
from mathics.core.number import get_type
from mathics.core.symbols import (
    BaseElement,
    BooleanType,
    SymbolFalse,
    SymbolNull,
    SymbolTrue,
)
from mathics.core.systemsymbols import SymbolByteArray, SymbolRule


def from_bool(arg: bool) -> BooleanType:
    """
    Conversion from a bool to something Mathics3 can use.
    """
    return SymbolTrue if arg else SymbolFalse


def from_complex(arg: complex) -> Complex:
    """
    Conversion from a Python complex to Complex.

    Care is taken to preserve integer-ness of the
    real and imaginary parts.
    """
    convert_fn = Integer if isinstance(arg.real, int) else Real
    real_value = convert_fn(arg.real)
    convert_fn = Integer if isinstance(arg.imag, int) else Real
    imag_value = convert_fn(arg.imag)
    return Complex(real_value, imag_value)


# Historically, from_python() was identified as a bottleneck.

# A large part of this was due to the inefficient monolithic
# non-specialized interpreter that forced everything into an single
# Expression class which tried to handle anything given it using
# conversions.

# Also, through vague or lazy coding this cause a lot of
# unnecessary conversions.

# We may be out of those days, but we should still
# be mindful that this routine can be the source
# of a bottleneck. So care may be warranted to make
# sure from_python() isn't too slow.


# TODO:
#  I think there are number of subtleties to be explained here.
#  In particular, the expression might been the result of evaluation
#  a SymPy expression which contains SymPy symbols.
#
#  If the end result is to go back into Mathics3 for further
#  evaluation, then probably no problem.  However if the end result
#  is produce say a Python string, then at a minimum we may want to
#  convert backtick (context) symbols into some Python identifier
#  symbol like underscore.


def from_python(arg: Any) -> BaseElement:
    """Converts a Python expression into a Mathics expression."""
    from mathics.core.convert.expression import to_mathics_list
    from mathics.core.expression import Expression
    from mathics.core.list import ListExpression

    if isinstance(arg, BaseElement):
        return arg

    number_type = get_type(arg)

    # We should investigate whether this could be sped up
    # using a dictionary lookup on type.
    if arg is None:
        return SymbolNull
    if isinstance(arg, bool):
        return from_bool(arg)
    if isinstance(arg, int) or number_type == "z":
        return Integer(arg)
    elif isinstance(arg, float) or number_type == "f":
        return Real(arg)
    elif number_type == "q":
        return Rational(arg)
    elif isinstance(arg, complex) or number_type == "c":
        return from_complex(arg)
    elif isinstance(arg, str):
        return String(arg)
        # if arg[0] == arg[-1] == '"':
        #     return String(arg[1:-1])
        # else:
        #     return Symbol(arg)
    elif isinstance(arg, dict):
        entries = [
            Expression(
                SymbolRule,
                from_python(key),
                from_python(arg[key]),
            )
            for key in arg
        ]
        return ListExpression(*entries)
    elif isinstance(arg, list) or isinstance(arg, tuple):
        return to_mathics_list(*arg, elements_conversion_fn=from_python)
    elif isinstance(arg, bytearray) or isinstance(arg, bytes):
        from mathics.builtin.binary.bytearray import ByteArray

        return Expression(SymbolByteArray, ByteArray(arg))
    elif isinstance(arg, numpy.ndarray):
        return NumericArray(arg)
    else:
        raise NotImplementedError
