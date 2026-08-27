"""
Assumptions and functions that Use Assumptions.
"""

import sympy

# Note: it is important *not* use: from mathics.eval.tracing import run_sympy
# but instead import the module and access below as tracing.run_sympy.
# This allows us change where tracing.run_sympy points at runtime.
import mathics.eval.tracing as tracing
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation


def eval_Refine(
    expr,
    sympy_assumptions: sympy.assumptions.assume.AppliedPredicate | bool,
    evaluation: Evaluation,
) -> BaseElement:
    """
    Apply assumption-aware simplification rules to an expression.

    This function recursively traverses the expression tree and applies
    refinement rules based on the provided assumptions.

    Parameters:
        expr: The expression to refine
        assumptions: The assumptions (And of conditions, or True)
        evaluation: The Evaluation context

    Returns:
        The refined expression
    """
    try:
        sympy_expr = expr.to_sympy()
        sympy_expr_refined = tracing.run_sympy(
            sympy.refine, sympy_expr, sympy_assumptions
        )
        refined_expr = from_sympy(sympy_expr_refined)
    except Exception:
        return expr

    return refined_expr
