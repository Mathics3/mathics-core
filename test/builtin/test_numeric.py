# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numeric

In particular, Rationalize and RealValuNumberQ
"""

from test.helper import check_evaluation, check_wrong_number_of_arguments

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
            "N[3^200]",
            None,
            "2.65614×10^95",
            "Numeric converts a large integer to a MachineReal without losing precision",
        ),
        (
            "N[2^1023]",
            None,
            "8.98847×10^307",
            "Numeric display digits for value under 2^1024 is DefaultPrintDisplay value 6",
        ),
        (
            "N[2^1024]",
            None,
            "1.797693134862316×10^308",
            "Numeric display digits for value on or over= 2^1024 is $MachineDigits",
        ),
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
        # Round must not go through a machine float (53 bits).
        ("Round[10^20 + 1]", None, "100000000000000000001", None),
        ("Round[-10^20 - 1]", None, "-100000000000000000001", None),
        ("Round[123456789012345678901/10]", None, "12345678901234567890", None),
        ("Round[(10^20 + 1)/2]", None, "50000000000000000000", None),
        ("Round[Pi 10^20]", None, "314159265358979323846", None),
        ("Round[Sqrt[2] 10^30]", None, "1414213562373095048801688724210", None),
        ("Round[1.5`30 10^25]", None, "15000000000000000000000000", None),
        ("Round[10^20 + 7, 10]", None, "100000000000000000010", None),
        ("Round[1/2 + 10^-40]", None, "1", None),
        ("Round[{5/2, 7/2, -5/2}]", None, "{2, 4, -2}", None),
    ],
)
def test_numeric(str_expr, msgs, str_expected, fail_msg):
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
    ("str_expr", "msgs", "str_expected"),
    [
        # The precision is min(prec, acc + Log10[Abs[x]]), as in WMA.
        ("Precision[N[Pi, {20, 5}]]", None, "5.49715"),
        ("Precision[N[Pi, {Infinity, 5}]]", None, "5.49715"),
        ("Precision[N[Pi*10^10, {20, 5}]]", None, "15.4971"),
        ("Precision[N[Pi*10^30, {Infinity, 5}]]", None, "35.4971"),
        ("Precision[N[Pi, {20, Infinity}]]", None, "20."),
        ("Precision[N[Pi, {10, 50}]]", None, "10."),
        ("Precision[N[Sqrt[2] + Pi, {30, 10}]]", None, "10.6586"),
        ("Abs[N[Pi, {20, 5}] - Pi] < 10^-5", None, "True"),
        ("Precision[N[{Pi, x + E}, {20, 5}]]", None, "5.43429"),
        # A number below the accuracy becomes a zero of that accuracy.
        ("Accuracy[N[Pi/10^10, {20, 5}]]", None, "5."),
        ("N[Pi/10^10, {20, 5}] == 0", None, "True"),
        ("N[Pi, {Infinity, Infinity}]", None, "Pi"),
        ("Precision[N[Pi, {MachinePrecision, 5}]]", None, "MachinePrecision"),
        ("Precision[N[2.5, {10, 5}]]", None, "MachinePrecision"),
        ("N[npx, {10, 5}]", None, "npx"),
        (
            "N[Pi, {20, 5, 3}]",
            ("Argument {20, 5, 3} is not of the form {precision, accuracy}.",),
            "N[Pi, {20, 5, 3}]",
        ),
        (
            "N[Pi, {a, 5}]",
            ("Requested precision a is not a machine-sized real number.",),
            "N[Pi, {a, 5}]",
        ),
    ],
)
def test_n_precision_and_accuracy(str_expr, msgs, str_expected):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("str_expr", "assert_fail_msg"),
    [
        (
            "Round[a, b]",
            "Round with one symbolic argument should not give an error message",
        ),
        (
            "Round[a, b]",
            "Round with two symbolic arguments should not give an error message",
        ),
        (
            "Sign[x]",
            "Sign with one symbolic argument should not give an error message",
        ),
    ],
)
def test_right_number_of_arguments(str_expr, assert_fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expr,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=assert_fail_msg,
        expected_messages=None,
    )


def test_wrong_number_of_arguments():
    tests = [
        (
            "Round[a, b, c]",
            ["Round called with 3 arguments; 1 or 2 arguments are expected."],
            "Round wrong number of arguments",
        ),
        (
            "Sign[4, 5, 6]",
            ["Sign called with 3 arguments; 1 argument is expected."],
            "Sign wrong number of arguments",
        ),
    ]
    check_wrong_number_of_arguments(tests)
