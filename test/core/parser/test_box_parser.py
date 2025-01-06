# -*- coding: utf-8 -*-
"""
Unit tests for Box-expression parsing of mathics.core.parser.parser
"""

import time
from typing import Optional

from mathics_scanner import SingleLineFeeder

from mathics.core.parser.parser import Parser

# Set up a Parser that we can use to parse expressions.
# Note we don't use or pull in sessions here since we
# want are testing just the parse layer, not the evaluation layer.
parser = Parser()


def check_evaluation(str_expr: str, str_expected: str, assert_message: Optional[str]):
    def parse(s: str):
        return parser.parse(SingleLineFeeder(s))

    result = parse(str_expr)
    expected = parse(str_expected)

    print(time.asctime())
    if assert_message:
        print((result, expected))
        assert result == expected, assert_message
    else:
        print((result, expected))
        assert result == expected


def test_box_parsing():
    for str_expr, str_expected, assert_message in (
        (
            r"\( 1 \)",
            '"1"',
            "Box parsing a non-box expression should strip boxing and convert to String",
        ),
        (
            r"\( 2 x \)",
            'RowBox[{"2", "x"}]',
            "Box parsing of implicit multiplication is concatenation",
        ),
        (
            r"\( 2 \^ n \)",
            'SuperscriptBox["2", "n"]',
            "Box parsing a Superscript box operator should find box function name",
        ),
        (
            r"\( x \_ i \)",
            'SubscriptBox["x", "i"]',
            "Box parsing a Subscript operator should find box function name",
        ),
        (
            r"\( x \_ i \^ n \)",
            'SuperscriptBox[SubscriptBox["x", "i"], "n"]',
            "Box parsing multiple box operators should work",
        ),
        (
            r"\( x \_ \( i \^ n \) \)",
            'SubscriptBox["x", SuperscriptBox["i", "n"]]',
            "Box parsing multiple box operators with box parenthesis should work",
        ),
        (
            r"\( x \^ \( i \/ 2 + 5 \) \)",
            'SuperscriptBox["x", RowBox[{FractionBox["i", "2"], "+", "5"}]]',
            "Box parsing using FractionBox and parenthesis should work",
        ),
        # (
        #     r"\(1 F[\(Q\)]\)",
        #     'RowBox[{"1", RowBox[{"F", "[", "Q", "]"}]}]',
        #     "Box parsing with a function expression",
        # ),
    ):
        check_evaluation(str_expr, str_expected, assert_message)
