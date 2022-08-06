# cython: language_level=3
# -*- coding: utf-8 -*-

import base64
import math
import mpmath
import re
import sympy
import typing

from typing import Any, Optional
from functools import lru_cache


from mathics.core.element import ImmutableValueMixin
from mathics.core.number import (
    dps,
    prec,
    min_prec,
    machine_digits,
    machine_precision,
)
from mathics.core.symbols import (
    Atom,
    NumericOperators,
    Symbol,
    SymbolNull,
    SymbolTrue,
    system_symbols,
)
from mathics.core.systemsymbols import SymbolInfinity

# Imperical number that seems to work.
# We have to be able to match mpmath values with sympy values
COMPARE_PREC = 50

SymbolI = Symbol("I")
SymbolString = Symbol("String")

SYSTEM_SYMBOLS_INPUT_OR_FULL_FORM = system_symbols("InputForm", "FullForm")


class Number(Atom, ImmutableValueMixin, NumericOperators):
    """
    Different kinds of Mathics Numbers, the main built-in subclasses
    being: Integer, Rational, Real, Complex.
    """

    def __str__(self) -> str:
        return str(self.value)

    def is_numeric(self, evaluation=None) -> bool:
        return True


def _ExponentFunction(value):
    n = value.get_int_value()
    if -5 <= n <= 5:
        return SymbolNull
    else:
        return value


def _NumberFormat(man, base, exp, options):
    from mathics.builtin.box.inout import RowBox, SuperscriptBox
    from mathics.core.formatter import _BoxedString

    if exp.get_string_value():
        if options["_Form"] in (
            "System`InputForm",
            "System`StandardForm",
            "System`FullForm",
        ):
            return RowBox(man, _BoxedString("*^"), exp)
        else:
            return RowBox(
                man,
                _BoxedString(options["NumberMultiplier"]),
                SuperscriptBox(base, exp),
            )
    else:
        return man


_number_form_options = {
    "DigitBlock": [0, 0],
    "ExponentFunction": _ExponentFunction,
    "ExponentStep": 1,
    "NumberFormat": _NumberFormat,
    "NumberPadding": ["", "0"],
    "NumberPoint": ".",
    "NumberSigns": ["-", ""],
    "SignPadding": False,
    "NumberMultiplier": "\u00d7",
}


class Integer(Number):
    value: int
    class_head_name = "System`Integer"

    # We use __new__ here to unsure that two Integer's that have the same value
    # return the same object.
    def __new__(cls, value) -> "Integer":
        n = int(value)
        self = super(Integer, cls).__new__(cls)
        self.value = n
        return self

    def __eq__(self, other) -> bool:
        return (
            self.value == other.value
            if isinstance(other, Integer)
            else super().__eq__(other)
        )

    def __le__(self, other) -> bool:
        return (
            self.value <= other.value
            if isinstance(other, Integer)
            else super().__le__(other)
        )

    def __lt__(self, other) -> bool:
        return (
            self.value < other.value
            if isinstance(other, Integer)
            else super().__lt__(other)
        )

    def __ge__(self, other) -> bool:
        return (
            self.value >= other.value
            if isinstance(other, Integer)
            else super().__ge__(other)
        )

    def __gt__(self, other) -> bool:
        return (
            self.value > other.value
            if isinstance(other, Integer)
            else super().__gt__(other)
        )

    def __ne__(self, other) -> bool:
        return (
            self.value != other.value
            if isinstance(other, Integer)
            else super().__ne__(other)
        )

    def abs(self) -> "Integer":
        return -self if self < Integer0 else self

    @lru_cache()
    def __init__(self, value):
        super().__init__()

    def make_boxes(self, form) -> "_BoxedString":
        from mathics.core.formatter import _BoxedString

        if form in ("System`InputForm", "System`FullForm"):
            return _BoxedString(str(self.value), number_as_text=True)
        return _BoxedString(str(self.value))

    def atom_to_boxes(self, f, evaluation):
        return self.make_boxes(f.get_name())

    def default_format(self, evaluation, form) -> str:
        return str(self.value)

    def to_sympy(self, **kwargs):
        return sympy.Integer(self.value)

    def to_mpmath(self):
        return mpmath.mpf(self.value)

    def to_python(self, *args, **kwargs):
        return self.value

    def round(self, d=None) -> typing.Union["MachineReal", "PrecisionReal"]:
        if d is None:
            d = self.value.bit_length()
            if d <= machine_precision:
                return MachineReal(float(self.value))
            else:
                # machine_precision / log_2(10) + 1
                d = machine_digits
        return PrecisionReal(sympy.Float(self.value, d))

    def get_int_value(self) -> int:
        return self.value

    def sameQ(self, other) -> bool:
        """Mathics SameQ"""
        return isinstance(other, Integer) and self.value == other.value

    def get_sort_key(self, pattern_sort=False) -> tuple:
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            return (0, 0, self.value, 0, 1)

    def do_copy(self) -> "Integer":
        return Integer(self.value)

    def __hash__(self):
        return hash(("Integer", self.value))

    def user_hash(self, update):
        update(b"System`Integer>" + str(self.value).encode("utf8"))

    def __getnewargs__(self):
        return (self.value,)

    def __neg__(self) -> "Integer":
        return Integer(-self.value)

    @property
    def is_zero(self) -> bool:
        return self.value == 0


