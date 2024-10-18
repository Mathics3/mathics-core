# -*- coding: utf-8 -*-

"""
Number theoretic functions
"""
import mpmath
import sympy
from packaging.version import Version
from sympy.utilities.iterables import ordered_partitions

from mathics.core.atoms import Integer, Integer0, Integer10, Rational, Real
from mathics.core.attributes import (
    A_LISTABLE,
    A_NUMERIC_FUNCTION,
    A_ORDERLESS,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, SympyFunction
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_bool, from_python
from mathics.core.convert.sympy import SympyPrime, from_sympy
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolDivide, SymbolFalse
from mathics.core.systemsymbols import (
    SymbolCeiling,
    SymbolComplex,
    SymbolFloor,
    SymbolIm,
    SymbolRe,
)
from mathics.eval.nevaluator import eval_N

SymbolFractionalPart = Symbol("System`FractionalPart")
SymbolIntegerPart = Symbol("System`IntegerPart")
SymbolMantissaExponent = Symbol("System`MantissaExponent")


class ContinuedFraction(SympyFunction):
    """
    <url>:Continued fraction:
    https://en.wikipedia.org/wiki/Continued_fraction</url> (<url>
    :SymPy: https://docs.sympy.org/latest/modules/ntheory.html#module-sympy.ntheory.continued_fraction</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/ContinuedFraction.html</url>)
    <dl>
      <dt>'ContinuedFraction[$x$, $n$]'
      <dd>generate the first $n$ terms in the continued fraction representation of $x$.

      <dt>'ContinuedFraction[$x$]'
      <dd>the complete continued fraction representation for a rational or quadradic irrational number.
    </dl>

    >> ContinuedFraction[Pi, 10]
     = {3, 7, 15, 1, 292, 1, 1, 1, 2, 1}

    >> ContinuedFraction[(1 + 2 Sqrt[3])/5]
     = {0, 1, {8, 3, 34, 3}}

    >> ContinuedFraction[Sqrt[70]]
     = {8, {2, 1, 2, 1, 2, 16}}
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    summary_text = "continued fraction expansion"
    sympy_name = "continued_fraction"

    def eval(self, x, evaluation: Evaluation):
        "%(name)s[x_]"
        return super().eval(x, evaluation)

    def eval_with_n(self, x, n: Integer, evaluation: Evaluation):
        "%(name)s[x_, n_Integer]"
        py_n = n.value
        sympy_x = x.to_sympy()
        it = sympy.continued_fraction_iterator(sympy_x)
        return from_sympy([next(it) for _ in range(py_n)])


class Divisors(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Divisors.html</url>

    <dl>
    <dt>'Divisors[$n$]'
        <dd>returns a list of the integers that divide $n$.
    </dl>

    >> Divisors[96]
     = {1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 96}
    >> Divisors[704]
     = {1, 2, 4, 8, 11, 16, 22, 32, 44, 64, 88, 176, 352, 704}
    >> Divisors[{87, 106, 202, 305}]
     = {{1, 3, 29, 87}, {1, 2, 53, 106}, {1, 2, 101, 202}, {1, 5, 61, 305}}
    """

    # TODO: support GaussianIntegers
    # e.g. Divisors[2, GaussianIntegers -> True]
    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "integer divisors"

    def eval(self, n: Integer, evaluation: Evaluation):
        "Divisors[n_Integer]"
        if n == Integer0:
            return None
        return to_mathics_list(*sympy.divisors(n.value), elements_conversion_fn=Integer)


class DivisorSigma(SympyFunction):
    """
    <url>:Divisor function: https://en.wikipedia.org/wiki/Divisor_function</url>
    (<url>:SymPy: https://docs.sympy.org/latest/modules/functions/combinatorial.html#sympy.functions.combinatorial.numbers.divisor_sigma</url>,
    <url>:WMA: https://reference.wolfram.com/language/ref/DivisorSigma.html</url>)

    <dl>
      <dt>'DivisorSigma[$k$, $n$]'
      <dd>returns $\\sigma_k(n)$
    </dl>

    >> DivisorSigma[1, 20]
    = 42
    >> DivisorSigma[2, 20]
    = 546
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "divisor function"
    sympy_name = "divisor_sigma"

    def eval(self, k: Integer, n: Integer, evaluation: Evaluation):
        "DivisorSigma[k_Integer, n_Integer]"
        # arguments are in reverse order
        return from_sympy(sympy.divisor_sigma(n.to_sympy(), k.to_sympy()))


class DivisorSum(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/DivisorSum.html</url>

    <dl>
      <dt>'DivisorSum[$n$, $form$]'
      <dd>transform the divisors of $n$ using $form$ and take their sum
    </dl>

    >> DivisorSum[30, # &]
    = 72
    >> DivisorSum[1000, #^2 &]
    = 1383460

    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "divisor sum"

    rules = {
        "DivisorSum[n_Integer, form_]": "Sum[form[d], {d, Divisors[n]}]",
        "DivisorSum[n_Integer, form_, cond_]": "Sum[If[cond[d], form[d], 0], {d, Divisors[n]}]",
    }


# FIXME: Previously this used gmpy's gcdext. sympy's gcdex is not as powerful
# class ExtendedGCD(Builtin):
#    """
#    >> ExtendedGCD[10, 15]
#     = {5, {-1, 1}}
#
#    'ExtendedGCD' works with any number of arguments:
#    >> ExtendedGCD[10, 15, 7]
#     = {1, {-3, 3, -2}}
#
#    Compute the greatest common divisor and check the result:
#    >> numbers = {10, 20, 14};
#    >> {gcd, factors} = ExtendedGCD[Sequence @@ numbers]
#     = {2, {3, 0, -2}}
#    >> Plus @@ (numbers * factors)
#     = 2
#
#    'ExtendedGCD' does not work for rational numbers and Gaussian integers yet
#    """
#
#    attributes = A_LISTABLE | A_PROTECTED
#
#    def eval(self, ns, evaluation: Evaluation):
#        'ExtendedGCD[ns___Integer]'
#
#        ns = ns.get_sequence()
#        result = 0
#        coeff = []
#        for n in ns:
#            value = n.value
#            if value is None:
#                return
#            new_result, c1, c2 = sympy.gcdex(result, value)
#            result = new_result
#            coeff = [c * c1 for c in coeff] + [c2]
#            return ListExpression(Integer(result), ListExpression(
#                *(Integer(c) for c in coeff)))


class EulerPhi(SympyFunction):
    """
    <url>:Euler's totient function: https://en.wikipedia.org/wiki/Euler%27s_totient_function</url> (<url>:SymPy: https://docs.sympy.org/latest/modules/ntheory.html#sympy.ntheory.factor_.totient</url>, <url>:WMA: https://reference.wolfram.com/language/ref/EulerPhi.html</url>)
    This function counts positive integers up to $n$ that are relatively prime to $n$.
    It is typically used in cryptography and in many applications in elementary number theory.
    <dl>
      <dt>'EulerPhi[$n$]'
      <dd>returns the Euler totient function .
    </dl>

    Compute the Euler totient function:
    >> EulerPhi[9]
    = 6

    'EulerPhi' of a negative integer is same as its positive counterpart:
    >> EulerPhi[-11] == EulerPhi[11]
    = True

    Large arguments are computed quickly:
    >> EulerPhi[40!]
    = 121343746763281707274905415180804423680000000000

    'EulerPhi' threads over lists:
    >> EulerPhi[Range[1, 17, 2]]
    = {1, 2, 4, 6, 6, 10, 12, 8, 16}
    Above, we get consecutive even numbers when the input is prime.

    Compare the results above with:
    >> EulerPhi[Range[1, 17]]
    = {1, 1, 2, 2, 4, 2, 6, 4, 6, 4, 10, 4, 12, 6, 8, 8, 16}
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "Euler totient function"
    sympy_name = "totient"

    def eval(self, n: Integer, evaluation: Evaluation):
        "EulerPhi[n_Integer]"
        return super().eval(abs(n), evaluation)


class FactorInteger(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/FactorInteger.html</url>

    <dl>
      <dt>'FactorInteger[$n$]'
      <dd>returns the factorization of $n$ as a list of factors and exponents.
    </dl>

    >> factors = FactorInteger[2010]
     = {{2, 1}, {3, 1}, {5, 1}, {67, 1}}
    To get back the original number:
    >> Times @@ Power @@@ factors
     = 2010
    'FactorInteger' factors rationals using negative exponents:
    >> FactorInteger[2010 / 2011]
     = {{2, 1}, {3, 1}, {5, 1}, {67, 1}, {2011, -1}}
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "list of prime factors and exponents"

    # TODO: GausianIntegers option
    # e.g. FactorInteger[5, GaussianIntegers -> True]

    def eval(self, n, evaluation: Evaluation):
        "FactorInteger[n_]"

        if isinstance(n, Integer):
            factors = sympy.factorint(n.value)
            factors = sorted(factors.items())
            return ListExpression(
                *(to_mathics_list(factor, exp) for factor, exp in factors)
            )

        elif isinstance(n, Rational):
            factors, factors_denom = list(
                map(sympy.factorint, n.value.as_numer_denom())
            )
            for factor, exp in factors_denom.items():
                factors[factor] = factors.get(factor, 0) - exp
            factors = sorted(factors.items())
            return ListExpression(
                *(to_mathics_list(factor, exp) for factor, exp in factors)
            )
        else:
            evaluation.message("FactorInteger", "exact", n)


def _integer_part(n, expr, evaluation: Evaluation):
    n_sympy = n.to_sympy()
    if n_sympy.is_constant():
        if n_sympy >= 0:
            return Expression(SymbolFloor, n).evaluate(evaluation)
        else:
            return Expression(SymbolCeiling, n).evaluate(evaluation)
    else:
        return expr


def _fractional_part(n, expr, evaluation: Evaluation):
    if n.to_sympy().is_constant():
        return n - _integer_part(n, expr, evaluation)
    else:
        return expr


class FractionalPart(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/FractionalPart.html</url>

    <dl>
    <dt>'FractionalPart[$n$]'
        <dd>finds the fractional part of $n$.
    </dl>

    >> FractionalPart[4.1]
     = 0.1

    >> FractionalPart[-5.25]
     = -0.25
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_READ_PROTECTED | A_PROTECTED
    summary_text = "fractional part of a number"

    def eval(self, n, evaluation: Evaluation):
        "FractionalPart[n_]"
        expr = Expression(SymbolFractionalPart, n)
        return _fractional_part(n, expr, evaluation)

    def eval_complex_n(self, n, evaluation: Evaluation):
        "FractionalPart[n_Complex]"
        expr = Expression(SymbolFractionalPart, n)
        n_real = Expression(SymbolRe, n).evaluate(evaluation)
        n_image = Expression(SymbolIm, n).evaluate(evaluation)

        real_fractional_part = _fractional_part(n_real, expr, evaluation)
        image_fractional_part = _fractional_part(n_image, expr, evaluation)
        return Expression(SymbolComplex, real_fractional_part, image_fractional_part)


class FromContinuedFraction(SympyFunction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/FromContinuedFraction.html</url>

    <dl>
      <dt>'FromContinuedFraction[$list$]'
      <dd>reconstructs a number from the list of its continued fraction terms.
    </dl>

    >> FromContinuedFraction[{3, 7, 15, 1, 292, 1, 1, 1, 2, 1}]
     = 1146408 / 364913

    >> FromContinuedFraction[Range[5]]
     = 225 / 157
    """

    attributes = A_NUMERIC_FUNCTION | A_PROTECTED

    summary_text = "reconstructs a number from its continued fraction representation"
    sympy_name = "continued_fraction_reduce"

    def eval(self, expr, evaluation: Evaluation):
        "%(name)s[expr_List]"
        nums = expr.to_python()
        if all(isinstance(i, int) for i in nums):
            return from_sympy(sympy.continued_fraction_reduce(nums))


class IntegerPart(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/IntegerPart.html</url>

    <dl>
      <dt>'IntegerPart[$n$]'
      <dd>finds the integer part of $n$.
    </dl>

    >> IntegerPart[4.1]
     = 4

    >> IntegerPart[-5.25]
     = -5
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_READ_PROTECTED | A_PROTECTED
    summary_text = "integer part of a number"

    def eval(self, n, evaluation: Evaluation):
        "IntegerPart[n_]"
        expr = Expression(SymbolIntegerPart, n)
        return _integer_part(n, expr, evaluation)

    def eval_complex_n(self, n, evaluation: Evaluation):
        "IntegerPart[n_Complex]"
        expr = Expression(SymbolIntegerPart, n)
        n_real = Expression(SymbolRe, n).evaluate(evaluation)
        n_image = Expression(SymbolIm, n).evaluate(evaluation)

        real_integer_part = _integer_part(n_real, expr, evaluation)
        image_integer_part = _integer_part(n_image, expr, evaluation)
        return Expression(SymbolComplex, real_integer_part, image_integer_part)


class IntegerPartitions(Builtin):
    """
    <url>:Integer partition: https://en.wikipedia.org/wiki/Integer_partition</url>
    (<url>:SymPy: https://docs.sympy.org/latest/modules/utilities/iterables.html#sympy.utilities.iterables.ordered_partitions</url>,
    <url>:WMA: https://reference.wolfram.com/language/ref/IntegerPartitions.html</url>)

    <dl>
      <dt>'IntegerPartitions[$n$]'
      <dd>lists partitions of the integer $n$
    </dl>

    >> IntegerPartitions[5]
    = {{5}, {4, 1}, {3, 2}, {3, 1, 1}, {2, 2, 1}, {2, 1, 1, 1}, {1, 1, 1, 1, 1}}
    >> IntegerPartitions[8, 3]
    = {{8}, {7, 1}, {6, 2}, {6, 1, 1}, {5, 3}, {5, 2, 1}, {4, 4}, {4, 3, 1}, {4, 2, 2}, {3, 3, 2}}
    >> IntegerPartitions[8, {3}]
    = {{6, 1, 1}, {5, 2, 1}, {4, 3, 1}, {4, 2, 2}, {3, 3, 2}}
    >> IntegerPartitions[8, All, {1, 2, 5}]
    = {{5, 2, 1}, {5, 1, 1, 1}, {2, 2, 2, 2}, {2, 2, 2, 1, 1}, {2, 2, 1, 1, 1, 1}, {2, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1, 1}}
    >> IntegerPartitions[8, All, All, 3]
    = {{8}, {7, 1}, {6, 2}}
    >> IntegerPartitions[4, {2}, {-1, 0, 1, 4, 5}]
    = {{5, -1}, {4, 0}}
    """

    attributes = A_PROTECTED
    summary_text = "list integer partitions"

    rules = {
        "IntegerPartitions[n_Integer]": "IntegerPartitions[n, All]",
        "IntegerPartitions[n_Integer, All]": "IntegerPartitions[n, n]",
        "IntegerPartitions[n_Integer, k_Integer]": "IntegerPartitions[n, {1, k}]",
        "IntegerPartitions[n_Integer, {k_Integer}]": "IntegerPartitions[n, {k, k}]",
        "IntegerPartitions[n_Integer, kspec_, s_List] /; SubsetQ[Range[n], s]": "Select[IntegerPartitions[n, kspec], SubsetQ[s, #] &]",
        "IntegerPartitions[n_Integer, kspec_, All]": "IntegerPartitions[n, kspec]",
        "IntegerPartitions[n_Integer, kspec_, sspec_, m_]": "Take[IntegerPartitions[n, kspec, sspec], m]",
        "IntegerPartitions[n_Integer, {k_Integer}, s_List]": "ReverseSort@Select[Union[ReverseSort /@ Tuples[s, k]], Total[#] == n &]",
    }

    def eval(self, n: Integer, kmin: Integer, kmax: Integer, evaluation: Evaluation):
        "IntegerPartitions[n_Integer, {kmin_Integer, kmax_Integer}]"
        partitions = []
        for k in range(kmin.value, kmax.value + 1):
            for p in ordered_partitions(n.value, k, sort=False):
                partitions.append([Integer(i) for i in reversed(p)])
        partitions.sort(reverse=True)
        return ListExpression(*[ListExpression(*p) for p in partitions])


class MantissaExponent(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MantissaExponent.html</url>

    <dl>
      <dt>'MantissaExponent[$n$]'
      <dd>finds a list containing the mantissa and exponent of a given number $n$.

      <dt>'MantissaExponent[$n$, $b$]'
      <dd>finds the base b mantissa and exponent of $n$.
    </dl>

    >> MantissaExponent[2.5*10^20]
     = {0.25, 21}

    >> MantissaExponent[125.24]
     = {0.12524, 3}

    >> MantissaExponent[125., 2]
     = {0.976563, 7}

    >> MantissaExponent[10, b]
     = MantissaExponent[10, b]
    """

    attributes = A_LISTABLE | A_PROTECTED
    messages = {
        "realx": "The value `1` is not a real number",
        "rbase": "Base `1` is not a real number greater than 1.",
    }
    rules = {
        "MantissaExponent[0]": "{0, 0}",
        "MantissaExponent[0, n_]": "{0, 0}",
    }
    summary_text = "decomposes numbers as mantissa and exponent"

    def eval(self, n, evaluation: Evaluation):
        "MantissaExponent[n_]"
        n_sympy = n.to_sympy()
        expr = Expression(SymbolMantissaExponent, n)

        if isinstance(n.to_python(), complex):
            evaluation.message("MantissaExponent", "realx", n)
            return expr
        # Handle Input with special cases such as PI and E
        if n_sympy.is_constant():
            temp_n = eval_N(n, evaluation)
            py_n = temp_n.to_python()
        else:
            return expr

        base_exp = int(mpmath.log10(py_n))
        exp = Integer((base_exp + 1) if base_exp >= 0 else base_exp)

        return ListExpression(Expression(SymbolDivide, n, Integer10**exp), exp)

    def eval_with_b(self, n, b, evaluation: Evaluation):
        "MantissaExponent[n_, b_]"
        # Handle Input with special cases such as PI and E
        n_sympy, b_sympy = n.to_sympy(), b.to_sympy()

        expr = Expression(SymbolMantissaExponent, n, b)

        if isinstance(n.to_python(), complex):
            evaluation.message("MantissaExponent", "realx", n)
            return expr

        if n_sympy.is_constant():
            temp_n = eval_N(n, evaluation)
            py_n = temp_n.to_python()
        else:
            return expr

        if b_sympy.is_constant():
            temp_b = eval_N(b, evaluation)
            py_b = temp_b.to_python()
        else:
            return expr

        if not py_b > 1:
            evaluation.message("MantissaExponent", "rbase", b)
            return expr

        base_exp = int(mpmath.log(py_n, py_b))

        exp = Integer((base_exp + 1) if base_exp >= 0 else base_exp)
        return ListExpression(Expression(SymbolDivide, n, b**exp), exp)


class MersennePrimeExponent(SympyFunction):
    """
    <url>:SymPy: https://docs.sympy.org/latest/modules/ntheory.html#sympy.ntheory.factor_.mersenne_prime_exponent</url>,
    <url>:WMA: https://reference.wolfram.com/language/ref/MersennePrimeExponent.html</url>

    <dl>
      <dt>'MersennePrimeExponent[$n$]'
      <dd>returns the exponent of the $n$th Mersenne prime.
    </dl>

    >> Table[MersennePrimeExponent[n], {n, 10}]
    = {2, 3, 5, 7, 13, 17, 19, 31, 61, 89}

    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "Mersenne prime exponent"
    sympy_name = "mersenne_prime_exponent"

    def eval(self, n: Integer, evaluation: Evaluation):
        "MersennePrimeExponent[n_Integer]"
        return super().eval(n, evaluation)


class MoebiusMu(SympyFunction):
    """
    <url>:Mobius function: https://en.wikipedia.org/wiki/M%C3%B6bius_function</url>
    (<url>:SymPy: https://docs.sympy.org/latest/modules/functions/combinatorial.html#sympy.functions.combinatorial.numbers.mobius</url>,
    <url>:WMA: https://reference.wolfram.com/language/ref/MoebiusMu.html</url>)

    <dl>
      <dt>'MoebiusMu[$n$]'
      <dd>returns $\\mu(n)$
    </dl>

    >> Array[MoebiusMu, 10]
    = {1, -1, -1, 0, -1, 1, -1, 0, 0, 1}

    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "Mobius function"
    sympy_name = "mobius"

    def eval(self, n: Integer, evaluation: Evaluation):
        "MoebiusMu[n_Integer]"
        return super().eval(n, evaluation)


class NextPrime(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/NextPrime.html</url>

    <dl>
      <dt>'NextPrime[$n$]'
      <dd>gives the next prime after $n$.

      <dt>'NextPrime[$n$,$k$]'
      <dd>gives the $k$th  prime after $n$.
    </dl>

    >> NextPrime[10000]
     = 10007

    >> NextPrime[100, -5]
     = 73

    >> NextPrime[10, -5]
    = -2

    >> NextPrime[100, 5]
     = 113

    >> NextPrime[5.5, 100]
     = 563

    >> NextPrime[5, 10.5]
     = NextPrime[5, 10.5]
    """

    rules = {
        "NextPrime[n_]": "NextPrime[n, 1]",
    }
    summary_text = "closest, smallest prime number"

    def eval(self, n, k: Integer, evaluation: Evaluation):
        "NextPrime[n_?NumberQ, k_Integer]"

        def to_int_value(x):
            if isinstance(x, Integer):
                return x.value
            x = eval_N(x, evaluation)
            if isinstance(x, Integer):
                return x.value
            elif isinstance(x, Real):
                return round(x.value)
            else:
                return None

        py_k = to_int_value(k)
        if py_k is None:
            return None

        py_n = n.value

        if py_k >= 0:
            return Integer(sympy.ntheory.nextprime(py_n, py_k))

        # Hack to get earlier primes
        result = n.to_python()
        for i in range(-py_k):
            try:
                # from sympy 1.13, the previous prime to 2 fails...
                result = -2 if result == 2 else sympy.ntheory.prevprime(result)
            except ValueError:
                # No earlier primes
                return Integer(-1 * sympy.ntheory.nextprime(0, py_k - i))

        return Integer(result)


class PartitionsP(SympyFunction):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/PartitionsP.html</url>

    <dl>
      <dt>'PartitionsP[$n$]'
      <dd>return the number $p$($n$) of unrestricted partitions of the integer $n$.
    </dl>

    >> Table[PartitionsP[k], {k, -2, 12}]
     = {0, 0, 1, 1, 2, 3, 5, 7, 11, 15, 22, 30, 42, 56, 77}
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_ORDERLESS | A_PROTECTED
    summary_text = "number of unrestricted partitions"
    # The name of this function changed in Sympy version 1.13.0.
    # This supports backward compatibility.
    sympy_name = (
        "npartitions" if Version(sympy.__version__) < Version("1.13.0") else "partition"
    )

    def eval(self, n, evaluation: Evaluation):
        """PartitionsP[n_Integer]"""
        return super().eval(n, evaluation)


class PowersRepresentations(Builtin):
    """
    <url>:WMA: https://reference.wolfram.com/language/ref/PowersRepresentations.html</url>
    <dl>
      <dt>'PowersRepresentations[$n$, $k$, $p$]'
      <dd>represent $n$ as a sum of $k$ non-negative integers raised to the power of $p$.
    </dl>

    >> PowersRepresentations[1729, 2, 3]
     = {{1, 12}, {9, 10}}
    >> PowersRepresentations[50, 3, 2]
     = {{0, 1, 7}, {0, 5, 5}, {3, 4, 5}}
    """

    attributes = A_PROTECTED
    summary_text = "represent a number as a sum of powers"

    rules = {
        "PowersRepresentations[n_,k_,p_]": "Sort /@ IntegerPartitions[n, {k}, Range[0, Floor[n^(1/p)]]^p]^(1/p) // Sort",
    }


class Prime(SympyFunction):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Prime.html</url>

    <dl>
      <dt>'Prime[$n$]'
      <dt>'Prime'[{$n0$, $n1$, ...}]
      <dd>returns the $n$th prime number where $n$ is an positive Integer.
      If given a list of integers, the return value is a list with 'Prime' applied to each.
    </dl>

    Note that the first prime is 2, not 1:
    >> Prime[1]
     = 2

    >> Prime[167]
     = 991

    When given a list of integers, a list is returned:
    >> Prime[{5, 10, 15}]
     = {11, 29, 47}

    1.2 isn't an integer
    >> Prime[1.2]
     = Prime[1.2]

    Since 0 is less than 1, like 1.2 it is invalid.
    >> Prime[{0, 1, 1.2, 3}]
     = {Prime[0], 2, Prime[1.2], 5}
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    summary_text = "n-esim prime number"

    def eval(self, n, evaluation: Evaluation):
        "Prime[n_]"
        return from_sympy(SympyPrime(n.to_sympy()))

    def to_sympy(self, expr, **kwargs):
        if expr.has_form("Prime", 1):
            return SympyPrime(expr.elements[0].to_sympy(**kwargs))


class PrimePi(SympyFunction):
    """
    <url>:Prime numbers:https://reference.wolfram.com/language/ref/PrimePi.html</url>

    <dl>
    <dt>'PrimePi[$x$]'
        <dd>gives the number of primes less than or equal to $x$.
    </dl>

    PrimePi is the inverse of Prime:
    >> PrimePi[2]
     = 1

    >> PrimePi[100]
     = 25

    >> PrimePi[-1]
     = 0

    >> PrimePi[3.5]
     = 2

    >> PrimePi[E]
     = 1
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    mpmath_name = "primepi"
    summary_text = "amount of prime numbers less than or equal"
    sympy_name = "primepi"

    # TODO: Traditional Form

    def eval(self, n, evaluation: Evaluation):
        "PrimePi[n_?NumericQ]"
        result = sympy.primepi(eval_N(n, evaluation).to_python())
        return Integer(result)


class PrimePowerQ(Builtin):
    """
    <url>:Prime numbers:https://reference.wolfram.com/language/ref/PrimePowerQ.html</url>

    <dl>
    <dt>'PrimePowerQ[$n$]'
        <dd>returns 'True' if $n$ is a power of a prime number.
    </dl>

    >> PrimePowerQ[9]
     = True

    >> PrimePowerQ[52142]
     = False

    >> PrimePowerQ[-8]
     = True

    >> PrimePowerQ[371293]
     = True
    """

    attributes = A_LISTABLE | A_PROTECTED | A_READ_PROTECTED
    rules = {
        "PrimePowerQ[1]": "False",
    }
    summary_text = "test if a number is a power of a prime number"

    # TODO: GaussianIntegers option
    """
    ##> PrimePowerQ[5, GaussianIntegers -> True]
     = False
    """

    # TODO: Complex args
    """
    ##> PrimePowerQ[{3 + I, 3 - 2 I, 3 + 4 I, 9 + 7 I}]
     = {False, True, True, False}
    """

    # TODO: Gaussian rationals
    """
    ##> PrimePowerQ[2/125 - 11 I/125]
     = True
    """

    def eval(self, n, evaluation: Evaluation):
        "PrimePowerQ[n_]"
        n = n.get_int_value()
        if n is None:
            return SymbolFalse

        n = abs(n)
        return from_bool(len(sympy.factorint(n)) == 1)


class RandomPrime(Builtin):
    """
    <url>:Prime numbers:https://reference.wolfram.com/language/ref/RandomPrime.html</url>

    <dl>
      <dt>'RandomPrime[{$imin$, $imax}]'
      <dd>gives a random prime between $imin$ and $imax$.

      <dt>'RandomPrime[$imax$]'
      <dd>gives a random prime between 2 and $imax$.

      <dt>'RandomPrime[$range$, $n$]'
      <dd>gives a list of $n$ random primes in $range$.
    </dl>

    >> RandomPrime[{14, 17}]
     = 17

    >> RandomPrime[{14, 16}, 1]
     : There are no primes in the specified interval.
     = RandomPrime[{14, 16}, 1]

    >> RandomPrime[{8,12}, 3]
     = {11, 11, 11}

    >> RandomPrime[{10,30}, {2,5}]
     = ...
    """

    messages = {
        "posdim": (
            "The dimensions parameter `1` is expected to be a positive "
            "integer or a list of positive integers."
        ),
        "noprime": "There are no primes in the specified interval.",
        "prmrng": (
            "First argument `1` is not a positive integer or a list "
            "of two positive integers."
        ),
        "posint": (
            "The parameter `1` describing the interval is expected to "
            "be a positive integer."
        ),
    }

    rules = {
        "RandomPrime[imax_?NotListQ]": "RandomPrime[{1, imax}, 1]",
        "RandomPrime[int_List]": "RandomPrime[int, 1]",
        "RandomPrime[imax_List, n_?ArrayQ]": ("ConstantArray[RandomPrime[imax, 1], n]"),
        "RandomPrime[imax_?NotListQ, n_?ArrayQ]": (
            "ConstantArray[RandomPrime[{1, imax}, 1], n]"
        ),
    }
    summary_text = "picks a random prime in an interval"

    # TODO: Use random state as in other randomised methods within mathics

    def eval(self, interval, n, evaluation: Evaluation):
        "RandomPrime[interval_List, n_]"

        if not isinstance(n, Integer):
            evaluation.message("RandomPrime", "posdim", n)
            return
        py_n = n.to_python()

        py_int = interval.to_python()
        if not (isinstance(py_int, list) and len(py_int) == 2):
            evaluation.message("RandomPrime", "prmrng", interval)

        imin, imax = min(py_int), max(py_int)
        if imin <= 0 or not isinstance(imin, int):
            evaluation.message("RandomPrime", "posint", interval.elements[0])
            return

        if imax <= 0 or not isinstance(imax, int):
            evaluation.message("RandomPrime", "posint", interval.elements[1])
            return

        try:
            if py_n == 1:
                return Integer(sympy.ntheory.randprime(imin, imax + 1))
            return from_python(
                [sympy.ntheory.randprime(imin, imax + 1) for i in range(py_n)]
            )
        except ValueError:
            evaluation.message("RandomPrime", "noprime")
            return
