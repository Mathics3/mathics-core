import unittest

from mathics_scanner import (
    IncompleteSyntaxError,
    InvalidSyntaxError,
    MultiLineFeeder,
    SingleLineFeeder,
    SyntaxError,
)
from mathics_scanner.location import ContainerKind

from mathics.core.definitions import Definitions
from mathics.core.load_builtin import import_and_load_builtins
from mathics.core.parser import parse as core_parse

import_and_load_builtins()
definitions = Definitions(add_builtin=True)


class UtilTests(unittest.TestCase):
    def parse(self, source_text: str):
        raise NotImplementedError

    def compare(self, expr1, expr2):
        raise NotImplementedError

    def check(self, expr1, expr2):
        if isinstance(expr1, str):
            expr1 = self.parse(expr1)
        if isinstance(expr2, str):
            expr2 = self.parse(expr2)

        if expr1 is None:
            self.assertIsNone(expr2)
        else:
            self.compare(expr1, expr2)

    def incomplete_error(self, string):
        self.assertRaises(IncompleteSyntaxError, self.parse, string)

    def invalid_error(self, string):
        self.assertRaises(InvalidSyntaxError, self.parse, string)

    def syntax_error(self, string):
        self.assertRaises(SyntaxError, self.parse, string)


class SingleLineParserTests(UtilTests):
    def parse(self, source_text):
        return core_parse(
            definitions,
            SingleLineFeeder(source_text, "<SingleLineParser>", ContainerKind.STRING),
        )

    def compare(self, expr1, expr2):
        assert expr1.sameQ(expr2)

    def test_continuation(self):
        self.incomplete_error("Sin[")
        self.check("Sin[\n0]", "Sin[0]")
        self.check("Sin[\n\n0]", "Sin[0]")

    def test_trailing_backslash(self):
        self.incomplete_error("x \\")
        self.syntax_error("X\\n\\t")

        ## TODO see what this should do and why
        ## self.check("x \\\ny", "Times[x, y]")


class MultiLineParserTests(UtilTests):
    def parse(self, source_text):
        return core_parse(
            definitions,
            MultiLineFeeder(
                source_text, "<MultiLineParserTests>", ContainerKind.STRING
            ),
        )

    def compare(self, expr1, expr2):
        assert expr1.sameQ(expr2)

    def test_trailing_backslash(self):
        self.incomplete_error("x \\")
        self.syntax_error("X\\n\\t")

        ## TODO see what this should do and why
        ## self.check("x \\\ny", "Times[x, y]")

    def test_continuation(self):
        self.incomplete_error("Sin[")
        self.check("Sin[\n0]", "Sin[0]")
        self.check("Sin[0\n]", "Sin[0]")
        self.check("Sin[\n\n0]", "Sin[0]")

    def test_CompoundExpression(self):
        self.check("f[a;\nb]", "f[CompoundExpression[a, b]]")
        self.check("f[a;\nb;\nc;]", "f[CompoundExpression[a, b, c, Null]]")
        self.check("f[a;\nb;\nc;\n]", "f[CompoundExpression[a, b, c, Null]]")

        self.check("a;^b", "Power[CompoundExpression[a, Null], b]")

        feeder = MultiLineFeeder(
            "a;\n^b", "<test_CompoundExpression>", ContainerKind.STRING
        )
        self.compare(
            core_parse(definitions, feeder), self.parse("CompoundExpression[a, Null]")
        )
        self.assertRaises(
            InvalidSyntaxError, lambda f: core_parse(definitions, f), feeder
        )

    def test_Span(self):
        self.check("a;;^b", "Power[Span[a, All], b]")
        feeder = MultiLineFeeder("a;;\n^b", "<test_Span>", ContainerKind.STRING)
        self.compare(core_parse(definitions, feeder), self.parse("Span[a, All]"))
        self.assertRaises(
            InvalidSyntaxError, lambda f: core_parse(definitions, f), feeder
        )
