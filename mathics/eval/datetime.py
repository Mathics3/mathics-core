"""
Implementation of the evaluation of datetime related expressions.
"""

import sys
from datetime import datetime
from typing import Optional

from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation


def valid_time_from_expression(
    t: BaseElement, evaluation: Evaluation
) -> Optional[float]:
    """
    Try to evaluate t to a nonnegative float number.
    """
    t = t.evaluate(evaluation)
    if not t.is_numeric(evaluation):
        evaluation.message("TimeConstrained", "timc", t)
        raise ValueError
    try:
        timeout = float(t.to_python())
    except TypeError:
        raise ValueError

    if timeout < 0:
        evaluation.message("TimeConstrained", "timc", t)
        raise ValueError
    return timeout


if sys.platform == "emscripten":
    from stopit import SignalTimeout as TimeoutHandler

    def eval_timeconstrained(
        expr: BaseElement, timeout: float, failexpr: BaseElement, evaluation: Evaluation
    ) -> Optional[BaseElement]:
        """Evaluate a TimeConstrained expression"""
        evaluation.message("TimeConstrained", "tcns")

else:
    from stopit import ThreadingTimeout as TimeoutHandler

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
