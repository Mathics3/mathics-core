# -*- coding: utf-8 -*-
"""
Unit tests for mathics.buitin.numbers.nintegrate

NIntegrate[] tests

"""
from test.helper import evaluate

import pytest

from mathics.builtin.base import check_requires_list

if check_requires_list(["scipy", "scipy.integrate"]):
    methods = ["Automatic", "Romberg", "Internal", "NQuadrature"]

    generic_tests_for_nintegrate = [
        (r"NIntegrate[x^2, {x,0,1}, {method} ]", r"1/3.", ""),
        (r"NIntegrate[x^2 y^2, {y,0,1}, {x,0,1}, {method} ]", r"1/9.", ""),
        # FIXME: improve singularity handling in NIntegrate
        # (
        #    r"NIntegrate[x^2 y^(-1.+1/3.), {x,1.*^-9,1},{y, 1.*^-9,1}, {method}]",
        #    r"1.",
        #    "",
        # ),
    ]

    tests_for_nintegrate = sum(
        [
            [
                (tst[0].replace("{method}", "Method->" + method), tst[1], tst[2])
                for tst in generic_tests_for_nintegrate
            ]
            for method in methods
        ],
        [],
    )
else:
    tests_for_nintegrate = [
        (r"NIntegrate[x^2, {x,0,1}]", r"1/3.", ""),
        (r"NIntegrate[x^2 y^2, {y,0,1}, {x,0,1}]", r"1/9.", ""),
        # FIXME: this can integrate to Infinity
        # (r"NIntegrate[x^2 y^(-.5), {x,0,1},{y,0,1}]", r"1.", ""),
    ]


@pytest.mark.parametrize("str_expr, str_expected, msg", tests_for_nintegrate)
def test_nintegrate(str_expr: str, str_expected: str, msg: str, message=""):
    result = evaluate(str_expr)
    expected = evaluate(str_expected)
    if msg:
        assert result == expected, msg
    else:
        assert result == expected
