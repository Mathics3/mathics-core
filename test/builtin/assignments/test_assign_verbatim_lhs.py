# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.assignments.assignment

Tests here check the compatibility of
the  default behavior of the different assignment operators
with WMA.
"""
# TODO: consider splitting this module into sub-modules.

from test.helper import check_arg_counts, check_evaluation, session

import pytest
from mathics_scanner.errors import IncompleteSyntaxError


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (None, None, None),
        (
            "Verbatim[F][x_Integer]:=3; DownValues[F]",
            "{HoldPattern[Verbatim[F][x_Integer]] :> 3}",
            None,
        ),
        ("Verbatim[F][x_Integer]=.; DownValues[F]", "{}", None),
        (
            "M[Verbatim[F][u_]]^:=3; UpValues[F]",
            "{HoldPattern[M[Verbatim[F][u_]]] :> 3}",
            None,
        ),
        ("F/:M[Verbatim[F][u_]]=.; UpValues[F]", "{}", None),
        (
            "Unprotect[N]; Verbatim[N][F[x_Integer],_]:=0.;DownValues[N]",
            "{HoldPattern[Verbatim[N][F[x_Integer], _]] :> 0.}",
            None,
        ),
    ],
)
def test_verbatim_assignment(str_expr, str_expected, msg):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=msg,
    )
