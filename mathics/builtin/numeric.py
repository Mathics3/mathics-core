# -*- coding: utf-8 -*-

# Note: docstring is flowed in documentation. Line breaks in the
# docstring will appear in the printed output, so be careful not to
# add them mid-sentence. Line breaks like \ this work though.

"""
Numerical Functions

Support for approximate real numbers and exact real numbers represented \
in algebraic or symbolic form.
"""

from typing import Optional

import sympy

from mathics.core.atoms import (
    Complex,
    Integer,
    Integer0,
    IntegerM1,
    Number,
    Rational,
    Real,
)
from mathics.core.attributes import (
    A_HOLD_ALL,
    A_LISTABLE,
    A_NUMERIC_FUNCTION,
    A_ORDERLESS,
    A_PROTECTED,
)
from mathics.core.builtin import Builtin, MPMathFunction, SympyFunction
from mathics.core.convert.sympy import from_sympy
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.number import MACHINE_EPSILON
from mathics.core.symbols import (
    Symbol,
    SymbolDivide,
    SymbolFalse,
    SymbolMachinePrecision,
    SymbolTimes,
    SymbolTrue,
)
from mathics.core.systemsymbols import SymbolPiecewise
from mathics.eval.inference import evaluate_predicate
from mathics.eval.nevaluator import eval_NValues
from mathics.eval.numeric import (
    eval_Abs,
    eval_negate_number,
    eval_RealSign,
    eval_Sign,
    eval_UnitStep,
    eval_UnitStep_multidimensional,
)


def chop(expr, delta=10.0 ** (-10.0)):
    if isinstance(expr, Real):
        if expr.is_nan(expr):
            return expr
        if -delta < expr.value < delta:
            return Integer0
    elif isinstance(expr, Complex) and expr.is_inexact():
        real, imag = expr.real, expr.imag
        if -delta < real.get_float_value() < delta:
            real = Integer0
        if -delta < imag.value < delta:
            imag = Integer0
        return Complex(real, imag)
    elif isinstance(expr, Expression):
        return Expression(
            chop(expr.head), *[chop(element) for element in expr.elements]
        )
    return expr


class Abs(MPMathFunction):
    """
    <url>
    :Absolute value:
    https://en.wikipedia.org/wiki/Absolute_value</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions
    /elementary.html#sympy.functions.elementary.complexes.Abs</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/Abs</url>)

    <dl>
      <dt>'Abs'[$x$]
      <dd>returns the absolute value of $x$.
    </dl>

    >> Abs[-3]
     = 3

    >> Plot[Abs[x], {x, -4, 4}]
     = -Graphics-

    'Abs' returns the magnitude of complex numbers:
    >> Abs[3 + I]
     = Sqrt[10]
    >> Abs[3.0 + I]
     = 3.16228

    All of the below evaluate to Infinity:

    >> Abs[Infinity] == Abs[I Infinity] == Abs[ComplexInfinity]
     = True
    """

    mpmath_name = "fabs"  # mpmath actually uses python abs(x) / x.__abs__()
    rules = {
        "Abs[Undefined]": "Undefined",
    }
    summary_text = "get absolute value of a number"
    sympy_name = "Abs"

    def eval(self, x, evaluation: Evaluation):
        "Abs[x_]"
        result = eval_Abs(x)
        if result is not None:
            return result
        return super(Abs, self).eval(x, evaluation)


