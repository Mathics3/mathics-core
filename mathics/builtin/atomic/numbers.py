# cython: language_level=3
# -*- coding: utf-8 -*-

# Note: docstring is not flowed in documentation. To avoid line breaks
# in docstrings appearing in the printed output, use \ before the line
# break.

"""
Representation of Numbers

Integers and Real numbers with any number of digits, automatically tagging \
numerical precision when appropriate.

Precision is not "guarded" through the evaluation process. Only integer \
precision is supported.

However, things like 'N[Pi, 100]' should work as expected.
"""

import mpmath

from mathics.core.atoms import (
    Complex,
    Integer,
    Integer0,
    Integer3,
    Integer10,
    MachineReal,
    Rational,
    Real,
)
from mathics.core.attributes import (
    A_LISTABLE,
    A_NO_ATTRIBUTES,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, Predefined
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.number import (
    FP_MANTISA_BINARY_DIGITS,
    MACHINE_EPSILON,
    get_float_inf,
    is_numeric,
)
from mathics.core.symbols import (
    Symbol,
    SymbolDivide,
    SymbolMaxPrecision,
    SymbolMinPrecision,
)
from mathics.core.systemsymbols import (
    SymbolIndeterminate,
    SymbolInfinity,
    SymbolLog,
    SymbolMachinePrecision,
    SymbolPrecision,
    SymbolRealDigits,
    SymbolRound,
)
from mathics.eval.nevaluator import eval_N, is_infinity
from mathics.eval.numbers.numbers import (
    check_finite_decimal,
    convert_float_base,
    eval_Accuracy,
    eval_Precision,
    has_machine_number,
    log_n_b,
    rational_digits,
    real_digits_truncated,
)
from mathics.eval.numbers.precision import eval_SetAccuracy, eval_SetPrecision

SymbolIntegerDigits = Symbol("IntegerDigits")
SymbolIntegerExponent = Symbol("IntegerExponent")


class Accuracy(Builtin):
    """
    <url>
    :Accuracy:
    https://en.wikipedia.org/wiki/Accuracy_and_precision</url>\
    (WMA <url>
    :Accuracy:
    https://reference.wolfram.com/language/ref/Accuracy.html</url>)

    <dl>
      <dt>'Accuracy'[$x$]
      <dd>examines the number of significant digits of $expr$ after the \
      decimal point in the number x.
    </dl>

    <i>Notice that the result could be slightly different from the result obtained \
    in WMA, due to differences in the internal representation of the real numbers.</i>

    'Accuracy' of a real number is estimated from its value and its precision:

    >> Accuracy[3.1416`2]
     = 1.50285

    Notice that the value is not exactly equal to the one obtained in WMA: \
    This is due to the different way in which 'Precision' is handled in SymPy.

    Accuracy for exact atoms is 'Infinity':
    >> Accuracy[1]
     = Infinity
    >> Accuracy[A]
     = Infinity

    For Complex numbers, the accuracy is estimated as (minus) the base-10 log
    of the square root of the squares of the errors on the real and complex parts:
    >> z=Complex[3.00``2, 4.00``2];
    >> Accuracy[z] == -Log[10, Sqrt[10^(-2 Accuracy[Re[z]]) + 10^(-2 Accuracy[Im[z]])]]
     = True

    Accuracy of expressions is given by the minimum accuracy of its elements:
    >> Accuracy[F[1, Pi, A]]
     = Infinity

    >> Accuracy[F[1.3, Pi, A]]
     = ...

    'Accuracy' for the value 0 is a fixed-precision Real number:
     >> 0``2
      = 0.00
     >> Accuracy[0.``2]
      = 2.

    For 0.`, the accuracy satisfies:
    >> Accuracy[0.`] == $MachinePrecision - Log[10, $MinMachineNumber]
     = True

    In compound expressions, the 'Accuracy' is fixed by the number with
    the lowest 'Accuracy':
    >> Accuracy[{{1, 1.`},{1.``5, 1.``10}}]
     = 5.

    See also <url>
    :'Precision':
    /doc/reference-of-built-in-symbols/atomic-elements-of-expressions
/representation-of-numbers/precision/</url>.
    """

    eval_error = Builtin.generic_argument_error
    expected_args = 1

    summary_text = "find the accuracy of a number"

    def eval(self, z, evaluation):
        """Accuracy[z_]"""
        acc = eval_Accuracy(z)
        if acc is None:
            return SymbolInfinity
        return MachineReal(acc)


class IntegerExponent(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/IntegerExponent.html</url>

    <dl>
      <dt>'IntegerExponent'[$n$, $b$]
      <dd>gives the highest exponent of $b$ that divides $n$.
    </dl>

    >> IntegerExponent[16, 2]
     = 4

    >> IntegerExponent[-510000]
     = 4

    >> IntegerExponent[10, b]
     = IntegerExponent[10, b]

    >> IntegerExponent[0, 2]
     = Infinity
    """

    attributes = A_LISTABLE | A_PROTECTED

    eval_error = Builtin.generic_argument_error
    expected_args = (1, 2)

    messages = {
        "int": "Integer expected at position 1 in `1`",
        "ibase": "Base `1` is not an integer greater than 1.",
    }

    rules = {
        "IntegerExponent[n_]": "IntegerExponent[n, 10]",
    }

    summary_text = "get the number of trailing 0s in a given base"

    def eval_two_arg_integers(self, n: Integer, b: Integer, evaluation: Evaluation):
        """IntegerExponent[n_Integer, b_Integer]"""

        py_n, py_b = n.value, b.value
        py_n = abs(py_n)

        # With a base below 2, the loop below never ends (b = 1), divides
        # by zero (b = 0), or counts powers of a negative number.
        if py_b < 2:
            evaluation.message("IntegerExponent", "ibase", b)
            return None
        # Every power of b divides 0.
        if py_n == 0:
            return SymbolInfinity

        result = 0
        while py_n % py_b == 0:
            py_n //= py_b
            result += 1

        return Integer(result)

    # FIXME: If WMA supports things other than Integers, the below code might
    # be useful as a starting point.
    # def eval(self, n: Integer, b: Integer, evaluation):
    #     "IntegerExponent[n_Integer, b_Integer]"

    #     py_n, py_b = n.to_python(), b.to_python()
    #     expr = Expression(SymbolIntegerExponent, n, b)

    #     if not isinstance(py_n, int):
    #         evaluation.message("IntegerExponent", "int", expr)
    #     py_n = abs(py_n)

    #     if not (isinstance(py_b, int) and py_b > 1):
    #         evaluation.message("IntegerExponent", "ibase", b)

    #     # TODO: Optimise this (we don't need to calc. base^result)
    #     # NOTE: IntegerExponent[a,b] causes a Python error here when a or b are
    #     # symbols
    #     result = 1
    #     while py_n % (py_b ** result) == 0:
    #         result += 1

    #     return Integer(result - 1)


class IntegerLength(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/IntegerLength.html</url>

    <dl>
      <dt>'IntegerLength'[$x$]
      <dd>gives the number of digits in the base-10 representation of $x$.

      <dt>'IntegerLength'[$x$, $b$]
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
    """

    attributes = A_LISTABLE | A_PROTECTED

    messages = {
        "base": "Base `1` is not an integer greater than 1.",
    }

    rules = {
        "IntegerLength[n_]": "IntegerLength[n, 10]",
    }

    summary_text = "get total number of digits in any base"

    def eval(self, n, b, evaluation):
        """IntegerLength[n_, b_]"""

        n, b = n.int_value, b.int_value
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


class NumberDigit(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/NumberDigit.html</url>

    <dl>
      <dt>'NumberDigit'[$x$, $n$]
      <dd>returns the digit coefficient of 10^$n$ for the real-valued number $x$.

      <dt>'NumberDigit'[$x$, $n$, $b$]
      <dd>returns the coefficient of $b$^$n$ in the base-$b$ representation of $x$.
    </dl>

    Get the 10^2 digit of 210.345:
    >> NumberDigit[210.345, 2]
     = 2

    Get the 10^-1 digit of 210.345:
    >> NumberDigit[210.345, -1]
     = 3

    >> BaseForm[N[Pi], 2]
     = 11.00100100001111110_2

    Get the 2^0 bit of Pi:
     = 1
    """

    attributes = A_PROTECTED | A_READ_PROTECTED

    rules = {
        "NumberDigit[x_, n_Integer]": "NumberDigit[x, n, 10]",
        "NumberDigit[x_, n_Integer, b_Integer]": "RealDigits[x, b, 1, n][[1]][[1]]",
    }

    summary_text = "get digits of a real number"


class RealDigits(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/RealDigits.html</url>

    <dl>
      <dt>'RealDigits'[$n$]
      <dd>returns the decimal representation for the real number $n$ as a list \
      of digits, together with the number of digits that are to the left of \
      the decimal point.

      <dt>'RealDigits'[$n$, $b$]
      <dd>returns a list of the "digits" in base-$b$ representation for the real number $n$.

      <dt>'RealDigits'[$n$, $b$, $len$]
      <dd>returns a list of $len$ digits.

      <dt>'RealDigits'[$n$, $b$, $len$, $p$]
      <dd>return $len$ digits starting with the coefficient of $b^p$.
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

    The digits are cut off, not rounded:
    >> RealDigits[1 - 10^-100, 10, 5]
     = {{9, 9, 9, 9, 9}, 0}
    >> RealDigits[Sqrt[104], 10, 1, -1]
     = {{1}, 0}

    RealDigits gives Indeterminate if more digits than the precision are requested:
    >> RealDigits[123.45, 10, 18]
     = {{1, 2, 3, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, Indeterminate, Indeterminate}, 3}

    Return 25 digits of in base 10:
    >> RealDigits[Pi, 10, 25]
     = {{3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 6, 4, 3}, 1}

    >> RealDigits[10]
     = {{1, 0}, 2}
    """

    attributes = A_LISTABLE | A_PROTECTED

    # Between one and four arguments are allowed.
    eval_error = Builtin.generic_argument_error
    expected_args = range(1, 5)

    messages = {
        "realx": "The value `1` is not a real number.",
        "ndig": "The number of digits to return cannot be determined.",
        "fnumx": "The value `1` did not evaluate to a sufficiently precise finite number.",
        "rbase": "Base `1` is not a real number greater than 1.",
        "intm": "Machine-sized integer expected at position 4 in `1`.",
    }

    summary_text = "get digits of a real number"

    def eval_rational_with_base(self, n, b, evaluation):
        "%(name)s[n_Rational, b_Integer]"
        # expr = Expression(SymbolRealDigits, n)
        py_n = abs(n.value)
        py_b = b.value
        if py_b < 2:
            evaluation.message("RealDigits", "rbase", b)
            return None
        if check_finite_decimal(n.denominator().int_value) and not py_b % 2:
            return self.eval_with_base(n, b, evaluation)
        numerator, denominator = py_n.as_numer_denom()
        digits, period, exponent = rational_digits(
            int(numerator), int(denominator), py_b
        )
        elements = [Integer(d) for d in digits]
        if period:
            elements.append(ListExpression(*(Integer(d) for d in period)))
        return ListExpression(ListExpression(*elements), Integer(exponent))

    def eval_rational_without_base(self, n, evaluation):
        "%(name)s[n_Rational]"

        return self.eval_rational_with_base(n, Integer(10), evaluation)

    def eval(self, n, evaluation):
        "%(name)s[n_]"

        # Handling the testcases that throw the error message and return the
        # output that doesn't include `base` argument
        if isinstance(n, Symbol) and n.name.startswith("System`"):
            evaluation.message("RealDigits", "ndig", n)
            return

        if is_numeric(n, evaluation):
            return self.eval_with_base(n, from_python(10), evaluation)

    def eval_with_base(self, n, b, evaluation, nr_elements=None, pos=None):
        """%(name)s[n_?NumericQ, b_Integer]"""

        if isinstance(n, Complex):
            evaluation.message("RealDigits", "realx", n)
            return

        expr = Expression(SymbolRealDigits, n)
        rational_no = (
            True if isinstance(n, Rational) else False
        )  # it is used for checking whether the input n is a rational or not
        py_b = b.int_value
        if not py_b > 1:
            evaluation.message("RealDigits", "rbase", py_b)
            return

        if isinstance(n, (Expression, Symbol, Rational)):
            if nr_elements is not None:
                result = real_digits_truncated(n, py_b, nr_elements, pos, evaluation)
                if result is None:
                    return None
                digits, exponent = result
                return ListExpression(
                    ListExpression(*(Integer(d) for d in digits)), Integer(exponent)
                )
            if rational_no:
                n = eval_N(n, evaluation)
            else:
                evaluation.message("RealDigits", "ndig", expr)
                return

        py_n = abs(n.value)

        if isinstance(py_n, complex):
            evaluation.message("RealDigits", "realx", expr)
            return

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
            if all(d == 0 for d in digits):
                digits = [0]
            else:
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

    def eval_with_base_and_length(self, n, b, length, evaluation, pos=None):
        """%(name)s[n_?NumericQ, b_Integer, length_]"""
        elements = []
        if pos is not None:
            elements.append(from_python(pos))
        expr = Expression(SymbolRealDigits, n, b, length, *elements)
        if not (isinstance(length, Integer) and length.int_value >= 0):
            evaluation.message("RealDigits", "intnm", Integer3, expr)
            return

        return self.eval_with_base(
            n, b, evaluation, nr_elements=length.int_value, pos=pos
        )

    def eval_with_base_length_and_precision(self, n, b, length, p, evaluation):
        """%(name)s[n_?NumericQ, b_Integer, length_, p_]"""
        if not isinstance(p, Integer):
            evaluation.message(
                "RealDigits", "intm", Expression(SymbolRealDigits, n, b, length, p)
            )
            return

        return self.eval_with_base_and_length(n, b, length, evaluation, pos=p.int_value)


class MaxPrecision(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/\$MaxPrecision.html</url>

    <dl>
      <dt>'\$MaxPrecision'
      <dd>represents the maximum number of digits of precision permitted \
          in abitrary-precision numbers.
    </dl>

    >> $MaxPrecision
     = Infinity

    >> $MaxPrecision = 10;

    >> N[Pi, 11]
     : Requested precision 11 is larger than $MaxPrecision. Using current $MaxPrecision of 10. instead. $MaxPrecision = Infinity specifies that any precision should be allowed.
     = 3.141592654
    """

    _is_numeric = False
    messages = {
        "precset": "Cannot set `1` to `2`; value must be a positive number or Infinity.",
        "preccon": "Cannot set `1` such that $MaxPrecision < $MinPrecision.",
    }

    name = "$MaxPrecision"

    rules = {
        "$MaxPrecision": "Infinity",
    }

    summary_text = "settable global maximum precision bound variable"


class MaxExtraPrecision(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/\$MaxExtraPrecision.html</url>

    <dl>
      <dt>'\$MaxExtraPrecision'
      <dd>is the largest number of digits beyond the requested precision \
          that 'N' uses to reach it.
    </dl>

    >> $MaxExtraPrecision
     = 50.

    'N' adds digits when a computation loses them:
    >> N[Pi - 314159/100000, 20] // Precision
     = 20.

    When that is not enough, the result has fewer digits:
    >> $MaxExtraPrecision = 5;
    >> N[Pi - 314159265358979/100000000000000, 20]
     : Internal precision limit $MaxExtraPrecision = 5. reached while evaluating -314159265358979 / 100000000000000 + Pi.
     = 3.238462643×10^-15

    >> $MaxExtraPrecision = -1
     : Cannot set $MaxExtraPrecision to -1; value must be a non-negative number or Infinity.
     = -1
    >> $MaxExtraPrecision
     = 5

    #> $MaxExtraPrecision = 50.;
    """

    attributes = A_NO_ATTRIBUTES
    messages = {
        "precset": "Cannot set `1` to `2`; value must be a non-negative number or Infinity.",
    }

    name = "$MaxExtraPrecision"

    rules = {
        "$MaxExtraPrecision": "50.",
    }

    summary_text = "settable limit on extra digits used to reach a precision"


class MachineEpsilon_(Predefined):
    r"""
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/\$MachineEpsilon.html</url>

    <dl>
      <dt>'\$MachineEpsilon'
      <dd>is the distance between '1.0' and the next \
          nearest representable machine-precision number.
    </dl>

    >> $MachineEpsilon
     = 2.22045×10^-16

    >> x = 1.0 + {0.4, 0.5, 0.6} $MachineEpsilon;
    >> x - 1
     = {0., 0., 2.22045×10^-16}
    """

    _is_numeric = True
    name = "$MachineEpsilon"

    summary_text = "get the difference between 1.0 and the next-nearest number representable as a machine-precision number"

    def evaluate(self, evaluation):
        return MachineReal(MACHINE_EPSILON)


class MachinePrecision_(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/\$MachinePrecision.html</url>

    <dl>
      <dt>'\$MachinePrecision'
      <dd>is the number of decimal digits of precision for machine-precision numbers.
    </dl>

    >> $MachinePrecision
     = 15.9546
    """

    name = "$MachinePrecision"

    summary_text = (
        "get the number of decimal digits of precision for machine-precision numbers"
    )
    _is_numeric = True
    rules = {
        "$MachinePrecision": "N[MachinePrecision]",
    }


class MachinePrecision(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/MachinePrecision.html</url>
    <dl>
      <dt>'MachinePrecision'
      <dd>represents the precision of machine precision numbers.
    </dl>

    >> N[MachinePrecision]
     = 15.9546
    >> N[MachinePrecision, 30]
     = 15.9545897701910033463281614204
    """

    _is_numeric = True
    rules = {
        "N[MachinePrecision, prec_]": (
            "N[Log[10, 2] * %i, prec]" % FP_MANTISA_BINARY_DIGITS
        ),
    }

    summary_text = "symbol used to indicate machine‐number precision"


class MinPrecision(Builtin):
    r"""
    <url>
    :WMA link:https://reference.wolfram.com/language/ref/\$MinPrecision.html</url>

    <dl>
      <dt>'\$MinPrecision'
      <dd>represents the minimum number of digits of precision permitted in \
          abitrary-precision numbers.
    </dl>

    >> $MinPrecision
     = 0

    >> $MinPrecision = 10;

    >> N[Pi, 9]
     : Requested precision 9 is smaller than $MinPrecision. Using current $MinPrecision of 10. instead.
     = 3.141592654
    """

    messages = {
        "precset": "Cannot set `1` to `2`; value must be a non-negative number.",
        "preccon": "Cannot set `1` such that $MaxPrecision < $MinPrecision.",
    }

    name = "$MinPrecision"
    _is_numeric = True
    rules = {
        "$MinPrecision": "0",
    }

    summary_text = "settable global minimum precision bound"


class Precision(Builtin):
    """
    <url>
    :Precision:
    https://en.wikipedia.org/wiki/Accuracy_and_precision</url> <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Precision.html</url>

    <dl>
      <dt>'Precision'[$expr$]
      <dd>examines the number of significant digits of $expr$.
    </dl>

    <i>Note that the result could be slightly different than the obtained \
    in WMA, due to differences in the internal representation of the real numbers.</i>

    The precision of an exact number, e.g., an Integer, is 'Infinity':

    >> Precision[1]
     = Infinity

    A fraction is an exact number too, so its Precision is 'Infinity':

    >> Precision[1/2]
     = Infinity

    Numbers entered in the form $digits$`$p$ are taken to have precision $p$:

    >> Precision[1.23`10]
     = 10.

    Precision of a machine‐precision number is 'MachinePrecision':
    >> Precision[0.5]
     = MachinePrecision

    In compound expressions, the 'Precision' is fixed by the number with \
    the lowest 'Precision':
    >> Precision[{{1, 1.`20},{1.`5, 1.`10}}]
     = 5.

    A machine number makes it 'MachinePrecision':
    >> Precision[{{1, 1.`},{1.`5, 1.`10}}]
     = MachinePrecision

    In general, 'Accuracy'[$z$] == 'Precision'[$z$] + 'Log'[$z$] \
    for non-zero Real values:

    >> (Accuracy[z] == Precision[z] + Log[z])/.z-> 37.`
     = True

    Following WMA, values in Machine Real representation starting with '0.' are values are special:
    >> Precision[0.]
     = MachinePrecision

    On the other hand, for a Precision Real with fixed accuracy, the precision is evaluated to '0.':
    >> Precision[0.``3]
     = 0.


    See also <url>
    :'Accuracy':
    /doc/reference-of-built-in-symbols/atomic-elements-of-expressions/representation-of-numbers/accuracy/</url>.
    """

    eval_error = Builtin.generic_argument_error
    expected_args = 1

    summary_text = "find the precision of a number"

    def eval(self, z, evaluation: Evaluation):
        """Precision[z_]"""
        # As in WMA, a machine number anywhere in z makes it MachinePrecision.
        if has_machine_number(z):
            return SymbolMachinePrecision

        prec = eval_Precision(z)
        if prec is None:
            return SymbolInfinity
        return MachineReal(prec)


class SetAccuracy(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/SetAccuracy.html</url>

    <dl>
      <dt>'SetAccuracy'[$expr$, $a$]
      <dd>gives $expr$ with every number in it set to $a$ digits of \
          accuracy.
    </dl>

    >> SetAccuracy[150.5, 20] // Precision
     = 22.1775

    A number with no digit left becomes a zero:
    >> SetAccuracy[0.001, 2] // Accuracy
     = 2.

    'Infinity' gives the exact value of each number:
    >> SetAccuracy[0.5, Infinity]
     = 1 / 2
    """

    eval_error = Builtin.generic_argument_error
    expected_args = 2

    messages = {
        "accbd": "Requested accuracy `1` is not a real number within the allowable range.",
    }

    summary_text = "set the accuracy of the numbers in an expression"

    def eval(self, expr, accuracy, evaluation: Evaluation):
        "SetAccuracy[expr_, accuracy_]"
        if is_infinity(accuracy):
            target = float("inf")
        elif isinstance(accuracy, (Integer, Rational, Real)):
            target = float(accuracy.value)
        else:
            evaluation.message("SetAccuracy", "accbd", accuracy)
            return None
        return eval_SetAccuracy(expr, target, evaluation)


class SetPrecision(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/SetPrecision.html</url>

    <dl>
      <dt>'SetPrecision'[$expr$, $p$]
      <dd>gives $expr$ with every number in it set to $p$ digits of \
          precision.
    </dl>

    >> SetPrecision[1/3, 20]
     = 0.33333333333333333333

    An inexact number keeps its binary value:
    >> SetPrecision[0.1, 20]
     = 0.10000000000000000555

    Numeric constants are evaluated:
    >> SetPrecision[f[Pi, x], 20]
     = f[3.1415926535897932385, x]

    'Infinity' gives the exact value of each number:
    >> SetPrecision[0.1, Infinity]
     = 3602879701896397 / 36028797018963968
    """

    eval_error = Builtin.generic_argument_error
    expected_args = 2

    messages = {
        "precbd": (
            "Requested precision `1` is not a machine-sized real number "
            "between $MinPrecision and $MaxPrecision."
        ),
        "precsm": (
            "Requested precision `1` is smaller than $MinPrecision. "
            "Using $MinPrecision instead."
        ),
        "preclg": (
            "Requested precision `1` is larger than $MaxPrecision. "
            "Using $MaxPrecision instead."
        ),
    }

    summary_text = "set the precision of the numbers in an expression"

    def eval(self, expr, precision, evaluation: Evaluation):
        "SetPrecision[expr_, precision_]"
        if precision is SymbolMachinePrecision:
            target = None
        elif is_infinity(precision):
            target = float("inf")
        elif isinstance(precision, (Integer, Rational, Real)):
            target = float(precision.value)
            min_precision = get_float_inf(SymbolMinPrecision, evaluation)
            max_precision = get_float_inf(SymbolMaxPrecision, evaluation)
            if min_precision is not None and target < min_precision:
                evaluation.message("SetPrecision", "precsm", precision)
                target = min_precision
            elif max_precision is not None and target > max_precision:
                evaluation.message("SetPrecision", "preclg", precision)
                target = max_precision
        else:
            evaluation.message("SetPrecision", "precbd", precision)
            return None
        return eval_SetPrecision(expr, target, evaluation)
