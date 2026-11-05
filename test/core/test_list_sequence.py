# -*- coding: utf-8 -*-
"""
List does not hold its elements, so a Sequence[...] element of a list is
spliced into it, as it is into any other expression: {1, Sequence[2, 3]}
evaluates to {1, 2, 3}. The expected values are those of WMA 15.
"""

from test.helper import check_evaluation, session

import pytest

from mathics.core.list import ListExpression


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ("{1, Sequence[2, 3]}", "{1, 2, 3}"),
        ("List[1, Sequence[2, 3]]", "{1, 2, 3}"),
        ("(m428x = {1, Sequence[2, 3]}; m428x)", "{1, 2, 3}"),
        ("m428f[1, Sequence[2, 3]]", "m428f[1, 2, 3]"),
        ("{m428y, Sequence[2, 3]}", "{m428y, 2, 3}"),
        ("{Sequence[]}", "{}"),
        ("{Sequence[m428a, m428b]}", "{m428a, m428b}"),
        ("{1, {2, Sequence[3, 4]}}", "{1, {2, 3, 4}}"),
        ("{{Sequence[]}, {}}", "{{}, {}}"),
        ("{1, Sequence[2, Sequence[3, 4]]}", "{1, 2, 3, 4}"),
        ("{Sequence[{1, 2}]}", "{{1, 2}}"),
        ("{m428f[Sequence[1, 2]], Sequence[]}", "{m428f[1, 2]}"),
        ("Length[{1, Sequence[2, 3]}]", "3"),
        ("{1, Sequence[2, 3]}[[2]]", "2"),
        ("First[{Sequence[2, 3]}]", "2"),
        ("Range[3] /. 2 -> Sequence[]", "{1, 3}"),
        ("{1, 2} /. 1 -> Sequence[m428a, m428b]", "{m428a, m428b, 2}"),
        # Held lists are not evaluated, so they keep the Sequence.
        ("Hold[{1, Sequence[2, 3]}]", "Hold[{1, Sequence[2, 3]}]"),
        ("HoldComplete[{1, Sequence[2, 3]}]", "HoldComplete[{1, Sequence[2, 3]}]"),
        ("Hold[Evaluate[{1, Sequence[2, 3]}]]", "Hold[{1, 2, 3}]"),
        ("ReleaseHold[Hold[{1, Sequence[2, 3]}]]", "{1, 2, 3}"),
        # Unevaluated[Sequence[...]] is not a Sequence: it stays, as in WMA.
        (
            "{1, Unevaluated[Sequence[2, 3]]}",
            "{1, Unevaluated[Sequence[2, 3]]}",
        ),
    ],
)
def test_list_splices_sequence(str_expr, str_expected):
    check_evaluation(None)
    check_evaluation(
        f"InputForm[{str_expr}]",
        str_expected,
        hold_expected=True,
    )


def test_spliced_list_is_a_list_expression():
    result = session.evaluate("{1, Sequence[2, 3]}")
    assert isinstance(result, ListExpression)
    assert [element.value for element in result.elements] == [1, 2, 3]
