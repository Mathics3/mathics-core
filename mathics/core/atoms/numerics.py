"""
Numeric types: Number, Integer Real, MachineReal, PrecisionReal, Complex, Rational
"""

# Note: Python warns of ambiguity with NumPy's module numpy.numerics if we name this file numeric.py

# For atomic numeric classes here, there can be many instances created during symbolic computations.

# On the use of slots.
# Benefits:
# * __slots__ can reduce memory consumption by more than half.
#     Standard object (with __dict__): ~150–200 bytes per instance.
#     Slotted object (with __slots__): ~48–64 bytes per instance.
# * Reading and writing slotted attributes (self._value) is about 15% to 30% faster than reading from __dict__
#     because Python accesses a fixed index in a C-array rather than performing a dictionary hash table lookup.

import math
import re
from functools import cache
from typing import Any, Generic, Optional, TypeVar, Union

import mpmath
import sympy
from sympy import Float as sympy_Float
from sympy.core import numbers as sympy_numbers

from mathics.core.atoms.strings import String
from mathics.core.element import ImmutableValueMixin
from mathics.core.keycomparable import BASIC_ATOM_NUMBER_ELT_ORDER
from mathics.core.number import (
    FP_MANTISA_BINARY_DIGITS,
    MAX_MACHINE_NUMBER,
    MIN_MACHINE_NUMBER,
    dps,
    min_prec,
    prec,
)
from mathics.core.symbols import Atom, NumericOperators, Symbol, SymbolNull, symbol_set
from mathics.core.systemsymbols import (
    SymbolFullForm,
    SymbolI,
    SymbolInfinity,
    SymbolInputForm,
)

# The value below is an empirical number for comparison precedence
# that seems to work.  We have to be able to match mpmath values with
# sympy values
COMPARE_PREC = 50

SYSTEM_SYMBOLS_INPUT_OR_FULL_FORM = symbol_set(SymbolInputForm, SymbolFullForm)

T = TypeVar("T")


class Number(Atom, ImmutableValueMixin, NumericOperators, Generic[T]):
    """
    Different kinds of Mathics3 Numbers, the main built-in subclasses
    being: Integer, Rational, Real, Complex.
    """

    __slots__ = ("_value", "hash")
    _value: Any
    hash: int

    def __eq__(self, other):
        if isinstance(other, Number):
            return self.element_order == other.element_order
        else:
            return False

    def __getnewargs__(self) -> tuple:
        """
        __getnewargs__ is used in pickle loading to ensure __new__ is
        called with the right value.

        Most of the time, a number takes one argument - its value
        When there is a kind of number, like Rational or Complex,
        that has more than one argument, it should define this method
        accordingly.
        """
        return (self._value,)

    def __str__(self) -> str:
        return str(self.value)

    def default_format(self, evaluation, form) -> str:
        return str(self.value)

    def do_copy(self) -> "Number":
        raise NotImplementedError

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return (
            BASIC_ATOM_NUMBER_ELT_ORDER,
            self.value,
            0,
            1,
        )

    def get_float_value(
        self, evaluation=None, permit_complex: bool = False
    ) -> Optional[Union[complex, float]]:
        try:
            return float(self._value)
        except Exception:
            return None

    @property
    def int_value(self) -> Optional[int]:
        return None

    @property
    def is_literal(self) -> bool:
        """Number can't change and has a Python representation,
        i.e., a value is set, and it does not depend on definition
        bindings. So we say it is a literal.
        """
        return True

    def is_numeric(self, evaluation=None) -> bool:
        # Anything that is in a number class is Numeric, so return True.
        return True

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        return super().pattern_precedence

    def round(self, d: Optional[int] = None) -> "Number":
        """
        Produce a Real approximation of ``self`` with decimal precision ``d``.
        """
        return self

    def round_to_float(
        self, evaluation=None, permit_complex: bool = True
    ) -> float | None:
        try:
            return float(self._value)
        except Exception:
            return None

    def to_mpmath(self, precision: Optional[int] = None) -> mpmath.mpf:
        """
        Convert self.value to an mpmath number with precision ``precision``
        If ``precision`` is None, use mpmath's default precision.

        A mpmath number is the default implementation for Number.
        There are kinds of numbers, like Rational or Complex, that
        need to work differently than this default, and they will
        change the implementation accordingly.
        """
        if precision is not None:
            with mpmath.workprec(precision):
                return mpmath.mpf(self.value)
        return mpmath.mpf(self.value)

    def to_python(self, *_, **kwargs):
        """Returns a native builtin Python object
        something in (int, float, complex, str, tuple, list or dict.).
        (See discussions in
        https://github.com/Mathics3/mathics-core/discussions/550
        and
        https://github.com/Mathics3/mathics-core/pull/551
        """
        return self.value

    @property
    def value(self) -> T:
        """Equivalent value in either SymPy's or Python's native
        datatype if that exists. Note that the SymPy value
        and the Python value might be the same thing.
        """
        return self._value


