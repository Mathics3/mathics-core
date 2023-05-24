# -*- coding: utf-8 -*-
"""
Conversion from AST node to Mathic BaseElement objects
"""

from math import log10
from typing import Tuple

import sympy

from mathics.core.atoms import Integer, MachineReal, PrecisionReal, Rational, String
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.number import RECONSTRUCT_MACHINE_PRECISION_DIGITS
from mathics.core.parser.ast import (
    Filename as AST_Filename,
    Number as AST_Number,
    String as AST_String,
    Symbol as AST_Symbol,
)
from mathics.core.symbols import Symbol, SymbolList


class GenericConverter:
    def do_convert(self, node):
        if isinstance(node, AST_Symbol):
            return self.convert_Symbol(node)
        elif isinstance(node, AST_String):
            return self.convert_String(node)
        elif isinstance(node, AST_Number):
            return self.convert_Number(node)
        elif isinstance(node, AST_Filename):
            return self.convert_Filename(node)
        else:
            head = self.do_convert(node.head)
            children = [self.do_convert(child) for child in node.children]
            return "Expression", head, children

    @staticmethod
    def string_escape(s):
        return s.encode("raw_unicode_escape").decode("unicode_escape")

    def convert_Symbol(self, node: AST_Symbol) -> Tuple[str, str]:
        if node.context is not None:
            return "Symbol", node.context + "`" + node.value
        else:
            return "Lookup", node.value

    def convert_String(self, node: AST_String) -> Tuple[str, str]:
        value = self.string_escape(node.value)
        return "String", value

    def convert_Filename(self, node: AST_Filename):
        s = node.value
        if s.startswith('"'):
            assert s.endswith('"')
            s = s[1:-1]
        s = self.string_escape(s)
        s = s.replace("\\", "\\\\")
        return "String", s

    def convert_Number(self, node: AST_Number) -> tuple:
        s = node.value
        sign = node.sign
        base = node.base
        suffix = node.suffix
        n = node.exp

        # Look for decimal point
        if "." not in s:
            if suffix is None:
                if n < 0:
                    return "Rational", sign * int(s, base), base ** abs(n)
                else:
                    return "Integer", sign * int(s, base) * (base**n)
            else:
                s = s + "."

        if base == 10:
            man = s
            if n != 0:
                s = s + "E" + str(n)

            if suffix is None:
                # MachineReal/PrecisionReal is determined by number of digits
                # in the mantissa
                # if the number of digits is less than 17, then MachineReal is used.
                # If more digits are provided, then PrecisionReal is used.
                digits = len(man) - 2
                if digits < RECONSTRUCT_MACHINE_PRECISION_DIGITS:
                    return "MachineReal", sign * float(s)
                else:
                    return (
                        "PrecisionReal",
                        ("DecimalString", str("-" + s if sign == -1 else s)),
                        digits,
                    )
            elif suffix == "":
                return "MachineReal", sign * float(s)
            elif suffix.startswith("`"):
                # A double Reversed Prime ("``") represents a fixed accuracy
                # (absolute uncertainty).
                acc = float(suffix[1:])
                x = float(s)
                # For 0, a finite absolute precision even if
                # the number is an integer, it is stored as a
                # PrecisionReal number.
                if x == 0:
                    prec10 = acc
                else:
                    prec10 = acc + log10(abs(x))
                return (
                    "PrecisionReal",
                    ("DecimalString", str("-" + s if sign == -1 else s)),
                    prec10,
                )
            else:
                # A single Reversed Prime ("`") represents a fixed precision
                # (relative uncertainty).
                # For 0, a finite relative precision reduces to no uncertainty,
                # so ``` 0`3 === 0 ``` and  ``` 0.`3 === 0.`4 ```
                if node.value == "0":
                    return "Integer", 0

                s_float = float(s)
                prec = float(suffix)
                if s_float == 0.0:
                    return "MachineReal", sign * s_float
                return (
                    "PrecisionReal",
                    ("DecimalString", str("-" + s if sign == -1 else s)),
                    prec,
                )

        # Put into standard form mantissa * base ^ n
        s = s.split(".")
        if len(s) == 1:
            man = s[0]
        else:
            n -= len(s[1])
            man = s[0] + s[1]
        man = sign * int(man, base)
        if n >= 0:
            p = man * base**n
            q = 1
        else:
            p = man
            q = base**-n
        result = "Rational", p, q
        x = float(sympy.Rational(p, q))

        # determine `prec10` the digits of precision in base 10
        if suffix is None:
            acc = len(s[1])
            acc10 = acc * log10(base)
            if x == 0:
                prec10 = acc10
            else:
                prec10 = acc10 + log10(abs(x))
            if prec10 < RECONSTRUCT_MACHINE_PRECISION_DIGITS:
                prec10 = None
        elif suffix == "":
            prec10 = None
        elif suffix.startswith("`"):
            acc = float(suffix[1:])
            acc10 = acc * log10(base)
            if x == 0:
                prec10 = acc10
            else:
                prec10 = acc10 + log10(abs(x))
        else:
            prec = float(suffix)
            prec10 = prec * log10(base)

        if prec10 is None:
            return "MachineReal", x
        else:
            return "PrecisionReal", result, prec10


class Converter(GenericConverter):
    def __init__(self):
        self.definitions = None

    def convert(self, node, definitions):
        self.definitions = definitions
        result = self.do_convert(node)
        self.definitions = None
        return result

    def do_convert(self, node):
        result = GenericConverter.do_convert(self, node)
        return getattr(self, "_make_" + result[0])(*result[1:])

    def _make_Symbol(self, s: str) -> Symbol:
        return Symbol(s)

    def _make_Lookup(self, s: str) -> Symbol:
        value = self.definitions.lookup_name(s)
        return Symbol(value)

    def _make_String(self, s: str) -> String:
        return String(s)

    def _make_Integer(self, x) -> Integer:
        return Integer(x)

    def _make_Rational(self, x, y) -> Rational:
        return Rational(x, y)

    def _make_MachineReal(self, x):
        return MachineReal(x)

    def _make_PrecisionReal(self, value, prec):
        if value[0] == "Rational":
            assert len(value) == 3
            x = sympy.Rational(*value[1:])
        elif value[0] == "DecimalString":
            assert len(value) == 2
            x = value[1]
        else:
            assert False
        return PrecisionReal(sympy.Float(x, prec))

    def _make_Expression(self, head: Symbol, children: list):
        if head == SymbolList:
            return to_mathics_list(*children)

        return to_expression(head, *children)


converter = Converter()
convert = converter.convert
