"""
Evaluation of sympy functions
"""

import sys
from queue import Queue
from threading import Thread

import sympy

import mathics.eval.tracing as tracing
from mathics.core.convert.sympy import from_sympy, to_numeric_sympy_args


def eval_sympy(self, z, evaluation):
    """
    Evaluate expr using `Sympy`
    """

    def evaluate():
        sympy_args = to_numeric_sympy_args(z, evaluation)
        if self.sympy_name is None:
            return
        sympy_fn = getattr(sympy, self.sympy_name)
        try:
            return from_sympy(tracing.run_sympy(sympy_fn, *sympy_args))
        except Exception:
            return

    if evaluation.timeout is None:
        return evaluate()

    def _thread_target(request, queue) -> None:
        try:
            result = evaluate()
            queue.put((True, result))
        except BaseException:
            exc_info = sys.exc_info()
            queue.put((False, exc_info))

    queue = Queue(maxsize=1)  # stores the result or exception
    thread = Thread(target=_thread_target, args=(evaluate, queue))
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
