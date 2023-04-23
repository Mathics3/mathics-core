# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.arithmetic.Element
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Limit[Tan[x], x->Pi/2]", "Indeterminate", None),
        ("Limit[Cot[x], x->0]", "Indeterminate", None),
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
