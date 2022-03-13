# -*- coding: utf-8 -*-
import pytest

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
            "{F[a, b],  F[x__]:=H[x]; F[a,b], F=.; F[a,b]}",
            "{F[a, b], H[a, b], H[a, b]}",
            None,
        ),
        (
            "{F[a, b],  F[x__]:=H[x]; F[a,b], F[x__]=.; F[a,b]}",
            "{F[a, b], H[a, b], F[a, b]}",
            None,
        ),
        # Check over a builtin operator
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
            "{a+b, Unprotect[Plus]; Plus=Q; a+b, Plus=.; a+b}",
            "{a + b, Q[a, b], a + b}",
            None,
        ),
    ],
)
def test_set_and_clear(str_expr, str_expected, msg):
    session.evaluate("ClearAll[{H, Pi, F, Q, Plus}]")
    result = session.evaluate(str_expr, "")
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        message=msg,
    )
    session.evaluate("ClearAll[a]")
    session.evaluate("ClearAll[b]")
    session.evaluate("ClearAll[F]")
    session.evaluate("ClearAll[H]")
    session.evaluate("ClearAll[Q]")
    session.evaluate("ClearAll[Plus]")
    session.evaluate("ClearAll[Pi]")


# For some reason, using helper.check_evaluation leaves some
# garbage that affects other tests.

import time
from mathics.session import MathicsSession

session = MathicsSession(add_builtin=True, catch_interrupt=False)


def evaluate_value(str_expr: str):
    return session.evaluate(str_expr).value


def evaluate(str_expr: str):
    return session.evaluate(str_expr)


def check_evaluation(
    str_expr: str,
    str_expected: str,
    message="",
    to_string_expr=True,
    to_string_expected=True,
    to_python_expected=False,
):
    """Helper function to test Mathics expression against
    its results"""
    if to_string_expr:
        str_expr = f"ToString[{str_expr}]"
        result = evaluate_value(str_expr)
    else:
        result = evaluate(str_expr)

    if to_string_expected:
        str_expected = f"ToString[{str_expected}]"
        expected = evaluate_value(str_expected)
    else:
        expected = evaluate(str_expr)
        if to_python_expected:
            expected = expected.to_python(string_quotes=False)

    print(time.asctime())
    if message:
        print((result, expected))
        assert result == expected, message
    else:
        print((result, expected))
        assert result == expected
