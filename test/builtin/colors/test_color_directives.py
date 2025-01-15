# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.color.color_directives
"""

import sys
import time
from test.helper import check_evaluation, evaluate

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            'ColorDistance[Blue, Red, DistanceFunction -> "CIE2000"]',
            None,
            "0.557976",
            None,
        ),
        (
            "ColorDistance[Red, Black, DistanceFunction -> (Abs[#1[[1]] - #2[[1]]] &)]",
            None,
            "0.542917",
            None,
        ),
    ],
)
def test_private_doctests_color_directives(str_expr, msgs, str_expected, fail_msg):
    """builtin.color.color_directives"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
