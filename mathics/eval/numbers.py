import sympy

from mathics.core.convert.sympy import from_sympy
from mathics.core.expression import Expression
from mathics.core.symbols import SymbolPlus


def cancel(expr):
    if expr.has_form("Plus", None):
        return Expression(SymbolPlus, *[cancel(element) for element in expr.elements])
    else:
        try:
            result = expr.to_sympy()
            if result is None:
                return None

            # result = sympy.powsimp(result, deep=True)
            result = sympy.cancel(result)

            # cancel factors out rationals, so we factor them again
            result = sympy_factor(result)

            return from_sympy(result)
        except sympy.PolynomialError:
            # e.g. for non-commutative expressions
            return expr


def sympy_factor(expr_sympy):
    try:
        result = sympy.together(expr_sympy)
        result = sympy.factor(result)
    except sympy.PolynomialError:
        return expr_sympy
    return result
