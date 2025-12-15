"""
Convert expressions to Python regular expressions
"""
import re
from binascii import hexlify
from typing import Callable, Optional

from mathics.core.atoms import String
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolDigitCharacter,
    SymbolEndOfLine,
    SymbolEndOfString,
    SymbolHexadecimalCharacter,
    SymbolLetterCharacter,
    SymbolNumberString,
    SymbolStartOfLine,
    SymbolStartOfString,
    SymbolWhitespace,
    SymbolWhitespaceCharacter,
    SymbolWordBoundary,
    SymbolWordCharacter,
)

_regex_longest = {
    "+": "+",
    "*": "*",
}

_regex_shortest = {
    "+": "+?",
    "*": "*?",
}

# Regular expressions for various symbols.
# Note: the regexp patterns below must not contain
# re global flag like ?u or ?i.
REGEXP_FOR_SYMBOLS = {
    SymbolNumberString: r"[-|+]?(\d+(\.\d*)?|\.\d+)?",
    SymbolWhitespace: r"\s+",
    SymbolDigitCharacter: r"\d",
    SymbolWhitespaceCharacter: r"\s",
    SymbolWordCharacter: r"[^\W_]",
    SymbolStartOfLine: r"^",
    SymbolEndOfLine: r"$",
    SymbolStartOfString: r"\A",
    SymbolEndOfString: r"\Z",
    SymbolWordBoundary: r"\b",
    SymbolLetterCharacter: r"[^\W_0-9]",
    SymbolHexadecimalCharacter: r"[0-9a-fA-F]",
}


def _encode_pname(name):
    return "n" + hexlify(name.encode("utf8")).decode("utf8")


def to_regex(
    expr: Expression,
    q=_regex_longest,
    groups=None,
    abbreviated_patterns=False,
    show_message: Optional[Callable] = None,
) -> Optional[str]:
    """
    Convert an expression into a Python regular expression and return that.
    None is returned if there is an error of some sort.
    """
    if expr is None:
        return None

    if groups is None:
        groups = {}

    result = to_regex_internal(expr, q, groups, abbreviated_patterns, show_message)
    if result is None:
        return None

    return result


# Note: the code below must not introduct
# re global flag like ?u or ?i.
def to_regex_internal(
    expr: Expression,
    q,
    groups,
    abbreviated_patterns,
    show_message: Optional[Callable] = None,
) -> Optional[str]:
    """
    Internal recursive routine to for to_regex_internal.
    From to_regex,  values have been initialized.
    (None, "") is returned if there is an error of some sort.
    """

    def recurse(x: Expression, quantifiers=q) -> Optional[str]:
        """
        Shortened way to call to_regexp_internal -
        only the expr and quantifiers change here.
        """
        return to_regex_internal(
            expr=x,
            q=quantifiers,
            groups=groups,
            abbreviated_patterns=abbreviated_patterns,
            show_message=show_message,
        )

    if isinstance(expr, String):
        result = expr.get_string_value()
        if abbreviated_patterns:
            pieces = []
            i, j = 0, 0
            while j < len(result):
                c = result[j]
                if c == "\\" and j + 1 < len(result):
                    pieces.append(re.escape(result[i:j]))
                    pieces.append(re.escape(result[j + 1]))
                    j += 2
                    i = j
                elif c == "*":
                    pieces.append(re.escape(result[i:j]))
                    pieces.append("(.*)")
                    j += 1
                    i = j
                elif c == "@":
                    pieces.append(re.escape(result[i:j]))
                    # one or more characters, excluding uppercase letters
                    pieces.append("([^A-Z]+)")
                    j += 1
                    i = j
                else:
                    j += 1
            pieces.append(re.escape(result[i:j]))
            result = "".join(pieces)
        else:
            result = re.escape(result)
        return result

    if expr.has_form("RegularExpression", 1):
        regex = expr.elements[0].get_string_value()
        if regex is None:
            return regex
        try:
            re.compile(regex)
            # Don't return the compiled regex because it may need to composed
            # further e.g. StringExpression["abc", RegularExpression[regex2]].
            return regex
        except re.error:
            return None  # invalid regex

    if isinstance(expr, Symbol):
        return REGEXP_FOR_SYMBOLS.get(expr)

    if expr.has_form("CharacterRange", 2):
        start, stop = (element.get_string_value() for element in expr.elements)
        if all(x is not None and len(x) == 1 for x in (start, stop)):
            return f"[{re.escape(start)}-{re.escape(stop)}]"

    if expr.has_form("Blank", 0):
        return r"(.|\n)"
    if expr.has_form("BlankSequence", 0):
        return r"(.|\n)" + q["+"]
    if expr.has_form("BlankNullSequence", 0):
        return r"(.|\n)" + q["*"]
    if expr.has_form("Except", 1, 2):
        if len(expr.elements) == 1:
            # TODO: Check if this shouldn't be SymbolBlank
            # instead of SymbolBlank[]
            elements = [expr.elements[0], Expression(SymbolBlank)]
        else:
            elements = [expr.elements[0], expr.elements[1]]
        elements = [recurse(element) for element in elements]
        assert len(elements) == 2
        if all(element is not None for element in elements):
            return f"(?!{elements[0]}){elements[1]}"
    if expr.has_form("Characters", 1):
        element = expr.elements[0].get_string_value()
        if element is not None:
            return f"[{re.escape(element)}]"
    if expr.has_form("StringExpression", None):
        elements = [recurse(element) for element in expr.elements]
        if None in elements:
            return None  # invalid regex
        return "".join(element for element in elements)
    if expr.has_form("Repeated", 1):
        element = recurse(expr.elements[0])
        if element is None:
            return None  # invalid regex
        return f"({element})" + q["+"]
    if expr.has_form("RepeatedNull", 1):
        element = recurse(expr.elements[0])
        if element is None:
            return None  # invalid regex
        return f"({element})" + q["*"]
    if expr.has_form("Alternatives", None):
        elements = [recurse(element) for element in expr.elements]
        if all(element is not None for element in elements):
            return "|".join(elements)
        else:
            return None  # invalid regex
    if expr.has_form("Shortest", 1):
        return recurse(expr.elements[0], quantifiers=_regex_shortest)
    if expr.has_form("Longest", 1):
        return recurse(expr.elements[0], quantifiers=_regex_longest)
    if expr.has_form("Pattern", 2) and isinstance(expr.elements[0], Symbol):
        name = expr.elements[0].get_name()
        patt = groups.get(name, None)
        if patt is not None:
            if expr.elements[1].has_form("Blank", 0):
                pass  # ok, no warnings
            elif not expr.elements[1].sameQ(patt) and show_message:
                show_message(
                    "StringExpression", "cond", expr.elements[0], expr, expr.elements[0]
                )
            return f"(?P={_encode_pname(name)})"
        else:
            element = groups[name] = expr.elements[1]
            if element is None:
                return None
            result_regexp = recurse(element)
            if result_regexp is None:
                return None
            return f"(?P<{_encode_pname(name)}>{result_regexp})"

    return None
