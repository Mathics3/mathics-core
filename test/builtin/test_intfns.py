# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.intfns
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("HarmonicNumber[-1.5]", None, "0.613706", None),
    ],
)
def test_private_doctests_recurrence(str_expr, msgs, str_expected, fail_msg):
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
        ## TODO should be ComplexInfinity but mpmath returns +inf
        ("Binomial[-10, -3.5]", None, "Infinity", None),
        ("Subsets[{}]", None, "{{}}", None),
        ("Subsets[]", None, "Subsets[]", None),
        (
            "Subsets[{a, b, c}, 2.5]",
            (
                "Position 2 of Subsets[{a, b, c}, 2.5] must be All, Infinity, a non-negative integer, or a List whose first element (required) is a non-negative integer, second element (optional) is a non-negative integer or Infinity, and third element (optional) is a nonzero integer.",
            ),
            "Subsets[{a, b, c}, 2.5]",
            None,
        ),
        (
            "Subsets[{a, b, c}, -1]",
            (
                "Position 2 of Subsets[{a, b, c}, -1] must be All, Infinity, a non-negative integer, or a List whose first element (required) is a non-negative integer, second element (optional) is a non-negative integer or Infinity, and third element (optional) is a nonzero integer.",
            ),
            "Subsets[{a, b, c}, -1]",
            None,
        ),
        (
            "Subsets[{a, b, c}, {3, 4, 5, 6}]",
            (
                "Position 2 of Subsets[{a, b, c}, {3, 4, 5, 6}] must be All, Infinity, a non-negative integer, or a List whose first element (required) is a non-negative integer, second element (optional) is a non-negative integer or Infinity, and third element (optional) is a nonzero integer.",
            ),
            "Subsets[{a, b, c}, {3, 4, 5, 6}]",
            None,
        ),
        (
            "Subsets[{a, b, c}, {-1, 2}]",
            (
                "Position 2 of Subsets[{a, b, c}, {-1, 2}] must be All, Infinity, a non-negative integer, or a List whose first element (required) is a non-negative integer, second element (optional) is a non-negative integer or Infinity, and third element (optional) is a nonzero integer.",
            ),
            "Subsets[{a, b, c}, {-1, 2}]",
            None,
        ),
        (
            "Subsets[{a, b, c}, All]",
            None,
            "{{}, {a}, {b}, {c}, {a, b}, {a, c}, {b, c}, {a, b, c}}",
            None,
        ),
        (
            "Subsets[{a, b, c}, Infinity]",
            None,
            "{{}, {a}, {b}, {c}, {a, b}, {a, c}, {b, c}, {a, b, c}}",
            None,
        ),
        (
            "Subsets[{a, b, c}, ALL]",
            (
                "Position 2 of Subsets[{a, b, c}, ALL] must be All, Infinity, a non-negative integer, or a List whose first element (required) is a non-negative integer, second element (optional) is a non-negative integer or Infinity, and third element (optional) is a nonzero integer.",
            ),
            "Subsets[{a, b, c}, ALL]",
            None,
        ),
        (
            "Subsets[{a, b, c}, {a}]",
            (
                "Position 2 of Subsets[{a, b, c}, {a}] must be All, Infinity, a non-negative integer, or a List whose first element (required) is a non-negative integer, second element (optional) is a non-negative integer or Infinity, and third element (optional) is a nonzero integer.",
            ),
            "Subsets[{a, b, c}, {a}]",
            None,
        ),
        (
            "Subsets[{a, b, c}, {}]",
            (
                "Position 2 of Subsets[{a, b, c}, {}] must be All, Infinity, a non-negative integer, or a List whose first element (required) is a non-negative integer, second element (optional) is a non-negative integer or Infinity, and third element (optional) is a nonzero integer.",
            ),
            "Subsets[{a, b, c}, {}]",
            None,
        ),
        ("Subsets[{a, b}, 0]", None, "{{}}", None),
        (
            "Subsets[{1, 2}, x]",
            (
                "Position 2 of Subsets[{1, 2}, x] must be All, Infinity, a non-negative integer, or a List whose first element (required) is a non-negative integer, second element (optional) is a non-negative integer or Infinity, and third element (optional) is a nonzero integer.",
            ),
            "Subsets[{1, 2}, x]",
            None,
        ),
        (
            "Subsets[x]",
            ("Nonatomic expression expected at position 1 in Subsets[x].",),
            "Subsets[x]",
            None,
        ),
        (
            "Subsets[x, {1, 2}]",
            ("Nonatomic expression expected at position 1 in Subsets[x, {1, 2}].",),
            "Subsets[x, {1, 2}]",
            None,
        ),
        (
            "Subsets[x, {1, 2, 3}, {1, 3}]",
            (
                "Nonatomic expression expected at position 1 in Subsets[x, {1, 2, 3}, {1, 3}].",
            ),
            "Subsets[x, {1, 2, 3}, {1, 3}]",
            None,
        ),
        (
            "Subsets[a + b + c]",
            None,
            "{0, a, b, c, a + b, a + c, b + c, a + b + c}",
            None,
        ),
        (
            "Subsets[f[a, b, c]]",
            None,
            "{f[], f[a], f[b], f[c], f[a, b], f[a, c], f[b, c], f[a, b, c]}",
            None,
        ),
        ("Subsets[a + b + c, {1, 3, 2}]", None, "{a, b, c, a + b + c}", None),
        ("Subsets[a* b * c, All, {6}]", None, "{a c}", None),
        (
            "Subsets[{a, b, c}, {1, Infinity}]",
            None,
            "{{a}, {b}, {c}, {a, b}, {a, c}, {b, c}, {a, b, c}}",
            None,
        ),
        (
            "Subsets[{a, b, c}, {1, Infinity, 2}]",
            None,
            "{{a}, {b}, {c}, {a, b, c}}",
            None,
        ),
        ("Subsets[{a, b, c}, {3, Infinity, -1}]", None, "{}", None),
    ],
)
def test_private_doctests_combinatorial(str_expr, msgs, str_expected, fail_msg):
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
        (
            "Quotient[13, 0]",
            ("Infinite expression Quotient[13, 0] encountered.",),
            "ComplexInfinity",
            None,
        ),
        ("Quotient[-17, 7]", None, "-3", None),
        ("Quotient[-17, -4]", None, "4", None),
        ("Quotient[19, -4]", None, "-5", None),
        (
            "QuotientRemainder[13, 0]",
            ("The argument 0 in QuotientRemainder[13, 0] should be nonzero.",),
            "QuotientRemainder[13, 0]",
            None,
        ),
        ("QuotientRemainder[-17, 7]", None, "{-3, 4}", None),
        ("QuotientRemainder[-17, -4]", None, "{4, -1}", None),
        ("QuotientRemainder[19, -4]", None, "{-5, -1}", None),
        ("QuotientRemainder[a, 0]", None, "QuotientRemainder[a, 0]", None),
        ("QuotientRemainder[a, b]", None, "QuotientRemainder[a, b]", None),
        ("QuotientRemainder[5.2,2.5]", None, "{2, 0.2}", None),
        ("QuotientRemainder[5, 2.]", None, "{2, 1.}", None),
    ],
)
def test_private_doctests_divlike(str_expr, msgs, str_expected, fail_msg):
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
