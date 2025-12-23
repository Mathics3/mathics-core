# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.calculus

In partiuclar:

FindRoot[], FindMinimum[], NFindMaximum[] tests


"""
from test.helper import check_evaluation
from typing import Optional

import pytest

from mathics.core.builtin import check_requires_list

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
                "Multiple derivative specifier {x, y} does not have the form {variable,"
                " n}, where n is a non-negative machine integer."
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


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "D[2/3 Cos[x] - 1/3 x Cos[x] Sin[x] ^ 2,x]//Expand",
            None,
            "-2 x Cos[x] ^ 2 Sin[x] / 3 + x Sin[x] ^ 3 / 3 - 2 Sin[x] / 3 - Cos[x] Sin[x] ^ 2 / 3",
            None,
        ),
        ("D[f[#1], {#1,2}]", None, "f''[#1]", None),
        ("D[(#1&)[t],{t,4}]", None, "0", None),
        ("Attributes[f] ={HoldAll}; Apart[f''[x + x]]", None, "f''[2 x]", None),
        ("Attributes[f] = {}; Apart[f''[x + x]]", None, "f''[2 x]", None),
        (
            "D[{#^2}, #]",
            None,
            "{2 #1}",
            "Issue #375: avoid slots in rule handling D[{...}",
        ),
        ("FindRoot[2.5==x,{x,0}]", None, "{x -> 2.5}", None),
        ("DownValues[Integrate]", None, "{}", None),
        (
            "Definition[Integrate]",
            None,
            (
                "Attributes[Integrate] = {Protected, ReadProtected}\n"
                "\n"
                "Options[Integrate] = {Assumptions -> $Assumptions, GenerateConditions -> Automatic, PrincipalValue -> False}\n"
            ),
            None,
        ),
        (
            "Integrate[Hold[x + x], {x, a, b}]",
            None,
            "Integrate[Hold[x + x], {x, a, b}]",
            None,
        ),
        ("Integrate[sin[x], x]", None, "Integrate[sin[x], x]", None),
        ("Integrate[x ^ 3.5 + x, x]", None, "x ^ 2 / 2 + 0.222222 x ^ 4.5", None),
        ("Integrate[ArcTan(x), x]", None, "x ^ 2 ArcTan / 2", None),
        ("Integrate[E[x], x]", None, "Integrate[E[x], x]", None),
        ("Integrate[Exp[-(x/2)^2],{x,-Infinity,+Infinity}]", None, "2 Sqrt[Pi]", None),
        (
            "Integrate[Exp[-1/(x^2)], x]",
            None,
            "x E ^ (-1 / x ^ 2) + Sqrt[Pi] Erf[1 / x]",
            None,
        ),
        ("True'", None, "True'", None),
        ("False'", None, "False'", None),
        ("List'", None, "{1}&", None),
        ("1'", None, "0&", None),
        ("-1.4'", None, "-(0&)", None),
        ("(2/3)'", None, "0&", None),
        ("I'", None, "0&", None),
        ("Derivative[0,0,1][List]", None, "{0, 0, 1}&", None),
    ],
)
def test_calculus(str_expr, msgs, str_expected, fail_msg):
    """
    Tests of mathics.builtin.numbers.calculus module.
    """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
