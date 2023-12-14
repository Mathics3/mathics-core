# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.numbertheory
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("Divisors[0]", None, "Divisors[0]", None),
        (
            "Divisors[{-206, -502, -1702, 9}]",
            None,
            (
                "{{1, 2, 103, 206}, "
                "{1, 2, 251, 502}, "
                "{1, 2, 23, 37, 46, 74, 851, 1702}, "
                "{1, 3, 9}}"
            ),
            None,
        ),
        ("Length[Divisors[1000*369]]", None, "96", None),
        ("Length[Divisors[305*176*369*100]]", None, "672", None),
        ("FractionalPart[b]", None, "FractionalPart[b]", None),
        ("FractionalPart[{-2.4, -2.5, -3.0}]", None, "{-0.4, -0.5, 0.}", None),
        ("FractionalPart[14/32]", None, "7 / 16", None),
        ("FractionalPart[4/(1 + 3 I)]", None, "2 / 5 - I / 5", None),
        ("FractionalPart[Pi^20]", None, "-8769956796 + Pi ^ 20", None),
        ("MantissaExponent[E, Pi]", None, "{E / Pi, 1}", None),
        ("MantissaExponent[Pi, Pi]", None, "{1 / Pi, 2}", None),
        ("MantissaExponent[5/2 + 3, Pi]", None, "{11 / (2 Pi ^ 2), 2}", None),
        ("MantissaExponent[b]", None, "MantissaExponent[b]", None),
        ("MantissaExponent[17, E]", None, "{17 / E ^ 3, 3}", None),
        ("MantissaExponent[17., E]", None, "{0.84638, 3}", None),
        ("MantissaExponent[Exp[Pi], 2]", None, "{E ^ Pi / 32, 5}", None),
        (
            "MantissaExponent[3 + 2 I, 2]",
            ("The value 3 + 2 I is not a real number",),
            "MantissaExponent[3 + 2 I, 2]",
            None,
        ),
        (
            "MantissaExponent[25, 0.4]",
            ("Base 0.4 is not a real number greater than 1.",),
            "MantissaExponent[25, 0.4]",
            None,
        ),
        ("MantissaExponent[0.0000124]", None, "{0.124, -4}", None),
        ("MantissaExponent[0.0000124, 2]", None, "{0.812646, -16}", None),
        ("MantissaExponent[0]", None, "{0, 0}", None),
        ("MantissaExponent[0, 2]", None, "{0, 0}", None),
        ("PrimePowerQ[1]", None, "False", None),
        ("RandomPrime[{10,12}, {2,2}]", None, "{{11, 11}, {11, 11}}", None),
        ("RandomPrime[2, {3,2}]", None, "{{2, 2}, {2, 2}, {2, 2}}", None),
    ],
)
def test_private_doctests_numbertheory(str_expr, msgs, str_expected, fail_msg):
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
