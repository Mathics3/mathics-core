# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.trace
"""
from inspect import isfunction, ismethod
from test.helper import evaluate, session
from typing import Any, Callable, Optional

import pytest

import mathics.eval.tracing
from mathics import version_info
from mathics.core.evaluation import Evaluation
from mathics.core.interrupt import AbortInterrupt
from mathics.eval.tracing import TraceEvent

trace_evaluation_calls = 0


def test_TraceEvaluation():
    """
    Basic test of TraceEvaluate[]
    """
    old_recursion_limit = evaluate("$RecursionLimit")
    old_evaluation_hook = mathics.eval.tracing.print_evaluate

    def counting_print_evaluate(
        expr, evaluation: Evaluation, status: str, fn: Callable, orig_expr=None
    ) -> Optional[Any]:
        """
        A replacement for mathics.eval.tracing.print_evaluate() that counts the
        number of evaluation calls.
        """
        global trace_evaluation_calls
        trace_evaluation_calls += 1
        assert status in ("Evaluating", "Returning", "Rewriting")
        if "cython" not in version_info:
            assert isfunction(fn), "Expecting 4th argument to be a function"
        return None

    try:
        # Set a small recursion limit,
        # Replace TraceEvaluation's print function something that counts evaluation
        # calls, and then force a RecursionLimit Error.
        evaluate("$RecursionLimit = 40")
        assert mathics.eval.tracing.print_evaluate == old_evaluation_hook
        evaluate("f[x_] := x + f[x-1]; f[0] = 0")
        global trace_evaluation_calls
        trace_evaluation_calls = 0
        mathics.eval.tracing.print_evaluate = (
            mathics.eval.tracing.trace_evaluate_on_call
        ) = mathics.eval.tracing.trace_evaluate_on_return = counting_print_evaluate
        evaluate("f[30] // TraceEvaluation")

    except AbortInterrupt:
        # We should get an AbortInterrupt from exceeding RecursionLimit in evaluating f[30]
        assert trace_evaluation_calls != 0, "TraceEvaluate[] should have counted steps"

        # Clear evaluation-call count and then check that TraceEvaluation restored
        # ts print hook. We do this by running another evaluate and checking
        # that nothing happened.
        trace_evaluation_calls = 0
        evaluate("1+2")
        assert trace_evaluation_calls == 0
    else:
        pytest.xfail("We should have raised an AbortInterrupt in evaluation")
    finally:
        # Just in case, restore everything back to what it was before running this test.
        mathics.eval.tracing.print_evaluate = old_evaluation_hook
        old_recursion_limit = evaluate(f"$RecursionLimit = {old_recursion_limit.value}")
    assert mathics.eval.tracing.print_evaluate == old_evaluation_hook


event_queue = []


def test_skip_trivial_evaluation():
    """
    Test of TraceEvaluate[] to filter events
    """

    def empty_queue():
        global event_queue
        event_queue = []

    def call_event_func(event: TraceEvent, fn: Callable, *args) -> Optional[Any]:
        """
        Capture filtered calls in event_queue.
        """
        if isinstance(type(fn), type) or ismethod(fn) or isfunction(fn):
            name = f"{fn.__module__}.{fn.__qualname__}"
        else:
            name = str(fn)
        event_queue.append(f"{event.name} call  : {name}{args[:3]}")
        return None

    def return_event_func(event: TraceEvent, result: Any) -> Any:
        """
        A somewhat generic function to print a traced call's
        return value.
        """
        event_queue.append(f"{event.name} result: {result}")
        return result

    def capture_print(s: str):
        """
        A somewhat generic function to print a traced call's
        return value.
        """
        event_queue.append(s)

    session.reset()
    old_print_out = session.evaluation.print_out
    session.evaluation.print_out = capture_print
    empty_queue()

    try:
        session.evaluate("TraceEvaluation[2 3 + 4]")
        assert [
            "  Evaluating: System`Plus[System`Times[2, 3], 4]",
            "    Evaluating: System`Times[2, 3]",
            "      Replacing: System`Times[2, 3] = 6",
            "    Returning: System`Times[2, 3] = 6",
            "    Replacing: System`Plus[System`Times[2, 3], 4] = 10",
            "  Returning: System`Plus[System`Times[2, 3], 4] = 10",
        ] == event_queue
        # print()
        # for line in event_queue:
        #     print(line)

        empty_queue()
        session.evaluate("TraceEvaluation[(2 + 3) 4]")
        assert [
            "  Evaluating: System`Times[System`Plus[2, 3], 4]"
            "    Evaluating: System`Plus[2, 3]",
            "      Returning: System`Plus[2, 3] = (<Integer: 5>, False)",
            "    Returning: System`Plus[2, 3] = 5",
            "  Returning: System`Times[System`Plus[2, 3], 4] = (<Integer: 20>, False)",
        ]
        # print()
        # for line in event_queue:
        #     print(line)

    finally:
        # Just in case, restore everything back to what it was before running this test.
        session.evaluation.print_out = old_print_out
        session.reset()
