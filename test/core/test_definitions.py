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
        ("DisplayForm[boxexpr_InterpretationBox]", "InterpretationBox", "upvalues"),
        (
            "ToExpression[boxexpr_InterpretationBox, form___]",
            "InterpretationBox",
            "upvalues",
        ),
        # Just one argument, must be an upvalue
        ("N[A[s_]]", "A", "upvalues"),
    ],
)
def test_get_tag_position(pattern_str, tag, position):
    pattern = parse_builtin_rule(pattern_str)
    assert get_tag_position(pattern, f"System`{tag}") == position
