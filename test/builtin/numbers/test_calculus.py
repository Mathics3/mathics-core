# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.calculus

In parituclar:

FindRoot[], FindMinimum[], NFindMaximum[] tests


"""
from test.helper import check_evaluation, evaluate
from typing import Optional

import pytest

from mathics.builtin.base import check_requires_list

if check_requires_list(["scipy", "scipy.integrate"]):
    methods_findminimum = ["Automatic", "Newton", "brent", "golden"]
    generic_tests_for_findminimum = [
        (
            r"MatchQ[FindMinimum[Cos[x]^2, {x,1.}, {method}],{_Real,{x->_Real}}]",
            r"True",
            "",
        ),
        (
            r"MatchQ[FindMaximum[Cos[x]^2, {x,1.}, {method} ], {_Real,{x->_Real}}]",
            r"True",
            "",
        ),
    ]
    tests_for_findminimum = sum(
        [
            [
                (tst[0].replace("{method}", "Method->" + method), tst[1], tst[2], None)
                for tst in generic_tests_for_findminimum
            ]
            for method in methods_findminimum
        ],
        [
            (
                r"MatchQ[FindMaximum[Cos[x]^2, {x,1.}, Method->Newton], {_Real,{x->_Real}}]",
                r"True",
                r"check message",
                [
                    r"Encountered a gradient that is effectively zero. The result returned may not be a maximum; it may be a minimum or a saddle point."
                ],
            )
        ],
    )
    methods_findroot = ["Automatic", "Newton", "Secant", "brenth"]
    generic_tests_for_findroot = [
        (r"MatchQ[FindRoot[Cos[x+1.5], {x,.1}, {method}], {x->_Real}]", r"True", ""),
    ]
    tests_for_findroot = sum(
        [
            [
                (tst[0].replace("{method}", "Method->" + method), tst[1], tst[2])
                for tst in generic_tests_for_findroot
            ]
            for method in methods_findroot
        ],
        [],
    )

else:
    tests_for_findminimum = [
        (
            r"MatchQ[FindMinimum[Cos[x]^2, {x,1.}],{_Real,{x->_Real}}]",
            r"True",
            "",
            None,
        ),
        (
            r"MatchQ[FindMaximum[Cos[x]^2, {x,1.}], {_Real,{x->_Real}}]",
            r"True",
            "",
            None,
        ),
    ]
    tests_for_findroot = [
        (r"MatchQ[FindRoot[Cos[x+1.5], {x,.1}], {x->_Real}]", r"True", ""),
    ]


tests_for_integrate = [
    (r"Integrate[Sec[x]*Tan[x],x]", "1 / Cos[x]", "issue #346"),
    (r"Integrate[Sin[x]/(3 + Cos[x])^2,x]", "1 / (3 + Cos[x])", "issue #346"),
]


@pytest.mark.parametrize(
    "str_expr, str_expected, assert_fail_message, expected_messages",
    tests_for_findminimum,
)
def test_findminimum(
    str_expr: str,
    str_expected: str,
    assert_fail_message: str,
    expected_messages: Optional[list],
):
    check_evaluation(
        str_expr, str_expected, assert_fail_message, expected_messages=expected_messages
    )


@pytest.mark.parametrize(
    "str_expr, str_expected, assert_fail_message", tests_for_findroot
)
def test_findroot(
    str_expr: str, str_expected: str, assert_fail_message: str, message=""
):
    check_evaluation(str_expr, str_expected, assert_fail_message, expected_messages=[])


@pytest.mark.parametrize(
    "str_expr, str_expected, assert_fail_message", tests_for_integrate
)
def test_integrate(str_expr: str, str_expected: str, assert_fail_message):
    check_evaluation(str_expr, str_expected, assert_fail_message, expected_messages=[])


@pytest.mark.parametrize(
    "str_expr, str_expected, expected_messages",
    [
        (
            "D[{y, -x}[2], {x, y}]",
            "D[{y, -x}[2], {x, y}]",
            [
                "Multiple derivative specifier {x, y} does not have the form {variable, n}, where n is a non-negative machine integer."
            ],
        ),
    ],  # Issue #502
)
def test_D(str_expr: str, str_expected: str, expected_messages):
    check_evaluation(
        str_expr=str_expr,
        str_expected=str_expected,
        expected_messages=expected_messages,
    )


@pytest.mark.parametrize(
    "str_expr, str_expected, expected_messages",
    [
        (
            "Solve[x^2 +1 == 0, x]",
            "{{x -> -I}, {x -> I}}",
            [],
        ),
        (
            "Solve[x^5==x,x]",
            "{{x -> -1}, {x -> 0}, {x -> 1}, {x -> -I}, {x -> I}}",
            [],
        ),
        (
            "Solve[g[x] == 0, x]",
            "Solve[g[x] == 0, x]",
            [],
        ),
        (
            ## FIXME: should use inverse functions?
            "Solve[g[x] + h[x] == 0, x]",
            "Solve[g[x] + h[x] == 0, x]",
            [],
        ),
        (
            "Solve[Sin(x) == 1, x]",
            "{{x -> 1 / Sin}}",
            [],
        ),
        (
            "Solve[E == 1, E]",
            "Solve[False, E]",
            ["E is not a valid variable."],
        ),
        (
            "Solve[E == 1, E]",
            "Solve[False, E]",
            ["E is not a valid variable."],
        ),
        (
            "Solve[False, Pi]",
            "Solve[False, Pi]",
            ["Pi is not a valid variable."],
        ),
    ],
)
def test_Solve(str_expr: str, str_expected: str, expected_messages):
    check_evaluation(
        str_expr=str_expr,
        str_expected=str_expected,
        expected_messages=expected_messages,
    )
