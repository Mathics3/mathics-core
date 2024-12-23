# -*- coding: utf-8 -*-
"""
Recurrence and Sum Functions

A recurrence relation is an equation that recursively defines a \
sequence or multidimensional array of values, once one or more initial \
terms are given; each further term of the sequence or array is defined \
as a function of the preceding terms.
"""


from sympy.functions.combinatorial.numbers import stirling

from mathics.core.atoms import Integer
from mathics.core.attributes import (
    A_LISTABLE,
    A_NUMERIC_FUNCTION,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, MPMathFunction
from mathics.core.evaluation import Evaluation


class Fibonacci(MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Fibonacci.html</url>

    <dl>
      <dt>'Fibonacci[$n$]'
      <dd>computes the $n$th Fibonacci number.
      <dt>'Fibonacci[$n$, $x$]'
      <dd>computes the Fibonacci polynomial $F$_$n$($x$).
    </dl>

    >> Fibonacci[0]
     = 0
    >> Fibonacci[1]
     = 1
    >> Fibonacci[10]
     = 55
    >> Fibonacci[200]
     = 280571172992510140037611932413038677189525
    >> Fibonacci[7, x]
     = 1 + 6 x ^ 2 + 5 x ^ 4 + x ^ 6
    """

    nargs = {1}
    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED | A_READ_PROTECTED
    sympy_name = "fibonacci"
    mpmath_name = "fibonacci"
    summary_text = "Fibonacci's numbers"

    rules = {
        "Fibonacci[0, x_]": "0",
        "Fibonacci[n_Integer?Negative, x_]": "Fibonacci[-n, x]",
    }


class HarmonicNumber(MPMathFunction):
    """
    <url>:Harmonic Number:https://en.wikipedia.org/wiki/Harmonic_number</url> \
    (<url>:WMA link:https://reference.wolfram.com/language/ref/HarmonicNumber.html</url>)

    <dl>
      <dt>'HarmonicNumber[n]'
      <dd>returns the $n$th harmonic number.
    </dl>

    >> Table[HarmonicNumber[n], {n, 8}]
     = {1, 3 / 2, 11 / 6, 25 / 12, 137 / 60, 49 / 20, 363 / 140, 761 / 280}

    >> HarmonicNumber[3.8]
     = 2.03806
    """

    rules = {
        "HarmonicNumber[-1]": "ComplexInfinity",
    }
    summary_text = "Harmonic numbers"
    mpmath_name = "harmonic"
    sympy_name = "harmonic"


class LinearRecurrence(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/LinearRecurrence.html</url>

    <dl>
      <dt>'LinearRecurrence[$ker$, $init$, $n$]'
      <dd>computes $n$ terms of the linear recurrence with kernel $ker$ and initial values $init$
    </dl>

    >> LinearRecurrence[{1, 1}, {1, 1}, 10]
     = {1, 1, 2, 3, 5, 8, 13, 21, 34, 55}
    >> LinearRecurrence[{1, 1}, {1, 1}, {5, 5}]
     = {5}
    """

    attributes = A_PROTECTED | A_READ_PROTECTED
    summary_text = "linear recurrence"

    rules = {
        "LinearRecurrence[ker_List, init_List, n_Integer]": "Nest[Append[#, Reverse[ker] . Take[#, -Length[ker]]] &, init, n - Length[init]]",
        "LinearRecurrence[ker_List, init_List, {n_Integer?Positive}]": "LinearRecurrence[ker, init, n][[n]]",
        "LinearRecurrence[ker_List, init_List, {nmin_Integer?Positive, nmax_Integer?Positive}]": "LinearRecurrence[ker, init, nmax][[nmin;;nmax]]",
    }


# Note: WL allows StirlingS1[{2, 4, 6}, 2], but we don't (yet).
class StirlingS1(Builtin):
    """
    <url>
    :Stirling numbers of first kind:
    https://en.wikipedia.org/wiki/Stirling_numbers_of_the_first_kind</url> \
    (<url>
    :WMA link:
    https://reference.wolfram.com/language/ref/StirlingS1.html</url>)

    <dl>
      <dt>'StirlingS1[$n$, $m$]'
      <dd>gives the Stirling number of the first kind $ _n^m$.
    </dl>

    Integer mathematical function, suitable for both symbolic and numerical manipulation.
    gives the number of permutations of $n$ elements that contain exactly $m$ cycles.

    >> StirlingS1[50, 1]
    = -608281864034267560872252163321295376887552831379210240000000000
    """

    attributes = A_LISTABLE | A_PROTECTED

    nargs = {2}
    summary_text = "Stirling numbers of the first kind"
    sympy_name = "functions.combinatorial.stirling"
    mpmath_name = "stirling1"

    def eval(self, n: Integer, m: Integer, evaluation: Evaluation):
        "%(name)s[n_Integer, m_Integer]"
        n_value = n.value
        m_value = m.value
        return Integer(stirling(n_value, m_value, kind=1, signed=True))


class StirlingS2(Builtin):
    """
    <url>
    :Stirling numbers of second kind:
    https://en.wikipedia.org/wiki/Stirling_numbers_of_the_second_kind</url> \
    (<url>
    :WMA link
    :https://reference.wolfram.com/language/ref/StirlingS2.html</url>)

    <dl>
      <dt>'StirlingS2[$n$, $m$]'
      <dd>gives the Stirling number of the second kind  _n^m.
    </dl>

    returns the number of ways of partitioning a set of $n$ elements into $m$ \
    non empty subsets.

    >> Table[StirlingS2[10, m], {m, 10}]
    = {1, 511, 9330, 34105, 42525, 22827, 5880, 750, 45, 1}
    """

    attributes = A_LISTABLE | A_PROTECTED
    nargs = {2}
    sympy_name = "functions.combinatorial.numbers.stirling"
    mpmath_name = "stirling2"
    summary_text = "Stirling numbers of the second kind"

    def eval(self, m: Integer, n: Integer, evaluation: Evaluation):
        "%(name)s[n_Integer, m_Integer]"
        n_value = n.value
        m_value = m.value
        return Integer(stirling(n_value, m_value, kind=2))
