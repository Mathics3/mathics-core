# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.vectors.vector_space_operations.
"""

import sys
import time
from test.helper import check_evaluation, evaluate

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("Normalize[0]", None, "0", None),
        ("Normalize[{0}]", None, "{0}", None),
        ("Normalize[{}]", None, "{}", None),
        ("VectorAngle[{0, 1}, {0, 1}]", None, "0", None),
    ],
)
def test_private_doctests_vector_space_operations(
    str_expr, msgs, str_expected, fail_msg
):
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
