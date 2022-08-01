# -*- coding: utf-8 -*-

"""
Integer Functions
"""


import sympy
import string


from mathics.builtin.base import Builtin, SympyFunction
from mathics.core.atoms import Integer, Integer0, String
from mathics.core.attributes import listable, numeric_function, protected
from mathics.core.convert.sympy import from_sympy
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolPlus, SymbolTimes


class Floor(SympyFunction):
    """
    <dl>
      <dt>'Floor[$x$]'
      <dd>gives the greatest integer less than or equal to $x$.

      <dt>'Floor[$x$, $a$]'
      <dd>gives the greatest multiple of $a$ less than or equal to $x$.
    </dl>

    >> Floor[10.4]
     = 10
    >> Floor[10/3]
     = 3
    >> Floor[10]
     = 10
    >> Floor[21, 2]
     = 20
    >> Floor[2.6, 0.5]
     = 2.5
    >> Floor[-10.4]
     = -11

    For complex $x$, take the floor of real an imaginary parts.
    >> Floor[1.5 + 2.7 I]
     = 1 + 2 I

    For negative $a$, the smallest multiple of $a$ greater than or equal to $x$
    is returned.
    >> Floor[10.4, -1]
     = 11
    >> Floor[-10.4, -1]
     = -10
    """

    attributes = listable | numeric_function | protected
    rules = {"Floor[x_, a_]": "Floor[x / a] * a"}
    sympy_name = "floor"
    summary_text = "closest smaller integer"

    def apply_real(self, x, evaluation):
        "Floor[x_]"
        x = x.to_sympy()
        if x is not None:
            return from_sympy(sympy.floor(x))


class Ceiling(SympyFunction):
    """
    <dl>
       <dt>'Ceiling[$x$]'
       <dd>gives the smallest integer greater than or equal to $x$.
    </dl>

    >> Ceiling[1.2]
     = 2
    >> Ceiling[3/2]
     = 2

    For complex $x$, take the ceiling of real an imaginary parts.
    >> Ceiling[1.3 + 0.7 I]
     = 2 + I
    """

    attributes = listable | numeric_function | protected
    rules = {"Ceiling[x_, a_]": "Ceiling[x / a] * a"}
    summary_text = "closest larger integer"

    def apply(self, x, evaluation):
        "Ceiling[x_]"
        x = x.to_sympy()
        if x is None:
            return
        return from_sympy(sympy.ceiling(x))


class BitLength(Builtin):
    """
    <dl>
      <dt>'BitLength[$x$]'
      <dd>gives the number of bits needed to represent the integer $x$. $x$'s sign is ignored.
    </dl>

    >> BitLength[1023]
     = 10
    >> BitLength[100]
     = 7
    >> BitLength[-5]
     = 3
    >> BitLength[0]
     = 0
    """

    attributes = listable | protected
    summary_text = "length of the binary representation"

    def apply(self, n, evaluation):
        "BitLength[n_Integer]"
        n = n.get_int_value()
        if n < 0:
            n = -1 - n
        return Integer(n.bit_length())


def _reversed_digits(
    number, base
):  # yield digits for number in base "base" in reverse order
    number = abs(number)
    if number == 0:
        yield 0
    else:
        while number > 0:
            rest, digit = divmod(number, base)
            yield digit
            number = rest


def _pad(symbols, length, fill):  # pads "symbols" to length "length" using "fill"
    pad_length = length - len(symbols)
    if pad_length <= 0:
        return symbols[-pad_length:]
    else:
        return fill * pad_length + symbols


