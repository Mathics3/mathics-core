# -*- coding: utf-8 -*-
"""
Basic Arithmetic

The functions here are the basic arithmetic operations that you might find \
on a calculator.

"""

from mathics.core.atoms import (
    Complex,
    Integer,
    Integer1,
    Integer3,
    IntegerM1,
    Number,
    RationalOneHalf,
)
from mathics.core.attributes import (
    A_FLAT,
    A_LISTABLE,
    A_NUMERIC_FUNCTION,
    A_ONE_IDENTITY,
    A_ORDERLESS,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import (
    Builtin,
    InfixOperator,
    MPMathFunction,
    PrefixOperator,
    SympyFunction,
)
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolNull, SymbolPower, SymbolTimes
from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolComplexInfinity,
    SymbolIndeterminate,
    SymbolPattern,
    SymbolSequence,
)
from mathics.eval.arithfns.basic import eval_Plus, eval_Times
from mathics.eval.nevaluator import eval_N
from mathics.eval.numerify import numerify
from mathics.format.form_rule.arithfns import format_plus, format_times


class CubeRoot(Builtin):
    """
    <url>
    :Cube root:
    https://en.wikipedia.org/wiki/Cube_root</url> (<url> :WMA:
    https://reference.wolfram.com/language/ref/CubeRoot.html</url>)

    <dl>
      <dt>'CubeRoot'[$n$]
      <dd>finds the real-valued cube root of the given $n$.
    </dl>

    >> CubeRoot[16]
     = 2 2 ^ (1 / 3)
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED

    # Set checking that the number of arguments required is one.
    eval_error = Builtin.generic_argument_error
    expected_args = 1

    messages = {
        "preal": "The parameter `1` should be real valued.",
    }

    rules = {
        "CubeRoot[n_?NumberQ]": "If[n > 0, Power[n, Divide[1, 3]], Times[-1, Power[Times[-1, n], Divide[1, 3]]]]",
        "CubeRoot[n_]": "Power[n, Divide[1, 3]]",
        "MakeBoxes[CubeRoot[x_], f:StandardForm|TraditionalForm]": (
            "RadicalBox[MakeBoxes[x, f], 3]"
        ),
    }

    summary_text = "compute cube root of a number"

    def eval(self, n, evaluation: Evaluation):
        "CubeRoot[n_Complex]"

        evaluation.message("CubeRoot", "preal", n)
        return Expression(
            SymbolPower,
            n,
            Integer1 / Integer3,
        )


class Divide(InfixOperator):
    """
    <url>
    :Division:
    https://en.wikipedia.org/wiki/Division_(mathematics)</url> (<url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Divide.html</url>)

    <dl>
      <dt>'Divide'[$a$, $b$]
      <dt> $a$ '/' $b$
      <dd>represents the division of $a$ by $b$.
    </dl>

    >> 30 / 5
     = 6
    >> 1 / 8
     = 1 / 8
    >> Pi / 4
     = Pi / 4

    Use 'N' or a decimal point to force numeric evaluation:
    >> Pi / 4.0
     = 0.785398
    >> 1 / 8
     = 1 / 8
    >> N[%]
     = 0.125

    Nested divisions:
    >> a / b / c
     = a / (b c)
    >> a / (b / c)
     = a c / b
    >> a / b / (c / (d / e))
     = a d / (b c e)
    >> a / (b ^ 2 * c ^ 3 / e)
     = a e / (b ^ 2 c ^ 3)
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    default_formats = False

    # Set checking that the number of arguments required is two.
    eval_error = Builtin.generic_argument_error
    expected_args = 2

    formats = {
        (("InputForm", "OutputForm"), "Divide[x_, y_]"): (
            'Infix[{HoldForm[x], HoldForm[y]}, "/", 400, Left]'
        ),
    }

    grouping = "Left"

    rules = {
        "Divide[x_, y_]": "Times[x, Power[y, -1]]",
        "MakeBoxes[Divide[x_, y_], f:StandardForm|TraditionalForm]": (
            "FractionBox[MakeBoxes[x, f], MakeBoxes[y, f]]"
        ),
    }

    summary_text = "divide a number"


