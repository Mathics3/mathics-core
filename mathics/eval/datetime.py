"""
Implementation of the evaluation of datetime related expressions.
"""

import sys
import time
from datetime import datetime
from typing import Optional

from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation

PAUSE_TICKS_PER_SECOND = 1000


def valid_time_from_expression(t: BaseElement, evaluation: Evaluation) -> float:
    """
    Try to evaluate t to a nonnegative float number.
    """
    t = t.evaluate(evaluation)
    if not t.is_numeric(evaluation):
        raise ValueError
    try:
        timeout = float(t.to_python())
    except TypeError:
        raise ValueError
    if timeout < 0:
        raise ValueError
    return timeout


def eval_pause(sleeptime: float, evaluation):
    """
    Do a pause for `sleeptime`. If sleep
    """
    # Due to the GIL lock, if we implement this method
    # by just calling `time.sleep(sleeptime)`, the
    # evaluation would not be aware of `TimeoutException`
    # raised by an outer `TimeConstrained` expression.
    #
    # For this reason, the splitting of the sleep time is
    # needed.
    # It was also noticed in tests that in some platforms
    # the total time that takes n calls to time.sleep(delta_t)
    # can be appreciably larger than n*delta_t. For this reason,
    # we also need to check that inside the loop that the
    # enlapsed time at the i-esim iteration does not exceed
    # the  desired total time.

    steps = int(PAUSE_TICKS_PER_SECOND * sleeptime)
    step_duration = 1.0 / PAUSE_TICKS_PER_SECOND
    start = time.time()
    for _ in range(steps):
        time.sleep(step_duration)
        if evaluation.timeout:
            break
        if sleeptime < time.time() - start:
            break
    return


## @rocky rocky Jan 8, 2025
## See https://stackoverflow.com/questions/8420422/python-windows-equivalent-of-sigalrm
## for a more robust mechanism that uses Threading.
##Event to allow Pause or sleep to be canceled.


if sys.platform == "emscripten":
    # from timed_threads import SignalTimeout as TimeoutHandler

    def eval_timeconstrained(
        expr: BaseElement, timeout: float, failexpr: BaseElement, evaluation: Evaluation
    ) -> Optional[BaseElement]:
        """Evaluate a TimeConstrained expression"""
        evaluation.message("TimeConstrained", "tcns")

else:
    from timed_threads import ThreadingTimeout as TimeoutHandler

    def eval_timeconstrained(
        expr: BaseElement, timeout: float, failexpr: BaseElement, evaluation: Evaluation
    ) -> Optional[BaseElement]:
        """Evaluate a TimeConstrained expression"""

        try:
            evaluation.timeout_queue.append((timeout, datetime.now().timestamp()))
            request = lambda: expr.evaluate(evaluation)
            done = False
            with TimeoutHandler(timeout) as to_ctx_mgr:
                assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
                result = request()
                done = True
            if done:
                evaluation.timeout_queue.pop()
                return result
        except Exception:
            evaluation.timeout_queue.pop()
            raise
        evaluation.timeout_queue.pop()
        return failexpr.evaluate(evaluation)
