# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.patterns.rules
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "expected_messages", "str_expected", "assert_message"),
    [
        (
            "ReplaceList[expr, {}, -1]",
            (
                "Non-negative integer or Infinity expected at position 3 in ReplaceList[expr, {}, -1]",
            ),
            "ReplaceList[expr, {}, -1]",
            None,
        ),
    ],
)
def test_associations(str_expr, expected_messages, str_expected, assert_message):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=assert_message,
        expected_messages=expected_messages,
    )


def test_compiled_rules_are_reused_and_renewed():
    """
    A list of rules kept in a variable is compiled once and reused by every
    replacement, and compiled again when a symbol of a rule changes (here: the
    attributes of its head).
    """
    from mathics.eval.rules import compiled_rewrite_rule
    from mathics.session import MathicsSession

    session = MathicsSession()
    session.evaluate("ClearAll[h]; rules = Join[{}, {h[x_Integer, 1] :> x}];")
    assert str(session.evaluate("h[1, 2] /. rules")) == "Global`h[1, 2]"

    def stored_rule():
        return (
            session.definitions.get_definition("Global`rules")
            .get_values_list("ownvalues")[0]
            .replace.elements[0]
        )

    evaluation = session.evaluation
    first = compiled_rewrite_rule(stored_rule(), evaluation)
    session.evaluate("h[1, 2] /. rules")
    assert compiled_rewrite_rule(stored_rule(), evaluation) is first

    session.evaluate("SetAttributes[h, Orderless]")
    # The kept rule was compiled before h became Orderless: it is not used again.
    assert compiled_rewrite_rule(stored_rule(), evaluation) is not first
    assert session.evaluate("h[1, 2] /. rules").value == 2
