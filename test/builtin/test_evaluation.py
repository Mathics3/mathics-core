# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.evaluation.
"""

import sys
from test.helper import check_evaluation_as_in_cli

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (
            None,
            None,
            None,
            None,
        ),
        ("$RecursionLimit = 20", None, "20", None),
        ("a = a + a", ("Recursion depth of 20 exceeded.",), "$Aborted", None),
        ("$RecursionLimit = 200", None, "200", None),
        (
            "ClearAll[f]; f[0] = 0; f[n_] := 1 + f[n - 1]; Block[{$RecursionLimit = Infinity}, f[300]]",
            None,
            "300",
            "Infinity in a Block allows recursion deeper than the default limit",
        ),
        (
            "ClearAll[f]; f[0] = 0; f[n_] := Block[{$RecursionLimit = Infinity}, 1 + f[n - 1]]; f[150]",
            None,
            "150",
            "a Block value is evaluated before the variable is reset",
        ),
        (
            "ClearAll[f]; f[n_] := 1 + f[n + 1]; Block[{$RecursionLimit = Infinity}, f[0]]",
            ("Recursion depth of 512 exceeded.",),
            "$Aborted",
            "Infinity goes as deep as the Python stack is set up for, then stops",
        ),
        ("ClearAll[f];", None, None, None),
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
            ("Iteration limit of 4096 exceeded.",),
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
        # $IterationLimit bounds one chain of rewrites, not the number of
        # times symbols are looked up during the whole evaluation.
        (
            "Block[{$IterationLimit = 20, itlimX = {itlimA}}, Do[itlimX, {30}]; itlimX]",
            None,
            "{itlimA}",
            "Many separate lookups of a symbol do not add up",
        ),
        (
            'Do[Evaluate[Symbol["c" <> ToString[k]]] = Symbol["c" <> ToString[k + 1]], {k, 0, 29}]; Block[{$IterationLimit = 40}, c0]',
            None,
            "c30",
            "A chain of 30 rewrites is within the limit of 40",
        ),
        (
            "Block[{$IterationLimit = 20}, c0]",
            ("Iteration limit of 20 exceeded.",),
            "$Aborted",
            "A chain of 30 rewrites exceeds the limit of 20",
        ),
        (
            'ClearAll[c0, c30]; Do[ClearAll[Evaluate[Symbol["c" <> ToString[k]]]], {k, 1, 29}];',
            None,
            None,
            None,
        ),
        (
            "Attributes[h] = Flat;h[items___] := Plus[items];h[1, Unevaluated[Sequence[Unevaluated[2], 3]], Sequence[4, Unevaluated[5]]]",
            None,
            "15",
            None,
        ),
        ("ClearAll[f];", None, None, None),
        # Release, the obsolete form of Evaluate
        ("x = 1 + 1; Release[x]", None, "2", None),
        (
            "With[{name = h}, f[Release[name][k_]] := {name, k}]; f[h[3]]",
            None,
            "{h, 3}",
            "Release in the left-hand side of a definition",
        ),
        ("ClearAll[f, h, x];", None, None, None),
    ],
)
def test_evaluation(str_expr, msgs, str_expected, fail_msg):
    """These tests check the behavior of $RecursionLimit and $IterationLimit"""
    check_evaluation_as_in_cli(str_expr, str_expected, fail_msg, msgs)


@pytest.mark.skipif(
    sys.platform.startswith("win"),
    reason="Weird Block recursion test does not work on MS Windows",
)
@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        # FIX Later
        (
            "ClearAll[f];f[x_, 0] := x; f[x_, n_] := Module[{y = x + 1}, f[y, n - 1]];Block[{$IterationLimit = 20}, f[0, 100]]",
            None,
            "100",
            "Fix me!",
        ),
    ],
)
def test_evaluation_non_mswindows(str_expr, msgs, str_expected, fail_msg):
    """These tests check the behavior of $RecursionLimit and $IterationLimit
    that do not work on MS Windows.
    """
    check_evaluation_as_in_cli(str_expr, str_expected, fail_msg, msgs)


def test_python_recursion_error_is_reclim():
    """When Python runs out of stack before $RecursionLimit is reached, the
    evaluation is aborted with the $RecursionLimit message, not a crash."""
    from test.helper import session

    python_limit = sys.getrecursionlimit()
    try:
        session.evaluate("$RecursionLimit = 512")
        sys.setrecursionlimit(3000)
        result = session.evaluate_as_in_cli(
            "ClearAll[deep]; deep[n_] := 1 + deep[n + 1]; deep[1]"
        )
        assert result.result == "$Aborted"
        assert [m.text for m in result.out] == ["Recursion depth of 512 exceeded."]
    finally:
        sys.setrecursionlimit(python_limit)
        session.evaluate("ClearAll[deep]; $RecursionLimit = 200")
