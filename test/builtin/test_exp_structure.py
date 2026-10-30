# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.exp_structure
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("ClearAll[f,a,b,x,y];", None, "Null", None),
        ("LeafCount[f[a, b][x, y]]", None, "5", None),
        (
            "data=NestList[# /. s[x_][y_][z_] -> x[z][y[z]] &, s[s][s][s[s]][s][s], 4];",
            None,
            "Null",
            None,
        ),
        ("LeafCount /@ data", None, "{7, 8, 8, 11, 11}", None),
        ("Clear[data];", None, "Null", None),
        (
            "LeafCount[1 / 3, 1 + I]",
            ("LeafCount called with 2 arguments; 1 argument is expected.",),
            "LeafCount[1 / 3, 1 + I]",
            None,
        ),
    ],
)
def test_exp_size_and_sig(str_expr, msgs, str_expected, fail_msg):
    """exp_structure.size_and_sig"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "Operate[p, f, -1]",
            ("Non-negative integer expected at position 3 in Operate[p, f, -1].",),
            "Operate[p, f, -1]",
            None,
        ),
    ],
)
def test_general(str_expr, msgs, str_expected, fail_msg):
    """exp_structure.general"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected"),
    [
        ("Outer[f, {1, 2}, 3]", None, "{f[1], f[2]}"),
        (
            "Outer[f, {{1, 2}, {3, 4}}, {{a, b}}, 1]",
            None,
            "{{f[{1, 2}, {a, b}]}, {f[{3, 4}, {a, b}]}}",
        ),
        ("Outer[f, {{1, 2}}, {{a}}, 1, 2]", None, "{{{f[{1, 2}, a]}}}"),
        ("Outer[f, {{1, 2}}, {{a}}, Infinity]", None, "{{{{f[1, a]}}, {{f[2, a]}}}}"),
        # A list without a level of its own is taken apart completely, and
        # levels beyond the number of lists are ignored.
        ("Outer[f, {{a}}, {{b}}, {{c}}, 1, 2]", None, "{{{{{f[{a}, b, c]}}}}}"),
        ("Outer[f, {{a}}, {{b}}, 1, 2, 1]", None, "{{{f[{a}, b]}}}"),
        ("Outer[f, {{a}}, {{b}}, Infinity, 1]", None, "{{{f[a, {b}]}}}"),
        (
            "Outer[List, {1, 2}, {a, b}, 1, 1]",
            None,
            "{{{1, a}, {1, b}}, {{2, a}, {2, b}}}",
        ),
        (
            "Outer[f, x]",
            ("Nonatomic expression expected at position 2 in Outer[f, x].",),
            "Outer[f, x]",
        ),
        (
            "Outer[f, {{a}}, {{b}}, 0]",
            (
                "Positive machine-sized integer or Infinity expected at position 4 in Outer[f, {{a}}, {{b}}, 0].",
            ),
            "Outer[f, {{a}}, {{b}}, 0]",
        ),
        (
            "Outer[f, {{a}}, x, 1]",
            (
                "Positive machine-sized integer or Infinity expected at position 3 in Outer[f, {{a}}, x, 1].",
            ),
            "Outer[f, {{a}}, x, 1]",
        ),
    ],
)
def test_outer_levels(str_expr, msgs, str_expected):
    """Outer[f, lists, n1, n2, ...] takes each list apart only down to its
    level."""
    check_evaluation(
        str_expr,
        str_expected,
        hold_expected=True,
        expected_messages=msgs,
    )
