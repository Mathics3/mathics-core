"""
Unit tests for mathics.builtins.optimization

In particular:

Maximize[] and Minimize[]


"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (None, None, None, None),
        ("Maximize[1 - (x y - 3)^2, {x, y}]", None, "{{1, {x -> 3, y -> 1}}}", None),
        (
            "Maximize[{x - 2 y, x^2 + y^2 <= 1}, {x, y}]",
            None,
            "{{Sqrt[5], {x -> Sqrt[5] / 5, y -> -2 Sqrt[5] / 5}}}",
            None,
        ),
        ("Minimize[(x y - 3)^2 + 1, {x, y}]", None, "{{1, {x -> 3, y -> 1}}}", None),
        (
            "Minimize[{x - 2 y, x^2 + y^2 <= 1}, {x, y}]",
            None,
            "{{-Sqrt[5], {x -> -Sqrt[5] / 5, y -> 2 Sqrt[5] / 5}}}",
            None,
        ),
    ],
)
def test_optimization(str_expr, msgs, str_expected, fail_msg):
    """
    Tests of mathics.builtin.optimization.
    """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
