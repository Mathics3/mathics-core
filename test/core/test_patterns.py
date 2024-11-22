# -*- coding: utf-8 -*-
"""
Unit tests for mathics pattern matching
"""

import sys
import time
from test.helper import check_evaluation, evaluate

import pytest

@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        # Two default arguments (linear)
        ("MatchQ[1, a_.+b_.*x_]",None,"True",None),
        ("MatchQ[x, a_.+b_.*x_]",None,"True",None),
        ("MatchQ[2*x, a_.+b_.*x_]",None,"True",None),
        ("MatchQ[1+x, a_.+b_.*x_]",None,"True",None),
        ("MatchQ[1+2*x, a_.+b_.*x_]",None,"True",None),
        # Default argument (power)
        ("MatchQ[1, x_^m_.]",None,"True",None),
        ("MatchQ[x, x_^m_.]",None,"True",None),
        ("MatchQ[x^1, x_^m_.]",None,"True",None),
        ("MatchQ[x^2, x_^m_.]",None,"True",None),
        # Two default arguments (power)
        ("MatchQ[1, x_.^m_.]",None,"True",None),
        ("MatchQ[x, x_.^m_.]",None,"True",None),
        ("MatchQ[x^1, x_.^m_.]",None,"True",None),
        ("MatchQ[x^2, x_.^m_.]",None,"True",None),
        # Two default arguments (no non-head)
        ("MatchQ[1, a_.+b_.]",None,"True",None),
        ("MatchQ[x, a_.+b_.]",None,"True",None),
        ("MatchQ[1+x, a_.+b_.]",None,"True",None),
        ("MatchQ[1+2*x, a_.+b_.]",None,"True",None),
        ("MatchQ[1, a_.+b_.]",None,"True",None),
        ("MatchQ[x, a_.*b_.]",None,"True",None),
        ("MatchQ[2*x, a_.*b_.]",None,"True",None),
    ],
)
def test_patterns(str_expr, msgs, str_expected, fail_msg):
    """patterns"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
