# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.physchemdata
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            'Outer[ElementData, Range[118], ElementData["Properties"]];',
            None,
            "Null",
            "Ensure all data parses #664",
        ),
    ],
)
def test_private_doctests_physchemdata(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=False,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