class Minus(PrefixOperator):
    """
    <url>
    :Additive inverse:
    https://en.wikipedia.org/wiki/Additive_inverse</url> (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/Minus.html</url>)

    <dl>
      <dt>'Minus'[$expr$]
      <dd> is the negation of $expr$.
    </dl>

    >> -a // FullForm
     = Times[-1, a]

    'Minus' automatically distributes:
    >> -(x - 2/3)
     = 2 / 3 - x

    'Minus' threads over lists:
    >> -Range[10]
    = {-1, -2, -3, -4, -5, -6, -7, -8, -9, -10}
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    # Set checking that the number of arguments required is two.
    eval_error = Builtin.generic_argument_error
    expected_args = 1

    formats = {
        "Minus[x_]": 'Prefix[{HoldForm[x]}, "-", 480]',
        # don't put e.g. -2/3 in parentheses
        "Minus[expr_Divide]": 'Prefix[{HoldForm[expr]}, "-", 399]',
        "Minus[Infix[expr_, op_, 400, grouping_]]": (
            'Prefix[{Infix[expr, op, 400, grouping]}, "-", 399]'
        ),
    }

    rules = {
        "Minus[x_]": "Times[-1, x]",
    }

    summary_text = "perform an arithmetic negation on a number"

    def eval_int(self, x: Integer, evaluation):
        "Minus[x_Integer]"
        return Integer(-x.value)


class Plus(InfixOperator, SympyFunction):
    """
    <url>
    :Addition:
    https://en.wikipedia.org/wiki/Addition</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/core.html#id48</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Plus.html</url>)

    <dl>
      <dt>'Plus'[$a$, $b$, ...]
      <dt>$a$ + $b$ + ...
      <dd>represents the sum of the terms $a$, $b$, ...
    </dl>

    >> 1 + 2
     = 3

    'Plus' performs basic simplification of terms:

    >> a + b + a
     = 2 a + b
    >> a + a + 3 * a
     = 5 a
    >> a + b + 4.5 + a + b + a + 2 + 1.5 b
     = 6.5 + 3 a + 3.5 b

    Apply 'Plus' on a list to sum up its elements:
    >> Plus @@ {2, 4, 6}
     = 12
    The sum of the first 1000 integers:
    >> Plus @@ Range[1000]
     = 500500

    'Plus' has default value 0:
    >> DefaultValues[Plus]
     = {HoldPattern[Default[Plus]] :> 0}
    >> a /. n_. + x_ :> {n, x}
     = {0, a}

    The sum of 2 red circles and 3 red circles is...
    >> 2 Graphics[{Red,Disk[]}] + 3 Graphics[{Red,Disk[]}]
     = 5 -Graphics-
    """

    attributes = (
        A_FLAT
        | A_LISTABLE
        | A_NUMERIC_FUNCTION
        | A_ONE_IDENTITY
        | A_ORDERLESS
        | A_PROTECTED
    )

    default_formats = False

    defaults = {
        None: "0",
    }

    summary_text = "add a number"

    # FIXME Note this is deprecated in 1.11
    # Remember to up sympy doc link when this is corrected
    sympy_name = "Add"

    def eval(self, elements, evaluation: Evaluation):
        "Plus[elements___]"
        elements_tuple = numerify(elements, evaluation).get_sequence()
        return eval_Plus(*elements_tuple)

    def format_plus(self, items, evaluation: Evaluation):
        "Plus[items__]"
        return format_plus(items, evaluation)


class Power(InfixOperator, MPMathFunction):
    """
    <url>
    :Exponentiation:
    https://en.wikipedia.org/wiki/Exponentiation</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/core.html#sympy.core.power.Pow</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Power.html</url>)

    <dl>
      <dt>'Power'[$a$, $b$]
      <dt>$a$ '^' $b$
      <dd>represents $a$ raised to the power of $b$.
    </dl>

    >> 4 ^ (1/2)
     = 2
    >> 4 ^ (1/3)
     = 2 ^ (2 / 3)
    >> 3^123
     = 48519278097689642681155855396759336072749841943521979872827

    >> (y ^ 2) ^ (1/2)
     = Sqrt[y ^ 2]
    >> (y ^ 2) ^ 3
     = y ^ 6

    >> Plot[Evaluate[Table[x^y, {y, 1, 5}]], {x, -1.5, 1.5}, AspectRatio -> 1]
     = -Graphics-

    Use a decimal point to force numeric evaluation:
    >> 4.0 ^ (1/3)
     = 1.5874

    'Power' has default value 1 for its second argument:
    >> DefaultValues[Power]
     = {HoldPattern[Default[Power, 2]] :> 1}
    >> a /. x_ ^ n_. :> {x, n}
     = {a, 1}

    'Power' can be used with complex numbers:
    >> (1.5 + 1.0 I) ^ 3.5
     = -3.68294 + 6.95139 I
    >> (1.5 + 1.0 I) ^ (3.5 + 1.5 I)
     = -3.19182 + 0.645659 I
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_ONE_IDENTITY | A_PROTECTED
    default_formats = False

    defaults = {
        2: "1",
    }

    formats = {
        Expression(
            SymbolPower,
            Expression(SymbolPattern, Symbol("x"), Expression(SymbolBlank)),
            RationalOneHalf,
        ): "HoldForm[Sqrt[x]]",
        (("InputForm", "OutputForm"), "x_ ^ y_"): (
            'Infix[{HoldForm[x], HoldForm[y]}, "^", 590, Right]'
        ),
        ("", "x_ ^ y_"): (
            "PrecedenceForm[Superscript[PrecedenceForm[HoldForm[x], 590],"
            "  HoldForm[y]], 590]"
        ),
        ("", "x_ ^ y_?Negative"): (
            "HoldForm[Divide[1, #]]&[If[y==-1, HoldForm[x], HoldForm[x]^-y]]"
        ),
        ("", "x_?Negative ^ y_"): (
            'Infix[{HoldForm[(x)], HoldForm[y]},"^", 590, Right]'
        ),
    }

    grouping = "Right"

    mpmath_name = "power"

    messages = {
        "infy": "Infinite expression `1` encountered.",
        "indet": "Indeterminate expression `1` encountered.",
    }

    nargs = {2}
    rules = {
        "Power[]": "1",
        "Power[x_]": "x",
    }

    summary_text = "exponentiate a number"

    # FIXME Note this is deprecated in 1.11
    # Remember to up sympy doc link when this is corrected
    sympy_name = "Pow"

    def eval_check(self, x, y, evaluation: Evaluation):
        "Power[x_, y_]"

        # Power uses MPMathFunction but does some error checking first
        if isinstance(x, Number) and x.is_zero:
            if isinstance(y, Number):
                y_err = y
            else:
                y_err = eval_N(y, evaluation)
            if isinstance(y_err, Number):
                py_y = y_err.round_to_float(permit_complex=True).real
                if py_y > 0:
                    return x
                elif py_y == 0.0:
                    evaluation.message(
                        "Power", "indet", Expression(SymbolPower, x, y_err)
                    )
                    return SymbolIndeterminate
                elif py_y < 0:
                    evaluation.message(
                        "Power", "infy", Expression(SymbolPower, x, y_err)
                    )
                    return SymbolComplexInfinity
        if isinstance(x, Complex) and x.real.is_zero:
            yhalf = Expression(SymbolTimes, y, RationalOneHalf)
            factor = self.eval(Expression(SymbolSequence, x.imag, y), evaluation)
            return Expression(
                SymbolTimes, factor, Expression(SymbolPower, IntegerM1, yhalf)
            )

        result = self.eval(Expression(SymbolSequence, x, y), evaluation)
        if result is None or result is not SymbolNull:
            return result


