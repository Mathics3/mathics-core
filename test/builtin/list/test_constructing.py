# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.list.constructing
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "failure_message"),
    [
        (
            "Table[x, {x,0,1/3}]",
            "{0}",
            None,
        ),
        (
            "Table[x, {x, -0.2, 3.9}]",
            "{-0.2, 0.8, 1.8, 2.8, 3.8}",
            None,
        ),
    ],
)
def test_array(str_expr, str_expected, failure_message):
    check_evaluation(str_expr, str_expected, failure_message)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "failure_message"),
    [
        (
            "Array[f, {2, 3}, {1, 2, 3}]",
            "Array[f, {2, 3}, {1, 2, 3}]",
            "plen: {2, 3} and {1, 2, 3} should have the same length.",
        ),
        (
            "Array[f, a]",
            "Array[f, a]",
            "ilsnn: Single or list of non-negative integers expected at position 2.",
        ),
        (
            "Array[f, 2, b]",
            "Array[f, 2, b]",
            "ilsnn: Single or list of non-negative integers expected at position 3.",
        ),
    ],
)
def test_range(str_expr, str_expected, failure_message):
    check_evaluation(str_expr, str_expected, failure_message)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "failure_message"),
    [
        (
            "Table[x, {x,0,1/3}]",
            "{0}",
            None,
        ),
        (
            "Table[x, {x, -0.2, 3.9}]",
            "{-0.2, 0.8, 1.8, 2.8, 3.8}",
            None,
        ),
        (
            "Table[i, {i, 1, 9, 0}]",
            "Table[i, {i, 1, 9, 0}]",
            "Table::iterb: Iterator does not have appropriate bounds.",
        ),
    ],
)
def test_table(str_expr, str_expected, failure_message):
    check_evaluation(str_expr, str_expected, failure_message)


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "failure_message"),
    [
        (None, None, None),
        (
            "ClearAll[l, x]; l = Table[x, {1}]; x = 1; l",
            "{1}",
            "A table sees a definition made after it.",
        ),
        (
            "ClearAll[l, f, y]; l = Table[f[y], {1}]; f[y_] := 7; l",
            "{7}",
            "A table sees a rule defined after it.",
        ),
        (
            "ClearAll[t, x]; t = Table[i + x, {i, 2}]; x = 1; t",
            "{2, 3}",
            None,
        ),
        ("{f /@ {}}", "{{}}", "A list of literals with pessimistic properties."),
        ("Table[f /@ {}, {2}]", "{{}, {}}", None),
        ("ClearAll[l, t, f, x, y]", "Null", None),
    ],
)
def test_table_is_evaluated_again(str_expr, str_expected, failure_message):
    check_evaluation(str_expr, str_expected, failure_message)


def test_table_fully_evaluated_at_creation():
    """A table of literal elements, like a list of numbers, is known to be
    fully evaluated as soon as Table builds it; a table with other elements
    is not."""
    from mathics.builtin.list.constructing import Table
    from mathics.core.atoms import Integer1, Integer2
    from mathics.core.expression import Expression
    from mathics.core.list import ListExpression
    from mathics.core.symbols import Symbol
    from mathics.core.systemsymbols import SymbolTimes

    numbers = Table.get_result(None, [Integer1, Integer2])
    assert numbers.elements_properties is not None
    assert numbers.elements_properties.elements_fully_evaluated

    pairs = Table.get_result(
        None, [ListExpression(Integer1, Integer2), ListExpression(Integer2, Integer1)]
    )
    assert pairs.elements_properties.elements_fully_evaluated

    x = Symbol("Global`x")
    symbolic = Table.get_result(None, [x, Expression(SymbolTimes, Integer2, x)])
    assert not (
        symbolic.elements_properties
        and symbolic.elements_properties.elements_fully_evaluated
    )
