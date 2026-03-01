# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.atomic.symbols.
"""
from test.helper import check_evaluation

import pytest


def test_downvalues():
    for str_expr, str_expected, message in (
        (
            "DownValues[foo]={x_^2:>y}",
            "{x_ ^ 2 :> y}",
            "Issue #1251 part 1",
        ),
        (
            "PrependTo[DownValues[foo], {x_^3:>z}]",
            "{{x_ ^ 3 :> z}, HoldPattern[x_ ^ 2] :> y}",
            "Issue #1251 part 2",
        ),
        (
            "DownValues[foo]={x_^3:>y}",
            "{x_ ^ 3 :> y}",
            "Issue #1251 part 3",
        ),
    ):
        check_evaluation(str_expr, str_expected, message)


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
        ("a = 2;", None, "Null", None),
        ("Information[a]", tuple(), "Global`a\n\na = 2\n", None),
        ("f[x_] := x ^ 2;", None, "Null", None),
        ("g[f] ^:= 2;", None, "Null", None),
        ('f::usage = "f[x] returns the square of x";', None, "Null", None),
        (
            "Information[f]",
            tuple(),
            "f[x] returns the square of x\n\nf[x_] = x^2\n\ng[f] ^= 2\n",
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
def test_private_doctests_symbol(str_expr, warnings, str_expected, fail_msg):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message="",
        expected_messages=warnings,
        hold_expected=True,
    )
