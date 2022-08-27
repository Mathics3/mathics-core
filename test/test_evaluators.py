# -*- coding: utf-8 -*-

import pytest

from mathics.session import MathicsSession
from mathics.core.evaluators import eval_N, eval_nvalues

session = MathicsSession()
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
        ("2/9", "$MachinePrecision", "2.000000`5*9.0000000000`5^(-1.`)"),
        ("Pi", "$MachinePrecision", "3.141592653589793`15"),
        ("F[1.2, 2/9]", "$MachinePrecision", "F[1.2, .2222222222222222]"),
        ("F[1.2, 2/9]", "$MachinePrecision", "F[1.2, .2222222222222222`15]"),
        # It is  necessary to have 17 digits to get SameQ against N[2/9,5]
        # ("F[1.2`3, 2/9]", "5", "F[1.20`3, .22222232818603515`15]"),
        ("F[1.2`3, 2/9]", "5", "F[1.20`3, .222222`5]"),
        ("F[1.2`3, 2/9]", "5", "F[1.20`3, .222222]"),
        ("a=1.2`3;F[a, 2/9]", "5", "F[1.20`3, .222222]"),
        # In WMA, N[b]=1.2`3 should assign a NValue rule to N[b, $MachinePrecision]
        ("N[b]=1.2`3;F[b, 2/9]", "5", "F[b, .222222]"),
        ("N[b,_]=1.2`3;F[b, 2/9]", "5", "F[1.20`3, .222222]"),
    ],
)
def test_eval_N(str_expr, prec, str_expected):
    expr_in = session.evaluate(f"Hold[{str_expr}]").elements[0]
    prec = session.evaluate(prec)
    expr_expected = session.evaluate(str_expected)
    result = eval_N(expr_in, evaluation, prec=prec)
    assert expr_expected.sameQ(result)


@pytest.mark.parametrize(
    "str_expr, prec, str_expected, setup",
    [
        ("1", "$MachinePrecision", "1.000000000", None),
        # eval_nvalues does not call  `evaluate` over the input expression. So
        # 2/9 is not evaluated to a Rational number, but kept as a division.
        ("2/9", "$MachinePrecision", "2.000000`5*9.0000000000`5^(-1.`)", None),
        # eval_nvalues does not call  `evaluate` at the end neither. So
        # Sqrt[2]->Sqrt[2.0`]
        ("Sqrt[2]", "$MachinePrecision", "Sqrt[2.0`]", None),
        ("Pi", "$MachinePrecision", "3.141592653589793`15", None),
        (
            "F[1.2, 2/9]",
            "$MachinePrecision",
            "F[1.2, 2.000000`5*9.0000000000`5^(-1.`)]",
            None,
        ),
        # Here 2/9 -> 2./9.
        ("F[1.2`3, 2/9]", "5", "F[1.20`3, 2.`5*9.`5^(-1.`)]", None),
        # Here, since the input expression is not evaluated, `a` remains unevaluated.
        ("F[a, 2/9]", "5", "F[a, 2.000000`5*9.0000000000`5^(-1.`)]", "a=1.2`3;"),
        ("F[b, 2/9]", "5", "F[1.20`3, 2.*9.^(-1.`)]", "N[b,_]=1.2`3"),
    ],
)
def test_eval_nvalues(str_expr, prec, str_expected, setup):
    if setup:
        session.evaluate(setup)
    expr_in = session.evaluate(f"Hold[{str_expr}]").elements[0]
    prec = session.evaluate(prec)
    expr_expected = session.evaluate(f"Hold[{str_expected}]").elements[0]
    result = eval_nvalues(expr_in, prec, evaluation)
    session.evaluate("ClearAll[a,b,c]")
    assert expr_expected.sameQ(result)


@pytest.mark.parametrize(
    "str_expr, str_expected, setup",
    [
        ("1", "1", None),
        ("{1, 1.}", "{1, 1.}", None),
        ("{1.000123`6, 1.0001`4, 2/9}", "{1.000123`6, 1.0001`4, .22222`4}", None),
        ("F[1.000123`6, 1.0001`4, 2/9]", "F[1.000123`6, 1.0001`4, .22222`4]", None),
        # eval_nvalues does not call  `evaluate` over the input expression. So
        # 2/9 is not evaluated to a Rational number, but kept as a division.
        ("2/9", "2 * 9 ^ (-1)", None),
        ("Sqrt[2]", "Sqrt[2]", None),
        ("Pi", "Pi", None),
        ("F[1.3, 2/9]", "F[1.3, 0.2222222222222222]", None),
        # Here 2/9 -> .22222232818603515`15
        ("F[1.2`3, 2/9]", "F[1.20`3, .2222`3]", None),
        # Here, since the input expression is not evaluated, `a` remains unevaluated.
        ("F[a, 2/9]", "F[a, 2 *9 ^ (-1)]", "a=1.2`3;"),
        # Here b is not evaluated
        ("F[b, 2/9]", "F[b, 2 *9 ^ (-1)]", "N[b,_]=1.2`3"),
    ],
)
def test_numerify(str_expr, str_expected, setup):
    if setup:
        session.evaluate(setup)
    expr_in = session.evaluate(f"Hold[{str_expr}]").elements[0]
    expr_expected = session.evaluate(f"Hold[{str_expected}]").elements[0]
    result = numerify(expr_in, evaluation)
    session.evaluate("ClearAll[a,b,c]")
    assert expr_expected.sameQ(result)
