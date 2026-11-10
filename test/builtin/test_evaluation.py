# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.evaluation.
"""

import sys
from test.helper import check_evaluation_as_in_cli

import pytest

from mathics.core import evaluation as core_evaluation


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
        ("$RecursionLimit = 1024", None, "1024", None),
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
            ("Recursion depth of 100000 exceeded.",),
            "$Aborted",
            "Infinity goes as deep as the Python stack is set up for, then stops",
        ),
        (
            "ClearAll[f]; f[0] = 0; f[n_] := 1 + f[n - 1]; Block[{$RecursionLimit = Infinity}, f[2000]]",
            None,
            "2000",
            "Infinity is not bounded by the largest integer $RecursionLimit",
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
        # Release, the obsolete form of Evaluate
        ("x = 1 + 1; Release[x]", None, "2", None),
        (
            "With[{name = h}, f[Release[name][k_]] := {name, k}]; f[h[3]]",
            None,
            "{h, 3}",
            "Release in the left-hand side of a definition",
        ),
        # a = a + a above is left defined otherwise, and the next test file
        # in the same worker that uses a hits the recursion limit
        ("ClearAll[a, f, h, x];", None, None, None),
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
        session.evaluate("ClearAll[deep]; $RecursionLimit = 1024")


def test_session_reset_restores_python_recursion_limit():
    """Resetting a session gives the default $RecursionLimit back, and with it
    the Python recursion limit that goes with it."""
    from test.helper import reset_session, session

    from mathics.core.evaluation import python_recursion_depth

    default_limit = session.evaluate("$RecursionLimit").value
    session.evaluate("$RecursionLimit = 100")
    assert sys.getrecursionlimit() == python_recursion_depth(100)
    reset_session()
    assert session.evaluate("$RecursionLimit").value == default_limit
    assert sys.getrecursionlimit() == python_recursion_depth(default_limit)


@pytest.mark.parametrize(
    "str_expr",
    [
        "Do[k^2, {k, 10^7}]",
        "Table[Timing[Length[Range[2000 i]]; ], {i, 3000}];",
    ],
)
def test_evaluate_timeout(str_expr):
    """The timeout given to evaluate stops the evaluation between two steps,
    with $Aborted and General::timeout, not with a Python exception."""
    from test.helper import session

    result = session.evaluate_as_in_cli(str_expr, timeout=0.3)
    assert result.result == "$Aborted"
    assert [m.text for m in result.out] == ["Timeout reached."]
    # The next evaluation has no limit left over.
    assert session.evaluate_as_in_cli("Length[Table[i, {i, 10}]]").result == "10"


def test_infinite_recursion_limit(monkeypatch):
    """$RecursionLimit = Infinity goes as deep as MAX_INFINITE_RECURSION_DEPTH,
    then stops, and the message gives the limit in effect inside the Block."""
    monkeypatch.setattr(core_evaluation, "MAX_INFINITE_RECURSION_DEPTH", 1000)
    check_evaluation_as_in_cli(
        "ClearAll[f]; f[n_] := 1 + f[n + 1]; Block[{$RecursionLimit = Infinity}, f[0]]",
        "$Aborted",
        "Infinity goes as deep as the stack is set up for, then stops",
        ("Recursion depth of 1000 exceeded.",),
    )
    check_evaluation_as_in_cli("ClearAll[f];")


def test_recursion_error_reports_limit_in_effect(monkeypatch):
    """A RecursionError from Python is reported with the $RecursionLimit in
    effect where it happened, not the one restored after leaving the Block."""
    from mathics.core.evaluation import Evaluation

    original = Evaluation.inc_recursion_depth

    def inc_recursion_depth(self):
        original(self)
        if self.recursion_depth > 600:
            raise RecursionError

    monkeypatch.setattr(Evaluation, "inc_recursion_depth", inc_recursion_depth)
    check_evaluation_as_in_cli(
        "ClearAll[f]; f[n_] := 1 + f[n + 1]; Block[{$RecursionLimit = Infinity}, f[0]]",
        "$Aborted",
        None,
        (
            "Recursion depth of %d exceeded."
            % core_evaluation.MAX_INFINITE_RECURSION_DEPTH,
        ),
    )
    check_evaluation_as_in_cli("ClearAll[f];")


@pytest.mark.skipif(
    not core_evaluation.USE_EVALUATION_THREAD,
    reason="evaluations run on the calling thread on this platform",
)
def test_evaluation_runs_on_a_thread_with_a_large_stack(monkeypatch):
    """Evaluation.evaluate() runs the evaluation on a thread whose stack is
    sized for the deepest recursion allowed, and hands back its result and
    its exceptions."""
    import threading

    from mathics.session import MathicsSession

    seen = {}
    original = core_evaluation.Evaluation._evaluate

    def _evaluate(self, query, timeout=None, format=None):
        seen["thread"] = threading.current_thread()
        return original(self, query, timeout, format)

    monkeypatch.setattr(core_evaluation.Evaluation, "_evaluate", _evaluate)
    session = MathicsSession()
    assert session.evaluate_as_in_cli("1 + 1").result == "2"
    assert seen["thread"] is not threading.main_thread()
    assert getattr(seen["thread"], "mathics3_evaluation", False)
    # The stack size is set only while the thread is started.
    assert threading.stack_size() == 0

    def failing(self, query, timeout=None, format=None):
        raise SystemExit(7)

    monkeypatch.setattr(core_evaluation.Evaluation, "_evaluate", failing)
    with pytest.raises(SystemExit) as exc_info:
        session.evaluate_as_in_cli("1 + 1")
    assert exc_info.value.code == 7
