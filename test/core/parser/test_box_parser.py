# -*- coding: utf-8 -*-
"""
Unit tests for Box-expression parsing of mathics.core.parser.parser
"""

import time
from typing import Optional

from mathics_scanner import SingleLineFeeder
from mathics_scanner.errors import InvalidSyntaxError
from mathics_scanner.location import ContainerKind

from mathics.core.parser.ast import Node
from mathics.core.parser.parser import Parser

# Set up a Parser that we can use to parse expressions.
# Note we don't import mathics.session here since we
# are testing just the parse layer, not the evaluation layer.
# Simpler is better.
core_parser = Parser()


def check_evaluation(
    str_expr: str,
    str_expected: Optional[str],
    parse_failure_args: tuple,
    assert_fail_message: Optional[str],
):
    def parse(source_text: str):
        return core_parser.parse(
            SingleLineFeeder(source_text, "<test_box_parser>", ContainerKind.STRING)
        )

    error_args = None
    result = None
    try:
        result = parse(str_expr)
    except InvalidSyntaxError as e:
        # Handle asserts outside of exception so that
        # failures in checking don't report:
        #  During handling of the above exception, another exception occurred
        error_args = e.args

    if error_args is not None:
        assert (
            parse_failure_args is not None
        ), "Syntax error, but test creator has none registered."
        assert error_args == parse_failure_args, assert_fail_message
        return

    assert isinstance(result, Node), "Should get result when no Syntax error"
    assert (
        str_expected is not None
    ), "Test creator's error; when the expected result is None, there should be expected output"
    expected = parse(str_expected)

    print(time.asctime())
    if assert_fail_message:
        print((result, expected))
        assert result == expected, assert_fail_message
    else:
        print((result, expected))
        assert result == expected


def test_box_parsing():
    for str_expr, str_expected, parse_fail_args, assert_fail_message in (
        (
            r"\( 1 \)",
            '"1"',
            tuple(),
            "Box parsing a non-box expression should strip boxing and convert to String",
        ),
        (
            r"\( 2 x \)",
            'RowBox[{"2", "x"}]',
            tuple(),
            "Box parsing of implicit multiplication is concatenation",
        ),
        (
            r"\( 2 \^ n \)",
            'SuperscriptBox["2", "n"]',
            tuple(),
            "Box parsing a Superscript box operator should find box function name",
        ),
        (
            r"\( x \_ i \)",
            'SubscriptBox["x", "i"]',
            tuple(),
            "Box parsing a Subscript operator should find box function name",
        ),
        (
            r"\( x \_ i \^ n \)",
            'SuperscriptBox[SubscriptBox["x", "i"], "n"]',
            tuple(),
            "Box parsing multiple box operators should work",
        ),
        (
            r"\( x \_ \( i \^ n \) \)",
            'SubscriptBox["x", SuperscriptBox["i", "n"]]',
            tuple(),
            "Box parsing multiple box operators with box parenthesis should work",
        ),
        (
            r"\( x \^ \( i \/ 2 + 5 \) \)",
            'SuperscriptBox["x", RowBox[{FractionBox["i", "2"], "+", "5"}]]',
            tuple(),
            "Box parsing using FractionBox and parenthesis should work",
        ),
        (
            r"\(1 F[\(Q\)]\)",
            'RowBox[{"1", "F", "[", "Q", "]"}]',
            tuple(),
            "Box parsing with a function expression",
        ),
        (
            r"\(1 F[3 x]\)",
            'RowBox[{"1", "F", "[", "3", "x", "]"}]',
            tuple(),
            "Box parsing with a function expression with arithmetic expression parameter",
        ),
        (
            r"\(1 F[3 \/ x]\)",
            'RowBox[{"1", "F", "[", FractionBox["3", "x"], "]"}]',
            tuple(),
            "Box parsing with a function expression with box expression parameter",
        ),
    ):
        check_evaluation(str_expr, str_expected, parse_fail_args, assert_fail_message)


def test_box_escape_input_parsing():
    for str_expr, str_expected, parse_fail_args, assert_fail_message in (
        (
            r"\(\*RowBox[x]\)",
            "RowBox[x]",
            tuple(),
            r"Escaped Box input function with a single argument",
        ),
        (
            r"\(\*SuperscriptBox[x, y]\)",
            "SuperscriptBox[x, y]",
            tuple(),
            r"Escaped Box input function with two arguments",
        ),
        (
            r"\(\*RowBox  [x]\)",
            "RowBox[x]",
            tuple(),
            "Spaces are ignored between function name and parameters are ignored in Escaped Box input",
        ),
        (
            r"\(\*2\)",
            None,
            (2, 7),
            r"A number can't be used for a \* input",
        ),
        # TODO later:
        # (r'\(\*F\)', None, 'Syntax::syntyp: \\ operators can only be used between \\( \\).\n\nSyntax::sntxf: "\\(\\*F" cannot be followed by "\\) //Hold//FullForm".'),
        # (r'\(\*+\)', None, r'Syntax::sntxf: "\(\*" cannot be followed by "+\) //Hold//FullForm".'),
        #
        # # The head of a expression following \* only can be a symbol:
        # (r'\(\*F[x][g]\)', 'RowBox[List[F[x], "[", "g", "]"]]', None),
        #
        # # Another expression is processed as a box expression, at the side of the result of `F[x]`
        # (r'\(\*F[x]g[y]\)', 'RowBox[List[F[x], RowBox[List["g", "[", "y", "]"]]]]', None),
        #
        # # An operation  is processed as a box expression, at the side of the result of `F[x]`
        # (r'\(\*F[x]+g[y]\)', 'RowBox[List[F[x], "+", RowBox[List["g", "[", "y", "]"]]]]', None),
        #
        # # Nested box expressions:
        # (r'\(\*F[x, \( y z\)]\)', 'F[x, RowBox[List["y", "z"]]]', None),
        #
        # # Nested box expressions, with \* again:
        # (r'\(\*F[x, \( y \*z[t]\)]\)', 'F[x, RowBox[List["y", z[t]]]]', None),
        #
        # # Operators inside the elements inside the expression are processed.
        # (r'\(\*F[x+t, \( y \*z[t]\)]\)',  'F[Plus[x, t], RowBox[List["y", z[t]]]]', None),
    ):
        check_evaluation(str_expr, str_expected, parse_fail_args, assert_fail_message)
