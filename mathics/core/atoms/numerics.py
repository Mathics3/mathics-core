"""
Numeric types: Number, Integer Real, MachineReal, PrecisionReal, Complex, Rational
"""
# Note: Python warns of ambiguity numpy's module numpy.numerics if we name this file this numeric.py

import math
import re
from functools import cache
from typing import Any, Dict, Generic, Optional, Tuple, TypeVar, Union

import mpmath
import sympy
from sympy.core import numbers as sympy_numbers

from mathics.core.atoms.strings import String
from mathics.core.element import ImmutableValueMixin
from mathics.core.keycomparable import BASIC_ATOM_NUMBER_ELT_ORDER
from mathics.core.number import (
    FP_MANTISA_BINARY_DIGITS,
    MACHINE_PRECISION_VALUE,
    MAX_MACHINE_NUMBER,
    MIN_MACHINE_NUMBER,
    dps,
    min_prec,
    prec,
)
from mathics.core.symbols import Atom, NumericOperators, Symbol, SymbolNull, symbol_set
from mathics.core.systemsymbols import SymbolFullForm, SymbolInfinity, SymbolInputForm

# The below value is an empirical number for comparison precedence
# that seems to work.  We have to be able to match mpmath values with
# sympy values
COMPARE_PREC = 50

SymbolI = Symbol("I")

SYSTEM_SYMBOLS_INPUT_OR_FULL_FORM = symbol_set(SymbolInputForm, SymbolFullForm)

T = TypeVar("T")


class Number(Atom, ImmutableValueMixin, NumericOperators, Generic[T]):
    """
    Different kinds of Mathics Numbers, the main built-in subclasses
    being: Integer, Rational, Real, Complex.
    """

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

        Most of the time a number takes one argument - its value
        When there is a kind of number, like Rational, or Complex,
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

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        return super().pattern_precedence

    @property
    def is_literal(self) -> bool:
        """Number can't change and has a Python representation,
        i.e., a value is set and it does not depend on definition
        bindings. So we say it is a literal.
        """
        return True

    def is_numeric(self, evaluation=None) -> bool:
        # Anything that is in a number class is Numeric, so return True.
        return True

    def to_mpmath(self, precision: Optional[int] = None) -> mpmath.ctx_mp_python.mpf:
        """
        Convert self.value to an mpmath number with precision ``precision``
        If ``precision`` is None, use mpmath's default precision.

        A mpmath number is the default implementation for Number.
        There are kinds of numbers, like Rational, or Complex, that
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

    def round(self, d: Optional[int] = None) -> "Number":
        """
        Produce a Real approximation of ``self`` with decimal precision ``d``.
        """
        return self

    @property
    def value(self) -> T:
        """Equivalent value in either SymPy's or Python's native
        datatype if that exist. Note the SymPy value
        and the Python value might be the same thing.
        """
        return self._value


def _ExponentFunction(value):
    n = value.get_int_value()
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
    class_head_name = "System`Integer"

    # Dictionary of Integer constant values defined so far.
    # We use this for object uniqueness.
    # The key is the Integer's Python `int` value, and the
    # dictionary's value is the corresponding Mathics Integer object.
    _integers: Dict[Any, "Integer"] = {}
    _value: int

    _sympy: sympy_numbers.Integer

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
            self._sympy = sympy_numbers.Integer(value)

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

    def get_int_value(self) -> int:
        return self._value

    def get_float_value(self, permit_complex=False) -> float:
        return float(self._value)

    @property
    def is_zero(self) -> bool:
        # Note: 0 is self._value or the other way around is a syntax
        # error.
        return self._value == 0

    def round(self, d: Optional[int] = None) -> Union["MachineReal", "PrecisionReal"]:
        """
        Produce a Real approximation of ``self`` with decimal precision ``d``.
        If ``d`` is  ``None``, and self.value fits in a float,
        returns a ``MachineReal`` number.
        Is the low-level equivalent to ``N[self, d]``.
        """
        if d is None:
            d = self.value.bit_length()
            if d <= FP_MANTISA_BINARY_DIGITS:
                return MachineReal(float(self.value))
            else:
                d = MACHINE_PRECISION_VALUE
        return PrecisionReal(sympy.Float(self.value, d))

    @property
    def sympy(self) -> sympy_numbers.Integer:
        return self._sympy

    def to_sympy(self, **_) -> sympy_numbers.Integer:
        return self.sympy

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ"""
        return isinstance(rhs, Integer) and self._value == rhs._value

    def do_copy(self) -> "Integer":
        return Integer(self._value)

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


