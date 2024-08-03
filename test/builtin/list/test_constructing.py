# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.list.constructing
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "failure_message"),
    [
        (
            "Table[x, {x,0,1/3}]",
            "{0}",
            None,
        ),
        (
            "Table[x, {x, -0.2, 3.9}]",
            "{-0.2, 0.8, 1.8, 2.8, 3.8}",
            None,
        ),
    ],
)
def test_array(str_expr, str_expected, failure_message):
    check_evaluation(str_expr, str_expected, failure_message)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "failure_message"),
    [
        (
            "Array[f, {2, 3}, {1, 2, 3}]",
            "Array[f, {2, 3}, {1, 2, 3}]",
            "plen: {2, 3} and {1, 2, 3} should have the same length.",
        ),
        (
            "Array[f, a]",
            "Array[f, a]",
            "ilsnn: Single or list of non-negative integers expected at position 2.",
        ),
        (
            "Array[f, 2, b]",
            "Array[f, 2, b]",
            "ilsnn: Single or list of non-negative integers expected at position 3.",
        ),
    ],
)
def test_range(str_expr, str_expected, failure_message):
    check_evaluation(str_expr, str_expected, failure_message)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "failure_message"),
    [
        (
            "Table[x, {x,0,1/3}]",
            "{0}",
            None,
        ),
        (
            "Table[x, {x, -0.2, 3.9}]",
            "{-0.2, 0.8, 1.8, 2.8, 3.8}",
            None,
        ),
    ],
)
def test_table(str_expr, str_expected, failure_message):
    check_evaluation(str_expr, str_expected, failure_message)
