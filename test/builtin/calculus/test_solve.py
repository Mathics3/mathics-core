# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.arithmetic.Solve
"""

from test.helper import check_evaluation, session


def test_solve():
    for str_expr, str_expected, message in (
        # Clean the definitions, because
        # a previous definition of `a` makes
        # the test to fail.
        (None, None, None),
        (
            "Solve[{(7+x)*ma == 167, (5+x)*mb == 167, (7+5)*(ma+mb) == 334}, {ma, mb, x}]//Sort",
            "{{ma -> 1169 / 12 - 167 Sqrt[37] / 12, mb -> -835 / 12 + 167 Sqrt[37] / 12, x -> Sqrt[37]}, {ma -> 1169 / 12 + 167 Sqrt[37] / 12, mb -> -835 / 12 - 167 Sqrt[37] / 12, x -> -Sqrt[37]}}",
            "Issue63",
        ),
        (
            "Solve[{(7+x)*ma == 167, (5+x)*mb == 167, (7+5)*(ma+mb) == 334}, {x, ma, mb}]//Sort",
            "{{x -> Sqrt[37], ma -> 1169 / 12 - 167 Sqrt[37] / 12, mb -> -835 / 12 + 167 Sqrt[37] / 12},{x -> -Sqrt[37], ma -> 1169 / 12 + 167 Sqrt[37] / 12, mb -> -835 / 12 - 167 Sqrt[37] / 12}}",
            "Issue 208",
        ),
        (
            "Solve[x + 1 == 2, x]",
            "{{x -> 1}}",
            "",
        ),
        (
            "Solve[{a == 1, 0==0, b==I, 1==1},{a}]",
            "{{a -> 1}}",
            "Issue #1168",
        ),
        (
            "v1 := Exp[x] - 3x; v2 = {x, 1.5}; FindRoot[v1, v2]",
            "{x->1.51213}",
            "Issue #1235",
        ),
        (
            "v1 := Exp[x] - 3x; v2 = {x, 2}; FindRoot[v1, v2]",
            "{x->1.51213}",
            "Issue #1235",
        ),
    ):
        session.evaluate("Clear[h]; Clear[g]; Clear[f];")
        check_evaluation(str_expr, str_expected, message)
