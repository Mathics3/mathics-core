# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.hyperbolic

These simple verify various rules from
from symja_android_library/symja_android_library/rules/Gudermannian.m
"""
from test.helper import check_evaluation


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
