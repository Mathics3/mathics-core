# -*- coding: utf-8 -*-
"""
Test mathics.core.symbols
"""

from mathics.core.symbols import Symbol


def test_Symbol_get_name():
    """
    Test Symbol().get_name()
    """
    short_symbol_name = "testSymbol"
    symbol_with_context_name = f"System`{short_symbol_name}"
    symbol = Symbol(symbol_with_context_name)
    assert symbol.get_name() == symbol_with_context_name
    assert symbol.get_name(short=False) == symbol_with_context_name
    assert symbol.get_name(short=True) == short_symbol_name
