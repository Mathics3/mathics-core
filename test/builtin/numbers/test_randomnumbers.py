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
