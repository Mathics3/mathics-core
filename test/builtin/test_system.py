# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.system.
"""


from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "assert_tag_message"),
    [
        ('MemberQ[$Packages, "System`"]', "True", "$Packages"),
        ("Head[$ParentProcessID] == Integer", "True", "$ParentProcessID"),
        ("Head[$ProcessID] == Integer", "True", "$ProcessID"),
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
