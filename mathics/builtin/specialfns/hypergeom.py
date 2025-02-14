"""
Hypergeometric functions

See also <url>
:Chapter 15 Hypergeometric Functions in the Digital Library of Mathematical Functions:
https://dlmf.nist.gov/15</url>.
"""

import mpmath
import sympy

from mathics.core.attributes import (
    A_LISTABLE,
    A_N_HOLD_FIRST,
    A_NUMERIC_FUNCTION,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import MPMathFunction
from mathics.core.convert.sympy import from_sympy
from mathics.core.evaluation import Evaluation
from mathics.core.number import FP_MANTISA_BINARY_DIGITS
from mathics.core.symbols import SymbolMachinePrecision
from mathics.eval.arithmetic import run_mpmath


class HypergeometricPFQ(MPMathFunction):
    """
    <url>
    :Generalized hypergeometric function: https://en.wikipedia.org/wiki/Generalized_hypergeometric_function</url> (<url>
    :mpmath: https://mpmath.org/doc/current/functions/hypergeometric.html#hyper</url>, <url>
    :sympy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.hyper.hyper</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/HypergeometricPFQ.html</url>)
    <dl>
      <dt>'HypergeometricPFQ'[${a_1, ..., a_p}, {b_1, ..., b_q}, z$]
      <dd>returns ${}_p F_q({a_1, ..., a_p}; {b_1, ..., b_q}; z)$.
    </dl>
    >> HypergeometricPFQ[{2}, {2}, 1]
     = E

    Result is symbollicaly simplified by default:
    >> HypergeometricPFQ[{3}, {2}, 1]
     = HypergeometricPFQ[{3}, {2}, 1]
    unless a numerical evaluation is explicitly requested:
    >> HypergeometricPFQ[{3}, {2}, 1] // N
     = 4.07742

    The following special cases are handled:
    >> HypergeometricPFQ[{}, {}, z]
     = 1
    >> HypergeometricPFQ[{0}, {b}, z]
     = 1
    >> HypergeometricPFQ[{b}, {b}, z]
     = E ^ z
    """

    attributes = A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = "hyper"
    nargs = {3}
    rules = {
        "HypergeometricPFQ[{}, {}, z_]": "1",
        "HypergeometricPFQ[{0}, b_, z_]": "1",
        "HypergeometricPFQ[b_, b_, z_]": "Exp[z]",
    }
    summary_text = "compute the generalized hypergeometric function"
    sympy_name = "hyper"

    def eval(self, a, b, z, evaluation: Evaluation):
        "HypergeometricPFQ[a_, b_, z_]"
        try:
            a_sympy = [e.to_sympy() for e in a]
            b_sympy = [e.to_sympy() for e in b]
            return from_sympy(sympy.hyper(a_sympy, b_sympy, z.to_sympy()))
        except Exception:
            pass

    def eval_N(self, a, b, z, prec, evaluation: Evaluation):
        "N[HypergeometricPFQ[a_, b_, z_], prec_]"
        try:
            return run_mpmath(
                mpmath.hyper,
                tuple([a.to_python(), b.to_python(), z.to_python()]),
                FP_MANTISA_BINARY_DIGITS,
            )
        except Exception:
            pass


class Hypergeometric1F1(MPMathFunction):
    """
    <url>
    :Kummer confluent hypergeometric function: https://en.wikipedia.org/wiki/Confluent_hypergeometric_function</url> (<url>
    :mpmath: https://mpmath.org/doc/current/functions/hypergeometric.html#hyper</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/Hypergeometric1F1.html</url>)
    <dl>
      <dt>'Hypergeometric1F1'[$a$, $b$, $z$]
      <dd>returns ${}_1 F_1(a; b; z)$.
    </dl>

    Result is symbollicaly simplified by default:
    >> Hypergeometric1F1[3, 2, 1]
     = HypergeometricPFQ[{3}, {2}, 1]
    unless a numerical evaluation is explicitly requested:
    >> Hypergeometric1F1[3, 2, 1] // N
     = 4.07742

    Plot 'M'[3, 2, x] from 0 to 2 in steps of 0.5:
    >> Plot[Hypergeometric1F1[3, 2, x], {x, 0.5, 2}]
     = -Graphics-
    Here, plot explicitly requests a numerical evaluation.
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = ""
    nargs = {3}
    rules = {
        "Hypergeometric1F1[a_, b_, z_]": "HypergeometricPFQ[{a},{b},z]",
    }
    summary_text = "compute Kummer confluent hypergeometric function"
    sympy_name = ""


class MeijerG(MPMathFunction):
    """
    <url>
    :Meijer G-function: https://en.wikipedia.org/wiki/Meijer_G-function</url> (<url>
    :mpmath: https://mpmath.org/doc/current/functions/hypergeometric.html#meijerg</url>, <url>
    :sympy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.hyper.meijerg</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/MeijerG.html</url>)
    <dl>
      <dt>'MeijerG'[${{a_1, ..., a_n}, {a_{n+1}, ..., a_p}}, {{b_1, ..., b_m}, {b_{m+1}, ..., a_q}}, z$]
      <dd>returns $G^{m,n}_{p,q}(z | {a_1, ..., a_p}; {b_1, ..., b_q})$.
    </dl>
    Result is symbollicaly simplified by default:
    >> MeijerG[{{1, 2}, {}}, {{3}, {}}, 1]
     = MeijerG[{{1, 2}, {}}, {{3}, {}}, 1]
    unless a numerical evaluation is explicitly requested:
    >> MeijerG[{{1, 2},{}}, {{3},{}}, 1] // N
     = 0.210958
    """

    attributes = A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = "meijerg"
    nargs = {3}
    rules = {}
    summary_text = "compute the Meijer G-function"
    sympy_name = "meijerg"

    def eval(self, a, b, z, evaluation: Evaluation):
        "MeijerG[a_, b_, z_]"
        try:
            a_sympy = [e.to_sympy() for e in a]
            b_sympy = [e.to_sympy() for e in b]
            return from_sympy(sympy.meijerg(a_sympy, b_sympy, z.to_sympy()))
        except Exception:
            pass

    def eval_N(self, a, b, z, prec, evaluation: Evaluation):
        "N[MeijerG[a_, b_, z_], prec_]"
        try:
            return run_mpmath(
                mpmath.meijerg,
                tuple([a.to_python(), b.to_python(), z.to_python()]),
                FP_MANTISA_BINARY_DIGITS,
            )
        except Exception:
            pass


class HypergeometricU(MPMathFunction):
    """
    <url>
    :Confluent hypergeometric function: https://en.wikipedia.org/wiki/Confluent_hypergeometric_function</url> (<url>
    :mpmath: https://mpmath.org/doc/current/functions/bessel.html#mpmath.hyperu</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/HypergeometricU.html</url>)
    <dl>
      <dt>'HypergeometricU'[$a$, $b$, $z$]
      <dd>returns $U(a, b, z)$.
    </dl>
    Result is symbollicaly simplified by default:
    >> HypergeometricU[3, 2, 1]
     = MeijerG[{{1, 2}, {}}, {{3}, {}}, 1]
    unless a numerical evaluation is explicitly requested:
    >> HypergeometricU[3, 2, 1] // N
     = 0.210958

    Plot 'U'[3, 2, x] from 0 to 10 in steps of 0.5:
    >> Plot[HypergeometricU[3, 2, x], {x, 0.5, 10}]
     = -Graphics-

    We handle this special case:
    >> HypergeometricU[0, b, z]
     = 1
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = ""
    nargs = {3}
    rules = {
        "HypergeometricU[0, c_, z_]": "1",
        "HypergeometricU[a_, b_, z_]": "MeijerG[{{1-a},{}},{{0,1-b},{}},z]/Gamma[a]/Gamma[a-b+1]",
    }
    summary_text = "compute the Tricomi confluent hypergeometric function"
    sympy_name = ""
