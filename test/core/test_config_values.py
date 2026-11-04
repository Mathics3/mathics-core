# -*- coding: utf-8 -*-
"""
$RecursionLimit and $IterationLimit are looked up by their full names at
each evaluation step, not resolved through $Context and $ContextPath.
"""

import pytest

from mathics.core.interrupt import AbortInterrupt

from test.helper import check_evaluation, session


def test_limits_do_not_resolve_names(monkeypatch):
    definitions = session.definitions
    looked_up = []
    original = definitions.lookup_name

    def recording(name):
        if name in ("$RecursionLimit", "$IterationLimit"):
            looked_up.append(name)
        return original(name)

    monkeypatch.setattr(definitions, "lookup_name", recording)
    session.evaluate("Do[cvF[i], {i, 50}]")
    assert looked_up == []


def test_other_recursion_limit_symbol_is_not_the_limit():
    # A symbol $RecursionLimit in another context is not the limit.
    check_evaluation(
        "Global`$RecursionLimit = 30; cvR[0] = 0; cvR[n_] := cvR[n - 1] + 1; cvR[100]",
        "100",
    )
    session.evaluate("Remove[Global`$RecursionLimit]; ClearAll[cvR]")


@pytest.mark.parametrize(
    "str_expr",
    [
        "cvR[0] = 0; cvR[n_] := cvR[n - 1] + 1; Block[{$RecursionLimit = 40}, cvR[100]]",
        "Block[{$IterationLimit = 20}, cvK := cvK + 1; cvK]",
    ],
)
def test_limits_still_apply(str_expr):
    with pytest.raises(AbortInterrupt):
        session.evaluate(str_expr)
    session.evaluate("ClearAll[cvR, cvK]")
