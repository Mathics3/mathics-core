# -*- coding: utf-8 -*-
# cython: language_level=3

import string
from math import ceil, log
from sys import float_info
from typing import List, Optional

import mpmath
import sympy

from mathics.core.element import BaseElement
from mathics.core.symbols import (
    SymbolMachinePrecision,
    SymbolMaxPrecision,
    SymbolMinPrecision,
)

LOG2_10 = mpmath.log(10.0, 2.0)  # ~ 3.3219280948873626

# Number of digits in the mantisa of a normalized floatting point number:
FP_MANTISA_BINARY_DIGITS = float_info.mant_dig  # ~53

# the (integer) number of decimal digits hold by a
# normalized floatting point number.
MACHINE_DIGITS = float_info.dig  # ~15

# the difference between 1. and the next
# representable floatting point number:
MACHINE_EPSILON = float_info.epsilon
# the number of accurate decimal digits hold by a normalized floatting point number.
MACHINE_PRECISION_VALUE = float_info.mant_dig / LOG2_10


#  Maximum normalized float
MAX_MACHINE_NUMBER = float_info.max

#  Minimum positive normalized float
MIN_MACHINE_NUMBER = float_info.min

# the accuracy associated to 0.`
ZERO_MACHINE_ACCURACY = -mpmath.log(MIN_MACHINE_NUMBER, 10.0) + MACHINE_PRECISION_VALUE

# the (integer) number of decimal digits needed to reconstruct a floatting point number.
RECONSTRUCT_MACHINE_PRECISION_DIGITS = int(ceil(float_info.mant_dig / LOG2_10) + 1)


class PrecisionValueError(Exception):
    pass


class SpecialValueError(Exception):
    def __init__(self, name) -> None:
        self.name = name


def _get_float_inf(value, evaluation) -> Optional[float]:
    value = value.evaluate(evaluation)
    if value.has_form("DirectedInfinity", 1):
        if value.elements[0].get_int_value() == 1:
            return float("inf")
        elif value.elements[0].get_int_value() == -1:
            return float("-inf")
        else:
            return None
    return value.round_to_float(evaluation)


def get_precision(value, evaluation, show_messages=True) -> Optional[float]:
    """
    Returns the ``float`` in the interval     [``$MinPrecision``, ``$MaxPrecision``] closest to ``value``.
    If ``value`` does not belongs to that interval, and ``show_messages`` is True, a Message warning is shown.
    If ``value`` fails to be evaluated as a number, returns None.
    """
    if value is SymbolMachinePrecision:
        return None
    else:
        from mathics.core.atoms import MachineReal

        dmin = _get_float_inf(SymbolMinPrecision, evaluation)
        dmax = _get_float_inf(SymbolMaxPrecision, evaluation)
        d = value.round_to_float(evaluation)
        assert dmin is not None and dmax is not None
        if d is None:
            if show_messages:
                evaluation.message("N", "precbd", value)
        elif d < dmin:
            dmin = int(dmin)
            if show_messages:
                evaluation.message("N", "precsm", value, MachineReal(dmin))
            return dmin
        elif d > dmax:
            dmax = int(dmax)
            if show_messages:
                evaluation.message("N", "preclg", value, MachineReal(dmax))
            return dmax
        else:
            return d
        raise PrecisionValueError()


def get_type(value) -> Optional[str]:
    if isinstance(value, sympy.Integer):
        return "z"
    elif isinstance(value, sympy.Rational):
        return "q"
    elif isinstance(value, sympy.Float) or isinstance(value, mpmath.mpf):
        return "f"
    elif (
        isinstance(value, sympy.Expr) and value.is_number and not value.is_real
    ) or isinstance(value, mpmath.mpc):
        return "c"
    else:
        return None


def sameQ(v1, v2) -> bool:
    """Mathics SameQ"""
    return get_type(v1) == get_type(v2) and v1 == v2


def dps(prec) -> int:
    return max(1, int(round(int(prec) / LOG2_10 - 1)))


def prec(dps) -> int:
    return max(1, int(round((int(dps) + 1) * LOG2_10)))


def min_prec(*args: BaseElement) -> Optional[float]:
    """
    Returns the precision of the expression with the minimum precision.
    If all the expressions are exact or non numeric, return None.

    If one of the expressions is an inexact value with zero
    nominal value, then its accuracy is used instead. For example,
    ```min_prec(1, 0.``4) ``` returns 4.

    Notice that this behaviour is different that the one obtained
    using mathics.core.numbers.eval_Precision.
    """
    args_prec = (arg.get_precision() for arg in args)
    return min(
        (arg_prec for arg_prec in args_prec if arg_prec is not None), default=None
    )


def pickle_mp(value):
    return (get_type(value), str(value))


def unpickle_mp(value):
    type, value = value
    if type == "z":
        return sympy.Integer(value)
    elif type == "q":
        return sympy.Rational(value)
    elif type == "f":
        return sympy.Float(value)
    else:
        return value


# algorithm based on
# http://stackoverflow.com/questions/5110177/how-to-convert-floating-point-number-to-base-3-in-python       # nopep8


def convert_base(x, base, precision=10) -> str:
    sign = -1 if x < 0 else 1
    x *= sign

    length_of_int = 0 if x == 0 else int(log(x, base))
    iexps = list(range(length_of_int, -1, -1))
    digits = string.digits + string.ascii_lowercase

    if base > len(digits):
        raise ValueError

    def convert(x, base, exponents):
        out = []
        for e in exponents:
            d = int(x / (base**e))
            x -= d * (base**e)
            out.append(digits[d])
            if x == 0 and e < 0:
                break
        return out

    int_part = convert(int(x), base, iexps)
    if sign == -1:
        int_part.insert(0, "-")

    if isinstance(x, (float, sympy.Float)):
        fexps = list(range(-1, -int(precision + 1), -1))
        real_part = convert(x - int(x), base, fexps)

        return "%s.%s" % ("".join(int_part), "".join(real_part))
    elif isinstance(x, int):
        return "".join(int_part)
    else:
        raise TypeError(x)


def convert_int_to_digit_list(x, base) -> List[int]:
    if x == 0:
        return [0]

    x = abs(x)

    length_of_int = int(log(x, base)) + 1
    iexps = list(range(length_of_int, -1, -1))

    def convert(x, base, exponents):
        out = []
        for e in exponents:
            d = int(x // (base**e))
            x -= d * (base**e)
            if out or d != 0:  # drop any leading zeroes
                out.append(d)
            if x == 0 and e < 0:
                break
        return out

    return convert(x, base, iexps)
