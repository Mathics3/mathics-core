# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtins.atomic.strings.

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
