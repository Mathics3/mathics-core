# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.calculus

In parituclar:

FindRoot[], FindMinimum[], NFindMaximum[] tests


"""
import pytest
from test.helper import evaluate
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
                (tst[0].replace("{method}", "Method->" + method), tst[1], tst[2])
                for tst in generic_tests_for_findminimum
            ]
            for method in methods_findminimum
        ],
        [],
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
        (r"MatchQ[FindMinimum[Cos[x]^2, {x,1.}],{_Real,{x->_Real}}]", r"True", ""),
        (r"MatchQ[FindMaximum[Cos[x]^2, {x,1.}], {_Real,{x->_Real}}]", r"True", ""),
    ]
    tests_for_findroot = [
        (r"MatchQ[FindRoot[Cos[x+1.5], {x,.1}], {x->_Real}]", r"True", ""),
    ]


tests_for_integrate = [
    (r"Integrate[Sec[x]*Tan[x],x]", "1 / Cos[x]", "issue #346"),
    (r"Integrate[Sin[x]/(3 + Cos[x])^2,x]", "1 / (3 + Cos[x])", "issue #346"),
]


@pytest.mark.parametrize("str_expr, str_expected, msg", tests_for_findminimum)
def test_findminimum(str_expr: str, str_expected: str, msg: str, message=""):
    result = evaluate(str_expr)
    expected = evaluate(str_expected)
    if msg:
        assert result == expected, msg
    else:
        assert result == expected


@pytest.mark.parametrize("str_expr, str_expected, msg", tests_for_findroot)
def test_findroot(str_expr: str, str_expected: str, msg: str, message=""):
    result = evaluate(str_expr)
    expected = evaluate(str_expected)
    if msg:
        assert result == expected, msg
    else:
        assert result == expected


@pytest.mark.parametrize("str_expr, str_expected, msg", tests_for_integrate)
def test_integrate(str_expr: str, str_expected: str, msg: str, message=""):
    result = evaluate(str_expr)
    expected = evaluate(str_expected)
    if msg:
        assert result == expected, msg
    else:
        assert result == expected
