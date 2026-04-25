# -*- coding: utf-8 -*-

import pickle
from typing import FrozenSet, Optional, Tuple

import mathics_scanner.location
from mathics_scanner.feed import LineFeeder
from mathics_scanner.location import ContainerKind

from mathics.core.definitions import Definitions
from mathics.core.element import BaseElement
from mathics.core.parser.ast import Node as ASTNode
from mathics.core.parser.convert import convert
from mathics.core.parser.feed import MathicsSingleLineFeeder
from mathics.core.parser.parser import Parser
from mathics.core.symbols import Symbol, SymbolTrue, ensure_context
from mathics.core.systemsymbols import SymbolFailed

parser = Parser()


def dump_exprs_to_pcl_file(exprs, pickle_file: str) -> Symbol:
    """
    Parse input from `feeder` and pickle serialize the parsed M-expression Python written
    to pickle_file.
    Serializes a Mathics3 AST Node to a file `pickle_file` using Python pickle.

    Return SymbolTrue if things went okay.
    """
    # Open the file in binary write mode
    with open(pickle_file, "wb") as f:
        # Protocol -1 uses the highest available binary protocol for efficiency
        pickle.dump(exprs, f, protocol=pickle.HIGHEST_PROTOCOL)
    return SymbolTrue


def parse(definitions, feeder: LineFeeder) -> Optional[BaseElement]:
    """
    Parse input (from the frontend, -e, input files, ToExpression etc).
    Look up symbols according to the Definitions instance supplied.

    Feeder must implement the feed and empty methods, see core/parser/feed.py.
    """
    return parse_returning_code(definitions, feeder)[0]


def parse_incrementally_by_line(
    definitions: Definitions, feeder: LineFeeder
) -> Optional[BaseElement]:
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
    an exception raised in parse which filters through this routine.

    """

    ast = parser.parse(feeder)
    if ast is None or isinstance(ast, Symbol):
        return ast
    return convert(ast, definitions)


def parse_returning_code(
    definitions: Definitions, feeder: LineFeeder
) -> Tuple[Optional[BaseElement], str]:
    """Parse input (from the frontend, -e, input files, ToExpression etc).
    Look up symbols according to the Definitions instance supplied.

    ``feeder`` must implement the ``feed()`` and ``empty()``
    methods. See the mathics_scanner.feed module.

    """
    ast = parser.parse(feeder)

    source_text = parser.tokeniser.source_text
    if (
        mathics_scanner.location.TRACK_LOCATIONS
        and feeder.container_kind == ContainerKind.STREAM
    ):
        feeder.container.append(source_text)

    if ast is None:
        return None, source_text

    converted = convert(ast, definitions)

    if hasattr(converted, "location") and ast.location:
        converted.location = ast.location
    return converted, source_text


def parse_dump_to_pcl_file(feeder: LineFeeder, pickle_file: str) -> Symbol:
    """
    Parse input from `feeder` and pickle serialize the parsed M-expression Python written
    to pickle_file.
    Serializes a Mathics3 AST Node to a file `pickle_file` using Python pickle.
    """
    ast = parser.parse(feeder)

    if ast is None:
        return SymbolFailed
    # Ensure the input is actually a Node (optional safety check)
    if not isinstance(ast, ASTNode):
        raise TypeError(f"Expected mathics.core.parser.ast.Node, got {type(ast)}")

    # Open the file in binary write mode
    with open(pickle_file, "wb") as f:
        # Protocol -1 uses the highest available binary protocol for efficiency
        pickle.dump(ast, f, protocol=pickle.HIGHEST_PROTOCOL)
    return SymbolTrue


def parse_from_pcl_file(definitions, pickle_file: str):

    with open(pickle_file, "rb") as f:
        # Load the object from the binary file.
        result = pickle.load(f)

    return result


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


def parse_builtin_rule(string, definitions=SystemDefinitions(), location=None):
    """
    Parse rules specified in builtin docstrings/attributes. Every symbol
    in the input is created in the System` context.
    """
    return parse(
        definitions,
        MathicsSingleLineFeeder(string, location, ContainerKind.PYTHON),
    )
