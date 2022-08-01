# -*- coding: utf-8 -*-

"""
Calculus

Originally called infinitesimal calculus or "the calculus of infinitesimals", is the mathematical study of continuous change, in the same way that geometry is the study of shape and algebra is the study of generalizations of arithmetic operations.
"""

import numpy as np
from itertools import product
from typing import Optional


from mathics.algorithm.integrators import (
    apply_D_to_Integral,
    _fubini,
    _internal_adaptative_simpsons_rule,
    decompose_domain,
)


from mathics.algorithm.series import (
    build_series,
    series_plus_series,
    series_times_series,
    series_derivative,
)


from mathics.builtin.base import Builtin, PostfixOperator, SympyFunction
from mathics.builtin.scoping import dynamic_scoping

from mathics.core.atoms import (
    String,
    Atom,
    Integer,
    Integer0,
    Integer1,
    Integer10,
    IntegerM1,
    Number,
    Rational,
    Real,
)
from mathics.core.attributes import (
    constant,
    hold_all,
    listable,
    n_hold_all,
    protected,
    read_protected,
)
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.function import expression_to_callable_and_args
from mathics.core.convert.python import from_python
from mathics.core.convert.sympy import sympy_symbol_prefix, SympyExpression, from_sympy
from mathics.core.evaluation import Evaluation
from mathics.core.evaluators import eval_N
from mathics.core.expression import Expression
from mathics.core.formatter import format_element
from mathics.core.list import ListExpression
from mathics.core.number import dps, machine_epsilon
from mathics.core.rules import Pattern

from mathics.core.symbols import (
    BaseElement,
    Symbol,
    SymbolFalse,
    SymbolList,
    SymbolPlus,
    SymbolPower,
    SymbolTimes,
    SymbolTrue,
)

from mathics.core.systemsymbols import (
    SymbolAnd,
    SymbolAutomatic,
    SymbolConditionalExpression,
    SymbolD,
    SymbolDerivative,
    SymbolInfinity,
    SymbolInfix,
    SymbolIntegrate,
    SymbolLeft,
    SymbolLog,
    SymbolNIntegrate,
    SymbolO,
    SymbolRule,
    SymbolSequence,
    SymbolSeries,
    SymbolSeriesData,
    SymbolSimplify,
    SymbolUndefined,
)


import sympy


class D(SympyFunction):
    """
    <dl>
      <dt>'D[$f$, $x$]'
      <dd>gives the partial derivative of $f$ with respect to $x$.

      <dt>'D[$f$, $x$, $y$, ...]'
      <dd>differentiates successively with respect to $x$, $y$, etc.

      <dt>'D[$f$, {$x$, $n$}]'
      <dd>gives the multiple derivative of order $n$.

      <dt>'D[$f$, {{$x1$, $x2$, ...}}]'
      <dd>gives the vector derivative of $f$ with respect to $x1$, $x2$, etc.
    </dl>

    First-order derivative of a polynomial:
    >> D[x^3 + x^2, x]
     = 2 x + 3 x ^ 2
    Second-order derivative:
    >> D[x^3 + x^2, {x, 2}]
     = 2 + 6 x

    Trigonometric derivatives:
    >> D[Sin[Cos[x]], x]
     = -Cos[Cos[x]] Sin[x]
    >> D[Sin[x], {x, 2}]
     = -Sin[x]
    >> D[Cos[t], {t, 2}]
     = -Cos[t]

    Unknown variables are treated as constant:
    >> D[y, x]
     = 0
    >> D[x, x]
     = 1
    >> D[x + y, x]
     = 1

    Derivatives of unknown functions are represented using 'Derivative':
    >> D[f[x], x]
     = f'[x]
    >> D[f[x, x], x]
     = Derivative[0, 1][f][x, x] + Derivative[1, 0][f][x, x]
    >> D[f[x, x], x] // InputForm
     = Derivative[0, 1][f][x, x] + Derivative[1, 0][f][x, x]

    Chain rule:
    >> D[f[2x+1, 2y, x+y], x]
     = 2 Derivative[1, 0, 0][f][1 + 2 x, 2 y, x + y] + Derivative[0, 0, 1][f][1 + 2 x, 2 y, x + y]
    >> D[f[x^2, x, 2y], {x,2}, y] // Expand
     = 8 x Derivative[1, 1, 1][f][x ^ 2, x, 2 y] + 8 x ^ 2 Derivative[2, 0, 1][f][x ^ 2, x, 2 y] + 2 Derivative[0, 2, 1][f][x ^ 2, x, 2 y] + 4 Derivative[1, 0, 1][f][x ^ 2, x, 2 y]

    Compute the gradient vector of a function:
    >> D[x ^ 3 * Cos[y], {{x, y}}]
     = {3 x ^ 2 Cos[y], -x ^ 3 Sin[y]}
    Hesse matrix:
    >> D[Sin[x] * Cos[y], {{x,y}, 2}]
     = {{-Cos[y] Sin[x], -Cos[x] Sin[y]}, {-Cos[x] Sin[y], -Cos[y] Sin[x]}}

    #> D[2/3 Cos[x] - 1/3 x Cos[x] Sin[x] ^ 2,x]//Expand
     = -2 x Cos[x] ^ 2 Sin[x] / 3 + x Sin[x] ^ 3 / 3 - 2 Sin[x] / 3 - Cos[x] Sin[x] ^ 2 / 3

    #> D[f[#1], {#1,2}]
     = f''[#1]
    #> D[(#1&)[t],{t,4}]
     = 0

    #> Attributes[f] ={HoldAll}; Apart[f''[x + x]]
     = f''[2 x]

    #> Attributes[f] = {}; Apart[f''[x + x]]
     = f''[2 x]

    ## Issue #375
    #> D[{#^2}, #]
     = {2 #1}
    """

    # TODO
    """
    >> D[2x, 2x]
     = 0
    """
    messages = {
        "dvar": (
            "Multiple derivative specifier `1` does not have the form "
            "{variable, n}, where n is a non-negative machine integer."
        ),
    }

    rules = {
        # Basic rules (implemented in apply):
        #   "D[f_ + g_, x_?NotListQ]": "D[f, x] + D[g, x]",
        #   "D[f_ * g_, x_?NotListQ]": "D[f, x] * g + f * D[g, x]",
        #   "D[f_ ^ r_, x_?NotListQ] /; FreeQ[r, x]": "r * f ^ (r-1) * D[f, x]",
        #   "D[E ^ f_, x_?NotListQ]": "E ^ f * D[f, x]",
        #   "D[f_ ^ g_, x_?NotListQ]": "D[E ^ (Log[f] * g), x]",
        # Hacky: better implement them in apply
        # "D[f_, x_?NotListQ] /; FreeQ[f, x]": "0",
        #  "D[f_[left___, x_, right___], x_?NotListQ] /; FreeQ[{left, right}, x]":
        #  "Derivative[Sequence @@ UnitVector["
        #  "  Length[{left, x, right}], Length[{left, x}]]][f][left, x, right]",
        #  'D[f_[args___], x_?NotListQ]':
        #  'Plus @@ MapIndexed[(D[f[Sequence@@ReplacePart[{args}, #2->t]], t] '
        #  '/. t->#) * D[#, x]&, {args}]',
        "D[{items___}, x_?NotListQ]": (
            "Function[{System`Private`item}, D[System`Private`item, x]]" " /@ {items}"
        ),
        # Handling iterated and vectorized derivative variables
        "D[f_, {list_List}]": "D[f, #]& /@ list",
        "D[f_, {list_List, n_Integer?Positive}]": (
            "D[f, Sequence @@ ConstantArray[{list}, n]]"
        ),
        "D[f_, x_, rest__]": "D[D[f, x], rest]",
        "D[expr_, {x_, n_Integer?NonNegative}]": (
            "Nest[Function[{t}, D[t, x]], expr, n]"
        ),
    }
    summary_text = "partial derivatives of scalar or vector functions"
    sympy_name = "Derivative"

    def apply(self, f, x, evaluation):
        "D[f_, x_?NotListQ]"
        x_pattern = Pattern.create(x)
        if f.is_free(x_pattern, evaluation):
            return Integer0
        elif f == x:
            return Integer1
        elif isinstance(f, Atom):  # Shouldn't happen
            1 / 0
            return
        # So, this is not an atom...

        head = f.get_head()
        if head is SymbolPlus:
            terms = [
                Expression(SymbolD, term, x)
                for term in f.elements
                if not term.is_free(x_pattern, evaluation)
            ]
            if len(terms) == 0:
                return Integer0
            return Expression(SymbolPlus, *terms)
        elif head is SymbolTimes:
            terms = []
            for i, factor in enumerate(f.elements):
                if factor.is_free(x_pattern, evaluation):
                    continue
                factors = [element for j, element in enumerate(f.elements) if j != i]
                factors.append(Expression(SymbolD, factor, x))
                terms.append(Expression(SymbolTimes, *factors))
            if len(terms) != 0:
                return Expression(SymbolPlus, *terms)
            else:
                return Integer0
        elif head is SymbolPower and len(f.elements) == 2:
            base, exp = f.elements
            terms = []
            if not base.is_free(x_pattern, evaluation):
                terms.append(
                    Expression(
                        SymbolTimes,
                        exp,
                        Expression(
                            SymbolPower,
                            base,
                            Expression(SymbolPlus, exp, IntegerM1),
                        ),
                        Expression(SymbolD, base, x),
                    )
                )
            if not exp.is_free(x_pattern, evaluation):
                if isinstance(base, Atom) and base.get_name() == "System`E":
                    terms.append(
                        Expression(SymbolTimes, f, Expression(SymbolD, exp, x))
                    )
                else:
                    terms.append(
                        Expression(
                            SymbolTimes,
                            f,
                            Expression(SymbolLog, base),
                            Expression(SymbolD, exp, x),
                        )
                    )

            if len(terms) == 0:
                return Integer0
            elif len(terms) == 1:
                return terms[0]
            else:
                return Expression(SymbolPlus, *terms)
        elif len(f.elements) == 1:
            if f.elements[0] == x:
                return Expression(
                    Expression(Expression(SymbolDerivative, Integer1), f.head), x
                )
            else:
                g = f.elements[0]
                return Expression(
                    SymbolTimes,
                    Expression(SymbolD, Expression(f.head, g), g),
                    Expression(SymbolD, g, x),
                )
        else:  # many elements

            def summand(element, index):
                result = Expression(
                    Expression(
                        Expression(
                            SymbolDerivative,
                            *(
                                [Integer0] * (index)
                                + [Integer1]
                                + [Integer0] * (len(f.elements) - index - 1)
                            ),
                        ),
                        f.head,
                    ),
                    *f.elements,
                )
                if element.sameQ(x):
                    return result
                else:
                    return Expression(
                        SymbolTimes, result, Expression(SymbolD, element, x)
                    )

            result = [
                summand(element, index)
                for index, element in enumerate(f.elements)
                if not element.is_free(x_pattern, evaluation)
            ]

            if len(result) == 1:
                return result[0]
            elif len(result) == 0:
                return Integer0
            else:
                return Expression(SymbolPlus, *result)

    def apply_wrong(self, expr, x, other, evaluation):
        "D[expr_, {x_, other___}]"

        arg = ListExpression(x, *other.get_sequence())
        evaluation.message(SymbolD, "dvar", arg)
        return Expression(SymbolD, expr, arg)


