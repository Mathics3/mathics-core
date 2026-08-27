# -*- coding: utf-8 -*-

from test.helper import check_evaluation

from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolPlus, SymbolTimes


def test_sort_wma():
    """Test the alphabetic order in WMA for Strings and Symbols"""
    # In Python, str are ordered as tuples of
    # ascii codes of the characters. So,
    #
    # "Abeja" <"Ave"<"aVe"<"abeja"
    #
    # In WMA, strings and symbols are sorted in alphabetical order, with
    # lowercaps characters coming before than the corresponding upper case.
    # Then, the same words are sorted in WMA as
    #
    # "abeja"< "Abeja"<"aVe"<"Ave"
    #
    # Such order is equivalent to use
    # `lambda s: (s.lower(), s.swapcaps(),)` as sort key.
    #
    # Finally, String atoms comes before than Symbols. The following test
    # reinforce this order.
    str_expr = (
        '{"Ave", "aVe", "abeja", AVe, ave, aVe, "Abeja", "ABEJA", '
        '"AVe", "ave del paraíso", "Ave del paraíso", '
        '"Ave del Paraíso"} // Sort // InputForm'
    )
    str_expected = (
        '{"abeja", "Abeja", "ABEJA", "aVe", "Ave", "AVe", '
        '"ave del paraíso", "Ave del paraíso", "Ave del Paraíso", '
        "ave, aVe, AVe}//InputForm"
    )
    check_evaluation(
        str_expr,
        str_expected,
        # to_string_expr=True,
        # to_string_expected=True,
        # hold_expected=True,
        failure_message="WMA order",
    )


def test_Expression_sameQ():
    """
    Test Expression.SameQ
    """
    symbolX = Symbol("X")
    expr_plus = Expression(SymbolPlus, symbolX, Symbol("Y"))
    assert (
        expr_plus.sameQ(expr_plus) is True
    ), "should pass when head and elements are the same"

    assert (
        expr_plus.sameQ(symbolX) is False
    ), "should fail because 'other' in Expression.SameQ() is not an Expression"

    expr_times = Expression(SymbolTimes, symbolX, Symbol("Y"))

    assert (
        expr_plus.sameQ(expr_times) is False
    ), "should fail when Expression head's mismatch"

    expr_plus_copy = Expression(SymbolPlus, symbolX, Symbol("Y"))
    assert (
        expr_plus.sameQ(expr_plus_copy) is True
    ), "should pass when Expressions are different Python objects, but otherwise the same"

    # Try where we compare and expression with something that contains itself
    nested_expr = Expression(SymbolPlus, expr_plus)
    assert (
        nested_expr.sameQ(expr_plus) is False
    ), "should fail when one expression has the other embedded in it"
