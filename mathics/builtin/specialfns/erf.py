# -*- coding: utf-8 -*-

"""
Error Function and Related Functions
"""


from mathics.builtin.arithmetic import _MPMathFunction, _MPMathMultiFunction

from mathics.core.attributes import (
    listable as A_LISTABLE,
    numeric_function as A_NUMERIC_FUNCTION,
    protected as A_PROTECTED,
)


class Erf(_MPMathMultiFunction):
    """
    <url>:Error function: https://en.wikipedia.org/wiki/Error_function</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.error_functions.erf</url>, <url>:WMA: https://reference.wolfram.com/language/ref/Erf.html</url>)
    <dl>
      <dt>'Erf[$z$]'
      <dd>returns the error function of $z$.

      <dt>'Erf[$z0$, $z1$]'
      <dd>returns the result of 'Erf[$z1$] - Erf[$z0$]'.
    </dl>

    'Erf[$x$]' is an odd function:
    >> Erf[-x]
     = -Erf[x]

    >> Erf[1.0]
     = 0.842701
    >> Erf[0]
     = 0
    >> {Erf[0, x], Erf[x, 0]}
     = {Erf[x], -Erf[x]}
    >> Plot[Erf[x], {x, -2, 2}]
     = -Graphics-
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    summary_text = "error function"
    mpmath_names = {
        1: "erf",
    }
    sympy_names = {
        1: "erf",
        2: "erf2",
    }

    rules = {
        "Derivative[1][Erf]": "2 Exp[-#^2] / Sqrt[Pi] &",
    }


class Erfc(_MPMathFunction):
    """
    <url>:Complementary Error function:.https://en.wikipedia.org/wiki/Error_function</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.error_functions.erfc</url>, <url>:WMA: https://reference.wolfram.com/language/ref/Erfc.html</url>)

    <dl>
      <dt>'Erfc[$z$]'
      <dd>returns the complementary error function of $z$.
    </dl>

    >> Erfc[-x] / 2
     = (2 - Erfc[x]) / 2
    >> Erfc[1.0]
     = 0.157299
    >> Erfc[0]
     = 1
    >> Plot[Erfc[x], {x, -2, 2}]
     = -Graphics-
    """

    mpmath_name = "erfc"
    summary_text = "complementary error function"
    rules = {
        "Derivative[1][Erfc]": "-2 Exp[-#^2] / Sqrt[Pi] &",
    }


class FresnelC(_MPMathFunction):
    """
    <url>:Fresnel integral: https://en.wikipedia.org/wiki/Fresnel_integral</url> (<url>:mpmath: https://mpmath.org/doc/current/functions/expintegrals.html?highlight=fresnelc#mpmath.fresnelc</url>, <url>:WMA: https://reference.wolfram.com/language/ref/FresnelC.html</url>)
    <dl>
      <dt>'FresnelC[$z$]'
      <dd>is the Fresnel C integral $C$($z$).
    </dl>

    >> FresnelC[{0, Infinity}]
     = {0, 1 / 2}

    ## SymPy can't currently simplify this all the way to FresnelC[z].
    >> Integrate[Cos[x^2 Pi/2], {x, 0, z}]
     = FresnelC[z]
    """

    summary_text = "Fresnel's integral C"
    rules = {
        "Derivative[1][FresnelC]": "Cos[(Pi*#1^2)/2]&",
    }
    mpmath_name = "fresnelc"


class FresnelS(_MPMathFunction):
    """
    <url>:Fresnel integral: https://en.wikipedia.org/wiki/Fresnel_integral</url> (<url>:mpmath: https://mpmath.org/doc/current/functions/expintegrals.html#mpmath.fresnels</url>, <url>:WMA: https://reference.wolfram.com/language/ref/FresnelS.html</url>)

    <dl>
    <dt>'FresnelS[$z$]'
        <dd>is the Fresnel S integral $S$($z$).
    </dl>

    >> FresnelS[{0, Infinity}]
     = {0, 1 / 2}

    ## SymPy can't currently simplify this all the way to FresnelS[z].
    >> Integrate[Sin[x^2 Pi/2], {x, 0, z}]
     = FresnelS[z]
    """

    rules = {
        "Derivative[1][FresnelS]": "Sin[(Pi*#1^2)/2]&",
    }
    summary_text = "Fresnel's integral S"
    mpmath_name = "fresnels"


class InverseErf(_MPMathFunction):
    """
      <url>:Inverse error function: https://en.wikipedia.org/wiki/Error_function#Inverse_functions</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/functions/special.html?highlight=erfinv#sympy.functions.special.error_functions.erfinv</url>, <url>:WMA: https://reference.wolfram.com/language/ref/InverseErf.html</url>)
    <dl>
      <dt>'InverseErf[$z$]'
      <dd>returns the inverse error function of $z$.
    </dl>

    >> InverseErf /@ {-1, 0, 1}
     = {-Infinity, 0, Infinity}
    >> Plot[InverseErf[x], {x, -1, 1}]
     = -Graphics-

    'InverseErf[$z$]' only returns numeric values for '-1 <= $z$ <= 1':
    >> InverseErf /@ {0.9, 1.0, 1.1}
     = {1.16309, Infinity, InverseErf[1.1]}
    """

    # No inherited NumericFunction
    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "inverse of the error function"
    sympy_name = "erfinv"
    mpmath_name = "erfinv"

    rules = {
        "Derivative[1][InverseErf]": "Sqrt[Pi] Exp[InverseErf[#]^2] / 2 &",
    }

    def apply(self, z, evaluation):
        "%(name)s[z__]"

        try:
            return super(InverseErf, self).apply(z, evaluation)
        except ValueError as exc:
            if str(exc) == "erfinv(x) is defined only for -1 <= x <= 1":
                return
            else:
                raise


class InverseErfc(_MPMathFunction):
    """
    <url>:Complementary error function: https://en.wikipedia.org/wiki/Error_function#Complementary_error_function</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/functions/special.html?highlight=erfinv#sympy.functions.special.error_functions.erfcinv</url>, <url>:WMA: https://reference.wolfram.com/language/ref/InverseErfc.html</url>)
    <dl>
      <dt>'InverseErfc[$z$]'
      <dd>returns the inverse complementary error function of $z$.
    </dl>

    >> InverseErfc /@ {0, 1, 2}
     = {Infinity, 0, -Infinity}
    """

    # No inherited NumericFunction
    attributes = A_LISTABLE | A_PROTECTED
    sympy_name = "erfcinv"
    summary_text = "inverse of the complementary error function"
    rules = {
        "Derivative[1][InverseErfc]": "-Sqrt[Pi] Exp[InverseErfc[#]^2] / 2 &",
    }
