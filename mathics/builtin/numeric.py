# cython: language_level=3
# -*- coding: utf-8 -*-

# Note: docstring is flowed in documentation. Line breaks in the docstring will appear in the
# printed output, so be carful not to add then mid-sentence.

"""
Numerical Functions

Support for approximate real numbers and exact real numbers represented in algebraic or symbolic form.
"""

import sympy

from mathics.builtin.base import Builtin
from mathics.core.atoms import Complex, Integer, Integer0, Rational, Real
from mathics.core.attributes import listable, numeric_function, protected
from mathics.core.convert.sympy import from_sympy
from mathics.core.evaluators import eval_nvalues
from mathics.core.expression import Expression
from mathics.core.number import machine_epsilon
from mathics.core.symbols import SymbolDivide, SymbolMachinePrecision, SymbolTimes


def chop(expr, delta=10.0 ** (-10.0)):
    if isinstance(expr, Real):
        if expr.is_nan(expr):
            return expr
        if -delta < expr.get_float_value() < delta:
            return Integer0
    elif isinstance(expr, Complex) and expr.is_inexact():
        real, imag = expr.real, expr.imag
        if -delta < real.get_float_value() < delta:
            real = Integer0
        if -delta < imag.get_float_value() < delta:
            imag = Integer0
        return Complex(real, imag)
    elif isinstance(expr, Expression):
        return Expression(
            chop(expr.head), *[chop(element) for element in expr.elements]
        )
    return expr


class Chop(Builtin):
    """
    <dl>
      <dt>'Chop[$expr$]'
      <dd>replaces floating point numbers close to 0 by 0.

      <dt>'Chop[$expr$, $delta$]'
      <dd>uses a tolerance of $delta$. The default tolerance is '10^-10'.
    </dl>

    >> Chop[10.0 ^ -16]
     = 0
    >> Chop[10.0 ^ -9]
     = 1.×10^-9
    >> Chop[10 ^ -11 I]
     = I / 100000000000
    >> Chop[0. + 10 ^ -11 I]
     = 0
    """

    messages = {
        "tolnn": "Tolerance specification a must be a non-negative number.",
    }

    rules = {
        "Chop[expr_]": "Chop[expr, 10^-10]",
    }

    summary_text = "set sufficiently small numbers or imaginary parts to zero"

    def apply(self, expr, delta, evaluation):
        "Chop[expr_, delta_:(10^-10)]"

        delta = delta.round_to_float(evaluation)
        if delta is None or delta < 0:
            return evaluation.message("Chop", "tolnn")

        return chop(expr, delta=delta)