class Derivative(PostfixOperator, SympyFunction):
    """
    <dl>
      <dt>'Derivative[$n$][$f$]'
      <dd>represents the $n$th derivative of the function $f$.

      <dt>'Derivative[$n1$, $n2$, ...][$f$]'
      <dd>represents a multivariate derivative.
    </dl>

    >> Derivative[1][Sin]
     = Cos[#1]&
    >> Derivative[3][Sin]
     = -Cos[#1]&
    >> Derivative[2][# ^ 3&]
     = 6 #1&

    'Derivative' can be entered using '\\'':
    >> Sin'[x]
     = Cos[x]
    >> (# ^ 4&)''
     = 12 #1 ^ 2&
    >> f'[x] // InputForm
     = Derivative[1][f][x]

    >> Derivative[1][#2 Sin[#1]+Cos[#2]&]
     = Cos[#1] #2&
    >> Derivative[1,2][#2^3 Sin[#1]+Cos[#2]&]
     = 6 Cos[#1] #2&
    Deriving with respect to an unknown parameter yields 0:
    >> Derivative[1,2,1][#2^3 Sin[#1]+Cos[#2]&]
     = 0&
    The 0th derivative of any expression is the expression itself:
    >> Derivative[0,0,0][a+b+c]
     = a + b + c

    You can calculate the derivative of custom functions:
    >> f[x_] := x ^ 2
    >> f'[x]
     = 2 x

    Unknown derivatives:
    >> Derivative[2, 1][h]
     = Derivative[2, 1][h]
    >> Derivative[2, 0, 1, 0][h[g]]
     = Derivative[2, 0, 1, 0][h[g]]

    ## Parser Tests
    #> Hold[f''] // FullForm
     = Hold[Derivative[2][f]]
    #> Hold[f ' '] // FullForm
     = Hold[Derivative[2][f]]
    #> Hold[f '' ''] // FullForm
     = Hold[Derivative[4][f]]
    #> Hold[Derivative[x][4] '] // FullForm
     = Hold[Derivative[1][Derivative[x][4]]]
    """

    attributes = n_hold_all
    default_formats = False
    operator = "'"
    precedence = 670
    rules = {
        "MakeBoxes[Derivative[n__Integer][f_], "
        "  form:StandardForm|TraditionalForm]": (
            r"SuperscriptBox[MakeBoxes[f, form], If[{n} === {2}, "
            r'  "\[Prime]\[Prime]", If[{n} === {1}, "\[Prime]", '
            r'    RowBox[{"(", Sequence @@ Riffle[{n}, ","], ")"}]]]]'
        ),
        "MakeBoxes[Derivative[n:1|2][f_], form:OutputForm]": """RowBox[{MakeBoxes[f, form], If[n==1, "'", "''"]}]""",
        # The following rules should be applied in the apply method, instead of relying on the pattern matching
        # mechanism.
        "Derivative[0...][f_]": "f",
        "Derivative[n__Integer][Derivative[m__Integer][f_]] /; Length[{m}] "
        "== Length[{n}]": "Derivative[Sequence @@ ({n} + {m})][f]",
        # This would require at least some comments...
        """Derivative[n__Integer][f_Symbol] /; Module[{t=Sequence@@Slot/@Range[Length[{n}]], result, nothing, ft=f[t]},
            If[Head[ft] === f
            && FreeQ[Join[UpValues[f], DownValues[f], SubValues[f]], Derivative|D]
            && Context[f] != "System`",
                False,
                (* else *)
                ft = f[t];
                Block[{f},
                    Unprotect[f];
                    (*Derivative[1][f] ^= nothing;*)
                    Derivative[n][f] ^= nothing;
                    Derivative[n][nothing] ^= nothing;
                    result = D[ft, Sequence@@Table[{Slot[i], {n}[[i]]}, {i, Length[{n}]}]];
                ];
                FreeQ[result, nothing]
            ]
            ]""": """Module[{t=Sequence@@Slot/@Range[Length[{n}]], result, nothing, ft},
                ft = f[t];
                Block[{f},
                    Unprotect[f];
                    Derivative[n][f] ^= nothing;
                    Derivative[n][nothing] ^= nothing;
                    result = D[ft, Sequence@@Table[{Slot[i], {n}[[i]]}, {i, Length[{n}]}]];
                ];
                Function @@ {result}
            ]""",
        "Derivative[n__Integer][f_Function]": """Evaluate[D[
            Quiet[f[Sequence @@ Table[Slot[i], {i, 1, Length[{n}]}]],
                Function::slotn],
            Sequence @@ Table[{Slot[i], {n}[[i]]}, {i, 1, Length[{n}]}]]]&""",
    }

    summary_text = "symbolic and numerical derivative functions"

    def __init__(self, *args, **kwargs):
        super(Derivative, self).__init__(*args, **kwargs)

    def to_sympy(self, expr, **kwargs):
        inner = expr
        exprs = [inner]
        try:
            while True:
                inner = inner.head
                exprs.append(inner)
        except AttributeError:
            pass

        if len(exprs) != 4 or not all(len(exp.elements) >= 1 for exp in exprs[:3]):
            return

        if len(exprs[0].elements) != len(exprs[2].elements):
            return

        sym_args = [element.to_sympy() for element in exprs[0].elements]
        if None in sym_args:
            return

        func = exprs[1].elements[0]
        sym_func = sympy.Function(str(sympy_symbol_prefix + func.__str__()))(*sym_args)

        counts = [element.get_int_value() for element in exprs[2].elements]
        if None in counts:
            return

        # sympy expects e.g. Derivative(f(x, y), x, 2, y, 5)
        sym_d_args = []
        for sym_arg, count in zip(sym_args, counts):
            sym_d_args.append(sym_arg)
            sym_d_args.append(count)

        try:
            return sympy.Derivative(sym_func, *sym_d_args)
        except ValueError:
            return


