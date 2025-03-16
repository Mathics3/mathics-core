# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.specialfns.hypergeom
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "N[HypergeometricPFQ[{4},{},1]]",
            None,
            "ComplexInfinity",
            None,
        ),
        (
            "MeijerG[{{},{}},{{0,0},{0,0}},100^2]",
            None,
            "MeijerG[{{}, {}}, {{0, 0}, {0, 0}}, 10000]",
            None
        ),
        (
            "N[MeijerG[{{},{}},{{0,0},{0,0}},100^2]]",
            None,
            "0.000893912",
            None
        ),
        (
            "HypergeometricU[{3,1},{2,4},{7,8}]",
            None,
            "{MeijerG[{{-2}, {}}, {{0, -1}, {}}, 7] / 2, HypergeometricU[1, 4, 8]}",
            None
        ),
        (
            "N[HypergeometricU[{3,1},{2,4},{7,8}]]",
            None,
            "{0.00154364, 0.160156}",
            None
        ),
        (
            "HypergeometricU[0,c,z]",
            None,
            "1",
            None
        ),
        (
            "Hypergeometric1F1[{3,5},{7,1},{4,2}]",
            None,
            "{HypergeometricPFQ[{3}, {7}, 4], HypergeometricPFQ[{5}, {1}, 2]}",
            None
        ),
        (
            "N[Hypergeometric1F1[{3,5},{7,1},{4,2}]]",
            None,
            "{7.12435, 199.505}",
            None
        ),
        (
            "Hypergeometric1F1[b,b,z]",
            None,
            "E ^ z",
            None
        ),
        (
            "HypergeometricPFQ[{6},{1},2]",
            None,
            "HypergeometricPFQ[{6}, {1}, 2]",
            None
        ),
        (
            "N[HypergeometricPFQ[{6},{1},2]]",
            None,
            "354.182",
            None
        ),
        (
            "HypergeometricPFQ[{},{},z]",
            None,
            "1",
            None
        ),
        (
            "HypergeometricPFQ[{0},{c1,c2},z]",
            None,
            "1",
            None
        ),
        (
            "HypergeometricPFQ[{c1,c2},{c1,c2},z]",
            None,
            "E ^ z",
            None
        )
    ],
)
def test_private_hypergeom(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
