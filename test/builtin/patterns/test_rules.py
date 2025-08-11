# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.patterns.rules
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        (
            "ReplaceList[expr, {}, -1]",
            (
                "Non-negative integer or Infinity expected at position 3 in ReplaceList[expr, {}, -1]",
            ),
            "ReplaceList[expr, {}, -1]",
            None,
        ),
    ],
)
def test_associations_private_doctests(
    str_expr, expected_messages, str_expected, assert_message
):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=assert_message,
        expected_messages=expected_messages,
    )