class Sqrt(SympyFunction):
    """
    <url>
    :Square root:
    https://en.wikipedia.org/wiki/Square_root</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/codegen.html#sympy.codegen.cfunctions.Sqrt</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Sqrt.html</url>)

    <dl>
      <dt>'Sqrt'[$expr$]
      <dd>returns the square root of $expr$.
    </dl>

    >> Sqrt[4]
     = 2
    >> Sqrt[5]
     = Sqrt[5]
    >> Sqrt[5] // N
     = 2.23607
    >> Sqrt[a]^2
     = a

    Complex numbers:
    >> Sqrt[-4]
     = 2 I
    >> I == Sqrt[-1]
     = True

    >> Plot[Sqrt[a^2], {a, -2, 2}]
     = -Graphics-
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    # Set checking that the number of arguments required is one.
    eval_error = Builtin.generic_argument_error
    expected_args = 1

    rules = {
        "Sqrt[x_]": "x ^ (1/2)",
        "MakeBoxes[Sqrt[x_], f:StandardForm|TraditionalForm]": (
            "SqrtBox[MakeBoxes[x, f]]"
        ),
    }

    summary_text = "take the square root of a number"


class Subtract(InfixOperator):
    """
    <url>
    :Subtraction:
    https://en.wikipedia.org/wiki/Subtraction</url>, (<url>:WMA:
    https://reference.wolfram.com/language/ref/Subtract.html</url>)

    <dl>
      <dt>'Subtract'[$a$, $b$]
      <dt>$a$ '-' $b$
      <dd>represents the subtraction of $b$ from $a$.
    </dl>

    >> 5 - 3
     = 2
    >> a - b // FullForm
     = Plus[a, Times[-1, b]]
    >> a - b - c
     = a - b - c
    >> a - (b - c)
     = a - b + c
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    # Set checking that the number of arguments required is two.
    eval_error = Builtin.generic_argument_error
    expected_args = 2

    grouping = "Left"

    rules = {
        "Subtract[x_, y_]": "Plus[x, Times[-1, y]]",
    }

    summary_text = "subtract from a number"


