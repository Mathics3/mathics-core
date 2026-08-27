"""
Test Built-in function in mathics.builtin.string.operations
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ('StringTake["abcd", 0] // InputForm', None, '""', None),
        ('StringTake["abcd", {3, 2}] // InputForm', None, '""', None),
        ('StringTake["", {1, 0}] // InputForm', None, '""', None),
        (
            'StringTake["abc", {0, 0}]',
            ('Cannot take positions 0 through 0 in "abc".',),
            "StringTake[abc, {0, 0}]",
            None,
        ),
        (
            r'StringTake["\!A",{2}]',
            None,
            "A",
            r"Escaped character \! should be treated like a single character",
        ),
        (
            "StringTake[{2, 4},2]",
            ("String or list of strings expected at position 1.",),
            "StringTake[{2, 4}, 2]",
            None,
        ),
        (
            'StringTake["kkkl",Graphics[{}]]',
            ("Integer or a list of sequence specifications expected at position 2.",),
            "StringTake[kkkl, -Graphics-]",
            None,
        ),
        (
            r"StringTake[]",
            ["StringTake called with 0 arguments; 2 arguments are expected."],
            "StringTake[]",
            "StringTake argument checking",
        ),
    ],
)
def test_string_take(str_expr, msgs, str_expected, fail_msg):
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
