"""
Hypergeometric functions

See also <url>
:Chapter 15 Bessel Functions in the Digital Library of Mathematical Functions:
https://dlmf.nist.gov/15</url>.
"""

import mpmath

from mathics.core.atoms import Integer
from mathics.core.attributes import (
    A_LISTABLE,
    A_N_HOLD_FIRST,
    A_NUMERIC_FUNCTION,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, MPMathFunction
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.evaluation import Evaluation
from mathics.core.number import (
    FP_MANTISA_BINARY_DIGITS,
    PrecisionValueError,
    get_precision,
    prec as _prec,
)


class Hypergeometric1F1(MPMathFunction):
    """
    <url>
    :Kummer confluent hypergeometric function: https://en.wikipedia.org/wiki/Confluent_hypergeometric_function</url> (<url>
    :mpmath: https://mpmath.org/doc/current/functions/hypergeometric.html#mpmath.hyp1f1</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/Hypergeometric1F1.html</url>)
    <dl>
      <dt>'Hypergeometric1F1'[$a$, $b$, $z$]
      <dd>returns $M(a, b, z)$.
    </dl>

    >> Hypergeometric1F1[3, 2, 1.]
     = 4.07742

    Plot 'M'[3, 2, x] from 0 to 2 in steps of 0.5:
    >> Plot[Hypergeometric1F1[3, 2, x], {x, 0.5, 2}]
     = -Graphics-

    We handle the following special cases:
    >> Hypergeometric1F1[0, b, z]
     = 1
    >> Hypergeometric1F1[b, b, z]
     = E ^ z
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    mpmath_name = "hyp1f1"
    nargs = {3}
    rules = {
        "Hypergeometric1F1[0, b_, z_]": "1",
        "Hypergeometric1F1[b_, b_, z_]": "Exp[z]",
    }
    summary_text = "compute Kummer confluent hypergeometric function"
    sympy_name = ""
