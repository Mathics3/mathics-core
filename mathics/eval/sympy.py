"""
Evaluation of SymPy functions
"""

import sys
from queue import Queue
from threading import Thread
from typing import Optional

import sympy

import mathics.eval.tracing as tracing
from mathics.core.convert.sympy import from_sympy, to_numeric_sympy_args
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation


def eval_sympy_unconstrained(
    self, z: BaseElement, evaluation: Evaluation
) -> Optional[BaseElement]:
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


def eval_sympy_with_timeout(
    self, z: BaseElement, evaluation: Evaluation
) -> Optional[BaseElement]:
    """
    Evaluate an element `z` converting it to SymPy,
    and back to Mathics3.
    If an exception is raised we return None.

    This version is run in a thread, and checked for evaluation timeout.
    """

    if evaluation.timeout is None:
        return eval_sympy_unconstrained(self, z, evaluation)

    def _thread_target(queue) -> None:
        try:
            result = eval_sympy_unconstrained(self, z, evaluation)
            queue.put((True, result))
        except BaseException:
            exc_info = sys.exc_info()
            queue.put((False, exc_info))

    queue = Queue(maxsize=1)  # stores the result or exception

    def evaluate():
        return

    thread = Thread(target=_thread_target, args=(queue,))
    thread.start()
    while thread.is_alive():
        thread.join(0.001)
        if evaluation.timeout:
            # I can kill the thread.
            # just leave it...
            return None

    # pick the result and return
    success, result = queue.get()
    if success:
        return result
    else:
        raise result[1].with_traceback(result[2])


# Common top-level evaluation SymPy "eval" function:
eval_sympy = (
    eval_sympy_unconstrained
    if sys.platform in ("emscripten",)
    else eval_sympy_with_timeout
)
