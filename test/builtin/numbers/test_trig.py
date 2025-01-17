# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.trig

For this to work we also make use of rules from
mathics/autoload/rules/trig.m
"""
from test.helper import check_evaluation

import pytest
from sympy.core.numbers import ComplexInfinity


def test_ArcCos():
    for str_expr, str_expected in (
        ("ArcCos[I Infinity]", "-I Infinity"),
        ("ArcCos[-I Infinity]", "I Infinity"),
        ("ArcCos[0]", "1/2 Pi"),
        ("ArcCos[1/2]", "1/3 Pi"),
        ("ArcCos[-1/2]", "2/3 Pi"),
        ("ArcCos[1/2 Sqrt[2]]", "1/4 Pi"),
        ("ArcCos[-1/2 Sqrt[2]]", "3/4 Pi"),
        ("ArcCos[1/2 Sqrt[3]]", "1/6 Pi"),
        ("ArcCos[-1/2 Sqrt[3]]", "5/6 Pi"),
        ("ArcCos[(1 + Sqrt[3]) / (2*Sqrt[2])]", "1/12 Pi"),
    ):
        check_evaluation(str_expr, str_expected)


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "ArcTan[ComplexInfinity]",
            None,
            "Indeterminate",
            "Rule added for Arctan[ComplexInfinity]",
        ),
        ("ArcTan[-1, 1]", None, "3 Pi / 4", None),
        ("ArcTan[1, -1]", None, "-Pi / 4", None),
        ("ArcTan[-1, -1]", None, "-3 Pi / 4", None),
        ("ArcTan[1, 0]", None, "0", None),
        ("ArcTan[-1, 0]", None, "Pi", None),
        ("ArcTan[0, 1]", None, "Pi / 2", None),
        ("ArcTan[0, -1]", None, "-Pi / 2", None),
        ("Cos[1.5 Pi]", None, "-1.83697×10^-16", None),
        ("N[Sin[1], 40]", None, "0.8414709848078965066525023216302989996226", None),
        ("Tan[0.5 Pi]", None, "1.63312×10^16", None),
    ],
)
def test_private_doctests_trig(str_expr, msgs, str_expected, fail_msg):
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
