"""
Conversions from the ASCII representation of Mathics operators to their Unicode equivalent
"""

import logging
import os.path as osp
from functools import lru_cache

from mathics.settings import ROOT_DIR

try:
    import ujson
except ImportError:
    import json as ujson  # type: ignore[no-redef]


# Load the conversion tables from disk
characters_path = osp.join(ROOT_DIR, "data", "op-tables.json")
assert osp.exists(
    characters_path
), f"ASCII operator to Unicode tables are missing from {characters_path}"
with open(characters_path, "r") as f:
    OPERATOR_CONVERSION_TABLES = ujson.load(f)

ascii_operator_to_symbol = OPERATOR_CONVERSION_TABLES["ascii-operator-to-symbol"]
builtin_constants = OPERATOR_CONVERSION_TABLES["builtin-constants"]
operator_to_unicode = OPERATOR_CONVERSION_TABLES["operator-to-unicode"]
operator_to_ascii = OPERATOR_CONVERSION_TABLES["operator-to-ascii"]
unicode_operator_to_ascii = {
    val: operator_to_ascii[key] for key, val in operator_to_unicode.items()
}

UNICODE_TO_AMSLATEX = OPERATOR_CONVERSION_TABLES["unicode-to-amslatex"]
UNICODE_TO_LATEX = OPERATOR_CONVERSION_TABLES["unicode-to-latex"]


AMSTEX_OPERATORS = {
    "\u2032": "'",
    "\u2032\u2032": "''",
    "\u2062": " ",
    "\u221e": r"\infty ",
    "\u00d7": r"\times ",
    "(": r"\left(",
    "[": r"\left[",
    "{": r"\left\{",
    ")": r"\right)",
    "]": r"\right]",
    "}": r"\right\}",
    "\u301a": r"\left[\left[",
    "\u301b": r"\right]\right]",
    ",": ",",
    ", ": ", ",
    "\u222b": r"\int",
    "\u2146": r"\, d",
    "\uF74C": r"\, d",
    "\U0001D451": r"\, d",
    "\u2211": r"\sum",
    "\u220f": r"\prod",
}


def is_named_operator(str_op):
    if len(str_op) < 3:
        return False
    if str_op[:2] != "\\[" or str_op[-1] != "]":
        return False
    return str_op[2:-1].isalnum()


@lru_cache(maxsize=1024)
def ascii_op_to_unicode(ascii_op: str, encoding: str) -> str:
    """
    Convert an ASCII representation of a Mathics operator into its
    Unicode equivalent based on encoding (in Mathics, $CharacterEncoding).
    If we can't come up with a unicode equivalent, just return "ascii_op".
    """
    if encoding in ("UTF-8", "utf-8", "Unicode"):
        return OPERATOR_CONVERSION_TABLES["ascii-operator-to-unicode"].get(
            ascii_op, ascii_op
        )
    if encoding in ("WMA",):
        return OPERATOR_CONVERSION_TABLES["ascii-operator-to-wl-unicode"].get(
            ascii_op, ascii_op
        )
    return ascii_op


def get_latex_operator(unicode_op: str) -> str:
    """
    Get a LaTeX representation of the unicode operator.
    """

    def hex_form_code(char_str):
        return hex(ord(char_str))[2:]

    for candidate_dict in (
        UNICODE_TO_AMSLATEX,
        # amstex_operators,
        unicode_operator_to_ascii,
    ):
        return_str = candidate_dict.get(unicode_op)
        if return_str and return_str.isascii():
            # if result match with \[[]:alpha:*[]]
            if is_named_operator(return_str):
                return "\\backslash\\text{" + return_str[1:] + "}"
            return return_str
    # `unicode_op` is not in any of the candidates.
    # if it is already an ascii, return without changes.
    if unicode_op.isascii():
        return unicode_op
    try:
        return r"\text{" + UNICODE_TO_LATEX[unicode_op] + "}"
    except KeyError:
        # the `unicode_op` cannot be converted into an ascii string. Show a
        # warning and return a `\symbol{code}` expression.
        logging.warning(
            "Unicode op" + unicode_op + "(" + hex_form_code(unicode_op) + ") not found."
        )
        return '\\symbol{"' + hex_form_code(unicode_op) + "}"
