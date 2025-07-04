# -*- coding: utf-8 -*-
"""
Algebraic Transformations

There are a number of built-in functions that perform:

<ul>
  <li>Structural Operations on Polynomials
  <li>Finding the Structure of a Polynomial
  <li>Structural Operations on Rational Expressions
  <li>Polynomials over Algebraic Number Fields
  <li>Simplification with or without Assumptions
</ul>
"""

from typing import Optional, Tuple, Union

import sympy

import mathics.eval.tracing as tracing
from mathics.builtin.options import options_to_rules
from mathics.builtin.scoping import dynamic_scoping
from mathics.core.atoms import (
    Integer,
    Integer0,
    Integer1,
    IntegerM1,
    Number,
    RationalOneHalf,
)
from mathics.core.attributes import A_LISTABLE, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.convert.python import from_bool
from mathics.core.convert.sympy import SympyExpression, from_sympy, sympy_symbol_prefix
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.expression_predefined import (
    MATHICS3_COMPLEX_INFINITY,
    MATHICS3_NEG_INFINITY,
)
from mathics.core.list import ListExpression
from mathics.core.rules import BasePattern
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolFalse,
    SymbolList,
    SymbolNull,
    SymbolPlus,
    SymbolPower,
    SymbolTimes,
    SymbolTrue,
)
from mathics.core.systemsymbols import (
    SymbolAlternatives,
    SymbolAssumptions,
    SymbolCos,
    SymbolCosh,
    SymbolCot,
    SymbolCoth,
    SymbolEqual,
    SymbolIndeterminate,
    SymbolLess,
    SymbolRule,
    SymbolRuleDelayed,
    SymbolSin,
    SymbolSinh,
    SymbolTable,
    SymbolTanh,
)
from mathics.eval.list.eol import eval_Part
from mathics.eval.numbers.algebra.simplify import eval_Simplify
from mathics.eval.numbers.numbers import cancel, sympy_factor
from mathics.eval.patterns import match


def expand(expr, numer=True, denom=False, deep=False, **kwargs):
    def _expand(expr):
        return expand(expr, numer=numer, denom=denom, deep=deep, **kwargs)

    if kwargs["modulus"] is not None and kwargs["modulus"] <= 0:
        return Integer0

    target_pat = kwargs.get("pattern", None)
    if target_pat:
        evaluation = kwargs["evaluation"]
    # A special case for trigonometric functions
    if "trig" in kwargs and kwargs["trig"]:
        if expr.has_form(
            ("Sin", "Cos", "Tan", "Cot", "Sinh", "Cosh", "Tanh", "Coth"), 1
        ):
            head = expr.get_head()
            theta = expr.elements[0]
            if (target_pat is not None) and theta.is_free(target_pat, evaluation):
                return expr
            if deep:
                theta = _expand(theta)

            if theta.has_form("Plus", 2, None):
                x, y = theta.elements[0], Expression(SymbolPlus, *theta.elements[1:])
                if head is SymbolSin:
                    a = Expression(
                        SymbolTimes,
                        _expand(Expression(SymbolSin, x)),
                        _expand(Expression(SymbolCos, y)),
                    )

                    b = Expression(
                        SymbolTimes,
                        _expand(Expression(SymbolCos, x)),
                        _expand(Expression(SymbolSin, y)),
                    )
                    return _expand(Expression(SymbolPlus, a, b))
                elif head is SymbolCos:
                    a = Expression(
                        SymbolTimes,
                        _expand(Expression(SymbolCos, x)),
                        _expand(Expression(SymbolCos, y)),
                    )

                    b = Expression(
                        SymbolTimes,
                        _expand(Expression(SymbolSin, x)),
                        _expand(Expression(SymbolSin, y)),
                    )

                    return _expand(Expression(SymbolPlus, a, -b))
                elif head is SymbolSinh:
                    a = Expression(
                        SymbolTimes,
                        _expand(Expression(SymbolSinh, x)),
                        _expand(Expression(SymbolCosh, y)),
                    )

                    b = Expression(
                        SymbolTimes,
                        _expand(Expression(SymbolCosh, x)),
                        _expand(Expression(SymbolSinh, y)),
                    )

                    return _expand(Expression(SymbolPlus, a, b))
                elif head is SymbolCosh:
                    a = Expression(
                        SymbolTimes,
                        _expand(Expression(SymbolCosh, x)),
                        _expand(Expression(SymbolCosh, y)),
                    )

                    b = Expression(
                        SymbolTimes,
                        _expand(Expression(SymbolSinh, x)),
                        _expand(Expression(SymbolSinh, y)),
                    )

                    return _expand(Expression(SymbolPlus, a, b))
                elif head is Symbol("Tan"):
                    a = _expand(Expression(SymbolSin, theta))
                    b = Expression(
                        SymbolPower, _expand(Expression(SymbolCos, theta)), IntegerM1
                    )
                    return _expand(Expression(SymbolTimes, a, b))
                elif head is SymbolCot:
                    a = _expand(Expression(SymbolCos, theta))
                    b = Expression(
                        SymbolPower, _expand(Expression(SymbolSin, theta)), IntegerM1
                    )
                    return _expand(Expression(SymbolTimes, a, b))
                elif head is SymbolTanh:
                    a = _expand(Expression(SymbolSinh, theta))
                    b = Expression(
                        SymbolPower, _expand(Expression(SymbolCosh, theta)), IntegerM1
                    )
                    return _expand(Expression(SymbolTimes, a, b))
                elif head is SymbolCoth:
                    a = _expand(Expression(SymbolTimes, SymbolCosh, theta))
                    b = Expression(
                        SymbolPower, _expand(Expression(SymbolSinh, theta)), IntegerM1
                    )
                    return _expand(Expression(a, b))

    sub_exprs = []

    def store_sub_expr(expr):
        sub_exprs.append(expr)
        result = sympy.Symbol(sympy_symbol_prefix + str(len(sub_exprs) - 1))
        return result

    def get_sub_expr(expr):
        name = expr.get_name()
        assert isinstance(expr, Symbol) and name.startswith("System`")
        i = int(name[len("System`") :])
        return sub_exprs[i]

    def convert_sympy(expr):
        "converts top-level to sympy"
        elements = expr.get_elements()
        if isinstance(expr, Integer):
            return sympy.Integer(expr.get_int_value())
        if target_pat is not None and not isinstance(expr, Number):
            if expr.is_free(target_pat, evaluation):
                return store_sub_expr(expr)
        if expr.has_form("Power", 2):
            # sympy won't expand `(a + b) / x` to `a / x + b / x` if denom is False
            # if denom is False we store negative powers to prevent this.
            n1 = elements[1].get_int_value()
            if not denom and n1 is not None and n1 < 0:
                return store_sub_expr(expr)
            return sympy.Pow(*[convert_sympy(element) for element in elements])
        elif expr.has_form("Times", 2, None):
            return sympy.Mul(*[convert_sympy(element) for element in elements])
        elif expr.has_form("Plus", 2, None):
            return sympy.Add(*[convert_sympy(element) for element in elements])
        else:
            return store_sub_expr(expr)

    def unconvert_subexprs(expr):
        if isinstance(expr, Atom):
            if isinstance(expr, Symbol):
                return get_sub_expr(expr)
            else:
                return expr
        else:
            return Expression(
                expr.head, *[unconvert_subexprs(element) for element in expr.elements]
            )

    sympy_expr = convert_sympy(expr)
    if deep:
        # thread over everything
        for (
            i,
            sub_expr,
        ) in enumerate(sub_exprs):
            if not isinstance(sub_expr, Atom):
                head = _expand(sub_expr.head)  # also expand head
                elements = sub_expr.elements
                if target_pat:
                    elements = [
                        (
                            element
                            if element.is_free(target_pat, evaluation)
                            else _expand(element)
                        )
                        for element in elements
                    ]
                else:
                    elements = [_expand(element) for element in elements]
                sub_exprs[i] = Expression(head, *elements)
    else:
        # thread over Lists etc.
        threaded_heads = ("List", "Rule")
        for i, sub_expr in enumerate(sub_exprs):
            for head in threaded_heads:
                if sub_expr.has_form(head, None):
                    elements = sub_expr.elements
                    if target_pat:
                        elements = [
                            (
                                element
                                if element.is_free(target_pat, evaluation)
                                else _expand(element)
                            )
                            for element in elements
                        ]
                    else:
                        elements = [_expand(element) for element in elements]
                    sub_exprs[i] = Expression(Symbol(head), *elements)
                    break

    hints = {
        "mul": True,
        "multinomial": True,
        "power_exp": False,
        "power_base": False,
        "basic": False,
        "log": False,
    }

    hints.update(kwargs)

    if numer and denom:
        # don't expand fractions when modulus is True
        if hints["modulus"] is not None:
            hints["frac"] = True
    else:
        # setting both True doesn't expand denom
        hints["numer"] = numer
        hints["denom"] = denom

    sympy_expr = sympy_expr.expand(**hints)
    result = from_sympy(sympy_expr)
    result = unconvert_subexprs(result)
    return result


