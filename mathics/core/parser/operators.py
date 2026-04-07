# -*- coding: utf-8 -*-
"""Mathics3 Operator tables.

This information is controlled by data from the MathicsScanner Project,
from YAML tables which are converted to JSON.

The dictionary from these which are read in here, are used by the
Mathics3 parser.
"""

from collections import defaultdict
from typing import Dict, Final

from mathics_scanner.characters import OPERATOR_DATA

box_operators: Final[Dict[str, str]] = OPERATOR_DATA["box-operators"]
flat_binary_operators: Final[Dict[str, int]] = OPERATOR_DATA["flat-binary-operators"]
left_binary_operators = OPERATOR_DATA["left-binary-operators"]
misc_operators: Final[Dict[str, int]] = OPERATOR_DATA["miscellaneous-operators"]
nonassoc_binary_operators: Final[Dict[str, int]] = OPERATOR_DATA[
    "non-associative-binary-operators"
]
operator_precedences: Final[Dict[str, int]] = OPERATOR_DATA["operator-precedences"]
operator_to_amslatex: Final[Dict[str, str]] = OPERATOR_DATA["operator-to-amslatex"]
operator_to_string: Final[dict] = OPERATOR_DATA.get(
    "operator-to-string", OPERATOR_DATA.get("operator-to_string", {})
)
postfix_operators = OPERATOR_DATA["postfix-operators"]
prefix_operators = OPERATOR_DATA["prefix-operators"]
right_binary_operators = OPERATOR_DATA["right-binary-operators"]
ternary_operators = OPERATOR_DATA["ternary-operators"]

# FIXME: get from JSON
inequality_operators: Final[tuple] = (
    "Less",
    "LessEqual",
    "Greater",
    "GreaterEqual",
    "Equal",
    "Unequal",
)

# binary_operators = left_binary_operators V right_binary_operators V flat_binary_operators V nonassoc_binary_operators
binary_operators: Dict[str, int] = {}

# all ops - check they're disjoint
OPERATOR_PRECEDENCE = defaultdict(lambda: operator_precedences["FunctionApply"])
BOX_OPERATOR_PRECEDENCE: Final[int] = operator_precedences["BoxGroup"]
PLUS_PRECEDENCE: Final[int] = operator_precedences["Plus"]

# Values are set below in calculate_operator_information
all_operator_names: tuple = tuple()


def calculate_operator_information():
    global all_operator_names

    all_operator_names = []

    for ops in (
        left_binary_operators,
        right_binary_operators,
        flat_binary_operators,
        nonassoc_binary_operators,
    ):
        for op, prec in ops.items():
            binary_operators[op] = prec

    all_op_collections = (
        prefix_operators,
        postfix_operators,
        left_binary_operators,
        right_binary_operators,
        flat_binary_operators,
        ternary_operators,
        nonassoc_binary_operators,
        misc_operators,
    )

    for ops in all_op_collections:
        for op, prec in ops.items():
            OPERATOR_PRECEDENCE[op] = prec

    all_operator_names = tuple(OPERATOR_PRECEDENCE.keys())
    pass


# Calculating operator information is also done
# after loading in Builtin operators with no-meaning.
# However we also need to do this before reading that module in.
# This is a mess!

calculate_operator_information()
