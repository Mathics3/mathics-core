# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.tensor.
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "Dimensions[{}]",
            None,
            "{0}",
            None,
        ),
        (
            "Dimensions[{{}}]",
            None,
            "{1, 0}",
            None,
        ),
        ## Issue #670
        (
            "A = {{ b ^ ( -1 / 2), 0}, {a * b ^ ( -1 / 2 ), b ^ ( 1 / 2 )}}",
            None,
            "{{1 / Sqrt[b], 0}, {a / Sqrt[b], Sqrt[b]}}",
            None,
        ),
        ("A . Inverse[A]", None, "{{1, 0}, {0, 1}}", None),
        ("A", None, "{{1 / Sqrt[b], 0}, {a / Sqrt[b], Sqrt[b]}}", None),
        # Transpose
        (
            "Transpose[x]",
            None,
            "Transpose[x]",
            None,
        ),
        # A matrix with a single row or column stays a matrix.
        (
            "Transpose[{{1, 2, 3}}]",
            None,
            "{{1}, {2}, {3}}",
            "Transpose of a single row turns into a single column",
        ),
        (
            "Transpose[{{1}, {2}, {3}}]",
            None,
            "{{1, 2, 3}}",
            "Transpose of a single column turns into a single row",
        ),
        (
            "Transpose[{{a}}]",
            None,
            "{{a}}",
            "Transpose of a single element",
        ),
        (
            "Transpose[Transpose[{{a, b}}]]",
            None,
            "{{a, b}}",
            None,
        ),
        (
            "Dimensions[Transpose[{{1, 2, 3}}]]",
            None,
            "{3, 1}",
            "Check the shape of a Transpose of a single row",
        ),
        # Elements are moved as they are, without a round trip through SymPy.
        (
            "Transpose[{{x + y, f[x]}, {1/2, Sin[x]}}]",
            None,
            "{{x + y, 1 / 2}, {f[x], Sin[x]}}",
            None,
        ),
        # Dimensions are those all elements share, even when the
        # elements disagree further down.
        (
            "Dimensions[{{a, b}, {{c, d}, {e, f}}}]",
            None,
            "{2, 2}",
            "Dimensions stops where element depths differ",
        ),
        (
            "Dimensions[{{{1, 2}, {3}}, {{4, 5}, {6, 7}}}]",
            None,
            "{2, 2}",
            "Dimensions stops where innermost lengths differ",
        ),
        (
            "Dimensions[{{a, b}, {b, c}, {c, d, e}}]",
            None,
            "{3}",
            "Dimensions of a ragged list is its length",
        ),
        (
            "ArrayDepth[{{a, b}, {{c, d}, {e, f}}}]",
            None,
            "2",
            "ArrayDepth is the length of the shared Dimensions",
        ),
        (
            "Transpose[{{a, b}, {{c, d}, {e, f}}}]",
            None,
            "{{a, {c, d}}, {b, {e, f}}}",
            "Transpose of a 2 x 2 array whose elements differ in depth",
        ),
    ],
)
def test_tensor(str_expr, msgs, str_expected, fail_msg):
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