class Integrate(SympyFunction):
    r"""
    <dl>
      <dt>'Integrate[$f$, $x$]'
      <dd>integrates $f$ with respect to $x$. The result does not contain the additive integration constant.

      <dt>'Integrate[$f$, {$x$, $a$, $b$}]'
      <dd>computes the definite integral of $f$ with respect to $x$ from $a$ to $b$.
    </dl>

    Integrate a polynomial:
    >> Integrate[6 x ^ 2 + 3 x ^ 2 - 4 x + 10, x]
     = x (10 - 2 x + 3 x ^ 2)

    Integrate trigonometric functions:
    >> Integrate[Sin[x] ^ 5, x]
     = Cos[x] (-1 - Cos[x] ^ 4 / 5 + 2 Cos[x] ^ 2 / 3)

    Definite integrals:
    >> Integrate[x ^ 2 + x, {x, 1, 3}]
     = 38 / 3
    >> Integrate[Sin[x], {x, 0, Pi/2}]
     = 1

    Some other integrals:
    >> Integrate[1 / (1 - 4 x + x^2), x]
     = Sqrt[3] (Log[-2 - Sqrt[3] + x] - Log[-2 + Sqrt[3] + x]) / 6
    >> Integrate[4 Sin[x] Cos[x], x]
     = 2 Sin[x] ^ 2

    > Integrate[-Infinity, {x, 0, Infinity}]
     = -Infinity

    > Integrate[-Infinity, {x, Infinity, 0}]
     = Infinity

    Integration in TeX:
    >> Integrate[f[x], {x, a, b}] // TeXForm
     = \int_a^b f\left[x\right] \, dx

    #> DownValues[Integrate]
     = {}
    #> Definition[Integrate]
     = Attributes[Integrate] = {Protected, ReadProtected}
     .
     . Options[Integrate] = {Assumptions -> $Assumptions, GenerateConditions -> Automatic, PrincipalValue -> False}
    #> Integrate[Hold[x + x], {x, a, b}]
     = Integrate[Hold[x + x], {x, a, b}]
    #> Integrate[sin[x], x]
     = Integrate[sin[x], x]

    #> Integrate[x ^ 3.5 + x, x]
     = x ^ 2 / 2 + 0.222222 x ^ 4.5

    Sometimes there is a loss of precision during integration.
    You can check the precision of your result with the following sequence
    of commands.
    >> Integrate[Abs[Sin[phi]], {phi, 0, 2Pi}] // N
     = 4.
     >> % // Precision
     = MachinePrecision

    #> Integrate[1/(x^5+1), x]
     = RootSum[1 + 5 #1 + 25 #1 ^ 2 + 125 #1 ^ 3 + 625 #1 ^ 4&, Log[x + 5 #1] #1&] + Log[1 + x] / 5

    #> Integrate[ArcTan(x), x]
     = x ^ 2 ArcTan / 2
    #> Integrate[E[x], x]
     = Integrate[E[x], x]

    #> Integrate[Exp[-(x/2)^2],{x,-Infinity,+Infinity}]
     = 2 Sqrt[Pi]

    #> Integrate[Exp[-1/(x^2)], x]
     = x E ^ (-1 / x ^ 2) + Sqrt[Pi] Erf[1 / x]

    >> Integrate[ArcSin[x / 3], x]
     = x ArcSin[x / 3] + Sqrt[9 - x ^ 2]

    >> Integrate[f'[x], {x, a, b}]
     = f[b] - f[a]
    and,
    >> D[Integrate[f[u, x],{u, a[x], b[x]}], x]
     = Integrate[Derivative[0, 1][f][u, x], {u, a[x], b[x]}] + f[b[x], x] b'[x] - f[a[x], x] a'[x]
    >> N[Integrate[Sin[Exp[-x^2 /2 ]],{x,1,2}]]
     = 0.330804
    """
    # Reinstate as a unit test or describe why it should be an example and fix.
    # >> Integrate[x/Exp[x^2/t], {x, 0, Infinity}]
    # = ConditionalExpression[t / 2, Abs[Arg[t]] < Pi / 2]
    # This should work after merging the more sophisticated predicate_evaluation routine
    # be merged...
    # >> Assuming[Abs[Arg[t]] < Pi / 2, Integrate[x/Exp[x^2/t], {x, 0, Infinity}]]
    # = t / 2
    attributes = protected | read_protected

    options = {
        "Assumptions": "$Assumptions",
        "GenerateConditions": "Automatic",
        "PrincipalValue": "False",
    }

    messages = {
        "idiv": "Integral of `1` does not converge on `2`.",
        "ilim": "Invalid integration variable or limit(s).",
        "iconstraints": "Additional constraints needed: `1`",
    }

    rules = {
        "N[Integrate[f_, x__List]]": "NIntegrate[f, x]",
        "Integrate[list_List, x_]": "Integrate[#, x]& /@ list",
        "MakeBoxes[Integrate[f_, x_], form:StandardForm|TraditionalForm]": r"""RowBox[{"\[Integral]","\[InvisibleTimes]", MakeBoxes[f, form], "\[InvisibleTimes]",
                RowBox[{"\[DifferentialD]", MakeBoxes[x, form]}]}]""",
        "MakeBoxes[Integrate[f_, {x_, a_, b_}], "
        "form:StandardForm|TraditionalForm]": r"""RowBox[{SubsuperscriptBox["\[Integral]", MakeBoxes[a, form],
                MakeBoxes[b, form]], "\[InvisibleTimes]" , MakeBoxes[f, form], "\[InvisibleTimes]",
                RowBox[{"\[DifferentialD]", MakeBoxes[x, form]}]}]""",
    }

    summary_text = "symbolic integrals in one or more dimensions"
    sympy_name = "Integral"

    def prepare_sympy(self, elements):
        if len(elements) == 2:
            x = elements[1]
            if x.has_form("List", 3):
                return [elements[0]] + x.elements
        return elements

    def from_sympy(self, sympy_name, elements):
        args = []
        for element in elements[1:]:
            if element.has_form("List", 1):
                # {x} -> x
                args.append(element.elements[0])
            else:
                args.append(element)
        new_elements = [elements[0]] + args
        return Expression(Symbol(self.get_name()), *new_elements)

    def apply(self, f, xs, evaluation, options):
        "Integrate[f_, xs__, OptionsPattern[]]"
        f_sympy = f.to_sympy()
        if f_sympy.is_infinite:
            return Expression(SymbolIntegrate, Integer1, xs).evaluate(evaluation) * f
        if f_sympy is None or isinstance(f_sympy, SympyExpression):
            return
        xs = xs.get_sequence()
        vars = []
        prec = None
        for x in xs:
            if x.has_form("List", 3):
                x, a, b = x.elements
                prec_a = a.get_precision()
                prec_b = b.get_precision()
                if prec_a is not None and prec_b is not None:
                    prec_new = min(prec_a, prec_b)
                    if prec is None or prec_new < prec:
                        prec = prec_new
                a = a.to_sympy()
                b = b.to_sympy()
                if a is None or b is None:
                    return
            else:
                a = b = None
            if not x.get_name():
                evaluation.message("Integrate", "ilim")
                return
            x = x.to_sympy()
            if x is None:
                return
            if a is None or b is None:
                vars.append(x)
            else:
                vars.append((x, a, b))
        try:
            sympy_result = sympy.integrate(f_sympy, *vars)
            pass
        except sympy.PolynomialError:
            return
        except ValueError:
            # e.g. ValueError: can't raise polynomial to a negative power
            return
        except NotImplementedError:
            # e.g. NotImplementedError: Result depends on the sign of
            # -sign(_Mathics_User_j)*sign(_Mathics_User_w)
            return
        if prec is not None and isinstance(sympy_result, sympy.Integral):
            # TODO MaxExtraPrecision -> maxn
            sympy_result = sympy_result.evalf(dps(prec))

        result = from_sympy(sympy_result)
        # If we obtain an atom (number or symbol)
        # just return...
        if isinstance(result, Atom):
            return result
        # If the result is defined as a Piecewise expression,
        # use ConditionalExpression.
        # This does not work now because the form sympy returns the values

        local_assumptions = options.get("System`Assumptions", None)
        old_assumptions = None
        if local_assumptions and local_assumptions is not Symbol("$Assumptions"):
            old_assumptions = evaluation.definitions.get_ownvalues(
                "System`$Assumptions"
            )
            assuming = local_assumptions.evaluate(evaluation)
            evaluation.definitions.set_ownvalue("System`$Assumptions", assuming)
        # Set the $Assumptions

        if result.get_head_name() == "System`Piecewise":
            cases = result.elements[0].elements
            if len(result.elements) == 1:
                if cases[-1].elements[1] is SymbolTrue:
                    default = cases[-1].elements[0]
                    cases = result.elements[0].elements[:-1]
                else:
                    default = SymbolUndefined
            else:
                cases = result.elements[0].elements
                default = result.elements[1]
            if default.has_form("Integrate", None):
                if default.elements[0] == f:
                    default = SymbolUndefined
            simplified_cases = []
            for case in cases:
                # TODO: if something like 0^n or 1/expr appears,
                # put the condition n!=0 or expr!=0 accordingly in the list of
                # conditions...
                cond = Expression(SymbolSimplify, case.elements[1]).evaluate(evaluation)
                resif = Expression(SymbolSimplify, case.elements[0]).evaluate(
                    evaluation
                )
                if cond is SymbolTrue:
                    if old_assumptions:
                        evaluation.definitions.set_ownvalue(
                            "System`$Assumptions", old_assumptions
                        )
                    return resif
                if resif.has_form("ConditionalExpression", 2):
                    cond = Expression(SymbolAnd, resif.elements[1], cond)
                    cond = Expression(SymbolSimplify, cond).evaluate(evaluation)
                    resif = resif.elements[0]
                simplified_cases.append(ListExpression(resif, cond))
            cases = simplified_cases
            if default is SymbolUndefined and len(cases) == 1:
                cases = cases[0]
                result = Expression(SymbolConditionalExpression, *(cases.elements))
            else:
                # FIXME: there is a bug in from_sympy which is leaving an integer
                # untranslated. Fix this and we can use Expression()
                result = to_expression(result._head, cases, default)
        else:
            if result.get_head() is SymbolIntegrate:
                if result.elements[0].evaluate(evaluation).sameQ(f):
                    # Sympy returned the same expression, so it can't be evaluated.
                    if old_assumptions:
                        evaluation.definitions.set_ownvalue(
                            "System`$Assumptions", old_assumptions
                        )
                    return
            result = Expression(SymbolSimplify, result)
            result = result.evaluate(evaluation)

        if old_assumptions:
            evaluation.definitions.set_ownvalue("System`$Assumptions", old_assumptions)
        return result

    def apply_D(self, func, domain, var, evaluation, options):
        """D[%(name)s[func_, domain__, OptionsPattern[%(name)s]], var_Symbol]"""
        return apply_D_to_Integral(
            func, domain, var, evaluation, options, SymbolIntegrate
        )


class Root(SympyFunction):
    """
    <dl>
    <dt>'Root[$f$, $i$]'
        <dd>represents the i-th complex root of the polynomial $f$
    </dl>

    >> Root[#1 ^ 2 - 1&, 1]
     = -1
    >> Root[#1 ^ 2 - 1&, 2]
     = 1

    Roots that can't be represented by radicals:
    >> Root[#1 ^ 5 + 2 #1 + 1&, 2]
     = Root[#1 ^ 5 + 2 #1 + 1&, 2]
    """

    messages = {
        "nuni": "Argument `1` at position 1 is not a univariate polynomial function",
        "nint": "Argument `1` at position 2 is not an integer",
        "iidx": "Argument `1` at position 2 is out of bounds",
    }

    summary_text = "the i-th root of a polynomial."
    sympy_name = "CRootOf"

    def apply(self, f, i, evaluation):
        "Root[f_, i_]"

        try:
            if not f.has_form("Function", 1):
                raise sympy.PolynomialError

            body = f.elements[0]
            poly = body.replace_slots([f, Symbol("_1")], evaluation)
            idx = i.to_sympy() - 1

            # Check for negative indeces (they are not allowed in Mathematica)
            if idx < 0:
                evaluation.message("Root", "iidx", i)
                return

            r = sympy.CRootOf(poly.to_sympy(), idx)
        except sympy.PolynomialError:
            evaluation.message("Root", "nuni", f)
            return
        except TypeError:
            evaluation.message("Root", "nint", i)
            return
        except IndexError:
            evaluation.message("Root", "iidx", i)
            return

        return from_sympy(r)

    def to_sympy(self, expr, **kwargs):
        try:
            if not expr.has_form("Root", 2):
                return None

            f = expr.elements[0]

            if not f.has_form("Function", 1):
                return None

            body = f.elements[0].replace_slots([f, Symbol("_1")], None)
            poly = body.to_sympy(**kwargs)

            i = expr.elements[1].get_int_value(**kwargs) - 1

            if i is None:
                return None

            return sympy.CRootOf(poly, i)
        except Exception:
            return None


