# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.procedural.
"""

from test.helper import (
    check_evaluation,
    check_evaluation_as_in_cli,
    check_wrong_number_of_arguments,
    session,
)

import pytest


# NestWhile tests
@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("NestWhile[#/2&, 10000, IntegerQ]", "625/2"),
        ("NestWhile[Total[IntegerDigits[#]^3] &, 5, UnsameQ, All]", "371"),
        ("NestWhile[Total[IntegerDigits[#]^3] &, 6, UnsameQ, All]", "153"),
    ],
)
def test_nestwhile(str_expr, str_expected):
    print(str_expr)
    print(session.evaluate(str_expr))
    check_evaluation(
        str_expr, str_expected, to_string_expr=True, to_string_expected=True
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("res=CompoundExpression[x, y, z]", None, "z", None),
        ("res", None, "z", "Issue 331"),
        ("z = Max[1, 1 + x]; x = 2; z", None, "3", "Issue 531"),
        ("Clear[x]; Clear[z]; Clear[res];", None, "Null", None),
        (
            'Do[Print["hi"],{1+1}]',
            (
                "hi",
                "hi",
            ),
            "Null",
            None,
        ),
        (
            "n := 1; For[i=1, i<=10, i=i+1, If[i > 5, Return[i]]; n = n * i]",
            None,
            "6",
            None,
        ),
        ("n", None, "120", "Side effect of the previous test"),
        ("h[x_] := (If[x < 0, Return[]]; x)", None, "Null", None),
        ("h[1]", None, "1", None),
        ("h[-1]", None, "Null", None),
        ("f[x_] := Return[x];g[y_] := Module[{}, z = f[y]; 2]", None, "Null", None),
        ("g[1]", None, "2", "Issue 513"),
        (
            "a; Switch[b, b]",
            (
                "Switch called with 2 arguments. Switch must be called with an odd number of arguments.",
            ),
            "Switch[b, b]",
            None,
        ),
        ## Issue 531
        (
            "z = Switch[b, b];",
            (
                "Switch called with 2 arguments. Switch must be called with an odd number of arguments.",
            ),
            "Null",
            "Issue 531",
        ),
        ("z", None, "Switch[b, b]", "Issue 531"),
        ("i = 1; While[True, If[i^2 > 100, Return[i + 1], i++]]", None, "12", None),
        # These tests check the result of a compound expression which finish with Null.
        # The result is different to the one obtained if we use the history (`%`)
        # which is test in `test_history_compound_expression`
        ("res=CompoundExpression[x, y, Null]", None, "Null", None),
        ("res", None, "Null", None),
        (
            "res=CompoundExpression[CompoundExpression[x, y, Null], Null]",
            None,
            "Null",
            None,
        ),
        ("res", None, "Null", None),
        ("res=CompoundExpression[x, Null, Null]", None, "Null", None),
        ("res", None, "Null", None),
        ("res=CompoundExpression[]", None, "Null", None),
        ("res", None, "Null", None),
        (
            "{MatchQ[Infinity,Infinity],Switch[Infinity,Infinity,True,_,False]}",
            None,
            "{True, True}",
            "Issue #956",
        ),
        (
            "Clear[f];Clear[g];Clear[h];Clear[i];Clear[n];Clear[res];Clear[z]; ",
            None,
            "Null",
            None,
        ),
    ],
)
def test_private_doctests_procedural(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


def test_history_compound_expression():
    """Test the effect in the history from the evaluation of a CompoundExpression"""
    check_evaluation_as_in_cli("Clear[x];Clear[y]")
    check_evaluation_as_in_cli("CompoundExpression[x, y, Null]")
    check_evaluation_as_in_cli("ToString[%]", "y")
    check_evaluation_as_in_cli(
        "CompoundExpression[CompoundExpression[y, x, Null], Null]"
    )
    check_evaluation_as_in_cli("ToString[%]", "x")
    check_evaluation_as_in_cli("CompoundExpression[x, y, Null, Null]")
    check_evaluation_as_in_cli("ToString[%]", "y")
    check_evaluation_as_in_cli("CompoundExpression[]")
    check_evaluation_as_in_cli("ToString[%]", "Null")
    check_evaluation_as_in_cli("Clear[x];Clear[y];")
    return

    def eval_expr(expr_str):
        query = session.evaluation.parse(expr_str)
        return session.evaluation.evaluate(query)

    eval_expr("Clear[x];Clear[y]")
    eval_expr("CompoundExpression[x, y, Null]")
    assert eval_expr("ToString[%]").result == "y"
    eval_expr("CompoundExpression[CompoundExpression[y, x, Null], Null])")
    assert eval_expr("ToString[%]").result == "x"
    eval_expr("CompoundExpression[x, y, Null, Null]")
    assert eval_expr("ToString[%]").result == "y"
    eval_expr("CompoundExpression[]")
    assert eval_expr("ToString[%]").result == "Null"
    eval_expr("Clear[x];Clear[y]")
    # Calling `session.evaluation.evaluate` ends by
    # set the flag `stopped` to `True`, which produces
    # a timeout exception if we evaluate an expression from
    # its `evaluate` method...
    session.evaluation.stopped = False


def test_wrong_number_of_arguments():
    tests = [
        # (
        #     "Abort[a, b]",
        #     ["Abort called with 2 arguments; 0 arguments are expected."],
        #     "Abort argument error call",
        # ),
        # (
        #     "Break[a, b, c]",
        #     ["Break called with 3 arguments; 0 arguments are expected."],
        #     "Break argument error call",
        # ),
        (
            "Catch[a, b, c, d, e]",
            ["Catch called with 5 arguments; between 1 and 3 arguments are expected."],
            "Catch argument error call",
        ),
        # (
        #     "Interrupt[a]",
        #     ["Interrupt called with 1 argument; 0 arguments are expected."],
        #     "Interrupt argument error call",
        # ),
        (
            "Throw[]",
            # Should be be between 1 and 3, but we don't have this implemented in Throw.
            ["Throw called with 0 arguments; 1 or 2 arguments are expected."],
            "Throw argument error call",
        ),
        (
            "While[a, b, c]",
            ["While called with 3 arguments; 1 or 2 arguments are expected."],
            "While argument error call",
        ),
    ]
    check_wrong_number_of_arguments(tests)
