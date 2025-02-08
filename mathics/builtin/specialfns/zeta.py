# -*- coding: utf-8 -*-

"""
Zeta Functions and Polylogarithms

See also <url>
:Chapters 25 Zeta and Related Functions in the Digital Libary of Mathematical Functions:
https://dlmf.nist.gov/25</url>.
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
from mathics.core.evaluation import Evaluation


class LerchPhi(MPMathFunction):
    r"""
    <url>:Lerch transcendent:
    https://en.wikipedia.org/wiki/Lerch_transcendent</url> (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/LerchPhi.html</url>)

    <dl>
      <dt>'LerchPhi[z,s,a]'
      <dd>gives the Lerch transcendent $\Phi(z,s,a)$.
    </dl>

    >> LerchPhi[2, 3, -1.5]
     = 19.3893 - 2.1346 I

    >> LerchPhi[1, 2, 1/4] == 8 Catalan + Pi^2
     = True

    Plot between between -1 and 1:
    >> Plot[LerchPhi[x, 1, 2], {x, -1, 1}]
     = -Graphics-

    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = "lerchphi"
    sympy_name = "lerchphi"
    summary_text = "compute Lerch's trascendental ϕ function"

    def eval(self, z, s, a, evaluation: Evaluation):
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
    <url>:Polylogarithm:
    https://en.wikipedia.org/wiki/Polylogarithm</url> (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/PolyLog.html</url>)

    <dl>
      <dt>'PolyLog'[$n$, $z$]
      <dd>returns the polylogarithm function $Li_n(z)$.
    </dl>

    >> PolyLog[s, 1]
     = Zeta[s]
    >> PolyLog[-7, I] //Chop
     = 136.

    Dilogarithm function $Li_2(x)$:
    >> Plot[PolyLog[2,x], {x, -20, 1}]
     = -Graphics-
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = "polylog"
    summary_text = "compute the Polylogarithm function"
    sympy_name = "polylog"

    def eval(self, n, z, evaluation: Evaluation):
        "PolyLog[n_, z_]"
        try:
            return from_mpmath(mpmath.polylog(n.to_python(), z.to_python()))
        except Exception:
            return from_sympy(sympy.polylog(n.to_sympy(), z.to_sympy()))


class Zeta(MPMathFunction):
    """
    <url>:Riemenn zeta function:
    https://en.wikipedia.org/wiki/Riemann_zeta_function</url> (<url>:WMA:
    https://reference.wolfram.com/language/ref/Zeta.html</url>)

    <dl>
      <dt>'Zeta'[$z$]
      <dd>returns the Riemann zeta function of $z$.
    </dl>

    >> Zeta[2]
     = Pi ^ 2 / 6

    >> Zeta[-2.5 + I]
     = 0.0235936 + 0.0014078 I

    >> Plot[Zeta[z], {z, -20, 10}]
     = -Graphics-
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    sympy_name = "zeta"
    mpmath_name = "zeta"
    summary_text = "compute Riemann's ζ function"


# TODO: ReimannSiegelTheta, ReimannSiegelZ, ReimannXi, ZetaZero
