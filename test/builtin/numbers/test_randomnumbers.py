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
        (
            "SeedRandom[1]; rbig = RandomInteger[2^100]; SeedRandom[1]; {rbig == RandomInteger[2^100], 0 <= rbig <= 2^100}",
            None,
            "{True, True}",
            "A range beyond machine integers, reproducible under SeedRandom.",
        ),
        (
            "Union[RandomInteger[{2^64, 2^64 + 2}, 200]] - 2^64",
            None,
            "{0, 1, 2}",
            None,
        ),
        (
            "Dimensions[RandomInteger[{-2^70, 2^70}, {2, 3}]]",
            None,
            "{2, 3}",
            None,
        ),
    ],
)
def test_randomnumbers(str_expr, msgs, str_expected, fail_msg):
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
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("Head[RandomVariate[BinomialDistribution[10, 0.3]]]", None, "Integer", None),
        (
            "Dimensions[RandomVariate[BinomialDistribution[10, 1/3], {2, 3}]]",
            None,
            "{2, 3}",
            None,
        ),
        ("RandomVariate[BinomialDistribution[0, 0.5], 3]", None, "{0, 0, 0}", None),
        (
            "{RandomVariate[BinomialDistribution[10, 0]], "
            "RandomVariate[BinomialDistribution[10, 1]]}",
            None,
            "{0, 10}",
            None,
        ),
        (
            "SeedRandom[5]; rbin = RandomVariate[BinomialDistribution[100, 0.3], 4]; "
            "SeedRandom[5]; rbin == RandomVariate[BinomialDistribution[100, 0.3], 4]",
            None,
            "True",
            "SeedRandom makes the draws reproducible.",
        ),
        (
            "Head[Random[BinomialDistribution[45, 0.3]]]",
            None,
            "Integer",
            "The legacy form used by Combinatorica's RandomGraph.",
        ),
        (
            "RandomVariate[BinomialDistribution[5, 2]]",
            (
                "Parameter 2 at position 2 in BinomialDistribution[5, 2] is expected "
                "to be between 0 and 1 inclusive.",
            ),
            "RandomVariate[BinomialDistribution[5, 2]]",
            None,
        ),
        (
            "RandomVariate[BinomialDistribution[n, p]]",
            (
                "Parameter n at position 1 in BinomialDistribution[n, p] is expected "
                "to be a non-negative integer.",
            ),
            "RandomVariate[BinomialDistribution[n, p]]",
            None,
        ),
        (
            "RandomVariate[BinomialDistribution[10, 0.3], -1]",
            (
                "The array dimensions -1 given in position 2 of "
                "RandomVariate[BinomialDistribution[10, 0.3], -1] should be a list "
                "of non-negative machine-sized integers giving the dimensions for "
                "the result.",
            ),
            "RandomVariate[BinomialDistribution[10, 0.3], -1]",
            None,
        ),
    ],
)
def test_binomial_distribution(str_expr, msgs, str_expected, fail_msg):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
