# -*- coding: utf-8 -*-
"""
Basic Arithmetic

The functions here are the basic arithmetic operations that you might find on a calculator.

"""


import sympy
import mpmath

from mathics.builtin.arithmetic import _MPMathFunction, create_infix
from mathics.core.evaluators import eval_N
from mathics.builtin.base import (
    Builtin,
    BinaryOperator,
    PrefixOperator,
    SympyFunction,
)
from mathics.core.atoms import (
    Complex,
    Integer,
    Integer0,
    Integer1,
    Integer2,
    Integer3,
    Integer310,
    IntegerM1,
    Number,
    Rational,
    Real,
    String,
)
from mathics.core.convert.expression import to_expression
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.expression import ElementsProperties, Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Symbol,
    SymbolDivide,
    SymbolHoldForm,
    SymbolNull,
    SymbolPlus,
    SymbolPower,
    SymbolTimes,
)
from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolComplexInfinity,
    SymbolDirectedInfinity,
    SymbolIndeterminate,
    SymbolInfinity,
    SymbolInfix,
    SymbolLeft,
    SymbolMinus,
    SymbolPattern,
    SymbolSequence,
)
from mathics.core.number import min_prec, dps

from mathics.core.convert.sympy import from_sympy

from mathics.core.attributes import (
    flat,
    listable,
    numeric_function,
    one_identity,
    orderless,
    protected,
    read_protected,
)


class CubeRoot(Builtin):
    """
    <dl>
      <dt>'CubeRoot[$n$]'
      <dd>finds the real-valued cube root of the given $n$.
    </dl>

    >> CubeRoot[16]
     = 2 2 ^ (1 / 3)

    #> CubeRoot[-5]
     = -5 ^ (1 / 3)

    #> CubeRoot[-510000]
     = -10 510 ^ (1 / 3)

    #> CubeRoot[-5.1]
     = -1.7213

    #> CubeRoot[b]
     = b ^ (1 / 3)

    #> CubeRoot[-0.5]
     = -0.793701

    #> CubeRoot[3 + 4 I]
     : The parameter 3 + 4 I should be real valued.
     = (3 + 4 I) ^ (1 / 3)
    """

    attributes = listable | numeric_function | protected | read_protected

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

    summary_text = "cubed root"

    def apply(self, n, evaluation):
        "CubeRoot[n_Complex]"

        evaluation.message("CubeRoot", "preal", n)
        return Expression(
            SymbolPower,
            n,
            Expression(
                SymbolDivide,
                Integer1,
                Integer3,
                elements_properties=ElementsProperties(True, True, True),
            ),
        )


class Divide(BinaryOperator):
    """
    <dl>
    <dt>'Divide[$a$, $b$]'
    <dt>'$a$ / $b$'
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

    #> 1 / 4.0
     = 0.25
    #> 10 / 3 // FullForm
     = Rational[10, 3]
    #> a / b // FullForm
     = Times[a, Power[b, -1]]

    """

    operator = "/"
    precedence = 470
    attributes = listable | numeric_function | protected
    grouping = "Left"

    default_formats = False

    rules = {
        "Divide[x_, y_]": "Times[x, Power[y, -1]]",
        "MakeBoxes[Divide[x_, y_], f:StandardForm|TraditionalForm]": (
            "FractionBox[MakeBoxes[x, f], MakeBoxes[y, f]]"
        ),
    }

    formats = {
        (("InputForm", "OutputForm"), "Divide[x_, y_]"): (
            'Infix[{HoldForm[x], HoldForm[y]}, "/", 400, Left]'
        ),
    }

    summary_text = r"division"


