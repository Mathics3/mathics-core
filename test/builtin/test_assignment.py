# -*- coding: utf-8 -*-
import os
from test.helper import check_evaluation, session

import pytest
from mathics_scanner.errors import IncompleteSyntaxError

DEBUGASSIGN = int(os.environ.get("DEBUGSET", "0")) == 1

if DEBUGASSIGN:
    skip_or_fail = pytest.mark.xfail
else:
    skip_or_fail = pytest.mark.skip


str_test_set_with_oneidentity = """
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
    for line in str_test_set_with_oneidentity.split("\n"):
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
            "F[x_]:=G[x]; H[F[y_]]^:=Q[y]; ClearAll[G]; {H[G[5]],H[F[5]]}",
            "{H[G[5]], H[G[5]]}",
            "The arguments on the LHS are evaluated before the assignment",
        ),
        (None, None, None),
        (
            (
                "A[x_]:=B[x];B[x_]:=F[x_];F[x_]:=G[x];"
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
    ],
)
@skip_or_fail
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


def test_predecrement():
    check_evaluation(
        "--5", "4", failure_message="Set::setraw: Cannot assign to raw object 5."
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
                expected_messages=[
                    f"Cannot set {limit} to 2; value must be an integer between 20 and {suffix}."
                ],
            )
        check_evaluation(f"{prefix}$ModuleNumber = 3", "3")
        check_evaluation(
            f"{prefix}$ModuleNumber = -1",
            "-1",
            expected_messages=[
                "Cannot set $ModuleNumber to -1; value must be a positive integer."
            ],
        )
