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


lisp1_path = f"{data_dir}/lisp1.m"
invalid_path = f"{data_dir}/file-should-not-appear"


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            f'Read["{lisp1_path}", Junk]',
            ["Junk is not a valid format specification."],
            f'Read["{lisp1_path}", Junk]',
            "Read invalid format specification",
        ),
        (
            f'Read["{invalid_path}"]',
            [f"Cannot open {invalid_path}."],
            "$Failed",
            "Read[] with missing path",
        ),
        (
            f'Read["{lisp1_path}"]',
            [f"Invalid input found when reading '(1) from {lisp1_path}."],
            "$Failed",
            "Read[] with unparsable default data",
        ),
    ],
)
def test_read(str_expr, msgs, str_expected, fail_msg):
    """Read[] tests."""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=False,
        to_string_expected=False,
        hold_expected=False,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
