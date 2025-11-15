# -*- coding: utf-8 -*-

from test.helper import check_evaluation

from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolPlus, SymbolTimes


def test_Sorting_Numbers():
    check_evaluation(
        "SameQ[Sort[{1.+0.I, 1.`50+0.`40I, 1.`50, 1.`3, 1.`4, 1., 1}], {1, 1., 1. + 0.*I, 1. + 0.*I, 1.00, 1.000, 1.0000000000000000000000000000000000000000000000000}]",
        "True", "Order according WMA for numeric expressions.")
    

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
