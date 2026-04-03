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
