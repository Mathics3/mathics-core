# -*- coding: utf-8 -*-
"""
Stored values such as f[1] = a are found through an index
(LiteralRuleIndex), which needs the sort keys of the rules to hash.
"""

from mathics.core.expression import Expression
from mathics.core.keycomparable import Monomial
from test.helper import check_evaluation, session


def test_monomials_hash_like_they_compare():
    assert hash(Monomial({"a": 1, "b": 2})) == hash(Monomial({"b": 2, "a": 1}))
    assert Monomial({"a": 1}) == Monomial({"a": 1.0})
    assert hash(Monomial({"a": 1})) == hash(Monomial({"a": 1.0}))
    assert len({Monomial({"a": 1}), Monomial({"a": 1}), Monomial({"a": 2})}) == 2


def test_stored_values_are_found_through_the_index(monkeypatch):
    session.evaluate("ClearAll[lriF]; Do[lriF[{i, i + 1}] = i, {i, 400}]; lriF[x_] := lin[x];")
    definition = session.definitions.get_definition("Global`lriF")
    values = definition.get_values_list("downvalues")
    assert definition._get_literal_index("downvalues", values) is not None

    calls = [0]
    original = Expression.sameQ

    def counting(self, other):
        calls[0] += 1
        return original(self, other)

    monkeypatch.setattr(Expression, "sameQ", counting)
    session.evaluate("Do[lriF[{i, i + 1}], {i, 300, 400}]")
    monkeypatch.undo()
    # A few comparisons per lookup, not one per stored value before it.
    assert calls[0] < 10 * 101, f"{calls[0]} SameQ for 101 lookups"

    check_evaluation("{lriF[{3, 4}], lriF[{400, 401}], lriF[{401, 402}]}", "{3, 400, lin[{401, 402}]}")
    session.evaluate("ClearAll[lriF]")