# This has to come before Complex which uses Real.
class Real(Number[T]):
    class_head_name = "System`Real"

    # __new__ rather than __init__ is used here because the kind of
    # object created differs based on contents of "value".
    def __new__(cls, value, p: Optional[int] = None) -> "Real":
        """
        Return either a MachineReal or a PrecisionReal object.
        Or raise a TypeError.
        p is the number of binary digits of precision.
        """
        if isinstance(value, str):
            value = str(value)
            if p is None:
                digits = ("".join(re.findall("[0-9]+", value))).lstrip("0")
                if digits == "":  # Handle weird Mathematica zero case
                    p = max(
                        prec(len(value.replace("0.", ""))), FP_MANTISA_BINARY_DIGITS
                    )
                else:
                    p = prec(len(digits.zfill(dps(FP_MANTISA_BINARY_DIGITS))))
        elif isinstance(value, sympy.Float):
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

    def __ne__(self, other) -> bool:
        # Real is a total order
        return not (self == other)

    def is_nan(self, d=None) -> bool:
        return isinstance(self.value, sympy.core.numbers.NaN)

    def user_hash(self, update):
        # ignore last 7 binary digits when hashing
        _prec = dps(self.get_precision())
        update(b"System`Real>" + str(self.to_sympy().n(_prec)).encode("utf8"))


# This has to come before PrecisionReal which uses MachineReal.
class MachineReal(Real[float]):
    """
    Machine precision real number.

    Stored internally as a python float.
    """

    # Dictionary of MachineReal constant values defined so far.
    # We use this for object uniqueness.
    # The key is the MachineReal's Python `float` value, and the
    # dictionary's value is the corresponding Mathics MachineReal object.
    _machine_reals: Dict[Any, "MachineReal"] = {}
    _value: float

    def __new__(cls, value) -> "MachineReal":
        n = float(value)
        if math.isinf(n) or math.isnan(n):
            raise OverflowError

        self = cls._machine_reals.get(n)
        if self is None:
            self = Number.__new__(cls)
            self._value = n

            # Cache object so we don't allocate again.
            self._machine_reals[n] = self

            # Set a value for self.__hash__() once so that every time
            # it is used this is fast. Note that in contrast to the
            # cached object key, the hash key needs to be unique across all
            # Python objects, so we include the class in the
            # event that different objects have the same Python value
            self.hash = hash((cls, n))

        return self

    # __hash__ is defined so that we can store Number-derived objects
    # in a set or dictionary.
    def __hash__(self):
        return self.hash

    def __neg__(self) -> "MachineReal":
        return MachineReal(-self.value)

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

    def get_float_value(self, permit_complex=False) -> float:
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
        """Mathics SameQ for MachineReal.
        If the rhs comparison value is a MachineReal, the values
        have to be equal.  If the rhs value is a PrecisionReal though, then
        the two values have to be within 1/2 ** (precision) of
        rhs-value's precision.  For any rhs type, sameQ is False.
        """
        if isinstance(rhs, MachineReal):
            return self._value == rhs._value
        if isinstance(rhs, PrecisionReal):
            rhs_value = rhs._value
            value = self.to_sympy()
            # If sympy fixes the issue, this comparison would be
            # enough
            if (value - rhs_value).is_zero:
                return True
            # this handles the issue...
            diff = abs(value - rhs_value)
            prec = min(value._prec, rhs_value._prec)
            return diff < 0.5 ** (prec)
        else:
            return False

    def to_python(self, *args, **kwargs) -> float:
        return self.value

    def to_sympy(self, *args, **kwargs):
        return sympy.Float(self.value)


