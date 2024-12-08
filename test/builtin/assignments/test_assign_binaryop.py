# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.assignments.assign_binaryop
"""

from test.helper import check_evaluation, session


def test_uninitialized():
    session.evaluate("Clear[a]")
    for inplace_operator, str_expected in (
        ("Decrement", "a--"),
        ("Increment", "a++"),
        ("PreDecrement", "--a"),
        ("PreIncrement", "++a"),
    ):
        check_evaluation(
            str_expr=f"{inplace_operator}[a]",
            str_expected=str_expected,
            to_string_expr=True,
            expected_messages=(
                "a is not a variable with a value, so its value cannot be changed.",
            ),
        ),


def test_predecrement():
    check_evaluation(
        "--5",
        "--5",
        failure_message="PreDecrement::rvalue: 5 is not a variable with a value, so its value cannot be changed.",
    )
