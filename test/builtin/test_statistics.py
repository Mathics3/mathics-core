# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.statistics.
"""

import sys
import time
from test.helper import check_evaluation, evaluate

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("Sort[{x_, y_}, PatternsOrderedQ]", None, "{x_, y_}", None),
    ],
)
def test_private_doctests_statistics_orderstatistics(
    str_expr, msgs, str_expected, fail_msg
):
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
