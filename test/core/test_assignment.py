# -*- coding: utf-8 -*-

from test.helper import session

import pytest

from mathics.core.assignment import pop_reference_head
from mathics.eval.assignments.assignment import get_reference_expression

evaluation = session.evaluation


@pytest.mark.parametrize(
    ("expr_str", "expected_str"),
    [
        (
            "A",
            "A",
        ),
        (
            "A[x]",
            "A[x]",
        ),
        (
            "HoldPattern[A[x]]",
            "A[x]",
        ),
        (
            "HoldPattern[A][x]",
            "A[x]",
        ),
        (
            "Condition[A[x],3]",
            "A[x]",
        ),
        (
            "HoldPattern[Condition[A[x],3]]",
            "A[x]",
        ),
        (
            "Condition[HoldPattern[A][x],3]",
            "A[x]",
        ),
    ],
)
def test_get_reference_expression(expr_str, expected_str):
    expr = evaluation.parse(expr_str)
    result = get_reference_expression(expr)
    expected = evaluation.parse(expected_str)
    assert str(result) == str(expected)


@pytest.mark.parametrize(
    ("expr_str", "lhs_ref_str", "expected_str"),
    [
        (
            "A",
            "A",
            "A",
        ),
        (
            "A[x]",
            "A",
            "A[x]",
        ),
        (
            "A[B[x],y]",
            "A",
            "A[B[x],y]",
        ),
        (
            "B[A[x,y],z]",
            "A",
            "A[B[x,z],y]",
        ),
        (
            "F[B[A[x,y],z]]",
            "A",
            "A[F[B[x,z]],y]",
        ),
        (
            "F[B[A[x,y],z],t]",
            "A",
            "A[F[B[x,z],t],y]",
        ),
    ],
)
def test_pop_reference_head(expr_str, lhs_ref_str, expected_str):
    lhs_ref = evaluation.parse(lhs_ref_str)
    expr = evaluation.parse(expr_str)
    print("reference:", lhs_ref)
    print("expr:", expr)
    result = pop_reference_head(expr, lhs_ref)
    expected = evaluation.parse(expected_str)
    assert str(result) == str(expected)
