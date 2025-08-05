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
    expr1_key = BasePattern.create(session.evaluate(str_expr1)).get_sort_key(True)
    expr2_key = BasePattern.create(session.evaluate(str_expr2)).get_sort_key(True)
    print(str_expr1, expr1_key)
    print(str_expr2, expr2_key)

    if dir == 0:
        assert expr1_key == expr2_key, msg or "'{expr1}'!='{expr2}'"
    elif dir > 0:
        assert expr1_key < expr2_key, msg or "'{expr1}'<='{expr2}'"
    else:
        assert expr1_key > expr2_key, msg or "'{expr1}'>='{expr2}'"
