# -*- coding: utf-8 -*-

"""
Hyperbolic Functions

<url>:Hyperbolic functions:
https://en.wikipedia.org/wiki/Hyperbolic_functions</url> are analogues \
of the ordinary trigonometric functions, but defined using the hyperbola \
rather than the circle.

Numerical values and derivatives can be computed; however, most special \
exact values and simplification rules are not implemented yet.
"""

from typing import Optional

from mathics.core.atoms import IntegerM1
from mathics.core.builtin import Builtin, MPMathFunction, SympyFunction
from mathics.core.convert.sympy import SympyExpression
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolPower
from mathics.eval.hyperbolic import eval_ComplexExpand

SymbolArcCosh = Symbol("ArcCosh")
SymbolArcSinh = Symbol("ArcSinh")
SymbolCosh = Symbol("Cosh")
SymbolSinh = Symbol("Sinh")


class ArcCosh(MPMathFunction):
    """
    <url>
    :Inverse hyperbolic cosine:
    https://en.wikipedia.org/wiki/Inverse_hyperbolic_functions#Inverse_hyperbolic_cosine</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#acosh</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/hyperbolic.html#acosh</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/ArcCosh.html</url>)

    <dl>
      <dt>'ArcCosh'[$z$]
      <dd>returns the inverse hyperbolic cosine of $z$.
    </dl>

    >> ArcCosh[0]
     = I / 2 Pi
    >> ArcCosh[0.]
     = 0. + 1.5708 I
    >> ArcCosh[0.00000000000000000000000000000000000000]
     = 1.5707963267948966192313216916397514421 I
    """

    mpmath_name = "acosh"

    rules = {
        "ArcCosh[Undefined]": "Undefined",
        "ArcCosh[DirectedInfinity[I]]": "Infinity",
        "ArcCosh[DirectedInfinity[-I]]": "Infinity",
        "ArcCosh[DirectedInfinity[]]": "Infinity",
        "Derivative[1][ArcCosh]": "1/(Sqrt[#-1]*Sqrt[#+1])&",
    }
    summary_text = "inverse hyperbolic cosine function"
    sympy_name = "acosh"


class ArcCoth(MPMathFunction):
    """
    <url>
    :Inverse hyperbolic cotangent:
    https://en.wikipedia.org/wiki/Inverse_hyperbolic_functions#Inverse_hyperbolic_cotangent</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#acoth</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/hyperbolic.html#acoth</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/ArcCoth.html</url>)

    <dl>
      <dt>'ArcCoth'[$z$]
      <dd>returns the inverse hyperbolic cotangent of $z$.
    </dl>

    >> ArcCoth[0]
     = I / 2 Pi
    >> ArcCoth[1]
     = Infinity
    >> ArcCoth[0.0]
     = 0. + 1.5708 I
    >> ArcCoth[0.5]
     = 0.549306 - 1.5708 I
    """

    summary_text = "inverse hyperbolic cotangent function"
    sympy_name = "acoth"
    mpmath_name = "acoth"

    rules = {
        "ArcCoth[Undefined]": "Undefined",
        "ArcCoth[z:0.0]": "N[I / 2 Pi, Precision[1+z]]",
        "Derivative[1][ArcCoth]": "1/(1-#^2)&",
    }


class ArcCsch(MPMathFunction):
    """
    <url>
    :Inverse hyperbolic cosecant:
    https://en.wikipedia.org/wiki/Inverse_hyperbolic_functions#Inverse_hyperbolic_cosecant</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/elementary.html#acsch</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/hyperbolic.html#acsch</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/ArcCsch.html</url>)

    <dl>
      <dt>'ArcCsch'[$z$]
      <dd>returns the inverse hyperbolic cosecant of $z$.
    </dl>

    >> ArcCsch[0]
     = ComplexInfinity
    >> ArcCsch[1.0]
     = 0.881374
    """

    mpmath_name = "acsch"

    rules = {
        "ArcCsch[Undefined]": "Undefined",
        "ArcCsch[0]": "ComplexInfinity",
        "ArcCsch[0.]": "ComplexInfinity",
        "Derivative[1][ArcCsch]": "-1 / (Sqrt[1+1/#^2] * #^2) &",
    }

    summary_text = "inverse hyperbolic cosecant function"
    sympy_name = "acsch"

    def to_sympy(self, expr, **kwargs) -> Optional[SympyExpression]:
        if len(expr.elements) == 1:
            return Expression(
                SymbolArcSinh, Expression(SymbolPower, expr.elements[0], IntegerM1)
            ).to_sympy()


