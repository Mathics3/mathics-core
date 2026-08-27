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
    ("str_expr", "str_expected", "assert_failure_msg"),
    [
        # Rayleigh formulas should expand half-integer orders for BesselJ/BesselI
        # into closed-form trig/hyperbolic expressions (not remain as Bessel calls).
        (
            "z=.;Head[BesselJ[3/2, z]]",
            "Times",
            "BesselJ[3/2, z] should be expanded by Rayleigh formula",
        ),
        (
            "Head[BesselJ[-3/2, z]]",
            "Times",
            "BesselJ[-3/2, z] should be expanded by Rayleigh formula",
        ),
        (
            "Head[BesselI[3/2, z]]",
            "Times",
            "BesselI[3/2, z] should be expanded by Rayleigh formula",
        ),
        (
            "Head[BesselI[-3/2, z]]",
            "Times",
            "BesselI[-3/2, z] should be expanded by Rayleigh formula",
        ),
        (
            "Head[BesselK[3/2, z]]",
            "Times",
            "BesselK[3/2, z] should be expanded by Rayleigh formula",
        ),
        (
            "Head[BesselK[-3/2, z]]",
            "Times",
            "BesselK[-3/2, z] should be expanded by Rayleigh formula",
        ),
        (
            "Head[BesselY[3/2, z]]",
            "Times",
            "BesselY[3/2, z] should be expanded by Rayleigh formula",
        ),
        (
            "Head[BesselY[-3/2, z]]",
            "Times",
            "BesselY[-3/2, z] should be expanded by Rayleigh formula",
        ),
    ],
)
def test_bessel_half_integer_rayleigh(str_expr, str_expected, assert_failure_msg):
    """Test that Rayleigh formulas correctly expand half-integer Bessel orders."""
    check_evaluation(
        str_expr, str_expected, hold_expected=True, failure_message=assert_failure_msg
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "assert_failure_msg"),
    [
        # Integer orders must NOT be expanded by Rayleigh formulas.
        # These should remain unevaluated (symbolic).
        (
            "z=.;BesselJ[1, z]",
            "BesselJ[1, z]",
            "BesselJ[1, z] should not be expanded by Rayleigh formula",
        ),
        (
            "BesselJ[2, z]",
            "BesselJ[2, z]",
            "BesselJ[2, z] should not be expanded by Rayleigh formula",
        ),
        (
            "BesselJ[-1, z]",
            "-BesselJ[1, z]",
            "BesselJ[-1, z] should use integer reflection, not Rayleigh",
        ),
        (
            "BesselI[1, z]",
            "BesselI[1, z]",
            "BesselI[1, z] should not be expanded by Rayleigh formula",
        ),
        (
            "BesselI[2, z]",
            "BesselI[2, z]",
            "BesselI[2, z] should not be expanded by Rayleigh formula",
        ),
        (
            "BesselK[1, z]",
            "BesselK[1, z]",
            "BesselK[1, z] should not be expanded by Rayleigh formula",
        ),
        (
            "BesselK[2, z]",
            "BesselK[2, z]",
            "BesselK[2, z] should not be expanded by Rayleigh formula",
        ),
        (
            "BesselY[1, z]",
            "BesselY[1, z]",
            "BesselY[1, z] should not be expanded by Rayleigh formula",
        ),
        (
            "BesselY[2, z]",
            "BesselY[2, z]",
            "BesselY[2, z] should not be expanded by Rayleigh formula",
        ),
    ],
)
def test_bessel_integer_order_not_expanded(str_expr, str_expected, assert_failure_msg):
    """
    Regression test: Rayleigh formulas must only match half-integer orders
    (e.g. 1/2, 3/2, 5/2), not integer orders (e.g. 1, 2, 3).

    Previously, the pattern condition `IntegerQ[2*nu]` also matched integers
    (since 2*1 = 2 is an integer), causing incorrect symbolic expansions.
    The fix adds `!IntegerQ[nu]` to exclude true integers.
    See https://github.com/Mathics3/mathics-core/pull/1762.
    """
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
def test_bessel(str_expr, msgs, str_expected, fail_msg):
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
def test_orthogonal(str_expr, msgs, str_expected, fail_msg):
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
