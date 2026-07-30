# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.symbol.properties
"""
from test.helper import check_evaluation

import pytest


def test_downvalues():
    for str_expr, str_expected, assert_fail_message in (
        (
            "DownValues[foo]={x_^2:>y}",
            "{x_ ^ 2 :> y}",
            "Issue #1251 part 1",
        ),
        (
            "DownValues[foo]",
            "{HoldPattern[x_ ^ 2] :> y}",
            "Check that we get the DownValue just assigned.",
        ),
        (
            'DownValues["foo"]',
            "{HoldPattern[x_ ^ 2] :> y}",
            "A string is allowed in as a DownValues argument.",
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
        check_evaluation(
            str_expr,
            str_expected,
            assert_fail_message,
            to_string_expr=False,
            to_string_expected=False,
        )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msgs", "failure_msg"),
    [
        (None, None, None, None),
        # From Clear
        ("x = 2;OwnValues[x]=.;x", "x", None, "Erase Ownvalues"),
        ("f[a][b] = 3; SubValues[f] =.;f[a][b]", "f[a][b]", None, "Erase Subvalues"),
        ("PrimeQ[p] ^= True; PrimeQ[p]", "True", None, "Subvalues"),
        ("UpValues[p]=.; PrimeQ[p]", "False", None, "Erase Subvalues"),
        ("a + b ^= 5; a =.; a + b", "5", None, None),
        ("{UpValues[a], UpValues[b]} =.; a+b", "a+b", None, None),
        (
            "Unset[Messages[1]]",
            "$Failed",
            [
                "First argument in Messages[1] is not a symbol or a string naming a symbol."
            ],
            "Unset Message",
        ),
        (" g[a+b] ^:= 2", "$Failed", ("Tag Plus in g[a + b] is Protected.",), None),
        (" g[a+b]", "g[a + b]", None, None),
    ],
)
def test_upvalues_ownvalues(str_expr, str_expected, msgs, failure_msg):
    check_evaluation(
        str_expr, str_expected, expected_messages=msgs, failure_message=failure_msg
    )
