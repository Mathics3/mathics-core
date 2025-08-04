# cython: language_level=3
# -*- coding: utf-8 -*-

import base64
import math
import re
from typing import Any, Dict, Generic, Optional, Tuple, TypeVar, Union

import mpmath
import sympy
from sympy.core import numbers as sympy_numbers

from mathics.core.element import BoxElementMixin, ImmutableValueMixin
from mathics.core.keycomparable import (
    BASIC_ATOM_NUMBER_SORT_KEY,
    BASIC_ATOM_STRING_OR_BYTEARRAY_SORT_KEY,
)
from mathics.core.number import (
    FP_MANTISA_BINARY_DIGITS,
    MACHINE_PRECISION_VALUE,
    MAX_MACHINE_NUMBER,
    MIN_MACHINE_NUMBER,
    dps,
    min_prec,
    prec,
)
from mathics.core.symbols import (
    Atom,
    NumericOperators,
    Symbol,
    SymbolNull,
    SymbolTrue,
    symbol_set,
)
from mathics.core.systemsymbols import SymbolFullForm, SymbolInfinity, SymbolInputForm

# The below value is an empirical number for comparison precedence
# that seems to work.  We have to be able to match mpmath values with
# sympy values
COMPARE_PREC = 50

SymbolI = Symbol("I")
SymbolString = Symbol("String")

SYSTEM_SYMBOLS_INPUT_OR_FULL_FORM = symbol_set(SymbolInputForm, SymbolFullForm)

T = TypeVar("T")


