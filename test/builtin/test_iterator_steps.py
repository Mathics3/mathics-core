"""
Iterators with exact bounds count their steps in Python, and exact numbers
are compared without SymPy. The results must stay those of WMA.
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("Table[k, {k, 1, 10, 3}]", "{1, 4, 7, 10}"),
        ("Table[k, {k, 10, 1, -3}]", "{10, 7, 4, 1}"),
        # The number of steps is a Rational: its integer part is taken.
        ("Table[k, {k, 1, 7/2}]", "{1, 2, 3}"),
        ("Table[k, {k, 0, 5, 2}]", "{0, 2, 4}"),
        ("Table[k, {k, 3, 1}]", "{}"),
        ("Table[k, {k, -2, 2}]", "{-2, -1, 0, 1, 2}"),
        # Bounds and steps that are not integers take the general path.
        ("Table[k, {k, 1/2, 3}]", "{1/2, 3/2, 5/2}"),
        ("Table[k, {k, 1, 2, 1/3}]", "{1, 4/3, 5/3, 2}"),
        ("Table[k, {k, 1, 2.5}]", "{1, 2}"),
        ("Sum[k, {k, 1, 100}]", "5050"),
        ("Product[k, {k, 1, 10, 2}]", "945"),
        ("iterStepsX = 0; Do[iterStepsX += k, {k, 5, 1, -2}]; iterStepsX", "9"),
        ("Table[If[k < 5/2, k, 0], {k, 4}]", "{1, 2, 0, 0}"),
    ],
)
def test_exact_iterators(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("1 < 3/2", "True"),
        ("3/2 < 1", "False"),
        ("1/2 == 2/4", "True"),
        ("1 <= 1", "True"),
        ("2 > 7/3", "False"),
        ("-5 >= -5", "True"),
        ("1 < 2 < 3/2", "False"),
        ("{Max[1, 3/2, -2], Min[1, 3/2, -2]}", "{3/2, -2}"),
        ("10^30 + 1 > 10^30", "True"),
    ],
)
def test_exact_comparisons(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)
