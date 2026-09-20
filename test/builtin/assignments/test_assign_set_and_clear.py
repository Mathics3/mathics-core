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


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (
            None,
            None,
            None,
        ),  # Reset session
        ("Attributes[Pi]", "{Constant, Protected, ReadProtected}", None),
        ("Unprotect[Pi]; Pi=.; Attributes[Pi]", "{Constant, ReadProtected}", None),
        ("Unprotect[Pi];Clear[Pi]; Attributes[Pi]", "{Constant, ReadProtected}", None),
        ("Unprotect[Pi];ClearAll[Pi]; Attributes[Pi]", "{}", None),
        ("Options[Expand]", "{Modulus ⇾ 0, Trig ⇾ False}", None),
        (
            "Unprotect[Expand]; Expand=.; Options[Expand]",
            "{Modulus ⇾ 0, Trig ⇾ False}",
            None,
        ),
        (
            "Clear[Expand];Options[Expand]=Join[Options[Expand], {MyOption ⇾ Automatic}]; Options[Expand]",
            "{MyOption ⇾ Automatic, Modulus ⇾ 0, Trig ⇾ False}",
            "Mathics3 stores options in a dictionary. This is why ``MyOption`` appears first.",
        ),
        # (
        #    "ClearAll[Expand]; Options[Expand]",
        #    "{}",
        #    "In WMA, options are erased, including the builtin options",
        # ),
        (None, None, None),  # reset session
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
        # Check over a user defined symbol using Set
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
        # Check over a user defined symbol using SetDelayed
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
        (None, None, None),  # reset session
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
            "The arguments on the SetDelayed LHS are evaluated before the assignment in := after G reset",
        ),
        (None, None, None),
        (
            "F[x_]:=G[x]; H[F[y_]]^:=Q[y]; ClearAll[G]; {H[G[5]],H[F[5]]}",
            "{H[G[5]], H[G[5]]}",
            "The arguments on the UpSetDelayed LHS are evaluated before the assignment in ^:= after G reset",
        ),
        (None, None, None),
        (
            (
                "A[x_]:=B[x];B[x_]:=F[x];F[x_]:=G[x];"
                "H[A[y_]]:=Q[y]; ClearAll[F];"
                "{H[A[5]],H[B[5]],H[F[5]],H[G[5]]}"
            ),
            "{H[F[5]], H[F[5]], H[F[5]], Q[5]}",
            "The arguments on the SetDelayed LHS are completely evaluated before the assignment",
        ),
        (None, None, None),
        (
            (
                "A[x_]=B[x];B[x_]=F[x];F[x_]=G[x];"
                "H[A[y_]]=Q[y]; ClearAll[F];"
                "{H[A[5]],H[B[5]],H[F[5]],H[G[5]]}"
            ),
            "{H[F[5]], H[F[5]], H[F[5]], Q[5]}",
            "The arguments on the Set LHS are completely evaluated before the assignment",
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
            "Clearing $Context",
            ("Special symbol $Context cannot be cleared.",),
        ),
        (
            "Unprotect[$ContextPath];Clear[$ContextPath]",
            "Null",
            "Clearing $ContextPath",
            ("Special symbol $ContextPath cannot be cleared.",),
        ),
        (
            "A=1; B=2; Clear[A, $Context, B];{A,$Context,B}",
            "{A, Global`, B}",
            "This clears A and B via `Clear`, but not $Context",
            ("Special symbol $Context cannot be cleared.",),
        ),
        (
            "A=1; B=2; ClearAll[A, $Context, B];{A,$Context,B}",
            "{A, Global`, B}",
            "This clears A and B via `ClearAll`, but not $Context",
            ("Special symbol $Context cannot be cleared.",),
        ),
        (
            "A=1; B=2; Clear[A, $ContextPath, B];{A,$ContextPath,B}",
            "{A, {System`, Global`}, B}",
            "This clears A and B via `Clear`, but not $Context",
            ("Special symbol $ContextPath cannot be cleared.",),
        ),
        (
            "A=1; B=2; ClearAll[A, $ContextPath, B];{A,$ContextPath,B}",
            "{A, {System`, Global`}, B}",
            "This clears A and B via `ClearAll`, but not $ContextPath",
            ("Special symbol $ContextPath cannot be cleared.",),
        ),
        # `This test was in mathics.builtin.arithmetic.Sum`. It does not
        # belong there. On the other hand, this is something to check at the level of the interpreter,
        # and is not related to Sum or Set.
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