class Number(Atom, ImmutableValueMixin, NumericOperators, Generic[T]):
    """
    Different kinds of Mathics Numbers, the main built-in subclasses
    being: Integer, Rational, Real, Complex.
    """

    _value: T
    hash: int

    def __getnewargs__(self):
        """
        __getnewargs__ is used in pickle loading to ensure __new__ is
        called with the right value.

        Most of the time a number takes one argument - its value
        When there is a kind of number, like Rational, or Complex,
        that has more than one argument, it should define this method
        accordingly.
        """
        return (self._value,)

    def __eq__(self, other):
        if isinstance(other, Number):
            return self.get_sort_key() == other.get_sort_key()
        else:
            return False

    def __str__(self) -> str:
        return str(self.value)

    def default_format(self, evaluation, form) -> str:
        return str(self.value)

    def do_copy(self) -> "Number":
        raise NotImplementedError

    # FIXME: can we refactor or subclass objects to remove pattern_sort?
    def get_sort_key(self, pattern_sort=False) -> tuple:
        """
        get_sort_key is used in Expression evaluation to determine how to
        order its list of elements. The tuple returned contains
        rank orders for different level as is found in say
        Python version release numberso or Python package version numbers.

        This is the default routine for Number. Subclasses of Number like
        Complex may need to define this differently.
        """
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            return (
                BASIC_ATOM_NUMBER_SORT_KEY,
                self.value,
                0,
                1,
            )

    @property
    def is_literal(self) -> bool:
        """Number can't change and has a Python representation,
        i.e. a value is set and it does not depend on definition
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
        return (
            self._value == other.value
            if isinstance(other, Integer)
            else super().__eq__(other)
        )

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
        return self.make_boxes(f.get_name())

    def get_int_value(self) -> int:
        return self._value

    @property
    def is_zero(self) -> bool:
        # Note: 0 is self._value or the other way around is a syntax
        # error.
        return self._value == 0

    def make_boxes(self, form) -> "String":
        from mathics.eval.makeboxes import _boxed_string

        try:
            if form in ("System`InputForm", "System`FullForm"):
                return _boxed_string(str(self.value), number_as_text=True)

            return String(str(self._value))
        except ValueError:
            # In Python 3.11, the size of the string
            # obtained from an integer is limited, and for longer
            # numbers, this exception is raised.
            # The idea is to represent the number by its
            # more significant digits, the lowest significant digits,
            # and a placeholder saying the number of omitted digits.
            from mathics.eval.makeboxes import int_to_string_shorter_repr

            return int_to_string_shorter_repr(self._value, form)

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
        return isinstance(rhs, Integer) and self._value == rhs.value

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


# This has to come before Complex
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
        if isinstance(other, Real):
            # MMA Docs: "Approximate numbers that differ in their last seven
            # binary digits are considered equal"
            _prec = min_prec(self, other)
            if _prec is not None:
                with mpmath.workprec(_prec):
                    rel_eps = 0.5 ** float(_prec - 7)
                    return mpmath.almosteq(
                        self.to_mpmath(), other.to_mpmath(), abs_eps=0, rel_eps=rel_eps
                    )
        return super().__eq__(other)

    def __hash__(self):
        # ignore last 7 binary digits when hashing
        _prec = dps(self.get_precision())
        return hash(("Real", self.to_sympy().n(_prec)))

    def __ne__(self, other) -> bool:
        # Real is a total order
        return not (self == other)

    def atom_to_boxes(self, f, evaluation):
        return self.make_boxes(f.get_name())

    def is_nan(self, d=None) -> bool:
        return isinstance(self.value, sympy.core.numbers.NaN)

    def user_hash(self, update):
        # ignore last 7 binary digits when hashing
        _prec = dps(self.get_precision())
        update(b"System`Real>" + str(self.to_sympy().n(_prec)).encode("utf8"))


# Has to come before PrecisionReal
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

    def do_copy(self) -> "MachineReal":
        return MachineReal(self._value)

    def get_precision(self) -> int:
        """Returns the default specification for precision in N and other numerical functions."""
        return FP_MANTISA_BINARY_DIGITS

    def get_float_value(self, permit_complex=False) -> float:
        return self.value

    @property
    def is_approx_zero(self) -> bool:
        # In WMA, Chop[10.^(-10)] == 0,
        # so, lets take it.
        res = abs(self.value) <= 1e-10
        return res

    def is_machine_precision(self) -> bool:
        return True

    def make_boxes(self, form):
        from mathics.eval.makeboxes import NumberForm_to_String

        _number_form_options["_Form"] = form  # passed to _NumberFormat
        if form in ("System`InputForm", "System`FullForm"):
            n = None
        else:
            n = 6
        return NumberForm_to_String(self, n, None, None, _number_form_options)

    @property
    def is_zero(self) -> bool:
        return self.value == 0.0

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ for MachineReal.
        If the rhs comparison value is a MachineReal, the values
        have to be equal.  If the rhs value is a PrecisionReal though, then
        the two values have to be within 1/2 ** (precision) of
        rhs-value's precision.  For any rhs type, sameQ is False.
        """
        if isinstance(rhs, MachineReal):
            return self.value == rhs.value
        if isinstance(rhs, PrecisionReal):
            rhs_value = rhs.value
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
    _sympy: Number

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

    def do_copy(self) -> "PrecisionReal":
        return PrecisionReal(self.value)

    def get_precision(self) -> int:
        """Returns the default specification for precision (in binary digits) in N and other numerical functions."""
        return self.value._prec + 1

    @property
    def is_zero(self) -> bool:
        # self.value == 0 does not work for sympy >=1.13
        return self.value.is_zero or False

    def make_boxes(self, form):
        from mathics.eval.makeboxes import NumberForm_to_String

        _number_form_options["_Form"] = form  # passed to _NumberFormat
        return NumberForm_to_String(
            self, dps(self.get_precision()), None, None, _number_form_options
        )

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

    def to_python(self, *args, **kwargs):
        return float(self.value)

    def to_sympy(self, *args, **kwargs):
        return self.value


