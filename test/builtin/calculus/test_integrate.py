# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.calculus.Integrate
"""

from test.helper import check_evaluation, session


def test_integrate():
    for str_expr, str_expected, message in (
        ("Integrate[Integrate[1,{y,0,E^x}],{x,0,Log[13]}]", "12", "Issue #153"),
        (
            "g/:Integrate[g[u_],u_]:=f[u]; Integrate[g[x],x]",
            "f[x]",
            "This should pass SymPy evaluation.",
        ),
        (
            "h=x;Integrate[Do[h=x*h,{5}]; h,x]",
            "x^7/7",
            "a more agressive SymPy translation.",
        ),
    ):
        session.evaluate("Clear[h]; Clear[g]; Clear[f];")
        check_evaluation(str_expr, str_expected, message)
