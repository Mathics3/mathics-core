"""
Conversions from the ASCII representation of Mathics operators to their Unicode equivalent
"""

import os.path as osp
from functools import lru_cache

import pkg_resources

try:
    import ujson
except ImportError:
    import json as ujson

ROOT_DIR = pkg_resources.resource_filename("mathics", "")

# Load the conversion tables from disk
characters_path = osp.join(ROOT_DIR, "data", "op-tables.json")
assert osp.exists(
    characters_path
), f"ASCII operator to Unicode tables are missing from {characters_path}"
with open(characters_path, "r") as f:
    op_data = ujson.load(f)

ascii_operator_to_symbol = op_data["ascii-operator-to-symbol"]
operator_to_unicode = op_data["operator-to-unicode"]
operator_to_ascii = op_data["operator-to-ascii"]


@lru_cache(maxsize=1024)
def ascii_op_to_unicode(ascii_op: str, encoding: str) -> str:
    """
    Convert an ASCII representation of a Mathics operator into its
    Unicode equivalent based on encoding (in Mathics, $CharacterEncoding).
    If we can't come up with a unicode equivalent, just return "ascii_op".
    """
    if encoding in ("UTF-8", "utf-8", "Unicode"):
        return op_data["ascii-operator-to-unicode"].get(ascii_op, ascii_op)
    if encoding in ("WMA",):
        return op_data["ascii-operator-to-wl-unicode"].get(ascii_op, ascii_op)
    return ascii_op
