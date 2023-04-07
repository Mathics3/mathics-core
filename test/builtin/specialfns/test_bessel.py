# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.arithmetic.bessel
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "assert_failure_msg"),
    # Basically special rules from autoload/rules/Bessel.m that are not covered
    # by SymPy.
    [
        (
            "BesselI[1/2,z]",
            "Sqrt[2] Sinh[z] / (Sqrt[z] Sqrt[Pi])",
            "BesselI 1/2 rule",
        ),
        (
            "BesselI[-1/2,z]",
            "Sqrt[2] Cosh[z] / (Sqrt[z] Sqrt[Pi])",
            "BesselI -1/2 rule",
        ),
        ("BesselJ[-1/2,z]", "Sqrt[2] Cos[z] / (Sqrt[z] Sqrt[Pi])", "BesselJ -1/2 rule"),
        ("BesselJ[1/2,z]", "Sqrt[2] Sin[z] / (Sqrt[z] Sqrt[Pi])", "BesselJ 1/2 rule"),
    ],
)
def test_add(str_expr, str_expected, assert_failure_msg):
    check_evaluation(
        str_expr, str_expected, hold_expected=True, failure_message=assert_failure_msg
    )
