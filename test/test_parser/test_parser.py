#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import random
import unittest

from mathics_scanner import (
    IncompleteSyntaxError,
    InvalidSyntaxError,
    ScanError,
    SingleLineFeeder,
)

from mathics.core.parser.ast import (
    Node,
    SymbolNode,
    NumberNode,
    StringNode,
    FilenameNode,
)
from mathics.core.parser.parser import Parser


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def parse(self, s):
        return self.parser.parse(SingleLineFeeder(s))

    def check(self, expr1, expr2):
        if isinstance(expr1, str):
            expr1 = self.parse(expr1)
        if isinstance(expr2, str):
            expr2 = self.parse(expr2)

        if expr1 is None:
            self.assertIsNone(expr2)
        else:
            self.assertEqual(repr(expr1), repr(expr2))
            self.assertEqual(expr1, expr2)

    def scan_error(self, string):
        self.assertRaises(ScanError, self.parse, string)

    def incomplete_error(self, string):
        self.assertRaises(IncompleteSyntaxError, self.parse, string)

    def invalid_error(self, string):
        self.assertRaises(InvalidSyntaxError, self.parse, string)


class PrecedenceTests(ParserTests):
    def test_minuslike(self):
        self.check("a * + b", "Times[a, Plus[b]]")
        self.check("- a . b", "Times[-1, Dot[a, b]]"),
        self.check("- a / b", "Times[-1, a, Power[b, -1]]"),
        self.check("- a / - b", "Times[-1, a, Power[Times[-1, b], -1]]")
        self.check("- a / - b", "Times[-1, a, Power[Times[-1, b], -1]]")
        self.check("a + b!", "Plus[a, Factorial[b]]")
        self.check("!a!", "Not[Factorial[a]]")
        self.check("+ + a", "Plus[a]")  # only one plus


class AssocTests(ParserTests):
    def test_right(self):
        self.check("a ^ b ^ c", "a ^ (b ^ c)")

    def test_flat(self):
        self.check("a + b + c", "Plus[a, b, c]")

    def test_left(self):
        self.check("a /; b /; c", "(a /; b) /; c")

    def test_Subtract(self):
        self.check("a - b - c", "Plus[a, Times[-1, b], Times[-1, c]]")
        self.check("(a - b) - c", "Plus[Plus[a, Times[-1, b]], Times[-1, c]]")

    def test_nonassoc(self):
        self.invalid_error("a ? b ? c")

    def test_Function(self):
        self.check("a==b&", "Function[Equal[a, b]]")
        self.check("First[#]==sse&", "Function[Equal[First[Slot[1]], sse]]")


class AtomTests(ParserTests):
    def check_number(self, s):
        self.assertEqual(self.parse(s), NumberNode(s))

    def testSymbol(self):
        self.check("xX", SymbolNode("xX"))
        self.check("context`name", SymbolNode("context`name"))
        self.check("`name", SymbolNode("`name"))
        self.check("`context`name", SymbolNode("`context`name"))

    def testSpecialSymbol(self):
        self.check("\\[Pi]", "Pi")
        self.check("\\[Degree]", "Degree")
        self.check("\\[ExponentialE]", "E")
        self.check("\\[ImaginaryI]", "I")
        self.check("\\[ImaginaryJ]", "I")
        self.check("\\[Infinity]", "Infinity")

    def testNumberNode(self):
        self.check_number("0")
        self.check_number("-1")
        self.check("- 1", "-1")
        self.check("- - 1", "Times[-1, -1]")
        self.check("x=.01", "x = .01")

    def testNumberBase(self):
        self.check_number("8^^23")
        self.check_number("10*^3")
        self.check_number("10*^-3")
        self.check_number("8^^23*^2")
        self.invalid_error("2^^102")
        self.invalid_error("2^^10.2")
        self.invalid_error("1^^0")
        self.invalid_error("37^^0")
        self.check_number("36^^abcxyz01239")
        self.check_number("6^^5023`307*^-720")

    def testNumberBig(self):
        for _ in range(10):
            self.check_number(str(random.randint(-sys.maxsize, sys.maxsize)))
            self.check_number(
                str(random.randint(sys.maxsize, sys.maxsize * sys.maxsize))
            )

    def testNumberReal(self):
        self.check_number("1.5")
        self.check_number("1.5`")
        self.check_number("0.0")
        self.check_number("-1.5`")

        self.check_number("0.00000000000000000")
        self.check_number("0.000000000000000000`")
        self.check_number("0.000000000000000000")

    def testString(self):
        self.check(r'"abc"', StringNode("abc"))
        self.incomplete_error(r'"abc')
        self.check(r'"abc(*def*)"', StringNode("abc(*def*)"))
        self.check(r'"a\"b\\c"', StringNode(r"a\"b\\c"))
        self.incomplete_error(r'"\"')
        self.invalid_error(r'\""')

    def testAccuracy(self):
        self.scan_error("1.5``")
        self.check_number("1.0``20")
        self.check_number("1.4``0")
        self.check_number("1.4``-20")

    def testPrecision(self):
        self.check_number("1.`20")
        self.check_number("1.00000000000000000000000`")
        self.check_number("1.00000000000000000000000`30")
        self.check_number("1.4`1")


