# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.arithmetic.abs
"""
from test.helper import check_evaluation


def test_abs():
    for str_expr, str_expected in [
        ("Abs[a - b]", "Abs[a - b]"),
        ("Abs[Sqrt[3]]", "Sqrt[3]"),
    ]:
        check_evaluation(str_expr, str_expected)
