# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.arithmetic
"""

from test.helper import check_arg_counts, check_evaluation

import pytest


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "Arg",
            "1 argument is",
        ),
        (
            "Conjugate",
            "1 argument is",
        ),
        (
            "Im",
            "1 argument is",
        ),
        (
            "Re",
            "1 argument is",
        ),
        (
            "Product",
            "2 or more arguments are",
        ),
        (
            "Sum",
            "2 or more arguments are",
        ),
        (
            "Boole",
            "2 arguments are",
        ),
        (
            "Complex",
            "2 arguments are",
        ),
        (
            "Element",
            "2 arguments are",
        ),
        (
            "Rational",
            "2 arguments are",
        ),
        (
            "ConditionalExpression",
            "2 or 3 arguments are",
        ),
    ],
)
def test_arithmetic_arg_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg"),
    [
        ("Sum[i, {i, 1, 10}]", "55", None),
        ("Sum[f[i], {i, 0, 3}]", "f[0] + f[1] + f[2] + f[3]", None),
        ("Sum[x^i, {i, 0, 3}]", "1 + x + x ^ 2 + x ^ 3", None),
        (
            "Sum[1/(x + i), {i, 1, 2}]",
            "1 / (1 + x) + 1 / (2 + x)",
            "With integer bounds the terms are added, not put over a common denominator",
        ),
        ("Sum[i, {i, 1, 0}]", "0", "Empty range"),
        ("Product[x + i, {i, 1, 3}]", "(1 + x) (2 + x) (3 + x)", None),
        ("Product[i, {i, 1, 0}]", "1", "Empty range"),
        (
            "Sum[k, {k, 1, n}]",
            "n (1 + n) / 2",
            "Symbolic bounds still go through SymPy",
        ),
        ("Sum[1/k^2, {k, 1, Infinity}]", "Pi ^ 2 / 6", None),
    ],
)
def test_sum_product_bounds(str_expr, str_expected, fail_msg):
    """Sum and Product with integer and with symbolic bounds"""
    check_evaluation(str_expr, str_expected, failure_message=fail_msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        # Arithmetic on arbitrary-precision reals keeps the binary value:
        # -x is the exact negative of x, so x - x is zero.
        ("x1 = N[1/3, 4]; x1 - x1 == 0", "True"),
        ("x1 = N[1/3, 4]; Abs[2 x1 - x1 - x1] < 10^-20", "True"),
        ("N[Pi, 16] - N[Pi, 16] == 0", "True"),
        ("Abs[N[1/7, 25] - N[1/7, 25]] < 10^-40", "True"),
        ("x1 = N[1/3, 4]; -x1 === -1 x1 === Minus[x1]", "True"),
    ],
)
def test_precision_real_cancellation(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)