class Solve(Builtin):
    """
    <dl>
      <dt>'Solve[$equation$, $vars$]'
      <dd>attempts to solve $equation$ for the variables $vars$.

      <dt>'Solve[$equation$, $vars$, $domain$]'
      <dd>restricts variables to $domain$, which can be 'Complexes' or 'Reals' or 'Integers'.
    </dl>

    >> Solve[x ^ 2 - 3 x == 4, x]
     = {{x -> -1}, {x -> 4}}
    >> Solve[4 y - 8 == 0, y]
     = {{y -> 2}}

    Apply the solution:
    >> sol = Solve[2 x^2 - 10 x - 12 == 0, x]
     = {{x -> -1}, {x -> 6}}
    >> x /. sol
     = {-1, 6}

    Contradiction:
    >> Solve[x + 1 == x, x]
     = {}
    Tautology:
    >> Solve[x ^ 2 == x ^ 2, x]
     = {{}}

    Rational equations:
    >> Solve[x / (x ^ 2 + 1) == 1, x]
     = {{x -> 1 / 2 - I / 2 Sqrt[3]}, {x -> 1 / 2 + I / 2 Sqrt[3]}}
    >> Solve[(x^2 + 3 x + 2)/(4 x - 2) == 0, x]
     = {{x -> -2}, {x -> -1}}

    Transcendental equations:
    >> Solve[Cos[x] == 0, x]
     = {{x -> Pi / 2}, {x -> 3 Pi / 2}}

    Solve can only solve equations with respect to symbols or functions:
    >> Solve[f[x + y] == 3, f[x + y]]
     = {{f[x + y] -> 3}}
    >> Solve[a + b == 2, a + b]
     : a + b is not a valid variable.
     = Solve[a + b == 2, a + b]
    This happens when solving with respect to an assigned symbol:
    >> x = 3;
    >> Solve[x == 2, x]
     : 3 is not a valid variable.
     = Solve[False, 3]
    >> Clear[x]
    >> Solve[a < b, a]
     : a < b is not a well-formed equation.
     = Solve[a < b, a]

    Solve a system of equations:
    >> eqs = {3 x ^ 2 - 3 y == 0, 3 y ^ 2 - 3 x == 0};
    >> sol = Solve[eqs, {x, y}] // Simplify
     = {{x -> 0, y -> 0}, {x -> 1, y -> 1}, {x -> -1 / 2 + I / 2 Sqrt[3], y -> -1 / 2 - I / 2 Sqrt[3]}, {x -> -1 / 2 - I / 2 Sqrt[3], y -> -1 / 2 + I / 2 Sqrt[3]}}
    >> eqs /. sol // Simplify
     = {{True, True}, {True, True}, {True, True}, {True, True}}

    An underdetermined system:
    >> Solve[x^2 == 1 && z^2 == -1, {x, y, z}]
     : Equations may not give solutions for all "solve" variables.
     = {{x -> -1, z -> -I}, {x -> -1, z -> I}, {x -> 1, z -> -I}, {x -> 1, z -> I}}

    Domain specification:
    >> Solve[x^2 == -1, x, Reals]
     = {}
    >> Solve[x^2 == 1, x, Reals]
     = {{x -> -1}, {x -> 1}}
    >> Solve[x^2 == -1, x, Complexes]
     = {{x -> -I}, {x -> I}}
    >> Solve[4 - 4 * x^2 - x^4 + x^6 == 0, x, Integers]
     = {{x -> -1}, {x -> 1}}

    #> Solve[x^2 +1 == 0, x] // FullForm
     = {{Rule[x, Complex[0, -1]]},{Rule[x, Complex[0, 1]]}}

    #> Solve[x^5==x,x]
     = {{x -> -1}, {x -> 0}, {x -> 1}, {x -> -I}, {x -> I}}

    #> Solve[g[x] == 0, x]
     = Solve[g[x] == 0, x]
    ## (should use inverse functions, actually!)
    #> Solve[g[x] + h[x] == 0, x]
     = Solve[g[x] + h[x] == 0, x]

    #> Solve[Sin(x) == 1, x]
     = {{x -> 1 / Sin}}

    #> Solve[E == 1, E]
     : E is not a valid variable.
     = Solve[False, E]
    #> Solve[False, Pi]
     : Pi is not a valid variable.
     = Solve[False, Pi]

    """

    messages = {
        "eqf": "`1` is not a well-formed equation.",
        "svars": 'Equations may not give solutions for all "solve" variables.',
    }

    rules = {
        "Solve[eqs_, vars_, Complexes]": "Solve[eqs, vars]",
        "Solve[eqs_, vars_, Reals]": (
            "Cases[Solve[eqs, vars], {Rule[x_,y_?RealNumberQ]}]"
        ),
        "Solve[eqs_, vars_, Integers]": (
            "Cases[Solve[eqs, vars], {Rule[x_,y_Integer]}]"
        ),
    }
    summary_text = "find generic solutions for variables"

    def apply(self, eqs, vars, evaluation):
        "Solve[eqs_, vars_]"

        vars_original = vars
        head_name = vars.get_head_name()
        if head_name == "System`List":
            vars = vars.elements
        else:
            vars = [vars]
        for var in vars:
            if (
                (isinstance(var, Atom) and not isinstance(var, Symbol))
                or head_name in ("System`Plus", "System`Times", "System`Power")  # noqa
                or constant & var.get_attributes(evaluation.definitions)
            ):

                evaluation.message("Solve", "ivar", vars_original)
                return
        eqs_original = eqs
        if eqs.get_head_name() in ("System`List", "System`And"):
            eqs = eqs.elements
        else:
            eqs = [eqs]
        sympy_eqs = []
        sympy_denoms = []
        for eq in eqs:
            if eq is SymbolTrue:
                pass
            elif eq is SymbolFalse:
                return ListExpression()
            elif not eq.has_form("Equal", 2):
                return evaluation.message("Solve", "eqf", eqs_original)
            else:
                left, right = eq.elements
                left = left.to_sympy()
                right = right.to_sympy()
                if left is None or right is None:
                    return
                eq = left - right
                eq = sympy.together(eq)
                eq = sympy.cancel(eq)
                sympy_eqs.append(eq)
                numer, denom = eq.as_numer_denom()
                sympy_denoms.append(denom)

        vars_sympy = [var.to_sympy() for var in vars]
        if None in vars_sympy:
            return

        # delete unused variables to avoid SymPy's
        # PolynomialError: Not a zero-dimensional system
        # in e.g. Solve[x^2==1&&z^2==-1,{x,y,z}]
        all_vars = vars[:]
        all_vars_sympy = vars_sympy[:]
        vars = []
        vars_sympy = []
        for var, var_sympy in zip(all_vars, all_vars_sympy):
            pattern = Pattern.create(var)
            if not eqs_original.is_free(pattern, evaluation):
                vars.append(var)
                vars_sympy.append(var_sympy)

        def transform_dict(sols):
            if not sols:
                yield sols
            for var, sol in sols.items():
                rest = sols.copy()
                del rest[var]
                rest = transform_dict(rest)
                if not isinstance(sol, (tuple, list)):
                    sol = [sol]
                if not sol:
                    for r in rest:
                        yield r
                else:
                    for r in rest:
                        for item in sol:
                            new_sols = r.copy()
                            new_sols[var] = item
                            yield new_sols
                break

        def transform_solution(sol):
            if not isinstance(sol, dict):
                if not isinstance(sol, (list, tuple)):
                    sol = [sol]
                sol = dict(list(zip(vars_sympy, sol)))
            return transform_dict(sol)

        if not sympy_eqs:
            sympy_eqs = True
        elif len(sympy_eqs) == 1:
            sympy_eqs = sympy_eqs[0]

        try:
            if isinstance(sympy_eqs, bool):
                result = sympy_eqs
            else:
                result = sympy.solve(sympy_eqs, vars_sympy)
            if not isinstance(result, list):
                result = [result]
            if isinstance(result, list) and len(result) == 1 and result[0] is True:
                return ListExpression(ListExpression())
            if result == [None]:
                return ListExpression()
            results = []
            for sol in result:
                results.extend(transform_solution(sol))
            result = results
            if any(
                sol and any(var not in sol for var in all_vars_sympy) for sol in result
            ):
                evaluation.message("Solve", "svars")

            # Filter out results for which denominator is 0
            # (SymPy should actually do that itself, but it doesn't!)
            result = [
                sol
                for sol in result
                if all(sympy.simplify(denom.subs(sol)) != 0 for denom in sympy_denoms)
            ]

            return ListExpression(
                *(
                    ListExpression(
                        *(
                            Expression(SymbolRule, var, from_sympy(sol[var_sympy]))
                            for var, var_sympy in zip(vars, vars_sympy)
                            if var_sympy in sol
                        ),
                    )
                    for sol in result
                ),
            )
        except sympy.PolynomialError:
            # raised for e.g. Solve[x^2==1&&z^2==-1,{x,y,z}] when not deleting
            # unused variables beforehand
            pass
        except NotImplementedError:
            pass
        except TypeError as exc:
            if str(exc).startswith("expected Symbol, Function or Derivative"):
                evaluation.message("Solve", "ivar", vars_original)


class Integers(Builtin):
    """
    <dl>
      <dt>'Integers'
      <dd>the domain of integer numbers, as in $x$ in Integers.
    </dl>

    Limit a solution to integer numbers:
    >> Solve[-4 - 4 x + x^4 + x^5 == 0, x, Integers]
     = {{x -> -1}}
    >> Solve[x^4 == 4, x, Integers]
     = {}
    """

    summary_text = "the domain integers numbers"


class Reals(Builtin):
    """
    <dl>
    <dt>'Reals'
        <dd>is the domain real numbers, as in $x$ in Reals.
    </dl>

    Limit a solution to real numbers:
    >> Solve[x^3 == 1, x, Reals]
     = {{x -> 1}}
    """

    summary_text = "the domain of the Real numbers"


class Complexes(Builtin):
    """
    <dl>
    <dt>'Complexes'
        <dd>the domain of complex numbers, as in $x$ in Complexes.
    </dl>
    """

    summary_text = "the domain complex numbers"


