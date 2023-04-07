# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.scoping.
"""

from test.helper import session

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
