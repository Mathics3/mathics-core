# -*- coding: utf-8 -*-

"""
Exponential Integral and Special Functions

See also <url>
:Chapters 4.2-4.13 Logarithm, Exponential, Powers in the Digital Library of Mathematical Functions:
https://dlmf.nist.gov/4#PT2</url>.
"""


from mathics.core.attributes import (
    A_LISTABLE,
    A_NUMERIC_FUNCTION,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, MPMathFunction


class ExpIntegralE(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ExpIntegralE.html</url>

    <dl>
    <dt>'ExpIntegralE'[$n$, $z$]
      <dd>returns the exponential integral function $E_n(z)$.
    </dl>

    >> ExpIntegralE[2.0, 2.0]
     = 0.0375343
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    summary_text = "exponential integral function of order n"
    nargs = {2}
    sympy_name = "expint"
    mpmath_name = "expint"


class ExpIntegralEi(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ExpIntegralEi.html</url>

    <dl>
      <dt>'ExpIntegralEi'[$z$]
      <dd>returns the exponential integral function $Ei(z)$.
    </dl>

    >> ExpIntegralEi[2.0]
     = 4.95423
    """

    summary_text = "exponential integral function"
    sympy_name = "Ei"
    mpmath_name = "ei"


class LambertW(Builtin):
    """
    <url>
      :Lambert <i>W</i> Function:
      https://en.wikipedia.org/wiki/Lambert_W_function</url>, <url>:MathWorld:
      https://mathworld.wolfram.com/LambertW-Function.html</url>

    <dl>
      <dt>'LambertW'[$k$]
      <dd>alias for ProductLog[$z$].

      <dt>'LambertW'[$k$, $z$]
      <dd>alias for ProductLog[$k$, $z$].
    </dl>

    >> LambertW[k, z]
     = ProductLog[k, z]

    >> Plot[LambertW[x], {x, -1/E, E}]
     = -Graphics-

    See also <url>
    :ProductLog:
    /doc/reference-of-built-in-symbols/special-functions/exponential-integral-and-special-functions/productlog</url>.
    """

    attributes = A_LISTABLE | A_PROTECTED
    mpmath_name = "lambertw"
    rules = {
        "LambertW[z_]": "ProductLog[z]",
        "LambertW[k_, z_]": "ProductLog[k, z]",
    }
    summary_text = "Lambert W function"
    sympy_name = "LambertW"  # function called LambertW in SymPy


class ProductLog(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ProductLog.html</url>

    <dl>
      <dt>'ProductLog'[$z$]
      <dd>returns the principle solution for $w$ in $z == wE^w$.

      <dt>'ProductLog'[$k$, $z$]
      <dd>gives the $k$-th solution.
    </dl>

    The defining equation:
    >> z == ProductLog[z] * E ^ ProductLog[z]
     = True

    Some special values:
    >> ProductLog[0]
     = 0
    >> ProductLog[E]
     = 1

    >> ProductLog[-1.5]
     = -0.0327837 + 1.54964 I

    The graph of 'ProductLog':
    >> Plot[ProductLog[x], {x, -1/E, E}]
     = -Graphics-
    """

    attributes = A_LISTABLE | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = "lambertw"

    rules = {
        "ProductLog[0]": "0",
        "ProductLog[E]": "1",
        "ProductLog[z_] * E ^ ProductLog[z_]": "z",
        "Derivative[1][ProductLog]": "ProductLog[#] / (# (ProductLog[#] + 1))&",
    }
    summary_text = "Lambert's W function"
    sympy_name = "LambertW"  # function called LambertW in SymPy


# TODO: Zernike polynomials not yet implemented in mpmath nor SymPy
#
# class ZernikeR(MPMathFunction):
#    """
#    <dl>
#    <dt>'ZernikeR'[$n$, $m$,  $r$]
#      <dd>returns the radial Zernike polynomial R_$n$^$m$($r$).
#    </dl>
#
#    >> ZernikeR[3, 1, r]
#     = -2 r + 3 r ^ 3
#
#    >> ZernikeR[5, 1, 1/2]
#     = 5 / 16
#
#    >> ZernikeR[3 - I, 4.5, 1.5 + I]
#     = 1.12642 - 1.21017 I
#    """
#
#    nargs = {3}
#    sympy_name = ''
#    mpmath_name = ''
