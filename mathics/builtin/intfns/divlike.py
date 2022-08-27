# -*- coding: utf-8 -*-

"""
Division-Related Functions
"""

from typing import List

import sympy
from itertools import combinations
from sympy import Q, ask

from mathics.builtin.base import Builtin, Test, SympyFunction
from mathics.core.atoms import Integer
from mathics.core.convert.python import from_bool
from mathics.core.expression import Expression
from mathics.core.convert.expression import to_mathics_list
from mathics.core.symbols import Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolComplexInfinity

from mathics.core.attributes import (
    flat as A_FLAT,
    listable as A_LISTABLE,
    numeric_function as A_NUMERIC_FUNCTION,
    one_identity as A_ONE_IDENTITY,
    orderless as A_ORDERLESS,
    protected as A_PROTECTED,
    read_protected as A_READ_PROTECTED,
)

SymbolQuotient = Symbol("Quotient")
SymbolQuotientRemainder = Symbol("QuotientRemainder")


class CompositeQ(Builtin):
    """
    <dl>
      <dt>'CompositeQ[$n$]'
      <dd>returns True if $n$ is a composite number
    </dl>

    <ul>
      <li>A composite number is a positive number that is the product of two integers other than 1.
      <li>For negative integer $n$, 'CompositeQ[$n$]' is effectively equivalent to 'CompositeQ[-$n$]'.
    </ul>

    >> Table[CompositeQ[n], {n, 0, 10}]
     = {False, False, False, False, True, False, True, False, True, True, True}
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "test whether a number is composite"

    def apply(self, n, evaluation):
        "CompositeQ[n_Integer]"
        return from_bool(ask(Q.composite(n.value)))


class CoprimeQ(Builtin):
    """
    <dl>
      <dt>'CoprimeQ[$x$, $y$]'
      <dd>tests whether $x$ and $y$ are coprime by computing their greatest common divisor.
    </dl>

    >> CoprimeQ[7, 9]
     = True

    >> CoprimeQ[-4, 9]
     = True

    >> CoprimeQ[12, 15]
     = False

    CoprimeQ also works for complex numbers
    >> CoprimeQ[1+2I, 1-I]
     = True

    >> CoprimeQ[4+2I, 6+3I]
     = True

    >> CoprimeQ[2, 3, 5]
     = True

    >> CoprimeQ[2, 4, 5]
     = False
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "test whether elements are coprime"

    def apply(self, args, evaluation):
        "CoprimeQ[args__]"

        py_args = [arg.to_python() for arg in args.get_sequence()]
        if not all(isinstance(i, int) or isinstance(i, complex) for i in py_args):
            return SymbolFalse

        if all(sympy.gcd(n, m) == 1 for (n, m) in combinations(py_args, 2)):
            return SymbolTrue
        else:
            return SymbolFalse


class Divisible(Builtin):
    """
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


class EvenQ(Test):
    """
    <dl>
      <dt>'EvenQ[$x$]'
      <dd>returns 'True' if $x$ is even, and 'False' otherwise.
    </dl>

    >> EvenQ[4]
     = True
    >> EvenQ[-3]
     = False
    >> EvenQ[n]
     = False
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "test whether one number is divisible by the other"

    def test(self, n):
        value = n.get_int_value()
        return value is not None and value % 2 == 0


