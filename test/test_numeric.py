# -*- coding: utf-8 -*-
from .helper import check_evaluation


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
