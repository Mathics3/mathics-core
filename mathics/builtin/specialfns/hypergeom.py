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
from mathics.core.builtin import MPMathFunction, SympyFunction
from mathics.core.convert.sympy import from_sympy
from mathics.core.number import FP_MANTISA_BINARY_DIGITS
from mathics.eval.arithmetic import run_mpmath
from mathics.core.evaluation import Evaluation


class HypergeometricPFQ(MPMathFunction):
    """
    <url>
    :Generalized hypergeometric function: https://en.wikipedia.org/wiki/Generalized_hypergeometric_function</url> (<url>
    :mpmath: https://mpmath.org/doc/current/functions/hypergeometric.html#hyper</url>, <url>
    :sympy: https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.hyper.hyper</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/HypergeometricPFQ.html</url>)
    <dl>
      <dt>'HypergeometricPFQ'[${a_1, a_2, a_p}, {b_1, b_2, b_q}, z$]
      <dd>returns ${}_p F_q({a_1, a_2, a_p}, {b_1, b_2, b_q}, z)$.
    </dl>

    >> HypergeometricPFQ[{2}, {2}, 1]
     = 2.71828

    We handle the following special cases:
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

    def eval_numeric(self, a, b, z, evaluation: Evaluation):
        "HypergeometricPFQ[a:{__?NumericQ}, b:{__?NumericQ}, z_?NumericQ]"
        return self.eval_N(a, b, z, evaluation)

    def eval_N(self, a, b, z, evaluation: Evaluation):
        "N[HypergeometricPFQ[a_, b_, z_]]"
        try:
            return run_mpmath(
                mpmath.hyper, tuple([a.to_python(), b.to_python(), z.to_python()]),
                FP_MANTISA_BINARY_DIGITS
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
      <dd>returns $M(a, b, z)$.
    </dl>
    >> Hypergeometric1F1[3, 2, 1]
     = 4.07742
    >> Hypergeometric1F1[a, b, z]
     = HypergeometricPFQ[{a}, {b}, z]

    Plot 'M'[3, 2, x] from 0 to 2 in steps of 0.5:
    >> Plot[Hypergeometric1F1[3, 2, x], {x, 0.5, 2}]
     = -Graphics-
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = ""
    nargs = {3}
    rules = {
        "Hypergeometric1F1[a_, b_, z_]": "HypergeometricPFQ[{a},{b},z]",
    }
    summary_text = "compute Kummer confluent hypergeometric function"
    sympy_name = ""