class N(Builtin):
    """
    <dl>
    <dt>'N[$expr$, $prec$]'
        <dd>evaluates $expr$ numerically with a precision of $prec$ digits.
    </dl>
    >> N[Pi, 50]
     = 3.1415926535897932384626433832795028841971693993751

    >> N[1/7]
     = 0.142857

    >> N[1/7, 5]
     = 0.14286

    You can manually assign numerical values to symbols.
    When you do not specify a precision, 'MachinePrecision' is taken.
    >> N[a] = 10.9
     = 10.9
    >> a
     = a

    'N' automatically threads over expressions, except when a symbol has
     attributes 'NHoldAll', 'NHoldFirst', or 'NHoldRest'.
    >> N[a + b]
     = 10.9 + b
    >> N[a, 20]
     = a
    >> N[a, 20] = 11;
    >> N[a + b, 20]
     = 11.000000000000000000 + b
    >> N[f[a, b]]
     = f[10.9, b]
    >> SetAttributes[f, NHoldAll]
    >> N[f[a, b]]
     = f[a, b]

    The precision can be a pattern:
    >> N[c, p_?(#>10&)] := p
    >> N[c, 3]
     = c
    >> N[c, 11]
     = 11.000000000

    You can also use 'UpSet' or 'TagSet' to specify values for 'N':
    >> N[d] ^= 5;
    However, the value will not be stored in 'UpValues', but
    in 'NValues' (as for 'Set'):
    >> UpValues[d]
     = {}
    >> NValues[d]
     = {HoldPattern[N[d, MachinePrecision]] :> 5}
    >> e /: N[e] = 6;
    >> N[e]
     = 6.

    Values for 'N[$expr$]' must be associated with the head of $expr$:
    >> f /: N[e[f]] = 7;
     : Tag f not found or too deep for an assigned rule.

    You can use 'Condition':
    >> N[g[x_, y_], p_] := x + y * Pi /; x + y > 3
    >> SetAttributes[g, NHoldRest]
    >> N[g[1, 1]]
     = g[1., 1]
    >> N[g[2, 2]] // InputForm
     = 8.283185307179586

    The precision of the result is no higher than the precision of the input
    >> N[Exp[0.1], 100]
     = 1.10517
    >> % // Precision
     = MachinePrecision
    >> N[Exp[1/10], 100]
     = 1.105170918075647624811707826490246668224547194737518718792863289440967966747654302989143318970748654
    >> % // Precision
     = 100.
    >> N[Exp[1.0`20], 100]
     = 2.7182818284590452354
    >> % // Precision
     = 20.

    N can also accept an option "Method". This establishes what is the prefered underlying method to
    compute numerical values:
    >> N[F[Pi], 30, Method->"numpy"]
     = F[3.14159265358979300000000000000]
    >> N[F[Pi], 30, Method->"sympy"]
     = F[3.14159265358979323846264338328]
    #> p=N[Pi,100]
     = 3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117068
    #> ToString[p]
     = 3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117068

    #> N[1.012345678901234567890123, 20]
     = 1.0123456789012345679

    #> N[I, 30]
     = 1.00000000000000000000000000000 I

    #> N[1.012345678901234567890123, 50]
     = 1.01234567890123456789012
    #> % // Precision
     = 24.
    """

    options = {"Method": "Automatic"}

    messages = {
        "precbd": ("Requested precision `1` is not a " + "machine-sized real number."),
        "preclg": (
            "Requested precision `1` is larger than $MaxPrecision. "
            + "Using current $MaxPrecision of `2` instead. "
            + "$MaxPrecision = Infinity specifies that any precision "
            + "should be allowed."
        ),
        "precsm": (
            "Requested precision `1` is smaller than "
            + "$MinPrecision. Using current $MinPrecision of "
            + "`2` instead."
        ),
    }

    summary_text = "numerical evaluation to specified precision and accuracy"

    def apply_with_prec(self, expr, prec, evaluation, options=None):
        "N[expr_, prec_, OptionsPattern[%(name)s]]"

        # If options are passed, set the preference in evaluation, and call again
        # without options set.
        # This also prevents to store this as an nvalue (nvalues always have two elements).
        preference = None
        # If a Method is passed, and the method is not either "Automatic" or
        # the last preferred method, according to evaluation._preferred_n_method,
        # set the new preference, reevaluate, and then remove the preference.
        if options:
            preference_queue = evaluation._preferred_n_method
            preference = self.get_option(
                options, "Method", evaluation
            ).get_string_value()
            if preference == "Automatic":
                preference = None
            if preference_queue and preference == preference_queue[-1]:
                preference = None

            if preference:
                preference_queue.append(preference)
                try:
                    result = self.apply_with_prec(expr, prec, evaluation)
                except Exception:
                    result = None
                preference_queue.pop()
                return result

        return eval_nvalues(expr, prec, evaluation)

    def apply_N(self, expr, evaluation):
        """N[expr_]"""
        # TODO: Specialize for atoms
        return eval_nvalues(expr, SymbolMachinePrecision, evaluation)


class Rationalize(Builtin):
    """
    <dl>
      <dt>'Rationalize[$x$]'
      <dd>converts a real number $x$ to a nearby rational number with small denominator.

      <dt>'Rationalize[$x$, $dx$]'
      <dd>finds the rational number lies within $dx$ of $x$.
    </dl>

    >> Rationalize[2.2]
    = 11 / 5

    For negative $x$, '-Rationalize[-$x$] == Rationalize[$x$]' which gives symmetric results:
    >> Rationalize[-11.5, 1]
    = -11

    Not all numbers can be well approximated.
    >> Rationalize[N[Pi]]
     = 3.14159

    Find the exact rational representation of 'N[Pi]'
    >> Rationalize[N[Pi], 0]
     = 245850922 / 78256779

    #> Rationalize[N[Pi] + 0.8 I, x]
     : Tolerance specification x must be a non-negative number.
     = Rationalize[3.14159 + 0.8 I, x]

    #> Rationalize[N[Pi] + 0.8 I, -1]
     : Tolerance specification -1 must be a non-negative number.
     = Rationalize[3.14159 + 0.8 I, -1]

    #> Rationalize[x, y]
     : Tolerance specification y must be a non-negative number.
     = Rationalize[x, y]
    """

    messages = {
        "tolnn": "Tolerance specification `1` must be a non-negative number.",
    }

    rules = {
        "Rationalize[z_Complex]": "Rationalize[Re[z]] + I Rationalize[Im[z]]",
        "Rationalize[z_Complex, dx_?Internal`RealValuedNumberQ]/;dx >= 0": "Rationalize[Re[z], dx] + I Rationalize[Im[z], dx]",
    }

    summary_text = "find a rational approximation"

    def apply(self, x, evaluation):
        "Rationalize[x_]"

        py_x = x.to_sympy()
        if py_x is None or (not py_x.is_number) or (not py_x.is_real):
            return x

        # For negative x, MMA treads Rationalize[x] as -Rationalize[-x].
        # Whether this is an implementation choice or not, it has been
        # expressed that having this give symmetric results for +/-
        # is nice.
        # See https://mathematica.stackexchange.com/questions/253637/how-to-think-about-the-answer-to-rationlize-11-5-1
        if py_x.is_positive:
            return from_sympy(self.find_approximant(py_x))
        else:
            return -from_sympy(self.find_approximant(-py_x))

    @staticmethod
    def find_approximant(x):
        c = 1e-4
        it = sympy.ntheory.continued_fraction_convergents(
            sympy.ntheory.continued_fraction_iterator(x)
        )
        for i in it:
            p, q = i.as_numer_denom()
            tol = c / q**2
            if abs(i - x) <= tol:
                return i
            if tol < machine_epsilon:
                break
        return x

    @staticmethod
    def find_exact(x):
        p, q = x.as_numer_denom()
        it = sympy.ntheory.continued_fraction_convergents(
            sympy.ntheory.continued_fraction_iterator(x)
        )
        for i in it:
            p, q = i.as_numer_denom()
            if abs(x - i) < machine_epsilon:
                return i

    def apply_dx(self, x, dx, evaluation):
        "Rationalize[x_, dx_]"
        py_x = x.to_sympy()
        if py_x is None:
            return x
        py_dx = dx.to_sympy()
        if (
            py_dx is None
            or (not py_dx.is_number)
            or (not py_dx.is_real)
            or py_dx.is_negative
        ):
            return evaluation.message("Rationalize", "tolnn", dx)
        elif py_dx == 0:
            return from_sympy(self.find_exact(py_x))

        # For negative x, MMA treads Rationalize[x] as -Rationalize[-x].
        # Whether this is an implementation choice or not, it has been
        # expressed that having this give symmetric results for +/-
        # is nice.
        # See https://mathematica.stackexchange.com/questions/253637/how-to-think-about-the-answer-to-rationlize-11-5-1
        if py_x.is_positive:
            a = self.approx_interval_continued_fraction(py_x - py_dx, py_x + py_dx)
            sym_x = sympy.ntheory.continued_fraction_reduce(a)
        else:
            a = self.approx_interval_continued_fraction(-py_x - py_dx, -py_x + py_dx)
            sym_x = -sympy.ntheory.continued_fraction_reduce(a)

        return Integer(sym_x) if sym_x.is_integer else Rational(sym_x)

    @staticmethod
    def approx_interval_continued_fraction(xmin, xmax):
        result = []
        a_gen = sympy.ntheory.continued_fraction_iterator(xmin)
        b_gen = sympy.ntheory.continued_fraction_iterator(xmax)
        while True:
            a, b = next(a_gen), next(b_gen)
            if a == b:
                result.append(a)
            else:
                result.append(min(a, b) + 1)
                break
        return result


