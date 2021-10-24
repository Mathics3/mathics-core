#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import unittest
from mathics.core.expression import Expression
from mathics.core.atoms import Integer, Rational, from_python
from mathics.core.symbols import Symbol
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation


class ArithmeticTest(unittest.TestCase):
    def setUp(self):
        definitions = Definitions(add_builtin=True)
        self.evaluation = Evaluation(definitions, format="xml")

    def testAdd(self):
        cases = (
            (Symbol("a") + 3, Expression("Plus", Integer(3), Symbol("a"))),
            (Integer(1) + 3, Integer(4)),
            (Integer(1) + (-3), Integer(-2)),
            (
                Expression("List", Integer(1), Integer(2))
                + Expression("List", from_python(-1), from_python(8)),
                Expression("List", from_python(0), from_python(10)),
            ),
        )
        self._testCases(cases)

    def testSub(self):
        cases = (
            (Symbol("a") - 3, Expression("Plus", from_python(-3), Symbol("a"))),
            (Integer(1) - 3, Integer(-2)),
            (Integer(1) - (-3), Integer(4)),
            (
                Expression("List", Integer(1), Integer(2))
                - Expression("List", from_python(-1), from_python(8)),
                Expression("List", from_python(2), from_python(-6)),
            ),
        )
        self._testCases(cases)

    def testMul(self):
        cases = (
            (Symbol("a") * 3, Expression("Times", from_python(3), Symbol("a"))),
            (Integer(3) * 7, Integer(21)),
            (Integer(3) * (-7), Integer(-21)),
            (
                Expression("List", from_python(1), from_python(2))
                * Expression("List", from_python(-1), from_python(8)),
                Expression("List", from_python(-1), from_python(16)),
            ),
        )
        self._testCases(cases)

    def testTrueDiv(self):
        cases = (
            (Symbol("a") / 3, Expression("Times", Rational(1, 3), Symbol("a"))),
            (Integer(8) / 2, Integer(4)),
            (Integer(8) / (-2), Integer(-4)),
            (Integer(7) / 2, Rational(7, 2)),
            (
                Expression("List", from_python(1), from_python(9))
                / Expression("List", from_python(-1), from_python(3)),
                Expression("List", from_python(-1), from_python(3)),
            ),
        )
        self._testCases(cases)

    def testFloorDiv(self):
        cases = (
            (Integer(8) // 2, Integer(4)),
            (Integer(8) // (-2), Integer(-4)),
            (Integer(7) // 2, Integer(3)),
        )
        self._testCases(cases)

    def testPow(self):
        cases = (
            (Integer(8) ** 2, Integer(64)),
            (
                Expression("List", from_python(2), from_python(5))
                ** Expression("List", from_python(3), from_python(4)),
                Expression("List", from_python(8), from_python(625)),
            ),
        )
        self._testCases(cases)

    def testAbs(self):
        cases = (
            (abs(Integer(-8)), Integer(8)),
            (abs(Expression("List")), Expression("Abs", Expression("List"))),
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
