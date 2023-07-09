# -*- coding: utf-8 -*-

"""
Division-Related Functions
"""

from typing import List

import sympy
from sympy import Q, ask

from mathics.builtin.base import Builtin, SympyFunction
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
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_bool
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.systemsymbols import (
    SymbolComplexInfinity,
    SymbolQuotient,
    SymbolQuotientRemainder,
)


class CompositeQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/CompositeQ.html</url>

    <dl>
      <dt>'CompositeQ[$n$]'
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
    summary_text = "test whether a number is composite"

    def eval(self, n: Integer, evaluation: Evaluation):
        "CompositeQ[n_Integer]"
        return from_bool(ask(Q.composite(n.value)))


class Divisible(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Divisible.html</url>

    <dl>
      <dt>'Divisible[$n$, $m$]'
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
      <dt>'GCD[$n1$, $n2$, ...]'
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
    summary_text = "greatest common divisor"

    def eval(self, ns, evaluation: Evaluation):
        "GCD[ns___Integer]"

        ns = ns.get_sequence()
        result = 0
        for n in ns:
            value = n.value
            if value is None:
                return
            result = sympy.gcd(result, value)
        return Integer(result)


class LCM(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/LCM.html</url>

    <dl>
      <dt>'LCM[$n1$, $n2$, ...]'
      <dd>computes the least common multiple of the given integers.
    </dl>

    >> LCM[15, 20]
     = 60
    >> LCM[20, 30, 40, 50]
     = 600
    """

    attributes = A_FLAT | A_LISTABLE | A_ONE_IDENTITY | A_ORDERLESS | A_PROTECTED
    summary_text = "least common multiple"

    def eval(self, ns: List[Integer], evaluation: Evaluation):
        "LCM[ns___Integer]"

        ns = ns.get_sequence()
        result = 1
        for n in ns:
            value = n.value
            if value is None:
                return
            result = sympy.lcm(result, value)
        return Integer(result)


class Mod(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Mod.html</url>

    <dl>
      <dt>'Mod[$x$, $m$]'
      <dd>returns $x$ modulo $m$.
    </dl>

    >> Mod[14, 6]
     = 2
    >> Mod[-3, 4]
     = 1
    >> Mod[-3, -4]
     = -3
    >> Mod[5, 0]
     : The argument 0 should be nonzero.
     = Mod[5, 0]
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    summary_text = "the remainder in an integer division"

    def eval(self, n: Integer, m: Integer, evaluation: Evaluation):
        "Mod[n_Integer, m_Integer]"

        n, m = n.value, m.value
        if m == 0:
            evaluation.message("Mod", "divz", m)
            return
        return Integer(n % m)


class ModularInverse(SympyFunction):
    """
    <url>
    :Modular multiplicative inverse:
    https://en.wikipedia.org/wiki/Modular_multiplicative_inverse</url> (<url>
    :SymPy: https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.mod_inverse</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/ModularInverse.html
    </url>)

    <dl>
      <dt>'ModularInverse[$k$, $n$]'
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
    summary_text = "returns the modular inverse $k^(-1)$ mod $n$"
    sympy_name = "mod_inverse"

    def eval_k_n(self, k: Integer, n: Integer, evaluation: Evaluation):
        "ModularInverse[k_Integer, n_Integer]"
        try:
            r = sympy.mod_inverse(k.value, n.value)
        except ValueError:
            return
        return Integer(r)


class PowerMod(Builtin):
    """
    Modular exponentiaion.
    See <url>https://en.wikipedia.org/wiki/Modular_exponentiation</url>.

    <dl>
      <dt>'PowerMod[$x$, $y$, $m$]'
      <dd>computes $x$^$y$ modulo $m$.
    </dl>

    >> PowerMod[2, 10000000, 3]
     = 1
    >> PowerMod[3, -2, 10]
     = 9
    >> PowerMod[0, -1, 2]
     : 0 is not invertible modulo 2.
     = PowerMod[0, -1, 2]
    >> PowerMod[5, 2, 0]
     : The argument 0 should be nonzero.
     = PowerMod[5, 2, 0]

    'PowerMod' does not support rational coefficients (roots) yet.
    """

    attributes = A_LISTABLE | A_PROTECTED

    messages = {
        "ninv": "`1` is not invertible modulo `2`.",
    }
    summary_text = "modular exponentiation"

    def eval(self, a: Integer, b: Integer, m: Integer, evaluation: Evaluation):
        "PowerMod[a_Integer, b_Integer, m_Integer]"

        a_int = a
        m_int = m
        a, b, m = a.value, b.value, m.value
        if m == 0:
            evaluation.message("PowerMod", "divz", m)
            return
        if b < 0:
            b = -b
            try:
                a = int(sympy.invert(a, m))
            except sympy.polys.polyerrors.NotInvertible:
                evaluation.message("PowerMod", "ninv", a_int, m_int)
                return
        return Integer(pow(a, b, m))


class Quotient(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Quotient.html</url>

    <dl>
      <dt>'Quotient[m, n]'
      <dd>computes the integer quotient of $m$ and $n$.
    </dl>

    >> Quotient[23, 7]
     = 3

    #> Quotient[13, 0]
     : Infinite expression Quotient[13, 0] encountered.
     = ComplexInfinity
    #> Quotient[-17, 7]
     = -3
    #> Quotient[-17, -4]
     = 4
    #> Quotient[19, -4]
     = -5
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    messages = {
        "infy": "Infinite expression `1` encountered.",
    }
    summary_text = "integer quotient"

    def eval(self, m: Integer, n: Integer, evaluation: Evaluation):
        "Quotient[m_Integer, n_Integer]"
        py_m = m.value
        py_n = n.value
        if py_n == 0:
            evaluation.message("Quotient", "infy", Expression(SymbolQuotient, m, n))
            return SymbolComplexInfinity
        return Integer(py_m // py_n)


class QuotientRemainder(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/QuotientRemainder.html</url>

    <dl>
      <dt>'QuotientRemainder[m, n]'
      <dd>computes a list of the quotient and remainder from division of $m$ by $n$.
    </dl>

    >> QuotientRemainder[23, 7]
     = {3, 2}

    #> QuotientRemainder[13, 0]
     : The argument 0 in QuotientRemainder[13, 0] should be nonzero.
     = QuotientRemainder[13, 0]
    #> QuotientRemainder[-17, 7]
     = {-3, 4}
    #> QuotientRemainder[-17, -4]
     = {4, -1}
    #> QuotientRemainder[19, -4]
     = {-5, -1}
    #> QuotientRemainder[a, 0]
     = QuotientRemainder[a, 0]
    #> QuotientRemainder[a, b]
     = QuotientRemainder[a, b]
    #> QuotientRemainder[5.2,2.5]
     = {2, 0.2}
    #> QuotientRemainder[5, 2.]
     = {2, 1.}
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    messages = {
        "divz": "The argument 0 in `1` should be nonzero.",
    }
    summary_text = "integer quotient and remainder"

    def eval(self, m, n, evaluation: Evaluation):
        "QuotientRemainder[m_, n_]"
        if m.is_numeric(evaluation) and n.is_numeric():
            py_m = m.to_python()
            py_n = n.to_python()
            if py_n == 0:
                evaluation.message(
                    "QuotientRemainder",
                    "divz",
                    Expression(SymbolQuotientRemainder, m, n),
                )
                return
            # Note: py_m % py_n can be a float or an int.
            # Also note that we *want* the first arguemnt to be an Integer.
            return to_mathics_list(Integer(py_m // py_n), py_m % py_n)
        else:
            return Expression(SymbolQuotientRemainder, m, n)
