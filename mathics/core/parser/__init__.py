# -*- coding: utf-8 -*-
"""
This module contains routines that takes tokens from the scanner (in a
separate module and repository) and parses this into some sort of
M-Expression as its AST (Abstract Syntax Tree).

There is a separate `README
<https://github.com/Mathics3/mathics-core/blob/master/mathics/core/parser/README.md>`_
for decribing how this works.
"""


from mathics_scanner import is_symbol_name

from mathics.core.parser.feed import (
    MathicsFileLineFeeder,
    MathicsLineFeeder,
    MathicsMultiLineFeeder,
    MathicsSingleLineFeeder,
)
from mathics.core.parser.operators import all_operator_names
from mathics.core.parser.util import parse, parse_builtin_rule

__all__ = [
    "MathicsFileLineFeeder",
    "MathicsFileLineFeeder",
    "MathicsLineFeeder",
    "MathicsMultiLineFeeder",
    "MathicsSingleLineFeeder",
    "all_operator_names",
    "is_symbol_name",
    "parse",
    "parse_builtin_rule",
]