class GeneralTests(ParserTests):
    def testCompound(self):
        self.check(
            "a ; {b}",
            Node("CompoundExpression", SymbolNode("a"), Node("List", SymbolNode("b"))),
        )
        self.check(
            "1 ;", Node("CompoundExpression", NumberNode("1"), SymbolNode("Null"))
        )
        self.check(
            "1 ; 5", Node("CompoundExpression", NumberNode("1"), NumberNode("5"))
        )
        self.check(
            "4; 1 ; 5",
            Node(
                "CompoundExpression", NumberNode("4"), NumberNode("1"), NumberNode("5")
            ),
        )
        self.check(
            "4;1;",
            Node(
                "CompoundExpression",
                NumberNode("4"),
                NumberNode("1"),
                SymbolNode("Null"),
            ),
        )
        self.check(
            "(a;b);c",
            Node(
                "CompoundExpression",
                Node("CompoundExpression", SymbolNode("a"), SymbolNode("b")),
                SymbolNode("c"),
            ),
        )
        self.check("f[a;]", "f[CompoundExpression[a, Null]]")

    def testMessage(self):
        self.check(
            '1 :: "abc"', Node("MessageName", NumberNode("1"), StringNode("abc"))
        )
        self.check(
            '1 :: "abc" :: "123"',
            Node("MessageName", NumberNode("1"), StringNode("abc"), StringNode("123")),
        )

    def testGetPut(self):
        self.check('<<"filename"', Node("Get", FilenameNode('"filename"')))
        self.check(
            "1 >> filename", Node("Put", NumberNode("1"), FilenameNode("filename"))
        )
        self.check(
            "1 >>> filename",
            Node("PutAppend", NumberNode("1"), FilenameNode("filename")),
        )
        self.check("<< filename", Node("Get", FilenameNode("filename")))

    def testExpression(self):
        self.check("expr1[expr2]", Node("expr1", SymbolNode("expr2")))
        self.check(
            "expr1[expr2][expr3]",
            Node(Node("expr1", SymbolNode("expr2")), SymbolNode("expr3")),
        )
        self.check(
            "expr1[[expr2]]", Node("Part", SymbolNode("expr1"), SymbolNode("expr2"))
        )
        self.check(
            "expr1[[expr2, expr3]]",
            Node("Part", SymbolNode("expr1"), SymbolNode("expr2"), SymbolNode("expr3")),
        )
        self.check(
            "expr1[[expr2]][[expr3]]",
            Node(
                "Part",
                Node("Part", SymbolNode("expr1"), SymbolNode("expr2")),
                SymbolNode("expr3"),
            ),
        )

        self.check(
            "expr1 ~ expr2 ~ expr3",
            Node("expr2", SymbolNode("expr1"), SymbolNode("expr3")),
        )
        self.check("x~f~y", "f[x, y]")

    def testFunctional(self):
        self.check("expr1 @ expr2", Node("expr1", SymbolNode("expr2")))
        self.check("f @@ expr", Node("Apply", SymbolNode("f"), SymbolNode("expr")))
        self.check("f /@ expr", Node("Map", SymbolNode("f"), SymbolNode("expr")))

        self.check(
            "f @@@ expr",
            Node(
                "Apply",
                SymbolNode("f"),
                SymbolNode("expr"),
                Node("List", NumberNode("1")),
            ),
        )
        self.check("f //@ expr", Node("MapAll", SymbolNode("f"), SymbolNode("expr")))
        self.check(
            "a @@ b @@ c",
            Node(
                "Apply",
                SymbolNode("a"),
                Node("Apply", SymbolNode("b"), SymbolNode("c")),
            ),
        )

        self.check("a /@ b @@ c", "Map[a, Apply[b, c]]")
        self.check("a @@ b /@ c", "Apply[a, Map[b, c]]")

    def testFunction(self):
        self.check("x &", Node("Function", SymbolNode("x")))
        self.check("x \\[Function] y", "Function[x, y]")
        self.check("x \uf4a1 y", "Function[x, y]")
        self.incomplete_error("x \uf4a1")
        self.check(
            "x & y", Node("Times", Node("Function", SymbolNode("x")), SymbolNode("y"))
        )

    def testPostfix(self):
        self.check("x // y", Node("y", SymbolNode("x")))
        self.check("x // y // z", "(x // y) // z")
        self.check("a | b // c | d", "(a | b) // (c | d)")

    def testIncDec(self):
        self.check("a++", Node("Increment", SymbolNode("a")))
        self.check("a--", Node("Decrement", SymbolNode("a")))
        self.check("++a", Node("PreIncrement", SymbolNode("a")))
        self.check("--a", Node("PreDecrement", SymbolNode("a")))

    def testBang(self):
        self.check("5!", Node("Factorial", NumberNode("5")))
        self.check("5 !", Node("Factorial", NumberNode("5")))
        self.check("5 ! !", Node("Factorial", Node("Factorial", NumberNode("5"))))
        self.check("!1", Node("Not", NumberNode("1")))
        self.check("5 !!", Node("Factorial2", NumberNode("5")))
        self.check(
            "x ! y", Node("Times", Node("Factorial", SymbolNode("x")), SymbolNode("y"))
        )

    def testDerivative(self):
        self.check("f'", "Derivative[1][f]")
        self.check("f''", "Derivative[2][f]")
        self.check("f' '", "Derivative[2][f]")

    def testPlus(self):
        self.check("+1", Node("Plus", NumberNode("1")))
        self.check("1 + 2", Node("Plus", NumberNode("1"), NumberNode("2")))
        self.check(
            "1 + 2 + 3", Node("Plus", NumberNode("1"), NumberNode("2"), NumberNode("3"))
        )
        self.check("1 + 2 + 3 + 4", "Plus[1, 2, 3, 4]")
        self.check("-a", Node("Times", NumberNode("-1"), SymbolNode("a")))
        self.check(
            "a - b",
            Node(
                "Plus",
                SymbolNode("a"),
                Node("Times", NumberNode("-1"), SymbolNode("b")),
            ),
        )

        self.check(
            "a*b+c",
            Node(
                "Plus", Node("Times", SymbolNode("a"), SymbolNode("b")), SymbolNode("c")
            ),
        )
        self.check(
            "a*+b+c",
            Node(
                "Plus",
                Node("Times", SymbolNode("a"), Node("Plus", SymbolNode("b"))),
                SymbolNode("c"),
            ),
        )
        self.check("a+b*c", "a+(b*c)")
        self.check("a*b+c", "(a*b) + c")
        self.check("1-2", "1 - 2")

    def testTimes(self):
        self.check("1 2", Node("Times", NumberNode("1"), NumberNode("2")))
        self.check("1*2", Node("Times", NumberNode("1"), NumberNode("2")))

        self.check(
            "1 2 3", Node("Times", NumberNode("1"), NumberNode("2"), NumberNode("3"))
        )
        self.check(
            "(1 2) 3",
            Node(
                "Times",
                Node("Times", NumberNode("1"), NumberNode("2")),
                NumberNode("3"),
            ),
        )
        self.check(
            "1*2*3", Node("Times", NumberNode("1"), NumberNode("2"), NumberNode("3"))
        )

        self.check(
            "x ^ 2 y",
            Node(
                "Times",
                Node("Power", SymbolNode("x"), NumberNode("2")),
                SymbolNode("y"),
            ),
        )

    def testSpan(self):
        self.check(";;", Node("Span", NumberNode("1"), SymbolNode("All")))
        self.check(
            "a;;b;;",
            Node(
                "Times",
                Node("Span", SymbolNode("a"), SymbolNode("b")),
                Node("Span", NumberNode("1"), SymbolNode("All")),
            ),
        )
        self.check(
            "1;;2;;3", Node("Span", NumberNode("1"), NumberNode("2"), NumberNode("3"))
        )
        self.check(
            "1;; ;;3", Node("Span", NumberNode("1"), SymbolNode("All"), NumberNode("3"))
        )
        self.check(
            "1;;;;3", Node("Span", NumberNode("1"), SymbolNode("All"), NumberNode("3"))
        )
        self.check(
            "1;;2;;",
            Node(
                "Times",
                Node("Span", NumberNode("1"), NumberNode("2")),
                Node("Span", NumberNode("1"), SymbolNode("All")),
            ),
        )
        self.check(
            " ;;2;;3", Node("Span", NumberNode("1"), NumberNode("2"), NumberNode("3"))
        )
        self.check(" ;;2", Node("Span", NumberNode("1"), NumberNode("2")))
        self.check("1;; ", Node("Span", NumberNode("1"), SymbolNode("All")))
        self.check(" ;; ", Node("Span", NumberNode("1"), SymbolNode("All")))
        self.check(
            "1;;2;;3;;4;;5;;6", "Times[Span[1, 2, 3], Span[1, 4, 5], Span[1, 6]]"
        )
        self.check("(a;;b);;c", "Span[Span[a, b], c]")

    @unittest.expectedFailure
    def testSpanNot(self):
        self.check("a ;; !b", "Times[Span[a, All], Not[b]]")

    def testBinOp(self):
        self.check("1 <> 2 ", Node("StringJoin", NumberNode("1"), NumberNode("2")))
        self.check(
            "1 <> 2 <> 3",
            Node("StringJoin", NumberNode("1"), NumberNode("2"), NumberNode("3")),
        )

        self.check("1 ^ 2", Node("Power", NumberNode("1"), NumberNode("2")))
        self.check("1 . 2", Node("Dot", NumberNode("1"), NumberNode("2")))
        self.check("1 && 2", Node("And", NumberNode("1"), NumberNode("2")))
        self.check("1 || 2", Node("Or", NumberNode("1"), NumberNode("2")))

        self.check("x /; y", Node("Condition", SymbolNode("x"), SymbolNode("y")))
        self.check("x -> y", Node("Rule", SymbolNode("x"), SymbolNode("y")))
        self.check("x :> y", Node("RuleDelayed", SymbolNode("x"), SymbolNode("y")))

        self.check("x /. y", Node("ReplaceAll", SymbolNode("x"), SymbolNode("y")))
        self.check("x //. y", Node("ReplaceRepeated", SymbolNode("x"), SymbolNode("y")))

        self.check("x += y", Node("AddTo", SymbolNode("x"), SymbolNode("y")))
        self.check("x -= y", Node("SubtractFrom", SymbolNode("x"), SymbolNode("y")))
        self.check("x *= y", Node("TimesBy", SymbolNode("x"), SymbolNode("y")))
        self.check("x /= y", Node("DivideBy", SymbolNode("x"), SymbolNode("y")))

        self.check(
            "3/2",
            Node(
                "Times",
                NumberNode("3"),
                Node("Power", NumberNode("2"), NumberNode("-1")),
            ),
        )

        self.check("x ~~ y", Node("StringExpression", SymbolNode("x"), SymbolNode("y")))
        self.check(
            "x ~~ y ~~ z",
            Node("StringExpression", SymbolNode("x"), SymbolNode("y"), SymbolNode("z")),
        )

    def testCompare(self):
        self.check("1 == 2", Node("Equal", NumberNode("1"), NumberNode("2")))
        self.check("1 != 2", Node("Unequal", NumberNode("1"), NumberNode("2")))
        self.check(
            "1 == 2 == 3",
            Node("Equal", NumberNode("1"), NumberNode("2"), NumberNode("3")),
        )
        self.check(
            "1 != 2 != 3",
            Node("Unequal", NumberNode("1"), NumberNode("2"), NumberNode("3")),
        )

        self.check("1 > 2", Node("Greater", NumberNode("1"), NumberNode("2")))
        self.check("1 >= 2", Node("GreaterEqual", NumberNode("1"), NumberNode("2")))
        self.check("1 < 2", Node("Less", NumberNode("1"), NumberNode("2")))
        self.check("1 <= 2", Node("LessEqual", NumberNode("1"), NumberNode("2")))

        self.check(
            "1 > 2 > 3",
            Node("Greater", NumberNode("1"), NumberNode("2"), NumberNode("3")),
        )
        self.check(
            "1 >= 2 >= 3",
            Node("GreaterEqual", NumberNode("1"), NumberNode("2"), NumberNode("3")),
        )
        self.check(
            "1 < 2 < 3", Node("Less", NumberNode("1"), NumberNode("2"), NumberNode("3"))
        )
        self.check(
            "1 <= 2 <= 3",
            Node("LessEqual", NumberNode("1"), NumberNode("2"), NumberNode("3")),
        )

        self.check("1 === 2", Node("SameQ", NumberNode("1"), NumberNode("2")))
        self.check("1 =!= 2", Node("UnsameQ", NumberNode("1"), NumberNode("2")))
        self.check(
            "1 === 2 === 3",
            Node("SameQ", NumberNode("1"), NumberNode("2"), NumberNode("3")),
        )
        self.check(
            "1 =!= 2 =!= 3",
            Node("UnsameQ", NumberNode("1"), NumberNode("2"), NumberNode("3")),
        )

    def testRepeated(self):
        self.check("1..", Node("Repeated", NumberNode("1")))
        self.check("1...", Node("RepeatedNull", NumberNode("1")))

    def testAlternatives(self):
        self.check("1 | 2", Node("Alternatives", NumberNode("1"), NumberNode("2")))
        self.check(
            "1 | 2 | 3",
            Node("Alternatives", NumberNode("1"), NumberNode("2"), NumberNode("3")),
        )

    def testSet(self):
        self.check("x = y", Node("Set", SymbolNode("x"), SymbolNode("y")))
        self.check("x := y", Node("SetDelayed", SymbolNode("x"), SymbolNode("y")))
        self.check("x ^= y", Node("UpSet", SymbolNode("x"), SymbolNode("y")))
        self.check("x ^:= y", Node("UpSetDelayed", SymbolNode("x"), SymbolNode("y")))
        self.check("x =.", Node("Unset", SymbolNode("x")))
        self.check(
            "x/:1=1", Node("TagSet", SymbolNode("x"), NumberNode("1"), NumberNode("1"))
        )
        self.check(
            "x/:1:=1",
            Node("TagSetDelayed", SymbolNode("x"), NumberNode("1"), NumberNode("1")),
        )
        self.check("x/:1=.", Node("TagUnset", SymbolNode("x"), NumberNode("1")))
        self.check(
            "f /: f[x_] + f[y_] := x + y", "TagSetDelayed[f, f[x_] + f[y_], x + y]"
        )

    def testList(self):
        self.check("{x, y}", Node("List", SymbolNode("x"), SymbolNode("y")))

        self.check("{1}", Node("List", NumberNode("1")))
        self.check("{}", Node("List"))
        self.check("{a,}", Node("List", SymbolNode("a"), SymbolNode("Null")))
        self.check("{,}", Node("List", SymbolNode("Null"), SymbolNode("Null")))

        self.check(
            "{a, b,}",
            Node("List", SymbolNode("a"), SymbolNode("b"), SymbolNode("Null")),
        )

        self.check("{,a}", Node("List", SymbolNode("Null"), SymbolNode("a")))
        self.check(
            "{, a, b}",
            Node("List", SymbolNode("Null"), SymbolNode("a"), SymbolNode("b")),
        )
        self.check(
            "{,a,b,}",
            Node(
                "List",
                SymbolNode("Null"),
                SymbolNode("a"),
                SymbolNode("b"),
                SymbolNode("Null"),
            ),
        )

    def testAssociation(self):
        self.check(
            "<|x -> m|>",
            Node("Association", Node("Rule", SymbolNode("x"), SymbolNode("m"))),
        )

    def testSequence(self):
        self.check("Sin[x, y]", Node("Sin", SymbolNode("x"), SymbolNode("y")))

    def testPart(self):
        self.check("a[[1]]", Node("Part", SymbolNode("a"), NumberNode("1")))

    def testSlot(self):
        self.check("#2", Node("Slot", NumberNode("2")))
        self.check("#", Node("Slot", NumberNode("1")))
        self.check("##2", Node("SlotSequence", NumberNode("2")))
        self.check("##", Node("SlotSequence", NumberNode("1")))
        self.check("%2", Node("Out", NumberNode("2")))
        self.check("#a", 'Slot["a"]')

    @unittest.expectedFailure
    def testNonLetterSymbol(self):
        self.incomplete_error("#\\[Equal]")
        self.check("#\uf431", 'Slot["\\[Equal]"]')
        self.check("a\uf431c", Node("Symbol", "a\uf431c"))
        self.check("a\uf522c", Node("Symbol", "a\uf522c"))

    def testOut(self):
        self.check("%%", Node("Out", NumberNode("-2")))
        self.check("%%%%", Node("Out", NumberNode("-4")))
        self.check("%", Node("Out"))

    def testNonAscii(self):
        self.check("z \\[Conjugate]", Node("Conjugate", SymbolNode("z")))
        self.check("z \\[Transpose]", Node("Transpose", SymbolNode("z")))
        self.check(
            "z \\[ConjugateTranspose]", Node("ConjugateTranspose", SymbolNode("z"))
        )
        self.check("z \uf3c7 ", Node("Transpose", SymbolNode("z")))
        self.check("z \uf3c8 ", Node("Conjugate", SymbolNode("z")))
        self.check("z \uf3c9 ", Node("ConjugateTranspose", SymbolNode("z")))
        self.check(
            "\\[Integral] x \\[DifferentialD] x",
            Node("Integrate", SymbolNode("x"), SymbolNode("x")),
        )
        self.check("\\[Del] x", Node("Del", SymbolNode("x")))
        self.check("\\[Square] x", Node("Square", SymbolNode("x")))
        self.check(
            "1 \\[SmallCircle] 2", Node("SmallCircle", NumberNode("1"), NumberNode("2"))
        )
        self.check(
            "1 \\[SmallCircle] 2 \\[SmallCircle] 3",
            Node("SmallCircle", NumberNode("1"), NumberNode("2"), NumberNode("3")),
        )
        self.check("1 \u2218 2", Node("SmallCircle", NumberNode("1"), NumberNode("2")))
        self.check(
            "1 \\[CircleDot] 2", Node("CircleDot", NumberNode("1"), NumberNode("2"))
        )
        self.check("1 \u2299 2", Node("CircleDot", NumberNode("1"), NumberNode("2")))
        self.check("1 \\[Diamond] 2", Node("Diamond", NumberNode("1"), NumberNode("2")))
        self.check("1 \\[Wedge] 2", Node("Wedge", NumberNode("1"), NumberNode("2")))
        self.check("1 \\[Vee] 2", Node("Vee", NumberNode("1"), NumberNode("2")))
        self.check(
            "1 \\[CircleTimes] 2", Node("CircleTimes", NumberNode("1"), NumberNode("2"))
        )
        self.check(
            "1 \\[CenterDot] 2", Node("CenterDot", NumberNode("1"), NumberNode("2"))
        )
        self.check("1 \\[Star] 2", Node("Star", NumberNode("1"), NumberNode("2")))
        self.check("a \\[Cap] b", "Cap[a,b]")
        self.check("a \\[Cup] b \\[Cup] c", "Cup[a,b,c]")
        self.check("a \u2322 b \u2322 c", "Cap[a,b,c]")
        self.check("a \u2323 b", "Cup[a, b]")
        self.check("1 \u22C4 2", Node("Diamond", NumberNode("1"), NumberNode("2")))
        self.check("1 \u22C0 2", Node("Wedge", NumberNode("1"), NumberNode("2")))
        self.check("1 \u22c1 2", Node("Vee", NumberNode("1"), NumberNode("2")))
        self.check("1 \u2297 2", Node("CircleTimes", NumberNode("1"), NumberNode("2")))
        self.check("1 \u00B7 2", Node("CenterDot", NumberNode("1"), NumberNode("2")))
        self.check("1 \u22C6 2", Node("Star", NumberNode("1"), NumberNode("2")))
        self.check(
            "expr1 ** expr2",
            Node("NonCommutativeMultiply", SymbolNode("expr1"), SymbolNode("expr2")),
        )
        self.check(
            "expr1 ** expr2 ** expr3",
            Node(
                "NonCommutativeMultiply",
                SymbolNode("expr1"),
                SymbolNode("expr2"),
                SymbolNode("expr3"),
            ),
        )
        self.check("1 \\[Cross] 2", Node("Cross", NumberNode("1"), NumberNode("2")))
        self.check("1 \uf4a0 2", Node("Cross", NumberNode("1"), NumberNode("2")))
        self.check(
            "3\\[Divide]2",
            Node(
                "Times",
                NumberNode("3"),
                Node("Power", NumberNode("2"), NumberNode("-1")),
            ),
        )
        self.check("3 \u00f7 2", "Times[3, Power[2, -1]]")
        self.scan_error("3\\2")
        self.check("1 \\[Times] 2", Node("Times", NumberNode("1"), NumberNode("2")))
        self.check("1 \u00d7 2", Node("Times", NumberNode("1"), NumberNode("2")))
        self.check(
            "1 \\[PlusMinus] 2", Node("PlusMinus", NumberNode("1"), NumberNode("2"))
        )
        self.check(
            "1 \\[MinusPlus] 2", Node("MinusPlus", NumberNode("1"), NumberNode("2"))
        )
        self.check("\\[PlusMinus] 1", Node("PlusMinus", NumberNode("1")))
        self.check("\\[MinusPlus] 1", Node("MinusPlus", NumberNode("1")))
        self.check("\u00b1 1", Node("PlusMinus", NumberNode("1")))
        self.check("\u2213 1", Node("MinusPlus", NumberNode("1")))
        self.check("1 \\[And] 2", Node("And", NumberNode("1"), NumberNode("2")))
        self.check("1 \u2227 2", Node("And", NumberNode("1"), NumberNode("2")))
        self.check("1 \\[Or] 2", Node("Or", NumberNode("1"), NumberNode("2")))
        self.check("1 \u2228 2", Node("Or", NumberNode("1"), NumberNode("2")))

        self.check("a \\[Colon] b", Node("Colon", SymbolNode("a"), SymbolNode("b")))
        self.check("a \u2236 b", Node("Colon", SymbolNode("a"), SymbolNode("b")))

        self.check("x1 \\[RightTee] x2", "RightTee[x1, x2]")
        self.check("x1 \\[DoubleRightTee] x2", "DoubleRightTee[x1, x2]")
        self.check("x1 \\[LeftTee] x2", "LeftTee[x1, x2]")
        self.check("x1 \\[DoubleLeftTee] x2", "DoubleLeftTee[x1, x2]")

    def testMessageName(self):
        self.check("a::b", 'MessageName[a, "b"]')
        self.check('a::"b"', 'MessageName[a, "b"]')
        self.check("a::b::c", 'MessageName[a, "b", "c"]')

    def testBoolean(self):
        # And = Nand > Xor = Xnor > Or = Nor
        self.check(r"a && b || c", r"(a && b) || c")
        self.check(r"a || b && c", r"a || (b && c)")
        self.check(r"a && b \[Xor] c", r"(a && b) \[Xor] c")
        self.check(r"a && b \[Xnor] c", r"(a && b) \[Xnor] c")
        self.check(r"a && b \[Nor] c", r"(a && b) \[Nor] c")
        self.check(r"a \[Xor] b || c", r"(a \[Xor] b) || c")
        self.check(r"a \[Xnor] b || c", r"(a \[Xnor] b) || c")
        self.check(r"a \[Xor] b \[Nor] c", r"(a \[Xor] b) \[Nor] c")
        self.check(r"a \[Xnor] b \[Nor] c", r"(a \[Xnor] b) \[Nor] c")

        # when the precs agree be left assoc
        self.check(r"a && b \[Nand] c", r"(a && b) \[Nand] c")
        self.check(r"a \[Nand] b && c", r"(a \[Nand] b) && c")
        self.check(r"a \[Xor] b \[Xnor] c", r"(a \[Xor] b) \[Xnor] c")
        self.check(r"a \[Xnor] b \[Xor] c", r"(a \[Xnor] b) \[Xor] c")
        self.check(r"a \[Or] b \[Nor] c", r"(a \[Or] b) \[Nor] c")
        self.check(r"a \[Nor] b \[Or] c", r"(a \[Nor] b) \[Or] c")

        # boolean ops are flat
        self.check("a && b && c", "And[a, b, c]")
        self.check("a || b || c", "Or[a, b, c]")
        self.check("a || b || c && d || e", "a || b || (c && d) || e")
        self.check("a && b && c || d && e", "(a && b && c) || (d && e)")

    def testInequality(self):
        self.check("a < b <= c", "Inequality[a, Less, b, LessEqual, c]")
        self.check("a < b < c", "Less[a, b, c]")
        self.check(
            "a < b <= c > d >= e != f == g",
            "Inequality[a, Less, b, LessEqual, c, Greater, d, GreaterEqual, e,  Unequal, f, Equal, g]",
        )

    def testInformation(self):
        self.check("??a", "Information[a, LongForm -> True]")
        self.check("a ?? b", "a Information[b, LongForm -> True]")
        self.invalid_error("a ?? + b")
        self.check("a + ?? b", "a + Information[b, LongForm -> True]")
        self.check("??a + b", "Information[a, LongForm -> True] + b")
        self.check("??a * b", "Information[a, Rule[LongForm, True]]*b")


