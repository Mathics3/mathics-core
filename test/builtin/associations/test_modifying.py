# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.associations.modifying
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        (
            "AssociateTo[1, 1->2]",
            ["The argument 1 -> 2 is not a valid Association."],
            "AssociateTo[1, 1->2]",
            "AssociateTo first parameter should be an association not an Integer.",
        ),
        (
            "Clear[x]; AssociateTo[x, 1->2]",
            ["The argument x is not a valid Association."],
            "AssociateTo[x, 1->2]",
            "AssociateTo first parameter should have a value.",
        ),
        (
            "assoc = <|a->1|>; AssociateTo[assoc, 1]",
            ["The argument 1 is not a list, Rule or Association."],
            "AssociateTo[assoc, 1]",
            "AssociateTo first parameter wrong type.",
        ),
    ],
)
def test_AssociateTo(str_expr, expected_messages, str_expected, assert_message):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=assert_message,
        expected_messages=expected_messages,
    )