class RealValuedNumericQ(Builtin):
    # No docstring since this is internal and it will mess up documentation.
    # FIXME: Perhaps in future we will have a more explicite way to indicate not
    # to add something to the docs.
    context = "Internal`"

    rules = {
        "Internal`RealValuedNumericQ[x_]": "Head[N[x]] === Real",
    }


class RealValuedNumberQ(Builtin):
    # No docstring since this is internal and it will mess up documentation.
    # FIXME: Perhaps in future we will have a more explicite way to indicate not
    # to add something to the docs.
    context = "Internal`"

    rules = {
        "Internal`RealValuedNumberQ[x_Real]": "True",
        "Internal`RealValuedNumberQ[x_Integer]": "True",
        "Internal`RealValuedNumberQ[x_Rational]": "True",
        "Internal`RealValuedNumberQ[x_]": "False",
    }


class Round(Builtin):
    """
    <dl>
      <dt>'Round[$expr$]'
      <dd>rounds $expr$ to the nearest integer.

      <dt>'Round[$expr$, $k$]'
      <dd>rounds $expr$ to the closest multiple of $k$.
    </dl>

    >> Round[10.6]
     = 11
    >> Round[0.06, 0.1]
     = 0.1
    >> Round[0.04, 0.1]
     = 0.

    Constants can be rounded too
    >> Round[Pi, .5]
     = 3.
    >> Round[Pi^2]
     = 10

    Round to exact value
    >> Round[2.6, 1/3]
     = 8 / 3
    >> Round[10, Pi]
     = 3 Pi

    Round complex numbers
    >> Round[6/(2 + 3 I)]
     = 1 - I
    >> Round[1 + 2 I, 2 I]
     = 2 I

    Round Negative numbers too
    >> Round[-1.4]
     = -1

    Expressions other than numbers remain unevaluated:
    >> Round[x]
     = Round[x]
    >> Round[1.5, k]
     = Round[1.5, k]
    """

    attributes = listable | numeric_function | protected

    rules = {
        "Round[expr_?NumericQ]": "Round[Re[expr], 1] + I * Round[Im[expr], 1]",
        "Round[expr_Complex, k_?RealNumberQ]": (
            "Round[Re[expr], k] + I * Round[Im[expr], k]"
        ),
    }

    summary_text = "find closest integer or multiple of"

    def apply(self, expr, k, evaluation):
        "Round[expr_?NumericQ, k_?NumericQ]"

        n = Expression(SymbolDivide, expr, k).round_to_float(
            evaluation, permit_complex=True
        )
        if n is None:
            return
        elif isinstance(n, complex):
            n = round(n.real)
        else:
            n = round(n)
        n = int(n)
        return Expression(SymbolTimes, Integer(n), k)
