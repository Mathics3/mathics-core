# -*- coding: utf-8 -*-
"""
Basic Arithmetic

The functions here are the basic arithmetic operations that you might find \
on a calculator.

"""
from mathics.builtin.arithmetic import create_infix
from mathics.builtin.base import (
    BinaryOperator,
    Builtin,
    MPMathFunction,
    PrefixOperator,
    SympyFunction,
)
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
from mathics.core.convert.expression import to_expression
from mathics.core.convert.sympy import from_sympy
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
    SymbolFractionBox,
    SymbolI,
    SymbolIndeterminate,
    SymbolInfix,
    SymbolInputForm,
    SymbolLeft,
    SymbolMakeBoxes,
    SymbolMinus,
    SymbolOutputForm,
    SymbolPattern,
    SymbolPrecedenceForm,
    SymbolRowBox,
    SymbolSequence,
    SymbolStandardForm,
    SymbolTraditionalForm,
)
from mathics.eval.arithmetic import eval_Plus, eval_Times
from mathics.eval.makeboxes import (
    builtins_precedence,
    do_format_complex,
    eval_makeboxes,
    parenthesize,
)
from mathics.eval.nevaluator import eval_N
from mathics.eval.numerify import numerify


class CubeRoot(Builtin):
    """
    <url>
    :Cube root:
    https://en.wikipedia.org/wiki/Cube_root</url> (<url> :WMA:
    https://reference.wolfram.com/language/ref/CubeRoot.html</url>)

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

    summary_text = "cube root"

    def eval(self, n, evaluation):
        "CubeRoot[n_Complex]"

        evaluation.message("CubeRoot", "preal", n)
        return Expression(
            SymbolPower,
            n,
            Integer1 / Integer3,
        )


class Divide(BinaryOperator):
    """
    <url>
    :Division:
    https://en.wikipedia.org/wiki/Division_(mathematics)</url> (<url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Divide.html</url>)

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

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    default_formats = False

    formats = {
        ("InputForm", "Divide[x_, y_]"): (
            'Infix[{HoldForm[x], HoldForm[y]}, "/", 400, Left]'
        ),
    }

    grouping = "Left"
    operator = "/"
    precedence = 470

    rules = {
        "Divide[x_, y_]": "Times[x, Power[y, -1]]",
        #        "MakeBoxes[Divide[x_, y_], f:StandardForm|TraditionalForm]": (
        #            "FractionBox[MakeBoxes[x, f], MakeBoxes[y, f]]"
        #        ),
    }
    summary_text = "divide"

    # The reason why we need these MakeBoxes methods instead of rules
    # is that we have still several incompatibilities with WMA.
    # In particular, OutputForm should produce a "2D" text representation,
    # similar to the pretty print of sympy. So, for example,
    # OutputForm[Divide[a+b,c+d]]  -> FractionBox[a+b, c+d]
    # shoud produce something like
    #
    #     a + b
    #    -------
    #     c + d
    # which does not require parenthesis in the numerator and the denominator.
    #
    # On the other hand, with our current implementation, FractionBox[a+b, c+d]
    # produces
    #  a + b / c + d
    #
    # For this reason, we need to add parenthesis to this expression.
    # Then, when we translate it to some representation admitting the 2D representation
    # like LaTeX or MathML, the parenthesis are removed.

    def eval_makeboxes_input_output_form(self, x, y, form, evaluation):
        """MakeBoxes[Divide[x_, y_], form:OutputForm]"""
        # This adds the parenthesis when they are needed, for the case
        # of 1D text output.
        num = parenthesize(400, x, eval_makeboxes(x, evaluation, form), False)
        den = parenthesize(400, y, eval_makeboxes(y, evaluation, form), True)
        return Expression(SymbolFractionBox, num, den)

    def eval_makeboxes_standardform(self, x, y, form, evaluation):
        """MakeBoxes[Divide[x_, y_], form:(StandardForm|TraditionalForm)]"""
        # This adds the parenthesis when they are needed, for the case
        # of 1D text output.
        num = parenthesize(400, x, eval_makeboxes(x, evaluation, form), False)
        den = parenthesize(400, y, eval_makeboxes(y, evaluation, form), True)
        return Expression(SymbolFractionBox, num, den)


