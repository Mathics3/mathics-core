# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.string.
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ('ToCharacterCode[{"ab"}]', None, "{{97, 98}}", None),
        (r'ToCharacterCode[{"\(A\)"}]', None, "{{63433, 65, 63424}}", None),
        (
            'ToCharacterCode[{{"ab"}}]',
            (
                "String or list of strings expected at position 1 in ToCharacterCode[{{ab}}].",
            ),
            "ToCharacterCode[{{ab}}]",
            None,
        ),
        (
            "ToCharacterCode[x]",
            (
                "String or list of strings expected at position 1 in ToCharacterCode[x].",
            ),
            "ToCharacterCode[x]",
            None,
        ),
        ('ToCharacterCode[""]', None, "{}", None),
        (
            "#1 == ToCharacterCode[FromCharacterCode[#1]] & [RandomInteger[{0, 65535}, 100]]",
            None,
            "True",
            None,
        ),
        (
            r"ToCharacterCode[]",
            ["ToCharacterCode called with 0 arguments; 1 or 2 arguments are expected."],
            "ToCharacterCode[]",
            "ToCharacterCode argument checking",
        ),
    ],
)
def test_to_character_code(str_expr, msgs, str_expected, fail_msg):
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
        ("FromCharacterCode[{}] // InputForm", None, '""', None),
        (
            "FromCharacterCode[65536]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 1 in {65536}.",
            ),
            "FromCharacterCode[65536]",
            None,
        ),
        (
            "FromCharacterCode[-1]",
            (
                "Non-negative machine-sized integer expected at position 1 in FromCharacterCode[-1].",
            ),
            "FromCharacterCode[-1]",
            None,
        ),
        (
            "FromCharacterCode[444444444444444444444444444444444444]",
            (
                "Non-negative machine-sized integer expected at position 1 in FromCharacterCode[444444444444444444444444444444444444].",
            ),
            "FromCharacterCode[444444444444444444444444444444444444]",
            None,
        ),
        (
            "FromCharacterCode[{100, 101, -1}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, -1}.",
            ),
            "FromCharacterCode[{100, 101, -1}]",
            None,
        ),
        (
            "FromCharacterCode[{100, 101, 65536}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, 65536}.",
            ),
            "FromCharacterCode[{100, 101, 65536}]",
            None,
        ),
        (
            "FromCharacterCode[{100, 101, x}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, x}.",
            ),
            "FromCharacterCode[{100, 101, x}]",
            None,
        ),
        (
            "FromCharacterCode[{100, {101}}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 2 in {100, {101}}.",
            ),
            "FromCharacterCode[{100, {101}}]",
            None,
        ),
        (
            "FromCharacterCode[{{97, 98, 99}, {100, 101, x}}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {100, 101, x}.",
            ),
            "FromCharacterCode[{{97, 98, 99}, {100, 101, x}}]",
            None,
        ),
        (
            "FromCharacterCode[{{97, 98, x}, {100, 101, x}}]",
            (
                "A character code, which should be a non-negative integer less than 65536, is expected at position 3 in {97, 98, x}.",
            ),
            "FromCharacterCode[{{97, 98, x}, {100, 101, x}}]",
            None,
        ),
    ],
)
def test_from_character_code(str_expr, msgs, str_expected, fail_msg):
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
