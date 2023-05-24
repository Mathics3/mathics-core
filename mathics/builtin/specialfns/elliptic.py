"""
Elliptic Integrals

In integral calculus, an <url>:elliptic integral:
https://en.wikipedia.org/wiki/Elliptic_integral</url>  is one of a number of \
related functions defined as the value of certain integral. Their name \
originates from their originally arising in connection with the problem of \
finding the arc length of an ellipse.

These functions often are used in cryptography to encode and decode messages.
"""

import sympy

from mathics.builtin.base import SympyFunction
from mathics.core.atoms import Integer
from mathics.core.attributes import A_LISTABLE, A_NUMERIC_FUNCTION, A_PROTECTED
from mathics.core.convert.expression import to_numeric_sympy_args
from mathics.core.convert.sympy import from_sympy
from mathics.eval.numerify import numerify


class EllipticE(SympyFunction):
    """
    <url>
    :Elliptic complete elliptic integral of the second kind:
    https://en.wikipedia.org/wiki/Elliptic_integral#Complete_elliptic_integral_of_the_second_kind</url> (<url>:SymPy:
    https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.elliptic_integrals.elliptic_e</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/EllipticE.html</url>)

    <dl>
      <dt>'EllipticE[$m$]'
      <dd>computes the complete elliptic integral $E$($m$).

      <dt>'EllipticE[phi|$m$]'
      <dd>computes the complete elliptic integral of the second kind $E$($m$|$phi$).
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
    messages = {
        "argt": "EllipticE called with `` arguments; 1 or 2 arguments are expected.",
    }
    summary_text = "elliptic integral of the second kind E(ϕ|m)"
    sympy_name = "elliptic_e"

    def eval_default(self, args, evaluation):
        "%(name)s[args___]"
        evaluation.message("EllipticE", "argt", Integer(len(args.elements)))

    def eval_m(self, m, evaluation):
        "%(name)s[m_]"
        sympy_arg = numerify(m, evaluation).to_sympy()
        try:
            return from_sympy(sympy.elliptic_e(sympy_arg))
        except Exception:
            return

    def eval_phi_m(self, phi, m, evaluation):
        "%(name)s[phi_, m_]"
        sympy_args = [numerify(a, evaluation).to_sympy() for a in (phi, m)]
        try:
            return from_sympy(sympy.elliptic_e(*sympy_args))
        except Exception:
            return


class EllipticF(SympyFunction):
    """
    <url>
    :Complete elliptic integral of the first kind:
    https://en.wikipedia.org/wiki/\
Elliptic_integral#Complete_elliptic_integral_of_the_first_kind</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/\
special.html#sympy.functions.special.elliptic_integrals.elliptic_f</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/EllipticF.html</url>)

    <dl>
      <dt>'EllipticF[$phi$, $m$]'
      <dd>computes the elliptic integral of the first kind $F$($ϕ$|$m$).
    </dl>

    >> EllipticF[0.3, 0.8]
     = 0.303652

    EllipticF is zero when the first argument is zero:
    >> EllipticF[0, 0.8]
     = 0

    """

    attributes = A_NUMERIC_FUNCTION | A_PROTECTED
    messages = {
        "argx": "EllipticF called with `` arguments; 1 argument is expected.",
    }
    summary_text = "elliptic integral F(ϕ|m)"
    sympy_name = "elliptic_f"

    def eval_default(self, args, evaluation):
        "%(name)s[args___]"
        evaluation.message("EllipticE", "argx", Integer(len(args.elements)))

    def eval(self, phi, m, evaluation):
        "%(name)s[phi_, m_]"
        sympy_args = [numerify(a, evaluation).to_sympy() for a in (phi, m)]
        try:
            return from_sympy(sympy.elliptic_f(*sympy_args))
        except Exception:
            return


class EllipticK(SympyFunction):
    """
    <url>
    :Complete elliptic integral of the first kind:
    https://en.wikipedia.org/wiki/Elliptic_integral#Complete_elliptic_integral_of_the_first_kind</url> (<url>:SymPy:
    https://docs.sympy.org/latest/modules/functions/special.html</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/EllipticK.html</url>)

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
    messages = {
        "argx": "EllipticK called with `` arguments; 1 argument is expected.",
    }
    summary_text = "elliptic integral of the first kind K(m)"
    sympy_name = "elliptic_k"

    def eval_default(self, args, evaluation):
        "%(name)s[args___]"
        evaluation.message("EllipticK", "argx", Integer(len(args.elements)))

    def eval(self, m, evaluation):
        "%(name)s[m_]"
        args = numerify(m, evaluation).get_sequence()
        sympy_args = [a.to_sympy() for a in args]
        try:
            return from_sympy(sympy.elliptic_k(*sympy_args))
        except Exception:
            return


class EllipticPi(SympyFunction):
    """
    <url>
    :Complete elliptic integral of the third kind:
    https://en.wikipedia.org/wiki/Elliptic_integral#Incomplete_elliptic_integral_of_the_third_kind</url> (<url>:SymPy:
    https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.elliptic_integrals.elliptic_pi</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/EllipticPi.html</url>)

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
    messages = {
        "argt": "EllipticPi called with `` arguments; 2 or 3 arguments are expected.",
    }
    summary_text = "elliptic integral of the third kind P(n|m)"
    sympy_name = "elliptic_pi"

    def eval_default(self, args, evaluation):
        "%(name)s[args___]"
        evaluation.message("EllipticPi", "argt", Integer(len(args.elements)))

    def eval_n_m(self, n, m, evaluation):
        "%(name)s[n_, m_]"
        sympy_m = to_numeric_sympy_args(m, evaluation)[0]
        sympy_n = to_numeric_sympy_args(n, evaluation)[0]
        try:
            return from_sympy(sympy.elliptic_pi(sympy_m, sympy_n))
        except Exception:
            return

    def eval_n_phi_m(self, n, phi, m, evaluation):
        "%(name)s[n_, phi_, m_]"
        sympy_n = to_numeric_sympy_args(n, evaluation)[0]
        sympy_phi = to_numeric_sympy_args(m, evaluation)[0]
        sympy_m = to_numeric_sympy_args(m, evaluation)[0]
        try:
            result = from_sympy(sympy.elliptic_pi(sympy_n, sympy_phi, sympy_m))
            return result
        except Exception:
            return
