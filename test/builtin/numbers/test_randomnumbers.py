# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.randomnumbers
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("SeedRandom[42]; RandomSample[{a, b, c, d}]", "{b, d, a, c}"),
        (
            "SeedRandom[42]; RandomSample[{a, b, c, d, e, f, g, h}, 7]",
            "{b, f, a, h, c, e, d}",
        ),
        ('SeedRandom[42]; RandomSample[{"a", {1, 2}, x, {}}, 3]', "{{1, 2}, {}, a}"),
        (
            "SeedRandom[42]; RandomSample[Range[100], {2, 3}]",
            "{{84, 54, 71}, {46, 45, 40}}",
        ),
        (
            "SeedRandom[42]; RandomSample[Range[100] -> Range[100], 5]",
            "{62, 98, 86, 78, 40}",
        ),
        ("SeedRandom[42]; RandomSample[Range[10]]", "{9, 2, 6, 1, 8, 3, 10, 5, 4, 7}"),
        (
            "SeedRandom[42]; RandomSample[Range[10], {10}]",
            "{9, 2, 6, 1, 8, 3, 10, 5, 4, 7}",
        ),
    ],
)
def test_random_sample(str_expr, str_expected):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "RandomComplex[] //(0 <= Re[#1] <= 1 && 0 <= Im[#1] <= 1)&",
            None,
            "True",
            None,
        ),
        (
            "z=RandomComplex[{1+I, 5+5I}];1 <= Re[z] <= 5 && 1 <= Im[z] <= 5",
            None,
            "True",
            None,
        ),
        (
            "z=.;RandomComplex[{6.3, 2.5 I}] // Head",
            None,
            "Complex",
            None,
        ),
        ("RandomInteger[{1, 5}]// (1<= #1 <= 5)&", None, "True", None),
        ("RandomReal[]// (0<= #1 <= 1)&", None, "True", None),
        (
            "Length /@ RandomReal[100, {2, 3}]",
            None,
            "{3, 3}",
            None,
        ),
        (
            "RandomReal[{0, 1}, {1, -1}]",
            (
                "The array dimensions {1, -1} given in position 2 of RandomReal[{0, 1}, {1, -1}] should be a list of non-negative machine-sized integers giving the dimensions for the result.",
            ),
            "RandomReal[{0, 1}, {1, -1}]",
            None,
        ),
        (
            "SeedRandom[x]",
            ("Argument x should be an integer or string.",),
            "SeedRandom[x]",
            None,
        ),
    ],
)
def test_private_doctests_randomnumbers(str_expr, msgs, str_expected, fail_msg):
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
