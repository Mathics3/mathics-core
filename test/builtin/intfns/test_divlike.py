# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.intfns.divlike
"""

from test.helper import check_evaluation

import pytest


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
def test_divlike(str_expr, msgs, str_expected, fail_msg):
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