Integer0 = Integer(0)
Integer1 = Integer(1)
Integer2 = Integer(2)
Integer3 = Integer(3)
Integer310 = Integer(310)
Integer10 = Integer(10)
IntegerM1 = Integer(-1)


class Rational(Number):
    class_head_name = "System`Rational"

    @lru_cache()
    def __new__(cls, numerator, denominator=1) -> "Rational":
        self = super().__new__(cls)
        self.value = sympy.Rational(numerator, denominator)
        return self

    def atom_to_boxes(self, f, evaluation):
        from mathics.core.formatter import format_element

        return format_element(self, evaluation, f)

    def to_sympy(self, **kwargs):
        return self.value

    def to_mpmath(self):
        return mpmath.mpf(self.value)

    def to_python(self, *args, **kwargs) -> float:
        return float(self.value)

    def round(self, d=None) -> typing.Union["MachineReal", "PrecisionReal"]:
        if d is None:
            return MachineReal(float(self.value))
        else:
            return PrecisionReal(self.value.n(d))

    def sameQ(self, other) -> bool:
        """Mathics SameQ"""
        return isinstance(other, Rational) and self.value == other.value

    def numerator(self) -> "Integer":
        return Integer(self.value.as_numer_denom()[0])

    def denominator(self) -> "Integer":
        return Integer(self.value.as_numer_denom()[1])

    def default_format(self, evaluation, form) -> str:
        return "Rational[%s, %s]" % self.value.as_numer_denom()

    def get_sort_key(self, pattern_sort=False) -> tuple:
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            # HACK: otherwise "Bus error" when comparing 1==1.
            return (0, 0, sympy.Float(self.value), 0, 1)

    def do_copy(self) -> "Rational":
        return Rational(self.value)

    def __hash__(self):
        return hash(("Rational", self.value))

    def user_hash(self, update) -> None:
        update(
            b"System`Rational>" + ("%s>%s" % self.value.as_numer_denom()).encode("utf8")
        )

    def __getnewargs__(self):
        return (self.numerator().get_int_value(), self.denominator().get_int_value())

    def __neg__(self) -> "Rational":
        return Rational(
            -self.numerator().get_int_value(), self.denominator().get_int_value()
        )

    @property
    def is_zero(self) -> bool:
        return (
            self.numerator().is_zero
        )  # (implicit) and not (self.denominator().is_zero)


RationalOneHalf = Rational(1, 2)


class Real(Number):
    class_head_name = "System`Real"

    # __new__ rather than __init__ is used here because the kind of
    # object created differs based on contents of "value".
    def __new__(cls, value, p=None) -> "Real":
        """
        Return either a MachineReal or a PrecisionReal object.
        Or raise a TypeError
        """
        if isinstance(value, str):
            value = str(value)
            if p is None:
                digits = ("".join(re.findall("[0-9]+", value))).lstrip("0")
                if digits == "":  # Handle weird Mathematica zero case
                    p = max(prec(len(value.replace("0.", ""))), machine_precision)
                else:
                    p = prec(len(digits.zfill(dps(machine_precision))))
        elif isinstance(value, sympy.Float):
            if p is None:
                p = value._prec + 1
        elif isinstance(value, (Integer, sympy.Number, mpmath.mpf, float, int)):
            if p is not None and p > machine_precision:
                value = str(value)
        else:
            raise TypeError("Unknown number type: %s (type %s)" % (value, type(value)))

        # return either machine precision or arbitrary precision real
        if p is None or p == machine_precision:
            return MachineReal.__new__(MachineReal, value)
        else:
            return PrecisionReal.__new__(PrecisionReal, value)

    def __eq__(self, other) -> bool:
        if isinstance(other, Real):
            # MMA Docs: "Approximate numbers that differ in their last seven
            # binary digits are considered equal"
            _prec = min_prec(self, other)
            with mpmath.workprec(_prec):
                rel_eps = 0.5 ** (_prec - 7)
                return mpmath.almosteq(
                    self.to_mpmath(), other.to_mpmath(), abs_eps=0, rel_eps=rel_eps
                )
        else:
            return self.get_sort_key() == other.get_sort_key()

    def __ne__(self, other) -> bool:
        # Real is a total order
        return not (self == other)

    def atom_to_boxes(self, f, evaluation):
        return self.make_boxes(f.get_name())

    def get_sort_key(self, pattern_sort=False) -> tuple:
        if pattern_sort:
            return super().get_sort_key(True)
        return (0, 0, self.value, 0, 1)

    def is_nan(self, d=None) -> bool:
        return isinstance(self.value, sympy.core.numbers.NaN)

    def __hash__(self):
        # ignore last 7 binary digits when hashing
        _prec = self.get_precision()
        return hash(("Real", self.to_sympy().n(dps(_prec))))

    def user_hash(self, update):
        # ignore last 7 binary digits when hashing
        _prec = self.get_precision()
        update(b"System`Real>" + str(self.to_sympy().n(dps(_prec))).encode("utf8"))


