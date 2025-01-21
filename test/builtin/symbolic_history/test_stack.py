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
    ):
        check_evaluation(str_expr, str_expected, message)
