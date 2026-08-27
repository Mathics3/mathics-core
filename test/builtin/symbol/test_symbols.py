# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.symbol.symbols.
"""
from test.helper import check_arg_counts, check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "warnings", "str_expected", "fail_msg"),
    [
        ## placeholder for general context-related tests
        ("x === Global`x", None, "True", None),
        ("`x === Global`x", None, "True", None),
        ("a`x === Global`x", None, "False", None),
        ("a`x === a`x", None, "True", None),
        ("a`x === b`x", None, "False", None),
        ## awkward parser cases
        ("FullForm[a`b_]", None, "Pattern[a`b, Blank[]]", None),
        (
            'Clear[a]; Information[a, "Usage"]',
            None,
            "Global`a",
            'When a symbol is not bound, Information[, "Usage"] of that symbol should return the context and name.',
        ),
        (
            "a = 2;",
            None,
            "Null",
            "When a symbol is bound, Information[] of that symbol do anything.",
        ),
        ("Information[a]", tuple(), "Information[2]", None),
        (
            "{?? q, ?? q}",
            tuple(),
            "{Missing[UnknownSymbol, q], Missing[UnknownSymbol, q]}",
            "q does not exist, and Information does not create it.",
        ),
        (
            '{Information[s, "Usage"], Information["s", "Usage"]}',
            None,
            "{Global`s, Global`s}",
            "When s is passed as a symbol, it creates the definition.",
        ),
        ("f[x_] := x ^ 2;", None, "Null", None),
        ("g[f] ^:= 2;", None, "Null", None),
        ('f::usage = "f[x] returns the square of x";', None, "Null", None),
        (
            'Information[f, "Usage"]',
            tuple(),
            "f[x] returns the square of x",
            None,
        ),
        ('Length[Names["System`*"]] > 350', None, "True", None),
        (
            "{\\[Eta], \\[CapitalGamma]\\[Beta], Z\\[Infinity], \\[Angle]XYZ, \\[FilledSquare]r, i\\[Ellipsis]j}",
            None,
            "{\u03b7, \u0393\u03b2, Z\u221e, \u2220XYZ, \u25a0r, i\u2026j}",
            None,
        ),
        ("SymbolName[a`b`x] // InputForm", None, '"x"', None),
        ("ValueQ[True]", None, "False", None),
    ],
)
def test_symbol(str_expr, warnings, str_expected, fail_msg):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message="",
        expected_messages=warnings,
        hold_expected=True,
    )


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "Information",
            "1 or 2 arguments are",
        ),
        (
            "Symbol",
            "1 argument is",
        ),
        (
            "SymbolName",
            "1 argument is",
        ),
        (
            "ValueQ",
            "1 argument is",
        ),
    ],
)
def test_symbols_arg_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)