def _ExponentFunction(value):
    n = value.int_value
    if -5 <= n <= 5:
        return SymbolNull
    else:
        return value


def _NumberFormat(man, base, exp, options):
    from mathics.builtin.box.layout import RowBox, SuperscriptBox

    if exp.get_string_value():
        if options["_Form"] in (
            "System`InputForm",
            "System`StandardForm",
            "System`FullForm",
        ):
            return RowBox(man, String("*^"), exp)
        else:
            return RowBox(
                man,
                String(options["NumberMultiplier"]),
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


class Integer(Number[int]):
    __slots__ = ("hash", "_sympy", "_value")

    class_head_name = "System`Integer"

    # Dictionary of Integer constant values defined so far.
    # We use this for object uniqueness.
    # The key is the Integer's Python `int` value, and the
    # dictionary's value is the corresponding Mathics3 Integer object.
    _integers: dict[int, "Integer"] = {}
    _sympy: Optional[sympy_numbers.Integer]
    hash: int
    _value: int

    # We use __new__ here to ensure that two Integer's that have the same value
    # return the same object, and to set an object hash value.
    # Consider also @lru_cache, and mechanisms for limiting and
    # clearing the cache and the object store which might be useful in implementing
    # Builtin Share[].
    def __new__(cls, value) -> "Integer":
        n = int(value)
        self = cls._integers.get(value)
        if self is None:
            self = super().__new__(cls)
            self._value = n

            # Cache object so we don't allocate again.
            self._integers[value] = self

            self._sympy = None  # We will lazily initialize sympy

            # Set a value for self.__hash__() once so that every time
            # it is used this is fast. Note that in contrast to the
            # cached object key, the hash key needs to be unique across all
            # Python objects, so we include the class in the
            # event that different objects have the same Python value
            self.hash = hash((cls, n))

        return self

    def __eq__(self, other) -> bool:
        if isinstance(other, Integer):
            return self._value == other._value
        if isinstance(other, Number):
            # If other is a number of a wider class, use
            # its implementation:
            return other.__eq__(self)

        return super().__eq__(other)

    def __ge__(self, other) -> bool:
        return (
            self._value >= other.value
            if isinstance(other, Integer)
            else super().__ge__(other)
        )

    def __gt__(self, other) -> bool:
        return (
            self._value > other.value
            if isinstance(other, Integer)
            else super().__gt__(other)
        )

    # __hash__ is defined so that we can store Number-derived objects
    # in a set or dictionary.
    def __hash__(self):
        return self.hash

    def __le__(self, other) -> bool:
        return (
            self._value <= other.value
            if isinstance(other, Integer)
            else super().__le__(other)
        )

    def __lt__(self, other) -> bool:
        return (
            self._value < other.value
            if isinstance(other, Integer)
            else super().__lt__(other)
        )

    def __ne__(self, other) -> bool:
        return (
            self._value != other.value
            if isinstance(other, Integer)
            else super().__ne__(other)
        )

    def __neg__(self) -> "Integer":
        return Integer(-self._value)

    def abs(self) -> "Integer":
        return -self if self < Integer0 else self

    def atom_to_boxes(self, f, evaluation):
        from mathics.format.box.numberform import numberform_to_boxes

        try:
            return numberform_to_boxes(
                self, None, None, evaluation, {"_Form": f.get_name()}
            )
        except ValueError:
            # from mathics.format.box import int_to_string_shorter_repr
            # return int_to_string_shorter_repr(self._value, form)
            raise

    def do_copy(self) -> "Integer":
        return Integer(self._value)

    @property
    def int_value(self) -> int:
        return self._value

    @property
    def is_zero(self) -> bool:
        # Note: 0 is self._value or the other way around is a syntax
        # error.
        return self._value == 0

    def round(self, d: Optional[int] = None) -> Union["MachineReal", "PrecisionReal"]:
        """Produce a Real approximation rounding value of ``Integer`` with
        decimal precision ``d``.

        If ``d`` is ``None`` we force the mantissa to fit the entire
        integer value, provided it is less than the magical number
        1024. 1024 is a common internal Mathematica implementation limit where
        it switches from using MachineReal to PrecisionReal.

        If a decimal precision ``d`` isn't ``None``, then we convert to
        a PrecisionReal using that value d.

        When ``d`` is ``None`` but the mantissa does not fit into a
        Python float, we implement the value as an mpmath.mpf value.
        """
        if d is None:
            d = self.value.bit_length()
            # Many WMA implementations seem to change behavior of the integer
            # representation that has more than 1024 digits. In theory, this number can vary depending
            # on hardware characteristics.
            if d <= 1024:
                return MachineReal(self.value)
            else:
                d = 16  # MACHINE_PRECISION_VALUE rounded up

        return PrecisionReal(sympy_Float(self.value, d))

    def sameQ(self, rhs) -> bool:
        """Mathics3 SameQ for Integer"""
        return isinstance(rhs, Integer) and self._value == rhs._value

    @property
    def sympy(self) -> sympy_numbers.Integer:
        return self.to_sympy()

    def to_sympy(self, **_) -> sympy_numbers.Integer:
        if self._sympy is None:
            self._sympy = sympy.Integer(self._value)
        return self._sympy

    @cache
    def user_hash(self, update):
        update(b"System`Integer>" + str(self._value).encode("utf8"))


Integer0 = Integer(0)
Integer1 = Integer(1)
Integer2 = Integer(2)
Integer3 = Integer(3)
Integer4 = Integer(4)
Integer310 = Integer(310)
Integer10 = Integer(10)
IntegerM1 = Integer(-1)


# This has to come before Complex, which uses Real.
class Real(Number[T]):
    class_head_name = "System`Real"

    __slots__ = ("_hash_bytes",)

    # __new__ rather than __init__ is used here because the kind of
    # object created differs based on contents of "value".
    def __new__(cls, value, p: Optional[int] = None) -> "Real":
        """
        Return either a MachineReal or a PrecisionReal object.
        Or raise a TypeError.
        p is the number of binary digits of precision.
        """
        if isinstance(value, str):
            if p is None:
                digits = ("".join(re.findall("[0-9]+", value))).lstrip("0")
                if digits == "":  # Handle weird Mathematica zero case
                    p = max(
                        prec(len(value.replace("0.", ""))), FP_MANTISA_BINARY_DIGITS
                    )
                else:
                    p = prec(len(digits.zfill(dps(FP_MANTISA_BINARY_DIGITS))))
        elif isinstance(value, sympy_Float):
            if p is None:
                p = value._prec + 1
        elif isinstance(value, (Integer, sympy.Number, mpmath.mpf, float, int)):
            if p is not None and p > FP_MANTISA_BINARY_DIGITS:
                value = str(value)
        else:
            raise TypeError("Unknown number type: %s (type %s)" % (value, type(value)))

        # return either machine precision or arbitrary precision real
        if p is None or p == FP_MANTISA_BINARY_DIGITS:
            return MachineReal.__new__(MachineReal, value)
        else:
            # TODO: check where p is set in value:
            return PrecisionReal.__new__(PrecisionReal, value)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Number):
            return super().__eq__(other)

        _prec: Optional[int] = min_prec(self, other)
        if _prec is None:
            return self._value == other._value

        with mpmath.workprec(_prec):
            rel_eps = 0.5 ** float(_prec - 7)
            return mpmath.almosteq(
                self.to_mpmath(), other.to_mpmath(), abs_eps=0, rel_eps=rel_eps
            )

    def __hash__(self):
        # ignore last 7 binary digits when hashing
        _prec = dps(self.get_precision())
        return hash(("Real", self.to_sympy().n(_prec)))

    @property
    def is_nan(self) -> bool:
        return isinstance(self.value, sympy.core.numbers.NaN)

    def __ne__(self, other) -> bool:
        # Real is a total order
        return not (self == other)

    def user_hash(self, update) -> None:
        if not hasattr(self, "_hash_bytes"):
            _prec = dps(self.get_precision())
            payload = str(self.to_sympy().n(_prec)).encode("utf8")
            self._hash_bytes = b"System`Real>" + payload

        update(self._hash_bytes)


