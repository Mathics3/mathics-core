# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.arithmetic
"""

from test.helper import check_arg_counts

import pytest


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "Arg",
            "1 argument is",
        ),
        (
            "Conjugate",
            "1 argument is",
        ),
        (
            "Im",
            "1 argument is",
        ),
        (
            "Re",
            "1 argument is",
        ),
        (
            "Product",
            "2 or more arguments are",
        ),
        (
            "Sum",
            "2 or more arguments are",
        ),
        (
            "Assuming",
            "2 arguments are",
        ),
        (
            "Boole",
            "2 arguments are",
        ),
        (
            "Complex",
            "2 arguments are",
        ),
        (
            "Element",
            "2 arguments are",
        ),
        (
            "Rational",
            "2 arguments are",
        ),
        (
            "ConditionalExpression",
            "2 or 3 arguments are",
        ),
    ],
)
def test_arithmetic_arg_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)
