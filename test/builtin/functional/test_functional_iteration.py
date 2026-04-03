# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.functional.functional_iteration
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("FixedPoint[f, x, 0]", None, "x", None),
        (
            "FixedPoint[f, x, -1]",
            ("Non-negative integer expected.",),
            "FixedPoint[f, x, -1]",
            None,
        ),
        ("FixedPoint[Cos, 1.0, Infinity]", None, "0.739085", None),
        ("FixedPointList[f, x, 0]", None, "{x}", None),
        (
            "FixedPointList[f, x, -1]",
            ("Non-negative integer expected.",),
            "FixedPointList[f, x, -1]",
            None,
        ),
        ("Last[FixedPointList[Cos, 1.0, Infinity]]", None, "0.739085", None),
    ],
)
def test_functional_iteration(str_expr, msgs, str_expected, fail_msg):
    """functional.functional_iteration"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