class Minus(PrefixOperator):
    """
    <url>
    :Additive inverse:
    https://en.wikipedia.org/wiki/Additive_inverse</url> (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/Minus.html</url>)

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

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    default_formats = False
    operator = "-"
    precedence = 480

    rules = {
        "Minus[x_]": "Times[-1, x]",
    }

    summary_text = "arithmetic negate"

    def eval_int(self, x: Integer, evaluation):
        "Minus[x_Integer]"
        return Integer(-x.value)

    def eval_makeboxes(self, x, form, evaluation):
        """MakeBoxes[Minus[x_], form:(InputForm|OutputForm|StandardForm|TraditionalForm)]"""
        # This adds the parenthesis when they are needed, for the case
        # of 1D text output.
        factor = parenthesize(400, x, eval_makeboxes(x, evaluation, form), False)
        return Expression(SymbolRowBox, ListExpression(String(self.operator), factor))


class Plus(BinaryOperator, SympyFunction):
    """
    <url>
    :Addition:
    https://en.wikipedia.org/wiki/Addition</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/core.html#id48</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Plus.html</url>)

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

    operator = "+"
    precedence = 310

    summary_text = "add"

    # FIXME Note this is deprecated in 1.11
    # Remember to up sympy doc link when this is corrected
    sympy_name = "Add"

    def eval_makeboxes_plus(self, items, form, evaluation):
        "MakeBoxes[Plus[items__], form:(InputForm|OutputForm|StandardForm|TraditionalForm)]"
        if form in (SymbolInputForm, SymbolOutputForm):
            ops = [String(" + "), String(" - ")]
        else:
            ops = [String("+"), String("-")]
        return self.do_eval_makeboxes_plus_ops(
            items.get_sequence(), form, evaluation, ops
        )

    def do_eval_makeboxes_plus_ops(
        self, terms, form, evaluation, ops=[String("+"), String("-")]
    ):
        term = terms[0]
        formatted_term = eval_makeboxes(term, evaluation, form)
        # formatted_term = parenthesize(310, term, formatted_term, True)
        formatted_terms = [formatted_term]

        def is_negative(t):
            if isinstance(t, Complex):
                re_symp, im_sympy = t.to_sympy().as_real_imag()
                if re_sympy == 0:
                    if im_sympy < 0:
                        return True
                if re_sympy < 0:
                    return True
            if isinstance(t, Number):
                return t.value < 0
            if t.has_form("Minus", 1):
                return not is_negative(t.elements[0])
            if t.has_form("Times", 2, None):
                return is_negative(t.elements[0])
            if t.has_form("HoldForm", 1):
                return is_negative(t.elements[0])
            if t.has_form("Divide", 2):
                return is_negative(t.elements[0])
            return False

        def negate(t):
            if isinstance(t, Number):
                return from_sympy(-t.to_sympy())
            if t.has_form("Times", 2, None):
                factors = t.elements
                return Expression(SymbolTimes, negate(factors[0]), *factors[1:])
            if t.has_form("Minus", 1):
                return t.elements[0]
            if t.has_form("HoldForm", 1):
                return negate(t.elements[0])
            if t.has_form("Divide", 2):
                num, den = t.elements
                return Expression(SymbolDivide, negate(num), den)
            return Expression(Minus, t)

        for term in terms[1:]:
            minus = 0
            while True:
                if term.has_form("HoldForm", 1):
                    term = term.elements[0]
                    continue
                if term.has_form("Minus", 1):
                    term = term.elements[0]
                    minus += 1
                    continue
                if is_negative(term):
                    minus += 1
                    term = negate(term)
                break
            formatted_terms.append(ops[minus % 2])
            formatted_term = eval_makeboxes(term, evaluation, form)
            formatted_term = parenthesize(310, term, formatted_term, True)
            formatted_terms.append(formatted_term)
        return Expression(SymbolRowBox, ListExpression(*formatted_terms))

    def eval(self, items, evaluation):
        "Plus[items___]"
        items_tuple = numerify(items, evaluation).get_sequence()
        return eval_Plus(*items_tuple)


class Power(BinaryOperator, MPMathFunction):
    """
    <url>
    :Exponentiation:
    https://en.wikipedia.org/wiki/Exponentiation</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/core.html#sympy.core.power.Pow</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Power.html</url>)

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
    operator = "^"
    precedence = 590

    rules = {
        "Power[]": "1",
        "Power[x_]": "x",
    }

    summary_text = "exponentiate"

    # FIXME Note this is deprecated in 1.11
    # Remember to up sympy doc link when this is corrected
    sympy_name = "Pow"

    def eval_check(self, x, y, evaluation):
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

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    rules = {
        "Sqrt[x_]": "x ^ (1/2)",
        "MakeBoxes[Sqrt[x_], f:StandardForm|TraditionalForm]": (
            "SqrtBox[MakeBoxes[x, f]]"
        ),
    }

    summary_text = "square root"


class Subtract(BinaryOperator):
    """
    <url>
    :Subtraction:
    https://en.wikipedia.org/wiki/Subtraction</url>, (<url>:WMA:
    https://reference.wolfram.com/language/ref/Subtract.html</url>)

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

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    grouping = "Left"

    operator = "-"
    precedence = 310
    precedence_parse = 311
    rules = {
        "Subtract[x_, y_]": "Plus[x, Times[-1, y]]",
    }

    summary_text = "subtract"


