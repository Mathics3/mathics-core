# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.testing_expressions
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("AnyTrue[{}, EvenQ]", None, "False", None),
        ("AllTrue[{}, EvenQ]", None, "True", None),
        ("Equivalent[]", None, "True", None),
        ("Equivalent[a]", None, "True", None),
        ("NoneTrue[{}, EvenQ]", None, "True", None),
        ("Xor[]", None, "False", None),
        ("Xor[a]", None, "a", None),
        ("Xor[False]", None, "False", None),
        ("Xor[True]", None, "True", None),
        ("Xor[a, b]", None, "a \\[Xor] b", None),
    ],
)
def test_logic(str_expr, msgs, str_expected, fail_msg):
    """text_expressions.logic"""
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
        ("SubsetQ[{1, 2, 3}, {0, 1}]", None, "False", None),
        ("SubsetQ[{1, 2, 3}, {1, 2, 3, 4}]", None, "False", None),
        (
            "SubsetQ[{1, 2, 3}]",
            ("SubsetQ called with 1 argument; 2 arguments are expected.",),
            "SubsetQ[{1, 2, 3}]",
            None,
        ),
        (
            "SubsetQ[{1, 2, 3}, {1, 2}, {3}]",
            ("SubsetQ called with 3 arguments; 2 arguments are expected.",),
            "SubsetQ[{1, 2, 3}, {1, 2}, {3}]",
            None,
        ),
        (
            "SubsetQ[a + b + c, {1}]",
            ("Heads Plus and List at positions 1 and 2 are expected to be the same.",),
            "SubsetQ[a + b + c, {1}]",
            None,
        ),
        (
            "SubsetQ[{1, 2, 3}, n]",
            ("Nonatomic expression expected at position 2 in SubsetQ[{1, 2, 3}, n].",),
            "SubsetQ[{1, 2, 3}, n]",
            None,
        ),
        ("SubsetQ[f[a, b, c], f[a]]", None, "True", None),
    ],
)
def test_list_oriented(str_expr, msgs, str_expected, fail_msg):
    """text_expressions.logic"""
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
        ('BooleanQ["string"]', None, "False", None),
        ("BooleanQ[Together[x/y + y/x]]", None, "False", None),
        ("Max[x]", None, "x", None),
        ("Min[x]", None, "x", None),
        ("Pi != N[Pi]", None, "False", None),
        ("a_ != b_", None, "a_ != b_", None),
        ("Clear[a, b];a != a != a", None, "False", None),
        ('"abc" != "def" != "abc"', None, "False", None),
        ("a != b != a", None, "a != b != a", "Reproduce strange MMA behaviour"),
    ],
)
def test_equality_inequality(str_expr, msgs, str_expected, fail_msg):
    """text_expressions.logic"""
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
        ("MachineNumberQ[1.5 + 3.14159265358979324 I]", None, "True", None),
        ("MachineNumberQ[1.5 + 5 I]", None, "True", None),
        ("Negative[-E]", None, "True", None),
        ("Negative[Sin[{11, 14}]]", None, "{True, False}", None),
        ("Positive[Pi]", None, "True", None),
        ("Positive[x]", None, "Positive[x]", None),
        ("Positive[Sin[{11, 14}]]", None, "{False, True}", None),
        ("PrimeQ[1]", None, "False", None),
        ("PrimeQ[2 ^ 255 - 1]", None, "False", None),
    ],
)
def test_numerical_properties(str_expr, msgs, str_expected, fail_msg):
    """text_expressions.numerical_properties"""
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
        # Two default arguments (linear)
        ("MatchQ[1, a_.+b_.*x_]", None, "True", None),
        ("MatchQ[x, a_.+b_.*x_]", None, "True", None),
        ("MatchQ[2*x, a_.+b_.*x_]", None, "True", None),
        ("MatchQ[1+x, a_.+b_.*x_]", None, "True", None),
        ("MatchQ[1+2*x, a_.+b_.*x_]", None, "True", None),
        # Default argument (power)
        ("MatchQ[1, x_^m_.]", None, "True", None),
        ("MatchQ[x, x_^m_.]", None, "True", None),
        ("MatchQ[x^1, x_^m_.]", None, "True", None),
        ("MatchQ[x^2, x_^m_.]", None, "True", None),
        # Two default arguments (power)
        ("MatchQ[1, x_.^m_.]", None, "True", None),
        ("MatchQ[x, x_.^m_.]", None, "True", None),
        ("MatchQ[x^1, x_.^m_.]", None, "True", None),
        ("MatchQ[x^2, x_.^m_.]", None, "True", None),
        # Two default arguments (no non-head)
        ("MatchQ[1, a_.+b_.]", None, "True", None),
        ("MatchQ[x, a_.+b_.]", None, "True", None),
        ("MatchQ[1+x, a_.+b_.]", None, "True", None),
        ("MatchQ[1+2*x, a_.+b_.]", None, "True", None),
        ("MatchQ[1, a_.*b_.]", None, "True", None),
        ("MatchQ[x, a_.*b_.]", None, "True", None),
        ("MatchQ[2*x, a_.*b_.]", None, "True", None),
    ],
)
def test_matchq(str_expr, msgs, str_expected, fail_msg):
    """text_expressions.matchq"""
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
    ("str_expr", "str_expected", "assert_fail_msg"),
    [
        ('Order["c", "d"]', "1", "Alphabetic order: 'c' comes before 'd'"),
        ('Order["d", "c"]', "-1", "Alphabetic order: 'd' comes after 'c'"),
        ('Order["c", ByteArray[{99}]]', "1", "String comes before ByteArray"),
        ('Order[ByteArray[{1, 99}], "ZZZZZ"]', "-1", "ByteArray comes after String"),
        ('Order["xyzzy", "xyzzy"]', "0", "Equal strings"),
        (
            "Order[ByteArray[{1, 99}], ByteArray[{2, 0}]]",
            "1",
            "Numeric ordering within a ByteArray",
        ),
        ('Order["a", 1000]', "-1", "String comes after Integer"),
        ("Order[0.9, 1]", "1", "Numeric less-than comparison between Real and Integer"),
        (
            "Order[1.2, 1]",
            "-1",
            "Numeric greater than comparison between Real and Integer",
        ),
        # FIXME: Intermittently fails - investigate why
        # ("Order[F[2], A[2]]", "-1", "Function ordering in function name"),
        (
            "Order[F[2], F[3]]",
            "1",
            "Function ordering in function with a single parameter",
        ),
        (
            "Order[F[2, 3], F[2]]",
            "-1",
            "Function ordering in function with mixed-length parameters",
        ),
    ],
)
def test_order(str_expr: str, str_expected: str, assert_fail_msg: str):
    """text_expressions.matchq"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=False,
        to_string_expected=False,
        hold_expected=False,
        failure_message=assert_fail_msg,
    )