# This has to come before PrecisionReal, which uses MachineReal.
class MachineReal(Real[float | mpmath.mpf]):
    """
    Machine precision real number.

    Stored internally as a Python float or an mpmath.mpf

    Precision for these numbers is `MachinePrecision`.
    """

    __slots__ = ("hash", "_sympy", "_value")

    # Dictionary of MachineReal constant values defined so far.
    # We use this for object uniqueness.
    # The key is the MachineReal's Python `float` value, and the
    # dictionary's value is the corresponding Mathics3 MachineReal object.
    _machine_reals: dict[Any, "MachineReal"] = {}
    _sympy: Optional[sympy_numbers.Integer]
    hash: int
    _value: float | mpmath.mpf

    def __new__(cls, value) -> "MachineReal":

        if isinstance(value, int):
            d = value.bit_length()

            if d <= FP_MANTISA_BINARY_DIGITS:
                n = float(value)

            else:
                with mpmath.workdps(d):
                    n = mpmath.mpf(value)
        else:
            n = float(value)

        if isinstance(n, float) and math.isinf(n) or math.isnan(n):
            # FIXME: can we do better here using mpmath.mpf?
            raise OverflowError

        self = cls._machine_reals.get(n)
        if self is None:
            self = Number.__new__(cls)

            # Set a value for self.__hash__() once so that every time
            # it is used this is fast. Note that in contrast to the
            # cached object key, the hash key needs to be unique across all
            # Python objects, so we include the class in the
            # event that different objects have the same Python value.
            self.hash = hash((cls, n))

            self._value = n

            # We will lazily initialize _sympy.
            self._sympy = None

            # Cache object so we don't allocate again.
            self._machine_reals[n] = self

        return self

    # __hash__ is defined so that we can store Number-derived objects
    # in a set or dictionary.
    def __hash__(self):
        return self.hash

    def __neg__(self) -> "MachineReal":
        return MachineReal(-self._value)

    def atom_to_boxes(self, f, evaluation):
        from mathics.format.box import numberform_to_boxes

        form = f.get_name()
        _number_form_options["_Form"] = form  # passed to _NumberFormat
        n = 6 if form == "System`OutputForm" else None
        num_str = numberform_to_boxes(self, n, None, evaluation, _number_form_options)
        return num_str

    def do_copy(self) -> "MachineReal":
        return MachineReal(self._value)

    def get_precision(self) -> int:
        """Returns the default specification for precision in N and other numerical functions."""
        return FP_MANTISA_BINARY_DIGITS

    def get_float_value(self, evaluation=None, permit_complex=False) -> float:
        return self._value

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return (
            BASIC_ATOM_NUMBER_ELT_ORDER,
            self._value,
            0,
            1,
            0,  # Machine precision comes first, and after Integers
        )

    @property
    def is_approx_zero(self) -> bool:
        # In WMA, Chop[10.^(-10)] == 0,
        # so, lets take it.
        res = abs(self.value) <= 1e-10
        return res

    def is_machine_precision(self) -> bool:
        return True

    @property
    def is_zero(self) -> bool:
        return self._value == 0.0

    def sameQ(self, rhs) -> bool:
        """Mathics3 SameQ for MachineReal.
        If the rhs comparison value is a MachineReal, the values
        equal _value.

        If the rhs value is a PrecisionReal, though, then
        the two values have to be within 1/2 ** (precision) of
        rhs-value's precision.

        For any other rhs type, sameQ is False.
        """
        if isinstance(rhs, MachineReal):
            return self._value == rhs._value

        if isinstance(rhs, PrecisionReal):
            rhs_value = rhs._value
            value = self.to_sympy()
            if (value - rhs_value).is_zero:
                return True
            diff = abs(value - rhs_value)
            prec = min(value._prec, rhs_value._prec)
            return diff < 0.5 ** (prec)

        return False

    @property
    def sympy(self):
        return self.to_sympy()

    def to_python(self, *_, **__) -> float:
        return self.value

    def to_sympy(self, **_):
        if self._sympy is None:
            self._sympy = sympy.Float(self._value)  # Machine precision float
        return self._sympy