def find_all_vars(expr):
    variables = set()

    def find_vars(e, e_sympy):
        assert e_sympy is not None
        if e_sympy.is_constant():
            return
        elif isinstance(e, Symbol):
            variables.add(e)
        elif e.has_form(("Plus", "Times"), None):
            for lv in e.elements:
                lv_sympy = lv.to_sympy()
                if lv_sympy is not None:
                    find_vars(lv, lv_sympy)
        elif e.has_form("Power", 2):
            a, b = e.elements  # a^b
            a_sympy, b_sympy = a.to_sympy(), b.to_sympy()
            if a_sympy is None or b_sympy is None:
                return
            if not (a_sympy.is_constant()) and b_sympy.is_rational:
                find_vars(a, a_sympy)
        elif not (isinstance(e, Atom)):
            variables.add(e)

    exprs = expr.elements if expr.has_form("List", None) else [expr]
    for e in exprs:
        e_sympy = e.to_sympy()
        if e_sympy is not None:
            find_vars(e, e_sympy)

    return variables


def get_exponents_sorted(expr, var) -> list:
    """
    Return a sorted list of exponents of var in expr
    """
    f = expr.to_sympy()
    x = var.to_sympy()
    if f is None or x is None:
        return [Integer0]

    result = set()
    for t in f.expand(power_exp=False).as_ordered_terms():
        coeff, exponent = t.as_coeff_exponent(x)
        if exponent:
            result.add(from_sympy(exponent))
        else:
            # find exponent of terms multiplied with functions: sin, cos, log, exp, ...
            # e.g: x^3 * Sin[x^2] should give 3
            muls = [
                (
                    term.as_coeff_mul(x)[1]
                    if term.as_coeff_mul(x)[1]
                    else (sympy.Integer(0),)
                )
                for term in coeff.as_ordered_terms()
            ]
            expos = [term.as_coeff_exponent(x)[1] for mul in muls for term in mul]
            result.add(from_sympy(sympy.Max(*[e for e in expos])))
    return sorted(result)