class ArcSech(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ArcSech.html</url>

    <dl>
      <dt>'ArcSech'[$z$]
      <dd>returns the inverse hyperbolic secant of $z$.
    </dl>

    >> ArcSech[0]
     = Infinity
    >> ArcSech[1]
     = 0
    >> ArcSech[0.5]
     = 1.31696
    """

    mpmath_name = "asech"

    rules = {
        "ArcSech[Undefined]": "Undefined",
        "ArcSech[0]": "Infinity",
        "ArcSech[0.]": "Indeterminate",
        "Derivative[1][ArcSech]": "-1 / (# * Sqrt[(1-#)/(1+#)] (1+#)) &",
    }

    summary_text = "inverse hyperbolic secant function"
    sympy_name = ""

    def to_sympy(self, expr, **kwargs) -> Optional[SympyExpression]:
        if len(expr.elements) == 1:
            return Expression(
                SymbolArcCosh, Expression(SymbolPower, expr.elements[0], IntegerM1)
            ).to_sympy()


class ArcSinh(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ArcSinh.html</url>

    <dl>
      <dt>'ArcSinh'[$z$]
      <dd>returns the inverse hyperbolic sine of $z$.
    </dl>

    >> ArcSinh[0]
     = 0
    >> ArcSinh[0.]
     = 0.
    >> ArcSinh[1.0]
     = 0.881374
    """

    summary_text = "inverse hyperbolic sine function"
    sympy_name = "asinh"
    mpmath_name = "asinh"

    rules = {
        "ArcSinh[Undefined]": "Undefined",
        "Derivative[1][ArcSinh]": "1/Sqrt[1+#^2]&",
    }


class ArcTanh(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ArcTanh.html</url>

    <dl>
      <dt>'ArcTanh'[$z$]
      <dd>returns the inverse hyperbolic tangent of $z$.
    </dl>

    >> ArcTanh[0]
     = 0
    >> ArcTanh[1]
     = Infinity
    >> ArcTanh[0]
     = 0
    >> ArcTanh[.5 + 2 I]
     = 0.0964156 + 1.12656 I
    >> ArcTanh[2 + I]
     = ArcTanh[2 + I]
    """

    mpmath_name = "atanh"
    numpy_name = "arctanh"

    rules = {
        "ArcTanh[Undefined]": "Undefined",
        "Derivative[1][ArcTanh]": "1/(1-#^2)&",
    }

    summary_text = "inverse hyperbolic tangent function"
    sympy_name = "atanh"


class ComplexExpand(SympyFunction):
    """
        (<url>
        :SymPy:
        https://docs.sympy.org/latest/
    modules/core.html#sympy.core.expr.Expr.expand</url>, <url>:WMA:
        https://reference.wolfram.com/language/ref/ComplexExpand.html
        </url>)

        <dl>
          <dt>'ComplexExpand'[$expr$]
          <dd>expands $expr$ assuming that all variables are real.

          <dt>'ComplexExpand'[$expr$,{$x_1$,$x_2$, ...}]
          <dd>expands $expr$ assuming that variables matching any of the $xi$ are complex.
        </dl>

        Note: we get equivalent, but different results from WMA:

        >> ComplexExpand[3^(I x)]
         = 3 ^ (-Im[x]) Re[3 ^ (I Re[x])] + I Im[3 ^ (I Re[x])] 3 ^ (-Im[x])

        Assume that both $x$ and $y$ and are real:
        >> ComplexExpand[Sin[x + I y]]
         = Cosh[y] Sin[x] + I Cos[x] Sinh[y]

        Take $x$ to be complex:

        >> ComplexExpand[Sin[x], x]
         = Cosh[Im[x]] Sin[Re[x]] + I Cos[Re[x]] Sinh[Im[x]]

        Polynomials:
        >> ComplexExpand[Re[z^5 - 2 z^3 - z + 1], z]
         = 1 + Re[z] ^ 5 - 2 Re[z] ^ 3 - Re[z] - 10 Im[z] ^ 2 Re[z] ^ 3 + 5 Im[z] ^ 4 Re[z] + 6 Im[z] ^ 2 Re[z]

        Trigonometric and hyperbolic functions
        >> ComplexExpand[Cos[x + I y] + Tanh[z], {z}]
         = Cos[x] Cosh[y] - I Sin[x] Sinh[y] + Cosh[Re[z]] Sinh[Re[z]] / (Cos[Im[z]] ^ 2 + Sinh[Re[z]] ^ 2) + I Cos[Im[z]] Sin[Im[z]] / (Cos[Im[z]] ^ 2 + Sinh[Re[z]] ^ 2)

        Exponential and logarithmic functions:
        >> ComplexExpand[Abs[2^z Log[2 z]], z]
         = Abs[I Arg[Re[z] + I Im[z]] + Log[4 Im[z] ^ 2 + 4 Re[z] ^ 2] / 2] 2 ^ Re[z]

        Specify that variable $z$ is taken to be complex:
        >> ComplexExpand[Re[2 z^3 - z + 1], z]
         = 1 - Re[z] + 2 Re[z] ^ 3 - 6 Im[z] ^ 2 Re[z]
    """

    summary_text = "expand a complex expression of real variables"
    sympy_name = "expand"

    def eval(self, expr, evaluation: Evaluation):
        "ComplexExpand[expr_]"
        return eval_ComplexExpand(expr, ListExpression())

    def eval_with_complex_vars(self, expr, vars, evaluation: Evaluation):
        "ComplexExpand[expr_, vars__]"
        return eval_ComplexExpand(expr, vars)


class Cosh(MPMathFunction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Cosh.html</url>

    <dl>
      <dt>'Cosh'[$z$]
      <dd>returns the hyperbolic cosine of $z$.
    </dl>

    >> Cosh[0]
     = 1
    """

    mpmath_name = "cosh"

    rules = {
        "Cosh[Undefined]": "Undefined",
        "Derivative[1][Cosh]": "Sinh[#]&",
    }

    summary_text = "hyperbolic cosine function"


class Coth(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Coth.html</url>

    <dl>
      <dt>'Coth'[$z$]
      <dd>returns the hyperbolic cotangent of $z$.
    </dl>

    >> Coth[0]
     = ComplexInfinity
    """

    mpmath_name = "coth"

    rules = {
        "Coth[Undefined]": "Undefined",
        "Coth[0]": "ComplexInfinity",
        "Coth[0.]": "ComplexInfinity",
        "Derivative[1][Coth]": "-Csch[#1]^2&",
    }

    summary_text = "hyperbolic cotangent function"


class Gudermannian(Builtin):
    """
    <url>:Gudermannian function:
    https://en.wikipedia.org/wiki/Gudermannian_function</url> (<url>
    :WMA: https://reference.wolfram.com/language/ref/Gudermannian.html</url>, <url>
    :MathWorld: https://mathworld.wolfram.com/Gudermannian.html</url>)
    <dl>
      <dt>'Gudermannian'[$z$]
      <dd>returns the Gudermannian function $gd$($z$).
    </dl>

    >> Gudermannian[4.2]
     = 1.54081

    'Gudermannian[-$z$]' == - 'Gudermannian[$z$]':

    >> Gudermannian[-4.2] ==  -Gudermannian[4.2]
     = True

    >> Plot[Gudermannian[x], {x, -10, 10}]
     = -Graphics-
    """

    # See https://mathworld.wolfram.com/Gudermannian.html for a number
    # of relations to trigonometric and hyperbolic functions that could be
    # used if needed.
    rules = {
        "Gudermannian[Undefined]": "Undefined",
        "Gudermannian[0]": "0",
        "Gudermannian[2*Pi*I]": "0",
        "Gudermannian[3 I / 2 Pi]": "DirectedInfinity[-I]",
        "Gudermannian[DirectedInfinity[-1]]": "-Pi/2",
        "Gudermannian[DirectedInfinity[]]": "Indeterminate",
        "Gudermannian[z_]": "2 ArcTan[Tanh[z / 2]]",
        # Commented out because := might not work properly
        # Gudermannian[z_] := Piecewise[{{1/2*[Pi - 4*ArcCot[E^z]], Re[z]>0||(Re[z]==0&&Im[z]>=0 )}}, 1/2 (-Pi + 4 ArcTan[E^z])];
        # D[Gudermannian[f_],x_?NotListQ] := Sech[f] D[f,x];
        # Derivative[1][InverseGudermannian] := Sec[#] &;
        # Derivative[1][Gudermannian] := Sech[#] &;
    }

    summary_text = "Gudermannian function gd(z)"


class InverseGudermannian(Builtin):
    """
    <url>:Inverse Gudermannian function:
    https://en.wikipedia.org/wiki/Gudermannian_function</url> (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/InverseGudermannian.html</url>, <url>
    :MathWorld: https://mathworld.wolfram.com/InverseGudermannian.html</url>)
    <dl>
      <dt>'InverseGudermannian'[$z$]
      <dd>returns the inverse Gudermannian function $gd$^-1($z$).
    </dl>

    >> InverseGudermannian[.5]
     = 0.522238

    'InverseGudermannian[-$z$]' == -'InversGudermannian[$z$]':

    >> InverseGudermannian[-.5] ==  -InverseGudermannian[.5]
     = True

    InverseGudermannian is 0 at multiples of 8 Pi:
     = 0

    >> Plot[InverseGudermannian[x], {x, -2 Pi, 2 Pi}]
     = -Graphics-
    """

    rules = {
        "InverseGudermannian[z_]": "Log[Tan[Pi/4 + z/2]]",
        # Derivative[1][InverseGudermannian] := Sec[#] &;
    }

    summary_text = "inverse Gudermannian function gd^-1(z)"


class Sech(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Sech.html</url>

    <dl>
      <dt>'Sech'[$z$]
      <dd>returns the hyperbolic secant of $z$.
    </dl>

    >> Sech[0]
     = 1
    """

    mpmath_name = "sech"

    rules = {
        "Derivative[1][Sech]": "-Sech[#1] Tanh[#1]&",
        "Sech[Undefined]": "Undefined",
    }
    summary_text = "hyperbolic secant function"
    sympy_name = ""

    def to_sympy(self, expr, **kwargs) -> Optional[SympyExpression]:
        if len(expr.elements) == 1:
            return Expression(
                SymbolPower, Expression(SymbolCosh, expr.elements[0]), IntegerM1
            ).to_sympy()


class Sinh(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Sinh.html</url>

    <dl>
      <dt>'Sinh'[$z$]
      <dd>returns the hyperbolic sine of $z$.
    </dl>

    >> Sinh[0]
     = 0
    """

    summary_text = "hyperbolic sine function"
    mpmath_name = "sinh"

    rules = {
        "Derivative[1][Sinh]": "Cosh[#]&",
        "Sinh[Undefined]": "Undefined",
    }


class Tanh(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Tanh.html</url>

    <dl>
      <dt>'Tanh'[$z$]
      <dd>returns the hyperbolic tangent of $z$.
    </dl>

    >> Tanh[0]
     = 0
    """

    summary_text = "hyperbolic tangent function"
    mpmath_name = "tanh"

    rules = {
        "Derivative[1][Tanh]": "Sech[#1]^2&",
        "Tanh[Undefined]": "Undefined",
    }
