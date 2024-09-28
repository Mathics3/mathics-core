"""
Mathics3 builtins from mathics.core.numbers.hyperbolic
"""

from sympy import Symbol as SympySymbol

from mathics.core.convert.sympy import from_sympy


def eval_ComplexExpand(expr, vars):
    sympy_expr = expr.to_sympy()
    if hasattr(vars, "elements"):
        sympy_vars = {v.to_sympy() for v in vars.elements}
    else:
        sympy_vars = {vars.to_sympy()}
    # All vars are assumed to be real
    replaces = [
        (fs, SympySymbol(fs.name, real=True))
        for fs in sympy_expr.free_symbols
        if fs not in sympy_vars
    ]
    sympy_expr = sympy_expr.subs(replaces)
    return from_sympy(sympy_expr.expand(complex=True))
