"""
Unit tests from mathics.builtin.symbolic_history.stack.
"""

from test.helper import check_evaluation


def test_trace():
    for str_expr, str_expected, message in (
        (
            "Trace[1]",
            "{}",
            "Trace with Constant - no intermediate values",
        ),
        (
            "Trace[a]",
            "{}",
            "Trace with Symbol - no intermediate values",
        ),
        (
            "Trace[Sin[Log[2.5, 7]]]",
            "{Sin[Log[2.5, 7]], Log[2.5, 7], 2.12368, 2.12368, 0.851013, 0.851013}",
            "Trace with expression. Issue #1465",
        ),
    ):
        check_evaluation(str_expr, str_expected, message, hold_expected=True)
