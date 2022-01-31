# -*- coding: utf-8 -*-

"""
Calculus

Originally called infinitesimal calculus or "the calculus of infinitesimals", is the mathematical study of continuous change, in the same way that geometry is the study of shape and algebra is the study of generalizations of arithmetic operations.
"""

import sympy
import numpy as np
from itertools import product
from typing import Optional

from mathics.core.evaluators import apply_N
from mathics.core.evaluation import Evaluation
from mathics.builtin.base import Builtin, PostfixOperator, SympyFunction
from mathics.builtin.scoping import dynamic_scoping

from mathics.core.atoms import (
    String,
    Integer,
    Integer0,
    Integer1,
    Integer2,
    Integer3,
    Integer10,
    Number,
    Rational,
    Real,
    from_python,
)

from mathics.core.attributes import (
    constant,
    hold_all,
    listable,
    n_hold_all,
    protected,
    read_protected,
)

from mathics.core.convert import sympy_symbol_prefix, SympyExpression, from_sympy

from mathics.core.expression import Expression
from mathics.core.number import dps, machine_epsilon
from mathics.core.rules import Pattern

from mathics.core.symbols import (
    BaseExpression,
    Symbol,
    SymbolSequence,
    SymbolFalse,
    SymbolList,
    SymbolTrue,
)

from mathics.core.systemsymbols import (
    SymbolAutomatic,
    SymbolD,
    SymbolInfinity,
    SymbolLess,
    SymbolLessEqual,
    SymbolLog,
    SymbolNone,
    SymbolPlus,
    SymbolPower,
    SymbolRule,
    SymbolTimes,
    SymbolUndefined,
)


