"""
Polynomial-like Routines.
"""

from typing import Final, FrozenSet

import sympy

import mathics.eval.tracing as tracing
from mathics.core.atoms import Integer, Integer0, IntegerM1, Number
from mathics.core.convert.sympy import from_sympy
from mathics.core.expression import Expression
from mathics.core.symbols import (
    SYMPY_SYMBOL_PREFIX,
    Atom,
    Symbol,
    SymbolPlus,
    SymbolPower,
    SymbolTimes,
)
from mathics.core.systemsymbols import (
    SymbolAnd,
    SymbolCos,
    SymbolCosh,
    SymbolCot,
    SymbolCoth,
    SymbolEqual,
    SymbolEquivalent,
    SymbolGreater,
    SymbolGreaterEqual,
    SymbolImplies,
    SymbolLess,
    SymbolNand,
    SymbolNor,
    SymbolOr,
    SymbolSin,
    SymbolSinh,
    SymbolTan,
    SymbolTanh,
    SymbolUnequal,
    SymbolXor,
)

# Trigonomic and hypergeometric function symbols
TRIG_OPERATORS: Final[FrozenSet] = frozenset(
    [
        SymbolSin,
        SymbolCos,
        SymbolTan,
        SymbolCot,
        SymbolSinh,
        SymbolCosh,
        SymbolTanh,
        SymbolCoth,
    ]
)

# Infix relational operators. As of SymPy 1.14, SymPy's
# polymonial-like operations do not support relational operators.
# Therefore, in Mathics3 operations like Expand or Apart, we have to
# split this out.
RELATIONAL_OPERATORS: Final[FrozenSet] = frozenset(
    [
        SymbolAnd,
        SymbolEqual,
        SymbolEquivalent,
        SymbolGreater,
        SymbolGreaterEqual,
        SymbolImplies,
        SymbolLess,
        SymbolNand,
        SymbolNor,
        SymbolOr,
        SymbolUnequal,
        SymbolXor,
    ]
)


def eval_Apart(expr, var: Symbol):
    """
    Evaluation routine for:
    Apart[expr_, var_Symbol]
    """

    operator = expr.get_head()
    if (expr.get_head()) in RELATIONAL_OPERATORS:
        expanded_operands = [eval_Apart(operand, var) for operand in expr.elements]
        return Expression(operator, *expanded_operands)

    expr_sympy = expr.to_sympy()
    var_sympy = var.to_sympy()
    # If the expression cannot be handled by SymPy, just return it.
    if expr_sympy is None or var_sympy is None:
        return expr

    try:
        result_sympy = tracing.run_sympy(sympy.apart, expr_sympy, var_sympy)
        return from_sympy(result_sympy)
    except sympy.PolynomialError:
        # raised e.g. for apart(sin(1/(x**2-y**2)))
        return expr


