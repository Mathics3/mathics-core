# -*- coding: utf-8 -*-
"""
Unit tests from builtins ... calculus.py
"""

from .helper import check_evaluation, session


def test_calculus():
    for str_expr, str_expected, message in (
        (
            "Solve[{(7+x)*ma == 167, (5+x)*mb == 167, (7+5)*(ma+mb) == 334}, {ma, mb, x}]",
            "{{ma -> 1169 / 12 - 167 Sqrt[37] / 12, mb -> -835 / 12 + 167 Sqrt[37] / 12, x -> Sqrt[37]}, {ma -> 1169 / 12 + 167 Sqrt[37] / 12, mb -> -835 / 12 - 167 Sqrt[37] / 12, x -> -Sqrt[37]}}",
            "Issue63",
        ),
        (
            "Solve[{(7+x)*ma == 167, (5+x)*mb == 167, (7+5)*(ma+mb) == 334}, {x, ma, mb}]",
            "{{x -> -Sqrt[37], ma -> 1169 / 12 + 167 Sqrt[37] / 12, mb -> -835 / 12 - 167 Sqrt[37] / 12}, {x -> Sqrt[37], ma -> 1169 / 12 - 167 Sqrt[37] / 12, mb -> -835 / 12 + 167 Sqrt[37] / 12}}",
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
        ("Integrate[Integrate[1,{y,0,E^x}],{x,0,Log[13]}]", "12", "Issue #153"),
        (
            "g/:Integrate[g[u_],u_]:=f[u]; Integrate[g[x],x]",
            "f[x]",
            "This should pass after implementing an earlier sympy evaluation.",
        ),
        (
            "h=x;Integrate[Do[h=x*h,{5}]; h,x]",
            "x^7/7",
            "another sanity check for a more agressive sympy translation.",
        ),
    ):
        session.evaluate("Clear[h]; Clear[g]; Clear[f];")
        check_evaluation(str_expr, str_expected, message)
