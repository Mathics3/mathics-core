# -*- coding: utf-8 -*-

"""
Division-Related Functions
"""

import sys
from typing import List, Optional, Union

from sympy import Q, ask

from mathics.core.atoms import Integer
from mathics.core.attributes import (
    A_FLAT,
    A_LISTABLE,
    A_NUMERIC_FUNCTION,
    A_ONE_IDENTITY,
    A_ORDERLESS,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, SympyFunction
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_bool
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolComplexInfinity,
    SymbolIndeterminate,
    SymbolQuotient,
    SymbolQuotientRemainder,
)
from mathics.eval.intfns.divlike import (
    eval_GCD,
    eval_LCM,
    eval_ModularInverse,
    eval_PowerMod,
    eval_Quotient,
)


class CompositeQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/CompositeQ.html</url>

    <dl>
      <dt>'CompositeQ'[$n$]
      <dd>returns 'True' if $n$ is a composite number
    </dl>

    <ul>
      <li>A composite number is a positive number that is the product of two \
          integers other than 1.
      <li>For negative integer $n$, 'CompositeQ[$n$]' is effectively equivalent \
          to 'CompositeQ[-$n$]'.
    </ul>

    >> Table[CompositeQ[n], {n, 0, 10}]
     = {False, False, False, False, True, False, True, False, True, True, True}
    """

    attributes = A_LISTABLE | A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = 1
    summary_text = "test whether a number is composite"

    def eval(self, n: Integer, evaluation: Evaluation):
        "CompositeQ[n_Integer]"
        return from_bool(ask(Q.composite(n.value)))


class Divisible(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Divisible.html</url>

    <dl>
      <dt>'Divisible'[$n$, $m$]
      <dd>returns 'True' if $n$ is divisible by $m$, and 'False' otherwise.
    </dl>

    <ul>
      <li>$n$ is divisible by $m$ if $n$ is the product of $m$ by an integer.
      <li>'Divisible[$n$,$m$]' is effectively equivalent to 'Mod[$n$,$m$]==0'.

    Test whether the number 10 is divisible by 2
    >> Divisible[10, 2]
     = True

    But the other way around is False: 2 is not divisible by 10:
    >> Divisible[2, 10]
     = False
    """

    attributes = A_LISTABLE | A_PROTECTED | A_READ_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = range(2, sys.maxsize)
    rules = {
        "Divisible[n_, m_]": "Mod[n, m] == 0",
    }
    summary_text = "test whether one number is divisible by the other"


