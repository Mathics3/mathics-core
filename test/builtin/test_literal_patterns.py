# -*- coding: utf-8 -*-
"""
A literal pattern, such as 1 or {1, 2}, matches exactly the expressions
that are SameQ to it; Position and the other functions that use a Matcher
check it that way, without the pattern matcher.
"""

import pytest

from mathics.eval.patterns import Matcher
from mathics.eval.parts import walk_levels
from test.helper import check_evaluation, session


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("Position[{1, 1., {1}, 2}, 1]", "{{1}, {3, 1}}"),
        ("Position[{{1, 2}, {1, 2.}, {2, 1}, f[{1, 2}]}, {1, 2}]", "{{1}, {4, 1}}"),
        ('Position[{"a", a, {"a"}}, "a"]', "{{1}, {3, 1}}"),
        ("Position[{1/2, 0.5, 1/2}, 1/2]", "{{1}, {3}}"),
        ("Position[{1, 2, 1}, 1, {1}]", "{{1}, {3}}"),
        ("Position[{{1}, 1}, {1}, Heads -> True]", "{{1}}"),
        ("Cases[{1, 1., 2, {1}}, 1]", "{1}"),
        ("Count[{{1, 2}, {1, 2}, {2, 1}}, {1, 2}]", "2"),
        ("MatchQ[{1, 2}, {1, 2}]", "True"),
        ("MatchQ[{1, 2.}, {1, 2}]", "False"),
        # Patterns that are not literal still go through the matcher.
        ("Position[{1, 2, {3}}, _Integer]", "{{1}, {2}, {3, 1}}"),
        ("Position[{{1, 2}, {2, 1}}, {_, 1}]", "{{2}}"),
    ],
)
def test_literal_patterns(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)


def test_literal_matcher_uses_sameq():
    pattern = session.evaluate("{1, 2}")
    matcher = Matcher(pattern, session.evaluation)
    assert matcher.literal is pattern
    assert matcher.match(session.evaluate("{1, 2}"), session.evaluation)
    assert not matcher.match(session.evaluate("{1, 2.}"), session.evaluation)
    assert Matcher(session.evaluate("_Integer"), session.evaluation).literal is None


def test_walk_levels_keeps_unchanged_expression():
    expr = session.evaluate("Table[{i, {i, i + 1}}, {i, 50}]")
    new, depth = walk_levels(expr, 0, None, callback=lambda level: level)
    assert new is expr
    assert depth == 3
    # A callback that changes a level still gives a new expression.
    changed, _ = walk_levels(
        expr, 1, 1, callback=lambda level: session.evaluate("x") if level is expr.elements[0] else level
    )
    assert changed is not expr and str(changed.elements[0]) == "Global`x"
