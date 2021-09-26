# cython: language_level=3
# -*- coding: utf-8 -*-

import sympy
import mpmath
import math
import re

import typing
from typing import Any
from functools import lru_cache

from mathics.core.formatter import encode_mathml, encode_tex, extra_operators
from mathics.core.symbols import (
    Atom,
    BaseExpression,
    Symbol,
    system_symbols,
    fully_qualified_symbol_name,
)
from mathics.core.systemsymbols import (
    SymbolTrue,
    SymbolFalse,
    SymbolNull,
    SymbolList,
    SymbolByteArray,
)
from mathics.core.numbers import dps, get_type, prec, min_prec, machine_precision
import base64

# Imperical number that seems to work.
# We have to be able to match mpmath values with sympy values
COMPARE_PREC = 50


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


class Number(Atom):
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
    from mathics.core.expression import Expression

    if exp.get_string_value():
        if options["_Form"] in (
            "System`InputForm",
            "System`OutputForm",
            "System`FullForm",
        ):
            return Expression("RowBox", Expression(SymbolList, man, String("*^"), exp))
        else:
            return Expression(
                "RowBox",
                Expression(
                    "List",
                    man,
                    String(options["NumberMultiplier"]),
                    Expression("SuperscriptBox", base, exp),
                ),
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

    def __new__(cls, value) -> "Integer":
        n = int(value)
        self = super(Integer, cls).__new__(cls)
        self.value = n
        return self

    @lru_cache()
    def __init__(self, value) -> "Integer":
        super().__init__()

    def boxes_to_text(self, **options) -> str:
        return str(self.value)

    def boxes_to_mathml(self, **options) -> str:
        return self.make_boxes("MathMLForm").boxes_to_mathml(**options)

    def boxes_to_tex(self, **options) -> str:
        return str(self.value)

    def make_boxes(self, form) -> "String":
        return String(str(self.value))

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
            return MachineReal(float(self.value))
        else:
            return PrecisionReal(sympy.Float(self.value, d))

    def get_int_value(self) -> int:
        return self.value

    def sameQ(self, other) -> bool:
        """Mathics SameQ"""
        return isinstance(other, Integer) and self.value == other.value

    def evaluate(self, evaluation):
        evaluation.check_stopped()
        return self

    def get_sort_key(self, pattern_sort=False):
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            return [0, 0, self.value, 0, 1]

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


class Rational(Number):
    @lru_cache()
    def __new__(cls, numerator, denominator=1) -> "Rational":
        self = super().__new__(cls)
        self.value = sympy.Rational(numerator, denominator)
        return self

    def atom_to_boxes(self, f, evaluation):
        return self.format(evaluation, f.get_name())

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

    def do_format(self, evaluation, form) -> "Expression":
        from mathics.core.expression import Expression

        assert fully_qualified_symbol_name(form)
        if form == "System`FullForm":
            return Expression(
                Expression("HoldForm", Symbol("Rational")),
                self.numerator(),
                self.denominator(),
            ).do_format(evaluation, form)
        else:
            numerator = self.numerator()
            minus = numerator.value < 0
            if minus:
                numerator = Integer(-numerator.value)
            result = Expression("Divide", numerator, self.denominator())
            if minus:
                result = Expression("Minus", result)
            result = Expression("HoldForm", result)
            return result.do_format(evaluation, form)

    def default_format(self, evaluation, form) -> str:
        return "Rational[%s, %s]" % self.value.as_numer_denom()

    def evaluate(self, evaluation) -> "Rational":
        evaluation.check_stopped()
        return self

    def get_sort_key(self, pattern_sort=False):
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            # HACK: otherwise "Bus error" when comparing 1==1.
            return [0, 0, sympy.Float(self.value), 0, 1]

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
    def __new__(cls, value, p=None) -> "Real":
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

    def boxes_to_text(self, **options) -> str:
        return self.make_boxes("System`OutputForm").boxes_to_text(**options)

    def boxes_to_mathml(self, **options) -> str:
        return self.make_boxes("System`MathMLForm").boxes_to_mathml(**options)

    def boxes_to_tex(self, **options) -> str:
        return self.make_boxes("System`TeXForm").boxes_to_tex(**options)

    def atom_to_boxes(self, f, evaluation):
        return self.make_boxes(f.get_name())

    def evaluate(self, evaluation) -> "Real":
        evaluation.check_stopped()
        return self

    def get_sort_key(self, pattern_sort=False):
        if pattern_sort:
            return super().get_sort_key(True)
        return [0, 0, self.value, 0, 1]

    def is_nan(self, d=None) -> bool:
        return isinstance(self.value, sympy.core.numbers.NaN)

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

    def __hash__(self):
        # ignore last 7 binary digits when hashing
        _prec = self.get_precision()
        return hash(("Real", self.to_sympy().n(dps(_prec))))

    def user_hash(self, update):
        # ignore last 7 binary digits when hashing
        _prec = self.get_precision()
        update(b"System`Real>" + str(self.to_sympy().n(dps(_prec))).encode("utf8"))

    def get_atom_name(self) -> str:
        return "Real"


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
        """Mathics SameQ"""
        if isinstance(other, MachineReal):
            return self.value == other.value
        elif isinstance(other, PrecisionReal):
            return self.to_sympy() == other.value
        return False

    def is_machine_precision(self) -> bool:
        return True

    def get_precision(self) -> int:
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
        """Mathics SameQ"""
        if isinstance(other, PrecisionReal):
            return self.value == other.value
        elif isinstance(other, MachineReal):
            return self.value == other.to_sympy()
        return False

    def get_precision(self) -> int:
        return self.value._prec + 1

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

    real: Any
    imag: Any

    def __new__(cls, real, imag):
        self = super().__new__(cls)
        if isinstance(real, Complex) or not isinstance(real, Number):
            raise ValueError("Argument 'real' must be a real number.")
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
        return self.format(evaluation, f.get_name())

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

    def do_format(self, evaluation, form) -> "Expression":
        from mathics.core.expression import Expression

        if form == "System`FullForm":
            return Expression(
                Expression("HoldForm", Symbol("Complex")), self.real, self.imag
            ).do_format(evaluation, form)

        parts: typing.List[Any] = []
        if self.is_machine_precision() or not self.real.is_zero:
            parts.append(self.real)
        if self.imag.sameQ(Integer(1)):
            parts.append(Symbol("I"))
        else:
            parts.append(Expression("Times", self.imag, Symbol("I")))

        if len(parts) == 1:
            result = parts[0]
        else:
            result = Expression("Plus", *parts)

        return Expression("HoldForm", result).do_format(evaluation, form)

    def default_format(self, evaluation, form) -> str:
        return "Complex[%s, %s]" % (
            self.real.default_format(evaluation, form),
            self.imag.default_format(evaluation, form),
        )

    def get_sort_key(self, pattern_sort=False):
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            return [0, 0, self.real.get_sort_key()[2], self.imag.get_sort_key()[2], 1]

    def sameQ(self, other) -> bool:
        """Mathics SameQ"""
        return (
            isinstance(other, Complex)
            and self.real == other.real
            and self.imag == other.imag
        )

    def evaluate(self, evaluation) -> "Complex":
        evaluation.check_stopped()
        return self

    def round(self, d=None) -> "Complex":
        real = self.real.round(d)
        imag = self.imag.round(d)
        return Complex(real, imag)

    def is_machine_precision(self) -> bool:
        if self.real.is_machine_precision() or self.imag.is_machine_precision():
            return True
        return False

    def get_float_value(self, permit_complex=False) -> typing.Optional[complex]:
        if permit_complex:
            real = self.real.get_float_value()
            imag = self.imag.get_float_value()
            if real is not None and imag is not None:
                return complex(real, imag)
        else:
            return None

    def get_precision(self) -> typing.Optional[int]:
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


class String(Atom):
    value: str

    def __new__(cls, value):
        self = super().__new__(cls)
        self.value = str(value)
        return self

    def __str__(self) -> str:
        return '"%s"' % self.value

    def boxes_to_text(self, show_string_characters=False, **options) -> str:
        value = self.value

        if (
            not show_string_characters
            and value.startswith('"')  # nopep8
            and value.endswith('"')
        ):
            value = value[1:-1]

        return value

    def boxes_to_mathml(self, show_string_characters=False, **options) -> str:
        from mathics.core.parser import is_symbol_name
        from mathics.builtin import builtins_by_module

        operators = set()
        for modname, builtins in builtins_by_module.items():
            for builtin in builtins:
                # name = builtin.get_name()
                operator = builtin.get_operator_display()
                if operator is not None:
                    operators.add(operator)

        text = self.value

        def render(format, string):
            encoded_text = encode_mathml(string)
            return format % encoded_text

        if text.startswith('"') and text.endswith('"'):
            if show_string_characters:
                return render("<ms>%s</ms>", text[1:-1])
            else:
                outtext = ""
                for line in text[1:-1].split("\n"):
                    outtext += render("<mtext>%s</mtext>", line)
                return outtext
        elif text and ("0" <= text[0] <= "9" or text[0] == "."):
            return render("<mn>%s</mn>", text)
        else:
            if text in operators or text in extra_operators:
                if text == "\u2146":
                    return render(
                        '<mo form="prefix" lspace="0.2em" rspace="0">%s</mo>', text
                    )
                if text == "\u2062":
                    return render(
                        '<mo form="prefix" lspace="0" rspace="0.2em">%s</mo>', text
                    )
                return render("<mo>%s</mo>", text)
            elif is_symbol_name(text):
                return render("<mi>%s</mi>", text)
            else:
                outtext = ""
                for line in text.split("\n"):
                    outtext += render("<mtext>%s</mtext>", line)
                return outtext

    def boxes_to_tex(self, show_string_characters=False, **options) -> str:
        from mathics.builtin import builtins_by_module

        operators = set()

        for modname, builtins in builtins_by_module.items():
            for builtin in builtins:
                operator = builtin.get_operator_display()
                if operator is not None:
                    operators.add(operator)

        text = self.value

        def render(format, string, in_text=False):
            return format % encode_tex(string, in_text)

        if text.startswith('"') and text.endswith('"'):
            if show_string_characters:
                return render(r'\text{"%s"}', text[1:-1], in_text=True)
            else:
                return render(r"\text{%s}", text[1:-1], in_text=True)
        elif text and text[0] in "0123456789-.":
            return render("%s", text)
        else:
            # FIXME: this should be done in a better way.
            if text == "\u2032":
                return "'"
            elif text == "\u2032\u2032":
                return "''"
            elif text == "\u2062":
                return " "
            elif text == "\u221e":
                return r"\infty "
            elif text == "\u00d7":
                return r"\times "
            elif text in ("(", "[", "{"):
                return render(r"\left%s", text)
            elif text in (")", "]", "}"):
                return render(r"\right%s", text)
            elif text == "\u301a":
                return r"\left[\left["
            elif text == "\u301b":
                return r"\right]\right]"
            elif text == "," or text == ", ":
                return text
            elif text == "\u222b":
                return r"\int"
            # Tolerate WL or Unicode DifferentialD
            elif text in ("\u2146", "\U0001D451"):
                return r"\, d"
            elif text == "\u2211":
                return r"\sum"
            elif text == "\u220f":
                return r"\prod"
            elif len(text) > 1:
                return render(r"\text{%s}", text, in_text=True)
            else:
                return render("%s", text)

    def atom_to_boxes(self, f, evaluation):
        inner = str(self.value)

        if f.get_name() in system_symbols("InputForm", "FullForm"):
            inner = inner.replace("\\", "\\\\")

        return String('"' + inner + '"')

    def do_copy(self) -> "String":
        return String(self.value)

    def default_format(self, evaluation, form) -> str:
        value = self.value.replace("\\", "\\\\").replace('"', '\\"')
        return '"%s"' % value

    def get_sort_key(self, pattern_sort=False):
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            return [0, 1, self.value, 0, 1]

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


class ByteArrayAtom(Atom):
    value: str

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

    def boxes_to_text(self, **options) -> str:
        return '"' + self.__str__() + '"'

    def boxes_to_mathml(self, **options) -> str:
        return encode_mathml(String('"' + self.__str__() + '"'))

    def boxes_to_tex(self, **options) -> str:
        return encode_tex(String('"' + self.__str__() + '"'))

    def atom_to_boxes(self, f, evaluation):
        res = String('""' + self.__str__() + '""')
        return res

    def do_copy(self) -> "ByteArrayAtom":
        return ByteArrayAtom(self.value)

    def default_format(self, evaluation, form) -> str:
        value = self.value
        return '"' + value.__str__() + '"'

    def get_sort_key(self, pattern_sort=False):
        if pattern_sort:
            return super().get_sort_key(True)
        else:
            return [0, 1, self.value, 0, 1]

    def sameQ(self, other) -> bool:
        """Mathics SameQ"""
        # FIX: check
        if isinstance(other, ByteArrayAtom):
            return self.value == other.value
        return False

    def get_string_value(self) -> str:
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


def from_python(arg):
    """Converts a Python expression into a Mathics expression.

    TODO: I think there are number of subtleties to be explained here.
    In particular, the expression might beeen the result of evaluation
    a sympy expression which contains sympy symbols.

    If the end result is to go back into Mathics for further
    evaluation, then probably no problem.  However if the end result
    is produce say a Python string, then at a minimum we may want to
    convert backtick (context) symbols into some Python identifier
    symbol like underscore.
    """
    from mathics.builtin.base import BoxConstruct
    from mathics.core.expression import Expression

    number_type = get_type(arg)
    if arg is None:
        return SymbolNull
    if isinstance(arg, bool):
        return SymbolTrue if arg else SymbolFalse
    if isinstance(arg, int) or number_type == "z":
        return Integer(arg)
    elif isinstance(arg, float) or number_type == "f":
        return Real(arg)
    elif number_type == "q":
        return Rational(arg)
    elif isinstance(arg, complex):
        return Complex(Real(arg.real), Real(arg.imag))
    elif number_type == "c":
        return Complex(arg.real, arg.imag)
    elif isinstance(arg, str):
        return String(arg)
        # if arg[0] == arg[-1] == '"':
        #     return String(arg[1:-1])
        # else:
        #     return Symbol(arg)
    elif isinstance(arg, dict):
        entries = [
            Expression(
                "Rule",
                from_python(key),
                from_python(arg[key]),
            )
            for key in arg
        ]
        return Expression(SymbolList, *entries)
    elif isinstance(arg, BaseExpression):
        return arg
    elif isinstance(arg, BoxConstruct):
        return arg
    elif isinstance(arg, list) or isinstance(arg, tuple):
        return Expression(SymbolList, *[from_python(leaf) for leaf in arg])
    elif isinstance(arg, bytearray) or isinstance(arg, bytes):
        return Expression(SymbolByteArray, ByteArrayAtom(arg))
    else:
        raise NotImplementedError
