# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.atomic.strings.

In particular, Alphabet
"""
from test.helper import check_evaluation
import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg", "warnings"),
    [
        (
            'Complement[Alphabet["Swedish"], Alphabet["English"]]',
            r'{"à", "ä", "å", "é", "ö"}',
            "Alphabet test",
            tuple(),
        ),
        (
            'Alphabet["Elvish45"]',
            'Alphabet["Elvish45"]',
            "Alphabet for a made-up language",
            ("The alphabet Elvish45 is not known or not available.",),
        ),
    ],
)
def test_alphabet(str_expr, str_expected, fail_msg, warnings):
    check_evaluation(
        str_expr, str_expected, failure_message="", expected_messages=warnings
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg", "warnings"),
    [
        (r'ToString["\[Integral]", CharacterEncoding->"Unicode"]', r'"∫"', None, None),
        (
            r'ToString["\[Integral]", CharacterEncoding->"ASCII"]',
            # FIXME:
            # "\\[Integral]" is parsed as "\u222b" instead of "\[Integral]"
            r'"\\[Inte" <> "gral]"',
            None,
            None,
        ),
        (
            r'ToString["\[Integral]", CharacterEncoding->"No"]',
            r'"∫"',
            None,
            [
                "The character encoding No is not supported. Use $CharacterEncodings to list supported encodings."
            ],
        ),
        (
            r'ToString["\[Integral]", CharacterEncoding->"3"]',
            r'"∫"',
            None,
            [
                "The character encoding 3 is not supported. Use $CharacterEncodings to list supported encodings."
            ],
        ),
        (
            r'ToString["\[Integral]", TeXForm]',
            r'"\\text{∫}"',  # Should be '\\int'
            None,
            None,
        ),
    ],
)
def test_tostring(str_expr, str_expected, fail_msg, warnings):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message="",
        expected_messages=warnings,
        to_string_expr=False,
        to_string_expected=False,
    )
