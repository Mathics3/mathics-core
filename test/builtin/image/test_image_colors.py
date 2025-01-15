# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.image.colors

Largely tests error messages when parameters are incorrect.
"""
from test.helper import check_evaluation, session

import pytest

img = session.evaluate('img = Import["ExampleData/hedy.tif"]')


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "assert_failure_msg"),
    [
        # FIXME: Setting "img" above in session sometimes fails. So do it again.
        ('img = Import["ExampleData/hedy.tif"];', "Null", ""),
        (
            """Binarize["a"]""",
            """Binarize[a]""",
            "imginv: Expecting an image instead of a.",
        ),
        (
            """Binarize[1, 3]""",
            """Binarize[1, 3]""",
            "imginv: Expecting an image instead of 1.",
        ),
        (
            """Binarize[img, I]""",
            """Binarize[-Image-, I]""",
            (
                "arg2: The argument I should be a real number or a pair of "
                "real numbers."
            ),
        ),
    ],
)
def test_binarize(str_expr, str_expected, assert_failure_msg):
    check_evaluation(
        str_expr, str_expected, hold_expected=True, failure_message=assert_failure_msg
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "assert_failure_msg"),
    [
        (
            """ColorQuantize[2, 0]""",
            """ColorQuantize[2, 0]""",
            "imginv: Expecting an image instead of 2.",
        ),
        (
            "ColorQuantize[img, I]",
            "ColorQuantize[-Image-, I]",
            (
                "intp: Positive integer expected at position 2 in "
                "ColorQuantize[-Image-, I]"
            ),
        ),
        (
            "ColorQuantize[img, -1]",
            "ColorQuantize[-Image-, -1]",
            (
                "intp: Positive integer expected at position 2 in "
                "ColorQuantize[-Image-, -1]"
            ),
        ),
    ],
)
def test_color_quantize(str_expr, str_expected, assert_failure_msg):
    check_evaluation(
        str_expr, str_expected, hold_expected=True, failure_message=assert_failure_msg
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "assert_failure_msg"),
    [
        (
            "ColorSeparate[1]",
            "ColorSeparate[1]",
            "imginv: Expecting an image instead of 1.",
        ),
    ],
)
def test_color_separate(str_expr, str_expected, assert_failure_msg):
    check_evaluation(
        str_expr, str_expected, hold_expected=True, failure_message=assert_failure_msg
    )
