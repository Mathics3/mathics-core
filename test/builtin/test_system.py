# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.system.
"""


from test.helper import check_evaluation, session

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ('MemberQ[$Packages, "System`"]', "True"),
        ("Head[$ParentProcessID] == Integer", "True"),
        ("Head[$ProcessID] == Integer", "True"),
        ("Head[$SystemWordLength] == Integer", "True"),
    ],
)
def test_private_doctests_system(str_expr, str_expected):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
    )
