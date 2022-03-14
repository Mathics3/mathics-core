# -*- coding: utf-8 -*-
import pytest
from .helper import check_evaluation, reset_session, session
from mathics_scanner.errors import IncompleteSyntaxError


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
            "F[a,b]",
            "F[a,b]",
            None,
        ),
        (
            "G[a,b]=1",
            "1",
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
        (
            None,
            None,
            None,
        ),
    ],
)
def test_set_and_clear(str_expr, str_expected, msg):
    if str_expr is None:
        reset_session()
        return
    result = session.evaluate(str_expr, "")
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        message=msg,
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "out_msgs", "msg"),
    [
        (None, None, None, None),
        (
            "A=1; B=2; Clear[A, $Context, B];{A,$Context,B}",
            '{A, "Global`",B}',
            ("Special symbol $Context cannot be cleared.",),
            "This clears A and B, but not $Context",
        ),
        (
            "A=1; B=2; ClearAll[A, $Context, B];{A,$Context,B}",
            '{A, "Global`",B}',
            ("Special symbol $Context cannot be cleared.",),
            "This clears A and B, but not $Context",
        ),
        (
            "A=1; B=2; ClearAll[A, $ContextPath, B];{A,$ContextPath,B}",
            '{A, {"Global`", "System`"},B}',
            ("Special symbol $ContextPath cannot be cleared.",),
            "This clears A and B, but not $ContextPath",
        ),
        (
            "A=1; B=2; ClearAll[A, $ContextPath, B];{A,$ContextPath,B}",
            '{A, {"Global`", "System`"},B}',
            ("Special symbol $ContextPath cannot be cleared.",),
            "This clears A and B, but not $ContextPath",
        ),
    ],
)
def test_set_and_clear_messages(str_expr, str_expected, out_msgs, msg):
    if str_expr is None:
        reset_session()
        return
    else:
        session.evaluate("ClearAll[a, b, A, B, F, H, Q]")
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        message=msg,
        msgs=out_msgs,
    )