IntegerMinusOne = Integer(-1)
SymbolIntegrate = Symbol("Integrate")


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

    sympy_name = "Derivative"

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

    def apply(self, f, x, evaluation):
        "D[f_, x_?NotListQ]"
        x_pattern = Pattern.create(x)
        if f.is_free(x_pattern, evaluation):
            return Integer0
        elif f == x:
            return Integer1
        elif f.is_atom():  # Shouldn't happen
            1 / 0
            return
        # So, this is not an atom...

        head = f.get_head()
        if head is SymbolPlus:
            terms = [
                Expression("D", term, x)
                for term in f.leaves
                if not term.is_free(x_pattern, evaluation)
            ]
            if len(terms) == 0:
                return Integer0
            return Expression(SymbolPlus, *terms)
        elif head is SymbolTimes:
            terms = []
            for i, factor in enumerate(f.leaves):
                if factor.is_free(x_pattern, evaluation):
                    continue
                factors = [leaf for j, leaf in enumerate(f.leaves) if j != i]
                factors.append(Expression("D", factor, x))
                terms.append(Expression(SymbolTimes, *factors))
            if len(terms) != 0:
                return Expression(SymbolPlus, *terms)
            else:
                return Integer0
        elif head is SymbolPower and len(f.leaves) == 2:
            base, exp = f.leaves
            terms = []
            if not base.is_free(x_pattern, evaluation):
                terms.append(
                    Expression(
                        SymbolTimes,
                        exp,
                        Expression(
                            SymbolPower,
                            base,
                            Expression(SymbolPlus, exp, IntegerMinusOne),
                        ),
                        Expression("D", base, x),
                    )
                )
            if not exp.is_free(x_pattern, evaluation):
                if base.is_atom() and base.get_name() == "System`E":
                    terms.append(Expression(SymbolTimes, f, Expression("D", exp, x)))
                else:
                    terms.append(
                        Expression(
                            SymbolTimes,
                            f,
                            Expression("Log", base),
                            Expression("D", exp, x),
                        )
                    )

            if len(terms) == 0:
                return Integer0
            elif len(terms) == 1:
                return terms[0]
            else:
                return Expression(SymbolPlus, *terms)
        elif len(f.leaves) == 1:
            if f.leaves[0] == x:
                return Expression(
                    Expression(Expression("Derivative", Integer(1)), f.head), x
                )
            else:
                g = f.leaves[0]
                return Expression(
                    SymbolTimes,
                    Expression("D", Expression(f.head, g), g),
                    Expression("D", g, x),
                )
        else:  # many leaves

            def summand(leaf, index):
                result = Expression(
                    Expression(
                        Expression(
                            "Derivative",
                            *(
                                [Integer0] * (index)
                                + [Integer1]
                                + [Integer0] * (len(f.leaves) - index - 1)
                            ),
                        ),
                        f.head,
                    ),
                    *f.leaves,
                )
                if leaf.sameQ(x):
                    return result
                else:
                    return Expression("Times", result, Expression("D", leaf, x))

            result = [
                summand(leaf, index)
                for index, leaf in enumerate(f.leaves)
                if not leaf.is_free(x_pattern, evaluation)
            ]

            if len(result) == 1:
                return result[0]
            elif len(result) == 0:
                return Integer0
            else:
                return Expression("Plus", *result)

    def apply_wrong(self, expr, x, other, evaluation):
        "D[expr_, {x_, other___}]"

        arg = Expression(SymbolList, x, *other.get_sequence())
        evaluation.message("D", "dvar", arg)
        return Expression("D", expr, arg)


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

    operator = "'"
    precedence = 670
    attributes = n_hold_all

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

    default_formats = False

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

        if len(exprs) != 4 or not all(len(exp.leaves) >= 1 for exp in exprs[:3]):
            return

        if len(exprs[0].leaves) != len(exprs[2].leaves):
            return

        sym_args = [leaf.to_sympy() for leaf in exprs[0].leaves]
        if None in sym_args:
            return

        func = exprs[1].leaves[0]
        sym_func = sympy.Function(str(sympy_symbol_prefix + func.__str__()))(*sym_args)

        counts = [leaf.get_int_value() for leaf in exprs[2].leaves]
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
     = -Cos[x] - Cos[x] ^ 5 / 5 + 2 Cos[x] ^ 3 / 3

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
     = Integrate[Derivative[0, 1][f][u, x], {u, a[x], b[x]}] - f[a[x], x] a'[x] + f[b[x], x] b'[x]
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

    def prepare_sympy(self, leaves):
        if len(leaves) == 2:
            x = leaves[1]
            if x.has_form("List", 3):
                return [leaves[0]] + x.leaves
        return leaves

    def from_sympy(self, sympy_name, leaves):
        args = []
        for leaf in leaves[1:]:
            if leaf.has_form("List", 1):
                # {x} -> x
                args.append(leaf.leaves[0])
            else:
                args.append(leaf)
        new_leaves = [leaves[0]] + args
        return Expression(self.get_name(), *new_leaves)

    def apply(self, f, xs, evaluation, options):
        "Integrate[f_, xs__, OptionsPattern[]]"
        assuming = options["System`Assumptions"].evaluate(evaluation)
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
                x, a, b = x.leaves
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
            result = sympy.integrate(f_sympy, *vars)
        except sympy.PolynomialError:
            return
        except ValueError:
            # e.g. ValueError: can't raise polynomial to a negative power
            return
        except NotImplementedError:
            # e.g. NotImplementedError: Result depends on the sign of
            # -sign(_Mathics_User_j)*sign(_Mathics_User_w)
            return
        if prec is not None and isinstance(result, sympy.Integral):
            # TODO MaxExtaPrecision -> maxn
            result = result.evalf(dps(prec))
        else:
            result = from_sympy(result)
        # If the result is defined as a Piecewise expression,
        # use ConditionalExpression.
        # This does not work now because the form sympy returns the values
        if result.get_head_name() == "System`Piecewise":
            cases = result._leaves[0]._leaves
            if len(result._leaves) == 1:
                if cases[-1]._leaves[1].is_true():
                    default = cases[-1]._leaves[0]
                    cases = result._leaves[0]._leaves[:-1]
                else:
                    default = SymbolUndefined
            else:
                cases = result._leaves[0]._leaves
                default = result._leaves[1]
            if default.has_form("Integrate", None):
                if default._leaves[0] == f:
                    default = SymbolUndefined

            simplified_cases = []
            for case in cases:
                # TODO: if something like 0^n or 1/expr appears,
                # put the condition n!=0 or expr!=0 accordingly in the list of
                # conditions...
                cond = Expression("Simplify", case._leaves[1], assuming).evaluate(
                    evaluation
                )
                resif = Expression("Simplify", case._leaves[0], assuming).evaluate(
                    evaluation
                )
                if cond.is_true():
                    return resif
                if resif.has_form("ConditionalExpression", 2):
                    cond = Expression("And", resif._leaves[1], cond)
                    cond = Expression("Simplify", cond, assuming).evaluate(evaluation)
                    resif = resif._leaves[0]
                simplified_cases.append(Expression(SymbolList, resif, cond))
            cases = simplified_cases
            if default is SymbolUndefined and len(cases) == 1:
                cases = cases[0]
                result = Expression("ConditionalExpression", *(cases._leaves))
            else:
                result = Expression(result._head, cases, default)
        else:
            if result.get_head() is SymbolIntegrate:
                if result._leaves[0].evaluate(evaluation).sameQ(f):
                    # Sympy returned the same expression, so it can't be evaluated.
                    return
            result = Expression("Simplify", result, assuming)
        return result

    # TODO: The following methods are exactly the same that in NIntegrate. DRY it!
    @staticmethod
    def decompose_domain(interval, evaluation):
        if interval.has_form("System`Sequence", 1, None):
            intervals = []
            for leaf in interval.leaves:
                inner_interval = Integrate.decompose_domain(leaf, evaluation)
                if inner_interval:
                    intervals.append(inner_interval)
                else:
                    evaluation.message("ilim", leaf)
                    return None
            return intervals

        if interval.has_form("System`List", 3, None):
            intervals = []
            intvar = interval.leaves[0]
            if not isinstance(intvar, Symbol):
                evaluation.message("ilim", interval)
                return None
            boundaries = [a for a in interval.leaves[1:]]
            if any([b.get_head_name() == "System`Complex" for b in boundaries]):
                intvar = Expression(
                    "List", intvar, Expression("Blank", Symbol("Complex"))
                )
            for i in range(len(boundaries) - 1):
                intervals.append((boundaries[i], boundaries[i + 1]))
            if len(intervals) > 0:
                return (intvar, intervals)

        evaluation.message("ilim", interval)
        return None

    def apply_D(self, func, domain, var, evaluation, options):
        """D[%(name)s[func_, domain__, OptionsPattern[%(name)s]], var_Symbol]"""
        options = tuple(
            Expression(Symbol("Rule"), Symbol(key), options[key]) for key in options
        )
        # if the integration is along several variables, take the integration of the inner
        # variables as func.
        if domain._head is SymbolSequence:
            func = Expression(
                Symbol(self.get_name()), func, *(domain._leaves[:-1]), *options
            )
            domain = domain._leaves[-1]

        terms = []
        # Evaluates the derivative regarding the integrand:
        integrand = Expression(SymbolD, func, var).evaluate(evaluation)
        if integrand:
            # TODO: put back options is they are not the default...
            term = Expression(Symbol("Integrate"), integrand, domain)
            terms = [term]

        # Run over the intervals, and evaluate the derivative
        # regarding the integration limits.
        list_domain = self.decompose_domain(domain, evaluation)
        if not list_domain:
            return

        ivar, limits = list_domain
        for limit in limits:
            for k, lim in enumerate(limit):
                jac = Expression(SymbolD, lim, var)
                ev_jac = jac.evaluate(evaluation)
                if ev_jac:
                    jac = ev_jac
                if isinstance(jac, Number) and jac.is_zero:
                    continue
                f = func.replace_vars({ivar.get_name(): lim})
                if k == 1:
                    f = Expression(SymbolTimes, f, jac)
                else:
                    f = Expression(SymbolTimes, Integer(-1), f, jac)
                eval_f = f.evaluate(evaluation)
                if eval_f:
                    f = eval_f
                if isinstance(f, Number) and f.is_zero:
                    continue
                terms.append(f)

        if len(terms) == 0:
            return Integer0
        if len(terms) == 1:
            return terms[0]
        return Expression(SymbolPlus, *terms)


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

    sympy_name = "CRootOf"

    def apply(self, f, i, evaluation):
        "Root[f_, i_]"

        try:
            if not f.has_form("Function", 1):
                raise sympy.PolynomialError

            body = f.leaves[0]
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

            f = expr.leaves[0]

            if not f.has_form("Function", 1):
                return None

            body = f.leaves[0].replace_slots([f, Symbol("_1")], None)
            poly = body.to_sympy(**kwargs)

            i = expr.leaves[1].get_int_value(**kwargs) - 1

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
     = {{x -> 0, y -> 0}, {x -> 1, y -> 1}, {x -> -1 / 2 + I / 2 Sqrt[3], y -> -1 / 2 - I / 2 Sqrt[3]}, {x -> (1 - I Sqrt[3]) ^ 2 / 4, y -> -1 / 2 + I / 2 Sqrt[3]}}
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
            vars = vars.leaves
        else:
            vars = [vars]
        for var in vars:
            if (
                (var.is_atom() and not var.is_symbol())
                or head_name in ("System`Plus", "System`Times", "System`Power")  # noqa
                or constant & var.get_attributes(evaluation.definitions)
            ):

                evaluation.message("Solve", "ivar", vars_original)
                return
        eqs_original = eqs
        if eqs.get_head_name() in ("System`List", "System`And"):
            eqs = eqs.leaves
        else:
            eqs = [eqs]
        sympy_eqs = []
        sympy_denoms = []
        for eq in eqs:
            if eq is SymbolTrue:
                pass
            elif eq is SymbolFalse:
                return Expression(SymbolList)
            elif not eq.has_form("Equal", 2):
                return evaluation.message("Solve", "eqf", eqs_original)
            else:
                left, right = eq.leaves
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
                return Expression(SymbolList, Expression(SymbolList))
            if result == [None]:
                return Expression(SymbolList)
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

            return Expression(
                "List",
                *(
                    Expression(
                        "List",
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
        <dd>is the set of integer numbers.
    </dl>

    Limit a solution to integer numbers:
    >> Solve[-4 - 4 x + x^4 + x^5 == 0, x, Integers]
     = {{x -> -1}}
    >> Solve[x^4 == 4, x, Integers]
     = {}
    """


class Reals(Builtin):
    """
    <dl>
    <dt>'Reals'
        <dd>is the set of real numbers.
    </dl>

    Limit a solution to real numbers:
    >> Solve[x^3 == 1, x, Reals]
     = {{x -> 1}}
    """


class Complexes(Builtin):
    """
    <dl>
    <dt>'Complexes'
        <dd>is the set of complex numbers.
    </dl>
    """


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

    options = {
        "Direction": "1",
    }

    messages = {
        "ldir": "Value of Direction -> `1` should be -1 or 1.",
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

    options = {
        "Trials": "5",
    }

    messages = {
        "dltrials": "The value of Trials should be a positive integer",
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


def find_root_secant(f, x0, x, opts, evaluation) -> (Number, bool):
    region = opts.get("$$Region", None)
    if not type(region) is list:
        if x0.is_zero:
            region = (Real(-1), Real(1))
        else:
            xmax = 2 * x0.to_python()
            xmin = -2 * x0.to_python()
            if xmin > xmax:
                region = (Real(xmax), Real(xmin))
            else:
                region = (Real(xmin), Real(xmax))

    maxit = opts["System`MaxIterations"]
    x_name = x.get_name()
    if maxit is SymbolAutomatic:
        maxit = 100
    else:
        maxit = maxit.evaluate(evaluation).get_int_value()

    x0 = from_python(region[0])
    x1 = from_python(region[1])
    f0 = dynamic_scoping(lambda ev: f.evaluate(evaluation), {x_name: x0}, evaluation)
    f1 = dynamic_scoping(lambda ev: f.evaluate(evaluation), {x_name: x1}, evaluation)
    if not isinstance(f0, Number):
        return x0, False
    if not isinstance(f1, Number):
        return x0, False
    f0 = f0.to_python(n_evaluation=True)
    f1 = f1.to_python(n_evaluation=True)
    count = 0
    while count < maxit:
        if f0 == f1:
            x1 = Expression(
                "Plus",
                x0,
                Expression(
                    "Times",
                    Real(0.75),
                    Expression("Plus", x1, Expression("Times", Integer(-1), x0)),
                ),
            )
            x1 = x1.evaluate(evaluation)
            f1 = dynamic_scoping(
                lambda ev: f.evaluate(evaluation), {x_name: x1}, evaluation
            )
            if not isinstance(f1, Number):
                return x0, False
            f1 = f1.to_python(n_evaluation=True)
            continue

        inv_deltaf = from_python(1.0 / (f1 - f0))
        num = Expression(
            "Plus",
            Expression("Times", x0, f1),
            Expression("Times", x1, f0, Integer(-1)),
        )
        x2 = Expression("Times", num, inv_deltaf)
        x2 = x2.evaluate(evaluation)
        f2 = dynamic_scoping(
            lambda ev: f.evaluate(evaluation), {x_name: x2}, evaluation
        )
        if not isinstance(f2, Number):
            return x0, False
        f2 = f2.to_python(n_evaluation=True)
        f1, f0 = f2, f1
        x1, x0 = x2, x1
        if x1 == x0 or abs(f2) == 0:
            break
        count = count + 1
    else:
        evaluation.message("FindRoot", "maxiter")
        return x0, False
    return x0, True


def find_root_newton(f, x0, x, opts, evaluation) -> (Number, bool):
    """
    Look for a root of a f: R->R using the Newton's method.
    """
    absf = abs(f)
    df = opts["System`Jacobian"]
    x_name = x.get_name()

    acc_goal, prec_goal, maxit_opt = get_accuracy_prec_and_maxit(opts, evaluation)
    maxit = maxit_opt.get_int_value() if maxit_opt else 100
    step_monitor = opts.get("System`StepMonitor", None)
    if step_monitor is SymbolNone:
        step_monitor = None
    evaluation_monitor = opts.get("System`EvaluationMonitor", None)
    if evaluation_monitor is SymbolNone:
        evaluation_monitor = None

    def decreasing(val1, val2):
        """
        Check if val2 has a smaller absolute value than val1
        """
        if not (val1.is_numeric() and val2.is_numeric()):
            return False
        if val2.is_zero:
            return True
        res = apply_N(Expression(SymbolLog, abs(val2 / val1)), evaluation)
        if not res.is_numeric():
            return False
        return res.to_python() < 0

    def new_seed():
        """
        looks for a new starting point, based on how close we are from the target.
        """
        x1 = apply_N(Integer2 * x0, evaluation)
        x2 = apply_N(x0 / Integer3, evaluation)
        x3 = apply_N(x0 - minus / Integer2, evaluation)
        x4 = apply_N(x0 + minus / Integer3, evaluation)
        absf1 = apply_N(absf.replace_vars({x_name: x1}), evaluation)
        absf2 = apply_N(absf.replace_vars({x_name: x2}), evaluation)
        absf3 = apply_N(absf.replace_vars({x_name: x3}), evaluation)
        absf4 = apply_N(absf.replace_vars({x_name: x4}), evaluation)
        if decreasing(absf1, absf2):
            x1, absf1 = x2, absf2
        if decreasing(absf1, absf3):
            x1, absf1 = x3, absf3
        if decreasing(absf1, absf4):
            x1, absf1 = x4, absf4
        return x1, absf1

    def sub(evaluation):
        d_value = apply_N(df, evaluation)
        if d_value == Integer(0):
            return None
        result = apply_N(f / d_value, evaluation)
        if evaluation_monitor:
            dynamic_scoping(
                lambda ev: evaluation_monitor.evaluate(ev), {x_name: x0}, evaluation
            )
        return result

    currval = absf.replace_vars({x_name: x0}).evaluate(evaluation)
    count = 0
    while count < maxit:
        if step_monitor:
            dynamic_scoping(
                lambda ev: step_monitor.evaluate(ev), {x_name: x0}, evaluation
            )
        minus = dynamic_scoping(sub, {x_name: x0}, evaluation)
        if minus is None:
            evaluation.message("FindRoot", "dsing", x, x0)
            return x0, False
        x1 = Expression("Plus", x0, Expression("Times", Integer(-1), minus)).evaluate(
            evaluation
        )
        if not isinstance(x1, Number):
            evaluation.message("FindRoot", "nnum", x, x0)
            return x0, False

        # Check convergence:
        new_currval = absf.replace_vars({x_name: x1}).evaluate(evaluation)
        if is_zero(new_currval, acc_goal, prec_goal, evaluation):
            return x1, True

        # This step tries to ensure that the new step goes forward to the convergence.
        # If not, tries to restart in a another point closer to x0 than x1.
        if decreasing(new_currval, currval):
            x0, currval = new_seed()
            count = count + 1
            continue
        else:
            currval = new_currval
            x0 = apply_N(x1, evaluation)
            # N required due to bug in sympy arithmetic
            count += 1
    else:
        evaluation.message("FindRoot", "maxiter")
    return x0, True


def find_minimum_newton1d(f, x0, x, opts, evaluation) -> (Number, bool):
    is_find_maximum = opts.get("_isfindmaximum", False)
    symbol_name = "FindMaximum" if is_find_maximum else "FindMinimum"
    if is_find_maximum:
        f = -f
        # TODO: revert jacobian if given...

    x_name = x.name
    maxit = opts["System`MaxIterations"]
    step_monitor = opts.get("System`StepMonitor", None)
    if step_monitor is SymbolNone:
        step_monitor = None
    evaluation_monitor = opts.get("System`EvaluationMonitor", None)
    if evaluation_monitor is SymbolNone:
        evaluation_monitor = None

    acc_goal, prec_goal, maxit_opt = get_accuracy_prec_and_maxit(opts, evaluation)
    maxit = maxit_opt.get_int_value() if maxit_opt else 100
    curr_val = apply_N(f.replace_vars({x_name: x0}), evaluation)

    # build the quadratic form:
    eps = determine_epsilon(x0, opts, evaluation)
    if not isinstance(curr_val, Number):
        evaluation.message(symbol_name, "nnum", x, x0)
        if is_find_maximum:
            return -x0, False
        else:
            return x0, False
    d1 = dynamic_scoping(
        lambda ev: Expression("D", f, x).evaluate(ev), {x_name: None}, evaluation
    )
    val_d1 = apply_N(d1.replace_vars({x_name: x0}), evaluation)
    if not isinstance(val_d1, Number):
        d1 = None
        d2 = None
        f2val = apply_N(f.replace_vars({x_name: x0 + eps}), evaluation)
        f1val = apply_N(f.replace_vars({x_name: x0 - eps}), evaluation)
        val_d1 = apply_N((f2val - f1val) / (Integer2 * eps), evaluation)
        val_d2 = apply_N(
            (f2val + f1val - Integer2 * curr_val) / (eps ** Integer2), evaluation
        )
    else:
        d2 = dynamic_scoping(
            lambda ev: Expression("D", d1, x).evaluate(ev), {x_name: None}, evaluation
        )
        val_d2 = apply_N(d2.replace_vars({x_name: x0}), evaluation)
        if not isinstance(val_d2, Number):
            d2 = None
            df2val = apply_N(d1.replace_vars({x_name: x0 + eps}), evaluation)
            df1val = apply_N(d1.replace_vars({x_name: x0 - eps}), evaluation)
            val_d2 = (df2val - df1val) / (Integer2 * eps)

    def reset_values(x0):
        x_try = [
            apply_N(x0 / Integer3, evaluation),
            apply_N(x0 * Integer2, evaluation),
            apply_N(x0 - offset / Integer2, evaluation),
        ]
        vals = [(u, apply_N(f.replace_vars({x_name: u}), evaluation)) for u in x_try]
        vals = [v for v in vals if isinstance(v[1], Number)]
        v0 = vals[0]
        for v in vals:
            if Expression(SymbolLess, v[1], v0[1]).evaluate(evaluation) is SymbolTrue:
                v0 = v
        return v0

    def reevaluate_coeffs():
        """reevaluates val_d1 and val_d2"""
        if d1:
            val_d1 = apply_N(d1.replace_vars({x_name: x0}), evaluation)
            if d2:
                val_d2 = apply_N(d2.replace_vars({x_name: x0}), evaluation)
            else:
                df2val = apply_N(d1.replace_vars({x_name: x0 + eps}), evaluation)
                df1val = apply_N(d1.replace_vars({x_name: x0 - eps}), evaluation)
                val_d2 = (df2val - df1val) / (Integer2 * eps)
        else:
            f2val = apply_N(f.replace_vars({x_name: x0 + eps}), evaluation)
            f1val = apply_N(f.replace_vars({x_name: x0 - eps}), evaluation)
            val_d1 = apply_N((f2val - f1val) / (Integer2 * eps), evaluation)
            val_d2 = apply_N(
                (f2val + f1val - Integer2 * curr_val) / (eps ** Integer2), evaluation
            )
        return (val_d1, val_d2)

    # Main loop
    count = 0

    while count < maxit:
        if step_monitor:
            step_monitor.replace_vars({x_name: x0}).evaluate(evaluation)

        if val_d1.is_zero:
            if is_find_maximum:
                evaluation.message(
                    symbol_name, "fmgz", String("maximum"), String("minimum")
                )
            else:
                evaluation.message(
                    symbol_name, "fmgz", String("minimum"), String("maximum")
                )

            if is_find_maximum:
                return (x0, -curr_val), True
            else:
                return (x0, curr_val), True
        if val_d2.is_zero:
            val_d2 = Integer1

        offset = apply_N(val_d1 / abs(val_d2), evaluation)
        x1 = apply_N(x0 - offset, evaluation)
        new_val = apply_N(f.replace_vars({x_name: x1}), evaluation)
        if (
            Expression(SymbolLessEqual, new_val, curr_val).evaluate(evaluation)
            is SymbolTrue
        ):
            if is_zero(offset, acc_goal, prec_goal, evaluation):
                if is_find_maximum:
                    return (x1, -curr_val), True
                else:
                    return (x1, curr_val), True
            x0 = x1
            curr_val = new_val
        else:
            if is_zero(offset / Integer2, acc_goal, prec_goal, evaluation):
                if is_find_maximum:
                    return (x0, -curr_val), True
                else:
                    return (x0, curr_val), True
            x0, curr_val = reset_values(x0)
        val_d1, val_d2 = reevaluate_coeffs()
        count = count + 1
    else:
        evaluation.message(symbol_name, "maxiter")
    if is_find_maximum:
        return (x0, -curr_val), False
    else:
        return (x0, curr_val), False


class _BaseFinder(Builtin):
    """
    This class is the basis class for FindRoot, FindMinimum and FindMaximum.
    """

    options = {
        "MaxIterations": "100",
        "Method": "Automatic",
        "AccuracyGoal": "Automatic",
        "PrecisionGoal": "Automatic",
        "StepMonitor": "None",
        "EvaluationMonitor": "None",
        "Jacobian": "Automatic",
    }

    attributes = hold_all | protected

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

    methods = {}

    def apply(self, f, x, x0, evaluation, options):
        "%(name)s[f_, {x_, x0_}, OptionsPattern[]]"
        # This is needed to get the right messages
        options["_isfindmaximum"] = self.__class__ is FindMaximum
        # First, determine x0 and x

        x0 = apply_N(x0, evaluation)
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
                "Plus", f.leaves[0], Expression("Times", Integer(-1), f.leaves[1])
            )
            f = dynamic_scoping(lambda ev: f.evaluate(ev), {x_name: None}, evaluation)

        # Determine the method
        method = options["System`Method"]
        if isinstance(method, Expression):
            if method.get_head() is SymbolList:
                method = method._leaves[0]
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
                return Expression("D", f, x).evaluate(evaluation)

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
            return Expression(
                SymbolList,
                x0[1],
                Expression(SymbolList, Expression(SymbolRule, x, x0[0])),
            )
        else:
            return Expression(SymbolList, Expression(SymbolRule, x, x0))

    def apply_with_x_tuple(self, f, xtuple, evaluation, options):
        "%(name)s[f_, xtuple_, OptionsPattern[]]"
        f_val = f.evaluate(evaluation)

        if f_val.has_form("Equal", 2):
            f = Expression("Plus", f_val.leaves[0], f_val.leaves[1])

        xtuple_value = xtuple.evaluate(evaluation)
        if xtuple_value.has_form("List", None):
            nleaves = len(xtuple_value.leaves)
            if nleaves == 2:
                x, x0 = xtuple.evaluate(evaluation).leaves
            elif nleaves == 3:
                x, x0, x1 = xtuple.evaluate(evaluation).leaves
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

    methods = {
        "Newton": find_root_newton,
        "Automatic": find_root_newton,
        "Secant": find_root_secant,
    }


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
    >> phi[x_?NumberQ]:=NIntegrate[u,{u,0,x}];
    >> FindMinimum[phi[x]-x,{x,1.2}]
     = {-0.5, {x -> 1.00001}}
    >> Clear[phi];
    For a not so well behaving function, the result can be less accurate:
    >> FindMinimum[Exp[-1/x^2]+1., {x,1.2}, MaxIterations->300]
     : The maximum number of iterations was exceeded. The result might be inaccurate.
     =  FindMinimum[Exp[-1 / x ^ 2] + 1., {x, 1.2}, MaxIterations -> 300]
    """

    methods = {
        "Automatic": find_minimum_newton1d,
        "Newton": find_minimum_newton1d,
    }


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
    >> phi[x_?NumberQ]:=NIntegrate[u,{u,0,x}];
    >> FindMaximum[-phi[x]+x,{x,1.2}]
     = {0.5, {x -> 1.00001}}
    >> Clear[phi];
    For a not so well behaving function, the result can be less accurate:
    >> FindMaximum[-Exp[-1/x^2]+1., {x,1.2}, MaxIterations->300]
     : The maximum number of iterations was exceeded. The result might be inaccurate.
     = FindMaximum[-Exp[-1 / x ^ 2] + 1., {x, 1.2}, MaxIterations -> 300]
    """

    methods = {
        "Automatic": find_minimum_newton1d,
        "Newton": find_minimum_newton1d,
    }


class O_(Builtin):
    """
    <dl>
      <dt>'O[$x$]^n'
      <dd> Represents a term of order $x^n$.
      <dd> O[x]^n is generated to represent omitted higher order terms in power series.
    </dl>

    >> Series[1/(1-x),{x,0,2}]
     = 1 + x + x ^ 2 + O[x] ^ 3

    """

    name = "O"
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
     = SeriesData[x, 0, {1,1,Rational[1, 2]}, 0, 2, 1]
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
    """

    summary_text = "power series and asymptotic expansions"

    def apply_series(self, f, x, x0, n, evaluation):
        """Series[f_, {x_Symbol, x0_, n_Integer}]"""
        # TODO:
        # - Asymptotic series
        # - Series of compositions
        vars = {
            x.get_name(): x0,
        }

        data = [f.replace_vars(vars)]
        df = f
        for i in range(n.get_int_value()):
            df = Expression("D", df, x).evaluate(evaluation)
            newcoeff = df.replace_vars(vars)
            factorial = Expression("Factorial", Integer(i + 1))
            newcoeff = Expression(
                SymbolTimes,
                Expression(SymbolPower, factorial, IntegerMinusOne),
                newcoeff,
            ).evaluate(evaluation)
            data.append(newcoeff)
        data = Expression(SymbolList, *data).evaluate(evaluation)
        return Expression(Symbol("SeriesData"), x, x0, data, Integer0, n, Integer1)


class SeriesData(Builtin):
    """
    <dl>
    <dt>'SeriesData[...]'
    <dd>Represents a series expansion
    </dl>

    TODO:
    - Implement sum, product and composition of series
    """

    summary_text = "Mathics representation Power series"

    def apply_normal(self, x, x0, data, nummin, nummax, den, evaluation):
        """Normal[SeriesData[x_, x0_, data_, nummin_, nummax_, den_]]"""
        return Expression(
            SymbolPlus,
            *[a * (x - x0) ** ((nummin + k) / den) for k, a in enumerate(data.leaves)],
        )

    def apply_makeboxes(self, x, x0, data, nmin, nmax, den, form, evaluation):
        """MakeBoxes[SeriesData[x_, x0_, data_List, nmin_Integer, nmax_Integer, den_Integer],
        form:StandardForm|TraditionalForm|OutputForm|InputForm]"""

        form = form.get_name()
        if x0.is_zero:
            variable = x
        else:
            variable = Expression(
                SymbolPlus, x, Expression(SymbolTimes, IntegerMinusOne, x0)
            )
        den = den.get_int_value()
        nmin = nmin.get_int_value()
        nmax = nmax.get_int_value() + 1
        if den != 1:
            powers = [Rational(i, den) for i in range(nmin, nmax)]
            powers = powers + [Rational(nmax, den)]
        else:
            powers = [Integer(i) for i in range(nmin, nmax)]
            powers = powers + [Integer(nmax)]

        expansion = []
        for i, leaf in enumerate(data.leaves):
            if leaf.is_numeric(evaluation) and leaf.is_zero:
                continue
            if powers[i].is_zero:
                expansion.append(leaf)
                continue
            if powers[i] == Integer1:
                if leaf == Integer1:
                    term = variable
                else:
                    term = Expression(SymbolTimes, leaf, variable)
            else:
                if leaf == Integer1:
                    term = Expression(SymbolPower, variable, powers[i])
                else:
                    term = Expression(
                        SymbolTimes, leaf, Expression(SymbolPower, variable, powers[i])
                    )
            expansion.append(term)
        expansion = expansion + [
            Expression(SymbolPower, Expression("O", variable), powers[-1])
        ]
        # expansion = [ex.format(form) for ex in expansion]
        expansion = Expression(SymbolPlus, *expansion)
        return expansion.format(evaluation, form)


def _scipy_interface(integrator, options_map, mandatory=None, adapt_func=None):
    """
    This function provides a proxy for scipy.integrate
    functions, adapting the parameters.
    """

    def _scipy_proxy_func_filter(fun, a, b, **opts):
        native_opts = {}
        if mandatory:
            native_opts.update(mandatory)
        for opt, val in opts.items():
            native_opt = options_map.get(opt, None)
            if native_opt:
                if native_opt[1]:
                    val = native_opt[1](val)
                native_opts[native_opt[0]] = val
        return adapt_func(integrator(fun, a, b, **native_opts))

    def _scipy_proxy_func(fun, a, b, **opts):
        native_opts = {}
        if mandatory:
            native_opts.update(mandatory)
        for opt, val in opts.items():
            native_opt = options_map.get(opt, None)
            if native_opt:
                if native_opt[1]:
                    val = native_opt[1](val)
                native_opts[native_opt[0]] = val
        return integrator(fun, a, b, **native_opts)

    return _scipy_proxy_func_filter if adapt_func else _scipy_proxy_func


def _internal_adaptative_simpsons_rule(f, a, b, **opts):
    """
    1D adaptative Simpson's rule integrator
    Adapted from https://en.wikipedia.org/wiki/Adaptive_Simpson%27s_method
       by @mmatera

    TODO: handle weak divergences
    """
    wsr = 1.0 / 6.0

    tol = opts.get("tol")
    if not tol:
        tol = 1.0e-10

    maxrec = opts.get("maxrec")
    if not maxrec:
        maxrec = 150

    def _quad_simpsons_mem(f, a, fa, b, fb):
        """Evaluates the Simpson's Rule, also returning m and f(m) to reuse"""
        m = 0.5 * (a + b)
        try:
            fm = f(m)
        except ZeroDivisionError:
            fm = None

        if fm is None or np.isinf(fm):
            m = m + 1e-10
            fm = f(m)
        return (m, fm, wsr * abs(b - a) * (fa + 4.0 * fm + fb))

    def _quad_asr(f, a, fa, b, fb, eps, whole, m, fm, maxrec):
        """
        Efficient recursive implementation of adaptive Simpson's rule.
        Function values at the start, middle, end of the intervals
        are retained.
        """
        maxrec = maxrec - 1
        try:
            left = _quad_simpsons_mem(f, a, fa, m, fm)
            lm, flm, left = left
            right = _quad_simpsons_mem(f, m, fm, b, fb)
            rm, frm, right = right

            delta = left + right - whole
            err = abs(delta)
            if err <= 15 * eps or maxrec == 0:
                return (left + right + delta / 15, err)
            left = _quad_asr(f, a, fa, m, fm, 0.5 * eps, left, lm, flm, maxrec)
            right = _quad_asr(f, m, fm, b, fb, 0.5 * eps, right, rm, frm, maxrec)
            return (left[0] + right[0], left[1] + right[1])
        except Exception:
            raise

    def ensure_evaluation(f, x):
        try:
            val = f(x)
        except ZeroDivisionError:
            return None
        try:
            if np.isinf(val):
                return None
        except TypeError:
            return None
        return val

    invert_interval = False
    if a > b:
        b, a, invert_interval = a, b, True

    fa, fb = ensure_evaluation(f, a), ensure_evaluation(f, b)
    if fa is None:
        x = 10.0 * machine_epsilon if a == 0 else a * (1.0 + 10.0 * machine_epsilon)
        fa = ensure_evaluation(f, x)
        if fa is None:
            raise Exception(f"Function undefined around {a}. Cannot integrate")
    if fb is None:
        x = -10.0 * machine_epsilon if b == 0 else b * (1.0 - 10.0 * machine_epsilon)
        fb = ensure_evaluation(f, x)
        if fb is None:
            raise Exception(f"Function undefined around {b}. Cannot integrate")

    m, fm, whole = _quad_simpsons_mem(f, a, fa, b, fb)
    if invert_interval:
        return -_quad_asr(f, a, fa, b, fb, tol, whole, m, fm, maxrec)
    else:
        return _quad_asr(f, a, fa, b, fb, tol, whole, m, fm, maxrec)


def _fubini(func, ranges, **opts):
    if not ranges:
        return 0.0
    a, b = ranges[0]
    integrator = opts["integrator"]
    tol = opts.get("tol")
    if tol is None:
        opts["tol"] = 1.0e-10
        tol = 1.0e-10

    if len(ranges) > 1:

        def subintegral(*u):
            def ff(*z):
                return func(*(u + z))

            val = _fubini(ff, ranges[1:], **opts)[0]
            return val

        opts["tol"] = 4.0 * tol
        val = integrator(subintegral, a, b, **opts)
        return val
    else:
        val = integrator(func, a, b, **opts)
        return val


class NIntegrate(Builtin):
    """
    <dl>
       <dt>'NIntegrate[$expr$, $interval$]'
       <dd>returns a numeric approximation to the definite integral of $expr$ with limits $interval$ and with a precision of $prec$ digits.

        <dt>'NIntegrate[$expr$, $interval1$, $interval2$, ...]'
        <dd>returns a numeric approximation to the multiple integral of $expr$ with limits $interval1$, $interval2$ and with a precision of $prec$ digits.
    </dl>

    >> NIntegrate[Exp[-x],{x,0,Infinity},Tolerance->1*^-6]
     = 1.
    >> NIntegrate[Exp[x],{x,-Infinity, 0},Tolerance->1*^-6]
     = 1.
    >> NIntegrate[Exp[-x^2/2.],{x,-Infinity, Infinity},Tolerance->1*^-6]
     = 2.50663

    >> Table[1./NIntegrate[x^k,{x,0,1},Tolerance->1*^-6], {k,0,6}]
     : The specified method failed to return a number. Falling back into the internal evaluator.
     = {1., 2., 3., 4., 5., 6., 7.}

    >> NIntegrate[1 / z, {z, -1 - I, 1 - I, 1 + I, -1 + I, -1 - I}, Tolerance->1.*^-4]
     : Integration over a complex domain is not implemented yet
     = NIntegrate[1 / z, {z, -1 - I, 1 - I, 1 + I, -1 + I, -1 - I}, Tolerance -> 0.0001]
     ## = 6.2832 I

    Integrate singularities with weak divergences:
    >> Table[ NIntegrate[x^(1./k-1.), {x,0,1.}, Tolerance->1*^-6], {k,1,7.} ]
     = {1., 2., 3., 4., 5., 6., 7.}

    Mutiple Integrals :
    >> NIntegrate[x * y,{x, 0, 1}, {y, 0, 1}]
     = 0.25

    """

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

    options = {
        "Method": '"Automatic"',
        "Tolerance": "1*^-10",
        "Accuracy": "1*^-10",
        "MaxRecursion": "10",
    }

    methods = {
        "Automatic": (None, False),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.methods["Internal"] = (_internal_adaptative_simpsons_rule, False)
        try:
            from scipy.integrate import romberg, quad, nquad

            self.methods["NQuadrature"] = (
                _scipy_interface(
                    nquad, {}, {"full_output": 1}, lambda res: (res[0], res[1])
                ),
                True,
            )
            self.methods["Quadrature"] = (
                _scipy_interface(
                    quad,
                    {
                        "tol": ("epsabs", None),
                        "maxrec": ("limit", lambda maxrec: int(2 ** maxrec)),
                    },
                    {"full_output": 1},
                    lambda res: (res[0], res[1]),
                ),
                False,
            )
            self.methods["Romberg"] = (
                _scipy_interface(
                    romberg,
                    {"tol": ("tol", None), "maxrec": ("divmax", None)},
                    None,
                    lambda x: (x, np.nan),
                ),
                False,
            )
            self.methods["Automatic"] = self.methods["Quadrature"]
        except Exception:
            self.methods["Automatic"] = self.methods["Internal"]
            self.methods["Simpson"] = self.methods["Internal"]

        self.messages["bdmtd"] = (
            "The Method option should be a "
            + "built-in method name in {`"
            + "`, `".join(list(self.methods))
            + "`}. Using `Automatic`"
        )

    @staticmethod
    def decompose_domain(interval, evaluation):
        if interval.has_form("System`Sequence", 1, None):
            intervals = []
            for leaf in interval.leaves:
                inner_interval = NIntegrate.decompose_domain(leaf, evaluation)
                if inner_interval:
                    intervals.append(inner_interval)
                else:
                    evaluation.message("ilim", leaf)
                    return None
            return intervals

        if interval.has_form("System`List", 3, None):
            intervals = []
            intvar = interval.leaves[0]
            if not isinstance(intvar, Symbol):
                evaluation.message("ilim", interval)
                return None
            boundaries = [a for a in interval.leaves[1:]]
            if any([b.get_head_name() == "System`Complex" for b in boundaries]):
                intvar = Expression(
                    "List", intvar, Expression("Blank", Symbol("Complex"))
                )
            for i in range(len(boundaries) - 1):
                intervals.append((boundaries[i], boundaries[i + 1]))
            if len(intervals) > 0:
                return (intvar, intervals)

        evaluation.message("ilim", interval)
        return None

    def apply_with_func_domain(self, func, domain, evaluation, options):
        "%(name)s[func_, domain__, OptionsPattern[%(name)s]]"
        if func.is_numeric() and func.is_zero:
            return Integer0
        method = options["System`Method"].evaluate(evaluation)
        method_options = {}
        if method.has_form("System`List", 2):
            method = method.leaves[0]
            method_options.update(method.leaves[1].get_option_values())
        if isinstance(method, String):
            method = method.value
        elif isinstance(method, Symbol):
            method = method.get_name()
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

        domain = self.decompose_domain(domain, evaluation)
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

        intvars = Expression(SymbolList, *coords)
        integrand = Expression("Compile", intvars, func).evaluate(evaluation)

        if len(integrand.leaves) >= 3:
            integrand = integrand.leaves[2].cfunc
        else:
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
                            (np.arctanh, lambda u: 1.0 / (1.0 - u ** 2))
                        )
                    else:
                        if not b.is_numeric(evaluation):
                            evaluation.message("nlim", coords[i], b)
                            return
                        z = a.leaves[0].value
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
                    z = b.leaves[0].value
                    subdomain2.append([machine_epsilon, 1.0])
                    coordtransform.append(
                        (lambda u: a - z + z / u, lambda u: z * u ** (-2.0))
                    )
                elif a.is_numeric(evaluation) and b.is_numeric(evaluation):
                    a = apply_N(a, evaluation).value
                    b = apply_N(b, evaluation).value
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
                    print("val_jac:", val_jac)
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
        options = tuple(
            Expression(Symbol("Rule"), Symbol(key), options[key]) for key in options
        )
        # if the integration is along several variables, take the integration of the inner
        # variables as func.
        if domain._head is SymbolSequence:
            func = Expression(
                Symbol(self.get_name()), func, *(domain._leaves[:-1]), *options
            )
            domain = domain._leaves[-1]

        terms = []
        # Evaluates the derivative regarding the integrand:
        integrand = Expression(SymbolD, func, var).evaluate(evaluation)
        if integrand:
            term = Expression(Symbol("NIntegrate"), integrand, domain, *options)
            terms = [term]

        # Run over the intervals, and evaluate the derivative
        # regarding the integration limits.
        list_domain = self.decompose_domain(domain, evaluation)
        if not list_domain:
            return

        ivar, limits = list_domain
        for limit in limits:
            for k, lim in enumerate(limit):
                jac = Expression(SymbolD, lim, var)
                ev_jac = jac.evaluate(evaluation)
                if ev_jac:
                    jac = ev_jac
                if isinstance(jac, Number) and jac.is_zero:
                    continue
                f = func.replace_vars({ivar.get_name(): lim})
                if k == 1:
                    f = Expression(SymbolTimes, f, jac)
                else:
                    f = Expression(SymbolTimes, Integer(-1), f, jac)
                eval_f = f.evaluate(evaluation)
                if eval_f:
                    f = eval_f
                if isinstance(f, Number) and f.is_zero:
                    continue
                terms.append(f)

        if len(terms) == 0:
            return Integer0
        if len(terms) == 1:
            return terms[0]
        return Expression(SymbolPlus, *terms)


# Auxiliary routines. Maybe should be moved to another module.


def is_zero(
    val: BaseExpression,
    acc_goal: Optional[Real],
    prec_goal: Optional[Real],
    evaluation: Evaluation,
) -> bool:
    """
    Check if val is zero upto the precision and accuracy goals
    """
    if not isinstance(val, Number):
        val = apply_N(val, evaluation)
    if not isinstance(val, Number):
        return False
    if val.is_zero:
        return True
    if not (acc_goal or prec_goal):
        return False

    eps_expr: BaseExpression = Integer10 ** (-prec_goal) if prec_goal else Integer0
    if acc_goal:
        eps_expr = eps_expr + Integer10 ** (-acc_goal) / abs(val)
    threeshold_expr = Expression(SymbolLog, eps_expr)
    threeshold: Real = apply_N(threeshold_expr, evaluation)
    return threeshold.to_python() > 0


def determine_epsilon(x0: Real, options: dict, evaluation: Evaluation) -> Real:
    """Determine epsilon  from a reference value, and from the accuracy and the precision goals"""
    acc_goal, prec_goal, maxit = get_accuracy_prec_and_maxit(options, evaluation)
    eps: Real = Real(1e-10)
    if not (acc_goal or prec_goal):
        return eps
    eps = apply_N(
        abs(x0) * Integer10 ** (-prec_goal) if prec_goal else Integer0, evaluation
    )
    if acc_goal:
        eps = apply_N(Integer10 ** (-acc_goal) + eps, evaluation)
    return eps


def get_accuracy_prec_and_maxit(opts: dict, evaluation: "Evaluation"):
    """
    Looks at an opts dictionary and tries to determine the numeric values of
    Accuracy and Precision goals. If not available, returns None.
    """
    # comment @mmatera: I fix the default value for Accuracy
    # and Precision goals to 12 because it ensures that
    # the results of the tests coincides with WMA upto
    # 6 digits. In any case, probably the default value should be
    # determined inside the methods that implements the specific
    # solvers.

    def to_real_or_none(value) -> Optional[Real]:
        if value:
            value = apply_N(value, evaluation)
        if value is SymbolAutomatic:
            value = Real(12.0)
        elif value is SymbolInfinity:
            value = None
        elif not isinstance(value, Number):
            value = None
        return value

    def to_integer_or_none(value) -> Optional[Integer]:
        if value:
            value = apply_N(value, evaluation)
        if value is SymbolAutomatic:
            value = Integer(100)
        elif value is SymbolInfinity:
            value = None
        elif not isinstance(value, Number):
            value = None
        return value

    acc_goal = opts.get("System`AccuracyGoal", None)
    acc_goal = to_real_or_none(acc_goal)
    prec_goal = opts.get("System`PrecisionGoal", None)
    prec_goal = to_real_or_none(prec_goal)
    max_it = opts.get("System`MaxIteration")
    max_it = to_integer_or_none(max_it)
    return acc_goal, prec_goal, max_it
