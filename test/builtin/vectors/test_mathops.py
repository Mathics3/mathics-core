# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.vectors.math_ops

In particular, Curl[] and Norm[].
"""

from test.helper import check_evaluation, check_wrong_number_of_arguments

import pytest


def test_norm():
    for str_expr, expected_message in (
        (
            "Norm[{1, {2, 3}}]",
            "The first Norm argument should be a number, vector, or matrix.",
        ),
        (
            "Norm[{x, y}, 0]",
            'The second argument of Norm, 0, should be a symbol, Infinity, or an integer or real number not less than 1 for vector p-norms; or 1, 2, Infinity, or "Frobenius" for matrix norms.',
        ),
        (
            "Norm[{x, y}, 0.5]",
            'The second argument of Norm, 0.5, should be a symbol, Infinity, or an integer or real number not less than 1 for vector p-norms; or 1, 2, Infinity, or "Frobenius" for matrix norms.',
        ),
    ):
        check_evaluation(
            str_expr=str_expr,
            str_expected=str_expr,
            expected_messages=[expected_message],
        )

    for str_expr, str_expected in (
        (
            "Norm[{x, y}]",
            "Sqrt[Abs[x] ^ 2 + Abs[y] ^ 2]",
        ),
        (
            "Norm[{x, y}, p]",
            "(Abs[x] ^ p + Abs[y] ^ p) ^ (1 / p)",
        ),
        (
            "Norm[{}]",
            "Norm[{}]",
        ),
        (
            "Norm[0]",
            "0",
        ),
    ):
        check_evaluation(str_expr=str_expr, str_expected=str_expected)


def test_wrong_number_of_arguments():
    tests = [
        (
            "Curl[a]",
            ["Curl called with 1 argument; 2 or 3 arguments are expected."],
            "Curl with one argument",
        ),
        (
            "Curl[a, b, c, d]",
            ["Curl called with 4 arguments; 2 or 3 arguments are expected."],
            "Curl with more than three arguments",
        ),
    ]
    check_wrong_number_of_arguments(tests)
