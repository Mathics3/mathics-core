# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.specialfns.bessel and
mathics.builtins.specialfns.orthogonal
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "assert_failure_msg"),
    # Basically special rules from autoload/rules/Bessel.m that are not covered
    # by SymPy.
    [
        (
            "z=.;BesselI[1/2,z]",
            "Sqrt[2] Sinh[z] / (Sqrt[z] Sqrt[Pi])",
            "BesselI 1/2 rule",
        ),
        (
            "BesselI[-1/2,z]",
            "Sqrt[2] Cosh[z] / (Sqrt[z] Sqrt[Pi])",
            "BesselI -1/2 rule",
        ),
        ("BesselJ[-1/2,z]", "Sqrt[2] Cos[z] / (Sqrt[z] Sqrt[Pi])", "BesselJ -1/2 rule"),
        ("BesselJ[1/2,z]", "Sqrt[2] Sin[z] / (Sqrt[z] Sqrt[Pi])", "BesselJ 1/2 rule"),
    ],
)
def test_add(str_expr, str_expected, assert_failure_msg):
    check_evaluation(
        str_expr, str_expected, hold_expected=True, failure_message=assert_failure_msg
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("AiryAiZero[1]", None, "AiryAiZero[1]", None),
        ("AiryAiZero[1.]", None, "AiryAiZero[1.]", None),
        ("AiryAi[AiryAiZero[1]]", None, "0", None),
        (
            "N[AiryAiZero[2], 100]",
            None,
            "-4.087949444130970616636988701457391060224764699108529754984160876025121946836047394331169160758270562",
            None,
        ),
        ("AiryBiZero[1]", None, "AiryBiZero[1]", None),
        ("AiryBiZero[1.]", None, "AiryBiZero[1.]", None),
        ("AiryBi[AiryBiZero[1]]", None, "0", None),
        (
            "N[AiryBiZero[2], 100]",
            None,
            "-3.271093302836352715680228240166413806300935969100284801485032396261130864238742879252000673830055014",
            None,
        ),
        ("BesselJ[2.5, 1]", None, "0.0494968", None),
    ],
)
def test_private_doctests_bessel(str_expr, msgs, str_expected, fail_msg):
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
            "SphericalHarmonicY[1,1,x,y]",
            None,
            "-Sqrt[6] E ^ (I y) Sin[x] / (4 Sqrt[Pi])",
            None,
        ),
    ],
)
def test_private_doctests_orthogonal(str_expr, msgs, str_expected, fail_msg):
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
