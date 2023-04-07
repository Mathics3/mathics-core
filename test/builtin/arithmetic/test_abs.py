# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.arithmetic.abs
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Abs[a - b]", "Abs[a - b]", None),
        ("Abs[Sqrt[3]]", "Sqrt[3]", None),
        ("Abs[Sqrt[3]/5]", "Sqrt[3]/5", None),
        ("Abs[-2/3]", "2/3", None),
        ("Abs[2+3 I]", "Sqrt[13]", None),
        ("Abs[2.+3 I]", "3.60555", None),
        ("Abs[Undefined]", "Undefined", None),
        ("Abs[E]", "E", None),
        ("Abs[Pi]", "Pi", None),
        ("Abs[Conjugate[x]]", "Abs[x]", None),
        ("Abs[4^(2 Pi)]", "4^(2 Pi)", None),
    ],
)
def test_abs(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Sign[a - b]", "Sign[a - b]", None),
        ("Sign[Sqrt[3]]", "1", None),
        ("Sign[0]", "0", None),
        ("Sign[0.]", "0", None),
        ("Sign[(1 + I)]", "(1/2 +  I/2)Sqrt[2]", None),
        ("Sign[(1. + I)]", "(0.707107 + 0.707107 I)", None),
        ("Sign[(1 + I)/Sqrt[2]]", "(1 + I)/Sqrt[2]", None),
        ("Sign[(1 + I)/Sqrt[2.]]", "(0.707107 + 0.707107 I)", None),
        ("Sign[-2/3]", "-1", None),
        ("Sign[2+3 I]", "(2 + 3 I)/(13^(1/2))", None),
        ("Sign[2.+3 I]", "0.5547 + 0.83205 I", None),
        ("Sign[4^(2 Pi)]", "1", None),
        # FIXME: add rules to handle this kind of case
        # ("Sign[I^(2 Pi)]", "I^(2 Pi)", None),
        # ("Sign[4^(2 Pi I)]", "1", None),
    ],
)
def test_sign(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)