MachineReal0 = MachineReal(0)
MachineReal1 = MachineReal(1)


class PrecisionReal(Real[sympy_Float]):
    """
    Arbitrary-precision floating-point number.

    Stored internally as a sympy.Float.

    Note: Plays nicely with the mpmath.mpf (float) type.
    """

    __slots__ = ("hash", "_sympy", "_value")
    _value: sympy.Float

    # Dictionary of PrecisionReal constant values defined so far.
    # We use this for object uniqueness.
    # The key is the PrecisionReal's `sympy.Float`, and the
    # dictionary's value is the corresponding Mathics3 PrecisionReal object.
    _precision_reals: dict[sympy.Float, "PrecisionReal"] = {}

    # Note: We have no _value attribute or value property .
    # value attribute comes from Number.value

    def __new__(cls, value) -> "PrecisionReal":

        n = sympy.Float(value)
        self = cls._precision_reals.get(n)

        if self is None:
            self = object.__new__(cls)
            self._value = n

            # Cache object so we don't allocate again.
            self._precision_reals[n] = self

            # Set a value for self.__hash__() once so that every time
            # it is used this is fast. Note that in contrast to the
            # cached object key, the hash key needs to be unique across all
            # Python objects, so we include the class in the
            # event that different objects have the same Python value.
            self.hash = hash((cls, n))

        return self

    # __hash__ is defined so that we can store Number-derived objects
    # in a set or dictionary.
    def __hash__(self):
        return self.hash

    def __neg__(self) -> "PrecisionReal":
        return PrecisionReal(-self.value)

    def atom_to_boxes(self, f, evaluation):
        from mathics.format.box import numberform_to_boxes

        form = f.get_name()
        _number_form_options["_Form"] = form  # passed to _NumberFormat
        digits = dps(self.get_precision()) if form == "System`OutputForm" else None
        return numberform_to_boxes(self, digits, None, evaluation, _number_form_options)

    def do_copy(self) -> "PrecisionReal":
        return PrecisionReal(self.value)

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """

        sympy_float = self._value
        value, prec = float(sympy_float), sympy_float._prec
        # For large values, use the sympy.Float value...
        if math.isinf(value):
            return (BASIC_ATOM_NUMBER_ELT_ORDER, sympy_float, 0, 2, prec)

        return (BASIC_ATOM_NUMBER_ELT_ORDER, value, 0, 2, prec)

    def get_precision(self) -> int:
        """Returns the default specification for precision (in binary digits) in N and other numerical functions."""
        return self.value._prec + 1

    @property
    def is_zero(self) -> bool:
        # self.value == 0 does not work for sympy >=1.13
        return self.value.is_zero or False

    def round(self, d: Optional[int] = None) -> Union[MachineReal, "PrecisionReal"]:
        if d is None:
            return MachineReal(float(self.value))
        min_prec = min(prec(d), self.value._prec)
        return PrecisionReal(sympy_Float(self.value, precision=min_prec))

    def sameQ(self, rhs) -> bool:
        """Mathics3 SameQ for PrecisionReal"""
        if isinstance(rhs, PrecisionReal):
            other_value = rhs.value
        elif isinstance(rhs, MachineReal):
            other_value = rhs.to_sympy()
        else:
            return False
        value = self.value

        # Keep math entirely inside SymPy to use its arbitrary precision.
        diff = sympy.Add(value, -other_value)
        if diff.simplify().is_zero:
            return True

        value = self.value
        prec = min(value._prec, other_value._prec)
        diff = abs(value - other_value)
        return diff < 0.5**prec

    @property
    def sympy(self):
        return self._value

    def to_python(self, *_, **__) -> float:
        return float(self._value)

    def to_sympy(self, *_, **__) -> sympy_Float:
        return self._value

    @property
    def value(self) -> sympy_Float:
        return self._value


class Complex(Number[tuple[Number[T], Number[T], Optional[int]]]):
    """Complex wraps two real-valued Numbers.

    Note that Mathics3 complex values are more precise than complex
    values in Python, NumPy, or mpmath. Both the Real and Imaginary
    parts can be Mathics3-kinds of numbers, as opposed to a generic
    floating-point number (which does not distinguish exact from approximate
    values like an integer does). Also, there can be a precision associated
    with a Mathics3 complex number.
    """

    __slots__ = ("_exact_value", "_imag", "_precision", "_real", "_sympy", "_value")

    class_head_name = "System`Complex"
    _real: Number[T]
    _imag: Number[T]

    # Class variable "precision" is a computed value from _real and _image.
    # When it is None, the value is exact.
    _precision: Optional[int]

    # Dictionary of Complex constant values defined so far.
    # We use this for object uniqueness.
    # The key is the Complex value's real and imaginary parts as a tuple,
    # the dictionary's value is the corresponding Mathics3 Complex object.
    _complex_numbers: dict[tuple[Number[T], Number[T], Optional[int]], "Complex"] = {}

    # The precise value: a real number, an imaginary number,
    # and an optional precision value.
    _exact_value: tuple[Number[T], Number[T], Optional[int]]

    hash: int

    # An approximate Python-equivalent number. Often, this is
    # all that is needed.
    _value: complex

    # We use __new__ here to ensure that two Complex number that have
    # down to the type of the imaginary and real parts and the precision of those --
    # the same value return the same object, and to set an object hash
    # value.  Consider also @lru_cache, and mechanisms for limiting
    # and clearing the cache and the object store which might be
    # useful in implementing Builtin Share[].
    def __new__(cls, real, imag):
        if not isinstance(real, (Integer, Real, Rational)):
            raise ValueError(
                f"Argument 'real' must be an Integer, Real, or Rational type; is {real}."
            )
        if imag is SymbolInfinity:
            return SymbolI * SymbolInfinity
        if not isinstance(imag, (Integer, Real, Rational)):
            raise ValueError(
                f"Argument 'image' must be an Integer, Real, or Rational type; is {imag}."
            )

        # Note: for the below test, imag.value == 0 catches more
        # reals.  In particular, MachineReals that have an imaginary
        # value of floating-point 0.0. But MachineReal 0.0 is "approximate 0",
        # not exactly 0. So "Complex[0., 0.]" is "0. + 0." and not "0."
        if imag.sameQ(Integer0):
            return real

        if isinstance(real, MachineReal) and not isinstance(imag, MachineReal):
            imag = imag.round()
            precision = FP_MANTISA_BINARY_DIGITS
        elif isinstance(imag, MachineReal) and not isinstance(real, MachineReal):
            real = real.round()
            precision = FP_MANTISA_BINARY_DIGITS
        else:
            precision = min(
                (u for u in (x.get_precision() for x in (real, imag)) if u is not None),
                default=None,
            )

        exact_value = (real, imag, precision)

        self = cls._complex_numbers.get(exact_value)
        if self is None:
            self = super().__new__(cls)
            self._real = real
            self._imag = imag

            self._exact_value = exact_value
            self._precision = precision
            self._sympy = None  # lazy evaluation for sympy
            self._value = complex(real.value, imag.value)

            # Cache object so we don't allocate again.
            self._complex_numbers[exact_value] = self

            # Set a value for self.__hash__() once so that every time
            # it is used this is fast. Note that in contrast to the
            # cached object key, the hash key needs to be unique across all
            # Python objects, so we include the class in the
            # event that different objects have the same Python value
            self.hash = hash((cls, exact_value))

        return self

    def __eq__(self, other) -> bool:
        if isinstance(other, Complex):
            return self._real.__eq__(other.real) and self._imag.__eq__(other._imag)
        if isinstance(other, Number):
            if abs(self._imag._value) != 0:
                return False
            return self._real.__eq__(other)

        return super().__eq__(other)

    def __getnewargs__(self) -> tuple:
        return (self._real, self._imag)

    def __hash__(self):
        return self.hash

    @property
    def imag(self) -> Number[T]:
        return self._imag

    @property
    def is_approx_zero(self) -> bool:
        real_zero = (
            self._real.is_approx_zero
            if hasattr(self._real, "is_approx_zero")
            else self._real.is_zero
        )
        imag_zero = (
            self._imag.is_approx_zero
            if hasattr(self._imag, "is_approx_zero")
            else self._imag.is_zero
        )
        return bool(real_zero) and bool(imag_zero)

    @property
    def is_zero(self) -> bool:
        return self._real.is_zero and self._imag.is_zero

    @cache
    def __neg__(self):
        return Complex(-self._real, -self._imag)

    @property
    def real(self) -> Number[T]:
        return self._real

    def __str__(self) -> str:
        return str(self.to_sympy())

    def atom_to_boxes(self, f, evaluation):
        from mathics.format.box import format_element

        return format_element(self, evaluation, f)

    def default_format(self, evaluation, form) -> str:
        return "Complex[%s, %s]" % (
            self._real.default_format(evaluation, form),
            self._imag.default_format(evaluation, form),
        )

    def do_copy(self) -> "Complex":
        return Complex(self._real.do_copy(), self._imag.do_copy())

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        order_real, order_imag = self._real.element_order, self._imag.element_order

        # If the real or the imaginary parts are real numbers, sort according
        # the minimum precision.
        # Example:
        # Sort[{1+2I, 1.+2.I, 1.`4+2.`5I, 1.`2+2.`7 I}]
        #
        # = {1+2I, 1.+2.I, 1.`2+2.`7 I, 1.`4+2.`5I}
        return order_real + order_imag

    # FIXME: remove permit_complex and adjust callers.
    def get_float_value(
        self, evaluation=None, permit_complex=False
    ) -> Optional[Union[complex, float]]:
        if self._imag == 0:
            return self._real.get_float_value()
        if permit_complex:
            return self._value
        return None

    def get_precision(self) -> Optional[int]:
        """Returns the default specification for precision in N and other numerical functions.
        When `None` is returned, no precision has been defined, and this object's value is
        exact.

        This function is called by method `is_inexact()`.
        """
        return self._precision

    def is_machine_precision(self) -> bool:
        if self._real.is_machine_precision() or self._imag.is_machine_precision():
            return True
        return False

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        return super().pattern_precedence

    @property
    def precision(self) -> Optional[int]:
        return self._precision

    def round(self, d=None) -> "Complex":
        real = self._real.round(d)
        imag = self._imag.round(d)
        return Complex(real, imag)

    def sameQ(self, rhs) -> bool:
        """Mathics3 SameQ for Complex"""
        return (
            isinstance(rhs, Complex)
            and self._real == rhs._real
            and self._imag == rhs._imag
        )

    @property
    def sympy(self):
        return self.to_sympy()

    def user_hash(self, update) -> None:
        update(b"System`Complex>")
        update(self._real)
        update(self._imag)

    def to_python(self, *args, **kwargs):
        return complex(
            self._real.to_python(*args, **kwargs), self._imag.to_python(*args, **kwargs)
        )

    def to_mpmath(self, precision: Optional[int] = None):
        return mpmath.mpc(
            self._real.to_mpmath(precision), self._imag.to_mpmath(precision)
        )

    def to_sympy(self, **_):
        if self._sympy is None:
            self._sympy = self._real.to_sympy() + sympy.I * self._imag.to_sympy()
        return self._sympy


class Rational(Number[sympy.Rational]):
    class_head_name = "System`Rational"

    __slots__ = "_value"

    # Collection of integers defined so far.
    _rationals: dict[Any, "Rational"] = {}
    hash: int
    _value: Union[
        sympy.Rational, sympy.core.numbers.NaN, sympy.core.numbers.ComplexInfinity
    ]

    # We use __new__ here to ensure that two Rationals's that have the same value
    # return the same object, and to set an object hash value.
    # Consider also @lru_cache, and mechanisms for limiting and
    # clearing the cache and the object store which might be useful in implementing
    # Builtin Share[].
    def __new__(cls, numerator, denominator=1) -> "Rational":
        value = sympy.Rational(numerator, denominator)
        key = (cls, value)
        self = cls._rationals.get(key)

        if self is None:
            self = super().__new__(cls)
            self._value = value

            # Cache object so we don't allocate again.
            self._rationals[key] = self

            # Set a value for self.__hash__() once so that every time
            # it is used this is fast.
            self.hash = hash(key)
        return self

    def __eq__(self, other) -> bool:
        if isinstance(other, Rational):
            return self.value.as_numer_denom() == other.value.as_numer_denom()
        if isinstance(other, Integer):
            return (other._value, 1) == self.value.as_numer_denom()
        if isinstance(other, Number):
            # For general numbers, rely on Real or Complex implementations.
            return other.__eq__(self)
        # General expressions
        return super().__eq__(other)

    def __getnewargs__(self) -> tuple:
        return (self.numerator().value, self.denominator().value)

    # __hash__ is defined so that we can store Number-derived objects
    # in a set or dictionary.
    def __hash__(self):
        return self.hash

    def __neg__(self) -> "Rational":
        return Rational(-self.numerator().value, self.denominator().value)

    def atom_to_boxes(self, f, evaluation):
        from mathics.format.box import format_element

        return format_element(self, evaluation, f)

    @property
    def is_zero(self) -> bool:
        return (
            self.numerator().is_zero
        )  # (implicit) and not (self.denominator().is_zero)

    @cache
    def denominator(self) -> "Integer":
        return Integer(self.value.as_numer_denom()[1])

    def default_format(self, evaluation, form) -> str:
        return "Rational[%s, %s]" % self.value.as_numer_denom()

    def do_copy(self) -> "Rational":
        return Rational(self.value)

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        # HACK: otherwise "Bus error" when comparing 1==1.
        return (
            BASIC_ATOM_NUMBER_ELT_ORDER,
            sympy.Float(self.value),
            1,
            1,
        )

    @cache
    def numerator(self) -> "Integer":
        return Integer(self.value.as_numer_denom()[0])

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        return super().pattern_precedence

    def round(self, d=None) -> Union["MachineReal", "PrecisionReal"]:
        if d is None:
            return MachineReal(float(self.value))
        else:
            return PrecisionReal(self.value.n(d))

    def round_to_float(self, evaluation=None, permit_complex: bool = True) -> float:
        return float(self.value)

    def sameQ(self, rhs) -> bool:
        """Mathics3 SameQ for Rational"""
        return isinstance(rhs, Rational) and self.value == rhs.value

    def to_python(self, *_, **__kwargs) -> float:
        return float(self.value)

    def to_sympy(self, **__):
        return self.value

    def user_hash(self, update) -> None:
        update(
            b"System`Rational>" + ("%s>%s" % self.value.as_numer_denom()).encode("utf8")
        )


RationalOneHalf = Rational(1, 2)
RationalMinusOneHalf = Rational(-1, 2)
MATHICS3_COMPLEX_I: Complex = Complex(Integer0, Integer1)
MATHICS3_COMPLEX_I_NEG: Complex = Complex(Integer0, IntegerM1)

# Numerical constants
# These constants are populated by the `Predefined`
# classes. See `mathics.builtin.numbers.constants`
NUMERICAL_CONSTANTS = {
    Symbol("System`$MaxMachineNumber"): MachineReal(MAX_MACHINE_NUMBER),
    Symbol("System`$MinMachineNumber"): MachineReal(MIN_MACHINE_NUMBER),
}


def get_int_value(element) -> Optional[int]:
    """
    Return the integer value of "element" if it is a data type that could be interpreted as a Python int.

    Otherwise, return None.
    """
    return element.int_value if hasattr(element, "int_value") else None


def is_integer_rational_or_real(expr) -> bool:
    """
    Return True if expr is either an Integer, Rational, or Real.
    """
    return isinstance(expr, (Integer, Rational, Real))
