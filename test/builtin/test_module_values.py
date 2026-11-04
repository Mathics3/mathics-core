# -*- coding: utf-8 -*-
"""
Module shares the initial values of its variables with the expressions
they come from; changing a variable never changes the value it started
from.
"""

import pytest

from test.helper import check_evaluation, session


def test_initial_value_is_not_copied():
    session.evaluate("ClearAll[mvA, mvGet, mvS]; mvA = Table[{i, 1}, {i, 100}];")
    stored = (
        session.definitions.get_definition("Global`mvA")
        .get_values_list("ownvalues")[0]
        .replace
    )
    session.evaluate("mvGet[] := Module[{s = mvA}, mvS = Hold[s]; s]; mvGet[];")
    name = session.evaluate("mvS").elements[0].get_name()
    value = (
        session.definitions.get_definition(name).get_values_list("ownvalues")[0].replace
    )
    # Reading mvA gives a shallow copy; its elements are those of the
    # stored value, not copies of them.
    assert all(new is old for new, old in zip(value.elements, stored.elements))
    session.evaluate("ClearAll[mvA, mvGet, mvS]")


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("mvA = {1, {2, 3}}; Module[{s = mvA}, s[[2, 1]] = x; {s, mvA}]", "{{1, {x, 3}}, {1, {2, 3}}}"),
        ("Module[{s = mvA}, s[[1]] = y; s]; mvA", "{1, {2, 3}}"),
        ("Module[{s = mvA}, AppendTo[s, 4]; {s, mvA}]", "{{1, {2, 3}, 4}, {1, {2, 3}}}"),
        ("Module[{s = mvA}, s[[2]] = Append[s[[2]], 9]; {s, mvA}]", "{{1, {2, 3, 9}}, {1, {2, 3}}}"),
        # Two variables starting from the same value.
        ("Module[{s = mvA, t = mvA}, s[[1]] = 5; {s, t}]", "{{5, {2, 3}}, {1, {2, 3}}}"),
        # A recursive function whose Module variable starts from its argument.
        (
            "mvU[l_, 0] := l; mvU[l_, n_] := Module[{set = l}, set[[n]] = -set[[n]]; mvU[set, n - 1]];"
            " {mvU[{1, 2, 3}, 3], mvA}",
            "{{-1, -2, -3}, {1, {2, 3}}}",
        ),
        ("ClearAll[mvA, mvU]", "Null"),
    ],
)
def test_changing_a_variable_keeps_its_initial_value(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)
