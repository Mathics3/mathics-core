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

from mathics.core.convert.sympy import SympyExpression
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

    # Evaluate the expr first in case it hasn't been already,
    # because some functions are not themselves sympy-enabled
    # if they always get rewritten to one that is.
    try:
        new_expr = expr.evaluate(evaluation)
        if new_expr:
            expr = new_expr
    except Exception:
        pass
    if debug >= 2:
        print("post-eval", expr)

    # Ask the expr Expression to generate a sympy expression and handle errors
    sympy_expr = expr.to_sympy(raise_on_error=CompileError)
    if isinstance(sympy_expr, SympyExpression):
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
