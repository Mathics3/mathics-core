# -*- coding: utf-8 -*-

"""
Hyperbolic Functions

<url>:Hyperbolic functions: https://en.wikipedia.org/wiki/Hyperbolic_functions</url> are analogues of the ordinary trigonometric functions, but defined using the hyperbola rather than the circle.

Numerical values and derivatives can be computed; however, most special exact values and simplification rules are not implemented yet.
"""

from typing import Optional
from mathics.core.convert.sympy import SympyExpression

from mathics.builtin.arithmetic import _MPMathFunction
from mathics.builtin.base import Builtin
from mathics.core.atoms import IntegerM1
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolPower

SymbolArcCosh = Symbol("ArcCosh")
SymbolArcSinh = Symbol("ArcSinh")
SymbolCosh = Symbol("Cosh")
SymbolSinh = Symbol("Sinh")


class ArcCosh(_MPMathFunction):
    """
    <dl>
      <dt>'ArcCosh[$z$]'
      <dd>returns the inverse hyperbolic cosine of $z$.
    </dl>

    >> ArcCosh[0]
     = I / 2 Pi
    >> ArcCosh[0.]
     = 0. + 1.5708 I
    >> ArcCosh[0.00000000000000000000000000000000000000]
     = 1.5707963267948966192313216916397514421 I
    #> ArcCosh[1.4]
     = 0.867015
    """

    summary_text = "inverse hyperbolic cosine function"
    sympy_name = "acosh"
    mpmath_name = "acosh"

    rules = {
        "Derivative[1][ArcCosh]": "1/(Sqrt[#-1]*Sqrt[#+1])&",
    }


class ArcCoth(_MPMathFunction):
    """
    <dl>
      <dt>'ArcCoth[$z$]'
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

    #> ArcCoth[0.000000000000000000000000000000000000000]
     = 1.57079632679489661923132169163975144210 I
    """

    summary_text = "inverse hyperbolic cotangent function"
    sympy_name = "acoth"
    mpmath_name = "acoth"

    rules = {
        "ArcCoth[z:0.0]": "N[I / 2 Pi, Precision[1+z]]",
        "Derivative[1][ArcCoth]": "1/(1-#^2)&",
    }


class ArcCsch(_MPMathFunction):
    """
    <dl>
      <dt>'ArcCsch[$z$]'
      <dd>returns the inverse hyperbolic cosecant of $z$.
    </dl>

    >> ArcCsch[0]
     = ComplexInfinity
    >> ArcCsch[1.0]
     = 0.881374
    """

    mpmath_name = "acsch"

    rules = {
        "ArcCsch[0]": "ComplexInfinity",
        "ArcCsch[0.]": "ComplexInfinity",
        "Derivative[1][ArcCsch]": "-1 / (Sqrt[1+1/#^2] * #^2) &",
    }

    summary_text = "inverse hyperbolic cosecant function"
    sympy_name = ""

    def to_sympy(self, expr, **kwargs) -> Optional[SympyExpression]:
        if len(expr.elements) == 1:
            return Expression(
                SymbolArcSinh, Expression(SymbolPower, expr.elements[0], IntegerM1)
            ).to_sympy()


class ArcSech(_MPMathFunction):
    """
    <dl>
      <dt>'ArcSech[$z$]'
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


class ArcSinh(_MPMathFunction):
    """
    <dl>
      <dt>'ArcSinh[$z$]'
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
        "Derivative[1][ArcSinh]": "1/Sqrt[1+#^2]&",
    }