class Limit(Builtin):
    """
    <dl>
      <dt>'Limit[$expr$, $x$->$x0$]'
      <dd>gives the limit of $expr$ as $x$ approaches $x0$.

      <dt>'Limit[$expr$, $x$->$x0$, Direction->1]'
      <dd>approaches $x0$ from smaller values.

      <dt>'Limit[$expr$, $x$->$x0$, Direction->-1]'
      <dd>approaches $x0$ from larger values.
    </dl>

    >> Limit[x, x->2]
     = 2
    >> Limit[Sin[x] / x, x->0]
     = 1
    >> Limit[1/x, x->0, Direction->-1]
     = Infinity
    >> Limit[1/x, x->0, Direction->1]
     = -Infinity

    #> Limit[x, x -> x0, Direction -> x]
     : Value of Direction -> x should be -1 or 1.
     = Limit[x, x -> x0, Direction -> x]
    """

    """
    The following test is currently causing PyPy to segfault...
     #> Limit[(1 + cos[x]) / x, x -> 0]
     = Limit[(1 + cos[x]) / x, x -> 0]
    """

    attributes = listable | protected

    messages = {
        "ldir": "Value of Direction -> `1` should be -1 or 1.",
    }
    options = {
        "Direction": "1",
    }

    summary_text = "directed and undirected limits"

    def apply(self, expr, x, x0, evaluation, options={}):
        "Limit[expr_, x_->x0_, OptionsPattern[Limit]]"

        expr = expr.to_sympy()
        x = x.to_sympy()
        x0 = x0.to_sympy()

        if expr is None or x is None or x0 is None:
            return

        direction = self.get_option(options, "Direction", evaluation)
        value = direction.get_int_value()
        if value == -1:
            dir_sympy = "+"
        elif value == 1:
            dir_sympy = "-"
        else:
            return evaluation.message("Limit", "ldir", direction)

        try:
            result = sympy.limit(expr, x, x0, dir_sympy)
        except sympy.PoleError:
            pass
        except RuntimeError:
            # Bug in Sympy: RuntimeError: maximum recursion depth exceeded
            # while calling a Python object
            pass
        except NotImplementedError:
            pass
        except TypeError:
            # Unknown SymPy0.7.6 bug
            pass
        else:
            return from_sympy(result)


class DiscreteLimit(Builtin):
    """
    <dl>
      <dt>'DiscreteLimit[$f$, $k$->Infinity]'
      <dd>gives the limit of the sequence $f$ as $k$ tends to infinity.
    </dl>

    >> DiscreteLimit[n/(n + 1), n -> Infinity]
     = 1

    >> DiscreteLimit[f[n], n -> Infinity]
     = f[Infinity]
    """

    # TODO: Make this work
    """
    >> DiscreteLimit[(n/(n + 2)) E^(-m/(m + 1)), {m -> Infinity, n -> Infinity}]
     = 1 / E
    """
    attributes = listable | protected

    messages = {
        "dltrials": "The value of Trials should be a positive integer",
    }
    options = {
        "Trials": "5",
    }
    summary_text = "limits of sequences including recurrence and number theory"

    def apply(self, f, n, n0, evaluation, options={}):
        "DiscreteLimit[f_, n_->n0_, OptionsPattern[DiscreteLimit]]"

        f = f.to_sympy(convert_all_global_functions=True)
        n = n.to_sympy()
        n0 = n0.to_sympy()

        if n0 != sympy.oo:
            return

        if f is None or n is None:
            return

        trials = options["System`Trials"].get_int_value()

        if trials is None or trials <= 0:
            evaluation.message("DiscreteLimit", "dltrials")
            trials = 5

        try:
            return from_sympy(sympy.limit_seq(f, n, trials))
        except Exception:
            pass


class _BaseFinder(Builtin):
    """
    This class is the basis class for FindRoot, FindMinimum and FindMaximum.
    """

    attributes = hold_all | protected
    methods = {}
    messages = {
        "snum": "Value `1` is not a number.",
        "nnum": "The function value is not a number at `1` = `2`.",
        "dsing": "Encountered a singular derivative at the point `1` = `2`.",
        "bdmthd": "Value option Method->`1` is not `2`",
        "maxiter": (
            "The maximum number of iterations was exceeded. "
            "The result might be inaccurate."
        ),
        "fmgz": (
            "Encountered a gradient that is effectively zero. "
            "The result returned may not be a `1`; "
            "it may be a `2` or a saddle point."
        ),
    }

    options = {
        "MaxIterations": "100",
        "Method": "Automatic",
        "AccuracyGoal": "Automatic",
        "PrecisionGoal": "Automatic",
        "StepMonitor": "None",
        "EvaluationMonitor": "None",
        "Jacobian": "Automatic",
    }

    def apply(self, f, x, x0, evaluation, options):
        "%(name)s[f_, {x_, x0_}, OptionsPattern[]]"
        # This is needed to get the right messages
        options["_isfindmaximum"] = self.__class__ is FindMaximum
        # First, determine x0 and x
        x0 = eval_N(x0, evaluation)
        # deal with non 1D problems.
        if isinstance(x0, Expression) and x0._head is SymbolList:
            options["_x0"] = x0.elements
            x0 = x0.elements[0]
        if not isinstance(x0, Number):
            evaluation.message(self.get_name(), "snum", x0)
            return
        x_name = x.get_name()
        if not x_name:
            evaluation.message(self.get_name(), "sym", x, 2)
            return

        # Now, get the explicit form of f, depending of x
        # keeping x without evaluation (Like inside a "Block[{x},f])
        f = dynamic_scoping(lambda ev: f.evaluate(ev), {x_name: None}, evaluation)
        # If after evaluation, we get an "Equal" expression,
        # convert it in a function by substracting both
        # members. Again, ensure the scope in the evaluation
        if f.get_head_name() == "System`Equal":
            f = Expression(
                SymbolPlus,
                f.elements[0],
                Expression(SymbolTimes, IntegerM1, f.elements[1]),
            )
            f = dynamic_scoping(lambda ev: f.evaluate(ev), {x_name: None}, evaluation)

        # Determine the method
        method = options["System`Method"]
        if isinstance(method, Expression):
            if method.get_head() is SymbolList:
                method = method.elements[0]
        if isinstance(method, Symbol):
            method = method.get_name().split("`")[-1]
        elif isinstance(method, String):
            method = method.value
        if not isinstance(method, str):
            evaluation.message(
                self.get_name(),
                "bdmthd",
                method,
                [String(m) for m in self.methods.keys()],
            )
            return

        # Determine the "jacobian"s
        if (
            method in ("Newton", "Automatic")
            and options["System`Jacobian"] is SymbolAutomatic
        ):

            def diff(evaluation):
                return Expression(SymbolD, f, x).evaluate(evaluation)

            d = dynamic_scoping(diff, {x_name: None}, evaluation)
            options["System`Jacobian"] = d

        method_caller = self.methods.get(method, None)
        if method_caller is None:
            evaluation.message(
                self.get_name(),
                "bdmthd",
                method,
                [String(m) for m in self.methods.keys()],
            )
            return
        x0, success = method_caller(f, x0, x, options, evaluation)
        if not success:
            return
        if isinstance(x0, tuple):
            return ListExpression(
                x0[1],
                ListExpression(Expression(SymbolRule, x, x0[0])),
            )
        else:
            return ListExpression(Expression(SymbolRule, x, x0))

    def apply_with_x_tuple(self, f, xtuple, evaluation, options):
        "%(name)s[f_, xtuple_, OptionsPattern[]]"
        f_val = f.evaluate(evaluation)

        if f_val.has_form("Equal", 2):
            f = Expression(SymbolPlus, f_val.elements[0], f_val.elements[1])

        xtuple_value = xtuple.evaluate(evaluation)
        if xtuple_value.has_form("List", None):
            nelements = len(xtuple_value.elements)
            if nelements == 2:
                x, x0 = xtuple.evaluate(evaluation).elements
            elif nelements == 3:
                x, x0, x1 = xtuple.evaluate(evaluation).elements
                options["$$Region"] = (x0, x1)
            else:
                return
            return self.apply(f, x, x0, evaluation, options)
        return


class FindRoot(_BaseFinder):
    r"""
    <dl>
      <dt>'FindRoot[$f$, {$x$, $x0$}]'
      <dd>searches for a numerical root of $f$, starting from '$x$=$x0$'.

      <dt>'FindRoot[$lhs$ == $rhs$, {$x$, $x0$}]'
      <dd>tries to solve the equation '$lhs$ == $rhs$'.
    </dl>

    'FindRoot' by default uses Newton\'s method, so the function of interest should have a first derivative.

    >> FindRoot[Cos[x], {x, 1}]
     = {x -> 1.5708}
    >> FindRoot[Sin[x] + Exp[x],{x, 0}]
     = {x -> -0.588533}

    >> FindRoot[Sin[x] + Exp[x] == Pi,{x, 0}]
     = {x -> 0.866815}

    'FindRoot' has attribute 'HoldAll' and effectively uses 'Block' to localize $x$.
    However, in the result $x$ will eventually still be replaced by its value.
    >> x = "I am the result!";
    >> FindRoot[Tan[x] + Sin[x] == Pi, {x, 1}]
     = {I am the result! -> 1.14911}
    >> Clear[x]

    'FindRoot' stops after 100 iterations:
    >> FindRoot[x^2 + x + 1, {x, 1}]
     : The maximum number of iterations was exceeded. The result might be inaccurate.
     = {x -> -1.}

    Find complex roots:
    >> FindRoot[x ^ 2 + x + 1, {x, -I}]
     = {x -> -0.5 - 0.866025 I}

    The function has to return numerical values:
    >> FindRoot[f[x] == 0, {x, 0}]
     : The function value is not a number at x = 0..
     = FindRoot[f[x] - 0, {x, 0}]

    The derivative must not be 0:
    >> FindRoot[Sin[x] == x, {x, 0}]
     : Encountered a singular derivative at the point x = 0..
     = FindRoot[Sin[x] - x, {x, 0}]


    #> FindRoot[2.5==x,{x,0}]
     = {x -> 2.5}

    >> FindRoot[x^2 - 2, {x, 1,3}, Method->"Secant"]
     = {x -> 1.41421}

    """

    rules = {
        "FindRoot[lhs_ == rhs_, {x_, xs_}, opt:OptionsPattern[]]": "FindRoot[lhs-rhs, {x, xs}, opt]",
        "FindRoot[lhs_ == rhs_, x__, opt:OptionsPattern[]]": "FindRoot[lhs-rhs, x, opt]",
    }
    messages = _BaseFinder.messages.copy()
    methods = {}
    summary_text = (
        "Looks for a root of an equation or a zero of a numerical expression."
    )

    try:
        from mathics.algorithm.optimizers import (
            native_findroot_methods,
            native_findroot_messages,
        )

        methods.update(native_findroot_methods)
        messages.update(native_findroot_messages)
    except Exception:
        pass
    try:
        from mathics.builtin.scipy_utils.optimizers import (
            scipy_findroot_methods,
            update_findroot_messages,
        )

        methods.update(scipy_findroot_methods)
        messages = _BaseFinder.messages.copy()
        update_findroot_messages(messages)
    except Exception:
        pass