MachineReal0 = MachineReal(0)
MachineReal1 = MachineReal(1)


class PrecisionReal(Real[sympy.Float]):
    """
    Arbitrary precision real number.

    Stored internally as a sympy.Float.

    Note: Plays nicely with the mpmath.mpf (float) type.
    """

    # Dictionary of PrecisionReal constant values defined so far.
    # We use this for object uniqueness.
    # The key is the PrecisionReal's sympy.Float, and the
    # dictionary's value is the corresponding Mathics PrecisionReal object.
    _precision_reals: Dict[Any, "PrecisionReal"] = {}
    _sympy: sympy.Float

    # Note: We have no _value attribute or value property .
    # value attribute comes from Number.value

    def __new__(cls, value) -> "PrecisionReal":
        n = sympy.Float(value)
        self = cls._precision_reals.get(n)
        if self is None:
            self = Number.__new__(cls)
            self._sympy = self._value = n

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

    def get_precision(self) -> int:
        """Returns the default specification for precision (in binary digits) in N and other numerical functions."""
        return self.value._prec + 1

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

    @property
    def is_zero(self) -> bool:
        # self.value == 0 does not work for sympy >=1.13
        return self.value.is_zero or False

    def round(self, d: Optional[int] = None) -> Union[MachineReal, "PrecisionReal"]:
        if d is None:
            return MachineReal(float(self.value))
        _prec = min(prec(d), self.value._prec)
        return PrecisionReal(sympy.Float(self.value, precision=_prec))

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ for PrecisionReal"""
        if isinstance(rhs, PrecisionReal):
            other_value = rhs.value
        elif isinstance(rhs, MachineReal):
            other_value = rhs.to_sympy()
        else:
            return False
        value = self.value
        # If sympy would handle properly
        # the precision, this wold be enough
        if (value - other_value).is_zero:
            return True
        # in the meantime, let's use this comparison.
        value = self.value
        prec = min(value._prec, other_value._prec)
        diff = abs(value - other_value)
        return diff < 0.5**prec

    def to_python(self, *args, **kwargs) -> float:
        return float(self.value)

    def to_sympy(self, *args, **kwargs) -> sympy.Float:
        return self.value


class Complex(Number[Tuple[Number[T], Number[T], Optional[int]]]):
    """Complex wraps two real-valued Numbers.

    Note that Mathics3 complex values are more precise than complex
    values in Python, NumPy, or mpmath. Both the Real and Imaginary
    parts can be Mathics3-kinds of numbers, as opposed to a generic
    floating point number (which does not distinguish exact from approximate
    values like an integer does). Also, there can be a precision associated
    with a Mathics3 complex number.
    """

    class_head_name = "System`Complex"
    real: Number[T]
    imag: Number[T]
    precision: Optional[int]

    # Dictionary of Complex constant values defined so far.
    # We use this for object uniqueness.
    # The key is the Complex value's real and imaginary parts as a tuple,
    # dictionary's value is the corresponding Mathics Complex object.
    _complex_numbers: Dict[Any, "Complex"] = {}

    # The precise value: a real number, an imaginary number, and a
    # precision value.
    _exact_value: Tuple[Number[T], Number[T], Optional[int]]

    # An approximate Python-equivalent number. Often, this is
    # all that is needed.
    _value: complex

    # We use __new__ here to ensure that two Complex number that have
    # down to the type on the imaginary and real parts and precision of those --
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
        # value of floating point 0.0. But MachineReal 0.0 is "approximate 0",
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
            self.real = real
            self.imag = imag
            self.precision = precision

            self._exact_value = exact_value
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
            return self.real.__eq__(other.real) and self.imag.__eq__(other.imag)
        if isinstance(other, Number):
            if abs(self.imag._value) != 0:
                return False
            return self.real.__eq__(other)

        return super().__eq__(other)

    def __getnewargs__(self) -> tuple:
        return (self.real, self.imag)

    def __hash__(self):
        return self.hash

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

    @property
    def is_zero(self) -> bool:
        return self.real.is_zero and self.imag.is_zero

    @cache
    def __neg__(self):
        return Complex(-self.real, -self.imag)

    def __str__(self) -> str:
        return str(self.to_sympy())

    def atom_to_boxes(self, f, evaluation):
        from mathics.format.box import format_element

        return format_element(self, evaluation, f)

    def default_format(self, evaluation, form) -> str:
        return "Complex[%s, %s]" % (
            self.real.default_format(evaluation, form),
            self.imag.default_format(evaluation, form),
        )

    def do_copy(self) -> "Complex":
        return Complex(self.real.do_copy(), self.imag.do_copy())

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        order_real, order_imag = self.real.element_order, self.imag.element_order

        # If the real of the imag parts are real numbers, sort according
        # the minimum precision.
        # Example:
        # Sort[{1+2I, 1.+2.I, 1.`4+2.`5I, 1.`2+2.`7 I}]
        #
        # = {1+2I, 1.+2.I, 1.`2+2.`7 I, 1.`4+2.`5I}
        return order_real + order_imag

    def get_float_value(self, permit_complex=False) -> Optional[Union[complex, float]]:
        if self.imag == 0:
            return self.real.get_float_value()
        if permit_complex:
            return self._value
        return None

    def get_precision(self) -> Optional[int]:
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

    def is_machine_precision(self) -> bool:
        if self.real.is_machine_precision() or self.imag.is_machine_precision():
            return True
        return False

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        return super().pattern_precedence

    def round(self, d=None) -> "Complex":
        real = self.real.round(d)
        imag = self.imag.round(d)
        return Complex(real, imag)

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ"""
        return (
            isinstance(rhs, Complex) and self.real == rhs.real and self.imag == rhs.imag
        )

    def user_hash(self, update) -> None:
        update(b"System`Complex>")
        update(self.real)
        update(self.imag)

    def to_python(self, *args, **kwargs):
        return complex(
            self.real.to_python(*args, **kwargs), self.imag.to_python(*args, **kwargs)
        )

    def to_mpmath(self, precision: Optional[int] = None):
        return mpmath.mpc(
            self.real.to_mpmath(precision), self.imag.to_mpmath(precision)
        )

    def to_sympy(self, **kwargs):
        return self.real.to_sympy() + sympy.I * self.imag.to_sympy()


class Rational(Number[sympy.Rational]):
    class_head_name = "System`Rational"

    # Collection of integers defined so far.
    _rationals: Dict[Any, "Rational"] = {}
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

    def to_sympy(self, **kwargs):
        return self.value

    def to_python(self, *args, **kwargs) -> float:
        return float(self.value)

    def round(self, d=None) -> Union["MachineReal", "PrecisionReal"]:
        if d is None:
            return MachineReal(float(self.value))
        else:
            return PrecisionReal(self.value.n(d))

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ"""
        return isinstance(rhs, Rational) and self.value == rhs.value

    @cache
    def numerator(self) -> "Integer":
        return Integer(self.value.as_numer_denom()[0])

    @cache
    def denominator(self) -> "Integer":
        return Integer(self.value.as_numer_denom()[1])

    def default_format(self, evaluation, form) -> str:
        return "Rational[%s, %s]" % self.value.as_numer_denom()

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

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        return super().pattern_precedence

    def do_copy(self) -> "Rational":
        return Rational(self.value)

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


def is_integer_rational_or_real(expr) -> bool:
    """
    Return True  is expr is either an Integer, Rational, or Real.
    """
    return isinstance(expr, (Integer, Rational, Real))
