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
from mathics.core.symbols import (
    Symbol,
    SymbolPlus,
    sympy_slot_prefix,
    sympy_symbol_prefix,
)
from mathics.core.systemsymbols import (
    SymbolD,
    SymbolDerivative,
    SymbolFunction,
    SymbolGamma,
    SymbolIntegrate,
    SymbolSin,
    SymbolSlot,
)


class SympyConvert(unittest.TestCase):
    def compare_to_sympy(self, mathics_expr, sympy_expr, **kwargs):
        assert mathics_expr.to_sympy(**kwargs) == sympy_expr

    def compare_to_mathics(self, mathics_expr, sympy_expr, **kwargs):
        assert mathics_expr == from_sympy(sympy_expr, **kwargs)

    def compare(self, mathics_expr, sympy_expr, **kwargs):
        self.compare_to_sympy(mathics_expr, sympy_expr, **kwargs)
        self.compare_to_mathics(mathics_expr, sympy_expr)

    def testSymbol(self):
        self.compare(Symbol("Global`x"), sympy.Symbol(f"{sympy_symbol_prefix}Global`x"))
        self.compare(
            Symbol("_Mathics_User_x"),
            sympy.Symbol(f"{sympy_symbol_prefix}System`_Mathics_User_x"),
        )

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
            Expression(SymbolPlus, Integer1, Symbol("Global`x")),
            sympy.Add(sympy.Integer(1), sympy.Symbol(f"{sympy_symbol_prefix}Global`x")),
        )

    def testIntegrate(self):
        self.compare(
            Expression(SymbolIntegrate, Symbol("Global`x"), Symbol("Global`y")),
            sympy.Integral(
                sympy.Symbol(f"{sympy_symbol_prefix}Global`x"),
                sympy.Symbol(f"{sympy_symbol_prefix}Global`y"),
            ),
        )

    def testDerivative(self):
        self.compare(
            Expression(SymbolD, Symbol("Global`x"), Symbol("Global`y")),
            sympy.Derivative(
                sympy.Symbol(f"{sympy_symbol_prefix}Global`x"),
                sympy.Symbol(f"{sympy_symbol_prefix}Global`y"),
            ),
        )

    def testDerivative2(self):
        kwargs = {"converted_functions": set(["Global`f"])}

        head = Expression(
            Expression(SymbolDerivative, Integer1, Integer0),
            Symbol("Global`f"),
        )
        expr = Expression(head, Symbol("Global`x"), Symbol("Global`y"))

        sfxy = sympy.Function(str(f"{sympy_symbol_prefix}Global`f"))(
            sympy.Symbol(f"{sympy_symbol_prefix}Global`x"),
            sympy.Symbol(f"{sympy_symbol_prefix}Global`y"),
        )
        sym_expr = sympy.Derivative(
            sfxy, sympy.Symbol(f"{sympy_symbol_prefix}Global`x")
        )

        self.compare_to_sympy(expr, sym_expr, **kwargs)
        # compare_to_mathics fails because Derivative becomes D (which then evaluates to Derivative)

    def testConvertedFunctions(self):
        kwargs = {"converted_functions": set(["Global`f"])}

        marg1 = Expression(Symbol("Global`f"), Symbol("Global`x"))
        sarg1 = sympy.Function(str(f"{sympy_symbol_prefix}Global`f"))(
            sympy.Symbol(f"{sympy_symbol_prefix}Global`x")
        )
        self.compare(marg1, sarg1, **kwargs)

        marg2 = Expression(Symbol("Global`f"), Symbol("Global`x"), Symbol("Global`y"))
        sarg2 = sympy.Function(str(f"{sympy_symbol_prefix}Global`f"))(
            sympy.Symbol(f"{sympy_symbol_prefix}Global`x"),
            sympy.Symbol(f"{sympy_symbol_prefix}Global`y"),
        )
        self.compare(marg2, sarg2, **kwargs)

        self.compare(
            Expression(SymbolD, marg2, Symbol("Global`x")),
            sympy.Derivative(sarg2, sympy.Symbol(f"{sympy_symbol_prefix}Global`x")),
            **kwargs,
        )

    def testExpression(self):
        self.compare(
            Expression(SymbolSin, Symbol("Global`x")),
            sympy.sin(sympy.Symbol(f"{sympy_symbol_prefix}Global`x")),
        )

    def testConstant(self):
        self.compare(Symbol("System`E"), sympy.E)
        self.compare(Symbol("System`Pi"), sympy.pi)

    def testGamma(self):
        self.compare(
            Expression(SymbolGamma, Symbol("Global`z")),
            sympy.gamma(sympy.Symbol(f"{sympy_symbol_prefix}Global`z")),
        )
        self.compare(
            Expression(SymbolGamma, Symbol("Global`z"), Symbol("Global`x")),
            sympy.uppergamma(
                sympy.Symbol(f"{sympy_symbol_prefix}Global`z"),
                sympy.Symbol(f"{sympy_symbol_prefix}Global`x"),
            ),
        )

    def testSlots(self):
        """check the conversion of slots in anonymous functions."""
        sympy_symbol = sympy.Symbol("x")
        sympy_lambda_expr = sympy.Lambda(sympy_symbol, sympy_symbol + 1)
        # compare_to_sympy does not pass because Slot[1] are translated as
        # functions
        self.compare_to_mathics(
            Expression(
                SymbolFunction,
                Expression(SymbolPlus, Integer1, Expression(SymbolSlot, Integer1)),
            ),
            sympy_lambda_expr,
        )


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
