# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.assignments.assignment

Tests here check the compatibility of
the  default behavior of the different assignment operators
with WMA.
"""
# TODO: consider splitting this module into sub-modules.

from test.helper import check_arg_counts, check_evaluation, session

import pytest
from mathics_scanner.errors import IncompleteSyntaxError


@pytest.mark.parametrize(
    ("function_name", "msg_fragment"),
    [
        (
            "Set",
            "1 or more arguments are",
        ),
        (
            "SetDelayed",
            "1 or more arguments are",
        ),
        (
            "TagSet",
            "2 or more arguments are",
        ),
        (
            "UpSet",
            "1 or more arguments are",
        ),
        (
            "UpSetDelayed",
            "1 or more arguments are",
        ),
    ],
)
def test_arg_errors(function_name, msg_fragment):
    """ """
    check_arg_counts(function_name, msg_fragment)


def test_upset():
    """
    Test UpSet[] builtin
    """
    check_evaluation(
        "a ^= 3",
        "a ^= 3",
        failure_message="Should not be able to use UpSet on a Symbol",
        expected_messages=("Nonatomic expression expected at position 1 in a ^= 3.",),
    )
    check_evaluation(
        "f[g, a + b, h] ^= 2",
        "2",
        failure_message="UpSet on a protected value should fail",
        expected_messages=("Tag Plus in f[g, a + b, h] is Protected.",),
    )
    check_evaluation("UpValues[h]", "{HoldPattern[f[g, a + b, h]] ⧴ 2}")


def test_process_assign_other():
    # FIXME: beef up check_evaluation so it allows regexps in matching.
    # Then this code would be less fragile.
    for prefix in ("", "System`"):
        for kind, suffix in (
            (
                "Recursion",
                "512; use the MATHICS_MAX_RECURSION_DEPTH environment variable to allow higher limits",
            ),
            ("Iteration", "Infinity"),
        ):
            limit = f"${kind}Limit"
            check_evaluation(f"{prefix}{limit} = 511", "511")
            check_evaluation(
                f"{prefix}{limit} = 2",
                "2",
                expected_messages=(
                    f"Cannot set {limit} to 2; value must be an integer between 20 and {suffix}.",
                ),
            )
        check_evaluation(f"{prefix}$ModuleNumber = 3", "3")
        check_evaluation(
            f"{prefix}$ModuleNumber = -1",
            "-1",
            expected_messages=(
                "Cannot set $ModuleNumber to -1; value must be a positive integer.",
            ),
        )


@pytest.mark.parametrize(
    ["expr", "expect", "assert_msg", "expected_msgs"],
    [
        # Trivial cases on protected symbols. We should
        # get a message in every situation.
        (None, None, None, None),  # reset session
        (
            "List:=1;",
            None,
            "assign to protected element",
            ("Symbol List is Protected.",),
        ),
        (
            "HoldPattern[List]:=1;",
            None,
            "assign to wrapped protected element. Test 1.",
            ("Tag List in HoldPattern[List] is Protected.",),
        ),
        (
            "PatternTest[List, x]:=1;",
            None,
            "assign to wrapped protected element. Test 2.",
            ("Tag List in List ? x is Protected.",),
        ),
        (
            "Condition[List, x]:=1;",
            None,
            "assign to wrapped protected element. Test 3.",
            ("Tag List in List /; x is Protected.",),
        ),
        (
            "ClearAll[F,A,Y,x]; A=T; F[{a,b,c},Y[x_]]^:=x^2; ClearAll[A,F]; F[{a,b,c},Y[2]]",
            "4",
            "There is a warning, because a rule cannot be associated to List, but it is stored on Y.",
            ("Tag List in F[{a, b, c}, Y[x_]] is Protected.",),
        ),
    ],
)
def test_assignment_with_messages(expr, expect, assert_msg, expected_msgs):
    check_evaluation(
        expr, expect, failure_message=assert_msg, expected_messages=expected_msgs
    )
