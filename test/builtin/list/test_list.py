# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.list.constructing
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        (
            "Complement[a, b]",
            ("Nonatomic expression expected at position 1 in Complement[a, b].",),
            "Complement[a, b]",
            None,
        ),
        (
            "Complement[f[a], g[b]]",
            ("Heads f and g at positions 1 and 2 are expected to be the same.",),
            "Complement[f[a], g[b]]",
            None,
        ),
        ("Complement[{a, b, c}, {a, c}, SameTest->(True&)]", None, "{}", None),
        ("Complement[{a, b, c}, {a, c}, SameTest->(False&)]", None, "{a, b, c}", None),
        ("DeleteDuplicates[{3,2,1,2,3,4}, Greater]", None, "{3, 3, 4}", None),
        ("DeleteDuplicates[{}]", None, "{}", None),
        #
        ## Flatten
        #
        (
            "Flatten[{{1, 2}, {3, 4}}, {{-1, 2}}]",
            (
                "Levels to be flattened together in {{-1, 2}} should be lists of positive integers.",
            ),
            "Flatten[{{1, 2}, {3, 4}}, {{-1, 2}}, List]",
            None,
        ),
        (
            "Flatten[{a, b}, {{1}, {2}}]",
            (
                "Level 2 specified in {{1}, {2}} exceeds the levels, 1, which can be flattened together in {a, b}.",
            ),
            "Flatten[{a, b}, {{1}, {2}}, List]",
            None,
        ),
        (
            "m = {{{1, 2}, {3}}, {{4}, {5, 6}}};Flatten[m, {{2}, {1}, {3}, {4}}]",
            (
                "Level 4 specified in {{2}, {1}, {3}, {4}} exceeds the levels, 3, which can be flattened together in {{{1, 2}, {3}}, {{4}, {5, 6}}}.",
            ),
            "Flatten[{{{1, 2}, {3}}, {{4}, {5, 6}}}, {{2}, {1}, {3}, {4}}, List]",
            "Check `n` completion",
        ),
        (
            "m = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};Flatten[m, {3}]",
            (
                "Level 3 specified in {3} exceeds the levels, 2, which can be flattened together in {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}.",
            ),
            "Flatten[{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}, {3}, List]",
            "Test from issue #251",
        ),
        (
            "Flatten[{{1}, 2}, {1, 2}]",
            (
                "Level 2 specified in {1, 2} exceeds the levels, 1, which can be flattened together in {{1}, 2}.",
            ),
            "Flatten[{{1}, 2}, {1, 2}, List]",
            "Reproduce strange head behaviour",
        ),
        (
            "Flatten[a[b[1, 2], b[3]], {1, 2}, b]",
            (
                "Level 1 specified in {1, 2} exceeds the levels, 0, which can be flattened together in a[b[1, 2], b[3]].",
            ),
            "Flatten[a[b[1, 2], b[3]], {1, 2}, b]",
            "MMA BUG: {{1, 2}} not {1, 2}",
        ),
        (
            "Flatten[{{1, 2}, {3, {4}}}, {{1, 2, 3}}]",
            (
                "Level 3 specified in {{1, 2, 3}} exceeds the levels, 2, which can be flattened together in {{1, 2}, {3, {4}}}.",
            ),
            "Flatten[{{1, 2}, {3, {4}}}, {{1, 2, 3}}, List]",
            None,
        ),
        #
        # Join
        #
        ("x=.;y=.;z=.;a=.;m=.;", None, "Null", None),
        ("Join[x, y]", None, "Join[x, y]", None),
        ("Join[x + y, z]", None, "Join[x + y, z]", None),
        (
            "Join[x + y, y z, a]",
            ("Heads Plus and Times are expected to be the same.",),
            "Join[x + y, y z, a]",
            None,
        ),
        ("Join[x, y + z, y z]", None, "Join[x, y + z, y z]", None),
        # Partition
        ("Partition[{a, b, c, d, e}, 2]", None, "{{a, b}, {c, d}}", None),
        # Riffle
        ("Riffle[{1, 2, 3, 4}, {x, y, z, t}]", None, "{1, x, 2, y, 3, z, 4, t}", None),
        ("Riffle[{1, 2}, {1, 2, 3}]", None, "{1, 1, 2}", None),
        ("Riffle[{1, 2}, {1, 2}]", None, "{1, 1, 2, 2}", None),
        ("Riffle[{a,b,c}, {}]", None, "{a, {}, b, {}, c}", None),
        ("Riffle[{}, {}]", None, "{}", None),
        ("Riffle[{}, {a,b}]", None, "{}", None),
        # Split
        (
            "Split[{x, x, x, y, x, y, y, z}, x]",
            None,
            "{{x}, {x}, {x}, {y}, {x}, {y}, {y}, {z}}",
            None,
        ),
        ("Split[{}]", None, "{}", None),
        (
            "A[x__] := 321 /; Length[{x}] == 5;Split[A[x, x, x, y, x, y, y, z]]",
            None,
            "321",
            None,
        ),
        ("ClearAll[A];", None, "Null", None),
        # SplitBy
        (
            "SplitBy[Tuples[{1, 2}, 3], First]",
            None,
            "{{{1, 1, 1}, {1, 1, 2}, {1, 2, 1}, {1, 2, 2}}, {{2, 1, 1}, {2, 1, 2}, {2, 2, 1}, {2, 2, 2}}}",
            None,
        ),
        # Union and Intersection
        (
            "Union[{1, -1, 2}, {-2, 3}, SameTest -> (Abs[#1] == Abs[#2] &)]",
            None,
            "{-2, 1, 3}",
            "Union with SameTest option",
        ),
        (
            "Intersection[{1, -1, -2, 2, -3}, {1, -2, 2, 3}, SameTest -> (Abs[#1] == Abs[#2] &)]",
            None,
            "{-3, -2, 1}",
            "Intersection with SameTest option",
        ),
    ],
)
def test_rearrange_private_doctests(
    str_expr, expected_messages, str_expected, assert_message
):
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
            "ContainsOnly[1, {1, 2, 3}]",
            ("List or association expected instead of 1.",),
            "ContainsOnly[1, {1, 2, 3}]",
            None,
        ),
        (
            "ContainsOnly[{1, 2, 3}, 4]",
            ("List or association expected instead of 4.",),
            "ContainsOnly[{1, 2, 3}, 4]",
            None,
        ),
        (
            "ContainsOnly[{c, a}, {a, b, c}, IgnoreCase -> True]",
            ("Unknown option IgnoreCase -> True in ContainsOnly.",),
            "True",
            None,
        ),
    ],
)
def test_predicates_private_doctests(
    str_expr, expected_messages, str_expected, assert_message
):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=assert_message,
        expected_messages=expected_messages,
    )