class GCD(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/GCD.html</url>

    <dl>
      <dt>'GCD'[$n_1$, $n_2$, ...]
      <dd>computes the greatest common divisor of the given integers.
    </dl>

    >> GCD[20, 30]
     = 10
    >> GCD[10, y]
     = GCD[10, y]

    'GCD' is 'Listable':
    >> GCD[4, {10, 11, 12, 13, 14}]
     = {2, 1, 4, 1, 2}

    'GCD' does not work for rational numbers and Gaussian integers yet.
    """

    attributes = A_FLAT | A_LISTABLE | A_ONE_IDENTITY | A_ORDERLESS | A_PROTECTED
    summary_text = "compute the Greatest Common Divisor"
    sympy_name = "gcd"

    def eval(self, ns, evaluation: Evaluation) -> Optional[Integer]:
        "GCD[ns___Integer]"

        return eval_GCD(ns.get_sequence())


class LCM(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/LCM.html</url>

    <dl>
      <dt>'LCM'[$n_1$, $n_2$, ...]
      <dd>computes the least common multiple of the given integers.
    </dl>

    >> LCM[15, 20]
     = 60
    >> LCM[20, 30, 40, 50]
     = 600
    """

    attributes = A_FLAT | A_LISTABLE | A_ONE_IDENTITY | A_ORDERLESS | A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = range(1, sys.maxsize)
    messages = {
        "argm": "LCM called with 0 arguments; 1 or more arguments are expected.",
    }
    summary_text = "compute the Least Common Multiple"
    sympy_name = "lcm"

    def eval(self, ns: List[Integer], evaluation: Evaluation) -> Optional[Integer]:
        "LCM[ns___Integer]"

        ns_tuple = ns.get_sequence()
        if len(ns_tuple) == 0:
            evaluation.message("LCM", "argm")
            return
        return eval_LCM(ns_tuple)


class Mod(SympyFunction):
    """
    <url>:Congruence:https://en.wikipedia.org/wiki/Modular_arithmetic#Congruence</url> (<url>
    :SymPy:https://docs.sympy.org/latest/modules/core.html#sympy.core.mod.Mod</url>, <url>
    :WMA:https://reference.wolfram.com/language/ref/Mod.html</url>)

    <dl>
      <dt>'Mod'[$x$, $m$]
      <dd>returns $x$ modulo $m$.
    </dl>

    >> Mod[14, 6]
     = 2
    >> Mod[-3, 4]
     = 1
    >> Mod[-3, -4]
     = -3

    Plot a sequence with fixed modulus:
    >> DiscretePlot[Mod[n, 8], {n, 50}]
     = -Graphics-

    Plot a sequence with increasing modulus:
    >> DiscretePlot[Mod[100, m], {m, 30}]
     = -Graphics-

    Fermat's "little" theorem states that for a prime number $p$, and another number $a$ which is \
    relatively prime to that $a^{(p-1)} = 1_{mod\\:p}$:

    >> p=Prime[4]; Table[Mod[a^(p-1), p], {a, 1, p-1}]
     = {1, 1, 1, 1, 1, 1}

    #> Clear[p]

    Zero is not allowed as a modulus:
    >> Mod[5, 0]
     : The argument 0 in Mod[5, 0] should be nonzero.
     = Mod[5, 0]

    See also <url>
    :'PowerMod':
    /doc/reference-of-built-in-symbols/integer-functions/division-related-functions/powermod/</url>.
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = (2, 3)

    summary_text = "get the remainder in an integer division"
    sympy_name = "Mod"

    def eval(self, n: Integer, m: Integer, evaluation: Evaluation):
        "Mod[n_Integer, m_Integer]"

        n, m = n.value, m.value
        if m == 0:
            evaluation.message(
                "Mod",
                "divz",
                evaluation.current_expression,
            )
            return
        return Integer(n % m)


class ModularInverse(SympyFunction):
    """
    <url>
    :Modular multiplicative inverse:
    https://en.wikipedia.org/wiki/Modular_multiplicative_inverse</url> (<url>
    :SymPy:https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.mod_inverse</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/ModularInverse.html
    </url>)

    <dl>
      <dt>'ModularInverse'[$k$, $n$]
      <dd>returns the modular inverse $k$^(-1) mod $n$.
    </dl>

    'ModularInverse[$k$,$n$]' gives the smallest positive integer $r$ where the remainder \
    of the division of $r$ x $k$ by $n$ is equal to 1.

    >> ModularInverse[2, 3]
     = 2

    The following is be True for all values $n$, $k$ which have a modular inverse:
    >> k = 2; n = 3; Mod[ModularInverse[k, n] * k, n] == 1
     = True

    Some modular inverses just do not exists. For example when $k$ is a multiple of $n$:
    >> ModularInverse[k, k]
     = ModularInverse[2, 2]

    #> Clear[k, n]
    """

    attributes = A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = 2
    summary_text = "get the modular inverse $k^(-1)$ mod $n$"
    sympy_name = "mod_inverse"

    def eval(self, k: Integer, n: Integer, evaluation: Evaluation) -> Optional[Integer]:
        "ModularInverse[k_Integer, n_Integer]"
        return eval_ModularInverse(k.value, n.value)


class PowerMod(Builtin):
    """
    <url>:Modular exponentiation:
    https://en.wikipedia.org/wiki/Modular_exponentiation</url> (SymPy: <url>
    :mod_inverse:https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.mod_inverse</url>, <url>
    :nth_root_mod:https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.nth_root</url>, <url>
    :sqrt_mod:https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.sqrt_mod</url>, <url>
    :WMA link:https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.Pow</url> <url>
    https://reference.wolfram.com/language/ref/PowerMod.html</url>).

    <dl>
      <dt>'PowerMod'[$x$, $y$, $m$]
      <dd>computes $x$^$y$ modulo $m$.
      <dt>'PowerMod'[$x$, -1, $m$]
      <dd>computes modular inverse of $x$ modulo $m$.
      <dt>'PowerMod'[$x$, 1/$r$, $m$]
      <dd>computes a module $r$-th root of $x$.
    </dl>

    Compute 7 squared mod 5:
    >> PowerMod[7, 2, 5]
     = 4

    'PowerMod' is periodic:
    >> PowerMod[7 + 5, 2, 5]
    = 4

    Plot the sequence of 'PowerMod' using varying powers:
    >> DiscretePlot[PowerMod[m, 2, 11], {m, 1, 40}]
     = -Graphics-

    'PowerMod' can handle large integers:
    >> PowerMod[2, 10000000, 3]
     = 1

    >> PowerMod[3, -2, 10]
     = 9

    'PowerMod' works on square roots:
    >> PowerMod[3, 1/2, 2]
    = 1

    'PowerMod' works on nth roots other than a square root:
    >> PowerMod[11, 1/3, 19]
    = 5

    When $y$ is a root $1/r$, there may be more than one solution for 'PowerMod'.
    However, the result must satisfy $x^y = r$ mod $m$:

    > x=11; r=3; m=19; Mod[(PowerMod[x, 1/r, m] ^ r), m] == x
    = True

    #> Clear[x, r, m]

    Note the inverse relationship 'PowerMod' has when $y$ is negative one:
    >> PowerMod[3, -1, 11]
     = 4

    >> PowerMod[4, -1, 11]
     = 3

    Also, 'PowerMod' with $-y$, is inverse of 'PowerMod' with $y$:
    >> PowerMod[3, -10, 11]  == PowerMod[PowerMod[3, 10, 11], 10, 11]
     = True

    The first parameter, $x$ should be invertible for modulus $m$:
    >> PowerMod[0, -1, 2]
     : 0 is not invertible modulo 2.
     = PowerMod[0, -1, 2]

    Also, you should not use zero as a modulus for $y$:
    >> PowerMod[5, 2, 0]
     : The argument 0 in PowerMod[5, 2, 0] should be nonzero.
     = PowerMod[5, 2, 0]

    'PowerMod' threads over lists
    >> PowerMod[2, {10, 11, 12, 13, 14}, 5]
     = {4, 3, 1, 2, 4}
    """

    attributes = A_LISTABLE | A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = 3

    messages = {
        "ninv": "`1` is not invertible modulo `2`.",
    }

    rules = {
        "PowerMod[a, l_List, m_?NumberQ]": "Map[PowerMod[a, #, m] &, l]",
    }

    summary_text = "compute modular exponentiation"

    sympy_names = {
        -1: "mod_inverse",  # b = -1
        0: "nth_root_mod",  # 0 < b < 1 and is an inverse
        0.5: "sqrt_mod",  # b = 1/2
        3: "core.power.Pow",  # Handles complex numbers. Use builtin pow for integers
    }

    def eval(self, a: Integer, b, m: Integer, evaluation: Evaluation):
        "PowerMod[a_?NumberQ, b_?NumberQ, m_Integer]"

        a_py, b_py, m_py = a.value, b.value, m.value
        return eval_PowerMod(a_py, b_py, m_py, evaluation)


class Quotient(Builtin):
    """
    <url>:Quotient:https://en.wikipedia.org/wiki/Quotient</url> (<url>
    :WMA link:https://reference.wolfram.com/language/ref/Quotient.html</url>)

    <dl>
      <dt>'Quotient[m, n]'
      <dd>computes the integer quotient of $m$ and $n$. For non-complex numbers, this \
      equivalent to 'Floor[m/n]'. When a complex number is involved, it is 'Round[m/n]'.
      <dt>'Quotient[m, n, d]'
      <dd>computes the integer quotient of $m-d$ and $n$. For non-complex numbers, this \
      is equivalent to 'Floor[(m-d)/n]'. When a complex number is involved, it is \
      'Round[(m-d)/n]'.
    </dl>

    Plot showing the step-like 'Floor' behavior of 'Quotient':

    >> DiscretePlot[Quotient[n, 5], {n, 30}]
     = -Graphics-

    Integer-argument 'Quotient':
    >> Quotient[23, 7]
     = 3

    Rational-argument 'Quotient':
    >> Quotient[19/3, 5/2]
     = 2

    'Quotient' with inexact numbers:
    >> Quotient[4.56, 2.5]
     = 1

    'Quotient' with two complex numbers is same as 'Round[m/n]':
    >> Quotient[10.4 + 8 I, 4. + 5 I]
     = 2

    'Quotient' for large integers:
    >> Quotient[10^90, NextPrime[10^80]]
     = 9999999999

   'Quotient' threads elementwise over lists:
    >> Quotient[{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, 3]
     = {0, 0, 1, 1, 1, 2, 2, 2, 3, 3}
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = (2, 3)

    rules = {
        "Quotient[m_Complex, n_?NumberQ]": "Round[m / n]",
        "Quotient[m_?NumberQ, n_Complex]": "Round[m / n]",
        "Quotient[l_List, n_?NumberQ]": "Map[Quotient[#, m] &, l]",
        "Quotient[l_List, n_?NumberQ, d_?NumberQ]": "Map[Quotient[#, m, d] &, l]",
    }

    summary_text = "compute integer quotient"

    def eval(self, m, n, evaluation: Evaluation) -> Union[Symbol, Integer]:
        "Quotient[m_?NumberQ, n_?NumberQ]"
        py_m = m.value

        py_n = n.value
        if py_n == 0:
            if py_m == 0:
                tag = "indet"
                result = SymbolIndeterminate
            else:
                tag = "infy"
                result = SymbolComplexInfinity
            evaluation.message("Quotient", tag, Expression(SymbolQuotient, m, n))
            return result
        return eval_Quotient(py_m, py_n, 0)

    def eval_with_offset(
        self, m, n, d, evaluation: Evaluation
    ) -> Union[Symbol, Integer]:
        "Quotient[m_?NumberQ, n_?NumberQ, d_?NumberQ]"
        py_m = m.value
        py_n = n.value
        py_d = d.value
        if py_n == 0:
            if py_m - py_d == 0:
                tag = "indet"
                result = SymbolIndeterminate
            else:
                tag = "infy"
                result = SymbolComplexInfinity
            evaluation.message("Quotient", tag, Expression(SymbolQuotient, m, n, d))
            return result
        return eval_Quotient(py_m, py_n, py_d)


class QuotientRemainder(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/QuotientRemainder.html</url>

    <dl>
      <dt>'QuotientRemainder[m, n]'
      <dd>computes a list of the quotient and remainder from division of $m$ by $n$.
    </dl>

    Plot showing the repeated step-like nature of 'QuotientRemainder':

    >> DiscretePlot[First[QuotientRemainder[n, 5]], {n, 0, 30}]
     = -Graphics-

    >> DiscretePlot[Last[QuotientRemainder[n, 5]], {n, 0, 30}]
     = -Graphics-

    >> QuotientRemainder[23, 7]
     = {3, 2}
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    eval_error = Builtin.generic_argument_error
    expected_args = 2
    summary_text = "get the integer quotient and remainder"

    def eval(self, m, n, evaluation: Evaluation):
        "QuotientRemainder[m_, n_]"
        if m.is_numeric(evaluation) and n.is_numeric():
            py_m = m.to_python()
            py_n = n.to_python()
            if py_n == 0:
                evaluation.message(
                    "QuotientRemainder",
                    "divz",
                    evaluation.current_expression,
                )
                return
            # Note: py_m % py_n can be a float or an int.
            # Also note that we *want* the first argument to be an Integer.
            return to_mathics_list(Integer(py_m // py_n), py_m % py_n)
        else:
            return Expression(SymbolQuotientRemainder, m, n)
