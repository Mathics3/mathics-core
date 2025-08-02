# -*- coding: utf-8 -*-
"""
Basic Arithmetic

The functions here are the basic arithmetic operations that you might find \
on a calculator.

"""

from mathics.builtin.arithmetic import create_infix
from mathics.core.atoms import (
    Complex,
    Integer,
    Integer1,
    Integer3,
    Integer310,
    IntegerM1,
    Number,
    Rational,
    RationalOneHalf,
    Real,
    String,
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
from mathics.core.convert.expression import to_expression
from mathics.core.convert.sympy import from_sympy
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Symbol,
    SymbolDivide,
    SymbolHoldForm,
    SymbolNull,
    SymbolPower,
    SymbolTimes,
)
from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolComplexInfinity,
    SymbolIndeterminate,
    SymbolInfix,
    SymbolLeft,
    SymbolMinus,
    SymbolPattern,
    SymbolSequence,
)
from mathics.eval.arithfns.basic import eval_Plus, eval_Times
from mathics.eval.nevaluator import eval_N
from mathics.eval.numerify import numerify


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

    def eval(self, n, evaluation):
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

    >> -a //FullForm
     = Times[-1, a]

    'Minus' automatically distributes:
    >> -(x - 2/3)
     = 2 / 3 - x

    'Minus' threads over lists:
    >> -Range[10]
    = {-1, -2, -3, -4, -5, -6, -7, -8, -9, -10}
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

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

    def format_plus(self, items, evaluation: Evaluation):
        "Plus[items__]"

        def negate(item):  # -> Expression (see FIXME below)
            if item.has_form("Times", 2, None):
                if isinstance(item.elements[0], Number):
                    first, *rest = item.elements
                    first = -first
                    if first.sameQ(Integer1):
                        if len(rest) == 1:
                            return rest[0]
                        return Expression(SymbolTimes, *rest)

                    return Expression(SymbolTimes, first, *rest)
                else:
                    return Expression(SymbolTimes, IntegerM1, *item.elements)
            elif isinstance(item, Number):
                return from_sympy(-item.to_sympy())
            else:
                return Expression(SymbolTimes, IntegerM1, item)

        def is_negative(value) -> bool:
            if isinstance(value, Complex):
                real, imag = value.to_sympy().as_real_imag()
                if real <= 0 and imag <= 0:
                    return True
            elif isinstance(value, Number) and value.to_sympy() < 0:
                return True
            return False

        elements = items.get_sequence()
        values = [to_expression(SymbolHoldForm, element) for element in elements[:1]]
        ops = []
        for element in elements[1:]:
            if (
                element.has_form("Times", 1, None) and is_negative(element.elements[0])
            ) or is_negative(element):
                element = negate(element)
                op = "-"
            else:
                op = "+"
            values.append(Expression(SymbolHoldForm, element))
            ops.append(String(op))
        return Expression(
            SymbolInfix,
            ListExpression(*values),
            ListExpression(*ops),
            Integer310,
            SymbolLeft,
        )

    def eval(self, items, evaluation: Evaluation):
        "Plus[items___]"
        items_tuple = numerify(items, evaluation).get_sequence()
        return eval_Plus(*items_tuple)


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
        if result is None or result != SymbolNull:
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

    summary_text = "multiply a number"

    def format_times(self, items, evaluation, op="\u2062"):
        "Times[items__]"

        def inverse(item):
            if item.has_form("Power", 2) and isinstance(  # noqa
                item.elements[1], (Integer, Rational, Real)
            ):
                neg = -item.elements[1]
                if neg.sameQ(Integer1):
                    return item.elements[0]
                else:
                    return Expression(SymbolPower, item.elements[0], neg)
            else:
                return item

        items = items.get_sequence()
        if len(items) < 2:
            return
        positive = []
        negative = []
        for item in items:
            if (
                item.has_form("Power", 2)
                and isinstance(item.elements[1], (Integer, Rational, Real))
                and item.elements[1].to_sympy() < 0
            ):  # nopep8
                negative.append(inverse(item))
            elif isinstance(item, Rational):
                numerator = item.numerator()
                if not numerator.sameQ(Integer1):
                    positive.append(numerator)
                negative.append(item.denominator())
            else:
                positive.append(item)
        if positive and positive[0].get_int_value() == -1:
            del positive[0]
            minus = True
        else:
            minus = False
        positive = [Expression(SymbolHoldForm, item) for item in positive]
        negative = [Expression(SymbolHoldForm, item) for item in negative]
        if positive:
            positive = create_infix(positive, op, 400, "None")
        else:
            positive = Integer1
        if negative:
            negative = create_infix(negative, op, 400, "None")
            result = Expression(
                SymbolDivide,
                Expression(SymbolHoldForm, positive),
                Expression(SymbolHoldForm, negative),
            )
        else:
            result = positive
        if minus:
            result = Expression(
                SymbolMinus, result
            )  # Expression('PrecedenceForm', result, 481))
        result = Expression(SymbolHoldForm, result)
        return result

    def format_inputform(self, items, evaluation):
        "(InputForm,): Times[items__]"
        return self.format_times(items, evaluation, op="*")

    def format_standardform(self, items, evaluation):
        "(StandardForm,): Times[items__]"
        return self.format_times(items, evaluation, op=" ")

    def format_outputform(self, items, evaluation):
        "(OutputForm,): Times[items__]"
        return self.format_times(items, evaluation, op=" ")

    def eval(self, items, evaluation):
        "Times[items___]"
        items = numerify(items, evaluation).get_sequence()
        return eval_Times(*items)
