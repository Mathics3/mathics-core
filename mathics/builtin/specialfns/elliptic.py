"""
Elliptic Integrals

In integral calculus, an elliptic integral is one of a number of related functions defined as the value of certain integral. Their name originates from their originally arising in connection with the problem of finding the arc length of an ellipse. These funcion often are used in cryptography to encode and decode messages.

See <url>https://en.wikipedia.org/wiki/Elliptic_integral</url>.
"""

from mathics.core.attributes import (
    listable as A_LISTABLE,
    numeric_function as A_NUMERIC_FUNCTION,
    protected as A_PROTECTED,
)
from mathics.builtin.base import SympyFunction
from mathics.core.convert.sympy import from_sympy

import sympy


class EllipticE(SympyFunction):
    """
    <dl>
      <dt>'EllipticE[$m$]'
      <dd>computes the complete elliptic integral $E$($m$).

      <dt>'EllipticE[ϕ|$m$]'
      <dd>computes the complete elliptic integral of the second kind $E$($m$|$ϕ$).
    </dl>

    Elliptic curves give Pi / 2 when evaluated at zero:
    >> EllipticE[0]
     = Pi / 2

    >> EllipticE[0.3, 0.8]
     = 0.296426

    Plot over a reals centered around 0:
    >> Plot[EllipticE[m], {m, -2, 2}]
     = -Graphics-
    """

    attributes = A_NUMERIC_FUNCTION | A_PROTECTED
    summary_text = "elliptic integral of the second kind E(ϕ|m)"
    sympy_name = "elliptic_e"

    def apply_m(self, m, evaluation):
        "%(name)s[m_]"
        sympy_arg = m.numerify(evaluation).to_sympy()
        return from_sympy(sympy.elliptic_e(sympy_arg))

    def apply_phi_m(self, phi, m, evaluation):
        "%(name)s[phi_, m_]"
        sympy_args = [a.numerify(evaluation).to_sympy() for a in (phi, m)]
        return from_sympy(sympy.elliptic_e(*sympy_args))


class EllipticF(SympyFunction):
    """
    <dl>
      <dt>'EllipticF[$m$]'
      <dd>computes the elliptic integral of the first kind $F$($ϕ$|$m$).
    </dl>

    >> EllipticF[0.3, 0.8]
     = 0.303652

    EllipticF is zero when the firt argument is zero:
    >> EllipticF[0, 0.8]
     = 0

    """

    attributes = A_NUMERIC_FUNCTION | A_PROTECTED
    summary_text = "elliptic integral F(ϕ|m)"
    sympy_name = "elliptic_f"

    def apply(self, phi, m, evaluation):
        "%(name)s[phi_, m_]"
        sympy_args = [a.numerify(evaluation).to_sympy() for a in (phi, m)]
        return from_sympy(sympy.elliptic_f(*sympy_args))


class EllipticK(SympyFunction):
    """
    <dl>
      <dt>'EllipticK[$m$]'
      <dd>computes the elliptic integral of the first kind $K$($m$).
    </dl>

    >> EllipticK[0.5]
     = 1.85407

    Elliptic curves give Pi / 2 when evaluated at zero:
    >> EllipticK[0]
     = Pi / 2

    Plot over a reals around 0:
    >> Plot[EllipticK[n], {n, -1, 1}]
     = -Graphics-
    """

    attributes = A_NUMERIC_FUNCTION | A_LISTABLE | A_PROTECTED
    summary_text = "elliptic integral of the first kind K(m)"
    sympy_name = "elliptic_k"

    def apply(self, m, evaluation):
        "%(name)s[m__]"
        args = m.numerify(evaluation).get_sequence()
        sympy_args = [a.to_sympy() for a in args]
        return from_sympy(sympy.elliptic_k(*sympy_args))


class EllipticPi(SympyFunction):
    """
    <dl>
      <dt>'EllipticPi[$n$, $m$]'
      <dd>computes the elliptic integral of the third kind $Pi$($m$).
    </dl>

    >> EllipticPi[0.4, 0.6]
     = 2.89281

    Elliptic curves give Pi / 2 when evaluated at zero:
    >> EllipticPi[0, 0]
     = Pi / 2

    """

    attributes = A_NUMERIC_FUNCTION | A_PROTECTED
    summary_text = "elliptic integral of the third kind P(n|m)"
    sympy_name = "elliptic_pi"

    def apply_n_m(self, n, m, evaluation):
        "%(name)s[n_, m_]"
        sympy_n = m.numerify(evaluation).to_sympy()
        sympy_m = n.numerify(evaluation).to_sympy()
        return from_sympy(sympy.elliptic_pi(sympy_n, sympy_m))

    def apply_n_phi_m(self, n, phi, m, evaluation):
        "%(name)s[n_, phi_, m_]"
        sympy_n = m.numerify(evaluation).to_sympy()
        sympy_phi = m.numerify(evaluation).to_sympy()
        sympy_m = n.numerify(evaluation).to_sympy()
        return from_sympy(sympy.elliptic_pi(sympy_n, sympy_phi, sympy_m))
