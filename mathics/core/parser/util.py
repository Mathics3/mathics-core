# -*- coding: utf-8 -*-

from typing import Any, FrozenSet, Tuple

from mathics_scanner.errors import (
    IncompleteSyntaxError,
    InvalidSyntaxError,
    TranslateError,
    TranslateErrorNew,
)
from mathics_scanner.feed import LineFeeder

from mathics.core.parser.convert import convert
from mathics.core.parser.feed import MathicsSingleLineFeeder
from mathics.core.parser.parser import Parser
from mathics.core.symbols import Symbol, SymbolNull, ensure_context
from mathics.core.systemsymbols import SymbolFailed

parser = Parser()


def parse(definitions, feeder: LineFeeder) -> Any:
    """
    Parse input (from the frontend, -e, input files, ToExpression etc).
    Look up symbols according to the Definitions instance supplied.

    Feeder must implement the feed and empty methods, see core/parser/feed.py.
    """
    return parse_returning_code(definitions, feeder)[0]


def parse_incrementally_by_line(definitions, feeder: LineFeeder) -> Any:
    """Parse input incrementally by line. This is in contrast to parse() or
    parser_returning_code(), which parse the *entire*
    input which could be many line.

    This routine is called via Read[] which parses by line, possibly
    leaving of the input unparsed, depending on whether Read[]
    requires more expressions.

    By working incrementally, we may avoid reading lots of input that
    is not going to be needed.

    As a result, we do *not* handle exceptions raised. Instead, we leave that for the
    eval_Read() routine to handle, so it can ask for another line.

    Feeder must implement the feed and empty methods.

    The result is the AST parsed or syhmbols like $Failed or NullType. Or there can be
    an excpetion raised in parse which filters through this routine.

    """

    ast = parser.parse(feeder)
    if ast is None or isinstance(ast, Symbol):
        return ast
    return convert(ast, definitions)


def parse_returning_code(definitions, feeder: LineFeeder) -> Tuple[Any, str]:
    """
    Parse input (from the frontend, -e, input files, ToExpression etc).
    Look up symbols according to the Definitions instance supplied.

    Feeder must implement the feed and empty methods, see core/parser/feed.py.

    The result is the AST parsed, and the source-code text.

    If there was an error in parsing, AST is set to None.
    """

    try:
        ast = parser.parse(feeder)
    except (TranslateError, TranslateErrorNew) as e:
        # Here, we are just trying to match WMA's return value behavior.
        # Until we have a general model of how this works, we resort to a hacky
        # case-by-case approach.
        if isinstance(e, (InvalidSyntaxError, IncompleteSyntaxError)):
            ast = SymbolNull
        else:
            ast = SymbolFailed

    source_code = (
        parser.tokeniser.source_text if hasattr(parser.tokeniser, "source_text") else ""
    )
    if ast is None or isinstance(ast, Symbol):
        return ast, source_code
    return convert(ast, definitions), source_code


class SystemDefinitions:
    """
    Dummy Definitions object that puts every unqualified symbol in
    System`.
    """

    def lookup_name(self, name):
        assert isinstance(name, str)
        return ensure_context(name)


# FIXME: there has to be a better way, to get this
# from the current System list.
#  For now we'll hack these in and figure this out
# later
SYSTEM_LIST: FrozenSet[str] = frozenset(
    [
        "Alternatives",
        "Complex",
        "Integer",
        "List",
        "MachineReal",
        "Number",
        "OptionsPattern",
        "PrecisionReal",
        "Real",
        "String",
        "StringExpression",
        "Symbol",
    ]
)


class PyMathicsDefinitions:
    """
    Dummy Definitions object that puts every unqualified symbol in
    Pymathics`.
    """

    def lookup_name(self, name):
        assert isinstance(name, str)
        context = "System`" if name in SYSTEM_LIST else "Pymathics`"
        # print("XXX", name, context)
        return ensure_context(name, context)


def parse_builtin_rule(string, definitions=SystemDefinitions()):
    """
    Parse rules specified in builtin docstrings/attributes. Every symbol
    in the input is created in the System` context.
    """
    return parse(definitions, MathicsSingleLineFeeder(string, "<builtin_rules>"))
