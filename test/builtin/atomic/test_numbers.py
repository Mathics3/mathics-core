# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.atomic.numbers

In particular, RealDigits[] and N[]
"""

from test.helper import check_arg_counts, check_evaluation

import pytest

from mathics.core.number import MACHINE_PRECISION_VALUE, ZERO_MACHINE_ACCURACY

ZERO_MACHINE_ACCURACY_STR = str(ZERO_MACHINE_ACCURACY)
DEFAUT_ACCURACY_10_STR = str(MACHINE_PRECISION_VALUE - 1)


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "Accuracy",
            "1 argument is",
        ),
        (
            "IntegerExponent",
            "1 or 2 arguments are",
        ),
        (
            "Precision",
            "1 argument is",
        ),
    ],
)
def test_arg_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)


def test_realdigits():
    for str_expr, str_expected in (
        (
            "RealDigits[0.000012355555]",
            "{{1, 2, 3, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0}, -4}",
        ),
        (
            "RealDigits[-123.55555]",
            "{{1, 2, 3, 5, 5, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0}, 3}",
        ),
        (
            "RealDigits[Pi, 10, 20, 5]",
            "{{0, 0, 0, 0, 0, 3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9}, 6}",
        ),
        ("RealDigits[20 / 3]", "{{{6}}, 1}"),
        ("RealDigits[3 / 4]", "{{7, 5}, 0}"),
        ("RealDigits[23 / 4]", "{{5, 7, 5}, 1}"),
        (
            "RealDigits[19 / 7, 10, 25]",
            "{{2, 7, 1, 4, 2, 8, 5, 7, 1, 4, 2, 8, 5, 7, 1, 4, 2, 8, 5, 7, 1, 4, 2, 8, 5}, 1}",
        ),
        (
            "RealDigits[100 / 21]",
            "{{{4, 7, 6, 1, 9, 0}}, 1}",
        ),
        (
            "RealDigits[1.234, 2, 15]",
            "{{1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1}, 1}",
        ),
        (
            "RealDigits[Round[x + y]]",
            "RealDigits[Round[x + y]]",
        ),
        (
            "RealDigits[1, 7, 5]",
            "{{1, 0, 0, 0, 0}, 1}",
        ),
        ("RealDigits[0.004]", "{{4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}, -2}"),
        ("RealDigits[1/3]", "{{{3}}, 0}"),
        (
            "RealDigits[1/2, 7]",
            "{{{3}}, 0}",
        ),
        (
            "RealDigits[3/2, 7]",
            "{{1, {3}}, 1}",
        ),
        ("RealDigits[-3/2, 7]", "{{1, {3}}, 1}"),
        ("RealDigits[3/2, 6]", "{{1, 3}, 1}"),
        (
            "RealDigits[Pi, 260, 20]",
            "{{3, 36, 211, 172, 124, 173, 210, 42, 162, 76, 23, 206, 122, 187, 23, 245, 241, 225, 254, 98}, 1}",
        ),
        ("RealDigits[Pi, 260, 5]", "{{3, 36, 211, 172, 124}, 1}"),
        ("RealDigits[1/3]", "{{{3}}, 0}"),
        ("RealDigits[1/2, 7]", "{{{3}}, 0}"),
        ("RealDigits[3/2, 7]", "{{1, {3}}, 1}"),
        ("RealDigits[-3/2, 7]", "{{1, {3}}, 1}"),
        ("RealDigits[3/2, 6]", "{{1, 3}, 1}"),
        (
            "RealDigits[Pi, 10, 20, 5]",
            "{{0, 0, 0, 0, 0, 3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9}, 6}",
        ),
        ("RealDigits[abc]", "RealDigits[abc]"),
        ("RealDigits[abc, 2]", "RealDigits[abc, 2]"),
        ("RealDigits[45]", "{{4, 5}, 2}"),
        (
            "RealDigits[{3.14, 4.5}]",
            "{{{3, 1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}, 1}, {{4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}, 1}}",
        ),
        ("RealDigits[123.45, 40]", "{{3, 3, 18, 0, 0, 0, 0, 0, 0, 0}, 2}"),
        (
            "RealDigits[0.00012345, 2]",
            "{{1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0}, -12}",
        ),
        ("RealDigits[12345, 2, 4]", "{{1, 1, 0, 0}, 14}"),
        (
            "RealDigits[123.45, 2, 15]",
            "{{1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1}, 7}",
        ),
        (
            "RealDigits[0.000012345, 2]",
            "{{1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1}, -16}",
        ),
        ("RealDigits[1/197, 260, 5]", "{{1, 83, 38, 71, 69}, 0}"),
        ("RealDigits[1/197, 260, 5, -6]", "{{246, 208, 137, 67, 80}, -5}"),
        (
            "RealDigits[Pi, 10, 20, -5]",
            "{{9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 6, 4, 3}, -4}",
        ),
        (
            "RealDigits[305.0123, 10, 17, 0]",
            "{{5, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, Indeterminate, Indeterminate, Indeterminate}, 1}",
        ),
        ("RealDigits[220, 140]", "{{1, 80}, 2}"),
        (
            "RealDigits[Sqrt[3], 10, 50]",
            "{{1, 7, 3, 2, 0, 5, 0, 8, 0, 7, 5, 6, 8, 8, 7, 7, 2, 9, 3, 5, 2, 7, 4, 4, 6, 3, 4, 1, 5, 0, 5, 8, 7, 2, 3, 6, 6, 9, 4, 2, 8, 0, 5, 2, 5, 3, 8, 1, 0, 3}, 1}",
        ),
        ("RealDigits[0]", "{{0}, 1}"),
        ("RealDigits[1]", "{{1}, 1}"),
        ("RealDigits[0, 10, 5]", "{{0, 0, 0, 0, 0}, 0}"),
        (
            "RealDigits[11/23]",
            "{{{4, 7, 8, 2, 6, 0, 8, 6, 9, 5, 6, 5, 2, 1, 7, 3, 9, 1, 3, 0, 4, 3}}, 0}",
        ),
        (
            "RealDigits[1/97]",
            "{{{1, 0, 3, 0, 9, 2, 7, 8, 3, 5, 0, 5, 1, 5, 4, 6, 3, 9, 1, 7, 5, 2, 5, 7, 7, 3, 1, 9, 5, 8, 7, 6, 2, 8, 8, 6, 5, 9, 7, 9, 3, 8, 1, 4, 4, 3, 2, 9, 8, 9, 6, 9, 0, 7, 2, 1, 6, 4, 9, 4, 8, 4, 5, 3, 6, 0, 8, 2, 4, 7, 4, 2, 2, 6, 8, 0, 4, 1, 2, 3, 7, 1, 1, 3, 4, 0, 2, 0, 6, 1, 8, 5, 5, 6, 7, 0}}, -1}",
        ),
        (
            "RealDigits[1/97, 2]",
            "{{{1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0}}, -6}",
        ),
        (
            "RealDigits[Pi, 10, 20, -5]",
            "{{9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3, 2, 3, 8, 4, 6, 2, 6, 4, 3}, -4}",
        ),
        (
            "RealDigits[305.0123, 10, 17, 0]",
            "{{5, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, Indeterminate, Indeterminate, Indeterminate}, 1}",
        ),
        ("RealDigits[220, 140]", "{{1, 80}, 2}"),
        (
            "RealDigits[Sqrt[3], 10, 50]",
            "{{1, 7, 3, 2, 0, 5, 0, 8, 0, 7, 5, 6, 8, 8, 7, 7, 2, 9, 3, 5, 2, 7, 4, 4, 6, 3, 4, 1, 5, 0, 5, 8, 7, 2, 3, 6, 6, 9, 4, 2, 8, 0, 5, 2, 5, 3, 8, 1, 0, 3}, 1}",
        ),
        ("RealDigits[0]", "{{0}, 1}"),
        ("RealDigits[1]", "{{1}, 1}"),
        ("RealDigits[0, 10, 5]", "{{0, 0, 0, 0, 0}, 0}"),
        (
            "RealDigits[11/23]",
            "{{{4, 7, 8, 2, 6, 0, 8, 6, 9, 5, 6, 5, 2, 1, 7, 3, 9, 1, 3, 0, 4, 3}}, 0}",
        ),
        (
            "RealDigits[1/97]",
            "{{{1, 0, 3, 0, 9, 2, 7, 8, 3, 5, 0, 5, 1, 5, 4, 6, 3, 9, 1, 7, 5, 2, 5, 7, 7, 3, 1, 9, 5, 8, 7, 6, 2, 8, 8, 6, 5, 9, 7, 9, 3, 8, 1, 4, 4, 3, 2, 9, 8, 9, 6, 9, 0, 7, 2, 1, 6, 4, 9, 4, 8, 4, 5, 3, 6, 0, 8, 2, 4, 7, 4, 2, 2, 6, 8, 0, 4, 1, 2, 3, 7, 1, 1, 3, 4, 0, 2, 0, 6, 1, 8, 5, 5, 6, 7, 0}}, -1}",
        ),
        (
            "RealDigits[1/97, 2]",
            "{{{1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0}}, -6}",
        ),
    ):
        check_evaluation(str_expr, str_expected)


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        # The output form does not show quotes, so compare with ===:
        # the digits must be integers, not strings.
        ("RealDigits[1/7] === {{{1, 4, 2, 8, 5, 7}}, 0}", "True"),
        ("RealDigits[19/7] === {{2, {7, 1, 4, 2, 8, 5}}, 1}", "True"),
        # The period starts after the shortest pre-period.
        ("RealDigits[1/6]", "{{1, {6}}, 0}"),
        ("RealDigits[1/14]", "{{{7, 1, 4, 2, 8, 5}}, -1}"),
        # Zeros in the integer part are digits.
        ("RealDigits[703/7]", "{{1, 0, 0, {4, 2, 8, 5, 7, 1}}, 3}"),
        ("RealDigits[1/3, 1]", "RealDigits[1 / 3, 1]"),
    ],
)
def test_realdigits_rational(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected"),
    [
        (
            "RealDigits[]",
            (
                "RealDigits called with 0 arguments; between 1 and 4 arguments are expected.",
            ),
            "RealDigits[]",
        ),
        (
            "RealDigits[1, 2, 3, 4, 5]",
            (
                "RealDigits called with 5 arguments; between 1 and 4 arguments are expected.",
            ),
            "RealDigits[1, 2, 3, 4, 5]",
        ),
    ],
)
def test_realdigits_argument_count(str_expr, msgs, str_expected):
    check_evaluation(
        str_expr,
        str_expected,
        expected_messages=msgs,
        hold_expected=True,
    )


def test_n():
    for str_expr, str_expected in (
        ('3.14159 * "a string"', "3.14159 a string"),
        ("N[Pi, Pi]", "3.14"),
        ("N[1/9, 30]", "0.111111111111111111111111111111"),
        ("Precision[N[1/9, 30]]", "30."),
        ("N[1.5, 30]", "1.5"),
        ("Precision[N[1.5, 30]]", "MachinePrecision"),
        ("N[1.5, 5]", "1.5"),
        ("Precision[N[1.5, 5]]", "MachinePrecision"),
        ('{N[x], N[x, 30], N["abc"], N["abc", 30]}', "{x, x, abc, abc}"),
        ("N[1.01234567890123456789]", "1.01235"),
        ("N[1.012345678901234567890123, 5]", "1.0123"),
        ("N[1.012345678901234567890123, 5] // Precision", "5."),
        ("N[1.01234567890123456789`]", "1.01235"),
        ("N[1.01234567890123456789`, 20]", "1.01235"),
        ("N[1.01234567890123456789`, 20] // Precision", "MachinePrecision"),
        ("N[1.01234567890123456789`, 2]", "1.01235"),
        ("N[1.01234567890123456789`, 2] // Precision", "MachinePrecision"),
    ):
        check_evaluation(str_expr, str_expected)


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        # Accuracy for 0
        ("0", "Infinity"),
        ("0.", ZERO_MACHINE_ACCURACY_STR),
        ("0.00", ZERO_MACHINE_ACCURACY_STR),
        ("0.00`", ZERO_MACHINE_ACCURACY_STR),
        ("0.00`2", ZERO_MACHINE_ACCURACY_STR),
        ("0.00`20", ZERO_MACHINE_ACCURACY_STR),
        ("0.00000000000000000000", "20."),
        ("0.``2", "2."),
        ("0.``20", "20."),
        ("-0.`2", ZERO_MACHINE_ACCURACY_STR),
        ("-0.`20", ZERO_MACHINE_ACCURACY_STR),
        ("-0.``2", "2."),
        ("-0.``20", "20."),
        # Now for non-zero numbers
        ("10", "Infinity"),
        ("10.", DEFAUT_ACCURACY_10_STR),
        ("10.00", DEFAUT_ACCURACY_10_STR),
        ("10.00`", DEFAUT_ACCURACY_10_STR),
        ("10.00`2", "1."),
        ("10.00`20", "19."),
        ("10.00000000000000000000", "20."),
        ("10.``2", "2."),
        ("10.``20", "20."),
        # For some reason, the following test
        # would fail in WMA
        ("1. I", "Accuracy[1.]"),
        (" 0.4 + 2.4 I", "$MachinePrecision-Log[10, Abs[.4+2.4 I]]"),
        ("2 + 3 I", "Infinity"),
        ('"abc"', "Infinity"),
        # Returns the accuracy of ``` 3.2`3 ```
        ('F["a", 2, 3.2`3]', "Accuracy[3.2`3]"),
        ("F[1.3, Pi, A]", "15.8406"),
        ('{{a, 2, 3.2`},{2.1`5, 3.2`3, "a"}}', "Accuracy[3.2`3]"),
        ('{{a, 2, 3.2`},{2.1``3, 3.2``5, "a"}}', "Accuracy[2.1``3]"),
        ("{1, 0.}", ZERO_MACHINE_ACCURACY_STR),
        ("{1, 0.``5}", "5."),
    ],
)
def test_accuracy(str_expr, str_expected):
    check_evaluation(f"Accuracy[{str_expr}]", str_expected)


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        # Precision for 0
        ("0", "Infinity"),
        ("0.", "MachinePrecision"),
        ("0.00", "MachinePrecision"),
        ("0.00`", "MachinePrecision"),
        ("0.00`2", "MachinePrecision"),
        ("0.00`20", "MachinePrecision"),
        ("0.00000000000000000000", "0."),
        ("0.``2", "0."),
        ("0.``20", "0."),
        ("-0.`2", "MachinePrecision"),
        ("-0.`20", "MachinePrecision"),
        ("-0.``2", "0."),
        ("-0.``20", "0."),
        # Now for non-zero numbers
        ("10", "Infinity"),
        ("10.", "MachinePrecision"),
        ("10.00", "MachinePrecision"),
        ("10.00`", "MachinePrecision"),
        ("10.00`2", "2."),
        ("10.00`20", "20."),
        ("10.00000000000000000000", "21."),
        ("10.``2", "3."),
        ("10.``20", "21."),
        # Returns the precision of ```2.4```
        (" 0.4 + 2.4 I", "MachinePrecision"),
        ("2 + 3 I", "Infinity"),
        ('"abc"', "Infinity"),
        # Returns the precision of ``` 3.2`3 ```
        ('F["a", 2, 3.2`3]', "3."),
        # As in WMA, a machine number makes the precision MachinePrecision.
        ('{{a, 2, 3.2`},{2.1`5, 3.2`3, "a"}}', "MachinePrecision"),
        ('{{a, 2, 3.2`},{2.1``3, 3.2``5, "a"}}', "MachinePrecision"),
        ("F[1.5`3, x, 2.]", "MachinePrecision"),
        ("{1.5`20, 1}", "20."),
        ("1.5`15.954589770191003", "15.9546"),
        ("{1, 0.}", "MachinePrecision"),
        ("{1, 0.``5}", "0."),
        ("Re[0.5+2.3 I]", "MachinePrecision"),
        ("Re[1+2.3 I]", "MachinePrecision"),
        ("Im[0.5+2.3 I]", "MachinePrecision"),
    ],
)
def test_precision(str_expr, str_expected):
    check_evaluation(f"Precision[{str_expr}]", str_expected)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Precision[1.5`20.3]", "20.3", "a real-valued precision is kept"),
        ("Precision[-1.5`20.3]", "20.3", None),
        ("Precision[1.5``20.3]", "20.4761", "from the accuracy"),
        ("Precision[N[Pi, {20, 5}]]", "5.49715", "N with {prec, acc}"),
        (
            "Precision[1.5`5.497 + 1.5`5.497]",
            "5.497",
            "Plus: the absolute errors add up",
        ),
        ("Precision[1.5`5.497 + 2.5`8]", "5.9207", None),
        ("Precision[1.5`20.3 + 3.2`30]", "20.796", None),
        ("Precision[2 + 1.5`20.3]", "20.668", "an exact term adds no error"),
        ("Accuracy[1.5`5 - 1.5`5]", "4.52288", "a zero keeps the accuracy"),
        (
            "Precision[1.5`5.497 * 1.5`5.497]",
            "5.19597",
            "Times: the relative errors add up",
        ),
        ("Precision[N[Pi, 30] N[E, 30]]", "29.699", None),
        ("Precision[N[Pi, 30] E]", "30.", "an exact constant adds no error"),
        ("Precision[N[Pi, 30] + E]", "30.2707", None),
        (
            "ToString[3.14159265358979323846264`20.6]",
            '"3.14159265358979323846"',
            "the digits shown are the precision rounded",
        ),
        (
            "ToString[3.14159265358979323846264`20.4]",
            '"3.1415926535897932385"',
            None,
        ),
        ("ToString[1.5`20.3, InputForm]", '"1.5`20.3"', None),
    ],
)
def test_real_valued_precision(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            "Precision[1.5`20 + 0``10]",
            "10.1761",
            "Plus: a zero adds its absolute error",
        ),
        ("Precision[0``10 + 2]", "10.301", None),
        ("Precision[1.5`20 + 0``10 + 2.5`15]", "10.602", None),
        ("Precision[10^-10 + 0``30]", "20.", None),
        ("Accuracy[0``10 + 0``20]", "10.", "a sum of zeros is a zero"),
        ("Accuracy[0``10 - 0``10]", "9.69897", None),
        ("Accuracy[1.5`20 - 1.5`20 + 0``30]", "19.5229", None),
        (
            "Accuracy[1.5`20 * 0``10]",
            "9.82391",
            "Times: the error of the zero times the other factors",
        ),
        ("Accuracy[2 * 0``10]", "9.69897", None),
        ("Accuracy[0``10 * 0``20]", "30.", None),
        ("Precision[1.5`20 * 0``10]", "0.", None),
        ("0 * 0``10", "0", "an exact zero gives an exact zero"),
        ("0 * 1.5`20", "0", None),
        ("0 * 1.5 // Precision", "MachinePrecision", None),
    ],
)
def test_inexact_zero_plus_times(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        # exact zeros that are syntactically different from the literal 0
        ("(1 - 1) * 1.5`20", "0"),
        ("(1/2 - 1/2) * 1.5`20", "0"),
        ("SetPrecision[0, Infinity] * 1.5`20", "0"),
        ("Accuracy[SetAccuracy[0, 20] * 1.5`20]", "19.8239"),
    ],
)
def test_exact_zero_propagates_through_equivalent_zero_forms(str_expr, str_expected):
    """An exact zero that is constructed internally must still force an exact zero."""
    check_evaluation(str_expr, str_expected)


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("ToString[0``20, OutputForm]", '"0.×10^-20"'),
        ("ToString[0``20.5, OutputForm]", '"0.×10^-20"'),
        ("ToString[0``19.5, OutputForm]", '"0.×10^-19"'),
        ("ToString[SetAccuracy[0, 20] * 1.5`20, OutputForm]", '"0.×10^-19"'),
        ("ToString[0``0.5, OutputForm]", '"0."'),
        ("ToString[0``-2.3, OutputForm]", '"0."'),
    ],
)
def test_inexact_zero_output_form(str_expr, str_expected):
    """As in WMA 15, the exponent of an inexact zero is -Floor[accuracy]."""
    check_evaluation(str_expr, str_expected)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Precision[N[Pi, 20.3]]", "20.3", "a real-valued precision"),
        ("Precision[N[Pi, 41/2]]", "20.5", None),
        ("Precision[N[1/3, 20.3]]", "20.3", None),
        ("Precision[N[Pi E, 20]]", "20.", "the digits lost in Times are added"),
        ("Precision[N[Pi + E, 20.3]]", "20.3", None),
        ("Precision[N[Gamma[1/3], 20.3]]", "20.3", None),
        (
            "Precision[N[Pi - 314159/100000, 20.3]]",
            "20.3",
            "the digits lost in a cancellation are added",
        ),
        ("Precision[N[1.5`10, 20.3]]", "10.", "an input with fewer digits"),
        ("Precision[N[1.5`10 + Pi, 20.3]]", "10.4906", None),
        ("Precision /@ N[{Pi, 1.5`10, 2.5`30.2}, 20.3]", "{20.3, 10., 20.3}", None),
        (
            "ToString[N[a Pi + 1/3, 20.3], InputForm]",
            '"0.333333333333333333333`20.3 + 3.14159265358979323846`20.3*a"',
            None,
        ),
        (
            "N[c, p_?(#>10&)] := p; N[c Pi E, 11] // Precision",
            "MachinePrecision",
            "the rule gives a machine number",
        ),
    ],
)
def test_n_real_valued_precision(str_expr, str_expected, msg):
    """N[expr, p]: compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


