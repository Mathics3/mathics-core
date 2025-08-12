# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.assignments.assignment

Tests here check the compatibility of
the  default behavior of the different assignment operators
with WMA.
"""
# TODO: consider to split this module in sub-modules.

from test.helper import check_evaluation, session

import pytest
from mathics_scanner.errors import IncompleteSyntaxError


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


STR_TEST_SET_WITH_ONE_IDENTITY = """
SetAttributes[SUNIndex, {OneIdentity}];
SetAttributes[SUNFIndex, {OneIdentity}];

SUNIndex[SUNFIndex[___]]:=
	(Print["This error shouldn't be triggered here!"];
	Abort[]);

SUNFIndex[SUNIndex[___]]:=
	(Print["This error shouldn't be triggered here!"];
	Abort[]);

SUNIndex /: MakeBoxes[SUNIndex[p_], TraditionalForm]:=ToBoxes[p, TraditionalForm];

SUNFIndex /: MakeBoxes[SUNFIndex[p_], TraditionalForm]:=ToBoxes[p, TraditionalForm];
"""


def test_setdelayed_oneidentity():
    """
    This test checks the behavior of DelayedSet over
    symbols with the attribute OneIdentity.
    """
    expr = ""
    for line in STR_TEST_SET_WITH_ONE_IDENTITY.split("\n"):
        if line in ("", "\n"):
            continue
        expr = expr + line
        try:
            check_evaluation(
                expr, "Null", to_string_expr=False, to_string_expected=False
            )
            expr = ""
        except IncompleteSyntaxError:
            continue


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            None,
            None,
            None,
        ),
        ("Attributes[Pi]", "{Constant, Protected, ReadProtected}", None),
        ("Unprotect[Pi]; Pi=.; Attributes[Pi]", "{Constant, ReadProtected}", None),
        ("Unprotect[Pi];Clear[Pi]; Attributes[Pi]", "{Constant, ReadProtected}", None),
        ("Unprotect[Pi];ClearAll[Pi]; Attributes[Pi]", "{}", None),
        ("Options[Expand]", "{Modulus :> 0, Trig :> False}", None),
        (
            "Unprotect[Expand]; Expand=.; Options[Expand]",
            "{Modulus :> 0, Trig :> False}",
            None,
        ),
        (
            "Clear[Expand];Options[Expand]=Join[Options[Expand], {MyOption:>Automatic}]; Options[Expand]",
            "{MyOption :> Automatic, Modulus :> 0, Trig :> False}",
            "Mathics stores options in a dictionary. This is why ``MyOption`` appears first.",
        ),
        # (
        #    "ClearAll[Expand]; Options[Expand]",
        #    "{}",
        #    "In WMA, options are erased, including the builtin options",
        # ),
        (None, None, None),
        # Check over a builtin symbol
        (
            "{Pi,  Unprotect[Pi];Pi=3;Pi, Clear[Pi];Pi}",
            "{Pi, 3, Pi}",
            None,
        ),
        (
            "{Pi,  Unprotect[Pi];Pi=3;Pi, ClearAll[Pi];Pi}",
            "{Pi, 3, Pi}",
            None,
        ),
        (
            "{Pi,  Unprotect[Pi];Pi=3;Pi, Pi = .; Pi}",
            "{Pi, 3, Pi}",
            None,
        ),
        # Check over a user defined symbol
        (
            "{F[a, b],  F=Q; F[a,b], Clear[F]; F[a,b]}",
            "{F[a, b], Q[a, b], F[a, b]}",
            None,
        ),
        (
            "{F[a, b],  F=Q; F[a,b], ClearAll[F]; F[a,b]}",
            "{F[a, b], Q[a, b], F[a, b]}",
            None,
        ),
        (
            "{F[a, b],  F=Q; F[a,b], F=.; F[a,b]}",
            "{F[a, b], Q[a, b], F[a, b]}",
            None,
        ),
        # Check over a user defined symbol
        (
            "{F[a, b],  F[x__]:=H[x]; F[a,b], Clear[F]; F[a,b]}",
            "{F[a, b], H[a, b], F[a, b]}",
            None,
        ),
        (
            "{F[a, b],  F[x__]:=H[x]; F[a,b], ClearAll[F]; F[a,b]}",
            "{F[a, b], H[a, b], F[a, b]}",
            None,
        ),
        (
            None,
            None,
            None,
        ),
        (
            "{F[a, b],  F[x__]:=H[x]; F[a,b], F=.; F[a,b]}",
            "{F[a, b], H[a, b], H[a, b]}",
            None,
        ),
        (
            None,
            None,
            None,
        ),
        (
            "{F[a, b],  F[x__]:=H[x]; F[a,b], F[x__]=.; F[a,b]}",
            "{F[a, b], H[a, b], F[a, b]}",
            None,
        ),
        # Check over a builtin operator
        (
            "{a+b, Unprotect[Plus]; Plus=Q; a+b, Plus=.; a+b}",
            "{a + b, Q[a, b], a + b}",
            None,
        ),
        (
            "{a+b, Unprotect[Plus]; Plus=Q; a+b, Clear[Plus]; a+b}",
            "{a + b, Q[a, b], a + b}",
            None,
        ),
        (
            "{a+b, Unprotect[Plus]; Plus=Q; a+b, ClearAll[Plus]; a+b}",
            "{a + b, Q[a, b], a + b}",
            None,
        ),
        (None, None, None),
        (r"a=b; a=4; {a, b}", "{4, b}", None),
        (None, None, None),
        (r"a=b; b=4;  {a,b}", "{4, 4}", None),
        (None, None, None),
        (r"a=b; b=4; Clear[a]; {a,b}", "{a, 4}", None),
        (None, None, None),
        ("a=b; b=4; Clear[b]; {a, b}", "{b, b}", None),
        (None, None, None),
        ("F[x_]:=x^2; G[x_]:=F[x]; ClearAll[F]; G[u]", "F[u]", None),
        (None, None, None),
        ("F[x_]:=G[x]; G[x_]:=x^2; ClearAll[G]; F[u]", "G[u]", None),
        (None, None, None),
        (
            "F[x_]:=G[x]; H[F[y_]]:=Q[y]; ClearAll[F]; {H[G[5]],H[F[5]]}",
            "{Q[5], H[F[5]]}",
            "Arguments on the LHS are evaluated before the assignment in := after F reset",
        ),
        (None, None, None),
        (
            "F[x_]:=G[x]; H[F[y_]]^:=Q[y]; ClearAll[F]; {H[G[5]],H[F[5]]}",
            "{Q[5], H[F[5]]}",
            "Arguments on the LHS are evaluated before the assignment in ^:= after F reset",
        ),
        (None, None, None),
        (
            "F[x_]:=G[x]; H[F[y_]]:=Q[y]; ClearAll[G]; {H[G[5]],H[F[5]]}",
            "{Q[5], Q[5]}",
            "The arguments on the LHS are evaluated before the assignment in := after G reset",
        ),
        (None, None, None),
        (
            "F[x_]:=G[x]; H[F[y_]]^:=Q[y]; ClearAll[G]; {H[G[5]],H[F[5]]}",
            "{H[G[5]], H[G[5]]}",
            "The arguments on the LHS are evaluated before the assignment in ^:= after G reset",
        ),
        (None, None, None),
        (
            (
                "A[x_]:=B[x];B[x_]:=F[x];F[x_]:=G[x];"
                "H[A[y_]]:=Q[y]; ClearAll[F];"
                "{H[A[5]],H[B[5]],H[F[5]],H[G[5]]}"
            ),
            "{H[F[5]], H[F[5]], H[F[5]], Q[5]}",
            "The arguments on the LHS are completely evaluated before the assignment",
        ),
        (None, None, None),
        (
            "F[x_]:=G[x];N[F[x_]]:=x^2;ClearAll[F];{N[F[2]],N[G[2]]}",
            "{F[2.], 4.}",
            "Assign N rule",
        ),
        (
            None,
            None,
            None,
        ),
    ],
)
def test_set_and_clear(str_expr, str_expected, msg):
    """
    Test calls to Set, Clear and ClearAll. If
    str_expr is None, the session is reset,
    in a way that the next test run over a fresh
    environment.
    """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (None, None, None),
        (r"a=b; a=4; {a, b}", "{4, b}", None),
        (None, None, None),
        (r"a=b; b=4;  {a,b}", "{4, 4}", None),
        (None, None, None),
        (r"a=b; b=4; Clear[a]; {a,b}", "{a, 4}", None),
        (None, None, None),
        ("a=b; b=4; Clear[b]; {a, b}", "{b, b}", None),
        (None, None, None),
        ("F[x_]:=x^2; G[x_]:=F[x]; ClearAll[F]; G[u]", "F[u]", None),
        (None, None, None),
        ("F[x_]:=G[x]; G[x_]:=x^2; ClearAll[G]; F[u]", "G[u]", None),
        (None, None, None),
        (
            "F[x_]:=G[x]; H[F[y_]]:=Q[y]; ClearAll[F]; {H[G[5]],H[F[5]]}",
            "{Q[5], H[F[5]]}",
            "The arguments on the LHS are evaluated before the assignment",
        ),
        (None, None, None),
        (
            "F[x_]:=G[x]; H[F[y_]]^:=Q[y]; ClearAll[F]; {H[G[5]],H[F[5]]}",
            "{Q[5], H[F[5]]}",
            "The arguments on the LHS are evaluated before the assignment",
        ),
        (None, None, None),
        (
            "F[x_]:=G[x]; H[F[y_]]:=Q[y]; ClearAll[G]; {H[G[5]],H[F[5]]}",
            "{Q[5], Q[5]}",
            "The arguments on the LHS are evaluated before the assignment",
        ),
        (None, None, None),
        (
            "F[x_]=G[x]; H[F[y_]]^=Q[y]; ClearAll[G]; {H[G[5]],H[F[5]]}",
            "{H[G[5]], H[G[5]]}",
            "The arguments on the LHS are evaluated before the assignment",
        ),
        (None, None, None),
        (
            (
                "A[x_]=B[x];B[x_]=F[x];F[x_]=G[x];"
                "H[A[y_]]=Q[y]; ClearAll[F];"
                "{H[A[5]],H[B[5]],H[F[5]],H[G[5]]}"
            ),
            "{H[F[5]], H[F[5]], H[F[5]], Q[5]}",
            "The arguments on the LHS are completely evaluated before the assignment",
        ),
        (None, None, None),
        (
            "F[x_]=G[x];N[F[x_]]=x^2;ClearAll[F];{N[F[2]],N[G[2]]}",
            "{F[2.], 4.}",
            "Assign N rule",
        ),
    ],
)
def test_set_and_clear_to_fix(str_expr, str_expected, msg):
    """
    Test calls to Set, Clear and ClearAll. If
    str_expr is None, the session is reset,
    in a way that the next test run over a fresh
    environment.
    """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "message", "out_msgs"),
    [
        ("Pi=4", "4", "Trying to set a protected symbol", ("Symbol Pi is Protected.",)),
        (
            "Clear[Pi]",
            "Null",
            "Trying to clear a protected symbol",
            ("Symbol Pi is Protected.",),
        ),
        (
            "Unprotect[$ContextPath];Clear[$Context]",
            "Null",
            "Trying clear $Context",
            ("Special symbol $Context cannot be cleared.",),
        ),
        (
            "Unprotect[$ContextPath];Clear[$ContextPath]",
            "Null",
            "Trying clear $ContextPath",
            ("Special symbol $ContextPath cannot be cleared.",),
        ),
        (
            "A=1; B=2; Clear[A, $Context, B];{A,$Context,B}",
            "{A, Global`, B}",
            "This clears A and B, but not $Context",
            ("Special symbol $Context cannot be cleared.",),
        ),
        (
            "A=1; B=2; ClearAll[A, $Context, B];{A,$Context,B}",
            "{A, Global`, B}",
            "This clears A and B, but not $Context",
            ("Special symbol $Context cannot be cleared.",),
        ),
        (
            "A=1; B=2; ClearAll[A, $ContextPath, B];{A,$ContextPath,B}",
            "{A, {System`, Global`}, B}",
            "This clears A and B, but not $ContextPath",
            ("Special symbol $ContextPath cannot be cleared.",),
        ),
        (
            "A=1; B=2; ClearAll[A, $ContextPath, B];{A,$ContextPath,B}",
            "{A, {System`, Global`}, B}",
            "This clears A and B, but not $ContextPath",
            ("Special symbol $ContextPath cannot be cleared.",),
        ),
        # `This test was in mathics.builtin.arithmetic.Sum`. It is clear that it does not
        # belongs there. On the other hand, this is something to check at the level of the interpreter,
        # and is not related with Sum, or Set.
        # ("a=Sum[x^k*Sum[y^l,{l,0,4}],{k,0,4}]]", "None" , "syntax error",
        # ('"a=Sum[x^k*Sum[y^l,{l,0,4}],{k,0,4}]" cannot be followed by "]" (line 1 of "<test>").',))
    ],
)
def test_set_and_clear_messages(str_expr, str_expected, message, out_msgs):
    session.evaluate("ClearAll[a, b, A, B, F, H, Q]")
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=message,
        expected_messages=out_msgs,
    )


def test_assign_list():
    check_evaluation("G[x_Real]=x^2; a={G[x]}; {x=1.; a, x=.; a}", "{{1.}, {G[x]}}")


def test_process_assign_other():
    # FIXME: beef up check_evaluation so it allows regexps in matching.
    # Then this code would be less fragile.
    for prefix in ("", "System`"):
        for kind, suffix in (
            (
                "Recursion",
                "512; use the MATHICS_MAX_RECURSION_DEPTH environment variable to allow higher limits",
            ),
            ("Iteration", "Infinity"),
        ):
            limit = f"${kind}Limit"
            check_evaluation(f"{prefix}{limit} = 511", "511")
            check_evaluation(
                f"{prefix}{limit} = 2",
                "2",
                expected_messages=(
                    f"Cannot set {limit} to 2; value must be an integer between 20 and {suffix}.",
                ),
            )
        check_evaluation(f"{prefix}$ModuleNumber = 3", "3")
        check_evaluation(
            f"{prefix}$ModuleNumber = -1",
            "-1",
            expected_messages=(
                "Cannot set $ModuleNumber to -1; value must be a positive integer.",
            ),
        )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msgs", "failure_msg"),
    [
        (None, None, None, None),
        # From Clear
        ("x = 2;OwnValues[x]=.;x", "x", None, "Erase Ownvalues"),
        ("f[a][b] = 3; SubValues[f] =.;f[a][b]", "f[a][b]", None, "Erase Subvalues"),
        ("PrimeQ[p] ^= True; PrimeQ[p]", "True", None, "Subvalues"),
        ("UpValues[p]=.; PrimeQ[p]", "False", None, "Erase Subvalues"),
        ("a + b ^= 5; a =.; a + b", "5", None, None),
        ("{UpValues[a], UpValues[b]} =.; a+b", "a+b", None, None),
        (
            "Unset[Messages[1]]",
            "$Failed",
            [
                "First argument in Messages[1] is not a symbol or a string naming a symbol."
            ],
            "Unset Message",
        ),
        (" g[a+b] ^:= 2", "$Failed", ("Tag Plus in g[a + b] is Protected.",), None),
        (" g[a+b]", "g[a + b]", None, None),
    ],
)
def test_private_doctests(str_expr, str_expected, msgs, failure_msg):
    check_evaluation(
        str_expr, str_expected, expected_messages=msgs, failure_message=failure_msg
    )


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
            "{A[u], T[u]}",
            (
                "Head and elements on the LHS are evaluated before the assignment, but noticing that "
                "Condition has the attribute `HoldRest`..."
            ),
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
def test_assignment(expr, expect, fail_msg, expected_msgs):
    check_evaluation(
        expr, expect, failure_message=fail_msg, expected_messages=expected_msgs
    )


# Regression check of some assignment issues encountered.
@pytest.mark.parametrize(
    ["expr", "expect", "fail_msg", "hold_expected"],
    [
        (
            None,
            "Issue #1425 - Erroneous Protected message seen in SetDelayed loading Rubi.",
            None,
            False,
        ),
        (
            "ClearAll[A,x]; f[A_, x_] := x /; x == 2; DownValues[f] // FullForm",
            "{RuleDelayed[HoldPattern[f[Pattern[A, Blank[]], Pattern[x, Blank[]]]], Condition[x, Equal[x, 2]]]}",
            "Issue #1209 - Another problem seen in loading Rubi.",
            True,
        ),
    ],
)
def test_regression_of_assignment_issues(expr, expect, fail_msg, hold_expected):
    check_evaluation(
        expr, expect, failure_message=fail_msg, hold_expected=hold_expected
    )