class Apart(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Apart.html</url>

    <dl>
      <dt>'Apart'[$expr$]
      <dd>writes $expr$ as a sum of individual fractions.
      <dt>'Apart'[$expr$, $var$]
      <dd>treats $var$ as the main variable.
    </dl>

    >> Apart[1 / (x^2 + 5x + 6)]
     = 1 / (2 + x) - 1 / (3 + x)

    When several variables are involved, the results can be different
    depending on the main variable:
    >> Apart[1 / (x^2 - y^2), x]
     = -1 / (2 y (x + y)) + 1 / (2 y (x - y))
    >> Apart[1 / (x^2 - y^2), y]
     = 1 / (2 x (x + y)) + 1 / (2 x (x - y))

    'Apart' is 'Listable':
    >> Apart[{1 / (x^2 + 5x + 6)}]
     = {1 / (2 + x) - 1 / (3 + x)}

    But it does not touch other expressions:
    >> Sin[1 / (x ^ 2 - y ^ 2)] // Apart
     = Sin[1 / (x ^ 2 - y ^ 2)]
    """

    attributes = A_LISTABLE | A_PROTECTED
    rules = {
        "Apart[expr_]": (
            "Block[{vars = Cases[Level[expr, {-1}], _Symbol]},"
            "  If[Length[vars] > 0, Apart[expr, vars[[1]]], expr]]"
        ),
    }
    summary_text = "partial fraction decomposition"

    def eval(self, expr, var, evaluation: Evaluation):
        "Apart[expr_, var_Symbol]"

        expr_sympy = expr.to_sympy()
        var_sympy = var.to_sympy()
        if expr_sympy is None or var_sympy is None:
            return None

        try:
            result = sympy.apart(expr_sympy, var_sympy)
            result = from_sympy(result)
            return result
        except sympy.PolynomialError:
            # raised e.g. for apart(sin(1/(x**2-y**2)))
            return expr


class Cancel(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Cancel.html</url>

    <dl>
      <dt>'Cancel'[$expr$]
      <dd>cancels out common factors in numerators and denominators.
    </dl>

    >> Cancel[x / x ^ 2]
     = 1 / x
    'Cancel' threads over sums:
    >> Cancel[x / x ^ 2 + y / y ^ 2]
     = 1 / x + 1 / y

    >> Cancel[f[x] / x + x * f[x] / x ^ 2]
     = 2 f[x] / x
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "cancel common factors in rational expressions"

    def eval(self, expr, evaluation: Evaluation):
        "Cancel[expr_]"

        return cancel(expr)


# Get a coefficient of form in an expression
def _coefficient(
    name: str, expr: Expression, form, n: Integer, evaluation: Evaluation
) -> Optional[BaseElement]:
    if expr is SymbolNull or form is SymbolNull or n is SymbolNull:
        return Integer0

    if not (isinstance(form, Symbol)) and not (isinstance(form, Expression)):
        evaluation.message(name, "ivar", form)
        return

    sympy_exprs = expr.to_sympy().as_ordered_terms()
    sympy_var = form.to_sympy()
    sympy_n = n.to_sympy()

    # expand sub expressions if they contain variables
    sympy_expr: sympy.Expr = sum(
        sympy.expand(e) if sympy_var.free_symbols.issubset(e.free_symbols) else e
        for e in sympy_exprs
    )
    sympy_result = sympy_expr.coeff(sympy_var, sympy_n)
    return from_sympy(sympy_result)


class Coefficient(Builtin):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/Coefficient.html</url>

    <dl>
      <dt>'Coefficient[expr, form]'
      <dd>returns the coefficient of $form$ in the polynomial $expr$.
      <dt>'Coefficient[expr, form, n]'
      <dd>return the coefficient of $form$^$n$ in $expr$.
    </dl>

    ## Form 1: Coefficient[expr, form]
    >> Coefficient[(x + y)^4, (x^2) * (y^2)]
     = 6
    >> Coefficient[a x^2 + b y^3 + c x + d y + 5, x]
     = c
    >> Coefficient[(x + 3 y)^5, x]
     = 405 y ^ 4
    >> Coefficient[(x + 3 y)^5, x * y^4]
     = 405
    >> Coefficient[(x + 2)/(y - 3) + (x + 3)/(y - 2), x]
     = 1 / (-3 + y) + 1 / (-2 + y)
    >> Coefficient[x*Cos[x + 3] + 6*y, x]
     = Cos[3 + x]

    ## Form 2: Coefficient[expr, form, n]
    >> Coefficient[(x + 1)^3, x, 2]
     = 3
    >> Coefficient[a x^2 + b y^3 + c x + d y + 5, y, 3]
     = b

    Find the free term in a polynomial:
    >> Coefficient[(x + 2)^3 + (x + 3)^2, x, 0]
     = 17
    >> Coefficient[(x + 2)^3 + (x + 3)^2, y, 0]
     = (2 + x) ^ 3 + (3 + x) ^ 2
    >> Coefficient[a x^2 + b y^3 + c x + d y + 5, x, 0]
     = 5 + b y ^ 3 + d y

    ## ## TODO: Support Modulus
    ## >> Coefficient[(x + 2)^3 + (x + 3)^2, x, 0, Modulus -> 3]
    ##  = 2
    """

    attributes = A_LISTABLE | A_PROTECTED
    messages = {
        "argtu": "Coefficient called with 1 argument; 2 or 3 arguments are expected.",
        "ivar": "`1` is not a valid variable.",
    }

    summary_text = "coefficient of a monomial in a polynomial expression"

    def eval_noform(self, expr: Expression, evaluation: Evaluation):
        "Coefficient[expr_]"
        evaluation.message("Coefficient", "argtu")

    def eval(self, expr: Expression, form: Expression, evaluation: Evaluation):
        "Coefficient[expr_, form_]"
        return _coefficient(self.__class__.__name__, expr, form, Integer1, evaluation)

    def eval_n(
        self, expr: Expression, form: Expression, n: Integer, evaluation: Evaluation
    ):
        "Coefficient[expr_, form_, n_Integer]"
        return _coefficient(self.__class__.__name__, expr, form, n, evaluation)


class _CoefficientHandler(Builtin):
    def coeff_power_internal(
        self,
        expr: BaseElement,
        var_exprs: list,
        filt: BaseElement,
        evaluation: Evaluation,
        form: str = "expr",
    ) -> list:
        """
        This method returns a list of terms grouped by different powers of the expressions in var_expr.
        """

        if len(var_exprs) == 0:
            if form == "expr":
                return expr
            else:
                return [([], expr)]
        if len(var_exprs) == 1:
            target_pat = BasePattern.create(var_exprs[0])
            var_pats = [target_pat]
        else:
            target_pat = BasePattern.create(Expression(SymbolAlternatives, *var_exprs))
            var_pats = [BasePattern.create(var) for var in var_exprs]

        # ###### Auxiliary functions #########
        def key_powers(lst: list) -> Union[int, float]:
            key = Expression(SymbolPlus, *lst).evaluate(evaluation)
            if key is not None and key.is_numeric(evaluation):
                return key.to_python()
            return 0

        def powers_list(pf: Optional[Expression]) -> list:
            """
            Build a list of exponents associated to each indeterminate.
            """
            powers = [Integer0 for i, p in enumerate(var_pats)]
            if pf is None:
                return powers
            if isinstance(pf, Symbol):
                for i, pat in enumerate(var_pats):
                    if match(pf, pat, evaluation):
                        powers[i] = Integer1
                        return powers
            if pf.has_form("Sqrt", 1):
                for i, pat in enumerate(var_pats):
                    if match(pf.elements[0], pat, evaluation):
                        powers[i] = RationalOneHalf
                        return powers
            if pf.has_form("Power", 2):
                for i, pat in enumerate(var_pats):
                    matchval = match(pf.elements[0], pat, evaluation)
                    if matchval:
                        powers[i] = pf.elements[1]
                        return powers
            if pf.has_form("Times", None):
                contrib = [powers_list(factor) for factor in pf.elements]
                for i in range(len(var_pats)):
                    powers[i] = Expression(
                        SymbolPlus, *[c[i] for c in contrib]
                    ).evaluate(evaluation)
                return powers
            else:
                for i, pat in enumerate(var_pats):
                    if match(pf, pat, evaluation):
                        powers[i] = Integer1
                        return powers
            return powers

        def split_coeff_pow(term) -> Tuple[Optional[list], Optional[list]]:
            """
            This function factorizes term in a coefficient free
            of powers of the target variables, and a factor with
            that powers.
            """
            coeffs = []
            powers = []
            # First, split factors on those which are powers of the variables
            # and the rest.
            if term.is_free(target_pat, evaluation):
                coeffs.append(term)
            elif match(term, target_pat, evaluation):
                return None, term
            elif (
                isinstance(term, Symbol)
                or term.has_form("Power", 2)
                or term.has_form("Sqrt", 1)
            ):
                powers.append(term)
            elif term.has_form("Times", None):
                for factor in term.elements:
                    if factor.is_free(target_pat, evaluation):
                        coeffs.append(factor)
                    elif match(factor, target_pat, evaluation):
                        powers.append(factor)
                    elif (
                        factor.has_form("Power", 2) or factor.has_form("Sqrt", 1)
                    ) and match(factor.elements[0], target_pat, evaluation):
                        powers.append(factor)
                    else:
                        coeffs.append(factor)
            else:
                coeffs.append(term)
            # Now, rebuild both factors
            if len(coeffs) == 0:
                coeffs = None
            elif len(coeffs) == 1:
                coeffs = coeffs[0]
            else:
                coeffs = Expression(SymbolTimes, *coeffs)
            if len(powers) == 0:
                powers = None
            elif len(powers) == 1:
                powers = powers[0]
            else:
                powers = Expression(SymbolTimes, *sorted(powers))
            return coeffs, powers

        # ################  The actual begin ####################
        expr = expand(
            expr,
            numer=True,
            denom=False,
            deep=False,
            trig=False,
            modulus=None,
            target_pat=target_pat,
        )

        if expr.is_free(target_pat, evaluation):
            if filt:
                expr = Expression(filt, expr).evaluate(evaluation)
            if form == "expr":
                return expr
            else:
                return [(powers_list(None), expr)]
        elif (
            isinstance(expr, Symbol)
            or match(expr, target_pat, evaluation)
            or expr.has_form("Power", 2)
            or expr.has_form("Sqrt", 1)
        ):
            coeff = (
                Expression(filt, Integer1).evaluate(evaluation) if filt else Integer1
            )
            if form == "expr":
                if coeff is Integer1:
                    return expr
                else:
                    return Expression(SymbolTimes, coeff, expr)
            else:
                if not coeff.is_free(target_pat, evaluation):
                    return []
                return [(powers_list(expr), coeff)]
        elif expr.has_form("Times", None):
            coeff, powers = split_coeff_pow(expr)
            if coeff is None:
                coeff = Integer1
            else:
                if form != "expr" and not coeff.is_free(target_pat, evaluation):
                    return []
            if filt:
                coeff = Expression(filt, coeff).evaluate(evaluation)

            if form == "expr":
                if powers is None:
                    return coeff
                else:
                    if coeff is Integer1:
                        return powers
                    else:
                        return Expression(SymbolTimes, coeff, powers)
            else:
                pl = powers_list(powers)
                return [(pl, coeff)]
        elif expr.has_form("Plus", None):
            coeff_dict = {}
            powers_dict = {}
            powers_order = {}
            for term in expr.elements:
                coeff, powers = split_coeff_pow(term)
                if (
                    form != "expr"
                    and coeff is not None
                    and not coeff.is_free(target_pat, evaluation)
                ):
                    return []
                pl = powers_list(powers)
                key = str(pl)
                if key not in powers_dict:
                    if form == "expr":
                        powers_dict[key] = powers
                    else:
                        # TODO: check if pl is a monomial...
                        powers_dict[key] = pl
                    coeff_dict[key] = []
                    powers_order[key] = key_powers(pl)

                coeff_dict[key].append(Integer1 if coeff is None else coeff)

            terms = []
            for key in sorted(
                coeff_dict, key=lambda kv: powers_order[kv], reverse=False
            ):
                val = coeff_dict[key]
                if len(val) == 0:
                    continue
                elif len(val) == 1:
                    coeff = val[0]
                else:
                    coeff = Expression(SymbolPlus, *val)
                if filt:
                    coeff = Expression(filt, coeff).evaluate(evaluation)

                powerfactor = powers_dict[key]
                if form == "expr":
                    if powerfactor:
                        terms.append(Expression(SymbolTimes, coeff, powerfactor))
                    else:
                        terms.append(coeff)
                else:
                    terms.append([powerfactor, coeff])
            if form == "expr":
                return Expression(SymbolPlus, *terms)
            else:
                return terms
        else:
            # expr is not a polynomial.
            if form == "expr":
                if filt:
                    expr = Expression(filt, expr).evaluate(evaluation)
                return expr
            else:
                return []


class CoefficientArrays(_CoefficientHandler):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/CoefficientArrays.html</url>

    <dl>
      <dt>'CoefficientArrays'[$polys$, $vars$]
      <dd>returns a list of arrays of coefficients of the variables $vars$ \
          in the polynomial  $poly$.
    </dl>

    >> CoefficientArrays[1 + x^3, x]
     = {1, {0}, {{0}}, {{{1}}}}
    >> CoefficientArrays[1 + x y+ x^3, {x, y}]
     = {1, {0, 0}, {{0, 1}, {0, 0}}, {{{1, 0}, {0, 0}}, {{0, 0}, {0, 0}}}}
    >> CoefficientArrays[{1 + x^2, x y}, {x, y}]
     = {{1, 0}, {{0, 0}, {0, 0}}, {{{1, 0}, {0, 0}}, {{0, 1}, {0, 0}}}}
    >> CoefficientArrays[(x+y+Sin[z])^3, {x,y}]
     = {Sin[z] ^ 3, {3 Sin[z] ^ 2, 3 Sin[z] ^ 2}, {{3 Sin[z], 6 Sin[z]}, {0, 3 Sin[z]}}, {{{1, 3}, {0, 3}}, {{0, 0}, {0, 1}}}}
    >> CoefficientArrays[(x + y + Sin[z])^3, {x, z}]
     : (x + y + Sin[z]) ^ 3 is not a polynomial in {x, z}
     = CoefficientArrays[(x + y + Sin[z]) ^ 3, {x, z}]
    """

    messages = {
        "poly": "`1` is not a polynomial in `2`",
    }
    options = {
        "Symmetric": "False",
    }
    summary_text = (
        "array of coefficients associated with a polynomial in many variables"
    )

    def eval_list(self, polys, varlist, evaluation: Evaluation, options: dict):
        "%(name)s[polys_, varlist_, OptionsPattern[]]"

        if polys.has_form("List", None):
            list_polys = polys.elements
        else:
            list_polys = [polys]

        if isinstance(varlist, Symbol):
            var_exprs = [varlist]
        elif varlist.has_form("List", None):
            var_exprs = varlist.elements
        else:
            var_exprs = [varlist]

        coeffs = [
            self.coeff_power_internal(pol, var_exprs, None, evaluation, "coeffs")
            for pol in list_polys
        ]

        dim1 = len(coeffs)
        dim2 = len(var_exprs)
        arrays = []
        if dim1 == 1:
            arrays.append(Integer(0))
        for i, component in enumerate(coeffs):
            if len(component) == 0:
                evaluation.message("CoefficientArrays", "poly", polys, varlist)
                return
            for idxcoeff in component:
                idx, coeff = idxcoeff
                order = (
                    Expression(SymbolPlus, *idx).evaluate(evaluation).get_int_value()
                )
                if order is None:
                    evaluation.message("CoefficientArrays", "poly", polys, varlist)
                    return
                while len(arrays) <= order:
                    cur_ord = len(arrays)
                    range2 = ListExpression(Integer(dim2))
                    its2 = [range2 for k in range(cur_ord)]
                    # TODO: Use SparseArray...
                    # This constructs a tensor or range cur_ord+1
                    if dim1 > 1:
                        newtable = Expression(
                            SymbolTable,
                            Integer(0),
                            ListExpression(Integer(dim1)),
                            *its2,
                        )
                    else:
                        newtable = Expression(SymbolTable, Integer(0), *its2)
                    arrays.append(newtable.evaluate(evaluation))
                curr_array = arrays[order]
                arrayidx = [
                    Integer(n + 1)
                    for n, j in enumerate(idx)
                    for q in range(j.get_int_value())
                ]
                if dim1 > 1:
                    arrayidx = [Integer(i + 1)] + arrayidx
                if dim1 == 1 and order == 0:
                    arrays[0] = coeff
                else:
                    eval_Part([curr_array], arrayidx, evaluation, coeff)
                    arrays[order] = curr_array
        return ListExpression(*arrays)


class CoefficientList(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/CoefficientList.html</url>

    <dl>
      <dt>'CoefficientList[poly, var]'
      <dd>returns a list of coefficients of powers of $var$ in $poly$, starting with power 0.
      <dt>'CoefficientList[poly, {var1, var2, ...}]'
      <dd>returns an array of coefficients of the $vari$.
    </dl>

    ## Form 1 CoefficientList[poly, var]
    >> CoefficientList[(x + 3)^5, x]
     = {243, 405, 270, 90, 15, 1}
    >> CoefficientList[(x + y)^4, x]
     = {y ^ 4, 4 y ^ 3, 6 y ^ 2, 4 y, 1}
    >> CoefficientList[a x^2 + b y^3 + c x + d y + 5, x]
     = {5 + b y ^ 3 + d y, c, a}
    >> CoefficientList[(x + 2)/(y - 3) + x/(y - 2), x]
     = {2 / (-3 + y), 1 / (-3 + y) + 1 / (-2 + y)}
    >> CoefficientList[(x + y)^3, z]
     = {(x + y) ^ 3}
    ## Form 2 CoefficientList[poly, {var1, var2, ...}]
    >> CoefficientList[a x^2 + b y^3 + c x + d y + 5, {x, y}]
     = {{5, d, 0, b}, {c, 0, 0, 0}, {a, 0, 0, 0}}
    >> CoefficientList[(x - 2 y + 3 z)^3, {x, y, z}]
     = {{{0, 0, 0, 27}, {0, 0, -54, 0}, {0, 36, 0, 0}, {-8, 0, 0, 0}}, {{0, 0, 27, 0}, {0, -36, 0, 0}, {12, 0, 0, 0}, {0, 0, 0, 0}}, {{0, 9, 0, 0}, {-6, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}}, {{1, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}}}
    >> CoefficientList[Series[Log[1-x], {x, 0, 9}], x]
     = {0, -1, -1 / 2, -1 / 3, -1 / 4, -1 / 5, -1 / 6, -1 / 7, -1 / 8, -1 / 9}
    >> CoefficientList[Series[2x, {x, 0, 9}], x]
     = {0, 2}
    """

    messages = {
        "argtu": "CoefficientList called with 1 argument; 2 or 3 arguments are expected.",
        "ivar": "`1` is not a valid variable.",
        "poly": "`1` is not a polynomial.",
    }
    summary_text = "list of coefficients defining a polynomial"

    def eval_noform(self, expr, evaluation):
        "CoefficientList[expr_]"
        evaluation.message("CoefficientList", "argtu")

    def eval(self, expr: Expression, form: Expression, evaluation: Evaluation):
        "CoefficientList[expr_, form_]"
        vars = [form] if not form.has_form("List", None) else [v for v in form.elements]

        # check form is not a variable
        for v in vars:
            if not (isinstance(v, Symbol)) and not (isinstance(v, Expression)):
                evaluation.message("CoefficientList", "ivar", v)
                return

        # special cases for expr and form
        e_null = expr is SymbolNull
        f_null = form is SymbolNull
        if expr == Integer0:
            return ListExpression()
        elif e_null and f_null:
            return ListExpression(Integer0)
        elif e_null and not f_null:
            return ListExpression(SymbolNull)
        elif f_null:
            return ListExpression(expr)
        elif form.has_form("List", 0):
            return expr
        elif expr.get_head_name() == "System`SeriesData":
            coeffs: ListExpression
            nmin: Integer
            nmax: Integer
            x, x0, coeffs, nmin, nmax, den = expr.elements
            if x == form and x0 == Integer0 and den == Integer1:
                return ListExpression(
                    *[
                        coeffs.elements[i - nmin.value] if i >= nmin.value else Integer0
                        for i in range(
                            0, min(nmax.value, nmin.value + len(coeffs.elements))
                        )
                    ]
                )

        sympy_expr = expr.to_sympy()
        sympy_vars = [v.to_sympy() for v in vars]

        if not sympy_expr.is_polynomial(*[x for x in sympy_vars]):
            evaluation.message("CoefficientList", "poly", expr)
            return

        try:
            sympy_poly, sympy_opt = sympy.poly_from_expr(sympy_expr, sympy_vars)
            dimensions = [
                sympy_poly.degree(x) if x in sympy_poly.gens else 0 for x in sympy_vars
            ]

            # single & multiple variables cases
            if not form.has_form("List", None):
                return ListExpression(
                    *[
                        _coefficient(
                            self.__class__.__name__, expr, form, Integer(n), evaluation
                        )
                        for n in range(dimensions[0] + 1)
                    ],
                )
            elif form.has_form("List", 1):
                form = form.elements[0]
                return ListExpression(
                    *[
                        _coefficient(
                            self.__class__.__name__, expr, form, Integer(n), evaluation
                        )
                        for n in range(dimensions[0] + 1)
                    ],
                )
            else:

                def _nth(poly, dims, exponents):
                    if not dims:
                        return from_sympy(poly.coeff_monomial(exponents))

                    elements = []
                    first_dim = dims[0]
                    for i in range(first_dim + 1):
                        exponents.append(i)
                        subs = _nth(poly, dims[1:], exponents)
                        elements.append(subs)
                        exponents.pop()
                    result = ListExpression(*elements)
                    return result

                return _nth(sympy_poly, dimensions, [])
        except sympy.PolificationFailed:
            evaluation.message("CoefficientList", "poly", expr)


class Collect(_CoefficientHandler):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/Collect.html</url>

    <dl>
      <dt>'Collect'[$expr$, $x$]
      <dd> Expands $expr$ and collect together terms having the same power of $x$.

      <dt>'Collect'[$expr$, {$x_1$, $x_2$, ...}]
      <dd> Expands $expr$ and collect together terms having the same powers of \
         $x_1$, $x_2$, ....

      <dt>'Collect'[$expr$, {$x_1$, $x_2$, ...}, $filter$]
      <dd> After collect the terms, applies $filter$ to each coefficient.
    </dl>

    >> Collect[(x+y)^3, y]
     =  x ^ 3 + 3 x ^ 2 y + 3 x y ^ 2 + y ^ 3
    >> Collect[2 Sin[x z] (x+2 y^2 + Sin[y] x), y]
     = 2 x Sin[x z] + 2 x Sin[x z] Sin[y] + 4 y ^ 2 Sin[x z]
    >> Collect[3 x y+2 Sin[x z] (x+2 y^2 + x) + (x+y)^3, y]
     = 4 x Sin[x z] + x ^ 3 + y (3 x + 3 x ^ 2) + y ^ 2 (3 x + 4 Sin[x z]) + y ^ 3
    >> Collect[3 x y+2 Sin[x z] (x+2 y^2 + x) + (x+y)^3, {x,y}]
     = 4 x Sin[x z] + x ^ 3 + 3 x y + 3 x ^ 2 y + 4 y ^ 2 Sin[x z] + 3 x y ^ 2 + y ^ 3
    >> Collect[3 x y+2 Sin[x z] (x+2 y^2 + x) + (x+y)^3, {x,y}, h]
     = x h[4 Sin[x z]] + x ^ 3 h[1] + x y h[3] + x ^ 2 y h[3] + y ^ 2 h[4 Sin[x z]] + x y ^ 2 h[3] + y ^ 3 h[1]
    """

    rules = {
        "Collect[expr_, varlist_]": "Collect[expr, varlist, Identity]",
    }
    summary_text = "collect terms with a variable at the same power"

    def eval_var_filter(self, expr, varlist, filt, evaluation):
        """Collect[expr_, varlist_, filt_]"""
        if filt is Symbol("Identity"):
            filt = None
        if isinstance(varlist, Symbol):
            var_exprs = [varlist]
        elif varlist.has_form("List", None):
            var_exprs = varlist.elements
        else:
            var_exprs = [varlist]

        return self.coeff_power_internal(expr, var_exprs, filt, evaluation, "expr")


class Denominator(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Denominator.html</url>

    <dl>
      <dt>'Denominator'[$expr$]
      <dd>gives the denominator in $expr$.
    </dl>

    >> Denominator[a / b]
     = b
    >> Denominator[2 / 3]
     = 3
    >> Denominator[a + b]
     = 1
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "denominator of an expression"

    def eval(self, expr, evaluation):
        "Denominator[expr_]"

        sympy_expr = expr.to_sympy()
        if sympy_expr is None:
            return None
        numer, denom = sympy_expr.as_numer_denom()
        return from_sympy(denom)


class _Expand(Builtin):
    options = {
        "Trig": "False",
        "Modulus": "0",
    }

    messages = {
        "modn": "Value of option `1` -> `2` should be an integer.",
        "opttf": "Value of option `1` -> `2` should be True or False.",
    }

    def convert_options(self, options: dict, evaluation: Evaluation):
        modulus = options["System`Modulus"]
        py_modulus = modulus.get_int_value()
        if py_modulus is None:
            evaluation.message(self.get_name(), "modn", Symbol("Modulus"), modulus)
            return
        if py_modulus == 0:
            py_modulus = None

        trig = options["System`Trig"]
        if trig is SymbolTrue:
            py_trig = True
        elif trig is SymbolFalse:
            py_trig = False
        else:
            evaluation.message(self.get_name(), "opttf", Symbol("Trig"), trig)
            return

        return {"modulus": py_modulus, "trig": py_trig}


class Expand(_Expand):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Expand.html</url>

    <dl>
      <dt>'Expand'[$expr$]
      <dd>expands out positive integer powers and products of sums in $expr$, as \
          well as trigonometric identities.

      <dt>Expand[$expr$, $target$]
      <dd>just expands those parts involving $target$.
    </dl>

    >> Expand[(x + y) ^ 3]
     = x ^ 3 + 3 x ^ 2 y + 3 x y ^ 2 + y ^ 3
    >> Expand[(a + b) (a + c + d)]
     = a ^ 2 + a b + a c + a d + b c + b d
    >> Expand[(a + b) (a + c + d) (e + f) + e a a]
     = 2 a ^ 2 e + a ^ 2 f + a b e + a b f + a c e + a c f + a d e + a d f + b c e + b c f + b d e + b d f
    >> Expand[(a + b) ^ 2 * (c + d)]
     = a ^ 2 c + a ^ 2 d + 2 a b c + 2 a b d + b ^ 2 c + b ^ 2 d
    >> Expand[(x + y) ^ 2 + x y]
     = x ^ 2 + 3 x y + y ^ 2
    >> Expand[((a + b) (c + d)) ^ 2 + b (1 + a)]
     = a ^ 2 c ^ 2 + 2 a ^ 2 c d + a ^ 2 d ^ 2 + b + a b + 2 a b c ^ 2 + 4 a b c d + 2 a b d ^ 2 + b ^ 2 c ^ 2 + 2 b ^ 2 c d + b ^ 2 d ^ 2

    'Expand' expands items in lists and rules:
    >> Expand[{4 (x + y), 2 (x + y) -> 4 (x + y)}]
     = {4 x + 4 y, 2 x + 2 y -> 4 x + 4 y}

    'Expand' expands trigonometric identities
    >> Expand[Sin[x + y], Trig -> True]
     = Cos[x] Sin[y] + Cos[y] Sin[x]
    >> Expand[Tanh[x + y], Trig -> True]
     = Cosh[x] Sinh[y] / (Cosh[x] Cosh[y] + Sinh[x] Sinh[y]) + Cosh[y] Sinh[x] / (Cosh[x] Cosh[y] + Sinh[x] Sinh[y])

    'Expand' does not change any other expression.
    >> Expand[Sin[x (1 + y)]]
     = Sin[x (1 + y)]

    Using the second argument, the expression only
    expands those subexpressions containing $pat$:
    >> Expand[(x+a)^2+(y+a)^2+(x+y)(x+a), y]
     = a ^ 2 + 2 a y + x (a + x) + y (a + x) + y ^ 2 + (a + x) ^ 2
    'Expand' also works in Galois fields
    >> Expand[(1 + a)^12, Modulus -> 3]
     = 1 + a ^ 3 + a ^ 9 + a ^ 12

    >> Expand[(1 + a)^12, Modulus -> 4]
     = 1 + 2 a ^ 2 + 3 a ^ 4 + 3 a ^ 8 + 2 a ^ 10 + a ^ 12
    """

    summary_text = "expand out products and powers"

    def eval_patt(self, expr, target, evaluation: Evaluation, options: dict):
        "Expand[expr_, target_, OptionsPattern[Expand]]"

        if target.get_head_name() in ("System`Rule", "System`DelayedRule"):
            optname = target.elements[0].get_name()
            options[optname] = target.elements[1]
            target = None

        kwargs = self.convert_options(options, evaluation)
        if kwargs is None:
            return

        if target:
            kwargs["pattern"] = BasePattern.create(target)
        kwargs["evaluation"] = evaluation
        return expand(expr, True, False, **kwargs)

    def eval(self, expr, evaluation: Evaluation, options: dict):
        "Expand[expr_, OptionsPattern[Expand]]"

        kwargs = self.convert_options(options, evaluation)
        if kwargs is None:
            return

        return expand(expr, True, False, **kwargs)


class ExpandAll(_Expand):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ExpandAll.html</url>

    <dl>
      <dt>'ExpandAll'[$expr$]
      <dd>expands out negative integer powers and products of sums in $expr$.

      <dt>'ExpandAll'[$expr$, $target$]
      <dd>just expands those parts involving $target$.
    </dl>

    >> ExpandAll[(a + b) ^ 2 / (c + d)^2]
     = a ^ 2 / (c ^ 2 + 2 c d + d ^ 2) + 2 a b / (c ^ 2 + 2 c d + d ^ 2) + b ^ 2 / (c ^ 2 + 2 c d + d ^ 2)

    'ExpandAll' descends into sub expressions
    >> ExpandAll[(a + Sin[x (1 + y)])^2]
     = 2 a Sin[x + x y] + a ^ 2 + Sin[x + x y] ^ 2

    >> ExpandAll[Sin[(x+y)^2]]
     = Sin[x ^ 2 + 2 x y + y ^ 2]

    >> ExpandAll[Sin[(x+y)^2], Trig->True]
     = Cos[x ^ 2] Cos[2 x y] Sin[y ^ 2] + Cos[x ^ 2] Cos[y ^ 2] Sin[2 x y] + Cos[2 x y] Cos[y ^ 2] Sin[x ^ 2] - Sin[x ^ 2] Sin[2 x y] Sin[y ^ 2]
    'ExpandAll' also expands heads
    >> ExpandAll[((1 + x)(1 + y))[x]]
     = (1 + x + y + x y)[x]

    'ExpandAll' can also work in finite fields
    >> ExpandAll[(1 + a) ^ 6 / (x + y)^3, Modulus -> 3]
     = (1 + 2 a ^ 3 + a ^ 6) / (x ^ 3 + y ^ 3)

    """

    summary_text = "expand products and powers, including negative integer powers"

    def eval_patt(self, expr, target, evaluation: Evaluation, options: dict):
        "ExpandAll[expr_, target_, OptionsPattern[Expand]]"
        if target.get_head_name() in ("System`Rule", "System`DelayedRule"):
            optname = target.elements[0].get_name()
            options[optname] = target.elements[1]
            target = None

        kwargs = self.convert_options(options, evaluation)
        if kwargs is None:
            return

        if target:
            kwargs["pattern"] = BasePattern.create(target)
        kwargs["evaluation"] = evaluation
        return expand(expr, numer=True, denom=True, deep=True, **kwargs)

    def eval(self, expr, evaluation: Evaluation, options: dict):
        "ExpandAll[expr_, OptionsPattern[ExpandAll]]"

        kwargs = self.convert_options(options, evaluation)
        if kwargs is None:
            return
        return expand(expr, numer=True, denom=True, deep=True, **kwargs)


class ExpandDenominator(_Expand):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ExpandDenominator.html</url>

    <dl>
      <dt>'ExpandDenominator'[$expr$]
      <dd>expands out negative integer powers and products of sums in $expr$.
    </dl>

    >> ExpandDenominator[(a + b) ^ 2 / ((c + d)^2 (e + f))]
     = (a + b) ^ 2 / (c ^ 2 e + c ^ 2 f + 2 c d e + 2 c d f + d ^ 2 e + d ^ 2 f)
    """

    summary_text = "expand just the denominator of a rational expression"

    def eval(self, expr, evaluation: Evaluation, options: dict):
        "ExpandDenominator[expr_, OptionsPattern[ExpandDenominator]]"

        kwargs = self.convert_options(options, evaluation)
        if kwargs is None:
            return
        return expand(expr, False, True, **kwargs)


class Exponent(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Exponent.html</url>

    <dl>
      <dt>'Exponent[expr, form]'
      <dd>returns the maximum power with which $form$ appears in the expanded \
          form of $expr$.

      <dt>'Exponent[expr, form, h]'
      <dd>applies $h$ to the set of exponents with which $form$ appears in $expr$.
    </dl>

    >> Exponent[5 x^2 - 3 x + 7, x]
     = 2
    >> Exponent[(x^3 + 1)^2 + 1, x]
     = 6
    >> Exponent[x^(n + 1) + Sqrt[x] + 1, x]
     = Max[1 / 2, 1 + n]
    >> Exponent[x / y, y]
     = -1

    >> Exponent[(x^2 + 1)^3 - 1, x, Min]
     = 2

    >> Exponent[0, x]
     = -Infinity
    >> Exponent[1, x]
     = 0
    """

    attributes = A_LISTABLE | A_PROTECTED

    messages = {
        "argtu": "Exponent called with `1` argument; 2 or 3 arguments are expected.",
    }

    rules = {
        "Exponent[expr_, form_]": "Exponent[expr, form, Max]",
    }
    summary_text = "maximum power in which a form appears in a polynomial"

    def eval_novar(self, expr, evaluation):
        "Exponent[expr_]"
        evaluation.message("Exponent", "argtu", Integer1)

    def eval(self, expr, form, h, evaluation):
        "Exponent[expr_, form_, h_]"
        if expr == Integer0:
            return MATHICS3_NEG_INFINITY

        if not form.has_form("List", None):
            # TODO: add ElementProperties in Expression interface refactor branch:
            #   fully_evaluated, flat, and is_ordered are all True
            return Expression(h, *[i for i in get_exponents_sorted(expr, form)])
        else:
            exponents = [get_exponents_sorted(expr, var) for var in form.elements]
            # TODO: add ElementProperties in Expression interface refactor branch:
            #   fully_evaluated is True, flat is false, and is_ordered is probably True
            return ListExpression(*[Expression(h, *[i for i in s]) for s in exponents])


class Factor(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Factor.html</url>

    <dl>
      <dt>'Factor'[$expr$]
      <dd>factors the polynomial expression $expr$.
    </dl>

    >> Factor[x ^ 2 + 2 x + 1]
     = (1 + x) ^ 2

    >> Factor[1 / (x^2+2x+1) + 1 / (x^4+2x^2+1)]
     = (2 + 2 x + 3 x ^ 2 + x ^ 4) / ((1 + x) ^ 2 (1 + x ^ 2) ^ 2)

    Factor can also be used with equations:
    >> Factor[x a == x b + x c]
     = a x == x (b + c)

    And lists:
    >> Factor[{x + x^2, 2 x + 2 y + 2}]
     = {x (1 + x), 2 (1 + x + y)}

    It also works with more complex expressions:
    >> Factor[x ^ 3 + 3 x ^ 2 y + 3 x y ^ 2 + y ^ 3]
     = (x + y) ^ 3

    You can use Factor to find when a polynomial is zero:
    >> x^2 - x == 0 // Factor
     = x (-1 + x) == 0
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "factor sums into product and powers"

    def eval(self, expr, evaluation):
        "Factor[expr_]"

        expr_sympy = expr.to_sympy()
        if expr_sympy is None:
            return None

        try:
            return from_sympy(sympy_factor(expr_sympy))
        except sympy.PolynomialError:
            return expr


class FactorTermsList(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/FactorTermsList.html</url>

    <dl>
      <dt>'FactorTermsList[poly]'
      <dd>returns a list of 2 elements.
        The first element is the numerical factor in $poly$.
        The second one is the remaining of the polynomial with numerical factor removed.

      <dt>'FactorTermsList[poly, {x1, x2, ...}]'
      <dd>returns a list of factors in $poly$.
        The first element is the numerical factor in $poly$. \
        The next ones are factors that are independent of variables lists which \
        are created by removing each variable $xi$ from right to left. \
        The last one is the remaining of polynomial after dividing $poly$ to all previous factors.
    </dl>

    >> FactorTermsList[2 x^2 - 2]
     = {2, -1 + x ^ 2}
    >> FactorTermsList[x^2 - 2 x + 1]
     = {1, 1 - 2 x + x ^ 2}
    >> f = 3 (-1 + 2 x) (-1 + y) (1 - a)
     = 3 (-1 + 2 x) (-1 + y) (1 - a)
    >> FactorTermsList[f]
     = {-3, -1 + a - 2 a x - a y + 2 x + y - 2 x y + 2 a x y}
    >> FactorTermsList[f, x]
     = {-3, 1 - a - y + a y, -1 + 2 x}
    """

    messages = {
        # 'poly': '`1` is not a polynomial.',
        "ivar": "`1` is not a valid variable.",
    }
    rules = {
        "FactorTermsList[expr_]": "FactorTermsList[expr, {}]",
        "FactorTermsList[expr_, var_]": "FactorTermsList[expr, {var}]",
    }
    summary_text = "a polynomial as a list of factors"

    def eval_list(self, expr, vars, evaluation):
        "FactorTermsList[expr_, vars_List]"
        if expr == Integer0:
            return ListExpression(Integer1, Integer0)
        elif isinstance(expr, Number):
            return ListExpression(expr, Integer1)

        for x in vars.elements:
            if not (isinstance(x, Atom)):
                evaluation.message("CoefficientList", "ivar", x)
                return

        sympy_expr = expr.to_sympy()
        if sympy_expr is None:
            return ListExpression(Integer1, expr)
        sympy_expr = sympy.together(sympy_expr)

        sympy_vars = [
            x.to_sympy()
            for x in vars.elements
            if isinstance(x, Symbol) and sympy_expr.is_polynomial(x.to_sympy())
        ]

        result = []
        numer, denom = sympy_expr.as_numer_denom()
        try:
            if denom == 1:
                # Get numerical part
                num_coeff, num_polys = sympy.factor_list(sympy.Poly(numer))
                result.append(num_coeff)

                # Get factors are independent of sub list of variables
                if (
                    sympy_vars
                    and isinstance(expr, Expression)
                    and any(
                        x.free_symbols.issubset(sympy_expr.free_symbols)
                        for x in sympy_vars
                    )
                ):
                    for i in reversed(range(len(sympy_vars))):
                        numer = sympy.factor(numer) / sympy.factor(num_coeff)
                        num_coeff, num_polys = sympy.factor_list(
                            sympy.Poly(numer), *[x for x in sympy_vars[: (i + 1)]]
                        )
                        result.append(sympy.expand(num_coeff))

                # Last factor
                numer = sympy.factor(numer) / sympy.factor(num_coeff)
                result.append(sympy.expand(numer))
            else:
                num_coeff, num_polys = sympy.factor_list(sympy.Poly(numer))
                den_coeff, den_polys = sympy.factor_list(sympy.Poly(denom))
                result = [
                    num_coeff / den_coeff,
                    sympy.expand(
                        sympy.factor(numer)
                        / num_coeff
                        / (sympy.factor(denom) / den_coeff)
                    ),
                ]
        except sympy.PolynomialError:  # MMA does not raise error for non poly
            result.append(sympy.expand(numer))
            # evaluation.message(self.get_name(), 'poly', expr)

        return ListExpression(*[from_sympy(i) for i in result])


# This is out of order alphabetically because it has to come before
# FullSimplify
class Simplify(Builtin):
    r"""
    <url>:SymPy:
    https://docs.sympy.org/latest/modules/simplify
    /simplify.html</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Simplify.html</url>

    <dl>
      <dt>'Simplify'[$expr$]
      <dd>simplifies $expr$.

      <dt>'Simplify'[$expr$, $assump$]
      <dd>simplifies $expr$ assuming $assump$ instead of '\$Assumptions'.
    </dl>

    >> Simplify[2*Sin[x]^2 + 2*Cos[x]^2]
     = 2
    >> Simplify[x]
     = x
    >> Simplify[f[x]]
     = f[x]

    Simplify over conditional expressions uses '\$Assumptions', or $assump$
    to evaluate the condition:
    >> $Assumptions={a <= 0};
    >> Simplify[ConditionalExpression[1, a > 0]]
     = Undefined
    The $assump$ option  override '\$Assumption':
    >> Simplify[ConditionalExpression[1, a > 0] ConditionalExpression[1, b > 0], { b > 0 }]
     = ConditionalExpression[1, a > 0]
    On the other hand, 'Assumptions' option does not override '\$Assumptions', but add to them:
    >> Simplify[ConditionalExpression[1, a > 0] ConditionalExpression[1, b > 0], Assumptions -> { b > 0 }]
     = ConditionalExpression[1, a > 0]
    Passing both options overwrites '\$Assumptions' with the union of $assump$ the option
    >> Simplify[ConditionalExpression[1, a > 0] ConditionalExpression[1, b > 0], {a>0},Assumptions -> { b > 0 }]
     = 1
    >> $Assumptions={};

    The option 'ComplexityFunction' allows to control the way in which the \
    evaluator decides if one expression is simpler than another. For example, \
    by default, 'Simplify' tries to avoid expressions involving numbers with many digits:
    >> Simplify[20 Log[2]]
     = 20 Log[2]
    This behaviour can be modified by setting 'LeafCount' as the 'ComplexityFunction':
    >> Simplify[20 Log[2], ComplexityFunction->LeafCount]
     = Log[1048576]
    """

    options = {
        "Assumptions": "$Assumptions",
        "ComplexityFunction": "Automatic",
    }
    rules = {
        "Simplify[list_List]": "Simplify /@ list",
        "Simplify[rule_Rule]": "Simplify /@ rule",
    }
    summary_text = "apply transformations to simplify an expression"

    def eval_with_assumptions(self, expr, assum, evaluation, options={}):
        "%(name)s[expr_, assum_, OptionsPattern[]]"

        # If the second argument is a rule, it means that
        # it should be taken as an option.
        if assum.get_head() in (SymbolRule, SymbolRuleDelayed):
            options[assum.elements[0].get_name()] = assum.elements[1]
            return self.eval(expr, evaluation, options)

        # If the option "Assumptions" was passed, then merge with assum:
        assumptions_list = options.pop("System`Assumptions")
        if assumptions_list and assumptions_list is not SymbolAssumptions:
            if assum.get_head() is not SymbolList:
                assum = ListExpression(assum)
            if assumptions_list.get_head() is not SymbolList:
                assumptions_list = ListExpression(assumptions_list)
            assum = ListExpression(assum, assumptions_list)
        assumptions = assum.evaluate(evaluation).flatten_with_respect_to_head(
            SymbolList
        )
        # Now, reevaluate the expression with all the assumptions.
        simplify_expr = Expression(
            Symbol(self.get_name()), expr, *options_to_rules(options)
        )
        return dynamic_scoping(
            lambda ev: simplify_expr.evaluate(ev),
            {"System`$Assumptions": assumptions},
            evaluation,
        )

    def eval_power_of_zero(self, b, evaluation):
        "%(name)s[0^b_]"
        if self.eval(Expression(SymbolLess, Integer0, b), evaluation) is SymbolTrue:
            return Integer0
        if self.eval(Expression(SymbolLess, b, Integer0), evaluation) is SymbolTrue:
            return MATHICS3_COMPLEX_INFINITY
        if self.eval(Expression(SymbolEqual, b, Integer0), evaluation) is SymbolTrue:
            return Symbol(SymbolIndeterminate)
        return Expression(SymbolPower, Integer0, b)

    def eval(self, expr, evaluation, options={}):
        "%(name)s[expr_, OptionsPattern[]]"
        # If System`Assumptions is in the options,
        # rebuild the expression without this option, and evaluate it
        # inside a scope with $Assumptions set accordingly.
        assumptions = options.pop("System`Assumptions", None)
        if assumptions not in (None, SymbolAssumptions):
            simplify_expr = Expression(
                Symbol(self.get_name()), expr, *options_to_rules(options)
            )
            return dynamic_scoping(
                lambda ev: simplify_expr.evaluate(ev),
                {"System`$Assumptions": assumptions},
                evaluation,
            )

        symbol_name = Symbol(self.get_name())
        return eval_Simplify(symbol_name, expr, evaluation, options)


class FullSimplify(Simplify):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/FullSimplify.html</url>

    <dl>
      <dt>'FullSimplify'[$expr$]
      <dd>simplifies $expr$ using an extended set of simplification rules.
      <dt>'FullSimplify'[$expr$, $assump$]
      <dd>simplifies $expr$ assuming $assump$ instead of $Assumptions$.
    </dl>

    TODO: implement the extension. By now, this does the same than Simplify...

    >> FullSimplify[2*Sin[x]^2 + 2*Cos[x]^2]
     = 2

    """

    rules = {
        "FullSimplify[list_List]": "FullSimplify /@ list",
        "FullSimplify[rule_Rule]": "FullSimplify /@ rule",
        "FullSimplify[eq_Equal]": "FullSimplify /@ eq",
    }
    summary_text = "apply a full set of simplification transformations"


class MinimalPolynomial(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/MinimalPolynomial.html</url>

    <dl>
      <dt>'MinimalPolynomial[s, x]'
      <dd>gives the minimal polynomial in $x$ for which the algebraic \
      number $s$ is a root.
    </dl>

    >> MinimalPolynomial[7, x]
     = -7 + x
    >> MinimalPolynomial[Sqrt[2] + Sqrt[3], x]
     = 1 - 10 x ^ 2 + x ^ 4
    >> MinimalPolynomial[Sqrt[1 + Sqrt[3]], x]
     = -2 - 2 x ^ 2 + x ^ 4
    >> MinimalPolynomial[Sqrt[I + Sqrt[6]], x]
     = 49 - 10 x ^ 4 + x ^ 8
    """

    attributes = A_LISTABLE | A_PROTECTED

    messages = {
        "nalg": "`1` is not an explicit algebraic number.",
    }
    summary_text = "minimal polynomial for a general algebraic number"

    def eval_novar(self, s, evaluation):
        "MinimalPolynomial[s_]"
        x = Symbol("#1")
        return self.eval(s, x, evaluation)

    def eval(self, s, x, evaluation):
        "MinimalPolynomial[s_, x_]"
        variables = find_all_vars(s)
        if len(variables) > 0:
            evaluation.message("MinimalPolynomial", "nalg", s)
            return

        if s is SymbolNull:
            evaluation.message("MinimalPolynomial", "nalg", s)
            return

        sympy_s, sympy_x = s.to_sympy(), x.to_sympy()
        if sympy_s is None or sympy_x is None:
            return None
        sympy_result = sympy.minimal_polynomial(sympy_s, polys=True)(sympy_x)
        return from_sympy(sympy_result)


class Numerator(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Numerator.html</url>

    <dl>
      <dt>'Numerator'[$expr$]
      <dd>gives the numerator in $expr$.
    </dl>

    >> Numerator[a / b]
     = a
    >> Numerator[2 / 3]
     = 2
    >> Numerator[a + b]
     = a + b
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "numerator of an expression"

    def eval(self, expr, evaluation: Evaluation):
        "Numerator[expr_]"

        sympy_expr = expr.to_sympy()
        if sympy_expr is None:
            return None
        numer, _ = sympy_expr.as_numer_denom()
        return from_sympy(numer)


class PolynomialQ(Builtin):
    """
    <url>:Polynomial:
    https://en.wikipedia.org/wiki/Polynomial:</url> (<url>:SymPy:
    https://docs.sympy.org/latest/modules/core.html#sympy.core.expr.Expr.is_polynomial</url>, <url>:WMA:
    https://reference.wolfram.com/language/ref/PolynomialQ.html</url>)

    <dl>
      <dt>'PolynomialQ[expr]'
      <dd>returns True if $expr$ is a polynomial and returns False otherwise.
      <dt>'PolynomialQ[expr, var]'
      <dd>returns True if $expr$ is a polynomial in $var$, and returns False otherwise.
      <dt>'PolynomialQ[expr, {var1, ...}]'
      <dd>tests whether $expr$ is a polynomial in the $vari$.
    </dl>


    'PolynomialQ' with no explicit variable mentioned:

    >> PolynomialQ[x^2]
     = True

    A number is a degenerate kind of polynomial:
    >> PolynomialQ[2]
     = True

    The following is not a polynomial because $y$ is raised to \
    the power -1:
    >> PolynomialQ[x^2 + x/y]
     = False

    'PolynomialQ' using an expression and a single variable:
    >> PolynomialQ[x^3 - 2 x/y + 3xz, x]
     = True

    In the above, there were no negative powers for $x$. \
    In the below when we check with respect to $y$, \
    we <i>do</i> find $y$ is raised to a negative power:
    >> PolynomialQ[x^3 - 2 x/y^2 + 3xz, y]
     = False

    >> PolynomialQ[f[a] + f[a]^2, f[a]]
     = True

    'PolynomialQ' using an expression and a list of variables:

    >> PolynomialQ[x^2 + axy^2 - bSin[c], {x, y}]
     = True
    >> PolynomialQ[x^2 + axy^2 - bSin[c], {a, b, c}]
     = False


    """

    messages = {
        "argt": "PolynomialQ called with `1` arguments; 1 or 2 arguments are expected.",
        "novar": "No variable is not supported in PolynomialQ.",
    }
    summary_text = "test if the expression is a polynomial in a variable"

    def eval(self, expr, v, evaluation):
        "PolynomialQ[expr_, v___]"
        if expr is SymbolNull:
            return SymbolTrue

        v = v.get_sequence()
        if len(v) > 1:
            evaluation.message("PolynomialQ", "argt", Integer(len(v) + 1))
            return
        elif len(v) == 0:
            sympy_expr = expr.to_sympy(convert_functions_for_polynomialq=True)
            free_symbols = []
            # Until we understand and get expression generation under control,
            # for now, we include both sympy.Symbol and
            # SympyExpression(sympy.Symbol) variants
            # as free variables.
            for free_symbol in sympy_expr.free_symbols:
                free_symbols.append(SympyExpression(free_symbol))
                free_symbols.append(free_symbol)
            sympy_result = tracing.run_sympy(sympy_expr.is_polynomial, *free_symbols)
            return from_bool(sympy_result)

        var = v[0]
        if var is SymbolNull:
            return SymbolTrue
        elif var.has_form("List", None):
            if len(var.elements) == 0:
                evaluation.message("PolynomialQ", "novar")
                return
            sympy_var = [x.to_sympy() for x in var.elements]
        else:
            sympy_var = [var.to_sympy()]

        sympy_expr = expr.to_sympy()
        sympy_result = tracing.run_sympy(
            sympy_expr.is_polynomial, *[x for x in sympy_var]
        )
        return from_bool(sympy_result)


class PowerExpand(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/PowerExpand.html</url>

    <dl>
      <dt>'PowerExpand'[$expr$]
      <dd>expands out powers of the form $(x^y)^z$ and $(x y)^z$ in $expr$.
    </dl>

    >> PowerExpand[(a ^ b) ^ c]
     = a ^ (b c)
    >> PowerExpand[(a * b) ^ c]
     = a ^ c b ^ c

    'PowerExpand' is not correct without certain assumptions:
    >> PowerExpand[(x ^ 2) ^ (1/2)]
     = x
    """

    rules = {
        "PowerExpand[(x_ ^ y_) ^ z_]": "x ^ (y * z)",
        "PowerExpand[(x_ * y_) ^ z_]": "x ^ z * y ^ z",
        "PowerExpand[Log[x_ ^ y_]]": "y * Log[x]",
        "PowerExpand[x_Plus]": "PowerExpand /@ x",
        "PowerExpand[x_Times]": "PowerExpand /@ x",
        "PowerExpand[x_Power]": "PowerExpand /@ x",
        "PowerExpand[x_List]": "PowerExpand /@ x",
        "PowerExpand[x_Rule]": "PowerExpand /@ x",
        "PowerExpand[other_]": "other",
    }
    summary_text = "expand out powers"


class Together(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Together.html</url>

    <dl>
      <dt>'Together'[$expr$]
      <dd>writes sums of fractions in $expr$ together.
    </dl>

    >> Together[a / c + b / c]
     = (a + b) / c
    'Together' operates on lists:
    >> Together[{x / (y+1) + x / (y+1)^2}]
     = {x (2 + y) / (1 + y) ^ 2}
    But it does not touch other functions:
    >> Together[f[a / c + b / c]]
     = f[a / c + b / c]
    """

    attributes = A_LISTABLE | A_PROTECTED
    summary_text = "put over a common denominator"

    def eval(self, expr, evaluation):
        "Together[expr_]"

        expr_sympy = expr.to_sympy()
        if expr_sympy is None:
            return None
        result = sympy.together(expr_sympy)
        result = from_sympy(result)
        result = cancel(result)
        return result


class Variables(Builtin):
    # This builtin is incomplete. See the failing test case below.
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Variables.html</url>

    <dl>
      <dt>'Variables'[$expr$]
      <dd>gives a list of the variables that appear in the polynomial $expr$.
    </dl>

    >> Variables[a x^2 + b x + c]
     = {a, b, c, x}
    >> Variables[{a + b x, c y^2 + x/2}]
     = {a, b, c, x, y}
    >> Variables[x + Sin[y]]
     = {x, Sin[y]}
    """
    summary_text = "list of variables in a polynomial"

    def eval(self, expr, evaluation):
        "Variables[expr_]"

        variables = find_all_vars(expr)

        variables = ListExpression(*variables)
        variables.sort()  # MMA doesn't do this
        return variables
