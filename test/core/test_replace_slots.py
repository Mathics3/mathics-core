# -*- coding: utf-8 -*-
"""
Applying a pure function does not walk the parts of its body that have no
slot in them.
"""

from test.helper import check_evaluation, session

import pytest

from mathics.core.expression import Expression


def test_slot_free_part_is_not_walked(monkeypatch):
    big = session.evaluate("Table[{i, w -> i}, {i, 300}]")
    body = session.evaluate("Hold[{#1, Length[x]}]").elements[0]
    # The body {#1, Length[<big>]}, as when a list is passed to a function
    # and written into a pure function inside it.
    body = Expression(
        body.head, body.elements[0], Expression(body.elements[1].head, big)
    )
    calls = [0]
    original = Expression.replace_slots

    def counting(self, slots, evaluation):
        calls[0] += 1
        return original(self, slots, evaluation)

    monkeypatch.setattr(Expression, "replace_slots", counting)
    for i in range(5):
        new = body.replace_slots([None, session.evaluate(str(i))], session.evaluation)
        assert new.elements[1].elements[0] is big
    # Three calls per application (the body, #1 and Length[big]),
    # not one for each of the 900 subexpressions of big.
    assert calls[0] <= 5 * 4, f"{calls[0]} calls for 5 applications"


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        (
            "rsData = Range[5]; rsF[l_] := Map[{#, Length[l]} &, {a, b}]; rsF[rsData]",
            "{{a, 5}, {b, 5}}",
        ),
        ("Map[{#, {1, 2}} &, {a, b}]", "{{a, {1, 2}}, {b, {1, 2}}}"),
        ("Apply[{##, {x}} &, {a, b}]", "{a, b, {x}}"),
        ("Map[Function[{#, # &}], {1}]", "{{1, #1 &}}"),
        ("Map[{#, Hold[#]} &, {a}]", "{{a, Hold[a]}}"),
        ("ClearAll[rsData, rsF]", "Null"),
    ],
)
def test_pure_functions(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        # Slots in a compound head, at any depth.
        ("Map[#[0] &, {Sin, Cos}]", "{0, 1}"),
        ("Map[{a, {#[0]}} &, {Cos}]", "{{a, {1}}}"),
        ("Map[f[#][x] &, {1, 2}]", "{f[1][x], f[2][x]}"),
        ("Map[g[h[#]][x] &, {1}]", "{g[h[1]][x]}"),
        ("Apply[f[##][y] &, {1, 2}]", "f[1, 2][y]"),
    ],
)
def test_slots_in_compound_heads(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)
