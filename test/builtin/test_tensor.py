# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.tensor.
"""

import sys
import time
from test.helper import check_evaluation, evaluate

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("Dimensions[{}]", None, "{0}", None),
        ("Dimensions[{{}}]", None, "{1, 0}", None),
        ## Issue #670
        (
            "A = {{ b ^ ( -1 / 2), 0}, {a * b ^ ( -1 / 2 ), b ^ ( 1 / 2 )}}",
            None,
            "{{1 / Sqrt[b], 0}, {a / Sqrt[b], Sqrt[b]}}",
            None,
        ),
        ("A . Inverse[A]", None, "{{1, 0}, {0, 1}}", None),
        ("A", None, "{{1 / Sqrt[b], 0}, {a / Sqrt[b], Sqrt[b]}}", None),
        # Transpose
        ("Transpose[x]", None, "Transpose[x]", None),
    ],
)
def test_private_doctests_tensor(str_expr, msgs, str_expected, fail_msg):
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
