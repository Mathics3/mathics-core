# -*- coding: utf-8 -*-
from .helper import evaluate, check_evaluation, session

import sys
import pytest

from mathics.session import MathicsSession
from mathics.core.evaluators import apply_N

evaluation = session.evaluation


def numerify(expr, evaluation):
    return expr.numerify(evaluation)


def test_sameQ():
    a = session.evaluate("1.")
    b = session.evaluate("1.`30")
    c = session.evaluate("1.`10")
    assert a.sameQ(b)
    assert a.sameQ(c)
    assert b.sameQ(c)
    assert b.sameQ(a)
    assert c.sameQ(a)
    assert c.sameQ(b)


@pytest.mark.parametrize(
    "str_expr, prec, str_expected",
    [
        ("1", "$MachinePrecision", "1.000000000"),
        ("Sqrt[2]", "$MachinePrecision", "1.41421356237310"),
        ("2/9", "$MachinePrecision", ".2222222222222222`15"),
        ("Pi", "$MachinePrecision", "3.141592653589793`15"),
        ("F[1.2, 2/9]", "$MachinePrecision", "F[1.2, .2222222222222222`15]"),
        # It is  necessary to have 17 digits to get SameQ against N[2/9,5]
        ("F[1.2`3, 2/9]", "5", "F[1.20`3, .22222232818603515`15]"),
        ("a=1.2`3;F[a, 2/9]", "5", "F[1.20`3, .22222232818603515`15]"),
        # In WMA, N[b]=1.2`3 should assign a NValue rule to N[b, $MachinePrecision]
        ("N[b]=1.2`3;F[b, 2/9]", "5", "F[b, .22222232818603515`15]"),
        ("N[b,_]=1.2`3;F[b, 2/9]", "5", "F[1.20`3, .22222232818603515`15]"),
    ],
)
def test_apply_N(str_expr, prec, str_expected):
    expr_in = session.evaluate(f"Hold[{str_expr}]").leaves[0]
    prec = session.evaluate(prec)
    expr_expected = session.evaluate(str_expected)
    result = apply_N(expr_in, evaluation, prec=prec)
    if not expr_expected.sameQ(result):
        print([expr_expected, result])
        for leaf1, leaf2 in zip(expr_expected.leaves, result.leaves):

            print(
                [
                    leaf1.value - leaf2.value,
                    leaf1.value,
                    leaf1.value._prec,
                    leaf2.value,
                    leaf2.value._prec,
                ]
            )

    assert expr_expected.sameQ(result)


@pytest.mark.parametrize(
    "str_expr,str_expected",
    [
        ("1", "1"),
        ("Sqrt[2]", "Sqrt[2]"),
        ("2/9", "2/9"),
        ("Pi", "Pi"),
        ("F[1.23`2, 2/9, g[2/9]]", "F[1.2, .22, g[2/9]]"),
        ("Global`F[1.23`2, 2/9, Cos[2/9]]", "Global`F[1.2`2, .22`2 , 0.98`2]"),
    ],
)
def _test_numerify(str_expr, str_expected):
    expr_in = session.evaluate(f"Hold[{str_expr}]").leaves[0]
    expr_expected = session.evaluate(str_expected)
    result = numerify(expr_in, session.evaluation)
    for leaf1, leaf2 in zip(result.leaves, expr_expected.leaves):
        print(
            leaf1.value - leaf2.value,
            (leaf1.value, leaf1.value._prec, type(leaf1)),
            (leaf2.value, leaf2.value._prec, type(leaf2)),
        )

    print("expected:", expr_expected)
    assert result.sameQ(expr_expected)
