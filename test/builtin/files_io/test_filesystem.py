# -*- coding: utf-8 -*-
"""
Unit tests from builtins/files_io/filesystem.py
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            'AbsoluteFileName["Some/NonExistant/Path.ext"]',
            ("File not found during AbsoluteFileName[Some/NonExistant/Path.ext].",),
            "$Failed",
            None,
        ),
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
        ('FileBaseName["file."]', None, "file", None),
        ('FileBaseName["file"]', None, "file", None),
        ('FileExtension["file."]', None, "", None),
        ('FileExtension["file"]', None, "", None),
        ('FileInformation["ExampleData/missing_file.jpg"]', None, "{}", None),
        ('FindFile["SomeTypoPackage`"]', None, "$Failed", None),
        (
            'SetDirectory["MathicsNonExample"]',
            ("Cannot set current directory to MathicsNonExample.",),
            "$Failed",
            None,
        ),
        (
            'Needs["SomeFakePackageOrTypo`"]',
            (
                "Cannot open SomeFakePackageOrTypo`.",
                "Context SomeFakePackageOrTypo` was not created when Needs was evaluated.",
            ),
            "$Failed",
            None,
        ),
        (
            'Needs["VectorAnalysis"]',
            (
                "Invalid context specified at position 1 in Needs[VectorAnalysis]. A context must consist of valid symbol names separated by and ending with `.",
            ),
            "Needs[VectorAnalysis]",
            None,
        ),
    ],
)
def test_private_doctests_filesystem(str_expr, msgs, str_expected, fail_msg):
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
