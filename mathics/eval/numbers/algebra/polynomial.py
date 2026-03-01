"""
Polynomial-like Routines.
"""

import sympy

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


def expand_polynomial(expr, numer=True, denom=False, deep=False, **kwargs):
    """expands out products and positive integer powers in expr.  If
    "option pattern" is supplied, we leave unexpanded any parts of expr
    that are free of the pattern patt.
    """

    # FIXME: the below is not the right way to supply the default arguments
    # numer, demom, deep and **kwargs.
    def _expand_polynomial(expr):
        return expand_polynomial(expr, numer=numer, denom=denom, deep=deep, **kwargs)

    # Polymonmial expansion expects a nonnegative modules. When
    # given a negative value, give back the "canonic" value: 0.
    # Note: SymPy will give back an error, so we have to do this
    # soonish.
    if kwargs["modulus"] is not None and kwargs["modulus"] <= 0:
        return Integer0

    target_pat = kwargs.get("pattern", None)
    if target_pat:
        evaluation = kwargs["evaluation"]

    operator = expr.get_head()
    if (expr.get_head()) in (
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
    ):
        # Thanks to ad-si (Woxi) for the code suggestion below and axkr (Symja) for the
        # the list of operators above.
        expanded_operands = [_expand_polynomial(operand) for operand in expr.elements]
        return Expression(operator, *expanded_operands)

    # A special case for trigonometric functions
    if kwargs.get("trig", False):
        if operator in (
            SymbolSin,
            SymbolCos,
            SymbolTan,
            SymbolCot,
            SymbolSinh,
            SymbolCosh,
            SymbolTanh,
            SymbolCoth,
        ):
            theta = expr.elements[0]
            if (target_pat is not None) and theta.is_free(target_pat, evaluation):
                return expr
            if deep:
                theta = _expand_polynomial(theta)

            if theta.has_form("Plus", 2, None):
                x, y = theta.elements[0], Expression(SymbolPlus, *theta.elements[1:])
                if operator is SymbolSin:
                    a = Expression(
                        SymbolTimes,
                        _expand_polynomial(Expression(SymbolSin, x)),
                        _expand_polynomial(Expression(SymbolCos, y)),
                    )

                    b = Expression(
                        SymbolTimes,
                        _expand_polynomial(Expression(SymbolCos, x)),
                        _expand_polynomial(Expression(SymbolSin, y)),
                    )
                    return _expand_polynomial(Expression(SymbolPlus, a, b))
                elif operator is SymbolCos:
                    a = Expression(
                        SymbolTimes,
                        _expand_polynomial(Expression(SymbolCos, x)),
                        _expand_polynomial(Expression(SymbolCos, y)),
                    )

                    b = Expression(
                        SymbolTimes,
                        _expand_polynomial(Expression(SymbolSin, x)),
                        _expand_polynomial(Expression(SymbolSin, y)),
                    )

                    return _expand_polynomial(Expression(SymbolPlus, a, -b))
                elif operator is SymbolSinh:
                    a = Expression(
                        SymbolTimes,
                        _expand_polynomial(Expression(SymbolSinh, x)),
                        _expand_polynomial(Expression(SymbolCosh, y)),
                    )

                    b = Expression(
                        SymbolTimes,
                        _expand_polynomial(Expression(SymbolCosh, x)),
                        _expand_polynomial(Expression(SymbolSinh, y)),
                    )

                    return _expand_polynomial(Expression(SymbolPlus, a, b))
                elif operator is SymbolCosh:
                    a = Expression(
                        SymbolTimes,
                        _expand_polynomial(Expression(SymbolCosh, x)),
                        _expand_polynomial(Expression(SymbolCosh, y)),
                    )

                    b = Expression(
                        SymbolTimes,
                        _expand_polynomial(Expression(SymbolSinh, x)),
                        _expand_polynomial(Expression(SymbolSinh, y)),
                    )

                    return _expand_polynomial(Expression(SymbolPlus, a, b))
                elif operator is Symbol("Tan"):
                    a = _expand_polynomial(Expression(SymbolSin, theta))
                    b = Expression(
                        SymbolPower,
                        _expand_polynomial(Expression(SymbolCos, theta)),
                        IntegerM1,
                    )
                    return _expand_polynomial(Expression(SymbolTimes, a, b))
                elif operator is SymbolCot:
                    a = _expand_polynomial(Expression(SymbolCos, theta))
                    b = Expression(
                        SymbolPower,
                        _expand_polynomial(Expression(SymbolSin, theta)),
                        IntegerM1,
                    )
                    return _expand_polynomial(Expression(SymbolTimes, a, b))
                elif operator is SymbolTanh:
                    a = _expand_polynomial(Expression(SymbolSinh, theta))
                    b = Expression(
                        SymbolPower,
                        _expand_polynomial(Expression(SymbolCosh, theta)),
                        IntegerM1,
                    )
                    return _expand_polynomial(Expression(SymbolTimes, a, b))
                elif operator is SymbolCoth:
                    a = _expand_polynomial(Expression(SymbolTimes, SymbolCosh, theta))
                    b = Expression(
                        SymbolPower,
                        _expand_polynomial(Expression(SymbolSinh, theta)),
                        IntegerM1,
                    )
                    return _expand_polynomial(Expression(a, b))

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
                head = _expand_polynomial(sub_expr.head)  # also expand head
                elements = sub_expr.elements
                if target_pat:
                    elements = [
                        (
                            element
                            if element.is_free(target_pat, evaluation)
                            else _expand_polynomial(element)
                        )
                        for element in elements
                    ]
                else:
                    elements = [_expand_polynomial(element) for element in elements]
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
                                else _expand_polynomial(element)
                            )
                            for element in elements
                        ]
                    else:
                        elements = [_expand_polynomial(element) for element in elements]
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
