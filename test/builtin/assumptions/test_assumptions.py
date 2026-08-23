# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.arithmetic
"""

from test.helper import check_arg_counts, check_evaluation

import pytest

LIST_TEST_ASSUMPTIONS_INTEGRATE = [
    (
        "Integrate[x^n, {x, 0, 1}]",
        "Piecewise[{{1 / (1 + n), 1 + Re[n] > 0 && n > -Infinity && n < Infinity && n != -1}}, Infinity]",
        "This is so complicated due the sympy result is wrong...",
    ),
    (
        "Assuming[0 < n < 1, Integrate[x^n, {x, 0, 1}]]",
        "Piecewise[{{1 / (1 + n), 1 + Re[n] > 0 && n > -Infinity && n < Infinity && n != -1}}, Infinity]",
        "",
    ),
    (
        "Assuming[0 < Re[n] + 1, Integrate[x^n, {x, 0, 1}]]",
        "Piecewise[{{1 / (1 + n), n > -Infinity && n < Infinity && n != -1}}, Infinity]",
        "",
    ),
    ("Assuming[n == 1, Integrate[x^n, {x, 0, 1}]]", "1 / 2", ""),
    ("Assuming[n == 2, Integrate[x^n, {x, 0, 1}]]", "1 / 3", ""),
    ("Assuming[n == -1, Integrate[x^n, {x, 0, 1}]]", "Infinity", ""),
    #    ("Assuming[1<n<3, Integrate[x^n, {x, 0, 1}]]", "x^(n+1)/(n+1)", ""),
    #    ("Assuming[Or[n==1, n==2], Integrate[x^n, {x, 0, 1}]]", "x^(n+1)/(n+1)", ""),
    #    ("Assuming[Or[n>2, n>=3], Integrate[x^n, {x, 0, 1}]]", "x^(n+1)/(n+1)", ""),
]

LIST_TEST_ASSUMPTIONS_SIMPLIFY = [
    (
        "Simplify[a==b || a!=b]",
        "True",
        "",
    ),
    (
        "Simplify[a==b && a!=b]",
        "False",
        "",
    ),
    (
        "Simplify[a<=b && a>b]",
        "False",
        "",
    ),
    (
        "Simplify[a==b, ! a!=b]",
        "True",
        "",
    ),
    (
        "Simplify[a==b,   a!=b]",
        "False",
        "",
    ),
    (
        "Simplify[a > b,  {a==4}]",
        "b < 4",
        "",
    ),
    (
        "Simplify[And[a>b, b<a]]",
        "a>b",
        "",
    ),
    (
        "Simplify[Or[a>b, a<b]]",
        "a!=b",
        "",
    ),
    (
        "Simplify[Or[a>b, b<a]]",
        "a>b",
        "",
    ),
    (
        "Simplify[a>b,  {b<=a}]",
        "a>b",
        "",
    ),
]


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "Assuming",
            "2 arguments are",
        ),
        (
            "Refine",
            "1 or 2 arguments are",
        ),
    ],
)
def test_arithmetic_arg_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "assert_msg"),
    [
        ("Refine[Re[x], Element[x, Reals]]", "x", ""),
    ],
)
def test_add(str_expr, str_expected, assert_msg):
    check_evaluation(
        str_expr, str_expected, failure_message=assert_msg, hold_expected=True
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "message"),
    LIST_TEST_ASSUMPTIONS_INTEGRATE,
)
@pytest.mark.xfail(reason="the Assumptions with Integrate is not fully working")
def test_assumptions_integrate(str_expr, str_expected, message):
    check_evaluation(str_expr, str_expected)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "message"),
    LIST_TEST_ASSUMPTIONS_SIMPLIFY,
)
@pytest.mark.xfail(reason="the Assumptions with Simplify is not fully working")
def test_assumptions_simplify(str_expr, str_expected, message):
    check_evaluation(str_expr, str_expected)
