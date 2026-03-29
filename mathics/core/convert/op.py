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
CHARACTER_TO_NAME = {
    char: rf"\[{name}]"
    for name, char in NAMED_CHARACTERS_COLLECTION["named-characters"].items()
}


ESCAPE_CODE_BY_DIGITS = {
    1: r"\.0",
    2: r"\.",
    3: r"\:0",
    4: r"\:",
    5: r"\|0",
    6: r"\|",
}

builtin_constants = NAMED_CHARACTERS_COLLECTION["builtin-constants"]
operator_to_unicode = NAMED_CHARACTERS_COLLECTION["operator-to-unicode"]
operator_to_ascii = NAMED_CHARACTERS_COLLECTION["operator-to-ascii"]
unicode_operator_to_ascii = {
    val: operator_to_ascii[key] for key, val in operator_to_unicode.items()
}


# This dictionary is used for the default encoding from Unicode/UTF-8 to ASCII

UNICODE_CHARACTER_TO_ASCII = CHARACTER_TO_NAME.copy()
UNICODE_CHARACTER_TO_ASCII.update(
    {
        ch: operator_to_ascii[name]
        for name, ch in operator_to_unicode.items()
        if name in operator_to_ascii
    }
)
# These characters are used in encoding
# in WMA, and differs from what we have
# in Mathics3-scanner tables:
UNICODE_CHARACTER_TO_ASCII.update(
    {
        operator_to_unicode["Times"]: r" x ",
        "": r"\[DifferentialD]",
    }
)


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


def string_to_invertible_ansi(string: str):
    """
    Replace non-ANSI characters by their names. If the character
    does not have a name, use the WMA hex character code form.
    Passing the string through `evaluation.parse` brings back
    the original string.
    This is used in particular for rendering `FullForm` expressions,
    and when `Style` is called with both the options
    `ShowStringCharacters->True` and `ShowSpecialCharacters->False`.
    """
    result = ""
    for c in string:
        ord_c = ord(c)
        if ord_c < 128:
            result += c
        else:
            named = CHARACTER_TO_NAME.get(c, None)
            if named is None:
                named = hex(ord_c)[2:]
                named = ESCAPE_CODE_BY_DIGITS[len(named)] + named
            result += named
    return result


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
