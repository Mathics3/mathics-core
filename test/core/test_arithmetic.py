#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import unittest
from mathics.core.atoms import (
    Integer,
    Integer1,
    Integer2,
    Integer3,
    IntegerM1,
    Rational,
)
from mathics.core.definitions import Definitions
from mathics.core.convert.expression import to_expression
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.convert.expression import to_mathics_list
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolAbs, SymbolPlus, SymbolTimes


class ArithmeticTest(unittest.TestCase):
    def setUp(self):
        definitions = Definitions(add_builtin=True)
        self.evaluation = Evaluation(definitions, format="xml")
        self.symbol_a = Symbol("a")

    def testSubtraction(self):
        """
        Test forms of binary infix operator subtraction
        """
        cases = (
            (
                self.symbol_a - Integer3,
                Expression(SymbolPlus, Integer(-3), self.symbol_a),
            ),
            (Integer1 - Integer3, Integer(-2)),
            (Integer1 - Integer(-3), Integer(4)),
            (
                # test using to_mathics_list() and with element_convesion_fn
                to_mathics_list(1, 2) - to_mathics_list(-1, 8),
                to_mathics_list(2, -6, elements_conversion_fn=Integer),
            ),
        )
        self._testCases(cases)

    def testMultiplication(self):
        """
        Test forms of binary infix operator multiplication
        """
        cases = (
            (
                self.symbol_a * Integer3,
                Expression(SymbolTimes, Integer3, self.symbol_a),
            ),
            (Integer(3) * Integer(7), Integer(21)),
            (Integer(3) * -Integer(7), Integer(-21)),
            (
                to_mathics_list(1, 2) * to_mathics_list(-1, 8),
                to_mathics_list(-1, 16, elements_conversion_fn=Integer),
            ),
        )
        self._testCases(cases)

    def testTrueDivision(self):
        """
        Test forms of binary infix operator true division
        """
        cases = (
            (
                Symbol("a") / Integer3,
                Expression(SymbolTimes, Rational(1, 3), Symbol("a")),
            ),
            (Integer(8) / Integer2, Integer(4)),
            (Integer(8) / Integer(-2), Integer(-4)),
            (Integer(7) / Integer2, Rational(7, 2)),
            (
                # Here we test using ListExpression() instead of to_mathics_list()
                ListExpression(Integer1, Integer(9))
                / ListExpression(IntegerM1, Integer3),
                ListExpression(IntegerM1, Integer3),
            ),
        )
        self._testCases(cases)

    def testFloorDivision(self):
        cases = (
            (Integer(8) // Integer2, Integer(4)),
            (Integer(8) // -Integer2, Integer(-4)),
            (Integer(7) // Integer2, Integer3),
        )
        self._testCases(cases)

    def testPower(self):
        """
        Test forms of binary infix exponentiation operator
        """
        cases = (
            (Integer(8) ** Integer2, Integer(64)),
            (
                ListExpression(Integer2, Integer(5))
                ** ListExpression(Integer3, Integer(4)),
                ListExpression(Integer(8), Integer(625)),
            ),
        )
        self._testCases(cases)

    def testAbs(self):
        """
        Test forms of binary absolute value function
        """
        cases = (
            (abs(Integer(-8)), Integer(8)),
            (abs(ListExpression()), Expression(SymbolAbs, ListExpression())),
        )
        self._testCases(cases)

    def _testCases(self, cases):
        for expression, result in cases:
            self.assertEqual(
                # Use both Expression() ...
                Expression(Symbol("FullSimplify"), expression).evaluate(
                    self.evaluation
                ),
                # and to_expression()
                to_expression("FullSimplify", result).evaluate(self.evaluation),
            )


if __name__ == "__main__":
    unittest.main()
