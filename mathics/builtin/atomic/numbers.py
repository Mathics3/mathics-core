# cython: language_level=3
# -*- coding: utf-8 -*-

# Note: docstring is flowed in documentation. Line breaks in the docstring will appear in the
# printed output, so be carful not to add then mid-sentence.

"""
Representation of Numbers

Integers and Real numbers with any number of digits, automatically tagging numerical preceision when appropriate.

Precision is not "guarded" through the evaluation process. Only integer precision is supported.
However, things like 'N[Pi, 100]' should work as expected.
"""

import sympy
import mpmath
from functools import lru_cache


from mathics.builtin.base import Builtin, Predefined, Test

from mathics.core.atoms import (
    Integer,
    Integer0,
    Integer10,
    MachineReal,
    Number,
    Rational,
    Real,
)
from mathics.core.attributes import (
    listable as A_LISTABLE,
    protected as A_PROTECTED,
)
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_bool, from_python
from mathics.core.evaluators import eval_N
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.number import (
    dps,
    convert_int_to_digit_list,
    machine_precision,
    machine_epsilon,
)
from mathics.core.symbols import Symbol, SymbolDivide
from mathics.core.systemsymbols import (
    SymbolIndeterminate,
    SymbolInfinity,
    SymbolLog,
    SymbolN,
    SymbolPrecision,
    SymbolRealDigits,
    SymbolRound,
)

SymbolIntegerDigits = Symbol("IntegerDigits")
SymbolIntegerExponent = Symbol("IntegerExponent")


@lru_cache(maxsize=1024)
def log_n_b(py_n, py_b) -> int:
    return int(mpmath.ceil(mpmath.log(py_n, py_b))) if py_n != 0 and py_n != 1 else 1


def check_finite_decimal(denominator):
    # The rational number is finite decimal if the denominator has form 2^a * 5^b
    while denominator % 5 == 0:
        denominator = denominator / 5

    while denominator % 2 == 0:
        denominator = denominator / 2

    return True if denominator == 1 else False


