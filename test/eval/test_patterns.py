# -*- coding: utf-8 -*-
"""
Unit tests for mathics.eval.patterns
"""

from test.helper import session

import pytest

from mathics.core.definitions import Definitions
from mathics.core.parser import MathicsSingleLineFeeder, parse
from mathics.core.pattern import ExpressionPattern
from mathics.eval.patterns import Matcher

# Preload the Mathics definitions
defintions = Definitions(True)


def check_pattern(str_expr, str_pattern):
    expr = parse(defintions, MathicsSingleLineFeeder(str_expr))
    pattern = ExpressionPattern(parse(defintions, MathicsSingleLineFeeder(str_pattern)))
    ret = Matcher(pattern, session.evaluation).match(expr, session.evaluation)
    assert ret is True


@pytest.mark.parametrize(
    ("str_expr", "str_pattern"),
    [
        # Two default arguments (linear)
        ("1", "a_.+b_.*x_"),
        ("x", "a_.+b_.*x_"),
        ("2*x", "a_.+b_.*x_"),
        ("1+x", "a_.+b_.*x_"),
        ("1+2*x", "a_.+b_.*x_"),
        # Default argument (power)
        ("1", "x_^m_."),
        ("x", "x_^m_."),
        ("x^1", "x_^m_."),
        ("x^2", "x_^m_."),
        # Two default arguments (power)
        ("1", "x_.^m_."),
        ("x", "x_.^m_."),
        ("x^1", "x_.^m_."),
        ("x^2", "x_.^m_."),
        # Two default arguments (no non-head)
        ("1", "a_.+b_."),
        ("x", "a_.+b_."),
        ("1+x", "a_.+b_."),
        ("1+2*x", "a_.+b_."),
        ("1", "a_.*b_."),
        ("x", "a_.*b_."),
        ("2*x", "a_.*b_."),
    ],
)
def test_eval_patterns(str_expr, str_pattern):
    """eval_patterns"""
    check_pattern(str_expr, str_pattern)
