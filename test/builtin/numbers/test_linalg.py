# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.linalg
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg", "warnings"),
    [
        (None, None, None, None),
        (
            "Inverse[{{0, 2},{2, 0}}]",
            "{{0, 1 / 2},{1 / 2, 0}}",
            "",
            tuple(),
        ),
        (
            "Inverse[{{0, 2.},{2, 0}}]",
            "{{0, .5},{.5, 0}}",
            "",
            tuple(),
        ),
        (
            "Inverse[{{0, 2., 0},{2, 0, 0}, {0, 0, a}}]",
            "{{0, .5, 0},{.5, 0, 0},{0, 0, 1. / a}}",
            "",
            tuple(),
        ),
        # Multiplying a symbolic matrix by its inverse does not
        # produces the identity in general
        (
            "Inverse[{{a, b},{c, d}}].{{a, b},{c, d}}",
            (
                "{{a d / (a d - b c) - b c / (a d - b c), 0}, "
                "{0, a d / (a d - b c) - b c / (a d - b c)}}"
            ),
            "2x2 general inverse",
            tuple(),
        ),
        (
            "Inverse[{{a, b},{c, d}}].{{a, b},{c, d}}//Simplify",
            "{{1, 0},{0, 1}}",
            "2x2 general inverse",
            tuple(),
        ),
        (
            "Inverse[{{g[a], g[b]},{g[c], g[d]}}].{{g[a], g[b]},{g[c], g[d]}}//Simplify",
            ("{{1, 0},{0, 1}}"),
            "2x2 general inverse",
            tuple(),
        ),
        (
            "Inverse[{{1,1},{1,1}}]",
            "Inverse[{{1, 1},{1, 1}}]",
            "singular matrix",
            ("The matrix {{1, 1}, {1, 1}} is singular.",),
        ),
        (
            "Inverse[{{1, 1, 1},{1, 1, 2}}]",
            "Inverse[{{1, 1, 1},{1, 1, 2}}]",
            "singular matrix",
            (
                "Argument {{1, 1, 1}, {1, 1, 2}} at position 1 "
                "is not a non-empty square matrix.",
            ),
        ),
        (
            "Inverse[{{{1}, {1}},{{1}, {2}}}]",
            "Inverse[{{{1}, {1}},{{1}, {2}}}]",
            "singular matrix",
            (
                "Argument {{{1}, {1}}, {{1}, {2}}} at position 1 "
                "is not a non-empty square matrix.",
            ),
        ),
        (
            "Inverse[{{1, 0, 0}, {0, Sqrt[3]/2, 1/2}, {0,-1 / 2, Sqrt[3]/2}}]",
            "{{1, 0, 0}, {0, Sqrt[3] / 2, -1 / 2}, {0, 1 / 2, Sqrt[3] / 2}}",
            None,
            None,
        ),
    ],
)
def test_inverse(str_expr, str_expected, fail_msg, warnings):
    check_evaluation(
        str_expr, str_expected, failure_message="", expected_messages=warnings
    )
