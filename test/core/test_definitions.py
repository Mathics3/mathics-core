# -*- coding: utf-8 -*-
"""
Tests functions in mathics.core.definition
"""

from test.helper import check_evaluation, session

import pytest

from mathics.core.atoms import Integer
from mathics.core.definitions import determine_value_role
from mathics.core.expression import Expression
from mathics.core.parser import parse_builtin_rule
from mathics.core.pattern import BasePattern
from mathics.core.symbols import Symbol


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
    ("str_expr", "str_expected", "assert_failure_msg"),
    [
        (
            "ClearAll[insF]; insF[1] = a; insF[2] = b; insF[1] = c; DownValues[insF]",
            "{HoldPattern[insF[1]] :> c, HoldPattern[insF[2]] :> b}",
            "A new rule replaces the rule with the same pattern",
        ),
        (
            "ClearAll[insF]; insF[x_] := 1 /; x > 0; insF[x_] := 2; insF[x_] := 3 /; x > 0; "
            "Length[DownValues[insF]]",
            "3",
            "Conditional rules are never replaced",
        ),
        (
            "ClearAll[insF]; insF[1] = a; SetAttributes[insF, Flat]; insF[1] = b; "
            "DownValues[insF]",
            "{HoldPattern[insF[1]] :> b}",
            "Also when the head got attributes between the two assignments",
        ),
        (
            "ClearAll[insF, insH]; insF[insH[1]] = a; SetAttributes[insH, OneIdentity]; "
            "insF[insH[1]] = b; DownValues[insF]",
            "{HoldPattern[insF[insH[1]]] :> b}",
            "Also when an inner head got attributes between the two assignments",
        ),
        (
            "ClearAll[insF]; insF[1] = a; insF[2] = b; insF[1] =.; insF[1] = c; insF[1] = d; "
            "DownValues[insF]",
            "{HoldPattern[insF[1]] :> d, HoldPattern[insF[2]] :> b}",
            "Also after Unset",
        ),
        ("ClearAll[insF, insH];", "Null", None),
    ],
)
def test_insert_rule_replaces_same_pattern(str_expr, str_expected, assert_failure_msg):
    check_evaluation(
        str_expr,
        str_expected,
        failure_message=assert_failure_msg,
    )


def test_insert_rule_after_explicit_order():
    """
    After ``DownValues[f] = {...}`` the rules keep the order given, which
    need not be the precedence order. A new rule must still replace the
    rule with the same pattern.
    """
    from mathics.core.definitions import Definition
    from mathics.core.rules import RewriteRule

    f = Symbol("Global`insK")
    lhs = [Expression(f, Integer(k)) for k in range(1, 6)]
    definition = Definition(name=f.name)
    # The reverse of the precedence order.
    definition.set_values_list(
        "downvalues", [RewriteRule(expr, Symbol("old")) for expr in reversed(lhs)]
    )
    definition.add_rule(RewriteRule(lhs[0], Symbol("new")))
    assert len(definition.downvalues) == 5
    assert [
        r.replace for r in definition.downvalues if r.pattern.expr.sameQ(lhs[0])
    ] == [Symbol("new")]


def test_insert_rule_compares_few_rules(monkeypatch):
    """
    Adding a rule should not compare its pattern with every rule already
    stored: with n rules that makes loading a definition O(n^2).
    """
    session.evaluate("ClearAll[insG]; Do[insG[i, 2] = i, {i, 1, 500}]")
    calls = 0
    same_q = BasePattern.sameQ

    def counting_same_q(self, other):
        nonlocal calls
        calls += 1
        return same_q(self, other)

    monkeypatch.setattr(BasePattern, "sameQ", counting_same_q)
    session.evaluate("insG[501, 2] = 501; insG[250, 2] = -250")
    monkeypatch.undo()
    assert session.evaluate("{Length[DownValues[insG]], insG[250, 2]}").to_python() == (
        501,
        -250,
    )
    session.evaluate("ClearAll[insG]")
    assert calls < 10, f"{calls} pattern comparisons for two assignments"
