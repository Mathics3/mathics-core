import test.helper

import pytest
from sympy import Float as SympyFloat

from mathics.core.atoms import (
    MATHICS3_COMPLEX_I,
    Complex,
    Integer,
    Integer0,
    Integer1,
    Integer2,
    Integer3,
    IntegerM1,
    Rational,
    Real,
    String,
)
from mathics.core.convert.sympy import from_sympy, sympy_singleton_to_mathics
from mathics.core.expression import Expression
from mathics.core.expression_predefined import MATHICS3_COMPLEX_INFINITY
from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolNull,
    SymbolPlus,
    SymbolPower,
    SymbolTimes,
    SymbolTrue,
)
from mathics.core.systemsymbols import SymbolE, SymbolExp, SymbolI, SymbolPi, SymbolSin

Symbol_a = Symbol("Global`a")
Symbol_b = Symbol("Global`b")
Symbol_x = Symbol("Global`x")
Symbol_y = Symbol("Global`y")
Symbol_F = Symbol("Global`F")
Symbol_G = Symbol("Global`G")


@pytest.mark.parametrize(
    ("expr",),
    [
        (Symbol_x,),
        (Expression(Symbol_F, Symbol_x),),
        (SymbolPi,),
        (SymbolTrue,),
        (SymbolFalse,),
        (Integer1,),
        (Integer(37),),
        (Rational(1, 5),),
        (Real(1.2),),
        (Real(SympyFloat(1.2, 10)),),
        (Complex(Real(2.0), Real(3.0)),),
        (Expression(Symbol_F, Symbol_x, SymbolPi),),
        (Expression(Symbol_G, Expression(Symbol_F, Symbol_x, SymbolPi)),),
        (Expression(SymbolPlus, Integer3, Symbol_x, Symbol_y),),
    ],
)
def test_from_to_sympy_invariant(expr):
    """
    Check if the conversion back and forward is consistent.
    """
    result_sympy = expr.to_sympy()
    back_to_mathics = from_sympy(result_sympy)
    print([expr, result_sympy, back_to_mathics])
    assert expr.sameQ(back_to_mathics)


@pytest.mark.parametrize(
    ("expr", "result", "msg"),
    [
        (
            Expression(SymbolExp, Expression(SymbolTimes, SymbolI, SymbolPi)),
            IntegerM1,
            None,
        ),
        (
            Expression(
                SymbolPower, SymbolE, Expression(SymbolTimes, SymbolI, SymbolPi)
            ),
            IntegerM1,
            None,
        ),
        (Expression(SymbolSin, SymbolPi), Integer0, None),
        (Expression(SymbolPlus, Integer1, Integer2), Integer3, None),
        (String("Hola"), SymbolNull, None),
        (Rational(1, 0), MATHICS3_COMPLEX_INFINITY, None),
        (MATHICS3_COMPLEX_I, MATHICS3_COMPLEX_I, None),
        (
            SymbolI,
            MATHICS3_COMPLEX_I,
            (
                "System`I evaluates to Complex[0,1] in the back and forward conversion. "
                "This prevents an infinite recursion in evaluation"
            ),
        ),
        # (Integer3**Rational(-1, 2), Rational(Integer1, Integer3)* (Integer3 ** (RationalOneHalf)), None ),
    ],
)
def test_from_to_sympy_change(expr, result, msg):
    """
    Check if the conversion back and forward produces
    the expected evaluation.
    """
    print([expr, result])
    if msg:
        assert result.sameQ(from_sympy(expr.to_sympy())), msg
    else:
        assert result.sameQ(from_sympy(expr.to_sympy()))


def test_convert_sympy_singletons():
    """
    Check conversions between singleton symbols in
    SymPy and Mathics Symbols.
    """
    for key, val in sympy_singleton_to_mathics.items():
        print("equivalence", key, "<->", val)
        if key is not None:
            res = from_sympy(key)
            print("  ->  ", res)
            assert from_sympy(key).sameQ(val)

            res = val.to_sympy()
            print(res, "  <-  ")
            assert res is key
