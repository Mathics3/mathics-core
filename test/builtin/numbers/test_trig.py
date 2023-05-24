# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.numbers.trig

For this to work we also make use of rules from
mathics/autoload/rules/trig.m
"""
from test.helper import check_evaluation


def test_ArcCos():
    for str_expr, str_expected in (
        ("ArcCos[I Infinity]", "-I Infinity"),
        ("ArcCos[-I Infinity]", "I Infinity"),
        ("ArcCos[0]", "1/2 Pi"),
        ("ArcCos[1/2]", "1/3 Pi"),
        ("ArcCos[-1/2]", "2/3 Pi"),
        ("ArcCos[1/2 Sqrt[2]]", "1/4 Pi"),
        ("ArcCos[-1/2 Sqrt[2]]", "3/4 Pi"),
        ("ArcCos[1/2 Sqrt[3]]", "1/6 Pi"),
        ("ArcCos[-1/2 Sqrt[3]]", "5/6 Pi"),
        ("ArcCos[(1 + Sqrt[3]) / (2*Sqrt[2])]", "1/12 Pi"),
    ):
        check_evaluation(str_expr, str_expected)
