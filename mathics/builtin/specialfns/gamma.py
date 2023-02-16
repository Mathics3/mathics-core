"""
Gamma and Related Functions
"""
import sys

import mpmath
import sympy

from mathics.builtin.arithmetic import _MPMathFunction, _MPMathMultiFunction
from mathics.builtin.base import PostfixOperator, SympyFunction
from mathics.core.atoms import Integer, Integer0, Number
from mathics.core.attributes import A_LISTABLE, A_NUMERIC_FUNCTION, A_PROTECTED
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.python import from_python
from mathics.core.convert.sympy import from_sympy
from mathics.core.expression import Expression
from mathics.core.number import dps, min_prec
from mathics.core.symbols import Symbol, SymbolSequence
from mathics.core.systemsymbols import SymbolAutomatic, SymbolGamma
from mathics.eval.arithmetic import call_mpmath
from mathics.eval.nevaluator import eval_N
from mathics.eval.numerify import numerify


class Beta(_MPMathMultiFunction):
    """
    <url>
    :Euler beta function:
    https://en.wikipedia.org/wiki/Beta_function</url> (<url>:SymPy:
    https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.beta_functions.beta</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Beta.html</url>)

    <dl>
      <dt>'Beta[$a$, $b$]'
      <dd>is the Euler's Beta function.
      <dt>'Beta[$z$, $a$, $b$]'
      <dd>gives the incomplete Beta function.
    </dl>
    The Beta function satisfies the property
    Beta[x, y] = Integrate[t^(x-1)(1-t)^(y-1),{t,0,1}] = Gamma[a] Gamma[b] / Gamma[a + b]
    >> Beta[2, 3]
     = 1 / 12
    >> 12* Beta[1., 2, 3]
     = 1.
    """

    summary_text = "Euler's Beta function"
    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    mpmath_names = {
        2: "beta",  # two arguments
        3: "betainc",  # three arguments
        4: "betainc",  # three arguments
    }
    sympy_names = {
        2: "beta",  # two arguments
        # sympy still does not implement beta incomplete.
    }
    rules = {
        "Derivative[1, 0, 0][Beta]": "(#1^(#2-1) * (1-#1)^(#3-1) )&",
    }

    def get_sympy_names(self):
        return ["beta", "betainc"]

    def from_sympy(self, sympy_name, elements):
        if sympy_name == "betainc":
            # lowergamma(z, x) -> Gamma[z, 0, x]
            z, a, b = elements
            return Expression(Symbol(self.get_name()), z, a, b)
        else:
            return Expression(Symbol(self.get_name()), *elements)

    # SymPy does not handles Beta for integer arguments.
    def eval(self, a, b, evaluation):
        """Beta[a_, b_]"""
        if not (a.is_numeric() and b.is_numeric()):
            return
        gamma_a = Expression(SymbolGamma, a)
        gamma_b = Expression(SymbolGamma, b)
        gamma_a_plus_b = Expression(SymbolGamma, a + b)
        return gamma_a * gamma_b / gamma_a_plus_b

    def eval_with_z(self, z, a, b, evaluation):
        """Beta[z_, a_, b_]"""
        # Here I needed to do that because the order of the arguments in WL
        # is different from the order in mpmath. Most of the code is the same
        # thatn in
        if not all(isinstance(q, Number) for q in (a, b, z)):
            return

        args = numerify(
            Expression(SymbolSequence, a, b, Integer0, z), evaluation
        ).get_sequence()
        mpmath_function = self.get_mpmath_function(tuple(args))
        if any(arg.is_machine_precision() for arg in args):
            # if any argument has machine precision then the entire calculation
            # is done with machine precision.
            float_args = [
                arg.round().get_float_value(permit_complex=True) for arg in args
            ]
            if None in float_args:
                return

            result = call_mpmath(mpmath_function, tuple(float_args))
        else:
            prec = min_prec(*args)
            d = dps(prec)
            args = [eval_N(arg, evaluation, Integer(d)) for arg in args]
            with mpmath.workprec(prec):
                mpmath_args = [x.to_mpmath() for x in args]
                if None in mpmath_args:
                    return
                result = call_mpmath(mpmath_function, tuple(mpmath_args), prec)
        return result


