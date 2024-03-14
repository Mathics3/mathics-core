# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtin.directories
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ('DirectoryName["a/b/c", 3] // InputForm', None, '""', None),
        ('DirectoryName[""] // InputForm', None, '""', None),
        (
            'DirectoryName["a/b/c", x]',
            (
                "Positive machine-sized integer expected at position 2 in DirectoryName[a/b/c, x].",
            ),
            "DirectoryName[a/b/c, x]",
            None,
        ),
        (
            'DirectoryName["a/b/c", -1]',
            (
                "Positive machine-sized integer expected at position 2 in DirectoryName[a/b/c, -1].",
            ),
            "DirectoryName[a/b/c, -1]",
            None,
        ),
        (
            "DirectoryName[x]",
            ("String expected at position 1 in DirectoryName[x].",),
            "DirectoryName[x]",
            None,
        ),
        ('DirectoryQ["ExampleData"]', None, "True", None),
        ('DirectoryQ["ExampleData/MythicalSubdir/NestedDir/"]', None, "False", None),
        ("FileNameDepth[x]", None, "FileNameDepth[x]", None),
        ("FileNameDepth[$RootDirectory]", None, "0", None),
        (
            'FileNameSplit["example/path", OperatingSystem -> x]',
            (
                'The value of option OperatingSystem -> x must be one of "MacOSX", "Windows", or "Unix".',
            ),
            "{example, path}",
            None,
        ),
    ],
)
def test_private_doctests_directory_names(str_expr, msgs, str_expected, fail_msg):
    """private doctests in builtin.directories"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
