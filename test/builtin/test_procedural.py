# -*- coding: utf-8 -*-
import pytest
from test.helper import check_evaluation, session

# NestWhile tests
@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("NestWhile[#/2&, 10000, IntegerQ]", "625/2"),
        ("NestWhile[Total[IntegerDigits[#]^3] &, 5, UnsameQ, All]", "371"),
        ("NestWhile[Total[IntegerDigits[#]^3] &, 6, UnsameQ, All]", "153"),
    ],
)
def test_nestwhile(str_expr, str_expected):
    print(str_expr)
    print(session.evaluate(str_expr))
    check_evaluation(
        str_expr, str_expected, to_string_expr=True, to_string_expected=True
    )
