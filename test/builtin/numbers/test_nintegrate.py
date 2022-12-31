# -*- coding: utf-8 -*-
"""
Unit tests for mathics.buitin.numbers.nintegrate

NIntegrate[] tests

"""
from test.helper import check_evaluation
from typing import Optional

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
                (tst[0].replace("{method}", "Method->" + method), tst[1], tst[2], None)
                for tst in generic_tests_for_nintegrate
            ]
            for method in methods
        ],
        [
            (
                r'NIntegrate[1., {x,0,1}, Method->"Quadrature"]',
                "1.",
                "Check that the library is already loaded.",
                [],
            ),
            (
                r'NIntegrate[1., {x,0,1}, Method->"NotAMethod"]',
                "1.",
                None,
                [
                    r"The Method option should be a built-in method name in {`Automatic`, `Internal`, `Simpson`, `NQuadrature`, `Quadrature`, `Romberg`}. Using `Automatic`"
                ],
            ),
        ],
    )
else:
    tests_for_nintegrate = [
        (r"NIntegrate[x^2, {x,0,1}]", r"1/3.", "", None),
        (r"NIntegrate[x^2 y^2, {y,0,1}, {x,0,1}]", r"1/9.", "", None),
        # FIXME: this can integrate to Infinity
        # (r"NIntegrate[x^2 y^(-.5), {x,0,1},{y,0,1}]", r"1.", ""),
        (
            r'NIntegrate[1., {x,0,1}, Method->"NotAMethod"]',
            "1.",
            None,
            [
                r"The Method option should be a built-in method name in {`Automatic`, `Internal`, `Simpson`}. Using `Automatic`"
            ],
        ),
    ]


@pytest.mark.parametrize("str_expr, str_expected, msg, messages", tests_for_nintegrate)
def test_nintegrate(
    str_expr: str, str_expected: str, msg: str, messages: Optional[list]
):
    check_evaluation(
        str_expr, str_expected, failure_message=msg, expected_messages=messages
    )
