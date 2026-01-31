# -*- coding: utf-8 -*-

import random
import sys
import unittest

import sympy

from mathics.core.atoms import (
    Complex,
    Integer,
    Integer0,
    Integer1,
    IntegerM1,
    MachineReal,
    Real,
    String,
)
from mathics.core.convert.python import from_python
from mathics.core.convert.sympy import from_sympy
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SYMPY_SLOT_PREFIX, Symbol, SymbolPlus, sympy_name
from mathics.core.systemsymbols import (
    SymbolD,
    SymbolDerivative,
    SymbolFunction,
    SymbolGamma,
    SymbolIntegrate,
    SymbolSin,
    SymbolSlot,
)

Symbol_f = Symbol("Global`f")
Symbol_x = Symbol("Global`x")
Symbol_y = Symbol("Global`y")
Symbol_z = Symbol("Global`z")
Symbol_Mathics_User_x = Symbol("Mathics`User`x")


class SympyConvert(unittest.TestCase):
    def compare_to_sympy(self, mathics_expr, sympy_expr, **kwargs):
        assert mathics_expr.to_sympy(**kwargs) == sympy_expr

    def compare_to_mathics(self, mathics_expr, sympy_expr, **kwargs):
        assert mathics_expr == from_sympy(sympy_expr, **kwargs)

    def compare(self, mathics_expr, sympy_expr, **kwargs):
        self.compare_to_sympy(mathics_expr, sympy_expr, **kwargs)
        self.compare_to_mathics(mathics_expr, sympy_expr)

    def testSymbol(self):
        self.compare(Symbol_x, sympy.Symbol(sympy_name(Symbol_x)))
        self.compare(
            Symbol_Mathics_User_x,
            sympy.Symbol(sympy_name(Symbol_Mathics_User_x)),
        )
        # Sympy symbols without prefix are mapped to symbols in
        # System` context:
        self.compare_to_mathics(Symbol("x"), sympy.Symbol("x"))
        # Notice that a sympy Symbol named "x" is converted
        # to the Mathics symbol "System`x", and then, when converted
        # back to sympy, goes to sympy.Symbol("_uSystem_x").

    def testReal(self):
        self.compare(Real("1.0"), sympy.Float("1.0"))
        self.compare(Real(1.0), sympy.Float(1.0))

    def testInteger(self):
        self.compare(Integer0, sympy.Integer(0))
        self.compare(Integer1, sympy.Integer(1))

        n = random.randint(-sys.maxsize, sys.maxsize)
        self.compare(Integer(n), sympy.Integer(n))

        n = random.randint(sys.maxsize, sys.maxsize * sys.maxsize)
        self.compare(Integer(n), sympy.Integer(n))

    def testComplex(self):
        self.compare(
            Complex(Real("1.0"), Real("1.0")),
            sympy.Add(sympy.Float("1.0"), sympy.Float("1.0") * sympy.I),
        )

        self.compare(Complex(Integer0, Integer1), sympy.I)

        self.compare(
            Complex(IntegerM1, Integer1),
            sympy.Integer(-1) + sympy.I,
        )

    def testString(self):
        String("abc").to_sympy() is None

    def testAdd(self):
        self.compare(
            Expression(SymbolPlus, Integer1, Symbol_x),
            sympy.Add(sympy.Integer(1), sympy.Symbol(sympy_name(Symbol_x))),
        )

    def testIntegrate(self):
        self.compare(
            Expression(SymbolIntegrate, Symbol_x, Symbol_y),
            sympy.Integral(
                sympy.Symbol(sympy_name(Symbol_x)),
                sympy.Symbol(sympy_name(Symbol_y)),
            ),
        )

    def testDerivative(self):
        self.compare(
            Expression(SymbolD, Symbol_x, Symbol_y),
            sympy.Derivative(
                sympy.Symbol(sympy_name(Symbol_x)),
                sympy.Symbol(sympy_name(Symbol_y)),
            ),
        )

    def testDerivative2(self):
        kwargs = {"converted_functions": set(["Global`f"])}

        head = Expression(
            Expression(SymbolDerivative, Integer1, Integer0),
            Symbol_f,
        )
        expr = Expression(head, Symbol_x, Symbol_y)

        sfxy = sympy.Function(sympy_name(Symbol_f))(
            sympy.Symbol(sympy_name(Symbol_x)),
            sympy.Symbol(sympy_name(Symbol_y)),
        )
        sym_expr = sympy.Derivative(sfxy, sympy.Symbol(sympy_name(Symbol_x)))

        self.compare_to_sympy(expr, sym_expr, **kwargs)
        # compare_to_mathics fails because Derivative becomes D (which then evaluates to Derivative)

    def testConvertedFunctions(self):
        kwargs = {"converted_functions": set(["Global`f"])}

        marg1 = Expression(Symbol_f, Symbol_x)
        sarg1 = sympy.Function(sympy_name(Symbol_f))(sympy.Symbol(sympy_name(Symbol_x)))
        self.compare(marg1, sarg1, **kwargs)

        marg2 = Expression(Symbol_f, Symbol_x, Symbol_y)
        sarg2 = sympy.Function(sympy_name(Symbol_f))(
            sympy.Symbol(sympy_name(Symbol_x)),
            sympy.Symbol(sympy_name(Symbol_y)),
        )
        self.compare(marg2, sarg2, **kwargs)

        self.compare(
            Expression(SymbolD, marg2, Symbol_x),
            sympy.Derivative(sarg2, sympy.Symbol(sympy_name(Symbol_x))),
            **kwargs,
        )

    def testExpression(self):
        self.compare(
            Expression(SymbolSin, Symbol_x),
            sympy.sin(sympy.Symbol(sympy_name(Symbol_x))),
        )

    def testConstant(self):
        self.compare(Symbol("System`E"), sympy.E)
        self.compare(Symbol("System`Pi"), sympy.pi)

    def testGamma(self):
        self.compare(
            Expression(SymbolGamma, Symbol_z),
            sympy.gamma(sympy.Symbol(sympy_name(Symbol_z))),
        )
        self.compare(
            Expression(SymbolGamma, Symbol_z, Symbol_x),
            sympy.uppergamma(
                sympy.Symbol(sympy_name(Symbol_z)),
                sympy.Symbol(sympy_name(Symbol_x)),
            ),
        )

    def testSlots(self):
        """check the conversion of slots in anonymous functions."""
        sympy_symbol = sympy.Symbol(f"{SYMPY_SLOT_PREFIX}1")
        sympy_lambda_expr = sympy.Lambda(sympy_symbol, sympy_symbol + 1)
        expr = Expression(
            SymbolFunction,
            Expression(SymbolPlus, Integer1, Expression(SymbolSlot, Integer1)),
        )
        self.compare(expr, sympy_lambda_expr)