class Minus(PrefixOperator):
    """
    <dl>
    <dt>'Minus[$expr$]'
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

    operator = "-"
    precedence = 480
    attributes = listable | numeric_function | protected

    rules = {
        "Minus[x_]": "Times[-1, x]",
    }

    formats = {
        "Minus[x_]": 'Prefix[{HoldForm[x]}, "-", 480]',
        # don't put e.g. -2/3 in parentheses
        "Minus[expr_Divide]": 'Prefix[{HoldForm[expr]}, "-", 399]',
        "Minus[Infix[expr_, op_, 400, grouping_]]": (
            'Prefix[{Infix[expr, op, 400, grouping]}, "-", 399]'
        ),
    }

    summary_text = "arithmetic negation"

    def apply_int(self, x: Integer, evaluation):
        "Minus[x_Integer]"
        return Integer(-x.value)


class Plus(BinaryOperator, SympyFunction):
    """
    <dl>
    <dt>'Plus[$a$, $b$, ...]'
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

    #> -2a - 2b
     = -2 a - 2 b
    #> -4+2x+2*Sqrt[3]
     = -4 + 2 Sqrt[3] + 2 x
    #> 2a-3b-c
     = 2 a - 3 b - c
    #> 2a+5d-3b-2c-e
     = 2 a - 3 b - 2 c + 5 d - e

    #> 1 - I * Sqrt[3]
     = 1 - I Sqrt[3]

    #> Head[3 + 2 I]
     = Complex

    #> N[Pi, 30] + N[E, 30]
     = 5.85987448204883847382293085463
    #> % // Precision
     = 30.
    """

    operator = "+"
    precedence = 310
    attributes = (
        flat | listable | numeric_function | one_identity | orderless | protected
    )

    default_formats = False

    defaults = {
        None: "0",
    }

    summary_text = "addition of numbers, lists, arrays, or symbolic expressions"
    sympy_name = "Add"

    def format_plus(self, items, evaluation):
        "Plus[items__]"

        def negate(item):  # -> Expression (see FIXME below)
            if item.has_form("Times", 1, None):
                if isinstance(item.elements[0], Number):
                    neg = -item.elements[0]
                    if neg.sameQ(Integer1):
                        if len(item.elements) == 1:
                            return neg
                        else:
                            return Expression(SymbolTimes, *item.elements[1:])
                    else:
                        return Expression(SymbolTimes, neg, *item.elements[1:])
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

    def apply(self, items, evaluation):
        "Plus[items___]"

        items = items.numerify(evaluation).get_sequence()
        elements = []
        last_item = last_count = None

        prec = min_prec(*items)
        is_machine_precision = any(item.is_machine_precision() for item in items)
        numbers = []

        def append_last():
            if last_item is not None:
                if last_count == 1:
                    elements.append(last_item)
                else:
                    if last_item.has_form("Times", None):
                        elements.append(
                            Expression(
                                SymbolTimes, from_sympy(last_count), *last_item.elements
                            )
                        )
                    else:
                        elements.append(
                            Expression(SymbolTimes, from_sympy(last_count), last_item)
                        )

        for item in items:
            if isinstance(item, Number):
                numbers.append(item)
            else:
                count = rest = None
                if item.has_form("Times", None):
                    for element in item.elements:
                        if isinstance(element, Number):
                            count = element.to_sympy()
                            rest = item.get_mutable_elements()
                            rest.remove(element)
                            if len(rest) == 1:
                                rest = rest[0]
                            else:
                                rest.sort()
                                rest = Expression(SymbolTimes, *rest)
                            break
                if count is None:
                    count = sympy.Integer(1)
                    rest = item
                if last_item is not None and last_item == rest:
                    last_count = last_count + count
                else:
                    append_last()
                    last_item = rest
                    last_count = count
        append_last()

        if numbers:
            if prec is not None:
                if is_machine_precision:
                    numbers = [item.to_mpmath() for item in numbers]
                    number = mpmath.fsum(numbers)
                    number = from_mpmath(number)
                else:
                    with mpmath.workprec(prec):
                        numbers = [item.to_mpmath() for item in numbers]
                        number = mpmath.fsum(numbers)
                        number = from_mpmath(number, dps(prec))
            else:
                number = from_sympy(sum(item.to_sympy() for item in numbers))
        else:
            number = Integer0

        if not number.sameQ(Integer0):
            elements.insert(0, number)

        if not elements:
            return Integer0
        elif len(elements) == 1:
            return elements[0]
        else:
            elements.sort()
            return Expression(SymbolPlus, *elements)


class Power(BinaryOperator, _MPMathFunction):
    """
    <dl>
    <dt>'Power[$a$, $b$]'
    <dt>'$a$ ^ $b$'
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

    #> 1/0
     : Infinite expression 1 / 0 encountered.
     = ComplexInfinity
    #> 0 ^ -2
     : Infinite expression 1 / 0 ^ 2 encountered.
     = ComplexInfinity
    #> 0 ^ (-1/2)
     : Infinite expression 1 / Sqrt[0] encountered.
     = ComplexInfinity
    #> 0 ^ -Pi
     : Infinite expression 1 / 0 ^ 3.14159 encountered.
     = ComplexInfinity
    #> 0 ^ (2 I E)
     : Indeterminate expression 0 ^ (0. + 5.43656 I) encountered.
     = Indeterminate
    #> 0 ^ - (Pi + 2 E I)
     : Infinite expression 0 ^ (-3.14159 - 5.43656 I) encountered.
     = ComplexInfinity

    #> 0 ^ 0
     : Indeterminate expression 0 ^ 0 encountered.
     = Indeterminate

    #> Sqrt[-3+2. I]
     = 0.550251 + 1.81735 I
    #> Sqrt[-3+2 I]
     = Sqrt[-3 + 2 I]
    #> (3/2+1/2I)^2
     = 2 + 3 I / 2
    #> I ^ I
     = (-1) ^ (I / 2)

    #> 2 ^ 2.0
     = 4.

    #> Pi ^ 4.
     = 97.4091

    #> a ^ b
     = a ^ b
    """

    operator = "^"
    precedence = 590
    attributes = listable | numeric_function | one_identity | protected
    grouping = "Right"

    default_formats = False

    sympy_name = "Pow"
    mpmath_name = "power"
    nargs = {2}

    messages = {
        "infy": "Infinite expression `1` encountered.",
        "indet": "Indeterminate expression `1` encountered.",
    }

    defaults = {
        2: "1",
    }

    formats = {
        Expression(
            SymbolPower,
            Expression(SymbolPattern, Symbol("x"), Expression(SymbolBlank)),
            Rational(1, 2),
        ): "HoldForm[Sqrt[x]]",
        (("InputForm", "OutputForm"), "x_ ^ y_"): (
            'Infix[{HoldForm[x], HoldForm[y]}, "^", 590, Right]'
        ),
        ("", "x_ ^ y_"): (
            "PrecedenceForm[Superscript[OuterPrecedenceForm[HoldForm[x], 590],"
            "  HoldForm[y]], 590]"
        ),
        ("", "x_ ^ y_?Negative"): (
            "HoldForm[Divide[1, #]]&[If[y==-1, HoldForm[x], HoldForm[x]^-y]]"
        ),
        ("", "x_?Negative ^ y_"): (
            'Infix[{HoldForm[(x)], HoldForm[y]},"^", 590, Right]'
        ),
    }

    rules = {
        "Power[]": "1",
        "Power[x_]": "x",
    }

    summary_text = "exponentiation"

    def apply_check(self, x, y, evaluation):
        "Power[x_, y_]"

        # Power uses _MPMathFunction but does some error checking first
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
            yhalf = Expression(SymbolTimes, y, Rational(1, 2))
            factor = self.apply(Expression(SymbolSequence, x.imag, y), evaluation)
            return Expression(
                SymbolTimes, factor, Expression(SymbolPower, IntegerM1, yhalf)
            )

        result = self.apply(Expression(SymbolSequence, x, y), evaluation)
        if result is None or result != SymbolNull:
            return result


class Sqrt(SympyFunction):
    """
    <dl>
    <dt>'Sqrt[$expr$]'
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

    #> N[Sqrt[2], 50]
     = 1.4142135623730950488016887242096980785696718753769
    """

    attributes = listable | numeric_function | protected

    rules = {
        "Sqrt[x_]": "x ^ (1/2)",
        "MakeBoxes[Sqrt[x_], f:StandardForm|TraditionalForm]": (
            "SqrtBox[MakeBoxes[x, f]]"
        ),
    }

    summary_text = "square root"


class Subtract(BinaryOperator):
    """
    <dl>
    <dt>'Subtract[$a$, $b$]'
    <dt>$a$ - $b$
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

    operator = "-"
    precedence_parse = 311
    precedence = 310
    attributes = listable | numeric_function | protected
    grouping = "Left"

    rules = {
        "Subtract[x_, y_]": "Plus[x, Times[-1, y]]",
    }

    summary_text = "subtraction"


