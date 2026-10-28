# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.testing_expressions
"""

from test.helper import check_arg_counts, check_evaluation

import pytest


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "Between",
            "1 or 2 arguments are",
        ),
        (
            "BooleanQ",
            "1 argument is",
        ),
        (
            "Order",
            "2 arguments are",
        ),
        (
            "TrueQ",
            "1 argument is",
        ),
    ],
)
def test_arg_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)


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
        ("Xor[a, b]", None, "a ⊻ b", None),
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
        ("IntersectingQ[{1, 2}, {2, 3}]", None, "True", None),
        ("IntersectingQ[{1, 2}, {3, 4}]", None, "False", None),
        ("IntersectingQ[{}, {}]", None, "False", None),
        ("DisjointQ[{1, 2}, {3, 4}]", None, "True", None),
        ("DisjointQ[{1, 2}, {2, 3}]", None, "False", None),
        (
            "DisjointQ[{a}]",
            None,
            "DisjointQ[{a}]",
            "DisjointQ is not a one-argument test",
        ),
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
        ("a_ != b_", None, "a_ ≠ b_", None),
        ("Clear[a, b];a != a != a", None, "False", None),
        ('"abc" != "def" != "abc"', None, "False", None),
        ("a != b != a", None, "a ≠ b ≠ a", "Reproduce strange MMA behaviour"),
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
        # Real infinities
        ("{Negative[Infinity], Negative[-Infinity]}", None, "{False, True}", None),
        ("{Positive[Infinity], Positive[-Infinity]}", None, "{True, False}", None),
        (
            "{NonNegative[Infinity], NonNegative[-Infinity]}",
            None,
            "{True, False}",
            None,
        ),
        (
            "{NonPositive[Infinity], NonPositive[-Infinity]}",
            None,
            "{False, True}",
            None,
        ),
        ("Negative[2 {Infinity, 3} - {3, 0}]", None, "{False, False}", None),
        ("Negative[ComplexInfinity]", None, "Negative[ComplexInfinity]", None),
        # Other directions: the sign test of the direction, as in WMA
        (
            "{Positive[DirectedInfinity[1.]], Negative[DirectedInfinity[-1/2]],"
            " NonNegative[DirectedInfinity[Pi]], NonPositive[DirectedInfinity[-Sqrt[2]]]}",
            None,
            "{True, True, True, True}",
            None,
        ),
        (
            "{Positive[DirectedInfinity[I]], Negative[DirectedInfinity[1 + I]],"
            " NonNegative[DirectedInfinity[-I]], NonPositive[DirectedInfinity[I]]}",
            None,
            "{False, False, False, False}",
            None,
        ),
        (
            "Head[Positive[DirectedInfinity[x]]]",
            None,
            "Positive",
            "A symbolic direction is left undecided",
        ),
        # Non-atomic arguments
        ("EvenQ[f[2]]", None, "False", "Non-atomic EvenQ check"),
        ("OddQ[f[1]]", None, "False", "Non-atomic OddQ check"),
        ("PrimeQ[f[2]]", None, "False", "Non-atomic PrimeQ check"),
        ("MatchQ[f[2], _?EvenQ]", None, "False", None),
        ("Cases[{2, f[2], 3}, _?OddQ]", None, "{3}", None),
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
        # Orderless literal patterns mixing an atom and an expression
        ("MatchQ[2 x[3], 2 x[3]]", None, "True", None),
        ("MatchQ[x[3] + 2, 2 + x[3]]", None, "True", None),
        ("MatchQ[2 x[3], 3 x[3]]", None, "False", None),
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
        # Clean the definitions, because
        # a previous definition of `A` or `F` could make
        # the test to fail.
        (None, None, None),
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
        ("Order[F[2], A[2]]", "-1", "Function ordering in function name"),
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
        (
            'Order[<|1->2|>, "a"]',
            "1",
            "Associations come before Strings",
        ),
        (
            "Order[b c, a d]",
            "1",
            "Issue #1866",
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


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "assert_fail_msg"),
    [
        (None, None, None),
        # Sums come after the monomials of their largest variable.
        ("Sort[{a, a + b, b, c, x}]", "{a, b, a + b, c, x}", "a + b after b"),
        (
            "Sort[{f[x], 1 + x, g[x], a + b + c, h[a, b, c]}]",
            "{a + b + c, 1 + x, f[x], g[x], h[a, b, c]}",
            "Sums before general expressions",
        ),
        (
            "Sort[{x, 1 + x, y, x^2, 1 + x^2, x y}]",
            "{x, x ^ 2, 1 + x, 1 + x ^ 2, y, x y}",
            "1 + x after the powers of x, before y",
        ),
        (
            "{Order[1 + x, x^3], Order[1 + a b, a^5 b], Order[1 + a b, c]}",
            "{-1, -1, 1}",
            "The key of a sum is its largest variable to an infinite power",
        ),
        # Two sums: term by term from the largest term, the shorter first.
        (
            "Sort[{1 + x, 2 + x, x + y, a + x, 1 + y}]",
            "{1 + x, 2 + x, a + x, 1 + y, x + y}",
            "Sums with the same largest variable",
        ),
        (
            "Sort[{a + d, b + c, a + b, c + d}]",
            "{a + b, b + c, a + d, c + d}",
            "Sums of two symbols",
        ),
        (
            "Sort[{x + y z, x y + z, x + y + z}]",
            "{x + y + z, x y + z, x + y z}",
            "Sums with products",
        ),
        ("Order[a + b, a + b + c]", "1", "The shorter sum first"),
        ("x y + 1 + x", "1 + x + x y", "Terms of a polynomial"),
        # Symbols are ordered by their names without the context.
        ("Sort[{x, Pi, E, a, z}]", "{a, E, Pi, x, z}", "System` symbols"),
        ("x + Pi", "Pi + x", "Pi before x in a sum"),
        ("Pi x", "Pi x", "Pi before x in a product"),
        ("Sort[{2 Pi, Sqrt[2], E, x}]", "{Sqrt[2], E, 2 Pi, x}", "Numeric constants"),
        # Monomials that differ in a coefficient are ordered by it.
        ("Sort[{x, -x, 2 x}]", "{-x, x, 2 x}", "Coefficients"),
        ("Sort[{1 + x, 1 - x}]", "{1 - x, 1 + x}", "Coefficients in sums"),
        # Factors that are not symbols are variables of the monomial.
        (
            "Sort[{x f[x], Pi g[x], y f[x], a f[x], f[x], z, g[x], f[x]^2, 1 + f[x]}]",
            "{z, f[x], a f[x], x f[x], y f[x], f[x] ^ 2, 1 + f[x], g[x], Pi g[x]}",
            "Monomials in f[x] and g[x]",
        ),
        ("Sort[{a Sin[x], b Cos[x]}]", "{b Cos[x], a Sin[x]}", "Cos before Sin"),
        (
            "Sort[{E^x, E, E^2, F, x}]",
            "{E, E ^ 2, E ^ x, F, x}",
            "A symbolic power after the numeric ones",
        ),
        ("x E^x", "E ^ x x", "E^x before x"),
        (
            "Sort[{Sqrt[Pi] Erf[1/x], x E^(-1/x^2)}]",
            "{E ^ (-1 / x ^ 2) x, Sqrt[Pi] Erf[1 / x]}",
            "Products with general factors",
        ),
        # A sum as a factor sorts right after its largest variable.
        (
            "Sort[{y^3, (3 x + 3 x^2) y, x^3}]",
            "{x ^ 3, (3 x + 3 x ^ 2) y, y ^ 3}",
            "A sum factor before y^3",
        ),
        (
            "Sort[{y^2, (a + x) y, 2 a y, (a + x)^2, x (a + x)}]",
            "{x (a + x), (a + x) ^ 2, 2 a y, (a + x) y, y ^ 2}",
            "Sum factors and powers of sums",
        ),
    ],
)
def test_canonical_order(str_expr: str, str_expected: str, assert_fail_msg: str):
    """The canonical order of sums, symbols and monomials, as in WMA 15."""
    check_evaluation(
        str_expr,
        str_expected,
        hold_expected=True,
        failure_message=assert_fail_msg,
    )
