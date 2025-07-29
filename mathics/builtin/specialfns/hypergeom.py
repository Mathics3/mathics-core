"""
Hypergeometric functions

See also <url>
:Chapter 15 Hypergeometric Functions in the Digital Library of Mathematical Functions:
https://dlmf.nist.gov/15</url>.
"""

import mpmath

import mathics.eval.tracing as tracing
from mathics.core.atoms import Integer1, MachineReal1, Number
from mathics.core.attributes import (
    A_LISTABLE,
    A_NUMERIC_FUNCTION,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import MPMathFunction
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolComplexInfinity, SymbolMachinePrecision
from mathics.eval.specialfns.hypergeom import (
    eval_Hypergeometric1F1,
    eval_Hypergeometric2F1,
    eval_HypergeometricPQF,
    eval_MeijerG,
    eval_N_HypergeometricPQF,
)


class Hypergeometric1F1(MPMathFunction):
    """
    <url>
    :Kummer confluent hypergeometric function: https://en.wikipedia.org/wiki/Confluent_hypergeometric_function</url> (<url>
    :mpmath: https://mpmath.org/doc/current/functions/hypergeometric.html#hyp1f1</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/Hypergeometric1F1.html</url>)
    <dl>
      <dt>'Hypergeometric1F1'[$a$, $b$, $z$]
      <dd>returns ${}_1 F_1(a; b; z)$.
    </dl>

    Numeric evaluation:
    >> Hypergeometric1F1[1, 2, 3.0]
     = 6.36185

    Plot over a subset of reals:
    >> Plot[Hypergeometric1F1[1, 2, x], {x, -5, 5}]
     = -Graphics-

    >> Plot[{Hypergeometric1F1[1/2, Sqrt[2], x], Hypergeometric1F1[1/2, Sqrt[3], x], Hypergeometric1F1[1/2, Sqrt[5], x]}, {x, -4, 4}]
     = -Graphics-

    >> Plot[{Hypergeometric1F1[Sqrt[3], Sqrt[2], z], -0.01}, {z, -10, -2}]
     = -Graphics-

    >> Plot[{Hypergeometric1F1[Sqrt[2], b, 1], Hypergeometric1F1[Sqrt[5], b, 1], Hypergeometric1F1[Sqrt[7], b, 1]}, {b, -3, 3}]
     = -Graphics-

    Compute the elementwise values of an array:
    >> Hypergeometric1F1[1, 1, {{1, 0}, {0, 1}}]
     = {{E, 1}, {1, E}}

    >> Hypergeometric1F1[1/2, 1, x]
     = BesselI[0, x / 2] E ^ (x / 2)

    Evaluate using complex arguments:
    >> Hypergeometric1F1[2 + I, 2, 0.5]
     = 1.61833 + 0.379258 I

    Large numbers are supported:
    >> Hypergeometric1F1[3, 4, 10^10]
     = -3 / 500000000000000000000000000000 + 149999999970000000003 E ^ 10000000000 / 500000000000000000000000000000

    'Hypergeometric1F1' evaluates to simpler functions for certain parameters:
    >> Hypergeometric1F1[1/2, 1, x]
     = BesselI[0, x / 2] E ^ (x / 2)

    >> Hypergeometric1F1[2, 1, x]
     = (1 + x) E ^ x

    >> Hypergeometric1F1[1, 1/2, x]
     = -Sqrt[x] (-E ^ (-x) / Sqrt[x] - Sqrt[Pi] Erf[Sqrt[x]]) E ^ x
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    mpmath_name = "hyp1f1"
    nargs = {3}

    rules = {
        "Hypergeometric1F1[0, c_, z_?MachineNumberQ]": "1.0",
        "Hypergeometric1F1[0, c_, z_]": "1",
    }

    summary_text = "compute Kummer confluent hypergeometric function"
    sympy_name = ""

    def eval(self, a, b, z, evaluation: Evaluation):
        "Hypergeometric1F1[a_, b_, z_]"

        # SymPy returns E ^ z for Hypergeometric1F1[0,0,z], but
        # WMA gives 1.  Therefore, we add the below code to give the WMA
        # behavior. If SymPy switches, this code be eliminated.
        if hasattr(a, "is_zero") and a.is_zero:
            return (
                MachineReal1
                if a.is_machine_precision()
                or hasattr(z, "machine_precision")
                and z.is_machine_precision()
                else Integer1
            )

        return eval_Hypergeometric1F1(a, b, z)


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


class HypergeometricPFQ(MPMathFunction):
    """
    <url>
    :Generalized hypergeometric function: https://en.wikipedia.org/wiki/Generalized_hypergeometric_function</url> (<url>
    :mpmath: https://mpmath.org/doc/current/functions/hypergeometric.html#hyper</url>, <url>
    :SymPy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.hyper.hyper</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/HypergeometricPFQ.html</url>)
    <dl>
      <dt>'HypergeometricPFQ'[${a_1, ..., a_p}, {b_1, ..., b_q}, z$]
      <dd>returns ${}_p F_q({a_1, ..., a_p}; {b_1, ..., b_q}; z)$.
    </dl>
    >> HypergeometricPFQ[{2}, {2}, 1]
     = E

    Result is symbollicaly simplified by default:
    >> HypergeometricPFQ[{3}, {2}, 1]
     = 3 E / 2

    unless a numerical evaluation is explicitly requested:
    >> HypergeometricPFQ[{3}, {2}, 1] // N
     = 4.07742

    >> HypergeometricPFQ[{3}, {2}, 1.]
     = 4.07742

    >> Plot[HypergeometricPFQ[{1, 1}, {3, 3, 3}, x], {x, -30, 30}]
     = -Graphics-

    >> HypergeometricPFQ[{1, 1, 2}, {3, 3}, z]
     = -4 PolyLog[2, z] / z ^ 2 + 4 Log[1 - z] / z ^ 2 - 4 Log[1 - z] / z + 8 / z

    The following special cases are handled:
    >> HypergeometricPFQ[{}, {}, z]
     = E ^ z
    >> HypergeometricPFQ[{0}, {b}, z]
     = 1

     >> HypergeometricPFQ[{1, 1, 3}, {2, 2}, x]
      = -Log[1 - x] / (2 x) - 1 / (-2 + 2 x)

    'HypergeometricPFQ' evaluates to a polynomial if any of the parameters $a_k$ is a non-positive integer:
    >> HypergeometricPFQ[{-2, a}, {b}, x]
     = (-2 a x (1 + b) + a x ^ 2 (1 + a) + b (1 + b)) / (b (1 + b))

    Value at origin:
    >> HypergeometricPFQ[{a1, b2, a3}, {b1, b2, b3}, 0]
     = 1
    """

    attributes = A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = "hyper"
    nargs = {3}

    summary_text = "compute the generalized hypergeometric function"
    sympy_name = "hyper"

    def eval(self, a, b, z, evaluation: Evaluation):
        "HypergeometricPFQ[a_, b_, z_]"

        # FIXME: a lot more checking could be done here.
        if not (isinstance(a, ListExpression)):
            evaluation.message(
                "HypergeometricPQF",
                "hdiv",
                Expression(Symbol("Hypergeometric"), a, b, z),
            )

        # SymPy returns E for HypergeometricPFQ[{0},{0},Number], but
        # WMA gives 1.  Therefore, we add the below code to give the WMA
        # behavior. If SymPy switches, this code be eliminated.
        if (
            len(a.elements) > 0
            and hasattr(a[0], "is_zero")
            and a[0].is_zero
            and isinstance(z, Number)
        ):
            return MachineReal1 if a[0].is_machine_precision() else Integer1

        # FIXME: This isn't complete. If parameters "a" or "b" contain MachineReal
        # numbers then the results should be MachineReal as well.
        if z.is_machine_precision():
            return eval_N_HypergeometricPQF(a, b, z)

        return eval_HypergeometricPQF(a, b, z)

    def eval_N(self, a, b, z, prec, evaluation: Evaluation):
        "N[HypergeometricPFQ[a_, b_, z_], prec_]"
        # FIXME: prec is not used. It should be though.
        return eval_N_HypergeometricPQF(a, b, z)


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


class MeijerG(MPMathFunction):
    """
    <url>
    :Meijer G-function: https://en.wikipedia.org/wiki/Meijer_G-function</url> (<url>
    :mpmath: https://mpmath.org/doc/current/functions/hypergeometric.html#meijerg</url>, <url>
    :SymPy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.hyper.meijerg</url>, <url>
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
        return eval_MeijerG(a, b, z)

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