class GCD(Builtin):
    """
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

    def apply(self, ns, evaluation):
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

    def apply(self, ns: List[Integer], evaluation):
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

    def apply(self, n: Integer, m: Integer, evaluation):
        "Mod[n_Integer, m_Integer]"

        n, m = n.value, m.value
        if m == 0:
            evaluation.message("Mod", "divz", m)
            return
        return Integer(n % m)


class ModularInverse(SympyFunction):
    """
    <url>:Modular multiplicative inverse: https://en.wikipedia.org/wiki/Modular_multiplicative_inverse</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/core.html#sympy.core.numbers.mod_inverse</url>, <url>:WMA: https://reference.wolfram.com/language/ref/ModularInverse.html</url>)

    <dl>
      <dt>'ModularInverse[$k$, $n$]'
      <dd>returns the modular inverse $k$^(-1) mod $n$.
    </dl>

    'ModularInverse[$k$,$n$]' gives the smallest positive integer $r$ where the remainder of the division of $r$ x $k$ by $n$ is equal to 1.

    >> ModularInverse[2, 3]
     = 2

    The following is be True for all values $n$, $k$ which have a modular inverse:
    >> k = 2; n = 3; Mod[ModularInverse[k, n] * k, n] == 1
     = True

    Some modular inverses just do not exists. For example when $k$ is a multple of $n$:
    >> ModularInverse[k, k]
     = ModularInverse[2, 2]

    #> Clear[k, n]
    """

    attributes = A_PROTECTED
    summary_text = "returns the modular inverse $k^(-1)$ mod $n$"
    sympy_name = "mod_inverse"

    def apply_k_n(self, k: Integer, n: Integer, evaluation):
        "ModularInverse[k_Integer, n_Integer]"
        try:
            r = sympy.mod_inverse(k.value, n.value)
        except ValueError:
            return
        return Integer(r)


class OddQ(Test):
    """
    <dl>
      <dt>'OddQ[$x$]'
      <dd>returns 'True' if $x$ is odd, and 'False' otherwise.
    </dl>

    >> OddQ[-3]
     = True
    >> OddQ[0]
     = False
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "test whether elements are odd numbers"

    def test(self, n):
        value = n.get_int_value()
        return value is not None and value % 2 != 0


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

    def apply(self, a: Integer, b: Integer, m: Integer, evaluation):
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


class PrimeQ(SympyFunction):
    """
    <dl>
      <dt>'PrimeQ[$n$]'
      <dd>returns 'True' if $n$ is a prime number.
    </dl>

    For very large numbers, 'PrimeQ' uses probabilistic prime testing, so it might be wrong sometimes
    (a number might be composite even though 'PrimeQ' says it is prime).
    The algorithm might be changed in the future.

    >> PrimeQ[2]
     = True
    >> PrimeQ[-3]
     = True
    >> PrimeQ[137]
     = True
    >> PrimeQ[2 ^ 127 - 1]
     = True

    #> PrimeQ[1]
     = False
    #> PrimeQ[2 ^ 255 - 1]
     = False

    All prime numbers between 1 and 100:
    >> Select[Range[100], PrimeQ]
     = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}

    'PrimeQ' has attribute 'Listable':
    >> PrimeQ[Range[20]]
     = {False, True, True, False, True, False, True, False, False, False, True, False, True, False, False, False, True, False, True, False}
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    sympy_name = "isprime"
    summary_text = "test whether elements are prime numbers"

    def apply(self, n, evaluation):
        "PrimeQ[n_]"

        n = n.get_int_value()
        if n is None:
            return SymbolFalse

        n = abs(n)
        if sympy.isprime(n):
            return SymbolTrue
        else:
            return SymbolFalse


class Quotient(Builtin):
    """
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

    def apply(self, m: Integer, n: Integer, evaluation):
        "Quotient[m_Integer, n_Integer]"
        py_m = m.value
        py_n = n.value
        if py_n == 0:
            evaluation.message("Quotient", "infy", Expression(SymbolQuotient, m, n))
            return SymbolComplexInfinity
        return Integer(py_m // py_n)


class QuotientRemainder(Builtin):
    """
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

    def apply(self, m, n, evaluation):
        "QuotientRemainder[m_, n_]"
        if m.is_numeric(evaluation) and n.is_numeric():
            py_m = m.to_python()
            py_n = n.to_python()
            if py_n == 0:
                return evaluation.message(
                    "QuotientRemainder",
                    "divz",
                    Expression(SymbolQuotientRemainder, m, n),
                )
            # Note: py_m % py_n can be a float or an int.
            # Also note that we *want* the first arguemnt to be an Integer.
            return to_mathics_list(Integer(py_m // py_n), py_m % py_n)
        else:
            return Expression(SymbolQuotientRemainder, m, n)
