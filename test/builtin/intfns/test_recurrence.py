# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.intfns.recurrence
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("HarmonicNumber[-1.5]", None, "0.613706", None),
        # B_1 = -1/2 as in WMA, whatever SymPy's convention is.
        ("BernoulliB[1]", None, "-1 / 2", "BernoulliB[1] is -1/2 as in WMA"),
        (
            "BernoulliB[1] == BernoulliB[1, 0]",
            None,
            "True",
            "BernoulliB[1] agrees with the polynomial at 0",
        ),
        (
            "BernoulliB[{0, 1, 2}]",
            None,
            "{1, -1 / 2, 1 / 6}",
            "BernoulliB threads over a list, B_1 = -1/2",
        ),
    ],
)
def test_recurrence(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
