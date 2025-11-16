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

import inspect

import scipy
import sympy

from mathics.core.convert.sympy import SympyExpression, mathics_to_sympy
from mathics.core.symbols import strip_context
from mathics.core.util import print_expression_tree, print_sympy_tree


# TODO: not in use yet
# Add functions not found in scipy or numpy here.
# Hopefully they are just thin adapater layers.
# TODO: let's see how much is really needed here, and possibly consider moving
# them to the Builtin somehow
class AdditionalMappings:
    def hyppfq(p, q, x):
        if len(p) == 1 and len(q) == 1:
            return scipy.special.hyp1f1(p[0], q[0], x)
        else:
            raise Exception(f"can't handle hyppfq({p}, {q}, x)")


# mappings = [dict(AdditionalMappings.__dict__), "numpy"]


class CompileError(Exception):
    pass


def plot_compile(evaluation, expr, names, debug=0):
    """Compile the specified expression as a function of the given names"""

    if debug >= 2:
        print("=== compiling expr")
        print_expression_tree(expr)

    # Ask the expr Expression to generate a sympy expression and handle errors
    try:
        sympy_expr = expr.to_sympy()
    except Exception as oops:
        raise CompileError(f"{expr}.to_sympy() failed: {oops}")
    if isinstance(sympy_expr, SympyExpression):
        if debug:
            # duplicates lookup logic in mathics.core.convert.sympy
            lookup_name = expr.get_lookup_name()
            builtin = mathics_to_sympy.get(lookup_name)
            if builtin:
                sympy_name = getattr(builtin, "sympy_name", None) if builtin else None
                print(f"compile: Invalid sympy_expr {sympy_expr}")
                print(f"compile: {builtin}.sympy_name is {repr(sympy_name)}")
            else:
                print(f"compile: {lookup_name} not registered with mathics_to_sympy")
        raise CompileError(f"{expr.head}.to_sympy returns invalid sympy expr.")

    # Strip symbols in sympy expression of context.
    subs = {
        sym: sympy.Symbol(strip_context(str(sym))) for sym in sympy_expr.free_symbols
    }
    sympy_expr = sympy_expr.subs(subs)

    if debug >= 2:
        print("=== equivalent sympy", type(sympy_expr))
        print_sympy_tree(sympy_expr)

    # Ask sympy to generate a function that will evaluate the expr.
    # Use numpy and scipy to do the evaluation so that operations are vectorized.
    # Augment the default numpy mappings with some additional ones not handled by default.
    try:
        symbols = sympy.symbols(names)
        # compiled_function = sympy.lambdify(symbols, sympy_expr, mappings)
        compiled_function = sympy.lambdify(
            symbols, sympy_expr, modules=["numpy", "scipy"]
        )
    except Exception as oops:
        raise CompileError(f"error compiling sympy expr {sympy_expr}: {oops}")

    if debug >= 2:
        print("=== compiled python")
        print(inspect.getsource(compiled_function))

    return compiled_function
