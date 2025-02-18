# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.specialfns.gamma
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("0!", None, "1", None),
        (
            "N[Gamma[24/10], 100]",
            None,
            "1.242169344504305404913070252268300492431517240992022966055507541481863694148882652446155342679460339",
            "Issue 203",
        ),
        (
            "res=N[N[Gamma[24/10],100]/N[Gamma[14/10],100],100]",
            None,
            "1.400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "Issue 203",
        ),
        ("res // Precision", None, "100.", None),
        (
            "Gamma[1.*^20]",
            ("Overflow occurred in computation.",),
            "Overflow[]",
            "Overflow",
        ),
        ("Gamma[1., 2.]", None, "Gamma[1., 2.]", "needs mpmath for lowergamma"),
        ("Clear[x]; Gamma[1 + x]", None, "Gamma[1 + x]", None),
    ],
)
def test_private_doctests_gamma(str_expr, msgs, str_expected, fail_msg):
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
