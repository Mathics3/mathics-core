# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.scoping.
"""
from test.helper import check_evaluation, session

import pytest

from mathics.core.symbols import Symbol


def test_unique():
    """
    test Unique
    """

    # test Unique[]
    symbol = session.evaluate("Unique[]")
    assert isinstance(
        symbol, Symbol
    ), f"Unique[] should return a Symbol; got {type(symbol)}"
    symbol_set = set([symbol])
    for i in range(5):
        symbol = session.evaluate("Unique[]")
        assert (
            symbol not in symbol_set
        ), "Unique[] should return different symbols; {symbol.name} is duplicated"
        symbol_set.add(symbol)

    # test Unique[<prefix>]
    symbol_prefix = symbol.name[0]

    for i in range(5):
        symbol = session.evaluate(f"Unique[{symbol_prefix}]")
        assert (
            symbol not in symbol_set
        ), "Unique[{symbol_prefix}] should return different symbols; {symbol.name} is duplicated"


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("InputForm[$Context]", None, '"Global`"', None),
        ## Test general context behaviour
        ("Plus === Global`Plus", None, "False", None),
        ("`Plus === Global`Plus", None, "True", None),
        ("Unique[{}]", None, "{}", None),
    ],
)
def test_private_doctests_scoping(str_expr, msgs, str_expected, fail_msg):
    """ """
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
        ("Block[{i = 0}, With[{}, Module[{j = i}, Set[i, i+1]; j]]]", None, "0", None),
    ],
)
def test_scoping_constructs(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
