# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.intfns.combinatorial
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "fail_msg"),
    [
        (
            "BellB[]",
            ["BellB called with 0 arguments; 1 or 2 arguments are expected."],
            "BellB argument number error",
        ),
        (
            "Binomial[]",
            ["Binomial called with 0 arguments; 2 arguments are expected."],
            "Binomial argument number error",
        ),
        (
            "CatalanNumber[1, 2]",
            ["CatalanNumber called with 2 arguments; 1 argument is expected."],
            "CatalanNumber argument number error",
        ),
        (
            "DiceDissimilarity[1, 2, 3]",
            ["DiceDissimilarity called with 3 arguments; 2 arguments are expected."],
            "Binomial argument number error",
        ),
        (
            "EulerE[]",
            ["EulerE called with 0 arguments; 1 or 2 arguments are expected."],
            "Euler argument number error",
        ),
        (
            "JaccardDissimilarity[]",
            ["JaccardDissimilarity called with 0 arguments; 2 arguments are expected."],
            "JaccardDissimilarity argument number error",
        ),
        (
            "LucasL[]",
            ["LucasL called with 0 arguments; 1 or 2 arguments are expected."],
            "LucasL argument number error",
        ),
        (
            "PolygonalNumber[]",
            ["PolygonalNumber called with 0 arguments; 1 or 2 arguments are expected."],
            "PolygonalNumber argument number error",
        ),
        (
            "Subsets[]",
            [
                "Subsets called with 0 arguments; between 1 and 3 arguments are expected."
            ],
            "Subsets argument number error",
        ),
    ],
)
def test_combinatorial_arg_errors(str_expr, msgs, fail_msg):
    """ """

    check_evaluation(
        str_expr,
        str_expr,
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
def test_subsets(str_expr, msgs, str_expected, fail_msg):
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
