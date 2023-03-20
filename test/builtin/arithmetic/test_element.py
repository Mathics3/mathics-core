# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.arithmetic.Element
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            "Table[Element[elem, Integers], {elem, {1, 1.3, Pi, a, True, Sqrt[5]-2,Sin[3]}}]",
            "{True, False, False, Element[a, Integers], False, False, False}",
            "Integers",
        ),
        (
            "Table[Element[elem, Primes], {elem, {1, 2, 1.3, Pi, a, True, Sqrt[5]-2,Sin[3]}}]",
            "{False, True, False, False, Element[a, Primes], False, False, False}",
            "Primes",
        ),
        (
            "Table[Element[elem, Rationals], {elem, {1, 1.3, Pi, a, True, Sqrt[5]-2,Sin[3]}}]",
            "{True, Element[1.3, Rationals], False, Element[a, Rationals], False, False, False}",
            "Rationals",
        ),
        (
            "Table[Element[elem, Reals], {elem, {1, 1.3, Pi, a, True, Sqrt[5]-2, Sin[3]}}]",
            "{True, True, True, Element[a, Reals], False, True, True}",
            "Reals",
        ),
        (
            "Table[Element[elem, Complexes], {elem, {1, 1.3, Pi, a, True, Sqrt[5]-2, Sin[3]}}]",
            "{True, True, True, Element[a, Complexes], False, True, True}",
            "Complexes",
        ),
        (
            "Table[Element[elem, Algebraics], {elem, {1, 1.3, Pi, a, True, Sqrt[5]-2, Sin[3]}}]",
            "{True, Element[1.3, Algebraics], False, Element[a, Algebraics], False, True, False}",
            "Algebraics",
        ),
        (
            "Table[Element[elem, Booleans], {elem, {1, 1.3, Pi, a, True, Sqrt[5]-2, Sin[3]}}]",
            "{False, False, False, Element[a, Booleans], True, False, False}",
            "Booleans",
        ),
    ],
)
def test_element(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)
