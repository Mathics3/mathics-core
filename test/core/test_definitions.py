# -*- coding: utf-8 -*-
"""
Tests functions in mathics.core.definition
"""

import pytest

from mathics.core.definitions import get_tag_position
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
            except:
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
def test_get_tag_position(pattern_str, tag, position):
    target = parse_builtin_rule(tag)
    pattern_expr = parse_builtin_rule(pattern_str)
    pattern_pat = BasePattern.create(pattern_expr)
    assert get_tag_position(pattern_pat, target) == position
    assert get_tag_position(pattern_expr, target) == position