class Times(InfixOperator, SympyFunction):
    """
    <url>
    :Multiplication:
    https://en.wikipedia.org/wiki/Multiplication</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/core.html#sympy.core.mul.Mul</url>, <url>
    :WMA:https://reference.wolfram.com/language/ref/Times.html</url>)

    <dl>
      <dt>'Times'[$a$, $b$, ...]
      <dt>$a$ '*' $b$ '*' ...
      <dt>$a$ $b$ ...
      <dd>represents the product of the terms $a$, $b$, ...
    </dl>

    >> 10 * 2
     = 20
    >> 10 2
     = 20
    >> a * a
     = a ^ 2
    >> x ^ 10 * x ^ -2
     = x ^ 8
    >> {1, 2, 3} * 4
     = {4, 8, 12}
    >> Times @@ {1, 2, 3, 4}
     = 24
    >> IntegerLength[Times@@Range[5000]]
     = 16326

    'Times' has default value 1:
    >> DefaultValues[Times]
     = {HoldPattern[Default[Times]] :> 1}
    >> a /. n_. * x_ :> {n, x}
     = {1, a}
    """

    attributes = (
        A_FLAT
        | A_LISTABLE
        | A_NUMERIC_FUNCTION
        | A_ONE_IDENTITY
        | A_ORDERLESS
        | A_PROTECTED
    )

    defaults = {
        None: "1",
    }

    default_formats = False

    formats = {}

    operator_display = " "

    rules = {}

    # FIXME Note this is deprecated in 1.11
    # Remember to up sympy doc link when this is corrected
    sympy_name = "Mul"

    summary_text = "multiply numbers"

    def eval(self, elements, evaluation: Evaluation):
        "Times[elements___]"
        numeric_elements = numerify(elements, evaluation).get_sequence()
        return eval_Times(*numeric_elements)

    def format_times(self, items, evaluation: Evaluation, op="\u2062"):
        "Times[items__]"
        return format_times(items, evaluation, op)

    def format_inputform(self, items, evaluation):
        "(InputForm,): Times[items__]"
        return format_times(items, evaluation, op="*")

    def format_standardform(self, items, evaluation):
        "(StandardForm,): Times[items__]"
        return format_times(items, evaluation, op=" ")

    def format_outputform(self, items, evaluation):
        "(OutputForm,): Times[items__]"
        return format_times(items, evaluation, op=" ")
