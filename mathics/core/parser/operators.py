# -*- coding: utf-8 -*-
"""Mathics3 Operator tables.

This information is controlled by data from the MathicsScanner Project,
from YAML tables which are converted to JSON.

The dictionary from these which are read in here, are used by the
Mathics3 parser.
"""


import os.path as osp
from collections import defaultdict

from mathics.settings import ROOT_DIR

try:
    import ujson
except ImportError:
    import json as ujson  # type: ignore[no-redef]

# Load Mathics3 operator information from JSON. This file is derived from a
# Mathics3 Operator Data YAML file in MathicsScanner.
operator_tables_path = osp.join(ROOT_DIR, "data", "operator-tables.json")
assert osp.exists(
    operator_tables_path
), f"Internal error: Mathics3 Operator information are missing; expected to be in {operator_tables_path}"
with open(operator_tables_path, "r") as f:
    OPERATOR_DATA = ujson.load(f)

box_operators = OPERATOR_DATA["box-operators"]
flat_binary_operators = OPERATOR_DATA["flat-binary-operators"]
left_binary_operators = OPERATOR_DATA["left-binary-operators"]
misc_operators = OPERATOR_DATA["miscellaneous-operators"]
nonassoc_binary_operators = OPERATOR_DATA["non-associative-binary-operators"]
operator_precedences = OPERATOR_DATA["operator-precedence"]
postfix_operators = OPERATOR_DATA["postfix-operators"]
prefix_operators = OPERATOR_DATA["prefix-operators"]
right_binary_operators = OPERATOR_DATA["right-binary-operators"]
ternary_operators = OPERATOR_DATA["ternary-operators"]

# FIXME: get from JSON
inequality_operators = [
    "Less",
    "LessEqual",
    "Greater",
    "GreaterEqual",
    "Equal",
    "Unequal",
]

# binary_operators = left_binary_operators V right_binary_operators V flat_binary_operators V nonassoc_binary_operators
binary_operators = {}

# all ops - check they're disjoint
all_operators = defaultdict(lambda: 670)

# Set below
all_operator_names = []


def calculate_operator_information():
    global binary_operators
    global all_operators
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
            all_operators[op] = prec

    all_operator_names = list(all_operators.keys())


# Calculating operator information is also done
# after loading in Builtin operators with no-meaning.
# However we also need to do this before reading that module in.
# This is a mess!

calculate_operator_information()
