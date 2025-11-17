# -*- coding: utf-8 -*-

from test.helper import check_evaluation, session

from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolPlus, SymbolTimes


def test_Sorting_one():
    """
    In WMA, canonical order for numbers with the same value in different representations:
    * Integer
    * Complex[Integer, PrecisionReal]
    * MachineReal
    * Complex[MachineReal, MachineReal]
    * PrecisionReal, Complex[PrecisionReal, PrecisionReal] if precision of the real parts are equal,
    * otherwise, sort by precision of the real part.
    * Rational
    Example: {1, 1 + 0``10.*I, 1., 1. + 0.*I, 1.`4., 1.`4. + 0``4.*I, 1.`4. + 0``3.*I, 1.`6.}
    and
             {0.2, 0.2 + 0.*I, 0.2`4., 0.2`10., 1/5}
    are lists in canonical order.

    If the numbers are in different representations, numbers are sorted by their real parts,
    and then the imaginary part is considered:
    {0.2, 0.2 - 1.*I, 0.2 + 1.*I, 1/5}
    """
    # Canonical order
    for expr_str in [
        "{1, 1., 1. + 0.*I, 1.`5. + 0.``2*I, 1.`2., 1.`49.}",
        "{.2, .2+0.I, .2`20+0.``20 I,.2`20,.2`21, 1/5}",
    ]:
        order_equiv_forms = session.evaluate(f"OrderedFormsOfOne={expr_str}")
        print(order_equiv_forms)
        for elem, nelem in zip(order_equiv_forms[:-1], order_equiv_forms[1:]):
            e_order, ne_order = elem.element_order, nelem.element_order
            print("-------")
            print(type(elem), elem, e_order)
            print("vs", type(nelem), nelem, ne_order)
            assert e_order < ne_order and not (
                ne_order <= e_order
            ), "wrong order or undefined."
            assert elem == nelem, "elements are not equal"
            assert nelem == elem, "elements are not equal"


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
