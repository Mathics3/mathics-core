# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.attributes.
"""

from test.helper import check_evaluation, check_evaluation_as_in_cli

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        (None, None, None),
        # F has the attribute, but G doesn't.
        ("SetAttributes[F, OneIdentity]", "Null", None),
        ("SetAttributes[r, Flat]", "Null", None),
        ("SetAttributes[s, Flat]", "Null", None),
        ("SetAttributes[s, OneIdentity]", "Null", None),
        ("MatchQ[x, F[y_]]", "False", "With OneIdentity"),
        ("MatchQ[x, G[y_]]", "False", "Without OneIdentity"),
        ("MatchQ[x, F[x_:0,y_]]", "True", "With OneIdentity, and Default"),
        ("MatchQ[x, G[x_:0,y_]]", "False", "Without OneIdentity, and Default"),
        ("MatchQ[F[x], F[x_:0,y_]]", "True", "With OneIdentity, and Default"),
        ("MatchQ[G[x], G[x_:0,y_]]", "True", "Without OneIdentity, and Default"),
        ("MatchQ[F[F[F[x]]], F[x_:0,y_]]", "True", "With OneIdentity, nested"),
        ("MatchQ[G[G[G[x]]], G[x_:0,y_]]", "True", "Without OneIdentity, nested"),
        ("MatchQ[F[3, F[F[x]]], F[x_:0,y_]]", "True", "With OneIdentity, nested"),
        ("MatchQ[G[3, G[G[x]]], G[x_:0,y_]]", "True", "Without OneIdentity, nested"),
        (
            "MatchQ[x, F[x1_:0, F[x2_:0,y_]]]",
            "True",
            "With OneIdentity, pattern nested",
        ),
        (
            "MatchQ[x, G[x1_:0, G[x2_:0,y_]]]",
            "False",
            "With OneIdentity, pattern nested",
        ),
        (
            "MatchQ[x, F[x1___:0, F[x2_:0,y_]]]",
            "True",
            "With OneIdentity, pattern nested",
        ),
        (
            "MatchQ[x, G[x1___:0, G[x2_:0,y_]]]",
            "False",
            "With OneIdentity, pattern nested",
        ),
        ("MatchQ[x, F[F[x2_:0,y_],x1_:0]]", "True", "With OneIdentity, pattern nested"),
        (
            "MatchQ[x, G[G[x2_:0,y_],x1_:0]]",
            "False",
            "With OneIdentity, pattern nested",
        ),
        ("MatchQ[x, F[x_.,y_]]", "False", "With OneIdentity, and Optional, no default"),
        (
            "MatchQ[x, G[x_.,y_]]",
            "False",
            "Without OneIdentity, and Optional, no default",
        ),
        ("Default[F, 1]=1.", "1.", None),
        ("Default[G, 1]=2.", "2.", None),
        ("MatchQ[x, F[x_.,y_]]", "True", "With OneIdentity, and Optional, default"),
        ("MatchQ[x, G[x_.,y_]]", "False", "Without OneIdentity, and Optional, default"),
        ("MatchQ[F[F[H[y]]],F[x_:0,u_H]]", "False", None),
        ("MatchQ[G[G[H[y]]],G[x_:0,u_H]]", "False", None),
        ("MatchQ[F[p, F[p, H[y]]],F[x_:0,u_H]]", "False", None),
        ("MatchQ[G[p, G[p, H[y]]],G[x_:0,u_H]]", "False", None),
        (None, None, None),
    ],
)
def test_one_identity(str_expr, str_expected, msg):
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
        # F is OneIdentity, r is Flat and s is both:
        (
            (
                "SetAttributes[F, OneIdentity];"
                "SetAttributes[r, Flat];"
                "SetAttributes[s, {Flat, OneIdentity}];"
            ),
            "Null",
            None,
        ),
        # Replace also takes into account the OneIdentity attribute,
        # and also modifies the interpretation of the Flat attribute.
        (
            "F[a,b,b,c]/.F[x_,x_]->Fp[x]",
            "F[a, b, b, c]",
            "https://reference.wolfram.com/language/tutorial/Patterns.html",
        ),
        # When fixed, Add the difference between the next two as a
        # doctest example.
        (
            "r[a,b,b,c]/.r[x_,x_]->rp[x]",
            "r[a, rp[r[b]], c]",
            "https://reference.wolfram.com/language/tutorial/Patterns.html",
        ),
        (
            "s[a,b,b,c]/.s[x_,x_]->sp[x]",
            "s[a, rp[b], c]",
            "https://reference.wolfram.com/language/tutorial/Patterns.html",
        ),
        (None, None, None),
    ],
)
@pytest.mark.xfail(reason="Flat attribute in rules is not fully supported.")
def test_one_identity_still_failing(str_expr, str_expected, msg):
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
        # F has the attribute, but G doesn't.
        ("SetAttributes[F, OneIdentity]", "Null", None),
        ("SetAttributes[r, Flat]", "Null", None),
        ("SetAttributes[s, Flat]", "Null", None),
        ("SetAttributes[s, OneIdentity]", "Null", None),
        ("MatchQ[x, F[y_]]", "False", "With OneIdentity"),
        ("MatchQ[x, G[y_]]", "False", "Without OneIdentity"),
        ("MatchQ[x, F[x_:0,y_]]", "True", "With OneIdentity, and Default"),
        ("MatchQ[x, G[x_:0,y_]]", "False", "Without OneIdentity, and Default"),
        ("MatchQ[F[x], F[x_:0,y_]]", "True", "With OneIdentity, and Default"),
        ("MatchQ[G[x], G[x_:0,y_]]", "True", "Without OneIdentity, and Default"),
        ("MatchQ[F[F[F[x]]], F[x_:0,y_]]", "True", "With OneIdentity, nested"),
        ("MatchQ[G[G[G[x]]], G[x_:0,y_]]", "True", "Without OneIdentity, nested"),
        ("MatchQ[F[3, F[F[x]]], F[x_:0,y_]]", "True", "With OneIdentity, nested"),
        ("MatchQ[G[3, G[G[x]]], G[x_:0,y_]]", "True", "Without OneIdentity, nested"),
        (
            "MatchQ[x, F[x1_:0, F[x2_:0,y_]]]",
            "True",
            "With OneIdentity, pattern nested",
        ),
        (
            "MatchQ[x, G[x1_:0, G[x2_:0,y_]]]",
            "False",
            "With OneIdentity, pattern nested",
        ),
        (
            "MatchQ[x, F[x1___:0, F[x2_:0,y_]]]",
            "True",
            "With OneIdentity, pattern nested",
        ),
        (
            "MatchQ[x, G[x1___:0, G[x2_:0,y_]]]",
            "False",
            "With OneIdentity, pattern nested",
        ),
        ("MatchQ[x, F[F[x2_:0,y_],x1_:0]]", "True", "With OneIdentity, pattern nested"),
        (
            "MatchQ[x, G[G[x2_:0,y_],x1_:0]]",
            "False",
            "With OneIdentity, pattern nested",
        ),
        ("MatchQ[x, F[x_.,y_]]", "False", "With OneIdentity, and Optional, no default"),
        (
            "MatchQ[x, G[x_.,y_]]",
            "False",
            "Without OneIdentity, and Optional, no default",
        ),
        ("Default[F, 1]=1.", "1.", None),
        ("Default[G, 1]=2.", "2.", None),
        ("MatchQ[x, F[x_.,y_]]", "True", "With OneIdentity, and Optional, default"),
        ("MatchQ[x, G[x_.,y_]]", "False", "Without OneIdentity, and Optional, default"),
        ("MatchQ[F[F[H[y]]],F[x_:0,u_H]]", "False", None),
        ("MatchQ[G[G[H[y]]],G[x_:0,u_H]]", "False", None),
        ("MatchQ[F[p, F[p, H[y]]],F[x_:0,u_H]]", "False", None),
        ("MatchQ[G[p, G[p, H[y]]],G[x_:0,u_H]]", "False", None),
        (None, None, None),
    ],
)
def test_one_identity_stil_failing(str_expr, str_expected, msg):
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=msg,
    )


@pytest.mark.parametrize(
    ("str_expr", "arg_count"),
    [
        ("SetAttributes[F]", 1),
        ("SetAttributes[]", 0),
        ("SetAttributes[F, F, F]", 3),
    ],
)
def test_Attributes_wrong_args(str_expr, arg_count):
    what_expected = "argument" if arg_count == 1 else "arguments"
    check_evaluation(
        str_expr=str_expr,
        str_expected=str_expr,
        failure_message=f"Arg count mismatch test with {arg_count} args",
        hold_expected=True,
        to_string_expr=True,
        to_string_expected=True,
        expected_messages=(
            f"SetAttributes called with {arg_count} {what_expected}; 2 arguments are expected.",
        ),
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "assert_failure_msg"),
    [
        ("CleanAll[u];CleanAll[v];", None, None, None),
        ("SetAttributes[{u, v}, Flat];u[x_] := {x};u[]", None, "u[]", None),
        ("u[a]", None, "{a}", None),
        ("v[x_] := x;v[]", None, "v[]", None),
        ("v[a]", None, "a", None),
        (
            "Block[{$IterationLimit = 40}, v[a, b]]",
            None,
            "v[a, b]",
            "Test $IterationLimit catches unbounded expansion",
        ),
        ("CleanAll[u];CleanAll[v];", None, None, None),
    ],
)
def test_attributes(str_expr, msgs, str_expected, assert_failure_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=assert_failure_msg,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "assert_failure_msg"),
    [
        ("CleanAll[u];CleanAll[v];", None, None, None),
        (
            "Block[{$IterationLimit=30}, SetAttributes[{u, v}, Flat];u[x_] := {x};u[a, b]]",
            ("Iteration limit of 30 exceeded.",),
            "$Aborted",
            "Test $IterationLimit catches unbounded expansion using SetDelayed, test 1.",
        ),
        (
            "Block[{$IterationLimit=20}, u[a, b, c]]",
            ("Iteration limit of 20 exceeded.",),
            "$Aborted",
            "Test $IterationLimit catches unbounded expansion in function call.",
        ),
        (
            "Block[{$IterationLimit=20}, v[x_] := x;v[a,b,c]]",
            ("Iteration limit of 20 exceeded.",),
            "$Aborted",
            "Test $IterationLimit catches unbounded expansion using SetDelayed, test 2.",
        ),
        ("CleanAll[u];CleanAll[v];", None, None, None),
    ],
)
def test_IterationLimit(str_expr, msgs, str_expected, assert_failure_msg):
    """Check the behavior of $RecursionLimit and $IterationLimit"""
    check_evaluation_as_in_cli(str_expr, str_expected, assert_failure_msg, msgs)


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "assert_failure_msg"),
    [
        (
            None,
            None,
            None,
            None,
        ),  # Reset
        (
            'SetAttributes[{F, "H", G},{Flat, HoldFirst}]',
            ("Argument H at position 1 is expected to be a symbol.",),
            None,
            "Undefined Symbols by name makes the call fail ",
        ),
        (
            'Attributes[{F, "H", "G"}]',
            ("Argument H at position 1 is expected to be a symbol.",),
            "{{Flat, HoldFirst}, Attributes[H], {Flat, HoldFirst}}",
            "SetAttributes acted on F and G, but not in H, which is still undefined. Notice that now, `G` is defined due to the previous command.",
        ),
        (
            'ClearAttributes[{F, "H", "G"},Flat]; Attributes[{F, G}]',
            ("Argument H at position 1 is expected to be a symbol.",),
            "{{HoldFirst}, {HoldFirst}}",
            "ClearAttibutes acted on F and G, but not in H",
        ),
        (
            'H=1;SetAttributes[{"A+B", "Q", "H"},{Flat, HoldFirst}]; Attributes["H"]',
            (
                "Argument A+B at position 1 is expected to be a symbol.",
                "Argument Q at position 1 is expected to be a symbol.",
            ),
            "{Flat, HoldFirst}",
            "SetAttributes: Wrong symbol name (has an operator inside) and undefined operator.",
        ),
        (
            'Attributes[{"A+B", "Q", H}]',
            (
                "Argument A+B at position 1 is expected to be a symbol.",
                "Argument Q at position 1 is expected to be a symbol.",
            ),
            "{Attributes[A+B], Attributes[Q], {Flat, HoldFirst}}",
            "Attributes: Wrong symbol name (has an operator inside) and undefined operator.",
        ),
        (
            'ClearAttributes[{"A+B", "Q", H},{HoldFirst}]; Attributes[H]',
            (
                "Argument A+B at position 1 is expected to be a symbol.",
                "Argument Q at position 1 is expected to be a symbol.",
            ),
            "{Flat}",
            "ClearAttributes on wrong symbol name.",
        ),
        (
            "Attributes[HoldPattern[A]]=Flat",
            None,
            "Flat",
            "Set strips `HoldPattern` around symbols.",
        ),
        (
            'Attributes[HoldPattern["A"]]=Flat',
            (
                "First argument in Attributes[A] is not a symbol or a string naming a symbol.",
            ),
            "Flat",
            "Set does not strip `HoldPattern` around strings.",
        ),
        (
            "Attributes[HoldPattern[A]]=.",
            None,
            None,
            "Unset strips `HoldPattern` around symbols.",
        ),
        (
            'Attributes[HoldPattern["A"]]=.',
            (
                "First argument in Attributes[A] is not a symbol or a string naming a symbol.",
            ),
            "$Failed",
            "Unset does not strip `HoldPattern` around strings.",
        ),
        (
            "Attributes[{A, B}]=.",
            (
                (
                    "First argument in Attributes[{A, B}] "
                    "is not a symbol or a string naming a symbol."
                ),
            ),
            "$Failed",
            "Unset on expressions fails with fnsym message",
        ),
        (
            'Attributes["undefinedsymbol"]=.',
            ("Symbol undefinedsymbol not found.",),
            "$Failed",
            "Unset on undefined symbols fails with notfound message",
        ),
        (
            'Attributes["F"]=.',
            None,
            None,
            (
                "Unset on strings representing "
                "already defined symbols works without output"
            ),
        ),
        (
            "Attributes[G]=.",
            None,
            None,
            "Unset on already defined symbols works without output",
        ),
    ],
)
def test_set_and_clear_attributes(str_expr, msgs, str_expected, assert_failure_msg):
    check_evaluation_as_in_cli(str_expr, str_expected, assert_failure_msg, msgs)
