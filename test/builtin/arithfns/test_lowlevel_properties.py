# -*- coding: utf-8 -*-
"""
Unit tests for mathics.eval.arithmetic low level positivity tests
"""
from test.helper import session

import pytest

from mathics.eval.arithmetic import (
    test_positive_arithmetic_expr as check_positive,
    test_zero_arithmetic_expr as check_zero,
)


@pytest.mark.parametrize(
    ("str_expr", "expected", "msg"),
    [
        ("I", False, None),
        ("0", False, None),
        ("1", True, None),
        ("Pi", True, None),
        ("a", False, None),
        ("-Pi", False, None),
        ("(-1)^2", True, None),
        ("(-1)^3", False, None),
        ("Sqrt[2]", True, None),
        ("Sqrt[-2]", False, None),
        ("(-2)^(1/2)", False, None),
        ("(2)^(1/2)", True, None),
        ("Exp[a]", False, None),
        ("Exp[2.3]", True, None),
        ("Log[1/2]", False, None),
        ("Exp[I]", False, None),
        ("Log[3]", True, None),
        ("Log[I]", False, None),
        ("Abs[a]", False, None),
        ("Abs[0]", False, None),
        ("Abs[1+3 I]", True, None),
        ("Sin[Pi]", False, None),
    ],
)
def test_positivity(str_expr, expected, msg):
    expr = session.parse(str_expr)
    if msg:
        assert check_positive(expr) == expected, msg
    else:
        assert check_positive(expr) == expected


@pytest.mark.parametrize(
    ("str_expr", "expected", "msg"),
    [
        ("I", False, None),
        ("0", True, None),
        ("1", False, None),
        ("Pi", False, None),
        ("a", False, None),
        ("a-a", False, "the low-level check does not try to evaluate the input"),
        ("3-3.", True, None),
        ("2-Sqrt[4]", True, None),
        ("-Pi", False, None),
        ("(-1)^2", False, None),
        ("(-1)^3", False, None),
        ("Sqrt[2]", False, None),
        ("Sqrt[-2]", False, None),
        ("(-2)^(1/2)", False, None),
        ("(2)^(1/2)", False, None),
        ("Exp[a]", False, None),
        ("Exp[2.3]", False, None),
        ("Log[1/2]", False, None),
        ("Exp[I]", False, None),
        ("Log[3]", False, None),
        ("Log[I]", False, None),
        ("Abs[a]", False, None),
        ("Abs[0]", True, None),
        ("Abs[1+3 I]", False, None),
        ("Sin[Pi]", False, None),
    ],
)
def test_zero(str_expr, expected, msg):
    expr = session.parse(str_expr)
    if msg:
        assert check_zero(expr) == expected, msg
    else:
        assert check_zero(expr) == expected
