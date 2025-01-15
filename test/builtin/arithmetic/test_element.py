# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.arithmetic.Element
"""
from test.helper import check_evaluation

import pytest

test_set = "{elem, {1, 2, 4, 1.3, Pi, a, True, Sqrt[5]-2, Sin[3]}}"

domains = {
    "Integers": (
        "{True, True, True, False, False, " "Element[a, Integers], False, False, False}"
    ),
    "Primes": (
        "{False, True, False, False, False, " "Element[a, Primes], False, False, False}"
    ),
    "Rationals": (
        "{True, True, True, Element[1.3, Rationals], False, "
        "Element[a, Rationals], False, False, False}"
    ),
    "Reals": (
        "{True, True, True, True, True, " "Element[a, Reals], False, True, True}"
    ),
    "Complexes": (
        "{True, True, True, True, True, " "Element[a, Complexes], False, True, True}"
    ),
    "Algebraics": (
        "{True, True, True, Element[1.3, Algebraics], False, "
        "Element[a, Algebraics], False, True, False}"
    ),
    "Booleans": (
        "{False, False, False, False, False, "
        "Element[a, Booleans], True, False, False}"
    ),
}


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            f"Table[Element[elem, {key}], {test_set}]",
            domains[key],
            key,
        )
        for key in domains
    ],
)
def test_element(str_expr, str_expected, msg):
    check_evaluation(str_expr, str_expected, failure_message=msg)