class ByteArrayAtom(Atom, ImmutableValueMixin):
    value: Union[bytes, bytearray]
    class_head_name = "System`ByteArrayAtom"

    # We use __new__ here to ensure that two ByteArrayAtom's that have the same value
    # return the same object, and to set an object hash value.
    # Consider also @lru_cache, and mechanisms for limiting and
    # clearing the cache and the object store which might be useful in implementing
    # Builtin Share[].
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

        self.hash = hash(("ByteArrayAtom", str(self.value)))
        return self

    def __hash__(self):
        return self.hash

    def __str__(self) -> str:
        return base64.b64encode(self.value).decode("utf8")

    # FIXME: the below does not use the "f" parameter to
    # change behavior between FullForm and OutputForm
    # Below we have the OutputForm behavior.
    # A refactoring should be done so that this routine
    # is removed and the form makes decisions, rather than
    # have this routine know everything about all forms.
    def atom_to_boxes(self, f, evaluation) -> "String":
        res = String(f"<{len(self.value)}>")
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
            return (
                BASIC_ATOM_STRING_OR_BYTEARRAY_SORT_KEY,
                self.value,
                0,
                1,
            )

    @property
    def is_literal(self) -> bool:
        """For an ByteArrayAtom, the value can't change and has a Python representation,
        i.e. a value is set and it does not depend on definition
        bindings. So we say it is a literal.
        """
        return True

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ"""
        # FIX: check
        if isinstance(rhs, ByteArrayAtom):
            return self.value == rhs.value
        return False

    def get_string_value(self) -> Optional[str]:
        try:
            return self.value.decode("utf-8")
        except Exception:
            return None

    def to_sympy(self, **kwargs):
        return None

    def to_python(self, *args, **kwargs) -> Union[bytes, bytearray]:
        return self.value

    def user_hash(self, update):
        # hashing a String is the one case where the user gets the untampered
        # hash value of the string's text. this corresponds to MMA behavior.
        update(self.value)

    def __getnewargs__(self):
        return (self.value,)


class Complex(Number[Tuple[Number[T], Number[T], Optional[int]]]):
    """
    Complex wraps two real-valued Numbers.
    """

    class_head_name = "System`Complex"
    real: Number[T]
    imag: Number[T]

    # Dictionary of Complex constant values defined so far.
    # We use this for object uniqueness.
    # The key is the Complex value's real and imaginary parts as a tuple,
    # dictionary's value is the corresponding Mathics Complex object.
    _complex_numbers: Dict[Any, "Complex"] = {}

    # We use __new__ here to ensure that two Integer's that have the same value
    # return the same object, and to set an object hash value.
    # Consider also @lru_cache, and mechanisms for limiting and
    # clearing the cache and the object store which might be useful in implementing
    # Builtin Share[].
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
            prec = FP_MANTISA_BINARY_DIGITS
        elif isinstance(imag, MachineReal) and not isinstance(real, MachineReal):
            real = real.round()
            prec = FP_MANTISA_BINARY_DIGITS
        else:
            prec = min(
                (u for u in (x.get_precision() for x in (real, imag)) if u is not None),
                default=None,
            )

        value = (real, imag, prec)
        self = cls._complex_numbers.get(value)
        if self is None:
            self = super().__new__(cls)
            self.real = real
            self.imag = imag

            self._value = value

            # Cache object so we don't allocate again.
            self._complex_numbers[value] = self

            # Set a value for self.__hash__() once so that every time
            # it is used this is fast. Note that in contrast to the
            # cached object key, the hash key needs to be unique across all
            # Python objects, so we include the class in the
            # event that different objects have the same Python value
            self.hash = hash((cls, value))

        return self

    def __hash__(self):
        return self.hash

    def __str__(self) -> str:
        return str(self.to_sympy())

    def atom_to_boxes(self, f, evaluation):
        from mathics.eval.makeboxes import format_element

        return format_element(self, evaluation, f)

    def to_sympy(self, **kwargs):
        return self.real.to_sympy() + sympy.I * self.imag.to_sympy()

    def to_python(self, *args, **kwargs):
        return complex(
            self.real.to_python(*args, **kwargs), self.imag.to_python(*args, **kwargs)
        )

    def to_mpmath(self, precision: Optional[int] = None):
        return mpmath.mpc(
            self.real.to_mpmath(precision), self.imag.to_mpmath(precision)
        )

    def default_format(self, evaluation, form) -> str:
        return "Complex[%s, %s]" % (
            self.real.default_format(evaluation, form),
            self.imag.default_format(evaluation, form),
        )

    # Note we can
    def get_sort_key(self, pattern_sort=False) -> tuple:
        """
        get_sort_key is used in Expression evaluation to determine how to
        order its list of elements. The tuple returned contains
        rank orders for different level as is found in say
        Python version release numberso or Python package version numbers.
        """
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            return (
                BASIC_ATOM_NUMBER_SORT_KEY,
                self.real.get_sort_key(False)[1],
                self.imag.get_sort_key(False)[1],
                1,
            )

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ"""
        return (
            isinstance(rhs, Complex) and self.real == rhs.real and self.imag == rhs.imag
        )

    def round(self, d=None) -> "Complex":
        real = self.real.round(d)
        imag = self.imag.round(d)
        return Complex(real, imag)

    def is_machine_precision(self) -> bool:
        if self.real.is_machine_precision() or self.imag.is_machine_precision():
            return True
        return False

    # FIXME: funny name get_float_value returns complex?
    def get_float_value(self, permit_complex=False) -> Optional[complex]:
        if permit_complex:
            real = self.real.get_float_value()
            imag = self.imag.get_float_value()
            if real is not None and imag is not None:
                return complex(real, imag)
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

    def do_copy(self) -> "Complex":
        return Complex(self.real.do_copy(), self.imag.do_copy())

    def user_hash(self, update) -> None:
        update(b"System`Complex>")
        update(self.real)
        update(self.imag)

    def __eq__(self, other) -> bool:
        if isinstance(other, Complex):
            return self.real == other.real and self.imag == other.imag
        else:
            return super().__eq__(other)

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