class FindMinimum(_BaseFinder):
    r"""
    <dl>
    <dt>'FindMinimum[$f$, {$x$, $x0$}]'
        <dd>searches for a numerical minimum of $f$, starting from '$x$=$x0$'.
    </dl>

    'FindMinimum' by default uses Newton\'s method, so the function of interest should have a first derivative.


    >> FindMinimum[(x-3)^2+2., {x, 1}]
     : Encountered a gradient that is effectively zero. The result returned may not be a minimum; it may be a maximum or a saddle point.
     = {2., {x -> 3.}}
    >> FindMinimum[10*^-30 *(x-3)^2+2., {x, 1}]
     : Encountered a gradient that is effectively zero. The result returned may not be a minimum; it may be a maximum or a saddle point.
     = {2., {x -> 3.}}
    >> FindMinimum[Sin[x], {x, 1}]
     = {-1., {x -> -1.5708}}
    >> phi[x_?NumberQ]:=NIntegrate[u,{u,0,x}, Method->"Internal"];
    >> Quiet[FindMinimum[phi[x]-x,{x, 1.2}, Method->"Newton"]]
     = {-0.5, {x -> 1.00001}}
    >> Clear[phi];
    For a not so well behaving function, the result can be less accurate:
    >> FindMinimum[Exp[-1/x^2]+1., {x,1.2}, MaxIterations->10]
     : The maximum number of iterations was exceeded. The result might be inaccurate.
     =  FindMinimum[Exp[-1 / x ^ 2] + 1., {x, 1.2}, MaxIterations -> 10]
    """

    methods = {}
    messages = _BaseFinder.messages.copy()
    summary_text = "local minimum optimization"
    try:
        from mathics.algorithm.optimizers import (
            native_local_optimizer_methods,
            native_optimizer_messages,
        )

        methods.update(native_local_optimizer_methods)
        messages.update(native_optimizer_messages)
    except Exception:
        pass
    try:
        from mathics.builtin.scipy_utils.optimizers import scipy_optimizer_methods

        methods.update(scipy_optimizer_methods)
    except Exception:
        pass


class FindMaximum(_BaseFinder):
    r"""
    <dl>
    <dt>'FindMaximum[$f$, {$x$, $x0$}]'
        <dd>searches for a numerical maximum of $f$, starting from '$x$=$x0$'.
    </dl>

    'FindMaximum' by default uses Newton\'s method, so the function of interest should have a first derivative.

    >> FindMaximum[-(x-3)^2+2., {x, 1}]
     : Encountered a gradient that is effectively zero. The result returned may not be a maximum; it may be a minimum or a saddle point.
     = {2., {x -> 3.}}
    >> FindMaximum[-10*^-30 *(x-3)^2+2., {x, 1}]
     : Encountered a gradient that is effectively zero. The result returned may not be a maximum; it may be a minimum or a saddle point.
     = {2., {x -> 3.}}
    >> FindMaximum[Sin[x], {x, 1}]
     = {1., {x -> 1.5708}}
    >> phi[x_?NumberQ]:=NIntegrate[u, {u, 0., x}, Method->"Internal"];
    >> Quiet[FindMaximum[-phi[x] + x, {x, 1.2}, Method->"Newton"]]
     = {0.5, {x -> 1.00001}}
    >> Clear[phi];
    For a not so well behaving function, the result can be less accurate:
    >> FindMaximum[-Exp[-1/x^2]+1., {x,1.2}, MaxIterations->10]
     : The maximum number of iterations was exceeded. The result might be inaccurate.
     = FindMaximum[-Exp[-1 / x ^ 2] + 1., {x, 1.2}, MaxIterations -> 10]
    """

    methods = {}
    messages = _BaseFinder.messages.copy()
    summary_text = "local maximum optimization"
    try:
        from mathics.algorithm.optimizers import native_local_optimizer_methods

        methods.update(native_local_optimizer_methods)
    except Exception:
        pass
    try:
        from mathics.builtin.scipy_utils.optimizers import scipy_optimizer_methods

        methods.update(scipy_optimizer_methods)
    except Exception:
        pass


class O_(Builtin):
    """
    <dl>
      <dt>'O[$x$]^n'
      <dd> Represents a term of order $x^n$.
      <dd> O[x]^n is generated to represent omitted higher order terms in power series.
    </dl>

    >> Series[1/(1-x),{x,0,2}]
     = 1 + x + x ^ 2 + O[x] ^ 3

    When called alone, a `SeriesData` expression is built:
    >> O[x] // FullForm
     = SeriesData[x, 0, {}, 1, 1, 1]

    """

    name = "O"
    rules = {
        "O[x_Symbol]": "SeriesData[x, 0, {}, 1, 1, 1]",
    }
    summary_text = "symbolic representation of a higher-order series term"


class Series(Builtin):
    """
    <dl>
      <dt>'Series[$f$, {$x$, $x0$, $n$}]'
      <dd>Represents the series expansion around '$x$=$x0$' up to order $n$.
    </dl>

    For elementary expressions, 'Series' returns the explicit power series as a 'SeriesData' expression:
    >> Series[Exp[x], {x,0,2}]
     = 1 + x + 1 / 2 x ^ 2 + O[x] ^ 3
    >> % // FullForm
     = SeriesData[x, 0, {1,1,Rational[1, 2]}, 0, 3, 1]
    Replacing the variable by a value, the series will not be evaluated as
    an expression, but as a 'SeriesData' object:
    >> s = Series[Exp[x^2],{x,0,2}]
     = 1 + x ^ 2 + O[x] ^ 3
    >> s /. x->4
     = 1 + 4 ^ 2 + O[4] ^ 3

    'Normal' transforms a 'SeriesData' expression into a polynomial:
    >> s // Normal
     = 1 + x ^ 2
    >> (s // Normal) /. x-> 4
     = 17
    >> Clear[s];
    We can also expand over multiple variables
    >> Series[Exp[x-y], {x, 0, 2}, {y, 0, 2}]
     = (1 - y + 1 / 2 y ^ 2 + O[y] ^ 3) + (1 - y + 1 / 2 y ^ 2 + O[y] ^ 3) x + (1 / 2 + (-1 / 2) y + 1 / 4 y ^ 2 + O[y] ^ 3) x ^ 2 + O[x] ^ 3

    """

    messages = {
        "icm": "Series in `1` to be combined have unequal expansion points `2` and `3`.",
        "serlim": "Series order specification `1` is not a machine-sized integer.",
        "sspec": "Series specification `1` is not a list with three elements.",
    }

    summary_text = "power series and asymptotic expansions"

    def apply_series(self, f, x, x0, n, evaluation):
        """Series[f_, {x_Symbol, x0_, n_Integer}]"""
        return build_series(f, x, x0, n, evaluation)

    def apply_multivariate_series(self, f, varspec, evaluation):
        """Series[f_,varspec__List]"""
        lastvar = varspec.elements[-1]
        if not lastvar.has_form("List", 3):
            return None
        # inner = build_series(f, *(lastvar.elements), evaluation)
        inner = Expression(SymbolSeries, f, lastvar).evaluate(evaluation)
        if inner:
            if len(varspec.elements) == 1:
                return inner
            remain_vars = Expression(SymbolSequence, *varspec.elements[:-1])
            result = self.apply_multivariate_series(inner, remain_vars, evaluation)
            return result
        return None


