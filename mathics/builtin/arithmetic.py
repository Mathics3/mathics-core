# -*- coding: utf-8 -*-

"""
Mathematical Functions

Basic arithmetic functions, including complex number arithmetic.
"""

from typing import Optional

import sympy

from mathics.builtin.numeric import Abs
from mathics.builtin.scoping import dynamic_scoping
from mathics.core.atoms import (
    MATHICS3_COMPLEX_I,
    MATHICS3_COMPLEX_I_NEG,
    Complex,
    Integer,
    Integer0,
    Integer1,
    IntegerM1,
    Rational,
    Real,
    String,
)
from mathics.core.attributes import (
    A_HOLD_REST,
    A_LISTABLE,
    A_NO_ATTRIBUTES,
    A_NUMERIC_FUNCTION,
    A_PROTECTED,
)
from mathics.core.builtin import (
    Builtin,
    IterationFunction,
    MPMathFunction,
    Predefined,
    PrefixOperator,
    SympyFunction,
    SympyObject,
    Test,
)
from mathics.core.convert.sympy import SympyExpression, from_sympy
from mathics.core.element import BaseElement, ElementsProperties
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.expression_predefined import (
    MATHICS3_COMPLEX_INFINITY,
    MATHICS3_I_INFINITY,
    MATHICS3_I_NEG_INFINITY,
    MATHICS3_INFINITY,
    MATHICS3_NEG_INFINITY,
    PredefinedExpression,
)
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolFalse,
    SymbolList,
    SymbolPlus,
    SymbolTimes,
    SymbolTrue,
    sympy_name,
)
from mathics.core.systemsymbols import (
    SymbolAnd,
    SymbolDirectedInfinity,
    SymbolInfix,
    SymbolPossibleZeroQ,
    SymbolTable,
    SymbolUndefined,
)
from mathics.eval.inference import get_assumptions_list
from mathics.eval.nevaluator import eval_N
from mathics.eval.numeric import eval_Sign

# This tells documentation how to sort this module
sort_order = "mathics.builtin.mathematical-functions"


map_direction_infinity = {
    Integer1: MATHICS3_INFINITY,
    IntegerM1: MATHICS3_NEG_INFINITY,
    MATHICS3_COMPLEX_I: MATHICS3_I_INFINITY,
    MATHICS3_COMPLEX_I_NEG: MATHICS3_I_NEG_INFINITY,
}


def create_infix(items, operator, prec, grouping):
    if len(items) == 1:
        return items[0]
    else:
        return Expression(
            SymbolInfix,
            ListExpression(*items),
            String(operator),
            Integer(prec),
            Symbol(grouping),
        )


class Arg(MPMathFunction):
    """
    <url>:Argument (complex analysis):
    https://en.wikipedia.org/wiki/Argument_(complex_analysis)</url> (<url>
    :WMA link:https://reference.wolfram.com/language/ref/Arg.html</url>)

    <dl>
      <dt>'Arg'[$z$, 'Method ->' "$option$"]
      <dd>returns the argument of a complex value $z$.
    </dl>

    <ul>
         <li>'Arg'[$z$] is left unevaluated if $z$ is not a numeric quantity.
         <li>'Arg'[$z$] gives the phase angle of $z$ in radians.
         <li>The result from 'Arg'[$z$] is always between -Pi and +Pi.
         <li>'Arg'[$z$] has a branch cut discontinuity in the complex $z$ plane running \
             from -Infinity to 0.
         <li>'Arg'[0] is 0.
    </ul>

     >> Arg[-3]
      = Pi

     Same as above, but using SymPy's method:
     >> Arg[-3, Method->"sympy"]
      = Pi

    >> Arg[1-I]
     = -Pi / 4

    'Arg' evaluates the direction of 'DirectedInfinity' quantities by \
    the 'Arg' of its arguments:
    >> Arg[DirectedInfinity[1+I]]
     = Pi / 4
    >> Arg[DirectedInfinity[]]
     = 1
    Arg for 0 is assumed to be 0:
    >> Arg[0]
     = 0
    """

    summary_text = "phase of a complex number"
    rules = {
        "Arg[0]": "0",
        "Arg[DirectedInfinity[]]": "1",
        "Arg[DirectedInfinity[a_]]": "Arg[a]",
    }

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    options = {"Method": "Automatic"}

    numpy_name = "angle"  # for later
    mpmath_name = "arg"
    sympy_name = "arg"

    def eval(self, z, evaluation, options={}):
        "Arg[z_, OptionsPattern[Arg]]"
        if Expression(SymbolPossibleZeroQ, z).evaluate(evaluation) is SymbolTrue:
            return Integer0
        preference = self.get_option(options, "Method", evaluation).get_string_value()
        if preference is None or preference == "Automatic":
            return super(Arg, self).eval(z, evaluation)
        elif preference == "mpmath":
            return MPMathFunction.eval(self, z, evaluation)
        elif preference == "sympy":
            return SympyFunction.eval(self, z, evaluation)
        # TODO: add NumpyFunction
        evaluation.message(
            "meth", f'Arg Method {preference} not in ("sympy", "mpmath")'
        )
        return