class MachineReal(Real):
    """
    Machine precision real number.

    Stored internally as a python float.
    """

    value: float

    def __new__(cls, value) -> "MachineReal":
        self = Number.__new__(cls)
        self.value = float(value)
        if math.isinf(self.value) or math.isnan(self.value):
            raise OverflowError
        return self

    def to_python(self, *args, **kwargs) -> float:
        return self.value

    def to_sympy(self, *args, **kwargs):
        return sympy.Float(self.value)

    def to_mpmath(self):
        return mpmath.mpf(self.value)

    def round(self, d=None) -> "MachineReal":
        return self

    def sameQ(self, other) -> bool:
        """Mathics SameQ for MachineReal.
        If the other comparision value is a MachineReal, the values
        have to be equal.  If the other value is a PrecisionReal though, then
        the two values have to be within 1/2 ** (precision) of
        other-value's precision.  For any other type, sameQ is False.
        """
        if isinstance(other, MachineReal):
            return self.value == other.value
        if isinstance(other, PrecisionReal):
            other_value = other.value
            value = self.to_sympy()
            # If sympy fixes the issue, this comparison would be
            # enough
            if value == other_value:
                return True
            # this handles the issue...
            diff = abs(value - other_value)
            prec = min(value._prec, other_value._prec)
            return diff < 0.5 ** (prec)
        else:
            return False

    def is_machine_precision(self) -> bool:
        return True

    def get_precision(self) -> float:
        """Returns the default specification for precision in N and other numerical functions."""
        return machine_precision

    def get_float_value(self, permit_complex=False) -> float:
        return self.value

    def make_boxes(self, form):
        from mathics.builtin.inout import number_form

        _number_form_options["_Form"] = form  # passed to _NumberFormat
        if form in ("System`InputForm", "System`FullForm"):
            n = None
        else:
            n = 6
        return number_form(self, n, None, None, _number_form_options)

    def __getnewargs__(self):
        return (self.value,)

    def do_copy(self) -> "MachineReal":
        return MachineReal(self.value)

    def __neg__(self) -> "MachineReal":
        return MachineReal(-self.value)

    @property
    def is_zero(self) -> bool:
        return self.value == 0.0

    @property
    def is_approx_zero(self) -> bool:
        # In WMA, Chop[10.^(-10)] == 0,
        # so, lets take it.
        res = abs(self.value) <= 1e-10
        return res


