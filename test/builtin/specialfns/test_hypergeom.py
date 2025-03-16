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
