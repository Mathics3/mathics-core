"""
"Compile" an Expression by converting it to SymPy, then use sympy.lambdify
to turn it into a Python function that calls NumPy functions to evaluate it.

While possibly this provides an efficient function for point-wise evaluation,
the main goal is to use NumPy to perform vectorized operations on arrays,
which is a huge win for plotting.

This will need testing and building out to make it robustly applicable
to a wide array of expressions. So for now this is specific to plotting
and is used only when enabled, so it lives with the plotting functions.
Maybe eventually consider to move elsewhere if it seems to be more
widely useful.
"""

import scipy
import sympy

from mathics.core.symbols import strip_context
from mathics.core.util import print_expression_tree, print_sympy_tree

class AdditionalMappings:

    def hyppfq(p, q, x):
        if len(p) == 1 and len(q) == 1:
            return scipy.special.hyp1f1(p[0], q[0], x)
        else:
            raise Exception(f"can't handle hyppfq({p}, {q}, x)")

#mappings = [dict(AdditionalMappings.__dict__), "numpy"]

class CompileError(Exception):
    pass

def compile(evaluation, function, names):
    #print("=== compiling expr")
    #print_expression_tree(function)

    # Obtain sympy expr and strip context from free symbols.
    sympy_expr = function.to_sympy()
    subs = {
        sym: sympy.Symbol(strip_context(str(sym))) for sym in sympy_expr.free_symbols
    }
    sympy_expr = sympy_expr.subs(subs)

    #print("=== compiled sympy", type(sympy_expr))
    #print_sympy_tree(sympy_expr)

    # Ask sympy to generate a function that will evaluate the expr.
    # Use numpy to do the evaluation so that operations are vectorized.
    # Augment the default numpy mappings with some additional ones not handled by default.
    try:
        symbols = sympy.symbols(names)
        #compiled_function = sympy.lambdify(symbols, sympy_expr, mappings)
        compiled_function = sympy.lambdify(symbols, sympy_expr, modules=["numpy", "scipy"])
    except Exception as oops:
        raise CompileError(f"error compiling sympy expr {sympy_expr}: {oops}")

    return compiled_function