class Factorial(PostfixOperator, _MPMathFunction):
    """
    <url>:Factorial:
    https://en.wikipedia.org/wiki/Factorial</url> (<url>
    :SymPy:https://docs.sympy.org/latest/modules/functions/combinatorial.html#factorial</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/gamma.html#mpmath.factorial</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Factorial.html</url>)

    <dl>
      <dt>'Factorial[$n$]'
      <dt>'$n$!'
      <dd>computes the factorial of $n$.
    </dl>

    >> 20!
     = 2432902008176640000

    'Factorial' handles numeric (real and complex) values using the gamma function:
    >> 10.5!
     = 1.18994×10^7
    >> (-3.0+1.5*I)!
     = 0.0427943 - 0.00461565 I

    However, the value at poles is 'ComplexInfinity':
    >> (-1.)!
     = ComplexInfinity

    'Factorial' has the same operator ('!') as 'Not', but with higher precedence:
    >> !a! //FullForm
     = Not[Factorial[a]]

    #> 0!
     = 1
    """

    attributes = A_NUMERIC_FUNCTION | A_PROTECTED

    mpmath_name = "factorial"
    operator = "!"
    precedence = 610
    summary_text = "factorial"


class Factorial2(PostfixOperator, _MPMathFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Factorial2.html</url>

    <dl>
      <dt>'Factorial2[$n$]'
      <dt>'$n$!!'
      <dd>computes the double factorial of $n$.
    </dl>
    The double factorial or semifactorial of a number $n$, is the product of all the integers from 1 up to n that have the same parity (odd or even) as $n$.

    >> 5!!
     = 15.

    >> Factorial2[-3]
     = -1.

    'Factorial2' accepts Integers, Rationals, Reals, or Complex Numbers:
    >> I!! + 1
     = 3.71713 + 0.279527 I

    Irrationals can be handled by using numeric approximation:
    >> N[Pi!!, 6]
     = 3.35237
    """

    attributes = A_NUMERIC_FUNCTION | A_PROTECTED
    operator = "!!"
    precedence = 610
    mpmath_name = "fac2"
    sympy_name = "factorial2"
    messages = {
        "ndf": "`1` evaluation error: `2`.",
        "unknownp": "'`1`' not in ('Automatic', 'sympy', 'mpmath')",
    }
    summary_text = "semi-factorial"
    options = {"Method": "Automatic"}

    def eval(self, number, evaluation, options={}):
        "Factorial2[number_?NumberQ, OptionsPattern[%(name)s]]"

        try:
            import scipy.special as sp
            from numpy import pi

            # From https://stackoverflow.com/a/36779406/546218
            def fact2_generic(x):
                n = (x + 1.0) / 2.0
                return 2.0**n * sp.gamma(n + 0.5) / (pi ** (0.5))

        except ImportError:
            fact2_generic = None

        pref_expr = self.get_option(options, "Method", evaluation)
        is_automatic = False
        if pref_expr is SymbolAutomatic:
            is_automatic = True
            preference = "mpmath"
        else:
            preference = pref_expr.get_string_value()

        if preference in ("mpmath", "Automatic"):
            number_arg = number.to_mpmath()
            convert_from_fn = from_mpmath
            fact2_fn = getattr(mpmath, self.mpmath_name)
        elif preference == "sympy":
            number_arg = number.to_sympy()
            convert_from_fn = from_sympy
            fact2_fn = getattr(sympy, self.sympy_name)
        else:
            evaluation.message("Factorial2", "unknownp", preference)
            return

        try:
            result = fact2_fn(number_arg)
        except:  # noqa
            number_arg = number.to_python()
            # Maybe an even negative number? Try generic routine
            if is_automatic and fact2_generic:
                return from_python(fact2_generic(number_arg))
            evaluation.message("Factorial2", "ndf", preference, str(sys.exc_info()[1]))
            return
        return convert_from_fn(result)


class Gamma(_MPMathMultiFunction):
    """
    <url>:Gamma function:
    https://en.wikipedia.org/wiki/Gamma_function</url> (<url>
    :SymPy:https://docs.sympy.org/latest/modules/functions/special.html#module-sympy.functions.special.gamma_functions</url>, <url>
    :mpmath:
    https://mpmath.org/doc/current/functions/gamma.html#gamma</url>, <url>
    :WMA:https://reference.wolfram.com/language/ref/Gamma.html</url>)

    The gamma function is one commonly used extension of the factorial function \
    applied to complex numbers, and is defined for all complex numbers except \
    the non-positive integers.

    <dl>
      <dt>'Gamma[$z$]'
      <dd>is the gamma function on the complex number $z$.

      <dt>'Gamma[$z$, $x$]'
      <dd>is the upper incomplete gamma function.

      <dt>'Gamma[$z$, $x0$, $x1$]'
      <dd>is equivalent to 'Gamma[$z$, $x0$] - Gamma[$z$, $x1$]'.
    </dl>

    'Gamma[$z$]' is equivalent to '($z$ - 1)!':
    >> Simplify[Gamma[z] - (z - 1)!]
     = 0

    Exact arguments:
    >> Gamma[8]
     = 5040
    >> Gamma[1/2]
     = Sqrt[Pi]
    >> Gamma[1, x]
     = E ^ (-x)
    >> Gamma[0, x]
     = ExpIntegralE[1, x]

    Numeric arguments:
    >> Gamma[123.78]
     = 4.21078×10^204
    >> Gamma[1. + I]
     = 0.498016 - 0.15495 I

    Both 'Gamma' and 'Factorial' functions are continuous:
    >> Plot[{Gamma[x], x!}, {x, 0, 4}]
     = -Graphics-

    ## Issue 203
    #> N[Gamma[24/10], 100]
     = 1.242169344504305404913070252268300492431517240992022966055507541481863694148882652446155342679460339
    #> N[N[Gamma[24/10],100]/N[Gamma[14/10],100],100]
     = 1.400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
    #> % // Precision
     = 100.

    #> Gamma[1.*^20]
     : Overflow occurred in computation.
     = Overflow[]

    ## Needs mpmath support for lowergamma
    #> Gamma[1., 2.]
     = Gamma[1., 2.]
    """

    mpmath_names = {
        1: "gamma",  # one argument
    }
    sympy_names = {
        1: "gamma",  # one argument
        2: "uppergamma",
    }
    summary_text = "complete and incomplete gamma functions"

    rules = {
        "Gamma[z_, x0_, x1_]": "Gamma[z, x0] - Gamma[z, x1]",
        "Gamma[1 + z_]": "z!",
        "Gamma[Undefined]": "Undefined",
        "Gamma[x_, Undefined]": "Undefined",
        "Gamma[Undefined, y_]": "Undefined",
        "Derivative[1][Gamma]": "(Gamma[#1]*PolyGamma[0, #1])&",
        "Derivative[1, 0][Gamma]": "(Gamma[#1, #2]*Log[#2] + MeijerG[{{}, {1, 1}}, {{0, 0, #1}, {}}, #2])&",
        "Derivative[0, 1][Gamma]": "(-(#2^(-1 + #1)/E^#2))&",
    }

    def get_sympy_names(self):
        return ["gamma", "uppergamma", "lowergamma"]

    def from_sympy(self, sympy_name, elements):
        if sympy_name == "lowergamma":
            # lowergamma(z, x) -> Gamma[z, 0, x]
            z, x = elements
            return Expression(Symbol(self.get_name()), z, Integer0, x)
        else:
            return Expression(Symbol(self.get_name()), *elements)


class LogGamma(_MPMathMultiFunction):
    """
    <url>:log-gamma function:
    https://en.wikipedia.org/wiki/Gamma_function#The_log-gamma_function</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.gamma_functions.loggamma</url>, <url>
    :WMA:https://reference.wolfram.com/language/ref/LogGamma.html</url>)
    <dl>
      <dt>'LogGamma[$z$]'
      <dd>is the logarithm of the gamma function on the complex number $z$.
    </dl>

    >> LogGamma[3]
     = Log[2]

    LogGamma[z] has different analytical structure than Log[Gamma[z]]
    >> LogGamma[-2.+3 I]
     = -6.77652 - 4.56879 I
    >> Log[Gamma[-2.+3 I]]
     = -6.77652 + 1.71439 I
    LogGamma also can be evaluated for large arguments, for which Gamma produces Overflow:
    >>  LogGamma[1.*^20]
     = 4.50517×10^21
    >>  Log[Gamma[1.*^20]]
     : Overflow occurred in computation.
     = Overflow[]

    """

    summary_text = "logarithm of the gamma function"

    mpmath_names = {
        1: "loggamma",  # one argument
    }
    sympy_names = {
        1: "loggamma",  # one argument
    }
    rules = {
        "LogGamma[i_Integer]": "Log[Gamma[i]]",
        "Derivative[1][LogGamma]": "(PolyGamma[0, #1])&",
    }

    def get_sympy_names(self):
        return ["loggamma"]


class Pochhammer(SympyFunction):
    """
    <url>:Rising factorial:
    https://en.wikipedia.org/wiki/Falling_and_rising_factorials</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/combinatorial.html#risingfactorial</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Pochhammer.html</url>)

    The Pochhammer symbol or rising factorial often appears in series \
    expansions for hypergeometric functions.

    The Pochammer symbol has a definite value even when the gamma \
    functions which appear in its definition are infinite.
    <dl>
      <dt>'Pochhammer[$a$, $n$]'
      <dd>is the Pochhammer symbol $a_n$.
    </dl>

    Product of the first 3 numbers:
    >> Pochhammer[1, 3]
     = 6

    'Pochhammer[1, $n$]' is \
    the same as Pochhammer[2, $n$-1] since 1 is a multiplicative identity.

    >> Pochhammer[1, 3] == Pochhammer[2, 2]
     = True

    Although sometimes 'Pochhammer[0, $n$]' is taken to be 1, in Mathics it is 0:
    >> Pochhammer[0, n]
     = 0

    Pochhammer uses Gamma for non-Integer values of $n$:

    >> Pochhammer[1, 3.001]
     = 6.00754

    >> Pochhammer[1, 3.001] == Pochhammer[2, 2.001]
     = True

    >> Pochhammer[1.001, 3] == 1.001 2.001 3.001
      = True
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    rules = {
        "Pochhammer[0, n_]": "0",  # Wikipedia says it should be 1 though.
        "Pochhammer[a_, n_]": "Gamma[a + n] / Gamma[a]",
        "Derivative[1,0][Pochhammer]": "(Pochhammer[#1, #2]*(-PolyGamma[0, #1] + PolyGamma[0, #1 + #2]))&",
        "Derivative[0,1][Pochhammer]": "(Pochhammer[#1, #2]*PolyGamma[0, #1 + #2])&",
    }
    summary_text = "Pochhammer's symbols"
    sympy_name = "RisingFactorial"


class PolyGamma(_MPMathMultiFunction):
    r"""
    <url>:Polygamma function:
    https://en.wikipedia.org/wiki/Polygamma_function</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.gamma_functions.polygamma</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/PolyGamma.html</url>)

    PolyGamma is a meromorphic function on the complex numbers and is defined as a derivative of the logarithm of the gamma function.
    <dl>
      <dt>PolyGamma[z]
      <dd>returns the digamma function.

      <dt>PolyGamma[n,z]
      <dd>gives the n^(th) derivative of the digamma function.
    </dl>

    >> PolyGamma[5]
     = 25 / 12 - EulerGamma

    >> PolyGamma[3, 5]
     = -22369 / 3456 + Pi ^ 4 / 15
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    mpmath_names = {
        1: "digamma",  # 1 argument
        2: "psi",
    }

    rules = {
        "PolyGamma[Undefined]": "Undefined",
        "PolyGamma[Undefined, x_]": "Undefined",
        "PolyGamma[y_, Undefined]": "Undefined",
    }

    summary_text = "polygamma function"
    sympy_names = {1: "digamma", 2: "polygamma"}  # 1 argument


class StieltjesGamma(SympyFunction):
    """
    <url>:Stieltjes constants:
    https://en.wikipedia.org/wiki/Stieltjes_constants</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/functions/special.html#sympy.functions.special.zeta_functions.stieltjes</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/StieltjesGamma.html</url>)

    <dl>
      <dt>'StieltjesGamma[$n$]'
      <dd>returns the Stieltjes constant for $n$.

      <dt>'StieltjesGamma[$n$, $a$]'
      <dd>gives the generalized Stieltjes constant of its parameters
    </dl>

    ## Todo...
    ## >> N[StieltjesGamma[1], 50]
    ##  = ...
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    rules = {
        "StieltjesGamma[Undefined]": "Undefined",
        "StieltjesGamma[Undefined, x_]": "Undefined",
        "StieltjesGamma[y_, Undefined]": "Undefined",
    }

    summary_text = "Stieltjes' function"
    sympy_name = "stieltjes"
