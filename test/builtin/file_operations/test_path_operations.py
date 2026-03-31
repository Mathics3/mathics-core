# -*- coding: utf-8 -*-
"""
Unit tests from builtins/files_io/files.py
"""
from test.helper import check_evaluation, evaluate_value

import pytest

abc = evaluate_value('FileNameJoin[{"a", "b", "c"}]')
abcd = evaluate_value('FileNameJoin[{"a", "b", "c", "d"}]')


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        # One arg nonnegative tests
        (
            f'FileNameDrop["{abc}", 0]',
            None,
            f'"{abc}"',
            "",
        ),
        (
            f'FileNameDrop["{abc}", 1]',
            None,
            'FileNameJoin[{"b", "c"}]',
            "",
        ),
        (
            f'FileNameDrop["{abc}", 2]',
            None,
            '"c"',
            None,
        ),
        (
            f'FileNameDrop["{abc}", 3]',
            None,
            '""',
            None,
        ),
        (
            f'FileNameDrop["{abc}", 4]',
            None,
            '""',
            None,
        ),
        # One arg negative tests
        (
            f'FileNameDrop["{abc}", -1]',
            None,
            'FileNameJoin[{"a","b"}]',
            "",
        ),
        (
            f'FileNameDrop["{abc}", -2]',
            None,
            '"a"',
            None,
        ),
        (
            f'FileNameDrop["{abc}", -3]',
            None,
            '""',
            None,
        ),
        (
            f'FileNameDrop["{abc}", -4]',
            None,
            '""',
            None,
        ),
        # Two integer arg tests with positive bounds
        (
            f'FileNameDrop["{abc}", ' + "{3, 0}]",
            None,
            f'"{abc}"',
            None,
        ),
        (
            f'FileNameDrop["{abc}", ' + "{4, 0}]",
            None,
            f'"{abc}"',
            None,
        ),
        (
            f'FileNameDrop["{abc}", ' + "{3, 3}]",
            None,
            'FileNameJoin[{"a","b"}]',
            None,
        ),
        (
            f'FileNameDrop["{abcd}", ' + "{1, 3}]",
            None,
            'FileNameJoin[{"d"}]',
            None,
        ),
        (
            f'FileNameDrop["{abcd}", ' + "{2, 3}]",
            None,
            'FileNameJoin[{"a","d"}]',
            None,
        ),
        (
            f'FileNameDrop["{abcd}", ' + "{1, 3}]",
            None,
            '"d"',
            None,
        ),
        (
            f'FileNameDrop["{abcd}", ' + "{1, 4}]",
            None,
            '""',
            None,
        ),
        # m_pos > n_pos
        (
            f'FileNameDrop["{abcd}", ' + "{3, 2}]",
            None,
            f'"{abcd}"',
            None,
        ),
        (
            f'FileNameDrop["{abcd}", ' + "{4, 1}]",
            None,
            f'"{abcd}"',
            None,
        ),
        # Two integer arg tests with negative bounds: n < m
        (
            f'FileNameDrop["{abcd}", ' + "{-2, -3}]",
            None,
            f'"{abcd}"',
            None,
        ),
        (
            f'FileNameDrop["{abcd}", ' + "{-3, -2}]",
            None,
            'FileNameJoin[{"a","d"}]',
            None,
        ),
        (
            f'FileNameDrop["{abcd}", ' + "{-2, -2}]",
            None,
            'FileNameJoin[{"a", "b", "d"}]',
            None,
        ),
    ],
)
def test_FileNameDrop(str_expr, msgs, str_expected, fail_msg):
    """test FileNameDrop built-in function"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=False,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