def expand_polynomial(expr, numerator=True, denominator=False, deep=False, **kwargs):
    """expands out products and positive integer powers in expr.  If
    "option pattern" is supplied, we leave unexpanded any parts of expr
    that are free of the pattern patt.
    """

    # Polynomial expansion expects a nonnegative modules. When
    # given a negative value, give back the "canonic" value: 0.
    # Note: SymPy will give back an error, so we have to do this
    # soonish.
    if (modulus := kwargs["modulus"]) is not None and modulus <= 0:
        return Integer0

    target_pat = kwargs.get("pattern", None)
    if target_pat:
        evaluation = kwargs["evaluation"]

    trig_expand = kwargs.get("trig", False)

    def expand_polynomial_inner(expr):
        """Recursive expand_polymomial. We make use of closure
        variables trig_expand, target_pat, numerator, and denominator
        below without having to pass these explicitly as parameters.
        """

        operator = expr.get_head()
        if (expr.get_head()) in RELATIONAL_OPERATORS:
            # Thanks to ad-si (Woxi) for the code suggestion below and axkr (Symja) for the
            # the list of operators above.
            expanded_operands = [
                expand_polynomial_inner(operand) for operand in expr.elements
            ]
            return Expression(operator, *expanded_operands)

        # A special case for trigonometric functions
        if trig_expand:
            if operator in TRIG_OPERATORS:
                theta = expr.elements[0]
                if (target_pat is not None) and theta.is_free(target_pat, evaluation):
                    return expr
                if deep:
                    theta = expand_polynomial_inner(theta)

                if theta.has_form("Plus", 2, None):
                    x, y = theta.elements[0], Expression(
                        SymbolPlus, *theta.elements[1:]
                    )
                    if operator is SymbolSin:
                        a = Expression(
                            SymbolTimes,
                            expand_polynomial_inner(Expression(SymbolSin, x)),
                            expand_polynomial_inner(Expression(SymbolCos, y)),
                        )

                        b = Expression(
                            SymbolTimes,
                            expand_polynomial_inner(Expression(SymbolCos, x)),
                            expand_polynomial_inner(Expression(SymbolSin, y)),
                        )
                        return expand_polynomial_inner(Expression(SymbolPlus, a, b))
                    elif operator is SymbolCos:
                        a = Expression(
                            SymbolTimes,
                            expand_polynomial_inner(Expression(SymbolCos, x)),
                            expand_polynomial_inner(Expression(SymbolCos, y)),
                        )

                        b = Expression(
                            SymbolTimes,
                            expand_polynomial_inner(Expression(SymbolSin, x)),
                            expand_polynomial_inner(Expression(SymbolSin, y)),
                        )

                        return expand_polynomial_inner(Expression(SymbolPlus, a, -b))
                    elif operator is SymbolSinh:
                        a = Expression(
                            SymbolTimes,
                            expand_polynomial_inner(Expression(SymbolSinh, x)),
                            expand_polynomial_inner(Expression(SymbolCosh, y)),
                        )

                        b = Expression(
                            SymbolTimes,
                            expand_polynomial_inner(Expression(SymbolCosh, x)),
                            expand_polynomial_inner(Expression(SymbolSinh, y)),
                        )

                        return expand_polynomial_inner(Expression(SymbolPlus, a, b))
                    elif operator is SymbolCosh:
                        a = Expression(
                            SymbolTimes,
                            expand_polynomial_inner(Expression(SymbolCosh, x)),
                            expand_polynomial_inner(Expression(SymbolCosh, y)),
                        )

                        b = Expression(
                            SymbolTimes,
                            expand_polynomial_inner(Expression(SymbolSinh, x)),
                            expand_polynomial_inner(Expression(SymbolSinh, y)),
                        )

                        return expand_polynomial_inner(Expression(SymbolPlus, a, b))
                    elif operator is Symbol("Tan"):
                        a = expand_polynomial_inner(Expression(SymbolSin, theta))
                        b = Expression(
                            SymbolPower,
                            expand_polynomial_inner(Expression(SymbolCos, theta)),
                            IntegerM1,
                        )
                        return expand_polynomial_inner(Expression(SymbolTimes, a, b))
                    elif operator is SymbolCot:
                        a = expand_polynomial_inner(Expression(SymbolCos, theta))
                        b = Expression(
                            SymbolPower,
                            expand_polynomial_inner(Expression(SymbolSin, theta)),
                            IntegerM1,
                        )
                        return expand_polynomial_inner(Expression(SymbolTimes, a, b))
                    elif operator is SymbolTanh:
                        a = expand_polynomial_inner(Expression(SymbolSinh, theta))
                        b = Expression(
                            SymbolPower,
                            expand_polynomial_inner(Expression(SymbolCosh, theta)),
                            IntegerM1,
                        )
                        return expand_polynomial_inner(Expression(SymbolTimes, a, b))
                    elif operator is SymbolCoth:
                        a = expand_polynomial_inner(
                            Expression(SymbolTimes, SymbolCosh, theta)
                        )
                        b = Expression(
                            SymbolPower,
                            expand_polynomial_inner(Expression(SymbolSinh, theta)),
                            IntegerM1,
                        )
                        return expand_polynomial_inner(Expression(a, b))

        sub_exprs = []

        def store_sub_expr(expr):
            sub_exprs.append(expr)
            result = sympy.Symbol(SYMPY_SYMBOL_PREFIX + str(len(sub_exprs) - 1))
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
            operator = expr.get_head()

            if operator is SymbolPower:
                # sympy won't expand `(a + b) / x` to `a / x + b / x` if denominator is False
                # if denominator is False we store negative powers to prevent this.
                n1 = elements[1].get_int_value()
                if not denominator and n1 is not None and n1 < 0:
                    return store_sub_expr(expr)
                return tracing.run_sympy(
                    sympy.Pow, *[convert_sympy(element) for element in elements]
                )
            elif operator is SymbolTimes:
                return tracing.run_sympy(
                    sympy.Mul, *[convert_sympy(element) for element in elements]
                )
            elif operator is SymbolPlus:
                return tracing.run_sympy(
                    sympy.Add, *[convert_sympy(element) for element in elements]
                )
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
                    expr.head,
                    *[unconvert_subexprs(element) for element in expr.elements],
                )

        sympy_expr = convert_sympy(expr)
        if deep:
            # thread over everything
            for (
                i,
                sub_expr,
            ) in enumerate(sub_exprs):
                if not isinstance(sub_expr, Atom):
                    head = expand_polynomial_inner(sub_expr.head)  # also expand head
                    elements = sub_expr.elements
                    if target_pat:
                        elements = [
                            (
                                element
                                if element.is_free(target_pat, evaluation)
                                else expand_polynomial_inner(element)
                            )
                            for element in elements
                        ]
                    else:
                        elements = [
                            expand_polynomial_inner(element) for element in elements
                        ]
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
                                    else expand_polynomial_inner(element)
                                )
                                for element in elements
                            ]
                        else:
                            elements = [
                                expand_polynomial_inner(element) for element in elements
                            ]
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

        if numerator and denominator:
            # don't expand fractions when modulus is True
            if hints["modulus"] is not None:
                hints["frac"] = True
        else:
            # setting both True doesn't expand denominator
            hints["numer"] = numerator
            hints["denom"] = denominator

        sympy_expr = sympy_expr.expand(**hints)
        result = from_sympy(sympy_expr)
        result = unconvert_subexprs(result)
        return result

        return expand_polynomial_inner(expr)

    return expand_polynomial_inner(expr)


def find_all_vars(expr):
    variables = set()

    def find_vars(e, e_sympy):
        assert e_sympy is not None
        operator = e.get_head()
        if e_sympy.is_constant():
            return
        elif isinstance(e, Symbol):
            variables.add(e)
        elif operator in (SymbolPlus, SymbolTimes):
            for lv in e.elements:
                lv_sympy = lv.to_sympy()
                if lv_sympy is not None:
                    find_vars(lv, lv_sympy)
        elif operator is SymbolPower:
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
            result.add(from_sympy(tracing.run_sympy(sympy.Max, *[e for e in expos])))
    return sorted(result)
