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


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "CompositeQ",
            "1 argument is",
        ),
        (
            "Divisible",
            "2 or more arguments are",
        ),
        (
            "LCM",
            "1 or more arguments are",
        ),
        (
            "ModularInverse",
            "2 arguments are",
        ),
        (
            "PowerMod",
            "3 arguments are",
        ),
        (
            "Quotient",
            "2 or 3 arguments are",
        ),
    ],
)
def test_divlike_arg_errors(function_name, msg_fragment):
    """ """

    str_expr = f"{function_name}[]"
    expected_msgs = [
        f"{function_name} called with 0 arguments; {msg_fragment} expected."
    ]
    failure_message = f"{function_name} argument number error"
    check_evaluation(
        str_expr,
        str_expr,
        failure_message=failure_message,
        expected_messages=expected_msgs,
    )
