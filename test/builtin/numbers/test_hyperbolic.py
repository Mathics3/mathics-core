## -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.hyperbolic and 
mathics.builtins.numbers.exp

These simple verify various rules from
from symja_android_library/symja_android_library/rules/Gudermannian.m
"""
from test.helper import check_evaluation

import pytest


def test_gudermannian():
    for str_expr, str_expected in (
        ("Gudermannian[Undefined]", "Undefined"),
        ("Gudermannian[0]", "0"),
        ("Gudermannian[2 Pi I]", "0"),
        # FIXME: Mathics can't handle Rule substitution
        ("Gudermannian[6/4 Pi I]", "DirectedInfinity[-I]"),
        ("Gudermannian[Infinity]", "Pi/2"),
        # FIXME: rule does not work
        ("Gudermannian[-Infinity]", "-Pi/2"),
        ("Gudermannian[ComplexInfinity]", "Indeterminate"),
        # FIXME Tanh[1 / 2] doesn't eval but Tanh[0.5] does
        ("Gudermannian[z]", "2 ArcTan[Tanh[z / 2]]"),
    ):
        check_evaluation(str_expr, str_expected)


def test_complexexpand():
    for str_expr, str_expected in (
        ("ComplexExpand[Sin[x + I y]]", "Cosh[y]*Sin[x] + I*Cos[x]*Sinh[y]"),
        (
            "ComplexExpand[3^(I x)]",
            "3 ^ (-Im[x]) Re[3 ^ (I Re[x])] + I Im[3 ^ (I Re[x])] 3 ^ (-Im[x])",
        ),
    ):
        check_evaluation(str_expr, str_expected)


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("ArcCosh[1.4]", None, "0.867015", None),
        (
            "ArcCoth[0.000000000000000000000000000000000000000]",
            None,
            "1.57079632679489661923132169163975144210 I",
            None,
        ),
    ],
)
def test_private_doctests_hyperbolic(str_expr, msgs, str_expected, fail_msg):
    """ """
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
        ("Exp[1.*^20]", ("Overflow occurred in computation.",), "Overflow[]", None),
        ("Log[1000] / Log[10] // Simplify", None, "3", None),
        ("Log[1.4]", None, "0.336472", None),
        ("Log[Exp[1.4]]", None, "1.4", None),
        ("Log[-1.4]", None, "0.336472 + 3.14159 I", None),
        ("N[Log[10], 30]", None, "2.30258509299404568401799145468", None),
        ("LogisticSigmoid[I Pi]", None, "LogisticSigmoid[I Pi]", None),
    ],
)
def test_private_doctests_exp(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