class SeriesData(Builtin):
    """
    <dl>
      <dt>'SeriesData[...]'
      <dd>Represents a series expansion
    </dl>

    Sum of two series:
    >> Series[Cosh[x],{x,0,2}] + Series[Sinh[x],{x,0,3}]
     = 1 + x + 1 / 2 x ^ 2 + O[x] ^ 3
    >> Series[f[x],{x,0,2}] * g[w]
     = f[0] g[w] + g[w] f'[0] x + g[w] f''[0] / 2 x ^ 2 + O[x] ^ 3
    The product of two series on the same neighbourhood of the same variable are multiplied
    >> Series[Exp[-a x],{x,0,2}] * Series[Exp[-b x],{x,0,2}]
     = 1 + (-a - b) x + (a ^ 2 / 2 + a b + b ^ 2 / 2) x ^ 2 + O[x] ^ 3
    >> D[Series[Exp[-a x],{x,0,2}],a]
     = -x + a x ^ 2 + O[x] ^ 3
    """

    # TODO: Implement sum, product and composition of series

    precedence = 1000
    summary_text = "power series of a variable about a point"

    def apply_reduce(self, x, x0, data, nummin, nummax, den, evaluation):
        """SeriesData[x_,x0_,data_,nummin_Integer, nummax_Integer, den_Integer]"""
        # This method tries to reduce the series expansion in two ways:
        # if x===x0, evaluates the series
        if x.sameQ(x0):
            nummin_val = nummin.get_int_value()
            if nummin_val > 0:
                return Integer0
            if nummin_val < 0:
                return SymbolInfinity
            if data.elements:
                return data.elements[0]
            else:
                return Integer0
        # if data has trailing zeros, the method tries to remove them.
        coeffs = data.elements
        len_coeffs = len(coeffs)
        # If the series is trivial, do not do anything:
        if len_coeffs == 0:
            return

        nonzeroidx_left = 0
        nonzeroidx_right = 0
        while nonzeroidx_left < len_coeffs and Integer0.sameQ(coeffs[nonzeroidx_left]):
            nonzeroidx_left = nonzeroidx_left + 1

        len_coeffs = len_coeffs - nonzeroidx_left

        while nonzeroidx_right < len_coeffs and Integer0.sameQ(
            coeffs[-nonzeroidx_right - 1]
        ):
            nonzeroidx_right = nonzeroidx_right + 1

        if nonzeroidx_left == 0 and nonzeroidx_right == 0:
            return
        # if the lower order coeffs vanishes, moves xmin and xmax.
        if nonzeroidx_left:
            nummin = Integer(nummin.get_int_value() + nonzeroidx_left)
        if nonzeroidx_right:
            return Expression(
                SymbolSeriesData,
                x,
                x0,
                from_python(data.elements[nonzeroidx_left:(-nonzeroidx_right)]),
                nummin,
                nummax,
                den,
            )
        else:
            return Expression(
                SymbolSeriesData,
                x,
                x0,
                from_python(data.elements[nonzeroidx_left:]),
                nummin,
                nummax,
                den,
            )

    def apply_plus(self, x, x0, data, nummin, nummax, den, term, evaluation):
        """Plus[SeriesData[x_, x0_, data_, nummin_Integer, nummax_Integer, den_Integer], term__]"""
        # If the series is null, build a series with the remaining terms
        if all(Integer0.sameQ(element) for element in data.elements):
            if term.get_head() is SymbolSequence:
                term = Expression(SymbolPlus, *term.elements)
            ret = build_series(
                term,
                x,
                x0,
                nummax.value / nummax.value,
                evaluation,
            )
            return ret
        series = (
            data,
            nummin.value,
            nummax.value,
            den.value,
        )
        if term.get_head() is SymbolSequence:
            terms = term.elements
        else:
            terms = [term]

        # Tries to convert each term into a series around the same
        # neighbourhood
        incompat_series = []
        max_exponent = Integer(int(series[2] / series[3] + 1))
        for t in terms:
            if Integer0.sameQ(t):
                continue
            # if t.get_head() is not SymbolSeriesData:
            if t.get_head() is SymbolSeriesData:
                y, y0 = t.elements[0:2]
                if y.sameQ(x):
                    if not y0.sameQ(x0):
                        evaluation.message("Series", "icm", x, x0, y0)
                        incompat_series.append(t)
                        continue
                    else:
                        data_y, nmin_y, nmax_y, den_y = t.elements[2:]
                        nmin_val = nmin_y.get_int_value()
                        nmax_val = nmax_y.get_int_value()
                        den_val = den_y.get_int_value()
                        tseries = (data_y, nmin_val, nmax_val, den_val)
                        series_new = series_plus_series(series, tseries)
                        if series_new:
                            series = series_new
                            continue
                        else:
                            incompat_series.append(t)
                            continue
            # If t is not a series or is a series in a different variable,
            # try to convert it into a series in x around x0:
            tnew = build_series(t, x, x0, max_exponent, evaluation)
            tseries = None
            if tnew.get_head() is SymbolSeriesData:
                y, y0, data_y, nmin_y, nmax_y, den_y = tnew.elements
                if y.sameQ(x) and y0.sameQ(x0):
                    nmin_val = nmin_y.get_int_value()
                    nmax_val = nmax_y.get_int_value()
                    den_val = den_y.get_int_value()
                    tseries = (data_y, nmin_val, nmax_val, den_val)

            if tseries is None:
                data_y = ListExpression(t)
                tseries = (data_y, 0, max_exponent.get_int_value(), 1)
            series_new = series_plus_series(series, tseries)
            if series_new:
                series = series_new
            else:
                incompat_series.append(t)

        series_expr = Expression(
            SymbolSeriesData, x, x0, series[0], *[Integer(u) for u in series[1:]]
        )
        if incompat_series:
            series_expr = Expression(SymbolPlus, *incompat_series, series_expr)
        return series_expr

    def apply_times(self, x, x0, data, nummin, nummax, den, coeff, evaluation):
        """Times[SeriesData[x_, x0_, data_, nummin_, nummax_, den_], coeff__]"""
        series = (
            data,
            nummin.get_int_value(),
            nummax.get_int_value(),
            den.get_int_value(),
        )
        x_pattern = Pattern.create(x)
        incompat_series = []
        max_exponent = Integer(int(series[2] / series[3] + 1))
        if coeff.get_head() is SymbolSequence:
            factors = coeff.elements
        else:
            factors = [coeff]

        for factor in factors:
            if Integer0.sameQ(factor):
                return Integer0
            if Integer1.sameQ(factor):
                continue
            if factor.is_free(x_pattern, evaluation):
                newdata = to_mathics_list(
                    *[factor * element for element in data.elements]
                )
                series = (newdata, *series[1:])
                continue
            if factor.get_head() is SymbolSeriesData:
                y, y0 = factor.elements[0:2]
                if y.sameQ(x):
                    if not y0.sameQ(x0):
                        evaluation.message("Series", "icm", x, x0, y0)
                        incompat_series.append(factor)
                        continue
                    else:
                        data_y, nmin_y, nmax_y, den_y = factor.elements[2:]
                        nmin_val = nmin_y.get_int_value()
                        nmax_val = nmax_y.get_int_value()
                        den_val = den_y.get_int_value()
                        tseries = (data_y, nmin_val, nmax_val, den_val)
                        series_new = series_times_series(series, tseries)
                        if series_new:
                            series = series_new
                            continue
                        else:
                            incompat_series.append(factor)
                            continue

            # If t is not a series or is a series in a different variable,
            # try to convert it into a series in x around x0:
            factor_new = build_series(factor, x, x0, max_exponent, evaluation)
            fseries = None
            if factor_new.get_head() is SymbolSeriesData:
                y, y0, data_y, nmin_y, nmax_y, den_y = factor_new.elements
                if y.sameQ(x) and y0.sameQ(x0):
                    nmin_val = nmin_y.get_int_value()
                    nmax_val = nmax_y.get_int_value()
                    den_val = den_y.get_int_value()
                    fseries = (data_y, nmin_val, nmax_val, den_val)

            if fseries is None:
                data_y = ListExpression(factor)
                fseries = (data_y, 0, max_exponent.get_int_value(), 1)
            series_new = series_times_series(series, fseries)
            if series_new:
                series = series_new
            else:
                incompat_series.append(factor)

        series_expr = Expression(
            SymbolSeriesData, x, x0, series[0], *[Integer(u) for u in series[1:]]
        )
        if incompat_series:
            series_expr = Expression(SymbolTimes, *incompat_series, series_expr)
        return series_expr

    def apply_derivative(self, x, x0, data, nummin, nummax, den, y, evaluation):
        """D[SeriesData[x_, x0_, data_, nummin_, nummax_, den_], y_]"""
        series = (
            data,
            nummin.get_int_value(),
            nummax.get_int_value(),
            den.get_int_value(),
        )
        if isinstance(y, Symbol):
            order = 1
        elif y.has_form("List", 2):
            order = y.elements[1].get_int_value()
            y = y.elements[0]
        else:
            return
        while order:
            series = series_derivative(series, x, x0, y, evaluation)
            if series is None:
                return Integer0
            order = order - 1
        result = Expression(
            SymbolSeriesData,
            x,
            x0,
            series[0],
            Integer(series[1]),
            Integer(series[2]),
            Integer(series[3]),
        )
        return result

    def apply_normal(self, x, x0, data, nummin, nummax, den, evaluation):
        """Normal[SeriesData[x_, x0_, data_, nummin_, nummax_, den_]]"""
        new_data = []
        for element in data.elements:
            if element.has_form("SeriesData", 6):
                element = self.apply_normal(*(element.elements), evaluation)
                if element is None:
                    return
            new_data.extend([element])
        data = new_data
        return Expression(
            SymbolPlus,
            *[
                a * (x - x0) ** ((nummin + Integer(k)) / den)
                for k, a in enumerate(data)
            ],
        )

    def pre_makeboxes(self, x, x0, data, nmin, nmax, den, form, evaluation):
        if x0.is_zero:
            variable = x
        else:
            variable = Expression(SymbolPlus, x, Expression(SymbolTimes, IntegerM1, x0))
        den = den.get_int_value()
        nmin = nmin.get_int_value()
        nmax = nmax.get_int_value()
        if den != 1:
            powers = [Rational(i, den) for i in range(nmin, nmax)]
            powers = powers + [Rational(nmax, den)]
        else:
            powers = [Integer(i) for i in range(nmin, nmax)]
            powers = powers + [Integer(nmax)]

        expansion = []
        for i, element in enumerate(data.elements):
            if element.get_head() is Symbol("SeriesData"):
                element = self.pre_makeboxes(*(element.elements), form, evaluation)
            elif element.is_numeric(evaluation) and element.is_zero:
                continue
            if powers[i].is_zero:
                expansion.append(element)
                continue
            if powers[i] == Integer1:
                if element == Integer1:
                    term = variable
                else:
                    term = Expression(SymbolTimes, element, variable)
            else:
                if element == Integer1:
                    term = Expression(SymbolPower, variable, powers[i])
                else:
                    term = Expression(
                        SymbolTimes,
                        element,
                        Expression(SymbolPower, variable, powers[i]),
                    )
            expansion.append(term)
        expansion = ListExpression(
            Expression(SymbolPlus, *expansion),
            Expression(SymbolPower, Expression(SymbolO, variable), powers[-1]),
        )
        return Expression(SymbolInfix, expansion, String("+"), Integer(300), SymbolLeft)

    def apply_makeboxes(self, x, x0, data, nmin, nmax, den, form, evaluation):
        """MakeBoxes[SeriesData[x_, x0_, data_List, nmin_Integer, nmax_Integer, den_Integer],
        form:StandardForm|TraditionalForm|OutputForm|InputForm]"""

        expansion = self.pre_makeboxes(x, x0, data, nmin, nmax, den, form, evaluation)
        return format_element(expansion, evaluation, form)


