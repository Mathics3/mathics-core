"""
Unit tests for mathics.builtin.functional.application
"""

from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("g[x_,y_] := x+y;g[Sequence@@Slot/@Range[2]]&[1,2]", None, "#1 + #2", None),
        ("Evaluate[g[Sequence@@Slot/@Range[2]]]&[1,2]", None, "3", None),
        ("# // InputForm", None, "#1", None),
        ("#0 // InputForm", None, "#0", None),
        ("## // InputForm", None, "##1", None),
        ("Clear[g];", None, "Null", None),
    ],
)
def test_application(str_expr, msgs, str_expected, fail_msg):
    """functional.application"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


def test_slot_free_parts_kept():
    """Filling in the slots of a pure function keeps the parts of its body
    that have no slots, such as a literal list, as they are."""
    from mathics.core.atoms import Integer1
    from mathics.core.expression import Expression
    from mathics.core.list import ListExpression
    from mathics.core.symbols import Symbol
    from mathics.core.systemsymbols import SymbolSlot

    literal = ListExpression(Integer1, ListExpression(Integer1))
    body = Expression(Symbol("Global`f"), Expression(SymbolSlot, Integer1), literal)
    filled = body.replace_slots([None, Symbol("Global`a")], None)
    assert filled.elements[1] is literal
    assert body.replace_slots([None, Symbol("Global`a")], None) is not body
    assert literal.replace_slots([None, Symbol("Global`a")], None) is literal


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "fail_msg"),
    [
        (
            "fbody = (fbx = {1, 2, {3, 4}}; fbx[[1]] = #; fbx[[3, 1]] = #; fbx)&; "
            "{fbody[7], fbody[8], fbody[[1, 1, 2]]}",
            "{{7, 2, {7, 4}}, {8, 2, {8, 4}}, {1, 2, {3, 4}}}",
            "A part assignment inside the body leaves the body as it was.",
        ),
        (
            "fbh = (fbz = {{0}}; AppendTo[fbz[[1]], #]; fbz)&; {fbh[1], fbh[2]}",
            "{{{0, 1}}, {{0, 2}}}",
            None,
        ),
    ],
)
def test_function_body_unchanged(str_expr, str_expected, fail_msg):
    check_evaluation(str_expr, str_expected, failure_message=fail_msg)
