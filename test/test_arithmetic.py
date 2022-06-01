#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import unittest
from mathics.core.atoms import (
    Integer,
    Integer0,
    Integer1,
    Integer2,
    Integer3,
    IntegerM1,
    Rational,
)
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolAbs, SymbolPlus, SymbolTimes


class ArithmeticTest(unittest.TestCase):
    def setUp(self):
        definitions = Definitions(add_builtin=True)
        self.evaluation = Evaluation(definitions, format="xml")

    def testAdd(self):
        cases = (
            (Symbol("a") + Integer3, Expression(SymbolPlus, Integer3, Symbol("a"))),
            (Integer1 + Integer3, Integer(4)),
            (Integer1 + -Integer3, -Integer2),
            (
                ListExpression(Integer1, Integer2)
                + ListExpression(IntegerM1, Integer(8)),
                ListExpression(Integer0, Integer(10)),
            ),
        )
        self._testCases(cases)

    def testSub(self):
        cases = (
            (Symbol("a") - 3, Expression(SymbolPlus, -3, Symbol("a"))),
            (Integer1 - 3, Integer(-2)),
            (Integer1 - (-3), Integer(4)),
            (
                ListExpression(Integer1, Integer2)
                - ListExpression(IntegerM1, Integer(8)),
                ListExpression(Integer2, -Integer(6)),
            ),
        )
        self._testCases(cases)

    def testMul(self):
        cases = (
            (Symbol("a") * 3, Expression("Times", 3, Symbol("a"))),
            (Integer(3) * 7, Integer(21)),
            (Integer(3) * (-7), Integer(-21)),
            (
                Expression("List", 1, 2) * Expression("List", -1, 8),
                Expression("List", -1, 16),
            ),
        )
        self._testCases(cases)

    def testTrueDiv(self):
        cases = (
            (Symbol("a") / 3, Expression(SymbolTimes, Rational(1, 3), Symbol("a"))),
            (Integer(8) / 2, Integer(4)),
            (Integer(8) / (-2), Integer(-4)),
            (Integer(7) / 2, Rational(7, 2)),
            (
                ListExpression(Integer1, Integer(9))
                / ListExpression(IntegerM1, Integer3),
                ListExpression(IntegerM1, Integer3),
            ),
        )
        self._testCases(cases)

    def testFloorDiv(self):
        cases = (
            (Integer(8) // Integer2, Integer(4)),
            (Integer(8) // -Integer2, Integer(-4)),
            (Integer(7) // Integer2, Integer3),
        )
        self._testCases(cases)

    def testPow(self):
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
        cases = (
            (abs(Integer(-8)), Integer(8)),
            (abs(ListExpression()), Expression(SymbolAbs, ListExpression())),
        )
        self._testCases(cases)

    def _testCases(self, cases):
        for expression, result in cases:
            self.assertEqual(
                Expression("FullSimplify", expression).evaluate(self.evaluation),
                Expression("FullSimplify", result).evaluate(self.evaluation),
            )


if __name__ == "__main__":
    unittest.main()
