# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.trace
"""

from test.helper import evaluate

import pytest

import mathics.eval.tracing
from mathics.core.interrupt import AbortInterrupt

trace_evaluation_calls = 0


def test_TraceEvaluation():
    """
    Basic test of TraceEvaluate[]
    """
    old_recursion_limit = evaluate("$RecursionLimit")
    old_evaluation_hook = mathics.eval.tracing.print_evaluate

    def counting_print_evaluate(expr, evaluation, status: str, orig_expr=None) -> bool:
        """
        A replacement for mathics.eval.tracing.print_evaluate() that counts the
        number of evaluation calls.
        """
        global trace_evaluation_calls
        trace_evaluation_calls += 1
        return False

    try:
        # Set a small recursion limit,
        # Replace TraceEvaluation's print function something that counts evaluation
        # calls, and then force a RecursionLimit Error.
        evaluate("$RecursionLimit = 20")
        assert mathics.eval.tracing.print_evaluate == old_evaluation_hook
        evaluate("f[x_] := x + f[x-1]; f[0] = 0")
        global trace_evaluation_calls
        trace_evaluation_calls = 0
        mathics.eval.tracing.print_evaluate = counting_print_evaluate
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
        old_recursion_limit = evaluate(f"$RecursionLimit = {old_recursion_limit.value}")
        mathics.eval.tracing.trace_evaluate_on_call = old_evaluation_hook
    assert mathics.eval.tracing.trace_evaluate_on_call == old_evaluation_hook
