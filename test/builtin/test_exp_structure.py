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
def test_private_doctests_exp_size_and_sig(str_expr, msgs, str_expected, fail_msg):
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
def test_private_doctests_general(str_expr, msgs, str_expected, fail_msg):
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