class Times(BinaryOperator, SympyFunction):
    """
    <url>
    :Multiplication:
    https://en.wikipedia.org/wiki/Multiplication</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/core.html#sympy.core.mul.Mul</url>, <url>
    :WMA:https://reference.wolfram.com/language/ref/Times.html</url>)

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

    operator = "*"
    operator_display = " "

    precedence = 400
    rules = {}

    # FIXME Note this is deprecated in 1.11
    # Remember to up sympy doc link when this is corrected
    sympy_name = "Mul"

    summary_text = "mutiply"

    def do_eval_makeboxes_times(self, factors, form, evaluation, op=String("\u2062")):
        op_str = String(op)
        factor = factors[0]
        formatted_factor = eval_makeboxes(factor, evaluation, form)
        formatted_factor = parenthesize(400, factor, formatted_factor, False)
        elements = [formatted_factor]
        factors = factors[1:]

        for factor in factors:
            elements.append(op)
            formatted_factor = eval_makeboxes(factor, evaluation, form)
            formatted_factor = parenthesize(400, factor, formatted_factor, False)
            elements.append(formatted_factor)

        return Expression(SymbolRowBox, ListExpression(*elements))

    def do_format_times(self, items, evaluation, form):
        # format_times canonicalizes the form of a product in two ways:
        # * removes (-1) from the first element of a product, replacing it
        #   by "Minus[Times[rest]]"
        # * collect all Rational, Divide and negative power factors,
        # and reformat the expression as Divide[numerator, denominator]
        # with numerator and denominator free of these class of factors.

        factors = items.get_sequence()

        if factors[0] is IntegerM1:
            rest = factors[1:]
            if len(rest) > 1:
                result = Expression(
                    SymbolHoldForm,
                    Expression(SymbolMinus, Expression(SymbolTimes, *rest)),
                )
            else:
                result = Expression(SymbolHoldForm, Expression(SymbolMinus, rest[0]))
            return result
        if factors[0].has_form("Minus", 1):
            factors[0] = factors[0].elements[0]
            result = Expression(
                SymbolHoldForm,
                Expression(SymbolMinus, Expression(SymbolTimes, *factors)),
            )
            return result

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

        # Segretate negative powers
        positive = []
        negative = []
        changed = False
        for item in factors:
            if (
                item.has_form("Power", 2)
                and isinstance(item.elements[1], (Integer, Rational, Real))
                and item.elements[1].to_sympy() < 0
            ):  # nopep8
                negative.append(inverse(item))
            elif isinstance(item, Complex):
                positive.append(do_format_complex(item, evaluation, SymbolOutputForm))
            elif item.has_form("Divide", 2):
                numerator, denominator = item.elements()
                if numerator is not Integer1:
                    positive.append(numerator)
                negative.append(denominator)
            elif isinstance(item, Rational):
                numerator = item.numerator()
                if not numerator.sameQ(Integer1):
                    positive.append(numerator)
                negative.append(item.denominator())
            else:
                positive.append(item)

        # positive = [Expression(SymbolHoldForm, item) for item in positive]
        # negative = [Expression(SymbolHoldForm, item) for item in negative]
        if negative:
            den = (
                negative[0]
                if len(negative) == 1
                else Expression(SymbolTimes, *negative)
            )
            change_sign = False
            if positive:
                if len(positive) == 1:
                    num = positive[0]
                else:
                    first_factor = positive[0]
                    change_sign = (
                        isinstance(first_factor, (Integer, Real))
                        and first_factor.value < 0
                    )
                    if change_sign:
                        # negate first factor
                        first_factor = -first_factor.to_sympy()
                        if first_factor == 1:
                            positive = positive[1:]
                        else:
                            positive[0] = from_sympy(first_factor)
                    num = (
                        Expression(SymbolTimes, *positive)
                        if len(positive) > 1
                        else positive[0]
                    )
            else:
                num = Integer1
            result = Expression(SymbolHoldForm, Expression(SymbolDivide, num, den))
            if change_sign:
                result = Expression(SymbolMinus, result)
            return result
        # This happends if there are pure imaginary factors
        if changed or len(positive) != len(factors):
            result = Expression(SymbolHoldForm, Expression(SymbolTimes, *positive))
            return result

        return None

    def eval(self, items, evaluation):
        "Times[items___]"
        items = numerify(items, evaluation).get_sequence()
        return eval_Times(*items)

    def eval_makeboxes_times(self, items, form, evaluation):
        "MakeBoxes[Times[items__], form:(InputForm|OutputForm|StandardForm|TraditionalForm)]"
        factors = items.get_sequence()
        if len(factors) < 2:
            # Times[] and Times[...] are not evaluated here...
            return None
        if form is SymbolInputForm:
            op = String("*")
        else:
            op = String(" ")
        result = self.do_eval_makeboxes_times(factors, form, evaluation, op)
        return result

    def format_times_input(self, items, evaluation):
        "InputForm: Times[items__]"
        return self.do_format_times(items, evaluation, SymbolInputForm)

    def format_times_output(self, items, evaluation):
        "OutputForm: Times[items__]"
        return self.do_format_times(items, evaluation, SymbolOutputForm)

    def format_times_standardform(self, items, evaluation):
        "StandardForm: Times[items__]"
        return self.do_format_times(items, evaluation, SymbolStandardForm)

    def format_times_traditionalform(self, items, evaluation):
        "TraditionalForm: Times[items__]"
        return self.do_format_times(items, evaluation, SymbolStandardForm)
