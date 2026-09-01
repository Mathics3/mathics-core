# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.options.
"""

from test.helper import check_arg_counts, check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "assert_msg"),
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
        ("f /: Options[f] = {a -> b}", None, "{a ⇾ b}", None),
        ("Options[f]", None, "{a ⇾ b}", None),
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
        (
            "Options[Plot, Ticks]",
            None,
            "{Ticks ⇾ Automatic}",
            None,
        ),
        (
            'Options[Plot, "Ticks"]',
            None,
            "{Ticks ⇾ Automatic}",
            None,
        ),
        (
            "Options[AtomQ, Foo]",
            ["Option name Foo is not a known option for AtomQ."],
            "Options[AtomQ, Foo]",
            None,
        ),
        (
            'Options[AtomQ, "Foo"]',
            ["Option name Foo is not a known option for AtomQ."],
            "Options[AtomQ, Foo]",
            None,
        ),
    ],
)
def test_checkarguments(str_expr, msgs, str_expected, assert_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=assert_msg,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "assert_msg"),
    [
        (
            "CheckArguments[x[], 0]",
            None,
            "True",
            "CheckArguments with zero arguments",
        ),
        (
            "CheckArguments[x[], 1]",
            ("x called with 0 arguments; 1 argument is expected.",),
            "False",
            "CheckArguments mismatch with 0-argument call",
        ),
        (
            'CheckArguments[x[x], "foo"]',
            (
                "The range specification foo should have the form m, {m, n} or {m, Infinity}, where m and n are integers and 0 <= m <= n.",
            ),
            "CheckArguments[x[x], foo]",
            "CheckArguments called with an invalid string 2nd argument",
        ),
        (
            "Clear[g]; CheckArguments[g[1, a->5], 0]",
            ("g called with 2 arguments; 0 arguments are expected.",),
            "False",
            "CheckArguments with undeclared option parameter and mismatched count",
        ),
        (
            "Options[f] = {a -> 0}; CheckArguments[f[1, a->5], 0]",
            (
                "Options expected (instead of 1) beyond position 0 in f[1, a ⇾ 5]. An option must be a rule or a list of rules.",
            ),
            "False",
            "CheckArguments with declared option parameter and mismatched count",
        ),
    ],
)
def test_options(str_expr, msgs, str_expected, assert_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=assert_msg,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "CheckArguments",
            "2 or 3 arguments are",
        ),
    ],
)
def test_arg_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)
