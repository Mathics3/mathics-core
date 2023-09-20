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
        (
            "Solve[Abs[-2/3*(lambda + 2) + 8/3 + 4] == 4, lambda,Reals]",
            "{{lambda -> 2}, {lambda -> 14}}",
            "abs()",
        ),
        (
            "Solve[q^3 == (20-12)/(4-3), q,Reals]",
            "{{q -> 2}}",
            "domain check",
        ),
        (
            "Solve[x + Pi/3 == 2k*Pi + Pi/6 || x + Pi/3 == 2k*Pi + 5Pi/6, x,Reals]",
            "{{x -> -Pi / 6 + 2 k Pi}, {x -> Pi / 2 + 2 k Pi}}",
            "logics involved",
        ),
        (
            "Solve[m - 1 == 0 && -(m + 1) != 0, m,Reals]",
            "{{m -> 1}}",
            "logics and constraints",
        ),
        (
            "Solve[(lambda + 1)/6 == 1/(mu - 1) == lambda/4, {lambda, mu},Reals]",
            "{{lambda -> 2, mu -> 3}}",
            "chained equations",
        ),
        (
            "Solve[2*x0*Log[x0] + x0 - 2*a*x0 == -1 && x0^2*Log[x0] - a*x0^2 + b == b - x0, {x0, a, b},Reals]",
            "{{x0 -> 1, a -> 1}}",
            "excess variable b",
        ),
    ):
        session.evaluate("Clear[h]; Clear[g]; Clear[f];")
        check_evaluation(str_expr, str_expected, message)
