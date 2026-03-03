"""
Conversions from the ASCII representation of Mathics3 operators to their Unicode equivalent
"""

import logging
from functools import lru_cache

from mathics_scanner.characters import (
    NAME_TO_WL_UNICODE,
    NAMED_CHARACTERS,
    NAMED_CHARACTERS_COLLECTION,
)

ascii_operator_to_symbol = NAMED_CHARACTERS_COLLECTION["ascii-operator-to-symbol"]
builtin_constants = NAMED_CHARACTERS_COLLECTION["builtin-constants"]
operator_to_unicode = NAMED_CHARACTERS_COLLECTION["operator-to-unicode"]
operator_to_ascii = NAMED_CHARACTERS_COLLECTION["operator-to-ascii"]
unicode_operator_to_ascii = {
    val: operator_to_ascii[key] for key, val in operator_to_unicode.items()
}

UNICODE_TO_AMSLATEX = NAMED_CHARACTERS_COLLECTION.get("unicode-to-amslatex", {})
UNICODE_TO_LATEX = NAMED_CHARACTERS_COLLECTION.get("unicode-to-latex", {})


AMSTEX_OPERATORS = {
    NAMED_CHARACTERS["Prime"]: "'",
    NAMED_CHARACTERS["Prime"] * 2: "''",
    NAMED_CHARACTERS["InvisibleTimes"]: " ",
    NAMED_CHARACTERS["Infinity"]: r"\infty ",
    operator_to_unicode["Times"]: r"\times ",
    "(": r"\left(",
    "[": r"\left[",
    "{": r"\left\{",
    ")": r"\right)",
    "]": r"\right]",
    "}": r"\right\}",
    NAMED_CHARACTERS["LeftDoubleBracket"]: r"\left[\left[",
    NAMED_CHARACTERS["RightDoubleBracket"]: r"\right]\right]",
    ",": ",",
    ", ": ", ",
    NAMED_CHARACTERS["Integral"]: r"\int",
    "\u2146": r"\, d",
    NAME_TO_WL_UNICODE["DifferentialD"]: r"\, d",
    NAMED_CHARACTERS["DifferentialD"]: r"\, d",
    NAMED_CHARACTERS["Sum"]: r"\sum",
    NAMED_CHARACTERS["Product"]: r"\prod",
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
        return NAMED_CHARACTERS_COLLECTION["ascii-operator-to-unicode"].get(
            ascii_op, ascii_op
        )
    if encoding in ("WMA",):
        return NAMED_CHARACTERS_COLLECTION["ascii-operator-to-wl-unicode"].get(
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
