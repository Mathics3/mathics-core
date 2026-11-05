# -*- coding: utf-8 -*-
"""
Evaluation should leave no reference cycles behind: the garbage it
makes should be freed by reference counting, without the cyclic
garbage collector. Each case below used to leave cycles.
"""

import gc
from test.helper import session

import pytest


def unreachable_after(expr: str) -> int:
    """The number of objects only the cyclic garbage collector frees
    after evaluating ``expr``."""
    # A first evaluation may build caches and definitions that stay.
    session.evaluate(expr)
    gc.collect()
    enabled = gc.isenabled()
    gc.disable()
    try:
        session.evaluate(expr)
        return gc.collect()
    finally:
        if enabled:
            gc.enable()


@pytest.mark.parametrize(
    ("expr",),
    [
        # Sort keys of general expressions (GeneralVariable).
        ("Sort[{f[x] a, g[y], h[z]^2, 3 f[x], k[1] k[2]}];",),
        # Patterns of Symbols (SymbolPattern).
        ("MatchQ[{a, b}, {a, _}];",),
        # Orderless matching with repeated names (subsets, pre-choices).
        ("ReplaceList[p[a, b, a, b], p[x__, x__] -> {x}];",),
        (
            "SetAttributes[q, Orderless]; ReplaceList[q[a, b, a, c], q[x_, x_, y___] -> {x, y}];",
        ),
        ("ReplaceList[a + b + c + d, x_ + y__ -> {x, y}];",),
    ],
)
def test_no_reference_cycles(expr):
    assert unreachable_after(expr) == 0
