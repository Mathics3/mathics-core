# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.constants
"""
from test.helper import check_evaluation

import pytest


def test_Undefined():
    for fn in [
        "Abs",
        "ArcCos",
        "ArcCosh",
        "ArcCot",
        "ArcCoth",
        "ArcCsc",
        "ArcCsch",
        "ArcSec",
        "ArcSech",
        "ArcSin",
        "ArcSinh",
        "ArcTan",
        "ArcTanh",
        "Conjugate",
        "Cos",
        "Cosh",
        "Cosh",
        "Cot",
        "Coth",
        "Gamma",
        "Gudermannian",
        "Log",
        "Sech",
        "Sin",
        "Sinh",
        "Tan",
        "Tanh",
    ]:
        check_evaluation(f"{fn}[Undefined]", "Undefined")

    for fn in [
        "ArcTan",
        "BesselI",
        "BesselJ",
        "BesselK",
        "BesselY",
        "PolyGamma",
        "StieltjesGamma",
        "StruveH",
        "StruveL",
    ]:
        check_evaluation(f"{fn}[a, Undefined]", "Undefined")
        check_evaluation(f"{fn}[Undefined, b]", "Undefined")


# This is a miscelanea of private tests. I put here to make it easier to check
# where these tests comes from. Then, we can move them to more suitable places.
@pytest.mark.parametrize(
    ("expr_str", "expected_str", "fail_msg", "msgs"),
    [
        (
            "ComplexInfinity + ComplexInfinity",
            "Indeterminate",
            "Issue689",
            ["Indeterminate expression ComplexInfinity + ComplexInfinity encountered."],
        ),
        (
            "ComplexInfinity + Infinity",
            "Indeterminate",
            "Issue689",
            ["Indeterminate expression ComplexInfinity + Infinity encountered."],
        ),
        ("Cos[Degree[x]]", "Cos[Degree[x]]", "Degree as a function", None),
        ("N[Degree]//OutputForm", "0.0174533", "Degree", None),
        ("5. E//OutputForm", "13.5914", "E", None),
        ("N[Degree, 30]//OutputForm", "0.0174532925199432957692369076849", None, None),
        ("FullForm[Infinity]", "DirectedInfinity[1]", None, None),
        ("(2 + 3.5*I) / Infinity", "0. + 0. I", "Complex over Infinity", None),
        ("Infinity + Infinity", "Infinity", "Infinity plus Infinity", None),
        (
            "Infinity / Infinity",
            "Indeterminate",
            "Infinity over Infinity",
            ["Indeterminate expression 0 Infinity encountered."],
        ),
    ],
)
def test_constants_private(expr_str, expected_str, fail_msg, msgs):
    check_evaluation(
        expr_str,
        expected_str,
        fail_msg,
        expected_messages=msgs,
        hold_expected=True,
        to_string_expected=True,
        to_string_expr=True,
    )
