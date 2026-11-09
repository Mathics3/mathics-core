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
        if evaluation.interrupt_request is not None:
            # Ctrl-C while the evaluation runs on its own thread: the
            # interrupt menu runs here, as a signal would have cut into
            # the sleep on the main thread.
            evaluation.check_stopped()
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
    import ctypes
    import threading

    from timed_threads import async_raise

    from mathics.core.interrupt import TimeConstrainedTimeout

    # How often a fired timer raises again while its body is still
    # running, in case a bare ``except:`` swallowed the first one.
    REFIRE_INTERVAL = 0.05

    # The TimeConstrained blocks being evaluated in this thread,
    # innermost last.
    _active = threading.local()

    def _active_constraints() -> list:
        stack = getattr(_active, "stack", None)
        if stack is None:
            stack = _active.stack = []
        return stack

    def _clear_pending_async_exception(thread_id: int) -> None:
        """Discard an asynchronous exception that was set for
        ``thread_id`` but not delivered yet."""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_ulong(thread_id), None)

    class _TimeConstraint:
        """The timer of one TimeConstrained block.

        When the time runs out, the timer thread raises
        TimeConstrainedTimeout in the evaluating thread, and raises it
        again every REFIRE_INTERVAL seconds until the block is
        finished.

        No lock is shared with the evaluating thread: an asynchronous
        exception that arrives just after a ``lock.acquire()`` leaves
        the lock held for good. finish() instead marks the block as
        finished and then waits for the timer thread, so that no
        timeout can be raised once it has returned.
        """

        def __init__(self, seconds: float):
            self.seconds = seconds
            self.thread_id = threading.get_ident()
            self.timed_out = False
            self.finished = False
            self.timer: Optional[threading.Timer] = None

        def _start_timer(self, seconds: float) -> None:
            timer = threading.Timer(seconds, self._fire)
            timer.daemon = True
            timer.start()
            self.timer = timer

        def start(self) -> None:
            self._start_timer(self.seconds)

        def _fire(self) -> None:
            # Runs in the timer thread.
            if self.finished:
                return
            self.timed_out = True
            async_raise(self.thread_id, TimeConstrainedTimeout)
            if not self.finished:
                self._start_timer(REFIRE_INTERVAL)

        def finish(self) -> None:
            """Stop the timer for good. Can be called more than once."""
            self.finished = True
            timer = self.timer
            while timer is not None:
                timer.cancel()
                # A _fire() that is running may still raise and start
                # one more timer; wait for it to return.
                timer.join()
                if self.timer is timer:
                    break
                timer = self.timer
            if self.timed_out:
                # Our exception may still be pending; it must not be
                # delivered after we return. This may also discard one
                # raised for an outer TimeConstrained;
                # eval_timeconstrained raises that one again.
                _clear_pending_async_exception(self.thread_id)

    def eval_timeconstrained(
        expr: BaseElement, timeout: float, failexpr: BaseElement, evaluation: Evaluation
    ) -> Optional[BaseElement]:
        """Evaluate a TimeConstrained expression"""

        constraints = _active_constraints()
        outer_constraints = list(constraints)
        depth = len(constraints)
        queue_depth = len(evaluation.timeout_queue)
        constraint = _TimeConstraint(timeout)
        result = None
        constraints.append(constraint)
        evaluation.timeout_queue.append((timeout, datetime.now().timestamp()))
        try:
            try:
                constraint.start()
                result = expr.evaluate(evaluation)
            finally:
                constraint.finish()
        except TimeConstrainedTimeout:
            if not constraint.timed_out:
                # The time of an outer TimeConstrained ran out.
                raise
        finally:
            # finish() again, in case a timeout came in before the
            # first call had marked the block as finished. Truncate
            # rather than pop: an outer timeout may have cut short the
            # clean-up of an inner TimeConstrained.
            while True:
                try:
                    constraint.finish()
                    break
                except TimeConstrainedTimeout:
                    pass
            del constraints[depth:]
            del evaluation.timeout_queue[queue_depth:]

        # finish() may have discarded the pending exception of an
        # outer TimeConstrained whose time has run out too: hand the
        # timeout on to it.
        if any(outer.timed_out for outer in outer_constraints):
            raise TimeConstrainedTimeout

        # Whatever the body returned, if the time ran out, the result
        # is the failure expression: the timeout may have been
        # swallowed on the way, leaving a partial result.
        if constraint.timed_out:
            return failexpr.evaluate(evaluation)
        return result
