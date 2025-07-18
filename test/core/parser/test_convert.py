import random
import sys
import unittest

from mathics_scanner import SingleLineFeeder
from mathics_scanner.errors import (
    IncompleteSyntaxError,
    InvalidSyntaxError,
    SyntaxError,
)
from mathics_scanner.location import ContainerKind

from mathics.core.atoms import Integer, Integer0, Integer1, Rational, Real, String
from mathics.core.definitions import Definitions
from mathics.core.expression import Expression
from mathics.core.load_builtin import import_and_load_builtins
from mathics.core.parser import parse as core_parse
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolDerivative

import_and_load_builtins()
definitions = Definitions(add_builtin=True)


class ConvertTests(unittest.TestCase):
    def parse(self, source_text):
        return core_parse(
            definitions,
            SingleLineFeeder(source_text, "<test_convert>", ContainerKind.STRING),
        )

    def check(self, expr1, expr2):
        if isinstance(expr1, str):
            expr1 = self.parse(expr1)
        if isinstance(expr2, str):
            expr2 = self.parse(expr2)

        if expr1 is None:
            assert expr2 is None
        else:
            assert expr1.sameQ(expr2)

    def scan_error(self, string):
        self.assertRaises(SyntaxError, self.parse, string)

    def incomplete_error(self, string):
        self.assertRaises(IncompleteSyntaxError, self.parse, string)

    def invalid_error(self, string):
        self.assertRaises(InvalidSyntaxError, self.parse, string)

    def testSymbol(self):
        self.check("xX", Symbol("Global`xX"))
        self.check("context`name", Symbol("context`name"))
        self.check("`name", Symbol("Global`name"))
        self.check("`context`name", Symbol("Global`context`name"))

    def testInteger(self):
        self.check("0", Integer0)
        self.check("1", Integer1)
        self.check("-1", Integer(-1))

        self.check("8^^23", Integer(19))
        self.check("10*^3", Integer(10000))
        self.check("10*^-3", Rational(1, 100))
        self.check("8^^23*^2", Integer(1216))
        self.check("2^^0101", Integer(5))
        self.check(
            "36^^0123456789abcDEFxyzXYZ", Integer(14142263610074677021975869033659)
        )

        n = random.randint(-sys.maxsize, sys.maxsize)
        self.check(str(n), Integer(n))

        n = random.randint(sys.maxsize, sys.maxsize * sys.maxsize)
        self.check(str(n), Integer(n))

        # Requested base 1 in 1^^2 should be between 2 and 36.
        self.invalid_error(r"1^^2")
        # Requested base 37 in 37^^3 should be between 2 and 36.
        self.invalid_error(r"37^^3")
        # Digit at position 3 in 01210 is too large to be used in base 2.
        self.invalid_error(r"2^^01210")
        # "Digit at position 2 in 5g is too large to be used in base 16."
        self.invalid_error(r"16^^5g")

    def testReal(self):
        self.check("1.5", Real("1.5"))
        self.check("1.5`", Real("1.5"))
        self.check("0.0", Real(0))
        self.check("-1.5`", Real("-1.5"))
        self.check("0`3", Integer(0))
        self.check("0``3", "0.000`3")
        self.check("0.`3", "0.000`3")
        self.check("0.``3", "0.000``3")
        ## Mathematica treats zero strangely
        self.check("0.00000000000000000", "0.")
        self.check("0.000000000000000000`", "0.")
        self.check("0.000000000000000000", "0.``18")
        # Parse *^ notation
        self.check("1.5×10^24", Real(1.5) * Integer(10) ** Integer(24))
        self.check("1.5*^+24", Real("1.5e24"))
        self.check("1.5*^-24", Real("1.5e-24"))
        ## Don't accept *^ with spaces
        # > 1.5 *^10
        # "1.5*" cannot be followed by "^ 10"
        self.invalid_error("1.5 *^10")
        # "1.5*" cannot be followed by "^ 10"
        self.invalid_error("1.5*^ 10")

    def testString(self):
        self.check(r'"abc"', String("abc"))
        self.incomplete_error(r'"abc')
        self.check(r'"abc(*def*)"', String("abc(*def*)"))
        self.check(r'"a\"b\\c"', String(r'a"b\c'))
        self.check(r'"a\\nb"', String(r"a\nb"))
        self.incomplete_error(r'"\"')
        self.invalid_error(r'\""')

    def testAccuracy(self):
        self.scan_error("1.5``")
        self.check("1.0``20", Real("1.0", p=20))

    @unittest.expectedFailure
    def testLowAccuracy(self):
        self.check("1.4``0", Real(0))
        self.check("1.4``-20", Real(0))

    def testPrecision(self):
        self.check("1.`20", Real(1, p=20))
        self.check("1.00000000000000000000000`", Real(1))
        self.check("1.00000000000000000000000`30", Real(1, p=30))

    @unittest.expectedFailure
    def testLowPrecision(self):
        self.check("1.4`1", Real("1", p=1))
        self.check("1.4`0", Real(0, p=0))
        self.check("1.4`-5", Real(0, p=0))

    def testDerivative(self):
        f = Symbol("Global`f")
        self.check("f'", Expression(Expression(SymbolDerivative, Integer1), f))
        self.check("f''", Expression(Expression(SymbolDerivative, Integer(2)), f))
        self.check(
            "(f'')'''",
            Expression(
                Expression(SymbolDerivative, Integer(3)),
                Expression(Expression(SymbolDerivative, Integer(2)), f),
            ),
        )
        self.check("Derivative[f]", Expression(SymbolDerivative, f))
        self.check("Derivative[1][f]'", "(f')'")
