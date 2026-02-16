# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.system.
"""


from test.helper import check_evaluation

import pytest

from mathics import settings


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "assert_tag_message"),
    [
        ('MemberQ[$Packages, "System`"]', "True", "$Packages"),
        pytest.param(
            "Head[$ParentProcessID] == Integer",
            "True",
            "$ParentProcessID",
            marks=pytest.mark.skipif(
                not settings.ENABLE_SYSTEM_COMMANDS,
                reason="In sandbox mode, $ParentProcessID returns $Failed",
            ),
        ),
        pytest.param(
            "Head[$ProcessID] == Integer",
            "True",
            "$ProcessID",
            marks=pytest.mark.skipif(
                not settings.ENABLE_SYSTEM_COMMANDS,
                reason="In sandbox mode, $ProcessID returns $Failed",
            ),
        ),
        ("Head[$SessionID] == Integer", "True", "$SessionID"),
        ("Head[$SystemWordLength] == Integer", "True", "$SystemWordLength"),
    ],
)
def test_private_doctests_system(str_expr, str_expected, assert_tag_message):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=assert_tag_message,
    )


@pytest.mark.skipif(
    settings.ENABLE_SYSTEM_COMMANDS,
    reason="These tests are used to a Sandboxed environment",
)
@pytest.mark.parametrize(
    "str_expr",
    [
        "$CommandLine",
        "$MachineName",
        "$ParentProcessID",
        "$ProcessID",
        "$ScriptCommandLine",
        "$SystemMemory",
        "$UserName",
        "Breakpoint[]",
        'Environment["HOME"]',
        'GetEnvironment["HOME"]',
        "MemoryAvailable[]",
        'Run["date"]',
        'SetEnvironment["FOO"->"bar"]',
    ],
)
def test_sandboxing_system_functions(str_expr):
    """ """
    check_evaluation(
        str_expr,
        str_expected="$Failed",
        expected_messages=["Execution of external commands is disabled."],
    )
