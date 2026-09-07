# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.assignments.assignment

Tests here check the compatibility of
the  default behavior of the different assignment operators
with WMA.
"""
# TODO: consider splitting this module into sub-modules.

from test.helper import check_arg_counts, check_evaluation, session

import pytest
from mathics_scanner.errors import IncompleteSyntaxError


def test_order():
    check_evaluation(None, None)  # Reset session
    check_evaluation(
        "f[___]:=1;f[_,_]:=2; f[1,2]", "2", "f[_,_] must have priority over f[___]"
    )


def test_assign_list():
    check_evaluation("G[x_Real]=x^2; a={G[x]}; {x=1.; a, x=.; a}", "{{1.}, {G[x]}}")


@pytest.mark.parametrize(
    ["expr", "expect", "assert_msg"],
    [
        (None, None, None),  # reset session
        # Behavior with symbols in the LHS
        ("ClearAll[A,T];A=T; T=2; {A, T}", "{2, 2}", "Assignment to symbols"),
        (
            "ClearAll[A,T];A=T; A=2; Clear[A]; A=3; {A, T}",
            "{3, T}",
            "Assignment to symbols. Rewrite value.",
        ),
        (
            "ClearAll[A,T];A=T; A[x_]=x^2; {A[u], T[u]}",
            "{u^2, u^2}",
            "Assignment to symbols via Set.",
        ),
        (
            "ClearAll[A,T];A=T; A[x_]=x^2; ClearAll[A];  {A[u], T[u]}",
            "{A[u], u^2}",
            (
                "Rules are associated with T, not A, "
                "because the LHS is evaluated before the assignment."
            ),
        ),
        (
            "ClearAll[A, T];  A=T; HoldPattern[A[x_]]=x^2;  {A[u], T[u]}",
            "{T[u], T[u]}",
            "Hold Pattern prevents the evaluation of the LHS. The ownvalue comes first...",
        ),
        (
            "ClearAll[A, T];  A=T; HoldPattern[A[x_]]=x^2; A=.;  {A[u], T[u]}",
            "{u^2, T[u]}",
            "Hold Pattern prevents the evaluation of the LHS. Removing the ownvalue.",
        ),
        # HoldPattern on the LHS
        (
            "ClearAll[A,T];A=T; HoldPattern[T]=2; {2, 2}",
            "{2, 2}",
            "Assignment to symbols via Set and HoldPattern.",
        ),
        (
            "ClearAll[A,T];A=T; HoldPattern[A]=2; {2, T}",
            "{2, T}",
            "Assignment to symbols via HoldPattern. Rewrite value.",
        ),
        (
            "ClearAll[A,T];A=T; HoldPattern[A[x_]]:=x^2; {A[u], T[u]}",
            "{T[u], T[u]}",
            "Assignment to symbols via SetDelayed and HoldPattern.",
        ),
        (
            "ClearAll[A,T];A=T; HoldPattern[A[x_]]:=x^2;A=.; {A[u], T[u]}",
            "{u ^ 2, T[u]}",
            "Once the downvalue of A is gone, the rule applies...",
        ),
        # In this case, we erase all the rules associated to A:
        (
            "ClearAll[A, T]; A=T; HoldPattern[A[x_]]:=x^2; ClearAll[A];  {A[u], T[u]}",
            "{A[u], T[u]}",
            "Head and elements on the LHS are evaluated before the assignment.",
        ),
        (
            "ClearAll[A,T];A=T; HoldPattern[HoldPattern[A[x_]]]:=x^2;A=.; {A[u], T[u]}",
            "{u ^ 2, T[u]}",
            "Nested HoldPattern",
        ),
        # Conditions on the LHS
        (
            "ClearAll[A,T,x];A=T;x=3; Condition[T,x>2]=2; {2, 2}",
            "{2, 2}",
            "Assignment to symbols via Condition and Set.",
        ),
        (
            "ClearAll[A,T,x];A=T;x=3; Condition[A, x>2]=2; {2, T}",
            "{2, T}",
            "Assignment to symbols via Condition. Rewrite value.",
        ),
        (
            "ClearAll[A,T,x];A=T;x=3; Condition[A[x_],x>2]:=x^2; {A[u], T[u], A[4], T[4]}",
            "{A[u], T[u], 16, 16}",
            "Assignment to symbols via Condition and SetDelayed.",
        ),
        (
            "ClearAll[A,T,x];A=T;x=3; Condition[A[x_],x>2]:=x^2;A=.; {A[u], T[u], A[4], T[4]}",
            "{A[u], T[u], A[4], 16}",
            "Assignment to symbols via Condition, SetDelayed and Set.",
        ),
        (
            "ClearAll[A,T,x];A=T;x=3; Condition[A[x_],x>2]:=x^2; ClearAll[A];  {A[u], T[u]}",
            "{A[u], T[u]}",
            (
                "Head and elements on the LHS are evaluated before the assignment, but noticing that "
                "Condition has the attribute `HoldRest`..."
            ),
        ),
        (
            "ClearAll[A, T];  A=T; HoldPattern[A[x_]]:=x^2;  {A[u], T[u]}",
            "{T[u], T[u]}",
            "HoldPattern prevents the evaluation of the LHS.",
        ),
        (
            "ClearAll[A, T];  A=T; HoldPattern[A[x_]]:=x^2;A=.;  {A[u], T[u]}",
            "{u^2, T[u]}",
            "HoldPattern prevents the evaluation of the LHS, 2nd test.",
        ),
        # Format
        (
            'ClearAll[A,T,x]; Format[A[x_]]:={x,"a"}; A[2]//ToString',
            '"{2, a}"',
            None,
        ),
        (
            'ClearAll[A,T,x]; A=T; Format[A[x_]]:={x,"a"}; T[2]//ToString',
            '"{2, a}"',
            "Define the format for T",
        ),
        (
            'ClearAll[A,T,x]; A=T; Format[A[x_]]:={x,"a"}; A=.;A[2]//ToString',
            '"A[2]"',
            "Define the format for T, but not for A",
        ),
        # Now, using HoldPattern
        (
            'ClearAll[A,T,x]; A=T; Format[HoldPattern[A][x_]]:={x,"a"}; T[2]//ToString',
            '"T[2]"',
            ("Defines format for A because the HoldPattern does not affect T"),
        ),
        (
            'ClearAll[A,T,x]; A=T; Format[HoldPattern[A][x_]]:={x,"a"}; A[2]//ToString',
            '"T[2]"',
            "but A evals to T before format...",
        ),
        (
            'ClearAll[A,T,x]; A=T; Format[HoldPattern[A][x_]]:={x,"a"}; A=.; A[2]//ToString',
            '"{2, a}"',
            "Now A does not eval to T...",
        ),
        (
            'ClearAll[A,T,x]; A=T; HoldPattern[Format[A[x_]]]:={x,"a"}; A=.; A[2]//ToString',
            '"{2, a}"',
            "The same that put HoldPattern inside format...",
        ),
        # Conditionals
        (
            'ClearAll[A,T,x]; A=T; Format[Condition[A[x_],x>0]]:={x,"a"}; A=.; A[2]//ToString',
            '"A[2]"',
            "store the conditional rule for T...",
        ),
        (
            'ClearAll[A,T,x]; A=T; Format[Condition[A[x_],x>0]]:={x,"a"}; A=.; T[2]//ToString',
            '"{2, a}"',
            "store the conditional rule for T...",
        ),
        # Upvalues
        (
            "ClearAll[F,A,Y,x]; A=T; F[A[x_],Y[x_]]^:=x^2; ClearAll[A,F,Y]; F[T[2],Y[2]]",
            "4",
            "The rule should still be stored in T.",
        ),
        (
            "ClearAll[F,A,Y,x]; A=T; F[HoldPattern[A[x_]],Y[x_]]^:=x^2; ClearAll[A,F,Y]; F[T[2],Y[2]]",
            "F[T[2],Y[2]]",
            "The rule should still be stored in T using HoldPattern.",
        ),
        (
            "ClearAll[F,A,Y,x]; A=T; F[HoldPattern[A[x_]],Y[x_]]^:=x^2; ClearAll[A,F]; F[A[2],Y[2]]",
            "4",
            "The rule should still be stored in Y using HoldPattern.",
        ),
    ],
)
def test_assignment(expr, expect, assert_msg):
    check_evaluation(
        expr,
        expect,
        failure_message=assert_msg,
    )


# Regression check of some assignment issues encountered.
@pytest.mark.parametrize(
    ["expr", "expect", "assert_msg", "hold_expected", "messages"],
    [
        (
            None,
            None,
            "Issue #1425 - Erroneous Protected message seen in SetDelayed loading Rubi.",
            False,
            [],
        ),
        (
            "ClearAll[A,x]; f[A_, x_] := x /; x == 2; DownValues[f] // FullForm",
            "{RuleDelayed[HoldPattern[f[Pattern[A, Blank[]], Pattern[x, Blank[]]]], Condition[x, Equal[x, 2]]]}",
            "Issue #1209 - Another problem seen in loading Rubi.",
            True,
            [],
        ),
        (
            "ClearAll[F, Q];(F[x_] := s_) ^:= Q[x, s];F[1]:=2",
            "Q[1,2]",
            "Issue 1198 - Blanks are not tags.",
            False,
            [],
        ),
        (
            "ClearAll[F, Q];F[_Q,_]^:=1;{DownValues[F],UpValues[Q]}",
            "{{}, {HoldPattern[F[_Q, _]]⧴1}}",
            "Issue 1198 - Blanks are not tags.",
            False,
            [],
        ),
        (
            "ClearAll[F]; F[x_, opt:OptionsPattern[]]:=x^2;F[2]",
            "4",
            "ensure that Definition.options is a dict",
            False,
            [],
        ),
        (
            "ClearAll[F, Q];F[Verbatim[_Q],Verbatim[_]]^:=1;{DownValues[F],UpValues[Q]}",
            "{{}, {}}",
            "Issue 1198 - Blanks are not tags.",
            False,
            ["Tag Blank in F[Verbatim[_Q], Verbatim[_]] is Protected."],
        ),
    ],
)
def test_regression_of_assignment_issues(
    expr, expect, assert_msg, hold_expected, messages
):
    check_evaluation(
        expr,
        expect,
        failure_message=assert_msg,
        hold_expected=hold_expected,
        expected_messages=messages,
    )
