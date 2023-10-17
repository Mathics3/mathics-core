# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.evaluation.
"""


from test.helper import check_evaluation_as_in_cli, session

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("ClearAll[a];$RecursionLimit = 20", None, "20", None),
        ("a = a + a", ("Recursion depth of 20 exceeded.",), "$Aborted", None),
        ("$RecursionLimit = 200", None, "200", None),
        (
            "ClearAll[f];f[x_, 0] := x; f[x_, n_] := f[x + 1, n - 1];Block[{$RecursionLimit = 20}, f[0, 100]]",
            None,
            "100",
            None,
        ),
        (
            "ClearAll[f];f[x_, 0] := x; f[x_, n_] := Module[{y = x + 1}, f[y, n - 1]];Block[{$RecursionLimit = 20}, f[0, 100]]",
            ("Recursion depth of 20 exceeded.",),
            "$Aborted",
            None,
        ),
        (
            "ClearAll[f]; f[x_] := f[x + 1];f[x]",
            ("Iteration limit of 1000 exceeded.",),
            "$Aborted",
            None,
        ),
        (
            "$IterationLimit = x;",
            (
                "Cannot set $IterationLimit to x; value must be an integer between 20 and Infinity.",
            ),
            None,
            None,
        ),
        (
            "ClearAll[f];f[x_, 0] := x; f[x_, n_] := f[x + 1, n - 1];Block[{$IterationLimit = 20}, f[0, 100]]",
            ("Iteration limit of 20 exceeded.",),
            "$Aborted",
            None,
        ),
        ("ClearAll[f];", None, None, None),
        (
            "Attributes[h] = Flat;h[items___] := Plus[items];h[1, Unevaluated[Sequence[Unevaluated[2], 3]], Sequence[4, Unevaluated[5]]]",
            None,
            "15",
            None,
        ),
        # FIX Later
        (
            "ClearAll[f];f[x_, 0] := x; f[x_, n_] := Module[{y = x + 1}, f[y, n - 1]];Block[{$IterationLimit = 20}, f[0, 100]]",
            None,
            "100",
            "Fix me!",
        ),
        ("ClearAll[f];", None, None, None),
    ],
)
def test_private_doctests_evaluation(str_expr, msgs, str_expected, fail_msg):
    """These tests check the behavior of $RecursionLimit and $IterationLimit"""
    check_evaluation_as_in_cli(str_expr, str_expected, fail_msg, msgs)
