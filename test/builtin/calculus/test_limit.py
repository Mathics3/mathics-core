# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.calculus.Limit
"""
from test.helper import check_arg_counts, check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Limit[Tan[x], x->Pi/2]", "Indeterminate", None),
        ("Limit[Cot[x], x->0]", "Indeterminate", None),
        ("Limit[Cot[x], x->Infinity]", "Indeterminate", None),
        ("Limit[Cot[x], x->-Infinity]", "Indeterminate", None),
        ("Limit[x*Sqrt[2*Pi]^(x^-1)*(Sin[x]/(x!))^(x^-1), x->Infinity]", "E", None),
        (
            "Limit[x, x -> x0, Direction -> x]",
            "Limit[x, x -> x0, Direction -> x]",
            "Value of Direction -> x should be -1 or 1.",
        ),
    ],
)
def test_limit(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "Limit",
            "2 or 3 arguments are",
        ),
    ],
)
def test_limit_arg_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)
