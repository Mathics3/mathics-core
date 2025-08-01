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
            "Hypergeometric1F1[{3,5},{7,1},{4,2}]",
            None,
            "{-1545 / 128 + 45 E ^ 4 / 128, 27 E ^ 2}",
            None,
        ),
        ("N[Hypergeometric1F1[{3,5},{7,1},{4,2}]]", None, "{7.12435, 199.505}", None),
        ("Hypergeometric1F1[b,b,z]", None, "E ^ z", None),
        (
            "Hypergeometric1F1[0,0,z]",
            None,
            "1",
            "Special case: Integer 1 (SymPy may work differently)",
        ),
        (
            "Hypergeometric1F1[0.0,0,z]",
            None,
            "1.",
            "Special case: MachineReal a parameter (SymPy may work differently)",
        ),
        (
            "Hypergeometric1F1[0,0,1.]",
            None,
            "1.",
            "Special case: MachineReal z parameter (SymPy may work differently)",
        ),
    ],
)
def test_Hypergeometric1F1(str_expr, msgs, str_expected, fail_msg):
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


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "N[HypergeometricPFQ[{4},{},1]]",
            None,
            "ComplexInfinity",
            None,
        ),
        ("HypergeometricPFQ[{6},{1},2]", None, "719 E ^ 2 / 15", None),
        ("N[HypergeometricPFQ[{6},{1},2]]", None, "354.182", None),
        ("HypergeometricPFQ[{},{},z]", None, "E ^ z", None),
        ("HypergeometricPFQ[{0},{c1,c2},z]", None, "1", None),
        ("HypergeometricPFQ[{c1,c2},{c1,c2},z]", None, "E ^ z", None),
        (
            "HypergeometricPFQ[{0},{0},2]",
            None,
            "1",
            "Special case: using Integer 'z' parameter",
        ),
        (
            "HypergeometricPFQ[{0},{0},3.0]",
            None,
            "1",
            "Special case: using MachineInteger 'z' parameter",
        ),
        (
            "HypergeometricPFQ[{0.0},{0},3.0]",
            None,
            "1.",
            "Special case: using MachineInteger 'a' parameter",
        ),
    ],
)
def test_HypergeometricPFQ(str_expr, msgs, str_expected, fail_msg):
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


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("N[HypergeometricU[{3,1},{2,4},{7,8}]]", None, "{0.00154364, 0.160156}", None),
        ("HypergeometricU[0,c,z]", None, "1", None),
    ],
)
def test_HypergeometricU(str_expr, msgs, str_expected, fail_msg):
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


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            "MeijerG[{{},{}},{{0,0},{0,0}},100^2]",
            None,
            "MeijerG[{{}, {}}, {{0, 0}, {0, 0}}, 10000]",
            None,
        ),
        ("N[MeijerG[{{},{}},{{0,0},{0,0}},100^2]]", None, "0.000893912", None),
        (
            "HypergeometricU[{3,1},{2,4},{7,8}]",
            None,
            "{MeijerG[{{-2}, {}}, {{0, -1}, {}}, 7] / 2, HypergeometricU[1, 4, 8]}",
            None,
        ),
    ],
)
def test_MeijerG(str_expr, msgs, str_expected, fail_msg):
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