def convert_repeating_decimal(numerator, denominator, base):
    head = [x for x in str(numerator // denominator)]
    tails = []
    subresults = [numerator % denominator]
    numerator %= denominator

    while numerator != 0:  # only rational input can go to this case
        numerator *= base
        result_digit, numerator = divmod(numerator, denominator)
        tails.append(str(result_digit))
        if numerator not in subresults:
            subresults.append(numerator)
        else:
            break

    for i in range(len(head) - 1, -1, -1):
        j = len(tails) - 1
        if head[i] != tails[j]:
            break
        else:
            del tails[j]
            tails.insert(0, head[i])
            del head[i]
            j = j - 1

    # truncate all leading 0's
    if all(elem == "0" for elem in head):
        for i in range(0, len(tails)):
            if tails[0] == "0":
                tails = tails[1:] + [str(0)]
            else:
                break
    return (head, tails)


def convert_float_base(x, base, precision=10):

    length_of_int = 0 if x == 0 else int(mpmath.log(x, base))
    # iexps = list(range(length_of_int, -1, -1))

    def convert_int(x, base, exponents):
        out = []
        for e in range(0, exponents + 1):
            d = x % base
            out.append(d)
            x = x / base
            if x == 0:
                break
        out.reverse()
        return out

    def convert_float(x, base, exponents):
        out = []
        for e in range(0, exponents):
            d = int(x * base)
            out.append(d)
            x = (x * base) - d
            if x == 0:
                break
        return out

    int_part = convert_int(int(x), base, length_of_int)
    if isinstance(x, (float, sympy.Float)):
        # fexps = list(range(-1, -int(precision + 1), -1))
        real_part = convert_float(x - int(x), base, precision + 1)
        return int_part + real_part
    elif isinstance(x, int):
        return int_part
    else:
        raise TypeError(x)


class ExactNumberQ(Test):
    """
    <dl>
      <dt>'ExactNumberQ[$expr$]'
      <dd>returns 'True' if $expr$ is an exact number, and 'False' otherwise.
    </dl>

    >> ExactNumberQ[10]
     = True
    >> ExactNumberQ[4.0]
     = False
    >> ExactNumberQ[n]
     = False

    'ExactNumberQ' can be applied to complex numbers:
    >> ExactNumberQ[1 + I]
     = True
    >> ExactNumberQ[1 + 1. I]
     = False
    """

    summary_text = "test if an expression is an exact real or complex number"

    def test(self, expr):
        return isinstance(expr, Number) and not expr.is_inexact()


class IntegerDigits(Builtin):
    """
    <dl>
    <dt>'IntegerDigits[$n$]'
        <dd>returns a list of the base-10 digits in the integer $n$.
    <dt>'IntegerDigits[$n$, $base$]'
        <dd>returns a list of the base-$base$ digits in $n$.
    <dt>'IntegerDigits[$n$, $base$, $length$]'
        <dd>returns a list of length $length$, truncating or padding
        with zeroes on the left as necessary.
    </dl>

    >> IntegerDigits[76543]
     = {7, 6, 5, 4, 3}

    The sign of $n$ is discarded:
    >> IntegerDigits[-76543]
     = {7, 6, 5, 4, 3}

    >> IntegerDigits[15, 16]
     = {15}
    >> IntegerDigits[1234, 16]
     = {4, 13, 2}
    >> IntegerDigits[1234, 10, 5]
     = {0, 1, 2, 3, 4}

    #> IntegerDigits[1000, 10]
     = {1, 0, 0, 0}

    #> IntegerDigits[0]
     = {0}
    """

    attributes = A_LISTABLE | A_PROTECTED

    messages = {
        "int": "Integer expected at position 1 in `1`",
        "ibase": "Base `1` is not an integer greater than 1.",
    }

    rules = {
        "IntegerDigits[n_]": "IntegerDigits[n, 10]",
    }

    summary_text = "digits of an integer in any base"

    def apply_len(self, n, base, length, evaluation):
        "IntegerDigits[n_, base_, length_]"

        if not (isinstance(length, Integer) and length.get_int_value() >= 0):
            return evaluation.message("IntegerDigits", "intnn")

        return self.apply(n, base, evaluation, nr_elements=length.get_int_value())

    def apply(self, n, base, evaluation, nr_elements=None):
        "IntegerDigits[n_, base_]"

        if not (isinstance(n, Integer)):
            return evaluation.message(
                "IntegerDigits", "int", Expression(SymbolIntegerDigits, n, base)
            )

        if not (isinstance(base, Integer) and base.get_int_value() > 1):
            return evaluation.message("IntegerDigits", "ibase", base)

        if nr_elements == 0:
            # trivial case: we don't want any digits
            return ListExpression()

        # Note: above we checked that n and b are Integers, so we can use x.value.
        digits = convert_int_to_digit_list(n.value, base.value)

        if nr_elements is not None:
            if len(digits) >= nr_elements:
                # Truncate, preserving the digits on the right
                digits = digits[-nr_elements:]
            else:
                # Pad with zeroes
                digits = [0] * (nr_elements - len(digits)) + digits

        return to_mathics_list(*digits, element_conversion_fn=Integer)


class IntegerExponent(Builtin):
    """
    <dl>
      <dt>'IntegerExponent[$n$, $b$]'
      <dd>gives the highest exponent of $b$ that divides $n$.
    </dl>

    >> IntegerExponent[16, 2]
     = 4

    >> IntegerExponent[-510000]
     = 4

    >> IntegerExponent[10, b]
     = IntegerExponent[10, b]
    """

    attributes = A_LISTABLE | A_PROTECTED

    messages = {
        "int": "Integer expected at position 1 in `1`",
        "ibase": "Base `1` is not an integer greater than 1.",
    }

    rules = {
        "IntegerExponent[n_]": "IntegerExponent[n, 10]",
    }

    summary_text = "number of trailing 0s in a given base"

    def apply_two_arg_integers(self, n: Integer, b: Integer, evaluation):
        "IntegerExponent[n_Integer, b_Integer]"

        py_n, py_b = n.value, b.value
        py_n = abs(py_n)

        # TODO: Optimise this (dont need to calc. base^result)
        # NOTE: IntegerExponent[a,b] causes a Python error here when a or b are
        # symbols. The function signature here ensures we have Integers.
        result = 1
        while py_n % (py_b**result) == 0:
            result += 1

        return Integer(result - 1)

    # FIXME: If WMA supports things other than Integers, the below code might
    # be useful as a starting point.
    # def apply(self, n: Integer, b: Integer, evaluation):
    #     "IntegerExponent[n_Integer, b_Integer]"

    #     py_n, py_b = n.to_python(), b.to_python()
    #     expr = Expression(SymbolIntegerExponent, n, b)

    #     if not isinstance(py_n, int):
    #         evaluation.message("IntegerExponent", "int", expr)
    #     py_n = abs(py_n)

    #     if not (isinstance(py_b, int) and py_b > 1):
    #         evaluation.message("IntegerExponent", "ibase", b)

    #     # TODO: Optimise this (dont need to calc. base^result)
    #     # NOTE: IntegerExponent[a,b] causes a Python error here when a or b are
    #     # symbols
    #     result = 1
    #     while py_n % (py_b ** result) == 0:
    #         result += 1

    #     return Integer(result - 1)


class IntegerLength(Builtin):
    """
    <dl>
      <dt>'IntegerLength[$x$]'
      <dd>gives the number of digits in the base-10 representation of $x$.

      <dt>'IntegerLength[$x$, $b$]'
      <dd>gives the number of base-$b$ digits in $x$.
    </dl>

    >> IntegerLength[123456]
     = 6
    >> IntegerLength[10^10000]
     = 10001
    >> IntegerLength[-10^1000]
     = 1001
    'IntegerLength' with base 2:
    >> IntegerLength[8, 2]
     = 4
    Check that 'IntegerLength' is correct for the first 100 powers of 10:
    >> IntegerLength /@ (10 ^ Range[100]) == Range[2, 101]
     = True
    The base must be greater than 1:
    >> IntegerLength[3, -2]
     : Base -2 is not an integer greater than 1.
     = IntegerLength[3, -2]

    '0' is a special case:
    >> IntegerLength[0]
     = 0

    #> IntegerLength /@ (10 ^ Range[100] - 1) == Range[1, 100]
     = True
    """

    attributes = A_LISTABLE | A_PROTECTED

    messages = {
        "base": "Base `1` is not an integer greater than 1.",
    }

    rules = {
        "IntegerLength[n_]": "IntegerLength[n, 10]",
    }

    summary_text = "total number of digits in any base"

    def apply(self, n, b, evaluation):
        "IntegerLength[n_, b_]"

        n, b = n.get_int_value(), b.get_int_value()
        if n is None or b is None:
            evaluation.message("IntegerLength", "int")
            return
        if b <= 1:
            evaluation.message("IntegerLength", "base", b)
            return

        if n == 0:
            # special case
            return Integer0

        n = abs(n)

        # O(log(digits))

        # find bounds
        j = 1
        while b**j <= n:
            j *= 2
        i = j // 2

        # bisection
        while i + 1 < j:
            # assert b ** i <= n <= b ** j
            k = (i + j) // 2
            if b**k <= n:
                i = k
            else:
                j = k
        return Integer(j)


class InexactNumberQ(Test):
    """
    <dl>
      <dt>'InexactNumberQ[$expr$]'
      <dd>returns 'True' if $expr$ is not an exact number, and 'False' otherwise.
    </dl>

    >> InexactNumberQ[a]
     = False
    >> InexactNumberQ[3.0]
     = True
    >> InexactNumberQ[2/3]
     = False

    'InexactNumberQ' can be applied to complex numbers:
    >> InexactNumberQ[4.0+I]
     = True
    """

    summary_text = "the negation of ExactNumberQ"

    def test(self, expr):
        return isinstance(expr, Number) and expr.is_inexact()


class IntegerQ(Test):
    """
    <dl>
      <dt>'IntegerQ[$expr$]'
      <dd>returns 'True' if $expr$ is an integer, and 'False' otherwise.
    </dl>

    >> IntegerQ[3]
     = True
    >> IntegerQ[Pi]
     = False
    """

    summary_text = "test whether an expression is an integer"

    def test(self, expr):
        return isinstance(expr, Integer)


class MachineNumberQ(Test):
    """
    <dl>
      <dt>'MachineNumberQ[$expr$]'
      <dd>returns 'True' if $expr$ is a machine-precision real or complex number.
    </dl>

     = True
    >> MachineNumberQ[3.14159265358979324]
     = False
    >> MachineNumberQ[1.5 + 2.3 I]
     = True
    >> MachineNumberQ[2.71828182845904524 + 3.14159265358979324 I]
     = False
    #> MachineNumberQ[1.5 + 3.14159265358979324 I]
     = True
    #> MachineNumberQ[1.5 + 5 I]
     = True
    """

    summary_text = "test if expression is a machine‐precision real or complex number"

    def test(self, expr):
        return expr.is_machine_precision()


class RealDigits(Builtin):
    """
    <dl>
      <dt>'RealDigits[$n$]'
      <dd>returns the decimal representation of the real number $n$ as list of digits, together with the number of digits that are to the left of the decimal point.

      <dt>'RealDigits[$n$, $b$]'
      <dd>returns a list of base_$b$ representation of the real number $n$.

      <dt>'RealDigits[$n$, $b$, $len$]'
      <dd>returns a list of $len$ digits.

      <dt>'RealDigits[$n$, $b$, $len$, $p$]'
      <dd>return $len$ digits starting with the coefficient of $b$^$p$
    </dl>

    Return the list of digits and exponent:
    >> RealDigits[123.55555]
     = {{1, 2, 3, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0}, 3}

    Return an explicit recurring decimal form:
    >> RealDigits[19 / 7]
     = {{2, {7, 1, 4, 2, 8, 5}}, 1}

    The 500th digit of Pi is 2:
    >> RealDigits[Pi, 10, 1, -500]
    = {{2}, -499}

    11 digits starting with the coefficient of 10^-3:
    >> RealDigits[Pi, 10, 11, -3]
     = {{1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7}, -2}

    RealDigits gives Indeterminate if more digits than the precision are requested:
    >> RealDigits[123.45, 10, 18]
     = {{1, 2, 3, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, Indeterminate, Indeterminate}, 3}

    #> RealDigits[-1.25, -1]
     : Base -1 is not a real number greater than 1.
     = RealDigits[-1.25, -1]

    Return 25 digits of in base 10:
    >> RealDigits[Pi, 10, 25]
     = {{3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 6, 4, 3}, 1}

    #> RealDigits[-Pi]
     : The number of digits to return cannot be determined.
     = RealDigits[-Pi]

    #> RealDigits[I, 7]
     : The value I is not a real number.
    = RealDigits[I, 7]

    #> RealDigits[Pi]
     : The number of digits to return cannot be determined.
     = RealDigits[Pi]

    #> RealDigits[3 + 4 I]
     : The value 3 + 4 I is not a real number.
     = RealDigits[3 + 4 I]


    #> RealDigits[3.14, 10, 1.5]
     : Non-negative machine-sized integer expected at position 3 in RealDigits[3.14, 10, 1.5].
     = RealDigits[3.14, 10, 1.5]

    #> RealDigits[3.14, 10, 1, 1.5]
     : Machine-sized integer expected at position 4 in RealDigits[3.14, 10, 1, 1.5].
     = RealDigits[3.14, 10, 1, 1.5]

    """

    attributes = A_LISTABLE | A_PROTECTED

    messages = {
        "realx": "The value `1` is not a real number.",
        "ndig": "The number of digits to return cannot be determined.",
        "rbase": "Base `1` is not a real number greater than 1.",
        "intnm": "Non-negative machine-sized integer expected at position 3 in `1`.",
        "intm": "Machine-sized integer expected at position 4 in `1`.",
    }

    summary_text = "digits of a real number"

    def apply_complex(self, n, var, evaluation):
        "%(name)s[n_Complex, var___]"
        return evaluation.message("RealDigits", "realx", n)

    def apply_rational_with_base(self, n, b, evaluation):
        "%(name)s[n_Rational, b_Integer]"
        # expr = Expression(SymbolRealDigits, n)
        py_n = abs(n.value)
        py_b = b.value
        if check_finite_decimal(n.denominator().get_int_value()) and not py_b % 2:
            return self.apply_with_base(n, b, evaluation)
        else:
            exp = int(mpmath.ceil(mpmath.log(py_n, py_b)))
            (head, tails) = convert_repeating_decimal(
                py_n.as_numer_denom()[0], py_n.as_numer_denom()[1], py_b
            )

            elements = []
            for x in head:
                if x != "0":
                    elements.append(Integer(int(x)))
            elements.append(from_python(tails))
            list_expr = ListExpression(*elements)
        return ListExpression(list_expr, Integer(exp))

    def apply_rational_without_base(self, n, evaluation):
        "%(name)s[n_Rational]"

        return self.apply_rational_with_base(n, Integer(10), evaluation)

    def apply(self, n, evaluation):
        "%(name)s[n_]"

        # Handling the testcases that throw the error message and return the ouput that doesn't include `base` argument
        if isinstance(n, Symbol) and n.name.startswith("System`"):
            return evaluation.message("RealDigits", "ndig", n)

        if n.is_numeric(evaluation):
            return self.apply_with_base(n, from_python(10), evaluation)

    def apply_with_base(self, n, b, evaluation, nr_elements=None, pos=None):
        "%(name)s[n_?NumericQ, b_Integer]"

        expr = Expression(SymbolRealDigits, n)
        rational_no = (
            True if isinstance(n, Rational) else False
        )  # it is used for checking whether the input n is a rational or not
        py_b = b.get_int_value()
        if isinstance(n, (Expression, Symbol, Rational)):
            pos_len = abs(pos) + 1 if pos is not None and pos < 0 else 1
            if nr_elements is not None:
                # we can't use apply_n here because we have the two-arguemnt form
                n = Expression(
                    SymbolN,
                    n,
                    Integer(int(mpmath.log(py_b ** (nr_elements + pos_len), 10)) + 1),
                ).evaluate(evaluation)
            else:
                if rational_no:
                    n = eval_N(n, evaluation)
                else:
                    return evaluation.message("RealDigits", "ndig", expr)
        py_n = abs(n.value)

        if not py_b > 1:
            return evaluation.message("RealDigits", "rbase", py_b)

        if isinstance(py_n, complex):
            return evaluation.message("RealDigits", "realx", expr)

        if isinstance(n, Integer):
            display_len = (
                int(mpmath.floor(mpmath.log(py_n, py_b)))
                if py_n != 0 and py_n != 1
                else 1
            )
        else:
            display_len = int(
                eval_N(
                    Expression(
                        SymbolRound,
                        Expression(
                            SymbolDivide,
                            Expression(SymbolPrecision, n),
                            Expression(SymbolLog, Integer10, b),
                        ),
                    ),
                    evaluation,
                ).to_python()
            )

        exp = log_n_b(py_n, py_b)

        if py_n == 0 and nr_elements is not None:
            exp = 0

        digits = []
        if not py_b == 10:
            digits = convert_float_base(py_n, py_b, display_len - exp)
            # truncate all the leading 0's
            i = 0
            while digits and digits[i] == 0:
                i += 1
            digits = digits[i:]

            if not isinstance(n, Integer):
                if len(digits) > display_len:
                    digits = digits[: display_len - 1]
        else:
            # drop any leading zeroes
            for x in str(py_n):
                if x != "." and (digits or x != "0"):
                    digits.append(x)

        if pos is not None:
            temp = exp
            exp = pos + 1
            move = temp - 1 - pos
            if move <= 0:
                digits = [0] * abs(move) + digits
            else:
                digits = digits[abs(move) :]
                display_len = display_len - move

        elements = []
        for x in digits:
            if x == "e" or x == "E":
                break
            # Convert to Mathics' list format
            elements.append(Integer(int(x)))

        if not rational_no:
            while len(elements) < display_len:
                elements.append(Integer0)

        if nr_elements is not None:
            # display_len == nr_elements
            if len(elements) >= nr_elements:
                # Truncate, preserving the digits on the right
                elements = elements[:nr_elements]
            else:
                if isinstance(n, Integer):
                    while len(elements) < nr_elements:
                        elements.append(Integer0)
                else:
                    # Adding Indeterminate if the length is greater than the precision
                    while len(elements) < nr_elements:
                        elements.append(SymbolIndeterminate)
        list_expr = ListExpression(*elements)
        return ListExpression(list_expr, Integer(exp))

    def apply_with_base_and_length(self, n, b, length, evaluation, pos=None):
        "%(name)s[n_?NumericQ, b_Integer, length_]"
        elements = []
        if pos is not None:
            elements.append(from_python(pos))
        expr = Expression(SymbolRealDigits, n, b, length, *elements)
        if not (isinstance(length, Integer) and length.get_int_value() >= 0):
            return evaluation.message("RealDigits", "intnm", expr)

        return self.apply_with_base(
            n, b, evaluation, nr_elements=length.get_int_value(), pos=pos
        )

    def apply_with_base_length_and_precision(self, n, b, length, p, evaluation):
        "%(name)s[n_?NumericQ, b_Integer, length_, p_]"
        if not isinstance(p, Integer):
            return evaluation.message(
                "RealDigits", "intm", Expression(SymbolRealDigits, n, b, length, p)
            )

        return self.apply_with_base_and_length(
            n, b, length, evaluation, pos=p.get_int_value()
        )


class MaxPrecision(Predefined):
    """
    <dl>
      <dt>'$MaxPrecision'
      <dd>represents the maximum number of digits of precision permitted in abitrary-precision numbers.
    </dl>

    >> $MaxPrecision
     = Infinity

    >> $MaxPrecision = 10;

    >> N[Pi, 11]
     : Requested precision 11 is larger than $MaxPrecision. Using current $MaxPrecision of 10. instead. $MaxPrecision = Infinity specifies that any precision should be allowed.
     = 3.141592654

    #> N[Pi, 10]
     = 3.141592654

    #> $MaxPrecision = x
     : Cannot set $MaxPrecision to x; value must be a positive number or Infinity.
     = x
    #> $MaxPrecision = -Infinity
     : Cannot set $MaxPrecision to -Infinity; value must be a positive number or Infinity.
     = -Infinity
    #> $MaxPrecision = 0
     : Cannot set $MaxPrecision to 0; value must be a positive number or Infinity.
     = 0
    #> $MaxPrecision = Infinity;

    #> $MinPrecision = 15;
    #> $MaxPrecision = 10
     : Cannot set $MaxPrecision such that $MaxPrecision < $MinPrecision.
     = 10
    #> $MaxPrecision
     = Infinity
    #> $MinPrecision = 0;
    """

    is_numeric = False
    messages = {
        "precset": "Cannot set `1` to `2`; value must be a positive number or Infinity.",
        "preccon": "Cannot set `1` such that $MaxPrecision < $MinPrecision.",
    }

    name = "$MaxPrecision"

    rules = {
        "$MaxPrecision": "Infinity",
    }

    summary_text = "settable global maximum precision bound"


class MachineEpsilon_(Predefined):
    """
    <dl>
    <dt>'$MachineEpsilon'
        <dd>is the distance between '1.0' and the next
            nearest representable machine-precision number.
    </dl>

    >> $MachineEpsilon
     = 2.22045×10^-16

    >> x = 1.0 + {0.4, 0.5, 0.6} $MachineEpsilon;
    >> x - 1
     = {0., 0., 2.22045×10^-16}
    """

    is_numeric = True
    name = "$MachineEpsilon"

    summary_text = "the difference between 1.0 and the next-nearest number representable as a machine-precision number"

    def evaluate(self, evaluation):
        return MachineReal(machine_epsilon)


class MachinePrecision_(Predefined):
    """
    <dl>
      <dt>'$MachinePrecision'
      <dd>is the number of decimal digits of precision for machine-precision numbers.
    </dl>

    >> $MachinePrecision
     = 15.9546
    """

    name = "$MachinePrecision"

    summary_text = (
        "the number of decimal digits of precision for machine-precision numbers"
    )
    is_numeric = True
    rules = {
        "$MachinePrecision": "N[MachinePrecision]",
    }


class MachinePrecision(Predefined):
    """
    <dl>
      <dt>'MachinePrecision'
      <dd>represents the precision of machine precision numbers.
    </dl>

    >> N[MachinePrecision]
     = 15.9546
    >> N[MachinePrecision, 30]
     = 15.9545897701910033463281614204

    #> N[E, MachinePrecision]
     = 2.71828

    #> Round[MachinePrecision]
     = 16
    """

    is_numeric = True
    rules = {
        "N[MachinePrecision, prec_]": ("N[Log[10, 2] * %i, prec]" % machine_precision),
    }

    summary_text = "symbol used to indicate machine‐number precision"


class MinPrecision(Builtin):
    """
    <dl>
      <dt>'$MinPrecision'
      <dd>represents the minimum number of digits of precision permitted in abitrary-precision numbers.
    </dl>

    >> $MinPrecision
     = 0

    >> $MinPrecision = 10;

    >> N[Pi, 9]
     : Requested precision 9 is smaller than $MinPrecision. Using current $MinPrecision of 10. instead.
     = 3.141592654

    #> N[Pi, 10]
     = 3.141592654

    #> $MinPrecision = x
     : Cannot set $MinPrecision to x; value must be a non-negative number.
     = x
    #> $MinPrecision = -Infinity
     : Cannot set $MinPrecision to -Infinity; value must be a non-negative number.
     = -Infinity
    #> $MinPrecision = -1
     : Cannot set $MinPrecision to -1; value must be a non-negative number.
     = -1
    #> $MinPrecision = 0;

    #> $MaxPrecision = 10;
    #> $MinPrecision = 15
     : Cannot set $MinPrecision such that $MaxPrecision < $MinPrecision.
     = 15
    #> $MinPrecision
     = 0
    #> $MaxPrecision = Infinity;
    """

    messages = {
        "precset": "Cannot set `1` to `2`; value must be a non-negative number.",
        "preccon": "Cannot set `1` such that $MaxPrecision < $MinPrecision.",
    }

    name = "$MinPrecision"
    is_numeric = True
    rules = {
        "$MinPrecision": "0",
    }

    summary_text = "settable global minimum precision bound"


class NumericQ(Builtin):
    """
    <dl>
    <dt>'NumericQ[$expr$]'
        <dd>tests whether $expr$ represents a numeric quantity.
    </dl>

    >> NumericQ[2]
     = True
    >> NumericQ[Sqrt[Pi]]
     = True
    >> NumberQ[Sqrt[Pi]]
     = False

    It is possible to set that a symbol is numeric or not by assign a boolean value
    to ``NumericQ``
    >> NumericQ[a]=True
     = True
    >> NumericQ[a]
     = True
    >> NumericQ[Sin[a]]
     = True

    Clear and ClearAll do not restore the default value.

    >> Clear[a]; NumericQ[a]
     = True
    >> ClearAll[a]; NumericQ[a]
     = True
    >> NumericQ[a]=False; NumericQ[a]
     = False
    NumericQ can only set to True or False
    >> NumericQ[a] = 37
     : Cannot set NumericQ[a] to 37; the lhs argument must be a symbol and the rhs must be True or False.
     = 37
    """

    messages = {
        "argx": "NumericQ called with `1` arguments; 1 argument is expected.",
        "set": "Cannot set `1` to `2`; the lhs argument must be a symbol and the rhs must be True or False.",
    }
    summary_text = "test whether an expression is a number"

    def apply(self, expr, evaluation):
        "NumericQ[expr_]"
        return from_bool(expr.is_numeric(evaluation))


class Precision(Builtin):
    """
    <dl>
    <dt>'Precision[$expr$]'
        <dd>examines the number of significant digits of $expr$.
    </dl>
    This is rather a proof-of-concept than a full implementation.
    Precision of compound expression is not supported yet.
    >> Precision[1]
     = Infinity
    >> Precision[1/2]
     = Infinity
    >> Precision[0.5]
     = MachinePrecision

    #> Precision[0.0]
     = MachinePrecision
    #> Precision[0.000000000000000000000000000000000000]
     = 0.
    #> Precision[-0.0]
     = MachinePrecision
    #> Precision[-0.000000000000000000000000000000000000]
     = 0.

    #> 1.0000000000000000 // Precision
     = MachinePrecision
    #> 1.00000000000000000 // Precision
     = 17.

    #> 0.4 + 2.4 I // Precision
     = MachinePrecision
    #> Precision[2 + 3 I]
     = Infinity

    #> Precision["abc"]
     = Infinity
    """

    rules = {
        "Precision[z_?MachineNumberQ]": "MachinePrecision",
    }

    summary_text = "find the precision of a number"

    def apply(self, z, evaluation):
        "Precision[z_]"

        if not z.is_inexact():
            return SymbolInfinity
        elif z.to_sympy().is_zero:
            return Real(0)
        else:
            return Real(dps(z.get_precision()))