class Times(BinaryOperator, SympyFunction):
    """
    <dl>
    <dt>'Times[$a$, $b$, ...]'
    <dt>'$a$ * $b$ * ...'
    <dt>'$a$ $b$ ...'
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

    #> -a*b // FullForm
     = Times[-1, a, b]
    #> -(x - 2/3)
     = 2 / 3 - x
    #> -x*2
     = -2 x
    #> -(h/2) // FullForm
     = Times[Rational[-1, 2], h]

    #> x / x
     = 1
    #> 2x^2 / x^2
     = 2

    #> 3. Pi
     = 9.42478

    #> Head[3 * I]
     = Complex

    #> Head[Times[I, 1/2]]
     = Complex

    #> Head[Pi * I]
     = Times

    #> 3 * a //InputForm
     = 3*a
    #> 3 * a //OutputForm
     = 3 a

    #> -2.123456789 x
     = -2.12346 x
    #> -2.123456789 I
     = 0. - 2.12346 I

    #> N[Pi, 30] * I
     = 3.14159265358979323846264338328 I
    #> N[I Pi, 30]
     = 3.14159265358979323846264338328 I

    #> N[Pi * E, 30]
     = 8.53973422267356706546355086955
    #> N[Pi, 30] * N[E, 30]
     = 8.53973422267356706546355086955
    #> N[Pi, 30] * E
     = 8.53973422267356706546355086955
    #> % // Precision
     = 30.
    """

    operator = "*"
    operator_display = " "
    precedence = 400
    attributes = (
        flat | listable | numeric_function | one_identity | orderless | protected
    )

    defaults = {
        None: "1",
    }

    default_formats = False

    formats = {}

    rules = {}

    sympy_name = "Mul"

    summary_text = "mutiplication"

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
        "InputForm: Times[items__]"
        return self.format_times(items, evaluation, op="*")

    def format_standardform(self, items, evaluation):
        "StandardForm: Times[items__]"
        return self.format_times(items, evaluation, op=" ")

    def format_outputform(self, items, evaluation):
        "OutputForm: Times[items__]"
        return self.format_times(items, evaluation, op=" ")

    def apply(self, items, evaluation):
        "Times[items___]"
        items = items.numerify(evaluation).get_sequence()
        elements = []
        numbers = []
        infinity_factor = False

        prec = min_prec(*items)
        is_machine_precision = any(item.is_machine_precision() for item in items)

        # find numbers and simplify Times -> Power
        for item in items:
            if isinstance(item, Number):
                numbers.append(item)
            elif elements and item == elements[-1]:
                elements[-1] = Expression(SymbolPower, elements[-1], Integer2)
            elif (
                elements
                and item.has_form("Power", 2)
                and elements[-1].has_form("Power", 2)
                and item.elements[0].sameQ(elements[-1].elements[0])
            ):
                elements[-1] = Expression(
                    SymbolPower,
                    elements[-1].elements[0],
                    Expression(SymbolPlus, item.elements[1], elements[-1].elements[1]),
                )
            elif (
                elements
                and item.has_form("Power", 2)
                and item.elements[0].sameQ(elements[-1])
            ):
                elements[-1] = Expression(
                    SymbolPower,
                    elements[-1],
                    Expression(SymbolPlus, item.elements[1], Integer1),
                )
            elif (
                elements
                and elements[-1].has_form("Power", 2)
                and elements[-1].elements[0].sameQ(item)
            ):
                elements[-1] = Expression(
                    SymbolPower,
                    item,
                    Expression(SymbolPlus, Integer1, elements[-1].elements[1]),
                )
            elif item.get_head().sameQ(SymbolDirectedInfinity):
                infinity_factor = True
                if len(item.elements) > 1:
                    direction = item.elements[0]
                    if isinstance(direction, Number):
                        numbers.append(direction)
                    else:
                        elements.append(direction)
            elif item.sameQ(SymbolInfinity) or item.sameQ(SymbolComplexInfinity):
                infinity_factor = True
            else:
                elements.append(item)

        if numbers:
            if prec is not None:
                if is_machine_precision:
                    numbers = [item.to_mpmath() for item in numbers]
                    number = mpmath.fprod(numbers)
                    number = from_mpmath(number)
                else:
                    with mpmath.workprec(prec):
                        numbers = [item.to_mpmath() for item in numbers]
                        number = mpmath.fprod(numbers)
                        number = from_mpmath(number, dps(prec))
            else:
                number = sympy.Mul(*[item.to_sympy() for item in numbers])
                number = from_sympy(number)
        else:
            number = Integer1

        if number.sameQ(Integer1):
            number = None
        elif number.is_zero:
            if infinity_factor:
                return SymbolIndeterminate
            return number
        elif (
            number.sameQ(IntegerM1) and elements and elements[0].has_form("Plus", None)
        ):
            elements[0] = Expression(
                elements[0].get_head(),
                *[
                    Expression(SymbolTimes, IntegerM1, element)
                    for element in elements[0].elements
                ],
            )
            number = None

        if number is not None:
            elements.insert(0, number)

        if not elements:
            if infinity_factor:
                return SymbolComplexInfinity
            return Integer1

        if len(elements) == 1:
            ret = elements[0]
        else:
            ret = Expression(SymbolTimes, *elements)
        if infinity_factor:
            return Expression(SymbolDirectedInfinity, ret)
        else:
            return ret