class PythonConvert(unittest.TestCase):
    def compare(self, mathics_expr, python_expr):
        assert mathics_expr.to_python() == python_expr
        assert mathics_expr == from_python(python_expr)

    def testReal(self):
        self.compare(Real("0.0"), 0.0)
        self.compare(Real("1.5"), 1.5)
        self.compare(Real("-1.5"), -1.5)

    def testInteger(self):
        self.compare(Integer(1), 1)

    @unittest.expectedFailure
    def testString(self):
        self.compare(String("abc"), '"abc"')

    @unittest.expectedFailure
    def testSymbol(self):
        self.compare(Symbol("abc"), "abc")

    def testComplex(self):
        self.compare(Complex(Integer(1), Integer(1)), 1 + 1j)
        self.compare(
            Complex(MachineReal(1.0), MachineReal(1.0)),
            1.0 + 1.0j,
        )
        self.compare(Complex(Integer(1), MachineReal(1.0)), 1 + 1.0j)
        self.compare(Complex(MachineReal(1.0), Integer(1)), 1.0 + 1j)
        self.compare(Complex(Real("1.0", 5), Integer(1)), 1.0 + 1j)
        self.compare(Complex(Integer1, Real("1.0", 20)), 1 + 1.0j)

        self.compare(Complex(Integer0, Integer1), 1j)
        self.compare(Complex(Integer1, Integer0), 1)

    def testList(self):
        self.compare(ListExpression(Integer1), (1,))


if __name__ == "__main__":
    unittest.main()
