"""
Evaluation of sympy functions
"""

import sys
from queue import Queue
from threading import Thread

import sympy

import mathics.eval.tracing as tracing
from mathics.core.convert.sympy import from_sympy, to_numeric_sympy_args


def eval_sympy_unconstrained(self, z, evaluation):
    """
    Evaluate an expression converting it to Sympy
    and back to Mathics.
    """
    sympy_args = to_numeric_sympy_args(z, evaluation)
    if self.sympy_name is None:
        return
    sympy_fn = getattr(sympy, self.sympy_name)
    try:
        return from_sympy(tracing.run_sympy(sympy_fn, *sympy_args))
    except Exception:
        return


def eval_sympy_with_timeout(self, z, evaluation):
    """
    Evaluate an expression converting it to Sympy,
    and back to Mathics.
    This version put the evaluation in a thread,
    and check each some time if the evaluation
    reached a timeout.
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
        raise result[0].with_traceback(result[1], result[2])


eval_sympy = (
    eval_sympy_unconstrained
    if sys.platform in ("emscripten",)
    else eval_sympy_with_timeout
)
