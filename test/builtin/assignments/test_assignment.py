# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.assignments.assignment
"""
from test.helper import check_evaluation

import pytest


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


@pytest.mark.parametrize(
    ["expr", "expect", "fail_msg", "expected_msgs"],
    [
        (None, None, None, None),
        # Trivial cases on protected symbols
        (
            "List:=1;",
            None,
            "assign to protected element",
            ("Symbol List is Protected.",),
        ),
        (
            "HoldPattern[List]:=1;",
            None,
            "assign to wrapped protected element",
            ("Tag List in HoldPattern[List] is Protected.",),
        ),
        (
            "PatternTest[List, x]:=1;",
            None,
            "assign to wrapped protected element",
            ("Tag List in List ? x is Protected.",),
        ),
        (
            "Condition[List, x]:=1;",
            None,
            "assign to wrapped protected element",
            ("Tag List in List /; x is Protected.",),
        ),
        # Behavior with symbols in the LHS
        ("ClearAll[A,T];A=T; T=2; {A, T}", "{2, 2}", "Assignment to symbols", None),
        (
            "ClearAll[A,T];A=T; A=2; Clear[A]; A=3; {A, T}",
            "{3, T}",
            "Assignment to symbols. Rewrite value.",
            None,
        ),
        (
            "ClearAll[A,T];A=T; A[x_]=x^2; {A[u], T[u]}",
            "{u^2, u^2}",
            "Assignment to symbols.",
            None,
        ),
        (
            "ClearAll[A,T];A=T; A[x_]=x^2; ClearAll[A];  {A[u], T[u]}",
            "{A[u], u^2}",
            (
                "Rules are associated to T, not A, "
                "because the LHS is evaluated before the assignment."
            ),
            None,
        ),
        (
            "ClearAll[A, T];  A=T; HoldPattern[A[x_]]=x^2;  {A[u], T[u]}",
            "{T[u], T[u]}",
            "Hold Pattern prevents the evaluation of the LHS. The ownvalue comes first...",
            None,
        ),
        (
            "ClearAll[A, T];  A=T; HoldPattern[A[x_]]=x^2; A=.;  {A[u], T[u]}",
            "{u^2, T[u]}",
            "Hold Pattern prevents the evaluation of the LHS. Removing the ownvalue.",
            None,
        ),
        # HoldPattern on the LHS
        (
            "ClearAll[A,T];A=T; HoldPattern[T]=2; {2, 2}",
            "{2, 2}",
            "Assignment to symbols",
            None,
        ),
        (
            "ClearAll[A,T];A=T; HoldPattern[A]=2; {2, T}",
            "{2, T}",
            "Assignment to symbols. Rewrite value.",
            None,
        ),
        (
            "ClearAll[A,T];A=T; HoldPattern[A[x_]]:=x^2; {A[u], T[u]}",
            "{T[u], T[u]}",
            "Assignment to symbols.",
            None,
        ),
        (
            "ClearAll[A,T];A=T; HoldPattern[A][x_]:=x^2; {A[u], T[u]}",
            "{T[u], T[u]}",
            "Assignment to symbols.",
            None,
        ),
        (
            "ClearAll[A,T];A=T; HoldPattern[A[x_]]:=x^2;A=.; {A[u], T[u]}",
            "{u ^ 2, T[u]}",
            "Once the downvalue of A is gone, the rule applies...",
            None,
        ),
        # In this case, we erase all the rules associated to A:
        (
            "ClearAll[A, T]; A=T; HoldPattern[A[x_]]:=x^2; ClearAll[A];  {A[u], T[u]}",
            "{A[u], T[u]}",
            "Head and elements on the LHS are evaluated before the assignment.",
            None,
        ),
        (
            "ClearAll[A,T];A=T; HoldPattern[HoldPattern[A[x_]]]:=x^2;A=.; {A[u], T[u]}",
            "{u ^ 2, T[u]}",
            "Nested HoldPattern",
            None,
        ),
        # Conditions on the LHS
        (
            "ClearAll[A,T,x];A=T;x=3; Condition[T,x>2]=2; {2, 2}",
            "{2, 2}",
            "Assignment to symbols",
            None,
        ),
        (
            "ClearAll[A,T,x];A=T;x=3; Condition[A, x>2]=2; {2, T}",
            "{2, T}",
            "Assignment to symbols. Rewrite value.",
            None,
        ),
        (
            "ClearAll[A,T,x];A=T;x=3; Condition[A[x_],x>2]:=x^2; {A[u], T[u], A[4], T[4]}",
            "{A[u], T[u], 16, 16}",
            "Assignment to symbols.",
            None,
        ),
        (
            "ClearAll[A,T,x];A=T;x=3; Condition[A[x_],x>2]:=x^2;A=.; {A[u], T[u], A[4], T[4]}",
            "{A[u], T[u], A[4], 16}",
            "Assignment to symbols.",
            None,
        ),
        (
            "ClearAll[A,T,x];A=T;x=3; Condition[A[x_],x>2]:=x^2; ClearAll[A];  {A[u], T[u]}",
            "{A[u], u^2}",
            "Head and elements on the LHS are evaluated before the assignment.",
            None,
        ),
        (
            "ClearAll[A, T];  A=T; HoldPattern[A[x_]]:=x^2;  {A[u], T[u]}",
            "{T[u], T[u]}",
            "Hold Pattern prevents the evaluation of the LHS.",
            None,
        ),
        (
            "ClearAll[A, T];  A=T; HoldPattern[A[x_]]:=x^2;A=.;  {A[u], T[u]}",
            "{u^2, T[u]}",
            "Hold Pattern prevents the evaluation of the LHS.",
            None,
        ),
        # Format
        (
            'ClearAll[A,T,x]; Format[A[x_]]:={x,"a"}; A[2]//ToString',
            '"{2, a}"',
            None,
            None,
        ),
        (
            'ClearAll[A,T,x]; A=T; Format[A[x_]]:={x,"a"}; T[2]//ToString',
            '"{2, a}"',
            "Define the format for T",
            None,
        ),
        (
            'ClearAll[A,T,x]; A=T; Format[A[x_]]:={x,"a"}; A=.;A[2]//ToString',
            '"A[2]"',
            "but not for A",
            None,
        ),
        # Now, using HoldPattern
        (
            'ClearAll[A,T,x]; A=T; Format[HoldPattern[A][x_]]:={x,"a"}; T[2]//ToString',
            '"T[2]"',
            ("Define the format for A, " "because the HoldPattern. Do not affect T"),
            None,
        ),
        (
            'ClearAll[A,T,x]; A=T; Format[HoldPattern[A][x_]]:={x,"a"}; A[2]//ToString',
            '"T[2]"',
            "but A evals to T befor format...",
            None,
        ),
        (
            'ClearAll[A,T,x]; A=T; Format[HoldPattern[A][x_]]:={x,"a"}; A=.; A[2]//ToString',
            '"{2, a}"',
            "Now A do not eval to T...",
            None,
        ),
        (
            'ClearAll[A,T,x]; A=T; HoldPattern[Format[A[x_]]]:={x,"a"}; A=.; A[2]//ToString',
            '"{2, a}"',
            "The same that put HoldPattern inside format...",
            None,
        ),
        # Conditionals
        (
            'ClearAll[A,T,x]; A=T; Format[Condition[A[x_],x>0]]:={x,"a"}; A=.; A[2]//ToString',
            '"A[2]"',
            "store the conditional rule for T...",
            None,
        ),
        (
            'ClearAll[A,T,x]; A=T; Format[Condition[A[x_],x>0]]:={x,"a"}; A=.; T[2]//ToString',
            '"{2, a}"',
            "store the conditional rule for T...",
            None,
        ),
        # Upvalues
        (
            "ClearAll[F,A,Y,x]; A=T; F[A[x_],Y[x_]]^:=x^2; ClearAll[A,F,Y]; F[T[2],Y[2]]",
            "4",
            "the rule is still stored in T.",
            None,
        ),
        (
            "ClearAll[F,A,Y,x]; A=T; F[HoldPattern[A[x_]],Y[x_]]^:=x^2; ClearAll[A,F,Y]; F[T[2],Y[2]]",
            "F[T[2],Y[2]]",
            "the rule is still stored in T.",
            None,
        ),
        (
            "ClearAll[F,A,Y,x]; A=T; F[HoldPattern[A[x_]],Y[x_]]^:=x^2; ClearAll[A,F]; F[A[2],Y[2]]",
            "4",
            "the rule is still stored in Y.",
            None,
        ),
        (
            "ClearAll[F,A,Y,x]; A=T; F[{a,b,c},Y[x_]]^:=x^2; ClearAll[A,F]; F[{a,b,c},Y[2]]",
            "4",
            "There is a warning, because a rule cannot be associated to List, but it is stored on Y.",
            ("Tag List in F[{a, b, c}, Y[x_]] is Protected.",),
        ),
    ],
)
# @pytest.mark.xfail
def test_assignment(expr, expect, fail_msg, expected_msgs):
    check_evaluation(
        expr, expect, failure_message=fail_msg, expected_messages=expected_msgs
    )
