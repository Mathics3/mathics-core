# -*- coding: utf-8 -*-
"""
Empty sequences, as in WMA: a Sequence[] kept as an element (SequenceHold,
HoldComplete) is one element, matched by _; Set[x] assigns Sequence[].
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("MatchQ[HoldComplete[Sequence[]], HoldComplete[_]]", "True"),
        ("MatchQ[HoldComplete[1, Sequence[]], HoldComplete[_, _]]", "True"),
        ("MatchQ[HoldComplete[1, Sequence[]], HoldComplete[_]]", "False"),
        ("MatchQ[HoldComplete[1, Sequence[2, 3]], HoldComplete[_, _]]", "True"),
        # Set has SequenceHold: the value can be an empty sequence.
        ("hsX = Sequence[]; hsF[hsX, 1]", "hsF[1]"),
        ("Block[{hsY}, hsY = Sequence[]; hsF[hsY, 1]]", "hsF[1]"),
        # As in Combinatorica's ShowGraphArray, a function's empty options
        # kept in a variable.
        (
            "hsG[o___] := Block[{n}, n = o; hsF[n, 1]]; {hsG[], hsG[a -> 1]}",
            "{hsF[1], hsF[a -> 1, 1]}",
        ),
        (
            "SetAttributes[hsH, SequenceHold]; hsH[a_, b_] := {a, Hold[b]}; hsH[1, Sequence[]]",
            "{1, Hold[]}",
        ),
        # Set and SetDelayed with no value, or several: a Sequence, as in WMA.
        ("Set[hsA]; OwnValues[hsA]", "{HoldPattern[hsA] :> Sequence[]}"),
        ("Set[hsB, x, y]; OwnValues[hsB]", "{HoldPattern[hsB] :> Sequence[x, y]}"),
        ("SetDelayed[hsC]; OwnValues[hsC]", "{HoldPattern[hsC] :> Sequence[]}"),
        ("hsK[o___] := (hsN = o; {hsN}); {hsK[], hsK[a, b]}", "{{}, {a, b}}"),
        ("hsQ = 5", "5"),
        # A _ still does not match zero elements of an expression.
        ("MatchQ[hsF[], hsF[_]]", "False"),
        ("MatchQ[hsF[1], hsF[_, _]]", "False"),
        ("hsF[1, 2, 3] /. hsF[x___, y_, z_] :> {{x}, y, z}", "{{1}, 2, 3}"),
        (
            "ReplaceList[hsF[a, b], hsF[x___, y_, z___] :> {{x}, y, {z}}]",
            "{{{}, a, {b}}, {{a}, b, {}}}",
        ),
        ("ClearAll[hsX, hsF, hsG, hsH, hsA, hsB, hsC, hsK, hsN, hsQ]", "Null"),
    ],
)
def test_held_empty_sequence(str_expr, str_expected):
    check_evaluation(str_expr, str_expected)
