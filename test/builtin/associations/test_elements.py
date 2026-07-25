# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.association.elements
"""
from test.helper import check_arg_counts, check_evaluation

import pytest


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "Keys",
            "1 or 2 arguments are",
        ),
        (
            "Lookup",
            "between 2 and 4 arguments are",
        ),
        (
            "Values",
            "1 or 2 arguments are",
        ),
    ],
)
def test_arg_count_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        ("Keys[a -> x]", None, "a", None),
        (
            "Keys[{a -> x, a -> y, {a -> z, <|b -> t|>, <||>, {}}}]",
            None,
            "{a, a, {a, {b}, {}, {}}}",
            None,
        ),
        (
            "Keys[{a -> x, a -> y, <|a -> z, {b -> t}, <||>, {}|>}]",
            None,
            "{a, a, {a, b}}",
            None,
        ),
        (
            "Keys[<|a -> x, a -> y, <|a -> z, <|b -> t|>, <||>, {}|>|>]",
            None,
            "{a, b}",
            None,
        ),
        (
            "Keys[<|a -> x, a -> y, {a -> z, {b -> t}, <||>, {}}|>]",
            None,
            "{a, b}",
            None,
        ),
        (
            "Keys[<|a -> x, <|a -> y, b|>|>]",
            (
                "The argument Association[a -> x, Association[a -> y, b]] is not a valid Association or a list of rules.",
            ),
            "Keys[Association[a -> x, Association[a -> y, b]]]",
            None,
        ),
        (
            "Keys[<|a -> x, {a -> y, b}|>]",
            (
                "The argument Association[a -> x, {a -> y, b}] is not a valid Association or a list of rules.",
            ),
            "Keys[Association[a -> x, {a -> y, b}]]",
            None,
        ),
        (
            "Keys[{a -> x, <|a -> y, b|>}]",
            (
                "The argument Association[a -> y, b] is not a valid Association or a list of rules.",
            ),
            "Keys[{a -> x, Association[a -> y, b]}]",
            None,
        ),
        (
            "Keys[{a -> x, {a -> y, b}}]",
            ("The argument b is not a valid Association or a list of rules.",),
            "Keys[{a -> x, {a -> y, b}}]",
            None,
        ),
        # (
        #     "Keys[a -> x, b -> y]",
        #     None
        #     "(b -> y)[a]",
        #     None,
        # ),
    ],
)
def test_keys(str_expr, expected_messages, str_expected, assert_message):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=assert_message,
        expected_messages=expected_messages,
    )


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        (
            'a=Association[{"F":>1,"G":>2}]; Lookup[a, "H"]',
            None,
            "Missing[KeyAbsent, H]",
            "Lookup test on an association variable where the key is not found.",
        ),
        ("ClearAll[a];", None, "Null", None),
    ],
)
def test_lookup(str_expr, expected_messages, str_expected, assert_message):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=assert_message,
        expected_messages=expected_messages,
    )


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        ("Values[a -> x]", None, "x", None),
        (
            "Values[{a -> x, a -> y, {a -> z, <|b -> t|>, <||>, {}}}]",
            None,
            "{x, y, {z, {t}, {}, {}}}",
            None,
        ),
        (
            "Values[{a -> x, a -> y, <|a -> z, {b -> t}, <||>, {}|>}]",
            None,
            "{x, y, {z, t}}",
            None,
        ),
        (
            "Values[<|a -> x, a -> y, <|a -> z, <|b -> t|>, <||>, {}|>|>]",
            None,
            "{z, t}",
            None,
        ),
        (
            "Values[<|a -> x, a -> y, {a -> z, {b -> t}, <||>, {}}|>]",
            None,
            "{z, t}",
            None,
        ),
        (
            "Values[<|a -> x, <|a -> y, b|>|>]",
            (
                "The argument Association[a -> x, Association[a -> y, b]] is not a valid Association or a list of rules.",
            ),
            "Values[Association[a -> x, Association[a -> y, b]]]",
            None,
        ),
        (
            "Values[<|a -> x, {a -> y, b}|>]",
            (
                "The argument Association[a -> x, {a -> y, b}] is not a valid Association or a list of rules.",
            ),
            "Values[Association[a -> x, {a -> y, b}]]",
            None,
        ),
        (
            "Values[{a -> x, <|a -> y, b|>}]",
            (
                "The argument {a -> x, Association[a -> y, b]} is not a valid Association or a list of rules.",
            ),
            "Values[{a -> x, Association[a -> y, b]}]",
            None,
        ),
        (
            "Values[{a -> x, {a -> y, b}}]",
            (
                "The argument {a -> x, {a -> y, b}} is not a valid Association or a list of rules.",
            ),
            "Values[{a -> x, {a -> y, b}}]",
            None,
        ),
        # (
        #     "Values[a -> x, b -> y]",
        #     "(b -> y)[x]",
        #     None,
        # ),
        ("assoc=.;subassoc=.;", None, "Null", None),
    ],
)
def test_values(str_expr, expected_messages, str_expected, assert_message):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=assert_message,
        expected_messages=expected_messages,
    )
