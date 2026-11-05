"""
Integer Plus and Times are computed as Python integers, not through SymPy.
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("10^30 + 1 - 10^30", "1"),
        ("(-3) * 4 * 5", "-60"),
        ("2^40 * 2^40", "1208925819614629174706176"),
        ("1 + 2 + 3 + 4", "10"),
        ("Plus[5]", "5"),
        ("Times[7, 0]", "0"),
        # Other numbers still take the general path.
        ("1 + 1/2", "3/2"),
        ("2 * 1.5", "3."),
        ("0 * x", "0"),
        ("3 * I", "3 I"),
    ],
)
def test_integer_arithmetic(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)
