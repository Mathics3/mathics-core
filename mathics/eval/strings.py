import re
import sys
from binascii import hexlify
from typing import Optional

from mathics.core.atoms import String
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolBlank
from mathics.eval.makeboxes import format_element

_regex_longest = {
    "+": "+",
    "*": "*",
}

_regex_shortest = {
    "+": "+?",
    "*": "*?",
}


def _encode_pname(name):
    return "n" + hexlify(name.encode("utf8")).decode("utf8")


# A better thing to do would be to write a pymathics module that
def eval_ToString(
    expr: BaseElement, form: Symbol, encoding: String, evaluation: Evaluation
) -> String:
    boxes = format_element(expr, evaluation, form, encoding=encoding)
    text = boxes.boxes_to_text(evaluation=evaluation)
    return String(text)


# FIXME
# For 3.11, global options in a regexp must appear
# at the beginning and not inside a group.
# To support this, we need split out into such global flags.
# in particular re.IGNORECASE (?i), and re.ASCII (?u).
# These then are added at result string at the end just before return.
def to_regex(
    expr: Expression,
    evaluation: Evaluation,
    q=_regex_longest,
    groups=None,
    abbreviated_patterns=False,
) -> Optional[str]:
    """
    Convert an expression into a Python regular expression and return that.
    None is returned if there is an error of some sort.
    """
    if expr is None:
        return None

    if groups is None:
        groups = {}

    def recurse(x, quantifiers=q):
        return to_regex(x, evaluation, q=quantifiers, groups=groups)

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
        return {
            "System`NumberString": r"[-|+]?(\d+(\.\d*)?|\.\d+)?",
            "System`Whitespace": r"\s+",
            "System`DigitCharacter": r"\d",
            "System`WhitespaceCharacter": r"\s",
            "System`WordCharacter": r"[^\W_]",
            "System`StartOfLine": r"^",
            "System`EndOfLine": r"$",
            "System`StartOfString": r"\A",
            "System`EndOfString": r"\Z",
            "System`WordBoundary": r"\b",
            "System`LetterCharacter": r"[^\W_0-9]",
            "System`HexadecimalCharacter": r"[0-9a-fA-F]",
        }.get(expr.get_name())

    if expr.has_form("CharacterRange", 2):
        (start, stop) = (element.get_string_value() for element in expr.elements)
        if all(x is not None and len(x) == 1 for x in (start, stop)):
            return "[{0}-{1}]".format(re.escape(start), re.escape(stop))

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
        if all(element is not None for element in elements):
            return "(?!{0}){1}".format(*elements)
    if expr.has_form("Characters", 1):
        element = expr.elements[0].get_string_value()
        if element is not None:
            return "[{0}]".format(re.escape(element))
    if expr.has_form("StringExpression", None):
        elements = [recurse(element) for element in expr.elements]
        if None in elements:
            return None
        return "".join(elements)
    if expr.has_form("Repeated", 1):
        element = recurse(expr.elements[0])
        if element is not None:
            return "({0})".format(element) + q["+"]
    if expr.has_form("RepeatedNull", 1):
        element = recurse(expr.elements[0])
        if element is not None:
            return "({0})".format(element) + q["*"]
    if expr.has_form("Alternatives", None):
        elements = [recurse(element) for element in expr.elements]
        if all(element is not None for element in elements):
            return "|".join(elements)
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
            elif not expr.elements[1].sameQ(patt):
                evaluation.message(
                    "StringExpression", "cond", expr.elements[0], expr, expr.elements[0]
                )
            return "(?P=%s)" % _encode_pname(name)
        else:
            groups[name] = expr.elements[1]
            return "(?P<%s>%s)" % (_encode_pname(name), recurse(expr.elements[1]))

    return None
