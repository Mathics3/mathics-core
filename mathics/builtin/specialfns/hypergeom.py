"""
Hypergeometric functions

See also <url>
:Chapter 15 Hypergeometric Functions in the Digital Library of Mathematical Functions:
https://dlmf.nist.gov/15</url>.
"""

import mpmath
import sympy

import mathics.eval.tracing as tracing
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
from mathics.core.systemsymbols import SymbolComplexInfinity, SymbolMachinePrecision
from mathics.eval.specialfns.hypergeom import (
    eval_Hypergeometric2F1,
    eval_HypergeometricPQF,
    eval_N_HypergeometricPQF,
)


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
    >> HypergeometricPFQ[{3}, {2}, 1.]
     = 4.07742

    The following special cases are handled:
    >> HypergeometricPFQ[{}, {}, z]
     = 1
    >> HypergeometricPFQ[{0}, {b}, z]
     = 1
    >> Hypergeometric1F1[b, b, z]
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
        return eval_HypergeometricPQF(a, b, z)

    def eval_N(self, a, b, z, prec, evaluation: Evaluation):
        "N[HypergeometricPFQ[a_, b_, z_], prec_]"
        # FIXME: prec is not used. Why?
        return eval_N_HypergeometricPQF(a, b, z)

    def eval_numeric(self, a, b, z, evaluation: Evaluation):
        "HypergeometricPFQ[a:{__?NumericQ}, b:{__?NumericQ}, z_?MachineNumberQ]"
        return self.eval_N(a, b, z, SymbolMachinePrecision, evaluation)


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
    >> Hypergeometric1F1[3, 2, 1.]
     = 4.07742

    Plot 'M'[3, 2, x] from 0 to 2 in steps of 0.5:
    >> Plot[Hypergeometric1F1[3, 2, x], {x, 0.5, 2}]
     = -Graphics-
    Here, plot explicitly requests a numerical evaluation.
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    mpmath_name = "hymp1f1"
    nargs = {3}
    rules = {
        "Hypergeometric1F1[a_, b_, z_]": "HypergeometricPFQ[{a},{b},z]",
    }
    summary_text = "compute Kummer confluent hypergeometric function"
    sympy_name = ""


class Hypergeometric2F1(MPMathFunction):
    """
    <url>
    :Hypergeometric function: https://en.wikipedia.org/wiki/Hypergeometric_function</url> (<url>
    :mpmath: https://mpmath.org/doc/current/functions/hypergeometric.html#mpmath.hyp2f1</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/Hypergeometric2F1.html</url>)
    <dl>
      <dt>'Hypergeometric2F1'[$a$, $b$, $c$, $z$]
      <dd>returns ${}_2 F_1(a; b; c; z)$.
    </dl>

    >> Hypergeometric2F1[2., 3., 4., 5.0]
     = 0.156542 + 0.150796 I

    Evaluate symbolically:
    >> Hypergeometric2F1[2, 3, 4, x]
     = 6 Log[1 - x] / x ^ 3 + (-6 + 3 x) / (-x ^ 2 + x ^ 3)

    Evaluate using complex arguments:
    >> Hypergeometric2F1[2 + I, -I, 3/4, 0.5 - 0.5 I]
     = -0.972167 - 0.181659 I

    Plot over a subset of the reals:
    >> Plot[Hypergeometric2F1[1/3, 1/3, 2/3, x], {x, -1, 1}]
     = -Graphics-
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    mpmath_name = "hyp2f1"
    nargs = {4}
    summary_text = "compute Gauss hypergeometric function function"
    sympy_name = "hyper"

    def eval(self, a, b, c, z, evaluation: Evaluation):
        "Hypergeometric2F1[a_, b_, c_, z_]"

        return eval_Hypergeometric2F1(a, b, c, z)


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
    >> MeijerG[{{1, 2},{}}, {{3},{}}, 1.]
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
            a_sympy = [[e2.to_sympy() for e2 in e1] for e1 in a]
            b_sympy = [[e2.to_sympy() for e2 in e1] for e1 in b]
            result_sympy = tracing.run_sympy(
                sympy.meijerg, a_sympy, b_sympy, z.to_sympy()
            )
            return from_sympy(result_sympy)
        except Exception:
            pass

    def eval_N(self, a, b, z, prec, evaluation: Evaluation):
        "N[MeijerG[a_, b_, z_], prec_]"
        try:
            result_mpmath = tracing.run_mpmath(
                mpmath.meijerg, a.to_python(), b.to_python(), z.to_python()
            )
            return from_mpmath(result_mpmath)
        except ZeroDivisionError:
            return SymbolComplexInfinity
        except Exception:
            pass

    def eval_numeric(self, a, b, z, evaluation: Evaluation):
        "MeijerG[a:{___List?(AllTrue[#, NumericQ, Infinity]&)}, b:{___List?(AllTrue[#, NumericQ, Infinity]&)}, z_?MachineNumberQ]"
        return self.eval_N(a, b, z, SymbolMachinePrecision, evaluation)


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
    Result is symbollicaly simplified, where possible:
    >> HypergeometricU[3, 2, 1]
     = MeijerG[{{-2}, {}}, {{0, -1}, {}}, 1] / 2
    >> HypergeometricU[1,4,8]
     = HypergeometricU[1, 4, 8]
    unless a numerical evaluation is explicitly requested:
    >> HypergeometricU[3, 2, 1] // N
     = 0.105479
    >> HypergeometricU[3, 2, 1.]
     = 0.105479

    Plot 'U'[3, 2, x] from 0 to 10 in steps of 0.5:
    >> Plot[HypergeometricU[3, 2, x], {x, 0.5, 10}]
     = -Graphics-

    We handle this special case:
    >> HypergeometricU[0, b, z]
     = 1
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = "hyperu"
    nargs = {3}
    rules = {
        "HypergeometricU[0, c_, z_]": "1",
        "HypergeometricU[a_, b_, z_] /; (a > 0) && (a-b+1 > 0)": "MeijerG[{{1-a},{}},{{0,1-b},{}},z]/Gamma[a]/Gamma[a-b+1]",
    }
    summary_text = "compute the Tricomi confluent hypergeometric function"
    sympy_name = ""