class IntegerString(Builtin):
    """
    <dl>
    <dt>'IntegerString[$n$]'
        <dd>returns the decimal representation of integer $x$ as string. $x$'s sign is ignored.
    <dt>'IntegerString[$n$, $b$]'
        <dd>returns the base $b$ representation of integer $x$ as string. $x$'s sign is ignored.
    <dt>'IntegerString[$n$, $b$, $length$]'
        <dd>returns a string of length $length$. If the number is too short, the string gets padded
        with 0 on the left. If the number is too long, the $length$ least significant digits are
        returned.
    </dl>

    For bases > 10, alphabetic characters a, b, ... are used to represent digits 11, 12, ... . Note
    that base must be an integer in the range from 2 to 36.

    >> IntegerString[12345]
     = 12345
    >> IntegerString[-500]
     = 500
    >> IntegerString[12345, 10, 8]
     = 00012345
    >> IntegerString[12345, 10, 3]
     = 345
    >> IntegerString[11, 2]
     = 1011
    >> IntegerString[123, 8]
     = 173
    >> IntegerString[32767, 16]
     = 7fff
    >> IntegerString[98765, 20]
     = c6i5
    """

    _python_builtin = {
        16: lambda number: hex(abs(number))[2:],
        10: lambda number: str(abs(number)),
        2: lambda number: bin(abs(number))[2:],
        # oct() changed definition for Python 3
    }
    attributes = listable | protected
    list_of_symbols = string.digits + string.ascii_letters
    messages = {
        "basf": "Base `` must be an integer in the range from 2 to 36.",
    }

    rules = {
        "IntegerString[n_Integer]": "IntegerString[n, 10]",
    }
    summary_text = "decimal representation of a number as a string"

    def _symbols(self, n, b, evaluation):
        builtin = IntegerString._python_builtin.get(b)
        if builtin:
            return builtin(n)
        else:
            list_of_symbols = IntegerString.list_of_symbols
            if b > len(list_of_symbols) or b < 2:
                evaluation.message("IntegerString", "basf", b)
                return False
            else:
                return "".join(
                    reversed([list_of_symbols[r] for r in _reversed_digits(n, b)])
                )

    def apply_n(self, n, b, evaluation):
        "IntegerString[n_Integer, b_Integer]"
        s = self._symbols(n.get_int_value(), b.get_int_value(), evaluation)
        return String(s) if s else None

    def apply_n_b_length(self, n, b, length, evaluation):
        "IntegerString[n_Integer, b_Integer, length_Integer]"
        s = self._symbols(n.get_int_value(), b.get_int_value(), evaluation)
        return String(_pad(s, length.get_int_value(), "0")) if s else None


class _IntBaseBuiltin(Builtin):
    messages = {
        "basf": "Base `` must be an integer greater than 1.",
    }

    def _valid_base(self, b, evaluation):
        base = b.get_int_value()
        if base < 2:
            evaluation.message(self.get_name(), "basf", base)
            return False
        else:
            return base


class IntegerDigits(_IntBaseBuiltin):
    """
    <dl>
    <dt>'IntegerDigits[$n$]'
        <dd>returns the decimal representation of integer $x$ as list of digits. $x$'s sign is ignored.
    <dt>'IntegerDigits[$n$, $b$]'
        <dd>returns the base $b$ representation of integer $x$ as list of digits. $x$'s sign is ignored.
    <dt>'IntegerDigits[$n$, $b$, $length$]'
        <dd>returns a list of length $length$. If the number is too short, the list gets padded
        with 0 on the left. If the number is too long, the $length$ least significant digits are
        returned.
    </dl>

    >> IntegerDigits[12345]
     = {1, 2, 3, 4, 5}
    >> IntegerDigits[-500]
     = {5, 0, 0}
    >> IntegerDigits[12345, 10, 8]
     = {0, 0, 0, 1, 2, 3, 4, 5}
    >> IntegerDigits[12345, 10, 3]
     = {3, 4, 5}
    >> IntegerDigits[11, 2]
     = {1, 0, 1, 1}
    >> IntegerDigits[123, 8]
     = {1, 7, 3}
    >> IntegerDigits[98765, 20]
     = {12, 6, 18, 5}
    """

    summary_text = "list of digits of a number"
    rules = {
        "IntegerDigits[n_Integer]": "IntegerDigits[n, 10]",
    }

    _padding = [Integer0]

    def apply_n_b(self, n, b, evaluation):
        "IntegerDigits[n_Integer, b_Integer]"
        base = self._valid_base(b, evaluation)
        return (
            ListExpression(
                *[
                    Integer(d)
                    for d in reversed(list(_reversed_digits(n.get_int_value(), base)))
                ]
            )
            if base
            else None
        )

    def apply_n_b_length(self, n, b, length, evaluation):
        "IntegerDigits[n_Integer, b_Integer, length_Integer]"
        base = self._valid_base(b, evaluation)
        return (
            ListExpression(
                *_pad(
                    [
                        Integer(d)
                        for d in reversed(
                            list(_reversed_digits(n.get_int_value(), base))
                        )
                    ],
                    length.get_int_value(),
                    self._padding,
                )
            )
            if base
            else None
        )