def test_max_extra_precision():
    """Compared with WMA 15"""
    check_evaluation("$MaxExtraPrecision", "50.")
    check_evaluation(
        "Block[{$MaxExtraPrecision = 5}, "
        "Precision[N[Pi - 314159265358979/100000000000000, 20]]]",
        "9.71216",
        expected_messages=(
            "Internal precision limit $MaxExtraPrecision = 5. reached while "
            "evaluating -314159265358979 / 100000000000000 + Pi.",
        ),
    )
    check_evaluation(
        "Block[{$MaxExtraPrecision = 0}, Precision[N[Pi E, 20]]]",
        "19.699",
        failure_message="no extra digit, no message",
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Precision[Sqrt[1.5`20]]", "20.301", "Sqrt adds Log10[2]"),
        ("Precision[Sqrt[2.`20]]", "20.301", None),
        ("Precision[1.5`20^(1/3)]", "20.4771", None),
        ("Precision[1.5`20^3]", "19.5229", "x^n loses Log10[n]"),
        ("Precision[(-1.5`20)^3]", "19.5229", None),
        ("Precision[1.5`20^-1]", "20.", None),
        ("Precision[1.5`20^-2]", "19.699", None),
        ("Precision[1.5`20^1000]", "17.", None),
        ("Precision[1.5`20^(10^-5)]", "25.", None),
        ("Precision[2^1.5`20]", "19.9831", "b^x loses Log10[x Log[b]]"),
        ("Precision[(1/2)^1.5`20]", "19.9831", None),
        ("Precision[E^1.5`20]", "19.8239", None),
        ("Precision[10^100.`20]", "17.6378", None),
        ("Precision[1.`20^2.5`20]", "19.6021", None),
        ("Precision[1.5`20^2.5`20]", "19.4542", "the errors of both add up"),
        ("Precision[(1.5`20^2)^0.5`20]", "19.8522", None),
        (
            "ToString[1.5`20^(10^-5), InputForm]",
            '"1.0000040546593011904483653`25."',
            "the digits are computed for the precision",
        ),
        (
            "ToString[E^1.5`20, InputForm]",
            '"4.4816890703380648226`19.82390874094432"',
            None,
        ),
    ],
)
def test_power_real_valued_precision(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Precision[Log[1.5`20]]", "19.608", "Log loses Log10[1/Log[x]]"),
        ("Precision[Log[100.`20]]", "20.6632", None),
        ("Precision[Log[0.5`20]]", "19.8408", None),
        ("Precision[Log[1.0000001`20]]", "13.", "near 1, Log loses digits"),
        ("Precision[Log[10, 1.5`20]]", "19.608", None),
        ("Precision[Log[1.5`20, 10]]", "19.608", "an inexact base"),
        ("Precision[Log[2.`20, 1.5`30]]", "19.8408", "the errors of both add up"),
        ("Precision[Log[2, 8.`20]]", "20.3179", None),
        ("Precision[Log2[1.5`20]]", "19.608", None),
        ("Precision[Log10[1.5`20]]", "19.608", None),
        ("Precision[Exp[-1.5`20]]", "19.8239", "Exp[x] is E^x"),
    ],
)
def test_log_real_valued_precision(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Precision[Sin[1.5`20]]", "20.9732", None),
        ("Precision[Sin[0.3`20]]", "20.0133", None),
        ("Precision[Sin[100.`20]]", "17.7688", "a large argument loses digits"),
        ("Precision[Sin[-1.5`20]]", "20.9732", None),
        ("Precision[Sin[3.14159265358979`20]]", "5.01319", "near a zero of Sin"),
        ("Precision[Cos[1.5`20]]", "18.6746", "near a zero of Cos"),
        ("Precision[Cos[0.3`20]]", "21.0324", None),
        ("Precision[Cos[100.`20]]", "18.2312", None),
        ("Precision[Tan[1.5`20]]", "18.6725", None),
        ("Precision[Tan[0.3`20]]", "19.9736", None),
        ("Precision[Tan[100.`20]]", "17.6401", None),
        ("Precision[Cot[1.5`20]]", "18.6725", None),
        ("Precision[Sec[1.5`20]]", "18.6746", None),
        ("Precision[Sec[0.3`20]]", "21.0324", None),
        ("Precision[Csc[1.5`20]]", "20.9732", None),
        ("Precision[Csc[100.`20]]", "17.7688", None),
    ],
)
def test_trig_real_valued_precision(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Precision[Sin[0]]", "Infinity", "an exact zero stays exact"),
        ("Precision[Cos[0]]", "Infinity", None),
        ("Precision[Tan[0]]", "Infinity", None),
        ("Precision[Sin[Pi]]", "Infinity", None),
        ("Accuracy[Sin[N[Pi, 20]]]", "19.5029", "a zero result keeps an accuracy"),
        ("Accuracy[Cos[N[Pi/2, 20]]]", "19.8039", None),
        ("Accuracy[Sin[2 N[Pi, 20]]]", "19.2018", None),
        ("Accuracy[Sin[0``20]]", "20.", "the absolute error of a zero"),
        ("Accuracy[Tan[0``20]]", "20.", None),
        ("Accuracy[Sin[0``5.5]]", "5.5", None),
        ("Precision[Cos[0``20]]", "40.301", "Cos changes to second order"),
        ("Precision[Sec[0``20]]", "40.301", None),
        ("Precision[Cos[0``5]]", "10.301", None),
        ("Cot[0.]", "ComplexInfinity", "a pole"),
        ("Csc[0.]", "ComplexInfinity", None),
        ("Cot[0``20]", "ComplexInfinity", None),
        ("Csc[0``20]", "ComplexInfinity", None),
        ("Tan[N[Pi/2, 20]]", "ComplexInfinity", "no digit left next to a pole"),
        ("Sec[N[Pi/2, 20]]", "ComplexInfinity", None),
        ("Cot[N[Pi, 20]]", "ComplexInfinity", None),
        ("Csc[N[Pi, 20]]", "ComplexInfinity", None),
        ("Tan[1.5707963`5]", "ComplexInfinity", None),
        ("Precision[Tan[N[Pi/2, 20] + 10^-15]]", "4.80388", "close to a pole"),
        ("Accuracy[Sin[1.`20*^30]]", "0.", "the error is at most the bound 1"),
        ("Accuracy[Cos[1.`20*^30]]", "0.", None),
    ],
)
def test_trig_zero(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Precision[ArcSin[0.3`20]]", "19.9863", None),
        ("Precision[ArcSin[0.99`20]]", "19.3089", "near 1, ArcSin loses digits"),
        ("Precision[ArcCos[0.3`20]]", "20.6049", None),
        ("Precision[ArcCos[0.99`20]]", "18.3047", None),
        ("Precision[ArcCos[-0.3`20]]", "20.7755", None),
        ("Precision[ArcTan[0.3`20]]", "20.0249", None),
        ("Precision[ArcTan[25.`20]]", "21.5836", "a large argument gains digits"),
        ("Precision[ArcCot[-0.3`20]]", "20.6673", None),
        ("Precision[ArcCot[25.`20]]", "20.0005", None),
        ("Precision[ArcSec[1.5`20]]", "19.9733", None),
        ("Precision[ArcSec[-1.5`20]]", "20.4103", None),
        ("Precision[ArcCsc[1.5`20]]", "19.9116", None),
        ("Precision[ArcCsc[-25.`20]]", "19.9998", None),
        ("Precision[ArcTan[1.5`20, 2.5`20]]", "20.0674", "ArcTan[x, y]"),
        ("Precision[ArcTan[-1.5`20, 2.5`30]]", "20.6799", None),
        ("Precision[ArcSin[0]]", "Infinity", "an exact zero stays exact"),
        ("Accuracy[ArcSin[0``20]]", "20.", "the absolute error of a zero"),
        ("Accuracy[ArcTan[0``20]]", "20.", None),
        ("Precision[ArcCos[0``20]]", "20.1961", None),
        ("Precision[ArcCot[0``20]]", "20.1961", "ArcCot jumps at 0"),
        ("ArcSin[0`20]", "0", "0`20 is an exact 0"),
        ("Precision[ArcSin[0.0`20]]", "MachinePrecision", "0.0`20 is 0."),
        ("Accuracy[ArcCos[1.`20]]", "9.84949", "ArcCos changes by Sqrt[2 10^-20]"),
        ("Accuracy[ArcSec[1.`20]]", "9.84949", None),
        ("Accuracy[ArcCos[1.`5]]", "2.34948", None),
        ("Precision[ArcSec[-1.`20]]", "10.3466", None),
        ("Precision[ArcCos[0.99999999`20]]", "12.301", "next to the end"),
        ("Precision[ArcSin[0.99999999`20]]", "16.3466", None),
        ("Precision[ArcSec[1.00000001`20]]", "12.301", None),
        ("Precision[ArcSin[0.9999999999999999999`20]]", "10.8465", None),
        (
            "Precision[ArcSin[1.`20]]",
            "10.0456",
            "WMA gives 20.1961 here, but 10.8465 just below 1",
        ),
        ("Precision[ArcCsc[1.`20]]", "10.0456", None),
    ],
)
def test_arctrig_real_valued_precision(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Precision[Sinh[0.3`20]]", "19.9872", None),
        ("Precision[Sinh[-1.5`20]]", "19.7806", None),
        ("Precision[Sinh[25.`20]]", "18.6021", "a large argument loses digits"),
        ("Precision[Cosh[0.3`20]]", "21.0585", None),
        ("Precision[Cosh[1.5`20]]", "19.8672", None),
        ("Precision[Tanh[0.3`20]]", "19.9519", "as in WMA, as Sinh / Cosh"),
        ("Precision[Tanh[0.99`20]]", "19.6868", None),
        ("Precision[Tanh[1.`20]]", "20.2585", None),
        ("Precision[Tanh[1.5`20]]", "20.5237", None),
        ("Precision[Tanh[25.`20]]", "39.7147", "a large argument gains digits"),
        ("Precision[Coth[-0.3`20]]", "19.9519", None),
        ("Precision[Coth[1.5`20]]", "20.5237", None),
        ("Precision[Sech[0.3`20]]", "21.0585", None),
        ("Precision[Csch[1.5`20]]", "19.7806", None),
        ("Precision[ArcSinh[0.3`20]]", "20.0124", None),
        ("Precision[ArcSinh[25.`20]]", "20.5928", None),
        ("Precision[ArcCosh[1.5`20]]", "19.8557", None),
        ("Precision[ArcCosh[25.`20]]", "20.592", None),
        ("Precision[ArcTanh[-0.3`20]]", "19.9726", None),
        ("Precision[ArcTanh[0.99`20]]", "18.7259", "near 1, ArcTanh loses digits"),
        ("Precision[ArcCoth[1.5`20]]", "19.8265", None),
        ("Precision[ArcSech[0.3`20]]", "20.2522", None),
        ("Precision[ArcSech[0.99`20]]", "18.3018", None),
        ("Precision[ArcCsch[0.3`20]]", "20.3018", None),
        ("Precision[ArcCsch[-25.`20]]", "20.0002", None),
        ("Precision[Sinh[0]]", "Infinity", "an exact zero stays exact"),
        ("Accuracy[Sinh[0``20]]", "20.", "the absolute error of a zero"),
        ("Accuracy[Tanh[0``20]]", "20.", None),
        ("Accuracy[ArcSinh[0``20]]", "20.", None),
        ("Accuracy[ArcTanh[0``20]]", "20.", None),
        ("Precision[Cosh[0``20]]", "40.301", "Cosh changes to second order"),
        ("Precision[Sech[0``20]]", "40.301", None),
        ("Coth[0``20]", "ComplexInfinity", "a pole"),
        ("Csch[0.]", "ComplexInfinity", None),
        ("Csch[0``20]", "ComplexInfinity", None),
        ("Sinh[0`20]", "0", "0`20 is an exact 0"),
        ("Precision[Cosh[0.0`20]]", "MachinePrecision", "0.0`20 is 0."),
        ("Accuracy[ArcCosh[1.`20]]", "9.84949", "at the end of the domain"),
        ("Accuracy[ArcSech[1.`20]]", "9.84949", None),
        ("Precision[ArcCosh[1.00000001`20]]", "12.301", "next to the end"),
        ("Precision[ArcSech[0.99999999`20]]", "12.301", None),
        ("Precision[ArcTanh[0.99999999`20]]", "13.2813", "next to a pole"),
        ("ArcTanh[1.`20]", "Indeterminate", "an inexact pole"),
        ("ArcTanh[-1.`20]", "Indeterminate", None),
        ("ArcTanh[1.]", "Indeterminate", None),
        ("ArcTanh[1.0000001`5]", "Indeterminate", "the error covers the pole"),
        ("ArcTanh[0.9999999`5]", "Indeterminate", None),
        ("ArcTanh[1.000001`6]", "Indeterminate", None),
        ("Precision[ArcTanh[0.999999`6.1]]", "1.26163", "the error misses it"),
        ("ArcTanh[1]", "Infinity", "an exact pole"),
        ("ArcCoth[1.`20]", "Indeterminate", None),
        ("ArcCoth[-1.]", "Indeterminate", None),
        ("ArcCoth[1.0000001`5]", "Indeterminate", None),
        ("Precision[ArcCoth[1.000001`6.1]]", "1.26163", None),
        ("ArcCoth[-1]", "-Infinity", None),
        ("Accuracy[Sinh[1000.`2]]", "-434.993", "no digit left, no bound"),
    ],
)
def test_hyperbolic_real_valued_precision(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (None, None, None),
        ("N[Sqrt[2], 41]//Precision", "41.", "first round sqrt[2`41]"),
        ("N[Sqrt[2], 40]//Precision", "40.", "first round sqrt[2`40]"),
        ("N[Sqrt[2], 41]//Precision", "41.", "second round sqrt[2`41]"),
        ("N[Sqrt[2], 40]//Precision", "40.", "second round sqrt[2`40]"),
        (
            "N[Sqrt[2], 41]",
            '"1.4142135623730950488016887242096980785697"',
            "third round sqrt[2`41]",
        ),
        (
            "Precision/@Table[N[Pi,p],{p, {5, 100, MachinePrecision, 20}}]",
            "{5., 100., MachinePrecision, 20.}",
            None,
        ),
        (
            "Precision/@Table[N[Sin[1],p],{p, {5, 100, MachinePrecision, 20}}]",
            "{5., 100., MachinePrecision, 20.}",
            None,
        ),
        ("N[Sqrt[2], 40]", '"1.414213562373095048801688724209698078570"', None),
        ("N[Sqrt[2], 4]", '"1.414"', None),
        ("N[Pi, 40]", '"3.141592653589793238462643383279502884197"', None),
        ("N[Pi, 4]", '"3.142"', None),
        ("N[Pi, 41]", '"3.1415926535897932384626433832795028841972"', None),
        ("N[Sqrt[2], 41]", '"1.4142135623730950488016887242096980785697"', None),
    ],
)
def test_change_prec(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "warnings", "str_expected", "fail_msg"),
    [
        ("IntegerLength /@ (10 ^ Range[100] - 1) == Range[1, 100]", None, "True", None),
        (
            "RealDigits[-1.25, -1]",
            ("Base -1 is not a real number greater than 1.",),
            "RealDigits[-1.25, -1]",
            None,
        ),
        (
            "RealDigits[-Pi]",
            ("The number of digits to return cannot be determined.",),
            "RealDigits[-Pi]",
            None,
        ),
        (
            "RealDigits[I, 7]",
            ("The value I is not a real number.",),
            "RealDigits[I, 7]",
            None,
        ),
        (
            "RealDigits[Pi]",
            ("The number of digits to return cannot be determined.",),
            "RealDigits[Pi]",
            None,
        ),
        (
            "RealDigits[3 + 4 I]",
            ("The value 3 + 4 I is not a real number.",),
            "RealDigits[3 + 4 I]",
            None,
        ),
        (
            "RealDigits[3.14, 10, 1.5]",
            (
                "Non-negative machine-sized integer expected at position 3 in RealDigits[3.14, 10, 1.5].",
            ),
            "RealDigits[3.14, 10, 1.5]",
            None,
        ),
        (
            "RealDigits[3.14, 10, 1, 1.5]",
            (
                "Machine-sized integer expected at position 4 in RealDigits[3.14, 10, 1, 1.5].",
            ),
            "RealDigits[3.14, 10, 1, 1.5]",
            None,
        ),
        ("N[Pi, 10]", None, "3.141592654", None),
        (
            "$MaxPrecision = x",
            (
                "Cannot set $MaxPrecision to x; value must be a positive number or Infinity.",
            ),
            "x",
            None,
        ),
        (
            "$MaxPrecision = -Infinity",
            (
                "Cannot set $MaxPrecision to -Infinity; value must be a positive number or Infinity.",
            ),
            "-Infinity",
            None,
        ),
        (
            "$MaxPrecision = 0",
            (
                "Cannot set $MaxPrecision to 0; value must be a positive number or Infinity.",
            ),
            "0",
            None,
        ),
        ("$MaxPrecision = Infinity;$MinPrecision = 15;", None, "Null", None),
        (
            "$MaxPrecision = 10",
            ("Cannot set $MaxPrecision such that $MaxPrecision < $MinPrecision.",),
            "10",
            None,
        ),
        ("$MaxPrecision", None, "Infinity", None),
        ("$MinPrecision = 0;", None, "Null", None),
        ("N[E, MachinePrecision]", None, "2.71828", None),
        ("Round[MachinePrecision]", None, "16", None),
        ("N[Pi, 10]", None, "3.141592654", None),
        (
            "$MinPrecision = x",
            ("Cannot set $MinPrecision to x; value must be a non-negative number.",),
            "x",
            None,
        ),
        (
            "$MinPrecision = -Infinity",
            (
                "Cannot set $MinPrecision to -Infinity; value must be a non-negative number.",
            ),
            "-Infinity",
            None,
        ),
        (
            "$MinPrecision = -1",
            ("Cannot set $MinPrecision to -1; value must be a non-negative number.",),
            "-1",
            None,
        ),
        ("$MinPrecision = 0;", None, "Null", None),
        ("$MaxPrecision = 10;", None, "Null", None),
        (
            "$MinPrecision = 15",
            ("Cannot set $MinPrecision such that $MaxPrecision < $MinPrecision.",),
            "15",
            None,
        ),
        ("$MinPrecision", None, "0", None),
        ("$MaxPrecision = Infinity;", None, "Null", None),
    ],
)
def test_string(str_expr, warnings, str_expected, fail_msg):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message="",
        expected_messages=warnings,
        hold_expected=True,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected"),
    [
        ("IntegerExponent[0, 2]", None, "Infinity"),
        ("IntegerExponent[0]", None, "Infinity"),
        ("IntegerExponent[2^1000 3, 2]", None, "1000"),
        (
            "IntegerExponent[10, 1]",
            ("Base 1 is not an integer greater than 1.",),
            "IntegerExponent[10, 1]",
        ),
        (
            "IntegerExponent[10, 0]",
            ("Base 0 is not an integer greater than 1.",),
            "IntegerExponent[10, 0]",
        ),
        (
            "IntegerExponent[10, -2]",
            ("Base -2 is not an integer greater than 1.",),
            "IntegerExponent[10, -2]",
        ),
    ],
)
def test_integer_exponent(str_expr, msgs, str_expected):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Precision[SetPrecision[1.5, 20.3]]", "20.3", None),
        ("Precision[SetPrecision[1.5`10, 20.3]]", "20.3", "more digits"),
        ("Precision[SetPrecision[1.5`20, 2.5]]", "2.5", "fewer digits"),
        ("Precision[SetPrecision[1/3, 20.3]]", "20.3", None),
        ("Precision[SetPrecision[Pi, 20.3]]", "20.3", None),
        (
            "ToString[SetPrecision[0.1, 20]]",
            '"0.10000000000000000555"',
            "the binary value is kept",
        ),
        ("SetPrecision[0, 20.3]", "0", None),
        ("SetPrecision[0., 20]", "0", "a machine zero becomes an exact 0"),
        ("SetPrecision[0``10, 20]", "0", None),
        (
            "Precision /@ SetPrecision[{1.5, x, 2/3}, 20.3]",
            "{20.3, Infinity, 20.3}",
            None,
        ),
        (
            "SetPrecision[1.5`20, MachinePrecision] // Precision",
            "MachinePrecision",
            None,
        ),
        ("SetPrecision[1/3, MachinePrecision] // Precision", "MachinePrecision", None),
        ("SetPrecision[1.5`20, Infinity]", "3 / 2", None),
        ("SetPrecision[0.1, Infinity]", "3602879701896397 / 36028797018963968", None),
        ("SetPrecision[Pi, Infinity]", "Pi", None),
        ("Precision[SetPrecision[Sin[2], 20]]", "20.0384", "set, then evaluated"),
        ("Precision[SetPrecision[Sqrt[2], 20]]", "20.301", "an exact exponent stays"),
        ("Precision[SetPrecision[2^(1/3), 20]]", "20.4771", None),
        ("SetPrecision[x^2, 20]", "x ^ 2", None),
        ("Precision[SetPrecision[x^2.5, 20]]", "20.", None),
        ("Precision[SetPrecision[Sin[Pi/7], 20]]", "19.7296", None),
        ("Precision[SetPrecision[1.5 + 2.5 I, 20.3]]", "20.3", "complex"),
        ("Precision[Re[SetPrecision[1.5 + 2.5 I, 20.3]]]", "20.1619", None),
        ("Precision[Im[SetPrecision[1.5 + 2.5 I, 20.3]]]", "20.3837", None),
        ("Precision[SetPrecision[2 I, 20]]", "20.", None),
        ("Precision[SetPrecision[1.5 + 0. I, 20]]", "20.1505", None),
        ("Accuracy[Im[SetPrecision[1.5`20 + 0``5 I, 20]]]", "19.9744", None),
    ],
)
def test_set_precision(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("Precision[SetAccuracy[1.5, 20.3]]", "20.4761", None),
        ("Precision[SetAccuracy[1/3, 20.3]]", "19.8229", None),
        ("Precision[SetAccuracy[150.5, 20]]", "22.1775", None),
        ("Accuracy[SetAccuracy[0, 20.3]]", "20.3", "an exact 0 becomes inexact"),
        ("Accuracy[SetAccuracy[0., 20]]", "20.", None),
        ("Precision[SetAccuracy[1.5`10, 30]]", "30.1761", None),
        ("Precision[SetAccuracy[1.5`20, 5.5]]", "5.67609", None),
        ("Accuracy[SetAccuracy[0.001, 2]]", "2.", "no digit left: a zero"),
        ("Accuracy[SetAccuracy[1.5, -3]]", "-3.", None),
        ("SetAccuracy[1.5, Infinity]", "3 / 2", None),
        ("Precision /@ SetAccuracy[{1.5, 1500.}, 10]", "{10.1761, 13.1761}", None),
        ("Precision[SetAccuracy[1.5 + 2.5 I, 20]]", "20.4647", "complex"),
        ("Precision[Re[SetAccuracy[1.5 + 2.5 I, 20]]]", "20.3266", None),
        ("Accuracy[Re[SetAccuracy[2 I, 20]]]", "20.1505", None),
    ],
)
def test_set_accuracy(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


def test_set_precision_messages():
    """Compared with WMA 15"""
    check_evaluation(
        "SetPrecision[1.5, a]",
        "SetPrecision[1.5, a]",
        expected_messages=(
            "Requested precision a is not a machine-sized real number "
            "between $MinPrecision and $MaxPrecision.",
        ),
    )
    check_evaluation(
        "Accuracy[SetPrecision[1.5, -1]]",
        "-0.176091",
        expected_messages=(
            "Requested precision -1 is smaller than $MinPrecision. "
            "Using $MinPrecision instead.",
        ),
    )
    check_evaluation(
        "SetAccuracy[1.5, a]",
        "SetAccuracy[1.5, a]",
        expected_messages=(
            "Requested accuracy a is not a real number within the allowable range.",
        ),
    )
    check_evaluation(
        "SetPrecision[1.5, 20, 3]",
        "SetPrecision[1.5, 20, 3]",
        expected_messages=(
            "SetPrecision called with 3 arguments; 2 arguments are expected.",
        ),
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            "Precision[1.5`20 - 1.4`2]",
            "0.853872",
            "1.4`2 keeps its value, not 1.400390625",
        ),
        ("Accuracy[1.5`20 - 1.4`2]", "1.85387", None),
        ("Precision[1.4`2 + 1.4`2]", "2.", None),
        ("Precision[1.4`2]", "2.", "the precision does not change"),
        ("Precision[N[1.4`2, 10]]", "2.", None),
        ("ToString[SetPrecision[1.4`2, 20]]", '"1.4000000000000000000"', None),
        ("ToString[SetPrecision[-1.4`2, 20]]", '"-1.4000000000000000000"', None),
        ("ToString[SetPrecision[1.4`2 + 1.4`2, 20]]", '"2.8000000000000000000"', None),
        ("ToString[SetPrecision[1.4`2^2, 18]]", '"1.96000000000000000"', None),
        ("ToString[SetPrecision[Sin[1.4`2], 18]]", '"0.985449729988460181"', None),
        ("ToString[SetPrecision[N[1/3, 2], 18]]", '"0.333333333333333333"', "N"),
        ("ToString[SetPrecision[N[Pi, 3], 18]]", '"3.14159265358979324"', None),
        ("N[Pi, 3]", "3.14", None),
        ("SameQ[1.4`2, 1.4001`2]", "True", None),
    ],
)
def test_low_precision_storage(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            "ToString[3.1415926535897932385`3, InputForm]",
            '"3.1415926535897932385`3."',
            "InputForm shows the digits that are kept, not the precision",
        ),
        (
            "ToString[FullForm[3.1415926535897932385`3]]",
            '"3.1415926535897932385`3."',
            None,
        ),
        (
            "ToString[-3.1415926535897932385`3, InputForm]",
            '"-3.1415926535897932385`3."',
            None,
        ),
        ("ToString[3.1415926535897932385`3]", '"3.14"', "OutputForm: the precision"),
        (
            "StringTake[ToString[N[Pi, 20] + 0``3, InputForm], 22]",
            '"3.1415926535897932385`"',
            None,
        ),
        (
            "Precision[1.5`20 - ToExpression[ToString[1.4`2, InputForm]]]",
            "0.853872",
            "reading InputForm back gives the same kept value",
        ),
        (
            "ToExpression[ToString[#, InputForm]] === # &[N[1/3, 3]]",
            "True",
            None,
        ),
        (
            "Precision[1.5`20 - ToExpression[ToString[N[1/3, 3], InputForm]]]",
            "Precision[1.5`20 - N[1/3, 3]]",
            None,
        ),
    ],
)
def test_low_precision_input_form(str_expr, str_expected, msg):
    """Compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            "SetPrecision[1.5 + 2.5 I, 20] === SetPrecision[1.5 + 2.5 I, 20.3]",
            "True",
            "SameQ: numbers that agree to their precision are the same",
        ),
        (
            "Precision /@ {SetPrecision[1.5 + 2.5 I, 20], "
            "SetPrecision[1.5 + 2.5 I, 20.3]}",
            "{20., 20.3}",
            "but they are different numbers, not one cached object",
        ),
        ("SameQ[1.5`20, 1.5`20.3]", "True", None),
        (
            "Precision[SetAccuracy[1.5 + 2.5 I, 20]]",
            "20.4647",
            "each part gets accuracy 20 + Log10[2]/2",
        ),
        (
            "Precision /@ {Re[#], Im[#]} &[SetPrecision[1.5 + 2.5 I, 20.3]]",
            "{20.1619, 20.3837}",
            "both parts share the same accuracy",
        ),
    ],
)
def test_low_precision_complex_cache_regression(str_expr, str_expected, msg):
    """Guard against cache collisions in complex numbers; compared with WMA 15"""
    check_evaluation(str_expr, str_expected, failure_message=msg)
