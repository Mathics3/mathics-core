# -*- coding: utf-8 -*-
"""
Unit tests for mathics.core.pattern
"""

import sys
import time
from test.helper import check_evaluation, evaluate

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        # Two default arguments (linear)
        ("MatchQ[1, a_.+b_.*x_]", None, "True", None),
        ("MatchQ[x, a_.+b_.*x_]", None, "True", None),
        ("MatchQ[2*x, a_.+b_.*x_]", None, "True", None),
        ("MatchQ[1+x, a_.+b_.*x_]", None, "True", None),
        ("MatchQ[1+2*x, a_.+b_.*x_]", None, "True", None),
        # Default argument (power)
        ("MatchQ[1, x_^m_.]", None, "True", None),
        ("MatchQ[x, x_^m_.]", None, "True", None),
        ("MatchQ[x^1, x_^m_.]", None, "True", None),
        ("MatchQ[x^2, x_^m_.]", None, "True", None),
        # Two default arguments (power)
        ("MatchQ[1, x_.^m_.]", None, "True", None),
        ("MatchQ[x, x_.^m_.]", None, "True", None),
        ("MatchQ[x^1, x_.^m_.]", None, "True", None),
        ("MatchQ[x^2, x_.^m_.]", None, "True", None),
        # Two default arguments (no non-head)
        ("MatchQ[1, a_.+b_.]", None, "True", None),
        ("MatchQ[x, a_.+b_.]", None, "True", None),
        ("MatchQ[1+x, a_.+b_.]", None, "True", None),
        ("MatchQ[1+2*x, a_.+b_.]", None, "True", None),
        ("MatchQ[1, a_.*b_.]", None, "True", None),
        ("MatchQ[x, a_.*b_.]", None, "True", None),
        ("MatchQ[2*x, a_.*b_.]", None, "True", None),
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


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        # Two default arguments (linear)
        ("rule=A[a_.+B[b_.*x_]]->{a,b,x};", None, "Null", None),
        ("A[B[1]] /. rule", None, "{0, 1, 1}", None),
        ("A[B[x]] /. rule", None, "{0, 1, x}", None),
        ("A[B[2*x]] /. rule", None, "{0, x, 2}", None),
        ("A[1+B[x]] /. rule", None, "{1, 1, x}", None),
        ("A[1+B[2*x]] /. rule", None, "{1, x, 2}", None),
        # Default argument (power)
        ("rule=A[x_^n_.]->{x,n};", None, "Null", None),
        ("A[1] /. rule", None, "{1, 1}", None),
        ("A[x] /. rule", None, "{x, 1}", None),
        ("A[x^1] /. rule", None, "{x, 1}", None),
        ("A[x^2] /. rule", None, "{x, 2}", None),
        # Two default arguments (power)
        ("rule=A[x_.^n_.]->{x,n};", None, "Null", None),
        ("A[] /. rule", None, "A[]", None),
        ("A[1] /. rule", None, "{1, 1}", None),
        ("A[x] /. rule", None, "{x, 1}", None),
        ("A[x^1] /. rule", None, "{x, 1}", None),
        ("A[x^2] /. rule", None, "{x, 2}", None),
        # Two default arguments (no non-head)
        ("rule=A[a_. + B[b_.*x_.]]->{a,b,x};", None, "Null", None),
        ("A[B[]] /. rule", None, "A[B[]]", None),
        ("A[B[1]] /. rule", None, "{0, 1, 1}", None),
        ("A[B[x]] /. rule", None, "{0, 1, x}", None),
        ("A[1 + B[x]] /. rule", None, "{1, 1, x}", None),
        ("A[1 + B[2*x]] /. rule", None, "{1, 2, x}", None),
    ],
)
def test_pattern_substitutions(str_expr, msgs, str_expected, fail_msg):
    """pattern_substitutions"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