class BoxTests(ParserTests):
    def testSqrt(self):
        self.check("\\( \\@ b \\)", 'SqrtBox["b"]')
        self.check("\\( \\@ b \\% c \\)", 'RadicalBox["b", "c"]')
        self.check("\\(a \\@ b \\)", 'RowBox[{"a", SqrtBox["b"]}]')
        self.check("\\( \\@ \\)", 'SqrtBox[""]')

    def testSuperscript(self):
        self.check("\\(a \\^ b \\)", 'SuperscriptBox["a", "b"]')
        self.check("\\(a \\^ b \\% c\\)", 'SubsuperscriptBox["a", "c", "b"]')
        self.check("\\(a \\_ b \\)", 'SubscriptBox["a", "b"]')
        self.check("\\(a \\_ b \\% c\\)", 'SubsuperscriptBox["a", "b", "c"]')

        self.check("\\(  \\^ a \\)", 'SuperscriptBox["", "a"]')
        self.check("\\(a \\^   \\)", 'SuperscriptBox["a", ""]')
        self.check("\\(  \\^   \\)", 'SuperscriptBox["", ""]')

        self.check("\\(  \\_ a \\)", 'SubscriptBox["", "a"]')
        self.check("\\(a \\_   \\)", 'SubscriptBox["a", ""]')
        self.check("\\(  \\_   \\)", 'SubscriptBox["", ""]')

        self.check("\\(   \\^ b \\% c \\)", 'SubsuperscriptBox["", "c", "b"]')
        self.check("\\( a \\^   \\% c \\)", 'SubsuperscriptBox["a", "c", ""]')
        self.check("\\( a \\^ b \\%   \\)", 'SubsuperscriptBox["a", "", "b"]')
        self.check("\\(   \\^   \\% c \\)", 'SubsuperscriptBox["", "c", ""]')
        self.check("\\(   \\^ b \\%   \\)", 'SubsuperscriptBox["", "", "b"]')
        self.check("\\( a \\^   \\%   \\)", 'SubsuperscriptBox["a", "", ""]')
        self.check("\\(   \\^   \\%   \\)", 'SubsuperscriptBox["", "", ""]')

        self.check("\\(   \\_ b \\% c \\)", 'SubsuperscriptBox["", "b", "c"]')
        self.check("\\( a \\_   \\% c \\)", 'SubsuperscriptBox["a", "", "c"]')
        self.check("\\( a \\_ b \\%   \\)", 'SubsuperscriptBox["a", "b", ""]')
        self.check("\\(   \\_   \\% c \\)", 'SubsuperscriptBox["", "", "c"]')
        self.check("\\(   \\_ b \\%   \\)", 'SubsuperscriptBox["", "b", ""]')
        self.check("\\( a \\_   \\%   \\)", 'SubsuperscriptBox["a", "", ""]')
        self.check("\\(   \\_   \\%   \\)", 'SubsuperscriptBox["", "", ""]')

    def testOverscript(self):
        self.check("\\( a \\& b \\)", 'OverscriptBox["a", "b"]')
        self.check("\\( a \\& b \\% c \\)", 'UnderoverscriptBox["a", "c", "b"]')

        self.check("\\( a \\+ b \\)", 'UnderscriptBox["a", "b"]')
        self.check("\\( a \\+ b \\% c \\)", 'UnderoverscriptBox["a", "b", "c"]')

        self.check("\\(   \\& a \\)", 'OverscriptBox["", "a"]')
        self.check("\\( a \\&   \\)", 'OverscriptBox["a", ""]')
        self.check("\\(   \\&   \\)", 'OverscriptBox["", ""]')

        self.check("\\(   \\+ a \\)", 'UnderscriptBox["", "a"]')
        self.check("\\( a \\+   \\)", 'UnderscriptBox["a", ""]')
        self.check("\\(   \\+   \\)", 'UnderscriptBox["", ""]')

        self.check("\\(   \\& b \\% c \\)", 'UnderoverscriptBox["", "c", "b"]')
        self.check("\\( a \\&   \\% c \\)", 'UnderoverscriptBox["a", "c", ""]')
        self.check("\\( a \\& b \\%   \\)", 'UnderoverscriptBox["a", "", "b"]')
        self.check("\\(   \\&   \\% c \\)", 'UnderoverscriptBox["", "c", ""]')
        self.check("\\(   \\& b \\%   \\)", 'UnderoverscriptBox["", "", "b"]')
        self.check("\\( a \\&   \\%   \\)", 'UnderoverscriptBox["a", "", ""]')
        self.check("\\(   \\&   \\%   \\)", 'UnderoverscriptBox["", "", ""]')

        self.check("\\(   \\+ b \\% c \\)", 'UnderoverscriptBox["", "b", "c"]')
        self.check("\\( a \\+   \\% c \\)", 'UnderoverscriptBox["a", "", "c"]')
        self.check("\\( a \\+ b \\%   \\)", 'UnderoverscriptBox["a", "b", ""]')
        self.check("\\(   \\+   \\% c \\)", 'UnderoverscriptBox["", "", "c"]')
        self.check("\\(   \\+ b \\%   \\)", 'UnderoverscriptBox["", "b", ""]')
        self.check("\\( a \\+   \\%   \\)", 'UnderoverscriptBox["a", "", ""]')
        self.check("\\(   \\+   \\%   \\)", 'UnderoverscriptBox["", "", ""]')

    def testFraction(self):
        self.check("\\( a \\/ b \\)", 'FractionBox["a", "b"]')
        self.check("\\(   \\/ b \\)", 'FractionBox["", "b"]')
        self.check("\\( a \\/   \\)", 'FractionBox["a", ""]')
        self.check("\\(   \\/   \\)", 'FractionBox["", ""]')

    def testFormBox(self):
        self.check("\\( 1 \\` b \\)", 'FormBox["b", Removed["$$Failure"]]')
        self.check("\\( \\` b \\)", 'FormBox["b", StandardForm]')
        self.check("\\( a \\` b \\)", 'FormBox["b", a]')
        self.check("\\( a \\` \\)", 'FormBox["", a]')

    def testRow(self):
        self.check("\\( \\)", StringNode(""))
        self.check("\\( a \\)", StringNode("a"))
        self.check("\\( \\@ a \\_ b \\)", 'SqrtBox[SubscriptBox["a", "b"]]')
        self.check("\\( a + b \\)", 'RowBox[List["a", "+", "b"]]')
        self.check(
            "\\(a \\^ b \\+ c\\)", 'SuperscriptBox["a", UnderscriptBox["b", "c"]]'
        )
        self.check(
            "\\(a \\+ b \\^ c\\)", 'SuperscriptBox[UnderscriptBox["a", "b"], "c"]'
        )

    def testInvalid(self):
        self.invalid_error("\\( a \\% b \\)")
        self.invalid_error("\\( a \\+ \\% b \\% c \\)")

    def testNoRow(self):
        self.invalid_error("a \\% b")
        self.invalid_error("a \\+ b")
        self.invalid_error("\\@ a")


