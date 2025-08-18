# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numeric

In particular, Rationalize and RealValuNumberQ
"""
from test.helper import check_evaluation

import pytest


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


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "p=N[Pi,100]",
            None,
            "3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117068",
            None,
        ),
        (
            "ToString[p]",
            None,
            "3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117068",
            None,
        ),
        ("N[1.012345678901234567890123, 20]", None, "1.0123456789012345679", None),
        ("N[I, 30]", None, "1.00000000000000000000000000000 I", None),
        (
            "N[1.012345678901234567890123, 50] //{#1, #1//Precision}&",
            None,
            "{1.01234567890123456789012, 24.}",
            None,
        ),
        (
            "p=.;x=.;y=.;Rationalize[N[Pi] + 0.8 I, x]",
            ("Tolerance specification x must be a non-negative number.",),
            "Rationalize[3.14159 + 0.8 I, x]",
            None,
        ),
        (
            "Rationalize[N[Pi] + 0.8 I, -1]",
            ("Tolerance specification -1 must be a non-negative number.",),
            "Rationalize[3.14159 + 0.8 I, -1]",
            None,
        ),
        (
            "Rationalize[x, y]",
            ("Tolerance specification y must be a non-negative number.",),
            "Rationalize[x, y]",
            None,
        ),
        (
            "Sign[{1, 2.3, 4/5, {-6.7, 0}, {8/9, -10}}]",
            None,
            "{1, 1, 1, {-1, 0}, {1, -1}}",
            None,
        ),
        ("Sign[1 - 4*I] == (1/17 - 4 I/17) Sqrt[17]", None, "True", None),
        ('Sign["20"]', None, "Sign[20]", None),
    ],
)
def test_private_doctests_numeric(str_expr, msgs, str_expected, fail_msg):
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


@pytest.mark.parametrize(
    ("str_expr", "msgs", "assert_fail_msg"),
    [
        (
            "Round[a, b]",
            None,
            "Round with one symbolic argument should not give an error message",
        ),
        (
            "Round[a, b]",
            None,
            "Round with two symbolic arguments should not give an error message",
        ),
        (
            "Round[a, b, c]",
            ("Round called with 3 arguments; 1 or 2 arguments are expected.",),
            "Round wrong number of arguments",
        ),
        (
            "Sign[x]",
            None,
            "Sign with one symbolic argument should not give an error message",
        ),
        (
            "Sign[4, 5, 6]",
            ("Sign called with 3 arguments; 1 argument is expected.",),
            "Sign wrong number of arguments",
        ),
    ],
)
def test_wrong_number_of_arguments(str_expr, msgs, assert_fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expr,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=assert_fail_msg,
        expected_messages=msgs,
    )
