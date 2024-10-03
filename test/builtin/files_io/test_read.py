# -*- coding: utf-8 -*-
"""
Unit tests from builtins/files_io/files.py
"""
from test.helper import check_evaluation, data_dir

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            f'ReadList["{data_dir}/lisp1.m", '
            """Word, TokenWords->{"(", ")", "[", "]", "'"}]""",
            None,
            "{', (, 1, )}",
            None,
        ),
        (
            r'stream = StringToStream["\"abc123\""];ReadList[stream, "Invalid"]//{#1[[0]],#1[[2]]}&',
            ("Invalid is not a valid format specification.",),
            "{ReadList, Invalid}",
            "",
        ),
    ],
)
def test_read_list(str_expr, msgs, str_expected, fail_msg):
    """ReadList[] tests."""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