class Chop(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Chop.html</url>

    <dl>
      <dt>'Chop'[$expr$]
      <dd>replaces floating point numbers close to 0 by 0.

      <dt>'Chop'[$expr$, $delta$]
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

    def eval(self, expr, delta, evaluation: Evaluation):
        "Chop[expr_, delta_:(10^-10)]"

        delta = delta.round_to_float(evaluation)
        if delta is None or delta < 0:
            evaluation.message("Chop", "tolnn")
            return

        return chop(expr, delta=delta)


class N(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/N.html</url>

    <dl>
    <dt>'N'[$expr$, $prec$]
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

    N can also accept an option "Method". This establishes what is the \
    prefrered underlying method to compute numerical values:
    >> N[F[Pi], 30, Method->"numpy"]
     = F[3.14159265358979300000000000000]
    >> N[F[Pi], 30, Method->"sympy"]
     = F[3.14159265358979323846264338328]
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

    def eval_with_prec(self, expr, prec, evaluation, options=None):
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
                    result = self.eval_with_prec(expr, prec, evaluation)
                except Exception:
                    result = None
                preference_queue.pop()
                return result

        return eval_NValues(expr, prec, evaluation)

    def eval_N(self, expr, evaluation: Evaluation):
        """N[expr_]"""
        # TODO: Specialize for atoms
        return eval_NValues(expr, SymbolMachinePrecision, evaluation)


class Piecewise(SympyFunction):
    """
    <url>:SymPy:
    https://docs.sympy.org/latest/modules/functions
    /elementary.html#piecewise</url>, <url>
    :WMA:https://reference.wolfram.com/language/ref/Piecewise.html</url>

    <dl>
      <dt>'Piecewise[{{expr1, cond1}, ...}]'
      <dd>represents a piecewise function.

      <dt>'Piecewise[{{expr1, cond1}, ...}, expr]'
      <dd>represents a piecewise function with default 'expr'.
    </dl>

    Heaviside function
    >> Piecewise[{{0, x <= 0}}, 1]
     = Piecewise[{{0, x <= 0}}, 1]

    ## D[%, x]
    ## Piecewise({{0, Or[x < 0, x > 0]}}, Indeterminate).

    >> Integrate[Piecewise[{{1, x <= 0}, {-1, x > 0}}], x]
     = Piecewise[{{x, x <= 0}}, -x]

    >> Integrate[Piecewise[{{1, x <= 0}, {-1, x > 0}}], {x, -1, 2}]
     = -1

    Piecewise defaults to 0 if no other case is matching.
    >> Piecewise[{{1, False}}]
     = 0

    >> Plot[Piecewise[{{Log[x], x > 0}, {x*-0.5, x < 0}}], {x, -1, 1}]
     = -Graphics-

    >> Piecewise[{{0 ^ 0, False}}, -1]
     = -1
    """

    summary_text = "an arbitrary piecewise function"
    sympy_name = "Piecewise"

    attributes = A_HOLD_ALL | A_PROTECTED

    def eval(self, items, evaluation: Evaluation):
        "%(name)s[items__]"
        result = self.to_sympy(
            Expression(SymbolPiecewise, *items.get_sequence()), evaluation=evaluation
        )
        if result is None:
            return
        if not isinstance(result, sympy.Piecewise):
            result = from_sympy(result)
            return result

    def to_sympy(self, expr, **kwargs):
        elements = expr.elements
        evaluation = kwargs.get("evaluation", None)
        if len(elements) not in (1, 2):
            return

        sympy_cases = []
        for case in elements[0].elements:
            if case.get_head_name() != "System`List":
                return
            if len(case.elements) != 2:
                return
            then, cond = case.elements
            if evaluation:
                cond = evaluate_predicate(cond, evaluation)

            sympy_cond = None
            if isinstance(cond, Symbol):
                if cond is SymbolTrue:
                    sympy_cond = True
                elif cond is SymbolFalse:
                    sympy_cond = False
            if sympy_cond is None:
                sympy_cond = cond.to_sympy(**kwargs)
                if not (sympy_cond.is_Relational or sympy_cond.is_Boolean):
                    return

            sympy_cases.append((then.to_sympy(**kwargs), sympy_cond))

        if len(elements) == 2:  # default case
            sympy_cases.append((elements[1].to_sympy(**kwargs), True))
        else:
            sympy_cases.append((Integer0.to_sympy(**kwargs), True))

        return sympy.Piecewise(*sympy_cases)

    def from_sympy(self, sympy_name, args):
        # Hack to get around weird sympy.Piecewise 'otherwise' behaviour
        if str(args[-1].elements[1]).startswith("System`_True__Dummy_"):
            args[-1].elements[1] = SymbolTrue
        return Expression(self.get_name(), args)


class Rationalize(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Rationalize.html</url>

    <dl>
      <dt>'Rationalize'[$x$]
      <dd>converts a real number $x$ to a nearby rational number with \
          small denominator.

      <dt>'Rationalize'[$x$, $d_x$]
      <dd>finds the rational number lies within $d_x$ of $x$.
    </dl>

    >> Rationalize[2.2]
    = 11 / 5

    For negative $x$, '-Rationalize[-$x$] == Rationalize[$x$]' which \
    gives symmetric results:
    >> Rationalize[-11.5, 1]
    = -11

    Not all numbers can be well approximated.
    >> Rationalize[N[Pi]]
     = 3.14159

    Find the exact rational representation of 'N[Pi]'
    >> Rationalize[N[Pi], 0]
     = 245850922 / 78256779
    """

    messages = {
        "tolnn": "Tolerance specification `1` must be a non-negative number.",
    }

    rules = {
        "Rationalize[z_Complex]": "Rationalize[Re[z]] + I Rationalize[Im[z]]",
        "Rationalize[z_Complex, dx_?Internal`RealValuedNumberQ]/;dx >= 0": "Rationalize[Re[z], dx] + I Rationalize[Im[z], dx]",
    }

    summary_text = "find a rational approximation"

    def eval(self, x, evaluation: Evaluation):
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
            return from_sympy(-self.find_approximant(-py_x))

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
            if tol < MACHINE_EPSILON:
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
            if abs(x - i) < MACHINE_EPSILON:
                return i

    def eval_dx(self, x, dx, evaluation: Evaluation):
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
            evaluation.message("Rationalize", "tolnn", dx)
            return
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


class RealAbs(Builtin):
    """
    <url>:Abs (Real):
    https://en.wikipedia.org/wiki/Absolute_value</url> (<url>
    :WMA link:
    https://reference.wolfram.com/language/ref/RealAbs.html</url>)

    <dl>
      <dt>'RealAbs'[$x$]
      <dd>returns the absolute value of a real number $x$.
    </dl>

    'RealAbs' is also known as modulus. It is evaluated if $x$ can be compared \
    with $0$.

    >> RealAbs[-3.]
     = 3.
    'RealAbs[$z$]' is left unevaluated for complex $z$:
    >> RealAbs[2. + 3. I]
     = RealAbs[2. + 3. I]
    >> D[RealAbs[x ^ 2], x]
     = 2 x ^ 3 / RealAbs[x ^ 2]
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    rules = {
        "D[RealAbs[x_],x_]": "x/RealAbs[x]",
        "Integrate[RealAbs[x_],x_]": "1/2 x RealAbs[x]",
        "Integrate[RealAbs[u_],{u_,a_,b_}]": "1/2 b RealAbs[b]-1/2 a RealAbs[a]",
    }
    summary_text = "get absolute value of a real number"

    def eval(self, x: Number, evaluation: Evaluation):
        """RealAbs[x_]"""
        real_sign = eval_RealSign(x)
        if real_sign is IntegerM1:
            return eval_negate_number(x)
        if real_sign is None:
            return
        return x


class RealSign(Builtin):
    """
    <url>:Sign function:
    https://en.wikipedia.org/wiki/Sign_function</url> (<url>
    :WMA link:
    https://reference.wolfram.com/language/ref/RealSign.html</url>)

    <dl>
      <dt>'RealSign'[$x$]
      <dd>returns -1, 0 or 1 depending on whether $x$ is negative,
      zero or positive.
    </dl>

    'RealSign' is also known as $sgn$ or $signum$ function.

    >> RealSign[-3.]
     = -1
    'RealSign[$z$]' is left unevaluated for complex $z$:
    >> RealSign[2. + 3. I]
     = RealSign[2. + 3. I]

    >> D[RealSign[x^2],x]
     = 2 x Piecewise[{{0, x ^ 2 != 0}}, Indeterminate]
    >> Integrate[RealSign[u],{u,0,x}]
     = RealAbs[x]
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    rules = {
        "D[RealSign[x_],x_]": "Piecewise[{{0, x!=0}}, Indeterminate]",
        "Integrate[RealSign[x_],x_]": "RealAbs[x]",
        "Integrate[RealSign[u_],{u_, a_, b_}]": "RealAbs[b]-RealSign[a]",
    }
    summary_text = "real sign"

    def eval(self, x: Number, evaluation: Evaluation) -> Optional[Integer]:
        """RealSign[x_]"""
        return eval_RealSign(x)


class RealValuedNumberQ(Builtin):
    # No docstring since this is internal and it will mess up documentation.
    # FIXME: Perhaps in future we will have a more explicit way to indicate not
    # to add something to the docs.
    no_doc = True
    context = "Internal`"
    summary_text = "test whether an expression is a real number"
    rules = {
        "Internal`RealValuedNumberQ[x_Real]": "True",
        "Internal`RealValuedNumberQ[x_Integer]": "True",
        "Internal`RealValuedNumberQ[x_Rational]": "True",
        "Internal`RealValuedNumberQ[x_]": "False",
    }


class RealValuedNumericQ(Builtin):
    # No docstring since this is internal and it will mess up documentation.
    # FIXME: Perhaps in future we will have a more explicit way to indicate not
    # to add something to the docs.
    no_doc = True
    context = "Internal`"

    rules = {
        "Internal`RealValuedNumericQ[x_]": "Head[N[x]] === Real",
    }


class Round(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Round.html</url>

    <dl>
      <dt>'Round'[$expr$]
      <dd>rounds $expr$ to the nearest integer.

      <dt>'Round'[$expr$, $k$]
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

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    rules = {
        "Round[expr_?NumericQ]": "Round[Re[expr], 1] + I * Round[Im[expr], 1]",
        "Round[expr_Complex, k_?RealValuedNumberQ]": (
            "Round[Re[expr], k] + I * Round[Im[expr], k]"
        ),
    }

    summary_text = "find closest integer or multiple of"

    def eval(self, expr, k, evaluation: Evaluation):
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


class Sign(SympyFunction):
    """
    <url>
    :Sign:
    https://en.wikipedia.org/wiki/Sign_function</url> (<url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Sign.html</url>)

    <dl>
      <dt>'Sign'[$x$]
      <dd>return -1, 0, or 1 depending on whether $x$ is negative, zero, or positive.
    </dl>

    >> Sign[19]
     = 1
    >> Sign[-6]
     = -1
    >> Sign[0]
     = 0
    >> Sign[{-5, -10, 15, 20, 0}]
     = {-1, -1, 1, 1, 0}

    For a complex number, 'Sign' returns the phase of the number:
    >> Sign[3 - 4*I]
     = 3 / 5 - 4 I / 5

    """

    summary_text = "complex sign of a number"
    sympy_name = "sign"
    # mpmath_name = 'sign'

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    messages = {
        "argx": "Sign called with `1` arguments; 1 argument is expected.",
    }

    rules = {
        "Sign[Power[a_, b_]]": "Power[Sign[a], b]",
    }

    def eval(self, x, evaluation: Evaluation):
        "Sign[x_]"
        result = eval_Sign(x)
        if result is not None:
            return result
        # return None

        sympy_x = x.to_sympy()
        if sympy_x is None:
            return None
        # Unhandled cases. Use sympy
        return super(Sign, self).eval(x, evaluation)

    def eval_error(self, x, seqs, evaluation: Evaluation):
        "Sign[x_, seqs__]"
        evaluation.message("Sign", "argx", Integer(len(seqs.get_sequence()) + 1))


class UnitStep(Builtin):
    """
    <url>
    :Heaviside step function:
    https://en.wikipedia.org/wiki/Heaviside_step_function</url> (<url>
    :WMA link:
    https://reference.wolfram.com/language/ref/UnitStep.html</url>)

    <dl>
      <dt>'UnitStep'[$x$]
      <dd>return 0 if $x$ < 0, and 1 if $x$ >= 0.
      <dt>'UnitStep'[$x_1$, $x_2$, ...]
      <dd>return the multidimensional unit step function which is 1 only if none of the $xi$ are negative.
    </dl>

    Evaluation numerically:
    >> UnitStep[0.7]
     = 1

    We can use 'UnitStep' on irrational numbers and infinities:
    >> Map[UnitStep, {Pi, Infinity, -Infinity}]
     = {1, 1, 0}

    >> Table[UnitStep[x], {x, -3, 3}]
     = {0, 0, 0, 1, 1, 1, 1}

    Plot in one dimension:
    >> Plot[UnitStep[x], {x, -4, 4}]
     = -Graphics-

    ## UnitStep is a piecewise function
    ## PiecewiseExpand[UnitStep[x]]
    ## = ...
    """

    summary_text = "unit step function of a number"

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_ORDERLESS | A_PROTECTED

    def eval(self, x, evaluation: Evaluation):
        "UnitStep[x_]"
        return eval_UnitStep(x)

    def eval_multidimenional(self, seqs, evaluation: Evaluation):
        "UnitStep[seqs__]"
        return eval_UnitStep_multidimensional(seqs)
