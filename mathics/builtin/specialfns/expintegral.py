# -*- coding: utf-8 -*-

"""
Exponential Integral and Special Functions
"""


from mathics.builtin.arithmetic import _MPMathFunction


class ExpIntegralE(_MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ExpIntegralE.html</url>

    <dl>
    <dt>'ExpIntegralE[$n$, $z$]'
      <dd>returns the exponential integral function $E_n(z)$.
    </dl>

    >> ExpIntegralE[2.0, 2.0]
     = 0.0375343
    """

    summary_text = "exponential integral function of order n"
    nargs = {2}
    sympy_name = "expint"
    mpmath_name = "expint"


class ExpIntegralEi(_MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ExpIntegralEi.html</url>

    <dl>
      <dt>'ExpIntegralEi[$z$]'
      <dd>returns the exponential integral function $Ei(z)$.
    </dl>

    >> ExpIntegralEi[2.0]
     = 4.95423
    """

    summary_text = "exponential integral function"
    sympy_name = "Ei"
    mpmath_name = "ei"


class ProductLog(_MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ProductLog.html</url>

    <dl>
      <dt>'ProductLog[$z$]'
      <dd>returns the value of the Lambert W function at $z$.
    </dl>

    The defining equation:
    >> z == ProductLog[z] * E ^ ProductLog[z]
     = True

    Some special values:
    >> ProductLog[0]
     = 0
    >> ProductLog[E]
     = 1

    The graph of 'ProductLog':
    >> Plot[ProductLog[x], {x, -1/E, E}]
     = -Graphics-
    """

    summary_text = "Lambert's W function"
    sympy_name = "LambertW"  # function called LambertW in SymPy
    mpmath_name = "lambertw"

    rules = {
        "ProductLog[0]": "0",
        "ProductLog[E]": "1",
        "ProductLog[z_] * E ^ ProductLog[z_]": "z",
        "Derivative[1][ProductLog]": "ProductLog[#] / (# (ProductLog[#] + 1))&",
    }


# TODO: Zernike polynomials not yet implemented in mpmath nor sympy
#
# class ZernikeR(_MPMathFunction):
#    """
#    <dl>
#    <dt>'ZernikeR[$n$, $m$,  $r$]'
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