class PrecisionReal(Real):
    """
    Arbitrary precision real number.

    Stored internally as a sympy.Float.

    Note: Plays nicely with the mpmath.mpf (float) type.
    """

    value: sympy.Float

    def __new__(cls, value) -> "PrecisionReal":
        self = Number.__new__(cls)
        self.value = sympy.Float(value)
        return self

    def to_python(self, *args, **kwargs):
        return float(self.value)

    def to_sympy(self, *args, **kwargs):
        return self.value

    def to_mpmath(self):
        return mpmath.mpf(self.value)

    def round(self, d=None) -> typing.Union["MachineReal", "PrecisionReal"]:
        if d is None:
            return MachineReal(float(self.value))
        else:
            d = min(dps(self.get_precision()), d)
            return PrecisionReal(self.value.n(d))

    def sameQ(self, other) -> bool:
        """Mathics SameQ for PrecisionReal"""
        if isinstance(other, PrecisionReal):
            other_value = other.value
        elif isinstance(other, MachineReal):
            other_value = other.to_sympy()
        else:
            return False
        value = self.value
        # If sympy would handle properly
        # the precision, this wold be enough
        if value == other_value:
            return True
        # in the meantime, let's use this comparison.
        value = self.value
        prec = min(value._prec, other_value._prec)
        diff = abs(value - other_value)
        return diff < 0.5**prec

    def get_precision(self) -> float:
        """Returns the default specification for precision in N and other numerical functions."""
        return self.value._prec + 1.0

    def make_boxes(self, form):
        from mathics.builtin.inout import number_form

        _number_form_options["_Form"] = form  # passed to _NumberFormat
        return number_form(
            self, dps(self.get_precision()), None, None, _number_form_options
        )

    def __getnewargs__(self):
        return (self.value,)

    def do_copy(self) -> "PrecisionReal":
        return PrecisionReal(self.value)

    def __neg__(self) -> "PrecisionReal":
        return PrecisionReal(-self.value)

    @property
    def is_zero(self) -> bool:
        return self.value == 0.0


class Complex(Number):
    """
    Complex wraps two real-valued Numbers.
    """

    class_head_name = "System`Complex"
    real: Any
    imag: Any

    def __new__(cls, real, imag):
        self = super().__new__(cls)
        if isinstance(real, Complex) or not isinstance(real, Number):
            raise ValueError("Argument 'real' must be a real number.")
        if imag is SymbolInfinity:
            return SymbolI * SymbolInfinity
        if isinstance(imag, Complex) or not isinstance(imag, Number):
            raise ValueError("Argument 'imag' must be a real number.")

        if imag.sameQ(Integer0):
            return real

        if isinstance(real, MachineReal) and not isinstance(imag, MachineReal):
            imag = imag.round()
        if isinstance(imag, MachineReal) and not isinstance(real, MachineReal):
            real = real.round()

        self.real = real
        self.imag = imag
        return self

    def atom_to_boxes(self, f, evaluation):
        from mathics.core.formatter import format_element

        return format_element(self, evaluation, f)

    def __str__(self) -> str:
        return str(self.to_sympy())

    def to_sympy(self, **kwargs):
        return self.real.to_sympy() + sympy.I * self.imag.to_sympy()

    def to_python(self, *args, **kwargs):
        return complex(
            self.real.to_python(*args, **kwargs), self.imag.to_python(*args, **kwargs)
        )

    def to_mpmath(self):
        return mpmath.mpc(self.real.to_mpmath(), self.imag.to_mpmath())

    def default_format(self, evaluation, form) -> str:
        return "Complex[%s, %s]" % (
            self.real.default_format(evaluation, form),
            self.imag.default_format(evaluation, form),
        )

    def get_sort_key(self, pattern_sort=False) -> tuple:
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            return (0, 0, self.real.get_sort_key()[2], self.imag.get_sort_key()[2], 1)

    def sameQ(self, other) -> bool:
        """Mathics SameQ"""
        return (
            isinstance(other, Complex)
            and self.real == other.real
            and self.imag == other.imag
        )

    def round(self, d=None) -> "Complex":
        real = self.real.round(d)
        imag = self.imag.round(d)
        return Complex(real, imag)

    def is_machine_precision(self) -> bool:
        if self.real.is_machine_precision() or self.imag.is_machine_precision():
            return True
        return False

    def get_float_value(self, permit_complex=False) -> Optional[complex]:
        if permit_complex:
            real = self.real.get_float_value()
            imag = self.imag.get_float_value()
            if real is not None and imag is not None:
                return complex(real, imag)
        else:
            return None

    def get_precision(self) -> Optional[float]:
        """Returns the default specification for precision in N and other numerical functions.
        When `None` is be returned no precision is has been defined and this object's value is
        exact.

        This function is called by method `is_inexact()`.
        """
        real_prec = self.real.get_precision()
        imag_prec = self.imag.get_precision()
        if imag_prec is None or real_prec is None:
            return None
        return min(real_prec, imag_prec)

    def do_copy(self) -> "Complex":
        return Complex(self.real.do_copy(), self.imag.do_copy())

    def __hash__(self):
        return hash(("Complex", self.real, self.imag))

    def user_hash(self, update) -> None:
        update(b"System`Complex>")
        update(self.real)
        update(self.imag)

    def __eq__(self, other) -> bool:
        if isinstance(other, Complex):
            return self.real == other.real and self.imag == other.imag
        else:
            return self.get_sort_key() == other.get_sort_key()

    def __getnewargs__(self):
        return (self.real, self.imag)

    def __neg__(self):
        return Complex(-self.real, -self.imag)

    @property
    def is_zero(self) -> bool:
        return self.real.is_zero and self.imag.is_zero

    @property
    def is_approx_zero(self) -> bool:
        real_zero = (
            self.real.is_approx_zero
            if hasattr(self.real, "is_approx_zero")
            else self.real.is_zero
        )
        imag_zero = (
            self.imag.is_approx_zero
            if hasattr(self.imag, "is_approx_zero")
            else self.imag.is_zero
        )
        return real_zero and imag_zero


