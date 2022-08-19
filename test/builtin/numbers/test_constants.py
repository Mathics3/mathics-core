# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.constants
"""
from test.helper import check_evaluation


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
