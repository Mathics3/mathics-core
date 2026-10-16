# -*- coding: utf-8 -*-
"""
Tests functions in mathics.core.definition
"""

import pytest

from mathics.core.definitions import determine_value_role
from mathics.core.parser import parse_builtin_rule
from mathics.core.pattern import BasePattern


def load_pattern_objects():
    """Ensure that pattern objects are already loaded"""
    from mathics.builtin.patterns import basic, composite, defaults, restrictions
    from mathics.core.builtin import PatternObject
    from mathics.core.pattern import pattern_objects

    pattern_modules = (
        basic,
        composite,
        defaults,
        restrictions,
    )

    if len(pattern_objects):
        return

    for module in pattern_modules:
        for name in dir(module):
            candidate = getattr(module, name)
            if name[0] == "_":
                continue
            try:
                if issubclass(candidate, PatternObject):
                    full_name = f"System`{name}"
                    pattern_objects[full_name] = candidate
            except TypeError:
                # Not a class
                continue


load_pattern_objects()


@pytest.mark.parametrize(
    ("pattern_str", "tag", "position"),
    [
        # None
        ("A", "B", None),
        ("A_", "B", None),
        ("A[c_]", "B", None),
        ("A[3]", "B", None),
        ("A[B][3]", "B", None),
        ("A[s[x_]][y]", "s", None),
        # Ownvalues
        ("A", "A", "ownvalues"),
        ("A/;A>0", "A", "ownvalues"),
        ("s:(A/;A>0)", "A", "ownvalues"),
        ("(s:A)/;A>0", "A", "ownvalues"),
        ("s:A/;A>0", "A", "ownvalues"),
        # Downvalues
        ("_A", "A", "downvalues"),
        ("A[]", "A", "downvalues"),
        ("_A", "A", "downvalues"),
        ("A[p_, q]", "A", "downvalues"),
        ("s:A[p_, q]", "A", "downvalues"),
        ("A[p_, q]/;q>0", "A", "downvalues"),
        ("(s:A[p_, q])/;q>0", "A", "downvalues"),
        # NValues
        ("N[A[x_], _]", "A", "nvalues"),
        ("N[A[x_], _]/; x>0", "A", "nvalues"),
        # Subvalues
        ("_A[]", "A", "subvalues"),
        ("A[x][t]", "A", "subvalues"),
        ("(s:A[x])[t]", "A", "subvalues"),
        ("(x_A/;u>0)[p]", "A", "subvalues"),
        # Upvalues
        ("S[x_, A]", "A", "upvalues"),
        ("S[x_, _A]", "A", "upvalues"),
        ("S[x_, s_A/;s>0]", "A", "upvalues"),
        ("S[x_, q:A]", "A", "upvalues"),
        ("S[x_, q:(A[t_]/;t>0)]", "A", "upvalues"),
        ("A[x_][s[y]]", "s", "upvalues"),
        ("N[_A,_]", "A", "nvalues"),
        ("N[A[_],_]", "A", "nvalues"),
        ("N[F[_A],_]", "A", None),
        ("DisplayForm[boxexpr_InterpretationBox]", "InterpretationBox", "upvalues"),
        (
            "ToExpression[boxexpr_InterpretationBox, form___]",
            "InterpretationBox",
            "upvalues",
        ),
        # Just one argument, must be an upvalue
        ("N[A[s_]]", "A", "upvalues"),
        # Verbatim
        ("Verbatim[F][Verbatim[G][x_]]", "F", "downvalues"),
        ("Verbatim[F,3][Verbatim[G][x_]]", "F", None),
        ("expr:Verbatim[F][Verbatim[G][x_]]", "F", "downvalues"),
        ("Verbatim[F][Verbatim[G][x_]]", "G", "upvalues"),
        ("Verbatim[F][expr:Verbatim[G][x_]]", "G", "upvalues"),
        ("Verbatim[N][Verbatim[G][x_]]", "N", "downvalues"),
        ("Verbatim[N][Verbatim[G][x_],_]", "N", "downvalues"),
        ("Verbatim[N][Verbatim[G][x_],_]", "G", "upvalues"),
        ("Verbatim[Condition][Verbatim[G][x_],_]", "Condition", "downvalues"),
        ("Verbatim[Condition][Verbatim[G][x_],_]", "G", "upvalues"),
        ("Verbatim[Verbatim][F[x_]]", "Verbatim", "downvalues"),
        # HoldPattern
        ("HoldPattern[F[Verbatim[G][x_]]]", "F", "downvalues"),
        ("expr:HoldPattern[F[Verbatim[G][x_]]]", "F", "downvalues"),
        ("HoldPattern[expr:F[Verbatim[G][x_]]]", "F", "downvalues"),
        ("HoldPattern[F][HoldPattern[G][x_]]", "G", "upvalues"),
        ("HoldPattern[F][HoldPattern[expr:G[x_]]]", "G", "upvalues"),
        ("HoldPattern[N[Verbatim[G][x_]]]", "N", "downvalues"),
        ("HoldPattern[N][Verbatim[G][x_],_]", "N", "downvalues"),
        ("Verbatim[N][HoldPattern[G][x_],_]", "G", "upvalues"),
        ("HoldPattern[Condition[Verbatim[G][x_],_]]", "Condition", None),
        ("HoldPattern[Condition[Verbatim[G][x_],_]]", "G", "downvalues"),
    ],
)
def test_determine_value_role(pattern_str, tag, position):
    target = parse_builtin_rule(tag)
    pattern_expr = parse_builtin_rule(pattern_str)
    pattern_pat = BasePattern.create(pattern_expr)
    assert determine_value_role(pattern_pat, target) == position
    assert determine_value_role(pattern_expr, target) == position


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg"),
    [
        # A definition with many stored values, so that the literal index is used.
        (
            "ClearAll[f, g, h, k]; Do[f[i] = i^2, {i, 20}]; f[x_] := lin[x];"
            " {f[3], f[20], f[21], f[x]}",
            "{9, 400, lin[21], lin[x]}",
            "Stored values and a pattern rule",
        ),
        ("f[3] = new; {f[3], f[4]}", "{new, 16}", "A stored value replaced"),
        ("f[5] =.; {f[5], f[6]}", "{lin[5], 36}", "A stored value removed"),
        (
            "f[7] := cond /; True; {f[7], f[8]}",
            "{cond, 64}",
            "A conditional rule for a stored value comes first",
        ),
        (
            "f[9] := never /; False; f[9]",
            "81",
            "A failing condition falls back to the stored value",
        ),
        (
            "DownValues[f] = {HoldPattern[f[x_]] :> first[x], HoldPattern[f[1]] :> one};"
            " {f[1], f[2]}",
            "{first[1], first[2]}",
            "DownValues set in an order of their own",
        ),
        ("ClearAll[f]; f[1]", "f[1]", "Cleared"),
        (
            "Do[g[k][i] = -i, {i, 20}]; g[k][x_] := other[x]; {g[k][3], g[k][30]}",
            "{-3, other[30]}",
            "SubValues",
        ),
        (
            "Do[h[i, {i}] = i, {i, 20}]; {h[3, {3}], h[3, {4}], h[3, {3.}]}",
            "{3, h[3, {4}], h[3, {3.}]}",
            "Nested literal left-hand sides",
        ),
        (
            "SetAttributes[k, Orderless]; Do[k[i, a] = i, {i, 20}]; {k[a, 3], k[3, a]}",
            "{3, 3}",
            "Orderless heads",
        ),
        ("ClearAll[f, g, h, k];", "Null", None),
    ],
)
def test_stored_values_lookup(str_expr, str_expected, fail_msg):
    """Rules applied through the literal index of a rule list"""
    from test.helper import check_evaluation

    check_evaluation(str_expr, str_expected, failure_message=fail_msg)
