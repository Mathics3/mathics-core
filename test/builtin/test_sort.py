# -*- coding: utf-8 -*-

from test.helper import check_evaluation, evaluate_value

import pytest

from mathics.core.builtin import check_requires_list
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolPlus, SymbolTimes


def test_canonical_sort():
    check_evaluation(
        """
    Sort[{
    "a","b", 1,
    ByteArray[{1,2,4,1}],
    2, 1.2, I, 2I-3, A,
    a+b, a*b, a+1, a*2, b^3, 2/3,
    A[x], F[2], F[x], F[x_], F[x___], F[x,t], F[x__],
    Condition[A,b>2], Pattern[expr, A]
    }]
    """,
        """{ -3 + 2*I, I, 2 / 3, 1, 1.2, 2,
         "a", "b", A, 2*a, a*b, b^3,
          A[x], F[2], F[x], F[x_], F[x___], F[x__], F[x, t],
          ByteArray["AQIEAQ=="], A /; b > 2,
          expr:A, 1 + a, a + b}""",
    )
    # The right canonical order should be, according to WMA:
    #     -3 + 2*I, I, 2/3, 1, 1.2, 2,
    #     "a", "b", 2*a,
    #      1 + a, A, a*b, b^3, a + b,
    #     A[x], A /; b > 2,
    #     F[2], F[x], F[x_], F[x___], F[x__], F[x, t],
    #     ByteArray["AQIEAQ=="], expr:A

    check_evaluation(
        r"Sort[Table[IntegerDigits[2^n], {n, 10}]]",
        r"{{2}, {4}, {8}, {1, 6}, {3, 2}, {6, 4}, {1, 2, 8}, {2, 5, 6}, {5, 1, 2}, {1, 0, 2, 4}}",
    )
    check_evaluation(
        r"SortBy[Table[IntegerDigits[2^n], {n, 10}], First]",
        r"{{1, 6}, {1, 2, 8}, {1, 0, 2, 4}, {2}, {2, 5, 6}, {3, 2}, {4}, {5, 1, 2}, {6, 4}, {8}}",
    )


# FIXME: come up with an example that doesn't require skimage.
@pytest.mark.skipif(
    not check_requires_list(["skimage"]),
    reason="Right now need scikit-image for this to work",
)
def test_canonical_sort_images():
    check_evaluation(
        r'Sort[{Import["ExampleData/Einstein.jpg"], 5}]',
        r'{5, Import["ExampleData/Einstein.jpg"]}',
    )


def test_Expression_sameQ():
    """
    Test Expression.SameQ
    """
    symbolX = Symbol("X")
    expr_plus = Expression(SymbolPlus, symbolX, Symbol("Y"))
    assert (
        expr_plus.sameQ(expr_plus) == True
    ), "should pass when head and elements are the same"

    assert (
        expr_plus.sameQ(symbolX) == False
    ), "should fail because 'other' in Expression.SameQ() is not an Expression"

    expr_times = Expression(SymbolTimes, symbolX, Symbol("Y"))

    assert (
        expr_plus.sameQ(expr_times) == False
    ), "should fail when Expression head's mismatch"

    expr_plus_copy = Expression(SymbolPlus, symbolX, Symbol("Y"))
    assert (
        expr_plus.sameQ(expr_plus_copy) == True
    ), "should pass when Expressions are different Python objects, but otherwise the same"

    # Try where we compare and expression with something that contains itself
    nested_expr = Expression(SymbolPlus, expr_plus)
    assert (
        nested_expr.sameQ(expr_plus) == False
    ), "should fail when one expression has the other embedded in it"