class PatternTests(ParserTests):
    def testPattern(self):
        self.check("a:b", "Pattern[a, b]")
        self.check("_:b", "Optional[Blank[], b]")
        self.check("a:_", "Pattern[a, Blank[]]")
        self.check("a:b:c", "Optional[Pattern[a, b], c]")
        self.check("a?b:c", "PatternTest[a, Pattern[b, c]]")
        self.check(
            "a:b:c:d:e:f",
            "Optional[Pattern[a, b], Optional[Pattern[c, d], Pattern[e, f]]]",
        )
        self.check("a:b|c", "Pattern[a, Alternatives[b, c]]")

        self.check(
            "Map[f_, expr_, ls_?LevelQ:{1}, OptionsPattern[Map]]",
            "Map[Pattern[f, Blank[]], Pattern[expr, Blank[]], PatternTest[Pattern[ls, Blank[]], Pattern[LevelQ, List[1]]], OptionsPattern[Map]]",
        )
        self.check("-Sin[x]", "Times[-1, Sin[x]]")
        self.check("a[x_] := x^2", "SetDelayed[a[Pattern[x, Blank[]]], Power[x, 2]]")
        self.check(
            "MakeBoxes[expr_, f:TraditionalForm|StandardForm|OutputForm|InputForm|FullForm]",
            "MakeBoxes[Pattern[expr, Blank[]], Pattern[f, Alternatives[TraditionalForm, StandardForm, OutputForm, InputForm, FullForm]]]",
        )

    def testPatternTest(self):
        self.check("1?2", Node("PatternTest", NumberNode("1"), NumberNode("2")))
        self.check("_a?b|_c", "Alternatives[PatternTest[Blank[a], b], Blank[c]]")
        self.invalid_error("a?b?c")
        self.check("a?b[c]", "PatternTest[a, b][c]")
        self.check("_^_?t", "Power[Blank[], PatternTest[Blank[], t]]")

    def testAutoPatternTest(self):
        autogen = [
            ("a?b", "PatternTest[a, b]"),
            ("a:b", "Pattern[a, b]"),
            ("a|b", "Alternatives[a, b]"),
            ("a?b?c", None),
            ("a?b:c", "PatternTest[a, Pattern[b, c]]"),
            ("a?b|c", "Alternatives[PatternTest[a, b], c]"),
            ("a:b?c", "Pattern[a, PatternTest[b, c]]"),
            ("a:b:c", "Optional[Pattern[a, b], c]"),
            ("a:b|c", "Pattern[a, Alternatives[b, c]]"),
            ("a|b?c", "Alternatives[a, PatternTest[b, c]]"),
            ("a|b:c", "Alternatives[a, Pattern[b, c]]"),
            ("a|b|c", "Alternatives[a, b, c]"),
        ]
        for code, result in autogen:
            if result is None:
                self.invalid_error(code)
            else:
                self.check(code, result)

    def testBlank(self):
        self.check("f_", Node("Pattern", SymbolNode("f"), Node("Blank")))
        self.check("f__", Node("Pattern", SymbolNode("f"), Node("BlankSequence")))
        self.check("f___", Node("Pattern", SymbolNode("f"), Node("BlankNullSequence")))

        self.check("_", "Blank[]")
        self.check("_expr", "Blank[expr]")
        self.check("__", "BlankSequence[]")
        self.check("__expr", "BlankSequence[expr]")
        self.check("___", "BlankNullSequence[]")
        self.check("___expr", "BlankNullSequence[expr]")

        self.check("_.", "Optional[Blank[]]")
        self.check("symb_", "Pattern[symb, Blank[]]")
        self.check("symb_expr", "Pattern[symb, Blank[expr]]")
        self.check("symb__", "Pattern[symb, BlankSequence[]]")
        self.check("symb__expr", "Pattern[symb, BlankSequence[expr]]")
        self.check("symb___", "Pattern[symb, BlankNullSequence[]]")
        self.check("symb___expr", "Pattern[symb, BlankNullSequence[expr]]")
        self.check("symb_.", "Optional[Pattern[symb, Blank[]]]")

    def testOptional(self):
        self.check("x:expr", Node("Pattern", SymbolNode("x"), SymbolNode("expr")))
        self.check(
            "x_:expr",
            Node(
                "Optional",
                Node("Pattern", SymbolNode("x"), Node("Blank")),
                SymbolNode("expr"),
            ),
        )
        self.check(
            "f:a|b",
            Node(
                "Pattern",
                SymbolNode("f"),
                Node("Alternatives", SymbolNode("a"), SymbolNode("b")),
            ),
        )
        self.check(
            "rev:(True|False):False",
            "Optional[Pattern[rev, Alternatives[True, False]], False]",
        )