class Rational(Number[sympy.Rational]):
    class_head_name = "System`Rational"

    # Collection of integers defined so far.
    _rationals: Dict[Any, "Rational"] = {}

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

    # __hash__ is defined so that we can store Number-derived objects
    # in a set or dictionary.
    def __hash__(self):
        return self.hash

    def atom_to_boxes(self, f, evaluation):
        from mathics.eval.makeboxes import format_element

        return format_element(self, evaluation, f)

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
            return (
                BASIC_ATOM_NUMBER_SORT_KEY,
                sympy.Float(self.value),
                0,
                1,
            )

    def do_copy(self) -> "Rational":
        return Rational(self.value)

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
RationalMinusOneHalf = Rational(-1, 2)
MATHICS3_COMPLEX_I: Complex[int] = Complex(Integer0, Integer1)
MATHICS3_COMPLEX_I_NEG: Complex[int] = Complex(Integer0, IntegerM1)

# Numerical constants
# These constants are populated by the `Predefined`
# classes. See `mathics.builtin.numbers.constants`
NUMERICAL_CONSTANTS = {
    Symbol("System`$MaxMachineNumber"): MachineReal(MAX_MACHINE_NUMBER),
    Symbol("System`$MinMachineNumber"): MachineReal(MIN_MACHINE_NUMBER),
}


class String(Atom, BoxElementMixin):
    value: str
    class_head_name = "System`String"

    def __new__(cls, value):
        self = super().__new__(cls)
        self.value = str(value)
        # Set a value for self.__hash__() once so that every time
        # it is used this is fast.
        self.hash = hash(("String", self.value))
        return self

    def __hash__(self):
        return self.hash

    def __str__(self) -> str:
        return '"%s"' % self.value

    def atom_to_boxes(self, f, evaluation):
        from mathics.eval.makeboxes import _boxed_string

        inner = str(self.value)
        if f in SYSTEM_SYMBOLS_INPUT_OR_FULL_FORM:
            inner = '"' + inner.replace("\\", "\\\\") + '"'
            return _boxed_string(inner, **{"System`ShowStringCharacters": SymbolTrue})
        return String('"' + inner + '"')

    def do_copy(self) -> "String":
        return String(self.value)

    def default_format(self, evaluation, form) -> str:
        value = self.value.replace("\\", "\\\\").replace('"', '\\"')
        return '"%s"' % value

    def get_sort_key(self, pattern_sort=False) -> tuple:
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            return (
                BASIC_ATOM_STRING_OR_BYTEARRAY_SORT_KEY,
                self.value,
                0,
                1,
            )

    def get_string_value(self) -> str:
        return self.value

    @property
    def is_literal(self) -> bool:
        """For a String, the value can't change and has a Python representation,
        i.e. a value is set and it does not depend on definition
        bindings. So we say it is a literal.
        """
        return True

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ"""
        return isinstance(rhs, String) and self.value == rhs.value

    def to_expression(self):
        return self

    def to_sympy(self, **kwargs):
        return None

    def to_python(self, *args, **kwargs) -> str:
        if kwargs.get("string_quotes", True):
            return '"%s"' % self.value  # add quotes to distinguish from Symbols
        else:
            return self.value

    def user_hash(self, update):
        # hashing a String is the one case where the user gets the untampered
        # hash value of the string's text. this corresponds to MMA behavior.
        update(self.value.encode("utf8"))

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


def is_integer_rational_or_real(expr) -> bool:
    """
    Return True  is expr is either an Integer, Rational, or Real.
    """
    return isinstance(expr, (Integer, Rational, Real))
