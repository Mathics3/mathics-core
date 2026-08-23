# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.arithmetic
"""

from test.helper import check_arg_counts, check_evaluation

import pytest


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "Assuming",
            "2 arguments are",
        ),
        (
            "Refine",
            "1 or 2 arguments are",
        ),
    ],
)
def test_arithmetic_arg_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "assert_msg"),
    [
        ("Refine[Re[x], Element[x, Reals]]", "x", ""),
    ],
)
def test_add(str_expr, str_expected, assert_msg):
    check_evaluation(
        str_expr, str_expected, failure_message=assert_msg, hold_expected=True
    )
