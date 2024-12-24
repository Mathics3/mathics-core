"""
Unit tests for mathics.builtin.functional.application
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("g[x_,y_] := x+y;g[Sequence@@Slot/@Range[2]]&[1,2]", None, "#1 + #2", None),
        ("Evaluate[g[Sequence@@Slot/@Range[2]]]&[1,2]", None, "3", None),
        ("# // InputForm", None, "#1", None),
        ("#0 // InputForm", None, "#0", None),
        ("## // InputForm", None, "##1", None),
        ("Clear[g];", None, "Null", None),
    ],
)
def test_private_doctests_application(str_expr, msgs, str_expected, fail_msg):
    """functional.application"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