class String(Atom, ImmutableValueMixin):
    value: str
    class_head_name = "System`String"

    def __new__(cls, value):
        self = super().__new__(cls)

        self.value = str(value)
        return self

    def __str__(self) -> str:
        return '"%s"' % self.value

    def atom_to_boxes(self, f, evaluation):
        from mathics.core.formatter import _BoxedString

        inner = str(self.value)
        if f in SYSTEM_SYMBOLS_INPUT_OR_FULL_FORM:
            inner = inner.replace("\\", "\\\\")
            return _BoxedString(
                '"' + inner + '"', **{"System`ShowStringCharacters": SymbolTrue}
            )
        return _BoxedString('"' + inner + '"')

    def do_copy(self) -> "String":
        return String(self.value)

    def default_format(self, evaluation, form) -> str:
        value = self.value.replace("\\", "\\\\").replace('"', '\\"')
        return '"%s"' % value

    def get_sort_key(self, pattern_sort=False) -> tuple:
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            return (0, 1, self.value, 0, 1)

    def sameQ(self, other) -> bool:
        """Mathics SameQ"""
        return isinstance(other, String) and self.value == other.value

    def get_string_value(self) -> str:
        return self.value

    def to_sympy(self, **kwargs):
        return None

    def to_python(self, *args, **kwargs) -> str:
        if kwargs.get("string_quotes", True):
            return '"%s"' % self.value  # add quotes to distinguish from Symbols
        else:
            return self.value

    def __hash__(self):
        return hash(("String", self.value))

    def user_hash(self, update):
        # hashing a String is the one case where the user gets the untampered
        # hash value of the string's text. this corresponds to MMA behavior.
        update(self.value.encode("utf8"))

    def __getnewargs__(self):
        return (self.value,)


class ByteArrayAtom(Atom, ImmutableValueMixin):
    value: str
    class_head_name = "System`ByteArrayAtom"

    # We use __new__ here to unsure that two ByteArrayAtom's that have the same value
    # return the same object.
    def __new__(cls, value):
        self = super().__new__(cls)
        if type(value) in (bytes, bytearray):
            self.value = value
        elif type(value) is list:
            self.value = bytearray(list)
        elif type(value) is str:
            self.value = base64.b64decode(value)
        else:
            raise Exception("value does not belongs to a valid type")
        return self

    def __str__(self) -> str:
        return base64.b64encode(self.value).decode("utf8")

    def atom_to_boxes(self, f, evaluation) -> "_BoxedString":
        from mathics.core.formatter import _BoxedString

        res = _BoxedString('""' + self.__str__() + '""')
        return res

    def do_copy(self) -> "ByteArrayAtom":
        return ByteArrayAtom(self.value)

    def default_format(self, evaluation, form) -> str:
        value = self.value
        return '"' + value.__str__() + '"'

    def get_sort_key(self, pattern_sort=False) -> tuple:
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            return (0, 1, self.value, 0, 1)

    def sameQ(self, other) -> bool:
        """Mathics SameQ"""
        # FIX: check
        if isinstance(other, ByteArrayAtom):
            return self.value == other.value
        return False

    def get_string_value(self) -> Optional[str]:
        try:
            return self.value.decode("utf-8")
        except Exception:
            return None

    def to_sympy(self, **kwargs):
        return None

    def to_python(self, *args, **kwargs) -> str:
        return self.value

    def __hash__(self):
        return hash(("ByteArrayAtom", self.value))

    def user_hash(self, update):
        # hashing a String is the one case where the user gets the untampered
        # hash value of the string's text. this corresponds to MMA behavior.
        update(self.value)

    def __getnewargs__(self):
        return (self.value,)


class StringFromPython(String):
    def __new__(cls, value):
        self = super().__new__(cls, value)
        if isinstance(value, sympy.NumberSymbol):
            self.value = "sympy." + str(value)

        # Note that the test is done with math.inf first.
        # This is to use float's ==, which may not strictly be necessary.
        if math.inf == value:
            self.value = "math.inf"
        return self
