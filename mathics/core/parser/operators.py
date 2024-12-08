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

flat_binary_ops = OPERATOR_DATA["flat-binary-operators"]
left_binary_ops = OPERATOR_DATA["left-binary-operators"]
misc_ops = OPERATOR_DATA["miscellaneous-operators"]
nonassoc_binary_ops = OPERATOR_DATA["non-associative-binary-operators"]
postfix_ops = OPERATOR_DATA["postfix-operators"]
prefix_ops = OPERATOR_DATA["prefix-operators"]
right_binary_ops = OPERATOR_DATA["right-binary-operators"]
ternary_ops = OPERATOR_DATA["ternary-operators"]

inequality_ops = ["Less", "LessEqual", "Greater", "GreaterEqual", "Equal", "Unequal"]

# binary_ops = left_binary_ops V right_binary_ops V flat_binary_ops V nonassoc_binary_ops
binary_ops = {}

# all ops - check they're disjoint
all_ops = defaultdict(lambda: 670)

# Set below
all_operator_names = []


def calculate_operator_information():
    global binary_ops
    global all_ops
    global all_operator_names

    all_operator_names = []

    for ops in (
        left_binary_ops,
        right_binary_ops,
        flat_binary_ops,
        nonassoc_binary_ops,
    ):
        for op, prec in ops.items():
            binary_ops[op] = prec

    all_op_collections = (
        prefix_ops,
        postfix_ops,
        left_binary_ops,
        right_binary_ops,
        flat_binary_ops,
        ternary_ops,
        nonassoc_binary_ops,
        misc_ops,
    )

    for ops in all_op_collections:
        for op, prec in ops.items():
            all_ops[op] = prec

    all_operator_names = list(all_ops.keys())


# Calculating operator information is also done
# after loading in Builtin operators with no-meaning.
# However we also need to do this before reading that module in.
# This is a mess!

calculate_operator_information()
