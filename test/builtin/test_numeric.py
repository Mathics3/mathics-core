# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numeric

In particular, Rationalize and RealValuNumberQ
"""

from test.helper import check_evaluation


def test_rationalize():
    # Some of the Rationalize tests were taken from Symja's tests and docs
    for str_expr, str_expected in (
        (
            "Rationalize[42]",
            "42",
        ),
        (
            "Rationalize[3, 1]",
            "3",
        ),
        (
            "Rationalize[N[Pi] + 0.8 I, 0]",
            "245850922 / 78256779 + 4 I / 5",
        ),
        (
            "Rationalize[1.6 + 0.8 I]",
            "8 / 5 + 4 I / 5",
        ),
        (
            "Rationalize[17 / 7]",
            "17 / 7",
        ),
        (
            "Rationalize[6.75]",
            "27 / 4",
        ),
        (
            "Rationalize[0.25+I*0.33333]",
            "1 / 4 + I / 3",
        ),
        (
            "Rationalize[N[Pi] + 0.8 I, 1*^-6]",
            "355 / 113 + 4 I / 5",
        ),
        (
            "Rationalize[x]",
            "x",
        ),
        (
            "Table[Rationalize[E, 0.1^n], {n, 1, 10}]",
            "{8 / 3, 19 / 7, 87 / 32, 193 / 71, 1071 / 394, 2721 / 1001, 15062 / 5541, 23225 / 8544, 49171 / 18089, 419314 / 154257}",
        ),
    ):
        check_evaluation(str_expr, str_expected)


def test_realvalued():
    for str_expr, str_expected in (
        (
            "Internal`RealValuedNumberQ /@ {1, N[Pi], 1/2, Sin[1.], Pi, 3/4, aa, I}",
            "{True, True, True, True, False, True, False, False}",
        ),
        (
            "Internal`RealValuedNumericQ /@ {1, N[Pi], 1/2, Sin[1.], Pi, 3/4, aa,  I}",
            "{True, True, True, True, True, True, False, False}",
        ),
    ):
        check_evaluation(str_expr, str_expected)