class DigitCount(_IntBaseBuiltin):
    """
    <dl>
    <dt>'DigitCount[$n$, $b$, $d$]'
        <dd>returns the number of times digit $d$ occurs in the base $b$ representation of $n$.
    <dt>'DigitCount[$n$, $b$]'
        <dd>returns a list indicating the number of times each digit occurs in the base $b$ representation of $n$.
    <dt>'DigitCount[$n$, $b$]'
        <dd>returns a list indicating the number of times each digit occurs in the decimal representation of $n$.
    </dl>

    >> DigitCount[1022]
     = {1, 2, 0, 0, 0, 0, 0, 0, 0, 1}
    >> DigitCount[Floor[Pi * 10^100]]
     = {8, 12, 12, 10, 8, 9, 8, 12, 14, 8}
    >> DigitCount[1022, 2]
     = {9, 1}
    >> DigitCount[1022, 2, 1]
     = 9
    """

    summary_text = (
        "number of occurrences of a digit in the base-b representation of a number"
    )
    rules = {
        "DigitCount[n_Integer]": "DigitCount[n, 10]",
    }

    def apply_n_b_d(self, n, b, d, evaluation):
        "DigitCount[n_Integer, b_Integer, d_Integer]"
        base = self._valid_base(b, evaluation)
        if not base:
            return
        match = d.get_int_value()
        return Integer(
            sum(
                1
                for digit in _reversed_digits(n.get_int_value(), base)
                if digit == match
            )
        )

    def apply_n_b(self, n, b, evaluation):
        "DigitCount[n_Integer, b_Integer]"
        base = self._valid_base(b, evaluation)
        if not base:
            return
        occurence_count = [0] * base
        for digit in _reversed_digits(n.get_int_value(), base):
            occurence_count[digit] += 1
        # result list is rotated by one element to the left
        return to_mathics_list(*(occurence_count[1:] + [occurence_count[0]]))


class IntegerReverse(_IntBaseBuiltin):
    """
    <dl>
    <dt>'IntegerReverse[$n$]'
        <dd>returns the integer that has the reverse decimal representation of $x$ without sign.
    <dt>'IntegerReverse[$n$, $b$]'
        <dd>returns the integer that has the reverse base $b$ represenation of $x$ without sign.
    </dl>

    >> IntegerReverse[1234]
     = 4321
    >> IntegerReverse[1022, 2]
     = 511
    >> IntegerReverse[-123]
     = 321
    """

    summary_text = "number with digits in the inverse order"
    rules = {
        "IntegerReverse[n_Integer]": "IntegerReverse[n, 10]",
    }

    def apply_n_b(self, n, b, evaluation):
        "IntegerReverse[n_Integer, b_Integer]"
        base = self._valid_base(b, evaluation)
        if not base:
            return
        value = 0
        for digit in _reversed_digits(n.get_int_value(), base):
            value = value * base + digit
        return Integer(value)


class FromDigits(Builtin):
    """
    <dl>
    <dt>'FromDigits[$l$]'
        <dd>returns the integer corresponding to the decimal representation given by $l$. $l$ can be a list of
        digits or a string.
    <dt>'FromDigits[$l$, $b$]'
        <dd>returns the integer corresponding to the base $b$ representation given by $l$. $l$ can be a list of
        digits or a string.
    </dl>

    >> FromDigits["123"]
     = 123
    >> FromDigits[{1, 2, 3}]
     = 123
    >> FromDigits[{1, 0, 1}, 1000]
     = 1000001

    FromDigits can handle symbolic input:
    >> FromDigits[{a, b, c}, 5]
     = c + 5 (5 a + b)

    Note that FromDigits does not automatically detect if you are providing a non-decimal representation:
    >> FromDigits["a0"]
     = 100
    >> FromDigits["a0", 16]
     = 160

    FromDigits on empty lists or strings returns 0:
    >> FromDigits[{}]
     = 0
    >> FromDigits[""]
     = 0

    #> FromDigits[x]
     : The input must be a string of digits or a list.
     = FromDigits[x, 10]
    """

    summary_text = "integer from a list of digits"
    rules = {"FromDigits[l_]": "FromDigits[l, 10]"}

    messages = {"nlst": "The input must be a string of digits or a list."}

    @staticmethod
    def _parse_string(s, b):
        code_0 = ord("0")
        code_a = ord("a")
        assert code_a > code_0

        value = Integer0
        for char in s.lower():
            code = ord(char)
            if code >= code_a:
                digit = 10 + code - code_a
            else:
                digit = code - code_0
            if 0 <= digit < 36:
                value = Expression(
                    SymbolPlus, Expression(SymbolTimes, value, b), Integer(digit)
                )
            else:
                return None

        return value

    def apply(self, l, b, evaluation):
        "FromDigits[l_, b_]"
        if l.get_head_name() == "System`List":
            value = Integer0
            for element in l.elements:
                value = Expression(
                    SymbolPlus, Expression(SymbolTimes, value, b), element
                )
            return value
        elif isinstance(l, String):
            value = FromDigits._parse_string(l.get_string_value(), b)
            if value is None:
                evaluation.message("FromDigits", "nlst")
            else:
                return value
        else:
            evaluation.message("FromDigits", "nlst")
