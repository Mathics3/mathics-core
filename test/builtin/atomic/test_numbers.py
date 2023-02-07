# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.atomic.numbers

In particular, RealDigits[] and N[]
"""
from test.helper import check_evaluation

import pytest

from mathics.core.number import MACHINE_PRECISION_VALUE, ZERO_MACHINE_ACCURACY

ZERO_MACHINE_ACCURACY_STR = str(ZERO_MACHINE_ACCURACY)
DEFAUT_ACCURACY_10_STR = str(MACHINE_PRECISION_VALUE - 1)


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
        ('{{a, 2, 3.2`},{2.1`5, 3.2`3, "a"}}', "3."),
        ('{{a, 2, 3.2`},{2.1``3, 3.2``5, "a"}}', "3."),
        ("{1, 0.}", "MachinePrecision"),
        ("{1, 0.``5}", "0."),
    ],
)
def test_precision(str_expr, str_expected):
    check_evaluation(f"Precision[{str_expr}]", str_expected)


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