class IncompleteTests(ParserTests):
    def testParseError(self):
        self.incomplete_error("1+")

    def testBracketInvalid(self):
        self.invalid_error("x)")  # bktmop
        self.invalid_error("x]")  # bktmop
        self.invalid_error("x}")  # bktmop
        self.invalid_error("x]]")  # bktmop

    def testBracketIncomplete(self):
        self.incomplete_error("(x")  # bktmcp
        self.incomplete_error("f[x")  # bktmcp
        self.incomplete_error("{x")  # bktmcp
        self.incomplete_error("f[[x")  # bktmcp

    def testBracketIncompleteInvalid(self):
        self.invalid_error("(x,")
        self.incomplete_error("(x")
        self.invalid_error("[x")
        self.incomplete_error("{x")
        self.invalid_error("[[x")


class CommentTests(ParserTests):
    def testComment(self):
        self.check(
            "145 (* abf *) 345", Node("Times", NumberNode("145"), NumberNode("345"))
        )
        self.check(r'(*"\"\*)', None)
        self.check(r"(**)", None)
        self.check(r"(*)*)", None)
        self.incomplete_error(r"(*(*(*")
        self.incomplete_error(r"(*(*)")
        self.incomplete_error(r"(*(**)")
        self.invalid_error(r"*)")
        self.invalid_error(r"(**)*)")
        self.invalid_error(r"(*(*(**)*)*)*)")
        self.check(r"(*(*)*) (*)*)*)", None)

    def testNone(self):
        self.assertIs(self.parse(""), None)
        self.assertIs(self.parse("(*fdasf *)"), None)


if __name__ == "__main__":
    unittest.main()
