"""
Numerical Properties
"""
from itertools import combinations

import sympy

from mathics.builtin.base import Builtin, SympyFunction, Test
from mathics.core.atoms import Integer, Integer0, Number
from mathics.core.attributes import A_LISTABLE, A_NUMERIC_FUNCTION, A_PROTECTED
from mathics.core.convert.python import from_bool, from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolExpandAll, SymbolSimplify
from mathics.eval.nevaluator import eval_N


class CoprimeQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/CoprimeQ.html</url>

    <dl>
      <dt>'CoprimeQ[$x$, $y$]'
      <dd>tests whether $x$ and $y$ are coprime by computing their greatest \
          common divisor.
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

    def eval(self, args, evaluation: Evaluation):
        "CoprimeQ[args__]"

        py_args = [arg.to_python() for arg in args.get_sequence()]
        if not all(isinstance(i, int) or isinstance(i, complex) for i in py_args):
            return SymbolFalse

        if all(sympy.gcd(n, m) == 1 for (n, m) in combinations(py_args, 2)):
            return SymbolTrue
        else:
            return SymbolFalse


class EvenQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/EvenQ.html</url>

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


class IntegerQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/IntegerQ.html</url>

    <dl>
      <dt>'IntegerQ[$expr$]'
      <dd>returns 'True' if $expr$ is an integer, and 'False' otherwise.
    </dl>

    >> IntegerQ[3]
     = True
    >> IntegerQ[Pi]
     = False
    """

    summary_text = "test whether an expression is an integer"

    def test(self, expr):
        return isinstance(expr, Integer)


class MachineNumberQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MachineNumberQ.html</url>

    <dl>
      <dt>'MachineNumberQ[$expr$]'
      <dd>returns 'True' if $expr$ is a machine-precision real or complex number.
    </dl>

     = True
    >> MachineNumberQ[3.14159265358979324]
     = False
    >> MachineNumberQ[1.5 + 2.3 I]
     = True
    >> MachineNumberQ[2.71828182845904524 + 3.14159265358979324 I]
     = False
    #> MachineNumberQ[1.5 + 3.14159265358979324 I]
     = True
    #> MachineNumberQ[1.5 + 5 I]
     = True
    """

    summary_text = "test if expression is a machine‐precision real or complex number"

    def test(self, expr):
        return expr.is_machine_precision()