class Assuming(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Assuming.html</url>

    <dl>
      <dt>'Assuming'[$cond$, $expr$]
      <dd>Evaluates $expr$ assuming the conditions $cond$.
    </dl>

    >> $Assumptions = { x > 0 }
     = {x > 0}
    >> Assuming[y>0, ConditionalExpression[y x^2, y>0]//Simplify]
     = x ^ 2 y
    >> Assuming[Not[y>0], ConditionalExpression[y x^2, y>0]//Simplify]
     = Undefined
    >> ConditionalExpression[y x ^ 2, y > 0]//Simplify
     = ConditionalExpression[x ^ 2 y, y > 0]
    """

    summary_text = "set assumptions during the evaluation"
    attributes = A_HOLD_REST | A_PROTECTED

    def eval_assuming(self, assumptions, expr, evaluation: Evaluation):
        "Assuming[assumptions_, expr_]"
        assumptions = assumptions.evaluate(evaluation)
        if assumptions is SymbolTrue:
            cond = []
        elif isinstance(assumptions, Symbol) or not assumptions.has_form("List", None):
            cond = [assumptions]
        else:
            cond = assumptions.elements
        cond = tuple(cond) + get_assumptions_list(evaluation)
        list_cond = ListExpression(*cond)
        # TODO: reduce the list of predicates
        return dynamic_scoping(
            lambda ev: expr.evaluate(ev), {"System`$Assumptions": list_cond}, evaluation
        )


class Assumptions(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/\$Assumptions.html</url>
    <dl>
      <dt>'\$Assumptions'
      <dd>is the default setting for the 'Assumptions' option used in such functions as 'Simplify', 'Refine', and 'Integrate'.
    </dl>
    """

    summary_text = "assumptions used to simplify expressions"
    name = "$Assumptions"
    attributes = A_NO_ATTRIBUTES
    rules = {
        "$Assumptions": "True",
    }

    messages = {
        "faas": "Assumptions should not be False.",
        "baas": "Bad formed assumption.",
    }


class Boole(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Boole.html</url>

    <dl>
      <dt>'Boole[expr]'
      <dd>returns 1 if expr is True and 0 if expr is False.
    </dl>

    >> Boole[2 == 2]
     = 1
    >> Boole[7 < 5]
     = 0
    >> Boole[a == 7]
     = Boole[a == 7]
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "translate 'True' to 1, and 'False' to 0"

    def eval(self, expr, evaluation: Evaluation):
        "Boole[expr_]"
        if expr is SymbolTrue:
            return Integer1
        elif expr is SymbolFalse:
            return Integer0
        return None


class Complex_(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Complex.html</url>

    <dl>
      <dt>'Complex'
      <dd>is the head of complex numbers.

      <dt>'Complex'[$a$, $b$]
      <dd>constructs the complex number '$a$ + I $b$'.
    </dl>

    >> Head[2 + 3*I]
     = Complex
    >> Complex[1, 2/3]
     = 1 + 2 I / 3
    >> Abs[Complex[3, 4]]
     = 5
    """

    summary_text = "head for complex numbers"
    name = "Complex"

    def eval(self, r, i, evaluation: Evaluation):
        "Complex[r_?NumberQ, i_?NumberQ]"

        if isinstance(r, Complex) or isinstance(i, Complex):
            sym_form = r.to_sympy() + sympy.I * i.to_sympy()
            r, i = sym_form.simplify().as_real_imag()
            r, i = from_sympy(r), from_sympy(i)
        return Complex(r, i)


class ConditionalExpression(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/
language/ref/ConditionalExpression.html</url>

    <dl>
      <dt>'ConditionalExpression'[$expr$, $cond$]
      <dd>returns $expr$ if $cond$ evaluates to $True$, $Undefined$ if $cond$ \
          evaluates to $False$.
    </dl>

    >> ConditionalExpression[x^2, True]
     = x ^ 2

     >> ConditionalExpression[x^2, False]
     = Undefined

    >> f = ConditionalExpression[x^2, x>0]
     = ConditionalExpression[x ^ 2, x > 0]
    >> f /. x -> 2
     = 4
    >> f /. x -> -2
     = Undefined
    'ConditionalExpression' uses assumptions to evaluate the condition:
    >> $Assumptions = x > 0;
    >> ConditionalExpression[x ^ 2, x>0]//Simplify
     = x ^ 2
    >> $Assumptions = True;
    # >> ConditionalExpression[ConditionalExpression[s,x>a], x<b]
    # = ConditionalExpression[s, And[x>a, x<b]]
    """

    summary_text = "expression defined under condition"
    sympy_name = "Piecewise"

    rules = {
        "ConditionalExpression[expr_, True]": "expr",
        "ConditionalExpression[expr_, False]": "Undefined",
        "ConditionalExpression[ConditionalExpression[expr_, cond1_], cond2_]": "ConditionalExpression[expr, And@@Flatten[{cond1, cond2}]]",
        "ConditionalExpression[expr1_, cond_] + expr2_": "ConditionalExpression[expr1+expr2, cond]",
        "ConditionalExpression[expr1_, cond_]  expr2_": "ConditionalExpression[expr1 expr2, cond]",
        "ConditionalExpression[expr1_, cond_]^expr2_": "ConditionalExpression[expr1^expr2, cond]",
        "expr1_ ^ ConditionalExpression[expr2_, cond_]": "ConditionalExpression[expr1^expr2, cond]",
    }

    def eval_generic(self, expr, cond, evaluation: Evaluation):
        "ConditionalExpression[expr_, cond_]"
        # What we need here is a way to evaluate
        # cond as a predicate, using assumptions.
        # Let's delegate this to the And (and Or) symbols...
        if not isinstance(cond, Atom) and cond._head is SymbolList:
            cond = Expression(SymbolAnd, *(cond.elements))
        else:
            cond = Expression(SymbolAnd, cond)
        if cond is None:
            return
        if cond is SymbolTrue:
            return expr
        if cond is SymbolFalse:
            return SymbolUndefined
        return

    def to_sympy(self, expr, **kwargs):
        elements = expr.elements
        if len(elements) != 2:
            return
        expr, cond = elements

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

        sympy_cases = (
            (expr.to_sympy(**kwargs), sympy_cond),
            (sympy.Symbol(sympy_name(SymbolUndefined)), True),
        )
        return sympy.Piecewise(*sympy_cases)


class Conjugate(MPMathFunction):
    """
    <url>:Complex Conjugate:
    https://en.wikipedia.org/wiki/Complex_conjugate</url> \
    <url>:WMA link:https://reference.wolfram.com/language/ref/Conjugate.html</url>

    <dl>
      <dt>'Conjugate'[$z$]
      <dd>returns the complex conjugate of the complex number $z$.
    </dl>

    >> Conjugate[3 + 4 I]
     = 3 - 4 I

    >> Conjugate[3]
     = 3

    >> Conjugate[a + b * I]
     = Conjugate[a] - I Conjugate[b]

    >> Conjugate[{{1, 2 + I 4, a + I b}, {I}}]
     = {{1, 2 - 4 I, Conjugate[a] - I Conjugate[b]}, {-I}}

    >> Conjugate[1.5 + 2.5 I]
     = 1.5 - 2.5 I
    """

    mpmath_name = "conj"
    rules = {
        "Conjugate[Undefined]": "Undefined",
    }
    summary_text = "compute complex conjugation"


class DirectedInfinity(SympyFunction):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/DirectedInfinity.html</url>

    <dl>
      <dt>'DirectedInfinity'[$z$]
      <dd>represents an infinite multiple of the complex number $z$.
      <dt>'DirectedInfinity[]'
      <dd>is the same as 'ComplexInfinity'.
    </dl>

    >> DirectedInfinity[1]
     = Infinity
    >> DirectedInfinity[]
     = ComplexInfinity
    >> DirectedInfinity[1 + I]
     = (1 / 2 + I / 2) Sqrt[2] Infinity

    >> 1 / DirectedInfinity[1 + I]
     = 0
    >> DirectedInfinity[1] + DirectedInfinity[-1]
     : Indeterminate expression -Infinity + Infinity encountered.
     = Indeterminate

    >> DirectedInfinity[0]
     = ComplexInfinity

    """

    summary_text = "infinite quantity with a defined direction in the complex plane"
    rules = {
        "DirectedInfinity[args___] ^ -1": "0",
        # Special arguments:
        "DirectedInfinity[DirectedInfinity[args___]]": "DirectedInfinity[args]",
        "DirectedInfinity[Indeterminate]": "Indeterminate",
        "DirectedInfinity[Alternatives[0, 0.]]": "DirectedInfinity[]",
        # Plus
        "DirectedInfinity[a_] + DirectedInfinity[b_] /; b == -a": (
            "Message[Infinity::indet,"
            "  Unevaluated[DirectedInfinity[a] + DirectedInfinity[b]]];"
            "Indeterminate"
        ),
        "DirectedInfinity[] + DirectedInfinity[args___]": (
            "Message[Infinity::indet,"
            "  Unevaluated[DirectedInfinity[] + DirectedInfinity[args]]];"
            "Indeterminate"
        ),
        "DirectedInfinity[args___] + _?NumberQ": "DirectedInfinity[args]",
        # Times. See if can be reinstalled in eval_Times
        "Alternatives[0, 0.] DirectedInfinity[z___]": (
            "Message[Infinity::indet,"
            "  Unevaluated[0 DirectedInfinity[z]]];"
            "Indeterminate"
        ),
        "a_?NumericQ * DirectedInfinity[b_]": "DirectedInfinity[a * b]",
        "a_ DirectedInfinity[]": "DirectedInfinity[]",
        "DirectedInfinity[a_] * DirectedInfinity[b_]": "DirectedInfinity[a * b]",
    }

    formats = {
        "DirectedInfinity[1]": "HoldForm[Infinity]",
        "DirectedInfinity[-1]": "HoldForm[-Infinity]",
        "DirectedInfinity[]": "HoldForm[ComplexInfinity]",
        "DirectedInfinity[DirectedInfinity[z_]]": "DirectedInfinity[z]",
        "DirectedInfinity[z_?NumericQ]": "HoldForm[z Infinity]",
    }

    def eval_complex_infinity(self, evaluation: Evaluation):
        """DirectedInfinity[]"""
        return MATHICS3_COMPLEX_INFINITY

    def eval_directed_infinity(self, direction, evaluation: Evaluation):
        """DirectedInfinity[direction_]"""
        result = map_direction_infinity.get(direction, None)
        if result:
            return result

        if direction.is_zero:
            return MATHICS3_COMPLEX_INFINITY

        normalized_direction = eval_Sign(direction)
        # TODO: improve eval_Sign, to avoid the need of the
        # following block:
        #   ############################################
        if normalized_direction is None:
            ndir = eval_N(direction, evaluation)
            if isinstance(ndir, (Integer, Rational, Real)):
                if abs(ndir.value) == 1.0:
                    normalized_direction = direction
                else:
                    normalized_direction = direction / Abs(direction)
            elif isinstance(ndir, Complex):
                re, im = ndir.real, ndir.imag
                if abs(re.value**2 + im.value**2 - 1.0) < 1.0e-9:
                    normalized_direction = direction
                else:
                    normalized_direction = direction / Abs(direction)
            else:
                return None
        #  ##############################################

        if normalized_direction is None:
            return None
        return PredefinedExpression(
            SymbolDirectedInfinity,
            normalized_direction.evaluate(evaluation),
        )

    def to_sympy(self, expr, **kwargs):
        if len(expr.elements) == 1:
            dir = expr.elements[0].value
            if dir == 1:
                return sympy.oo
            elif dir == -1:
                return -sympy.oo
            else:
                return sympy.Mul((expr.elements[0].to_sympy()), sympy.zoo)
        else:
            return sympy.zoo


class Element(Builtin):
    """
    <url>:Element of:https://en.wikipedia.org/wiki/Element_(mathematics)</url> \
    <url>:WMA link:https://reference.wolfram.com/language/ref/Element.html</url>

    <dl>
      <dt>'Element'[$expr$, $domain$]
      <dd>returns $True$ if $expr$ is an element of $domain$
      <dt>'Element'[$expr_1$|$expr_2$|..., $domain$]
      <dd>returns $True$ if all the $expr_i$ belongs to $domain$, and \
    $False$ if one of the items doesn't.
    </dl>


    Check if $3$ and $a$ are both integers. If $a$ is not defined, then \
'Element' reduces the condition:
    >> Element[3 | a, Integers]
     = Element[a, Integers]

    Notice that standard domain names ('Primes', 'Integers', 'Rationals', \
'Algebraics', 'Reals', 'Complexes', and 'Booleans')\
    are in plural form. If a singular form is used, a warning is shown:

    >> Element[a, Real]
     : The second argument Real of Element should be one of: Primes, Integers, \
Rationals, Algebraics, Reals, Complexes, or Booleans.
     = Element[a, Real]

    """

    messages = {
        "bset": (
            "The second argument `1` of Element should be one of: "
            "Primes, Integers, Rationals, Algebraics, "
            "Reals, Complexes, or Booleans."
        ),
    }

    summary_text = "check whether belongs the domain"

    def eval_wrong_domain(
        self, elem: BaseElement, domain: BaseElement, evaluation: Evaluation
    ):
        (
            "Element[elem_, domain:(Alternatives["
            "Algebraic, Bool, Integer, Prime, Rational, Real, Complex])]"
        )
        evaluation.message("Element", "bset", domain)
        return None

    def eval_Element_alternatives(
        self, elems: BaseElement, domain: BaseElement, evaluation: Evaluation
    ) -> Optional[Expression]:
        """Element[elems_Alternatives, domain_]"""
        items = elems.elements
        unknown = []
        for item in items:
            item_belongs = Element(item, domain).evaluate(evaluation)
            if item_belongs is SymbolTrue:
                continue
            if item_belongs is SymbolFalse:
                return SymbolFalse
            unknown.append(item)
        if len(unknown) == len(items):
            return None
        if len(unknown) == 0:
            return SymbolTrue
        # If some of the items remain unknown, return a reduced expression
        return Element(Expression(elems.head, *unknown), domain)


class I_(Predefined, SympyObject):
    """
    <url>:Imaginary unit:https://en.wikipedia.org/wiki/Imaginary_unit</url> \
    (<url>:WMA:https://reference.wolfram.com/language/ref/I.html</url>)

    <dl>
      <dt>'I'
      <dd>represents the imaginary number 'Sqrt[-1]'.
    </dl>

    >> I^2
     = -1
    >> (3+I)*(3-I)
     = 10
    """

    name = "I"
    sympy_name = "I"
    sympy_obj = sympy.I
    summary_text = "imaginary unit number Sqrt[-1]"
    python_equivalent = 1j

    def evaluate(self, evaluation: Evaluation):
        return Complex(Integer0, Integer1)

    def is_constant(self) -> bool:
        """The value and evaluation of this object can never change."""
        return True

    @property
    def is_literal(self):
        return True

    @property
    def value(self) -> complex:
        return complex(0, 1)

    def to_sympy(self, expr, **kwargs):
        return self.sympy_obj


class Im(SympyFunction):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Im.html</url>

    <dl>
      <dt>'Im'[$z$]
      <dd>returns the imaginary component of the complex number $z$.
    </dl>

    >> Im[3+4I]
     = 4

    >> Plot[{Sin[a], Im[E^(I a)]}, {a, 0, 2 Pi}]
     = -Graphics-
    """

    summary_text = "imaginary part of a complex number"
    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED

    def eval_complex(self, number, evaluation: Evaluation):
        "Im[number_Complex]"
        if isinstance(number, Complex):
            return number.imag

    def eval_number(self, number, evaluation: Evaluation):
        "Im[number_?NumberQ]"

        return Integer0

    def eval(self, number, evaluation: Evaluation):
        "Im[number_]"

        return from_sympy(sympy.im(number.to_sympy().expand(complex=True)))


class Integer_(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Integer.html</url>

    <dl>
      <dt>'Integer'
      <dd>is the head of integers.
    </dl>

    >> Head[5]
     = Integer
    """

    summary_text = "head for integer numbers"
    name = "Integer"


class Product(IterationFunction, SympyFunction, PrefixOperator):
    """
    <url>:Direct product:https://en.wikipedia.org/wiki/Direct_product</url> (<url>
      :SymPy:https://docs.sympy.org/latest/modules/concrete.html#sympy.concrete.products.Product</url>, <url>
      :WMA:https://reference.wolfram.com/language/ref/Product.html</url>)

    <dl>
      <dt>'Product'[$f$, {$i$, $i_{min}$, $i_{max}$}]
      <dd>evaluates the discrete product of $f$ with $i$ ranging from $i_{min}$ to $i_{max}$.

      <dt>'Product'[$f$, {$i$, $i_{max}$}]
      <dd>same as 'Product'[$f$, {$i, 1, i_{max}$}].

      <dt>'Product'[$f$, {$i, i_{min}, i_{max}$, $di$}]
      <dd>$i$ ranges from $i_{min}$ to $i_{max}$ in steps of $di$.

      <dt>'Product'[$f$, {$i, i_{min}, i_{max}$}, {$j, j_{min}, j_{max}$}, ...]
      <dd>evaluates $f$ as a multiple product, with {$i$, ...}, {$j$, ...}, ... being in \
      outermost-to-innermost order.
    </dl>

    'Product[k, {k, i, n}]' is defined in terms of <url>
    :Factorial:
    /doc/reference-of-built-in-symbols/special-functions/gamma-and-related-functions/factorial/</url>:

    >> Product[k, {k, i, n}]
     = n! / (-1 + i)!

    When $i$ is 1, we get the factorial function:
    >> Product[k, {k, 1, n}]
     = n!

    Or more succinctly:
    >> Product[k, {k, n}]
     = n!

    Symbolic products involving the factorial are evaluated:
    >> Product[k, {k, 3, n}]
     = n! / 2

    Examples of numeric evaluation using more complex functions:
    >> Product[x^k, {k, 2, 20, 2}]
     = x ^ 110

    >> Product[2 ^ i, {i, 1, n}]
     = 2 ^ (n / 2 + n ^ 2 / 2)

    >> Product[f[i], {i, 1, 7}]
     = f[1] f[2] f[3] f[4] f[5] f[6] f[7]

    Evaluate the $n$-th <url>:Primorial:https://en.wikipedia.org/wiki/Primorial</url>:
    >> Primorial[0] = 1;
    >> Primorial[n_Integer] := Product[Prime[k], {k, 1, n}];
    >> Primorial[12]
     = 7420738134810

    """

    # FIXME Product[k, {k, 3, n}] is rewritten using Factorial via
    # Pochhammer rewrite rules. We want this for Product, but WMA
    # does not rewrite using Factorial for Pochhammer alone, although it could.
    # Nevertheless, if and when our Pochhammer is adjusted to remove
    # this transformation to Factorial to match WMA behavior,
    # we will need to add a rule that transforms to Factorial here.
    rules = IterationFunction.rules.copy()
    rules.update(
        {
            "MakeBoxes[Product[f_, {i_, a_, b_, 1}],"
            "  form:StandardForm|TraditionalForm]": (
                r'RowBox[{SubsuperscriptBox["\\[Product]",'
                r'  RowBox[{MakeBoxes[i, form], "=", MakeBoxes[a, form]}],'
                r"  MakeBoxes[b, form]], MakeBoxes[f, form]}]"
            ),
        }
    )
    summary_text = "compute the direct product"
    sympy_name = "Product"
    throw_iterb = False

    def get_result(self, elements, is_uniform=False):
        return Expression(
            SymbolTimes,
            *elements,
            elements_properties=ElementsProperties(is_uniform=is_uniform),
        )

    def to_sympy(self, expr, **kwargs):
        if expr.has_form("Product", 2) and expr.elements[1].has_form("List", 3):
            index = expr.elements[1]
            try:
                e_kwargs = kwargs.copy()
                e_kwargs["convert_all_global_functions"] = True
                e_kwargs["dummies"] = e_kwargs.get("dummies", set()).union((index,))
                e = expr.elements[0].to_sympy(**e_kwargs)
                e_kwargs["convert_all_global_functions"] = kwargs.get(
                    "convert_all_global_functions", False
                )

                i = index.elements[0].to_sympy(**e_kwargs)
                start = index.elements[1].to_sympy(**kwargs)
                stop = index.elements[2].to_sympy(**kwargs)

                return sympy.product(e, (i, start, stop))
            except ZeroDivisionError:
                pass


class Rational_(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Rational.html</url>

    <dl>
      <dt>'Rational'
      <dd>is the head of rational numbers.
      <dt>'Rational'[$a$, $b$]
      <dd>constructs the rational number $a$ / $b$.
    </dl>

    >> Head[1/2]
     = Rational

    >> Rational[1, 2]
     = 1 / 2
    """

    summary_text = "head for rational numbers"
    name = "Rational"

    def eval(self, n: Integer, m: Integer, evaluation: Evaluation):
        "Rational[n_Integer, m_Integer]"

        if m.value == 1:
            return n
        else:
            return Rational(n.value, m.value)


class Re(SympyFunction):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Re.html</url>

    <dl>
      <dt>'Re'[$z$]
      <dd>returns the real component of the complex number $z$.
    </dl>

    >> Re[3+4I]
     = 3

    >> Plot[{Cos[a], Re[E^(I a)]}, {a, 0, 2 Pi}]
     = -Graphics-
    """

    summary_text = "real part of a complex number"
    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    sympy_name = "re"

    def eval(self, number, evaluation: Evaluation):
        "Re[number_]"
        return from_sympy(sympy.re(number.to_sympy().expand(complex=True)))

    def eval_complex(self, number, evaluation: Evaluation):
        "Re[number_Complex]"
        if isinstance(number, Complex):
            return number.real

    def eval_number(self, number, evaluation: Evaluation):
        "Re[number_?NumberQ]"

        return number


class Real_(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Real.html</url>

    <dl>
      <dt>'Real'
      <dd>is the head of real (inexact) numbers.
    </dl>

    >> x = 3. ^ -20;
    >> InputForm[x]
     = 2.8679719907924413*^-10
    >> Head[x]
     = Real

    """

    summary_text = "head for real numbers"
    name = "Real"


class RealValuedNumberQ(Test):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/RealValuedNumberQ.html</url>

    <dl>
      <dt>'RealValuedNumberQ'[$expr$]
      <dd>returns 'True' if $expr$ is an explicit number with no imaginary component.
    </dl>

    >> RealValuedNumberQ[10]
     = True
    >> RealValuedNumberQ[4.0]
     = True
    >> RealValuedNumberQ[1+I]
     = False
    >> RealValuedNumberQ[0 * I]
     = True
    >> RealValuedNumberQ[0.0 * I]
     = False

    "Underflow[]" and "Overflow[]" are considered Real valued numbers:
    >> {RealValuedNumberQ[Underflow[]], RealValuedNumberQ[Overflow[]]}
     = {True, True}
    """

    attributes = A_NO_ATTRIBUTES

    summary_text = "test whether an expression is a real number"

    def test(self, expr) -> bool:
        return (
            isinstance(expr, (Integer, Rational, Real))
            or expr.has_form("Underflow", 0)
            or expr.has_form("Overflow", 0)
        )


class Sum(IterationFunction, SympyFunction, PrefixOperator):
    r"""
    <url>:Summation:https://en.wikipedia.org/wiki/Summation</url> (<url>
    :SymPy:https://docs.sympy.org/latest/modules/concrete.html#sympy.concrete.summations.Sum</url>, <url>
    :WMA:https://reference.wolfram.com/language/ref/Sum.html</url>)

    <dl>
      <dt>'Sum['$f, \{i, i_{min}, i_{max}\}$']'
      <dd>evaluates the discrete sum of $f$ with $i$ ranging from $i_{min}$ to $i_{max}$.

      <dt>'Sum['$f, \{i, i_{max}\}$']'
      <dd>same as 'Sum['$f, \{i, 1, i_{max}\}$']'.

      <dt>'Sum['$f, \{i, i_{min}, i_{max}, di\}$']'
      <dd>$i$ ranges from $i_{min}$ to $i_{max}$ in steps of $di$.

      <dt>'Sum['$f, \{i, i_{min}, i_{max}, \{j, j_{min}, j_{max}, ...$']'
      <dd>evaluates $f$ as a multiple sum, with {$i, ...$}, {$j, ...$}, ... being \
          in outermost-to-innermost order.
    </dl>


    A sum that Gauss in elementary school was asked to do to kill time:
    >> Sum[k, {k, 1, 10}]
     = 55

    The symbolic form he used:
    >> Sum[k, {k, 1, n}]
     = n (1 + n) / 2

    A Geometric series with a finite limit:
    >> Sum[1 / 2 ^ i, {i, 1, k}]
     = 1 - 2 ^ (-k)

    A Geometric series using Infinity:
    >> Sum[1 / 2 ^ i, {i, 1, Infinity}]
     = 1

    Leibniz formula used in computing Pi:
    >> Sum[1 / ((-1)^k (2k + 1)), {k, 0, Infinity}]
     = Pi / 4

    A table of double sums to compute squares:
    >> Table[ Sum[i * j, {i, 0, n}, {j, 0, n}], {n, 0, 4} ]
     = {0, 1, 9, 36, 100}

    Computing Harmonic using a sum
    >> Sum[1 / k ^ 2, {k, 1, n}]
     = HarmonicNumber[n, 2]

    Other symbolic sums:
    >> Sum[k, {k, n, 2 n}]
     = 3 n (1 + n) / 2

    A sum with Complex-number iteration values
    >> Sum[k, {k, I, I + 1}]
     = 1 + 2 I

    >> Sum[k, {k, Range[5]}]
     = 15

    >> Sum[f[i], {i, 1, 7}]
     = f[1] + f[2] + f[3] + f[4] + f[5] + f[6] + f[7]

    Verify algebraic identities:
    >> Sum[x ^ 2, {x, 1, y}] - y * (y + 1) * (2 * y + 1) / 6
     = 0

    Non-integer bounds:
    >> Sum[i, {i, 1, 2.5}]
     = 3
    >> Sum[i, {i, 1.1, 2.5}]
     = 3.2
    >> Sum[k, {k, I, I + 1.5}]
     = 1 + 2 I
    """

    rules = IterationFunction.rules.copy()
    rules.update(
        {
            "MakeBoxes[Sum[f_, {i_, a_, b_, 1}],"
            "  form:StandardForm|TraditionalForm]": (
                r'RowBox[{SubsuperscriptBox["\\[Sum]",'
                r'  RowBox[{MakeBoxes[i, form], "=", MakeBoxes[a, form]}],'
                r"  MakeBoxes[b, form]], MakeBoxes[f, form]}]"
            ),
        }
    )

    summary_text = "compute a summation"
    sympy_name = "Sum"

    # Do not throw warning message for symbolic iteration bounds
    throw_iterb = False

    def get_result(self, elements, is_uniform=False) -> Expression:
        return Expression(
            SymbolPlus,
            *elements,
            elements_properties=ElementsProperties(is_uniform=is_uniform),
        )

    def to_sympy(self, expr, **kwargs) -> Optional[SympyExpression]:
        """
        Perform summation via sympy.summation
        """
        if expr.has_form("Sum", 2) and expr.elements[1].has_form("List", 3):
            index = expr.elements[1]
            arg_kwargs = kwargs.copy()
            arg_kwargs["convert_all_global_functions"] = True
            arg_kwargs["dummies"] = kwargs.get("dummies", set()).union((index,))
            f_sympy = expr.elements[0].to_sympy(**arg_kwargs)
            if f_sympy is None:
                return

            evaluation = kwargs.get("evaluation", None)

            # Handle summation parameters: variable, min, max

            arg_kwargs["convert_all_global_functions"] = kwargs.get(
                "convert_all_global_functions", False
            )
            var_min_max = index.elements[:3]
            bounds = [expr.to_sympy(**arg_kwargs) for expr in var_min_max]
            if evaluation:
                # Min and max might be Mathics expressions. If so, evaluate them.
                for i in (1, 2):
                    min_max_expr = var_min_max[i]
                    if not isinstance(expr, Symbol):
                        min_max_expr_eval = min_max_expr.evaluate(evaluation)
                        value = min_max_expr_eval.to_sympy(**arg_kwargs)
                        bounds[i] = value

            # FIXME: The below tests on SympyExpression, but really the
            # test should be broader.
            if isinstance(f_sympy, sympy.core.basic.Basic):
                # sympy.summation() won't be able to handle Mathics functions in
                # in its first argument, the function parameter.
                # For example in Sum[Identity[x], {x, 3}], sympy.summation can't
                # evaluate Identity[x].
                # In general we want to avoid using Sympy if we can.
                # If we have integer bounds, we'll use Mathics's iterator Sum
                # (which is Plus)

                if evaluation and all(
                    (hasattr(i, "is_integer") and i.is_integer)
                    or (hasattr(i, "is_finite") and i.is_finite and i.is_constant())
                    for i in bounds[1:]
                ):
                    # When we have integer bounds, it is better to not use Sympy but
                    # use Mathics evaluation. We turn:
                    # Sum[f[x], {<limits>}] into
                    #   MathicsSum[Table[f[x], {<limits>}]]
                    # where MathicsSum is self.get_result() our Iteration iterator.
                    values = Expression(SymbolTable, *expr.elements).evaluate(
                        evaluation
                    )
                    if values.get_head_name() != SymbolTable.get_name():
                        ret = self.get_result(values.elements).evaluate(evaluation)
                        # Make sure to convert the result back to sympy.
                        return ret.to_sympy()

            if None not in bounds:
                return sympy.summation(f_sympy, bounds)
