# -*- coding: utf-8 -*-
"""
Tests functions in mathics.core.definition
"""

import pytest

from mathics.core.definitions import get_tag_position
from mathics.core.parser import parse_builtin_rule


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
        ("A", "A", "own"),
        ("A/;A>0", "A", "own"),
        ("s:(A/;A>0)", "A", "own"),
        ("(s:A)/;A>0", "A", "own"),
        ("s:A/;A>0", "A", "own"),
        # Downvalues
        ("_A", "A", "down"),
        ("A[]", "A", "down"),
        ("_A", "A", "down"),
        ("A[p_, q]", "A", "down"),
        ("s:A[p_, q]", "A", "down"),
        ("A[p_, q]/;q>0", "A", "down"),
        ("(s:A[p_, q])/;q>0", "A", "down"),
        # NValues
        ("N[A[x_], _]", "A", "n"),
        ("N[A[x_], _]/; x>0", "A", "n"),
        # Subvalues
        ("_A[]", "A", "sub"),
        ("A[x][t]", "A", "sub"),
        ("(s:A[x])[t]", "A", "sub"),
        ("(x_A/;u>0)[p]", "A", "sub"),
        # Upvalues
        ("S[x_, A]", "A", "up"),
        ("S[x_, _A]", "A", "up"),
        ("S[x_, s_A/;s>0]", "A", "up"),
        ("S[x_, q:A]", "A", "up"),
        ("S[x_, q:(A[t_]/;t>0)]", "A", "up"),
        ("A[x_][s[y]]", "s", "up"),
        ("DisplayForm[boxexpr_InterpretationBox]", "InterpretationBox", "up"),
        ("ToExpression[boxexpr_InterpretationBox, form___]", "InterpretationBox", "up"),
        # Just one argument, must be an upvalue
        ("N[A[s_]]", "A", "up"),
    ],
)
def test_get_tag_position(pattern_str, tag, position):
    pattern = parse_builtin_rule(pattern_str)
    assert get_tag_position(pattern, f"System`{tag}") == position
