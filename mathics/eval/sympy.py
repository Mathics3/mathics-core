"""
Evaluation of SymPy functions
"""

from typing import Optional

import sympy

import mathics.eval.tracing as tracing
from mathics.core.convert.sympy import from_sympy, to_numeric_sympy_args
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation


def eval_sympy(self, z: BaseElement, evaluation: Evaluation) -> Optional[BaseElement]:
    """
    Evaluate element `z` converting it to SymPy and back to Mathics3.
    If an exception is raised we return None.

    This version is called not-wrapped in a thread on systems like
    emscripten that do not support Python-style threading.
    """
    sympy_args = to_numeric_sympy_args(z, evaluation)
    if self.sympy_name is None:
        return
    sympy_fn = getattr(sympy, self.sympy_name)
    try:
        return from_sympy(tracing.run_sympy(sympy_fn, *sympy_args))
    except Exception:
        return
