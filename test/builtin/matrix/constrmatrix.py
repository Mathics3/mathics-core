# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.matrix.constrmatrix
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "failure_message"),
    [
        (
            """BoxMatrix["a"]""",
            """BoxMatrix["a"]""",
            "notre: The first argument must be a non-complex number or a list of"
            " noncomplex numbers.",
        ),
    ],
)
def test_boxmatrix(str_expr, str_expected, failure_message):
    check_evaluation(str_expr, str_expected, failure_message)