class NIntegrate(Builtin):
    """
    <dl>
       <dt>'NIntegrate[$expr$, $interval$]'
       <dd>returns a numeric approximation to the definite integral of $expr$ with limits $interval$ and with a precision of $prec$ digits.

        <dt>'NIntegrate[$expr$, $interval1$, $interval2$, ...]'
        <dd>returns a numeric approximation to the multiple integral of $expr$ with limits $interval1$, $interval2$ and with a precision of $prec$ digits.
    </dl>

    >> NIntegrate[Exp[-x],{x,0,Infinity},Tolerance->1*^-6, Method->"Internal"]
     = 1.
    >> NIntegrate[Exp[x],{x,-Infinity, 0},Tolerance->1*^-6, Method->"Internal"]
     = 1.
    >> NIntegrate[Exp[-x^2/2.],{x,-Infinity, Infinity},Tolerance->1*^-6, Method->"Internal"]
     = 2.5066...

    """

    # ## The Following tests fails if sympy is not installed.
    # >> Table[1./NIntegrate[x^k,{x,0,1},Tolerance->1*^-6], {k,0,6}]
    # : The specified method failed to return a number. Falling back into the internal evaluator.
    # = {1., 2., 3., 4., 5., 6., 7.}

    # >> NIntegrate[1 / z, {z, -1 - I, 1 - I, 1 + I, -1 + I, -1 - I}, Tolerance->1.*^-4]
    # ## = 6.2832 I

    # Integrate singularities with weak divergences:
    # >> Table[ NIntegrate[x^(1./k-1.), {x,0,1.}, Tolerance->1*^-6], {k,1,7.}]
    # = {1., 2., 3., 4., 5., 6., 7.}

    # Mutiple Integrals :
    # >> NIntegrate[x * y,{x, 0, 1}, {y, 0, 1}]
    # = 0.25

    messages = {
        "bdmtd": "The Method option should be a built-in method name.",
        "inumr": (
            "The integrand `1` has evaluated to non-numerical "
            + "values for all sampling points in the region "
            + "with boundaries `2`"
        ),
        "nlim": "`1` = `2` is not a valid limit of integration.",
        "ilim": "Invalid integration variable or limit(s) in `1`.",
        "mtdfail": (
            "The specified method failed to return a "
            + "number. Falling back into the internal "
            + "evaluator."
        ),
        "cmpint": ("Integration over a complex domain is not " + "implemented yet"),
    }

    methods = {
        "Automatic": (None, False),
    }
    options = {
        "Method": '"Automatic"',
        "Tolerance": "1*^-10",
        "Accuracy": "1*^-10",
        "MaxRecursion": "10",
    }

    summary_text = "numerical integration in one or several variables"

    try:
        # builtin integrators
        from mathics.algorithm.integrators import (
            integrator_methods,
            integrator_messages,
        )

        methods.update(integrator_methods)
        messages.update(integrator_messages)
    except Exception:
        pass

    try:
        # scipy integrators
        from mathics.builtin.scipy_utils.integrators import (
            scipy_nintegrate_methods,
            scipy_nintegrate_messages,
        )

        methods.update(scipy_nintegrate_methods)
        messages.update(scipy_nintegrate_messages)
    except Exception:
        pass

    messages.update(
        {
            "bdmtd": "The Method option should be a "
            + "built-in method name in {`"
            + "`, `".join(list(methods))
            + "`}. Using `Automatic`"
        }
    )

    def apply_with_func_domain(self, func, domain, evaluation, options):
        "%(name)s[func_, domain__, OptionsPattern[%(name)s]]"
        if func.is_numeric() and func.is_zero:
            return Integer0
        method = options["System`Method"].evaluate(evaluation)
        method_options = {}
        if method.has_form("System`List", 2):
            method = method.elements[0]
            method_options.update(method.elements[1].get_option_values())
        if isinstance(method, String):
            method = method.value
        elif isinstance(method, Symbol):
            method = method.get_name()
            # strip context
            method = method[method.rindex("`") + 1 :]
        else:
            evaluation.message("NIntegrate", "bdmtd", method)
            return
        tolerance = options["System`Tolerance"].evaluate(evaluation)
        tolerance = float(tolerance.value)
        accuracy = options["System`Accuracy"].evaluate(evaluation)
        accuracy = accuracy.value
        maxrecursion = options["System`MaxRecursion"].evaluate(evaluation)
        maxrecursion = maxrecursion.value
        nintegrate_method = self.methods.get(method, None)
        if nintegrate_method is None:
            evaluation.message("NIntegrate", "bdmtd", method)
            nintegrate_method = self.methods.get("Automatic")
        if type(nintegrate_method) is tuple:
            nintegrate_method, is_multidimensional = nintegrate_method
        else:
            is_multidimensional = False

        domain = decompose_domain(domain, evaluation)
        if not domain:
            return
        if not isinstance(domain, list):
            domain = [domain]

        coords = [axis[0] for axis in domain]
        # If any of the points in the integration domain is complex,
        # stop the evaluation...
        if any([c.get_head_name() == "System`List" for c in coords]):
            evaluation.message("NIntegrate", "cmpint")
            return

        integrand, cargs = expression_to_callable_and_args(func, coords, evaluation)

        if integrand is None:
            evaluation.message("inumer", func, domain)
            return
        results = []
        for subdomain in product(*[axis[1] for axis in domain]):
            # On each subdomain, check if the region is bounded.
            # If not, implement a coordinate map
            func2 = integrand
            subdomain2 = []
            coordtransform = []
            nulldomain = False
            for i, r in enumerate(subdomain):
                a = r[0].evaluate(evaluation)
                b = r[1].evaluate(evaluation)
                if a == b:
                    nulldomain = True
                    break
                elif a.get_head_name() == "System`DirectedInfinity":
                    if b.get_head_name() == "System`DirectedInfinity":
                        a = a.to_python()
                        b = b.to_python()
                        le = 1 - machine_epsilon
                        if a == b:
                            nulldomain = True
                            break
                        elif a < b:
                            subdomain2.append([-le, le])
                        else:
                            subdomain2.append([le, -le])
                        coordtransform.append(
                            (np.arctanh, lambda u: 1.0 / (1.0 - u**2))
                        )
                    else:
                        if not b.is_numeric(evaluation):
                            evaluation.message("nlim", coords[i], b)
                            return
                        z = a.elements[0].value
                        b = b.value
                        subdomain2.append([machine_epsilon, 1.0])
                        coordtransform.append(
                            (lambda u: b - z + z / u, lambda u: -z * u ** (-2.0))
                        )
                elif b.get_head_name() == "System`DirectedInfinity":
                    if not a.is_numeric(evaluation):
                        evaluation.message("nlim", coords[i], a)
                        return
                    a = a.value
                    z = b.elements[0].value
                    subdomain2.append([machine_epsilon, 1.0])
                    coordtransform.append(
                        (lambda u: a - z + z / u, lambda u: z * u ** (-2.0))
                    )
                elif a.is_numeric(evaluation) and b.is_numeric(evaluation):
                    a = eval_N(a, evaluation).value
                    b = eval_N(b, evaluation).value
                    subdomain2.append([a, b])
                    coordtransform.append(None)
                else:
                    for x in (a, b):
                        if not x.is_numeric(evaluation):
                            evaluation.message("nlim", coords[i], x)
                    return

            if nulldomain:
                continue
            if any(coordtransform):

                def func2_(*u):
                    x_u = (
                        x[0](u[i]) if x else u[i] for i, x in enumerate(coordtransform)
                    )
                    punctual_value = integrand(*x_u)
                    jac_factors = tuple(
                        jac[1](u[i]) for i, jac in enumerate(coordtransform) if jac
                    )
                    val_jac = np.prod(jac_factors)
                    return punctual_value * val_jac

                func2 = func2_
            opts = {
                "acur": accuracy,
                "tol": tolerance,
                "maxrec": maxrecursion,
            }
            opts.update(method_options)
            try:
                if len(subdomain2) > 1:
                    if is_multidimensional:
                        nintegrate_method(func2, subdomain2, **opts)
                    else:
                        val = _fubini(
                            func2, subdomain2, integrator=nintegrate_method, **opts
                        )
                else:
                    val = nintegrate_method(func2, *(subdomain2[0]), **opts)
            except Exception:
                val = None

            if val is None:
                evaluation.message("NIntegrate", "mtdfail")
                if len(subdomain2) > 1:
                    val = _fubini(
                        func2,
                        subdomain2,
                        integrator=_internal_adaptative_simpsons_rule,
                        **opts,
                    )
                else:
                    try:
                        val = _internal_adaptative_simpsons_rule(
                            func2, *(subdomain2[0]), **opts
                        )
                    except Exception:
                        return None
            results.append(val)

        result = sum([r[0] for r in results])
        # error = sum([r[1] for r in results]) -> use it when accuracy
        #                                         be implemented...
        return from_python(result)

    def apply_D(self, func, domain, var, evaluation, options):
        """D[%(name)s[func_, domain__, OptionsPattern[%(name)s]], var_Symbol]"""
        return apply_D_to_Integral(
            func, domain, var, evaluation, options, SymbolNIntegrate
        )


# Auxiliary routines. Maybe should be moved to another module.


def is_zero(
    val: BaseElement,
    acc_goal: Optional[Real],
    prec_goal: Optional[Real],
    evaluation: Evaluation,
) -> bool:
    """
    Check if val is zero upto the precision and accuracy goals
    """
    if not isinstance(val, Number):
        val = eval_N(val, evaluation)
    if not isinstance(val, Number):
        return False
    if val.is_zero:
        return True
    if not (acc_goal or prec_goal):
        return False

    eps_expr: BaseElement = Integer10 ** (-prec_goal) if prec_goal else Integer0
    if acc_goal:
        eps_expr = eps_expr + Integer10 ** (-acc_goal) / abs(val)
    threeshold_expr = Expression(SymbolLog, eps_expr)
    threeshold: Real = eval_N(threeshold_expr, evaluation)
    return threeshold.to_python() > 0
