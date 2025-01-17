# -*- coding: utf-8 -*-

"""
Zeta Functions and Polylogarithms
"""

import mpmath
import sympy

from mathics.core.attributes import (
    A_LISTABLE,
    A_NUMERIC_FUNCTION,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import MPMathFunction
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy


class LerchPhi(MPMathFunction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/LerchPhi.html</url>

    <dl>
      <dt>'LerchPhi[z,s,a]'
      <dd>gives the Lerch transcendent Φ(z,s,a).
    </dl>

    >> LerchPhi[2, 3, -1.5]
     = 19.3893 - 2.1346 I

    >> LerchPhi[1, 2, 1/4]
     = 17.1973
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = "lerchphi"
    sympy_name = "lerchphi"
    summary_text = "Lerch's trascendental ϕ function"

    def eval(self, z, s, a, evaluation):
        "%(name)s[z_, s_, a_]"

        py_z = z.to_python()
        py_s = s.to_python()
        py_a = a.to_python()
        try:
            return from_mpmath(mpmath.lerchphi(py_z, py_s, py_a))
        except Exception:
            pass
            # return sympy.expand_func(sympy.lerchphi(py_z, py_s, py_a))


class PolyLog(MPMathFunction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/PolyLog.html</url>

    <dl>
      <dt>'PolyLog[$n$, $z$]'
      <dd>returns the polylogarithm function Li_$n$($z$).
    </dl>

    >> PolyLog[s, 1]
     = Zeta[s]
    >> PolyLog[-7, I] //Chop
     = 136.
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    summary_text = "Polylogarithm function"
    sympy_name = "polylog"
    mpmath_name = "polylog"

    def eval(self, n, z, evaluation):
        "PolyLog[n_, z_]"
        try:
            return from_mpmath(mpmath.polylog(n.to_python(), z.to_python()))
        except:
            return from_sympy(sympy.polylog(n.to_sympy(), z.to_sympy()))


class Zeta(MPMathFunction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Zeta.html</url>

    <dl>
      <dt>'Zeta[$z$]'
      <dd>returns the Riemann zeta function of $z$.
    </dl>

    >> Zeta[2]
     = Pi ^ 2 / 6

    >> Zeta[-2.5 + I]
     = 0.0235936 + 0.0014078 I
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    summary_text = "Riemann's ζ function"
    sympy_name = "zeta"
    mpmath_name = "zeta"


# TODO: ReimannSiegelTheta, ReimannSiegelZ, ReimannXi, ZetaZero
