# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.assignments.assignment
"""

from test.helper import check_evaluation


def test_upset():
    """
    Test UpSet[] builtin
    """
    check_evaluation(
        "a ^= 3",
        "a ^= 3",
        failure_message="Should not be able to use UpSet on a Symbol",
        expected_messages=("Nonatomic expression expected at position 1 in a ^= 3.",),
    )
    check_evaluation(
        "f[g, a + b, h] ^= 2",
        "2",
        failure_message="UpSet on a protected value should fail",
        expected_messages=("Tag Plus in f[g, a + b, h] is Protected.",),
    )
    check_evaluation("UpValues[h]", "{HoldPattern[f[g, a + b, h]] :> 2}")


def test_order():
    check_evaluation(None, None)
    check_evaluation(
        "f[___]:=1;f[_,_]:=2; f[1,2]", "2", "f[_,_] must have priority over f[___]"
    )
