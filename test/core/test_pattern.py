"""
Test for pattern objects

MathicsSession object is used here just as a handy way to built Pattern
expressions.
"""

from test.helper import check_evaluation, session

import pytest

from mathics.core.pattern import BasePattern


@pytest.mark.parametrize(
    ("str_expr1", "str_expr2", "dir", "msg"),
    [
        (
            "A",
            "4",
            0,
            "All the atoms have the same precedence",
        ),
        (
            "A",
            "HoldPattern[A]",
            0,
            "HoldPattern does not affect the order",
        ),
        (
            "A",
            "Pattern[x, A]",
            0,
            "Pattern comes before.",
        ),  # Fix me!
        (
            "A",
            "A[x]",
            1,
            "Atoms have predecende over expressions",
        ),
        #
        (
            "f[x]",
            "f[_]",
            1,
            None,
        ),
        (
            "A",
            "f[x]",
            1,
            None,
        ),
        (
            "f[_]",
            "HoldPattern[f[_]]",
            0,
            None,
        ),
        (
            "f[_]",
            "Pattern[expr,f[_]]",
            0,
            None,
        ),
        #
        (
            "Condition[A, test]",
            "A",
            1,
            "Condition comes a before bare pattern",
        ),
        (
            "PatternTest[A, test]",
            "A",
            1,
            "PatternTest comes before a bare pattern",
        ),
        (
            "Condition[A, test]",
            "PatternTest[A, test]",
            1,
            "PatternTest comes after Condition",
        ),
        #
        (
            "f[__]",
            "f[_]",
            -1,
            "Blank comes first than BlankSequence",
        ),
        (
            "f[___]",
            "f[_]",
            -1,
            "Blank comes first than BlankNullSequence",
        ),
        (
            "f[___]",
            "f[_,_]",
            -1,
            "Sequence of Blanks comes first than BlankNullSequence",
        ),
        #
        (
            "f[__]",
            "Pattern[expr, f[_]]",
            -1,
            None,
        ),
        (
            "f[___]",
            "Pattern[expr, f[_]]",
            -1,
            None,
        ),
        (
            "f[___]",
            "Pattern[expr, f[_,_]]",
            -1,
            None,
        ),
        #
        (
            "f[__]",
            "HoldPattern[f[_]]",
            -1,
            None,
        ),
        (
            "f[___]",
            "HoldPattern[f[_]]",
            -1,
            None,
        ),
        (
            "f[___]",
            "HoldPattern[f[_,_]]",
            -1,
            None,
        ),
    ],
)
def test_pattern_sort_key(str_expr1, str_expr2, dir, msg):
    expr1_key = BasePattern.create(session.evaluate(str_expr1)).pattern_precedence
    expr2_key = BasePattern.create(session.evaluate(str_expr2)).pattern_precedence
    print(str_expr1, expr1_key)
    print(str_expr2, expr2_key)

    if dir == 0:
        assert expr1_key == expr2_key, msg or "'{expr1}'!='{expr2}'"
    elif dir > 0:
        assert expr1_key < expr2_key, msg or "'{expr1}'<='{expr2}'"
    else:
        assert expr1_key > expr2_key, msg or "'{expr1}'>='{expr2}'"


def test_binding_is_correct_not_just_truthy():
    """MatchQ succeeding isn't enough -- check the actual bound values."""
    check_evaluation(None, None, None)
    check_evaluation("SetAttributes[g, Orderless];", None)

    check_evaluation(
        "g[1, 1, 2, 3] /. g[a_, a_, b_, rest___] :> {a, b, {rest}}",
        "{1, 2, {3}}",
        failure_message="repeated-name binding produced wrong values",
    )


def test_no_duplicate_present_fails_to_match():
    """No two equal elements exist -- a_, a_ must not match."""
    check_evaluation(None, None, None)
    check_evaluation("SetAttributes[g, Orderless];", None)

    check_evaluation(
        "MatchQ[g[1, 2, 3], g[a_, a_, rest___]]",
        "False",
        failure_message="matched despite no duplicate value in the data",
    )


def test_two_independent_repeated_groups():
    """Two separate repeated-name groups in the same pattern."""
    check_evaluation(None, None, None)
    check_evaluation("SetAttributes[g, Orderless];", None)
    check_evaluation(
        "g[1, 1, 2, 2, 5] /. g[a_, a_, b_, b_, rest___] :> {a, b, {rest}}",
        "{1, 2, {5}}",
        failure_message="two independent repeated-name groups got mixed up",
    )


def test_triple_repeat_needs_three_copies():
    """a_, a_, a_ requires three equal elements, not two."""
    check_evaluation(None, None, None)
    check_evaluation("SetAttributes[g, Orderless];", None)

    check_evaluation(
        "MatchQ[g[1, 1, 2, 3], g[a_, a_, a_, rest___]]",
        "False",
        failure_message="matched with only two copies for a triple repeat",
    )
    check_evaluation(
        "g[1, 1, 1, 2] /. g[a_, a_, a_, rest___] :> {a, {rest}}",
        "{1, {2}}",
        failure_message="failed to match with exactly three copies present",
    )


def test_exact_supply_no_double_counting():
    """The sharpest test for the 'available not filtered' caveat.

    g[c_Integer, a_, a_, rest___] needs 1 (for c) + 2 (for a, a) = 3
    element-slots satisfied. With exactly 3 available it must succeed;
    with only 2 available, it must fail -- if the pre-choice phase ever
    let the same physical element cover both `c` and one of the `a`
    slots, this second case would incorrectly succeed.
    """
    check_evaluation(None, None, None)
    check_evaluation("SetAttributes[g, Orderless];", None)

    check_evaluation(
        "g[1, 1, 1] /. g[c_Integer, a_, a_, rest___] :> {c, a, {rest}}",
        "{1, 1, {}}",
        failure_message="exact supply (3 elements for 3 slots) failed to match",
    )
    check_evaluation(
        "MatchQ[g[1, 1], g[c_Integer, a_, a_, rest___]]",
        "False",
        failure_message=(
            "matched with only 2 elements for 3 slots -- likely double-"
            "counting an element between c_ and the a_,a_ group"
        ),
    )


def test_repeated_name_respects_type_constraint():
    """a_Integer, a_Integer should not bind to a non-Integer duplicate."""
    check_evaluation(None, None, None)
    check_evaluation("SetAttributes[g, Orderless];", None)

    check_evaluation(
        "MatchQ[g[x, x, 1], g[a_Integer, a_Integer, rest___]]",
        "False",
        failure_message=("matched a_Integer against a duplicated non-Integer symbol"),
    )
    check_evaluation(
        "g[1, 1, x] /. g[a_Integer, a_Integer, rest___] :> {a, {rest}}",
        "{1, {x}}",
        failure_message="failed to match a_Integer against a genuine Integer duplicate",
    )