class ArcTanh(_MPMathFunction):
    """
    <dl>
    <dt>'ArcTanh[$z$]'
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
        "Derivative[1][ArcTanh]": "1/(1-#^2)&",
    }

    summary_text = "inverse hyperbolic tangent function"
    sympy_name = "atanh"


class Cosh(_MPMathFunction):
    """
    <dl>
      <dt>'Cosh[$z$]'
      <dd>returns the hyperbolic cosine of $z$.
    </dl>

    >> Cosh[0]
     = 1
    """

    mpmath_name = "cosh"

    rules = {
        "Derivative[1][Cosh]": "Sinh[#]&",
    }

    summary_text = "hyperbolic cosine function"


class Coth(_MPMathFunction):
    """
    <dl>
      <dt>'Coth[$z$]'
      <dd>returns the hyperbolic cotangent of $z$.
    </dl>

    >> Coth[0]
     = ComplexInfinity
    """

    mpmath_name = "coth"

    rules = {
        "Coth[0]": "ComplexInfinity",
        "Coth[0.]": "ComplexInfinity",
        "Derivative[1][Coth]": "-Csch[#1]^2&",
    }

    summary_text = "hyperbolic cotangent function"


class Gudermannian(Builtin):
    """
    <url>:Gudermannian function: https://en.wikipedia.org/wiki/Gudermannian_function</url> (<url>:WMA: https://reference.wolfram.com/language/ref/Gudermannian.html</url>, <url>:MathWorld: https://mathworld.wolfram.com/Gudermannian.html</url>)
    <dl>
      <dt>'Gudermannian[$z$]'
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
    # of relatiions to trigonometric and hyperbolic functions that could be
    # used if needed.
    rules = {
        "Gudermannian[Undefined]": "Undefined",
        "Gudermannian[0]": "0",
        "Gudermannian[2*Pi*I]": "0",
        "Gudermannian[6/4*Pi*I]": "DirectedInfinity[-I]",
        "Gudermannian[Infinity]": "Pi/2",
        "Gudermannian[-Infinity]": "Pi/2",
        # Below, we don't use instead of ComplexInfinity that gets
        # substituted out for DirectedInfinity[] before we match on
        # Gudermannian[...]
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
    <url>:Inverse Gudermannian function: https://en.wikipedia.org/wiki/Gudermannian_function</url> (<url>:WMA: https://reference.wolfram.com/language/ref/InverseGudermannian.html</url>, <url>:MathWorld: https://mathworld.wolfram.com/InverseGudermannian.html</url>)
    <dl>
      <dt>'InverseGudermannian[$z$]'
       <dd>returns the inverse Gudermannian function $gd$^-1($z$).
    </dl>

    >> InverseGudermannian[.5]
     = 0.522238

    'InverseGudermannian[-$z$]' == -'InversGudermannian[$z$]':

    >> InverseGudermannian[-.5] ==  -InverseGudermannian[.5]
     = True

    >> Plot[InverseGudermannian[x], {x, -10, 10}]
     = -Graphics-
    """

    rules = {
        "InverseGudermannian[z_]": "Log[Tan[Pi/4 + z/2]]",
        # Derivative[1][InverseGudermannian] := Sec[#] &;
    }

    summary_text = "inverse Gudermannian function gd^-1(z)"


class Sech(_MPMathFunction):
    """
    <dl>
      <dt>'Sech[$z$]'
      <dd>returns the hyperbolic secant of $z$.
    </dl>

    >> Sech[0]
     = 1
    """

    mpmath_name = "sech"

    rules = {
        "Derivative[1][Sech]": "-Sech[#1] Tanh[#1]&",
    }
    summary_text = "hyperbolic secant function"
    sympy_name = ""

    def to_sympy(self, expr, **kwargs) -> Optional[SympyExpression]:
        if len(expr.elements) == 1:
            return Expression(
                SymbolPower, Expression(SymbolCosh, expr.elements[0]), IntegerM1
            ).to_sympy()


class Sinh(_MPMathFunction):
    """
    <dl>
      <dt>'Sinh[$z$]'
      <dd>returns the hyperbolic sine of $z$.
    </dl>

    >> Sinh[0]
     = 0
    """

    summary_text = "hyperbolic sine function"
    mpmath_name = "sinh"

    rules = {
        "Derivative[1][Sinh]": "Cosh[#]&",
    }


class Tanh(_MPMathFunction):
    """
    <dl>
      <dt>'Tanh[$z$]'
      <dd>returns the hyperbolic tangent of $z$.
    </dl>

    >> Tanh[0]
     = 0
    """

    summary_text = "hyperbolic tangent function"
    mpmath_name = "tanh"

    rules = {
        "Derivative[1][Tanh]": "Sech[#1]^2&",
    }