class Negative(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Negative.html</url>

    <dl>
      <dt>'Negative[$x$]'
      <dd>returns 'True' if $x$ is a negative real number.
    </dl>
    >> Negative[0]
     = False
    >> Negative[-3]
     = True
    >> Negative[10/7]
     = False
    >> Negative[1+2I]
     = False
    >> Negative[a + b]
     = Negative[a + b]
    #> Negative[-E]
     = True
    #> Negative[Sin[{11, 14}]]
     = {True, False}
    """

    attributes = A_LISTABLE | A_PROTECTED

    rules = {
        "Negative[x_?NumericQ]": "If[x < 0, True, False, False]",
    }
    summary_text = "test whether an expression is a negative number"


class NonNegative(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/NonNegative.html</url>

    <dl>
      <dt>'NonNegative[$x$]'
      <dd>returns 'True' if $x$ is a positive real number or zero.
    </dl>

    >> {Positive[0], NonNegative[0]}
     = {False, True}
    """

    attributes = A_LISTABLE | A_PROTECTED

    rules = {
        "NonNegative[x_?NumericQ]": "If[x >= 0, True, False, False]",
    }
    summary_text = "test whether an expression is a non-negative number"


class NonPositive(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/NonPositive.html</url>

    <dl>
      <dt>'NonPositive[$x$]'
      <dd>returns 'True' if $x$ is a negative real number or zero.
    </dl>

    >> {Negative[0], NonPositive[0]}
     = {False, True}
    """

    attributes = A_LISTABLE | A_PROTECTED

    rules = {
        "NonPositive[x_?NumericQ]": "If[x <= 0, True, False, False]",
    }
    summary_text = "test whether an expression is a non-positive number"


class NumberQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/NumberQ.html</url>

    <dl>
      <dt>'NumberQ[$expr$]'
      <dd>returns 'True' if $expr$ is an explicit number, and 'False' \
          otherwise.
    </dl>

    >> NumberQ[3+I]
     = True
    >> NumberQ[5!]
     = True
    >> NumberQ[Pi]
     = False
    """

    summary_text = "test whether an expression is a number"

    def test(self, expr):
        return isinstance(expr, Number)


class NumericQ(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/NumericQ.html</url>

    <dl>
      <dt>'NumericQ[$expr$]'
      <dd>tests whether $expr$ represents a numeric quantity.
    </dl>

    >> NumericQ[2]
     = True
    >> NumericQ[Sqrt[Pi]]
     = True
    >> NumberQ[Sqrt[Pi]]
     = False

    It is possible to set that a symbol is numeric or not by assign a boolean value
    to ``NumericQ``
    >> NumericQ[a]=True
     = True
    >> NumericQ[a]
     = True
    >> NumericQ[Sin[a]]
     = True

    Clear and ClearAll do not restore the default value.

    >> Clear[a]; NumericQ[a]
     = True
    >> ClearAll[a]; NumericQ[a]
     = True
    >> NumericQ[a]=False; NumericQ[a]
     = False
    NumericQ can only set to True or False
    >> NumericQ[a] = 37
     : Cannot set NumericQ[a] to 37; the lhs argument must be a symbol and the rhs must be True or False.
     = 37
    """

    messages = {
        "argx": "NumericQ called with `1` arguments; 1 argument is expected.",
        "set": "Cannot set `1` to `2`; the lhs argument must be a symbol and the rhs must be True or False.",
    }
    summary_text = "test whether an expression is a number"

    def eval(self, expr, evaluation):
        "NumericQ[expr_]"
        return from_bool(expr.is_numeric(evaluation))


class OddQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/OddQ.html</url>

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


class PossibleZeroQ(SympyFunction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/PossibleZeroQ.html</url>

    <dl>
      <dt>'PossibleZeroQ[$expr$]'
      <dd>returns 'True' if basic symbolic and numerical methods suggest that \
          expr has value zero, and 'False' otherwise.
    </dl>

    Test whether a numeric expression is zero:
    >> PossibleZeroQ[E^(I Pi/4) - (-1)^(1/4)]
     = True

    The determination is approximate.

    Test whether a symbolic expression is likely to be identically zero:
    >> PossibleZeroQ[(x + 1) (x - 1) - x^2 + 1]
     = True


    >> PossibleZeroQ[(E + Pi)^2 - E^2 - Pi^2 - 2 E Pi]
     = True

    Show that a numeric expression is nonzero:
    >> PossibleZeroQ[E^Pi - Pi^E]
     = False

    >> PossibleZeroQ[1/x + 1/y - (x + y)/(x y)]
     = True

    Decide that a numeric expression is zero, based on approximate computations:
    >> PossibleZeroQ[2^(2 I) - 2^(-2 I) - 2 I Sin[Log[4]]]
     = True

    >> PossibleZeroQ[Sqrt[x^2] - x]
     = False
    """

    summary_text = "test whether an expression is estimated to be zero"
    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    sympy_name = "_iszero"

    def eval(self, expr, evaluation):
        "%(name)s[expr_]"
        from sympy.matrices.utilities import _iszero

        sympy_expr = expr.to_sympy()
        result = _iszero(sympy_expr)
        if result is None:
            # try expanding the expression
            exprexp = Expression(SymbolExpandAll, expr).evaluate(evaluation)
            exprexp = exprexp.to_sympy()
            result = _iszero(exprexp)
        if result is None:
            # Can't get exact answer, so try approximate equal
            numeric_val = eval_N(expr, evaluation)
            if numeric_val and hasattr(numeric_val, "is_approx_zero"):
                result = numeric_val.is_approx_zero
            elif not numeric_val.is_numeric(evaluation):
                return (
                    SymbolTrue
                    if Expression(SymbolSimplify, expr).evaluate(evaluation) == Integer0
                    else SymbolFalse
                )

        return from_python(result)


class Positive(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Positive.html</url>

    <dl>
      <dt>'Positive[$x$]'
      <dd>returns 'True' if $x$ is a positive real number.
    </dl>

    >> Positive[1]
     = True

    'Positive' returns 'False' if $x$ is zero or a complex number:
    >> Positive[0]
     = False
    >> Positive[1 + 2 I]
     = False

    #> Positive[Pi]
     = True
    #> Positive[x]
     = Positive[x]
    #> Positive[Sin[{11, 14}]]
     = {False, True}
    """

    attributes = A_LISTABLE | A_PROTECTED

    rules = {
        "Positive[x_?NumericQ]": "If[x > 0, True, False, False]",
    }
    summary_text = "test whether an expression is a positive number"


class PrimeQ(SympyFunction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/PrimeQ.html</url>

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

    def eval(self, n, evaluation: Evaluation):
        "PrimeQ[n_]"

        n = n.get_int_value()
        if n is None:
            return SymbolFalse

        n = abs(n)
        if sympy.isprime(n):
            return SymbolTrue
        else:
            return SymbolFalse
