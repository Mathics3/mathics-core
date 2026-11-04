# -*- coding: utf-8 -*-
"""
A list that has been evaluated, and whose symbols have not changed since,
is not evaluated element by element again.
"""

import pytest

from mathics.core import list as mlist
from test.helper import check_evaluation, session


def test_evaluated_list_is_not_walked_again(monkeypatch):
    session.evaluate(
        "ClearAll[lvV]; lvV = Table[{i, lvW -> i}, {i, 200}];"
    )
    calls = [0]
    original = mlist.ListExpression.evaluate_elements

    def counting(self, evaluation):
        if len(self.elements) >= 200:
            calls[0] += 1
        return original(self, evaluation)

    monkeypatch.setattr(mlist.ListExpression, "evaluate_elements", counting)
    session.evaluate("Do[lvV[[1]], {20}]")
    session.evaluate("ClearAll[lvV]")
    # Its elements hold rules, so the list is not literal; still, twenty
    # reads must not go over its 200 elements twenty times.
    assert calls[0] <= 2, f"{calls[0]} walks over the list for 20 reads"


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        # A symbol in the list changes after it was evaluated.
        ("ClearAll[lvX, lvV]; lvV = {lvX, a -> lvX}; lvV", "{lvX, a -> lvX}", None),
        ("lvX = 1; lvV", "{1, a -> 1}", "The list is evaluated again"),
        ("lvX = 2; lvV", "{2, a -> 2}", "and again"),
        # A part assigned a symbol that gets a value later.
        (
            "ClearAll[lvY]; lvV = {u, b -> 1}; lvV; lvV[[2]] = b -> lvY; lvY = 3; lvV",
            "{u, b -> 3}",
            None,
        ),
        # A Block that changes a symbol of the list.
        ("ClearAll[lvZ]; lvV = {lvZ, c -> lvZ}; lvV; Block[{lvZ = 7}, lvV]", "{7, c -> 7}", None),
        ("lvV", "{lvZ, c -> lvZ}", "and the list as it was after the Block"),
        ("ClearAll[lvX, lvY, lvZ, lvV]", "Null", None),
    ],
)
def test_evaluated_list_follows_changes(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)
