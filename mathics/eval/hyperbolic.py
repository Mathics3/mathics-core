"""
Mathics3 builtins from mathics.core.numbers.hyperbolic
"""
from mathics.core.convert.sympy import from_sympy


def eval_ComplexExpand(expr, vars):
    sympy_expr = expr.to_sympy()
    # Turn Re[x] -> x and remove Im[x] for all variables X that are not in vars.
    return from_sympy(sympy_expr.expand(complex=True))
