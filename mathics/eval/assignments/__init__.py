"""
Evaluation routines and associated code for Built-in function found under module
mathics.builtins.assignments.
"""

from mathics.eval.assignments.assignment import (
    ASSIGNMENT_FUNCTION_MAP,
    eval_assign,
    get_unwrapped_name,
)

__all__ = [
    "ASSIGNMENT_FUNCTION_MAP",
    "eval_assign",
    "get_unwrapped_name",
]
