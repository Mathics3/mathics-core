# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.options.
"""


from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            (
                'f[x_, OptionsPattern[f]] := x ^ OptionValue["m"];'
                'Options[f] = {"m" -> 7};f[x]'
            ),
            None,
            "x ^ 7",
            None,
        ),
        ("f /: Options[f] = {a -> b}", None, "{a -> b}", None),
        ("Options[f]", None, "{a :> b}", None),
        (
            "f /: Options[g] := {a -> b}",
            ("Rule for Options can only be attached to g.",),
            "$Failed",
            None,
        ),
        (
            "Options[f] = a /; True",
            ("a /; True is not a valid list of option rules.",),
            "a /; True",
            None,
        ),
    ],
)
def test_private_doctests_options(str_expr, msgs, str_expected, fail_msg):
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
