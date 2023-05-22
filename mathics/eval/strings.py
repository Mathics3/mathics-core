"""
String-related evaluation functions.
"""
import re
from binascii import hexlify
from typing import Optional, Tuple

from mathics.core.atoms import String
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
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
from mathics.eval.makeboxes import format_element

_regex_longest = {
    "+": "+",
    "*": "*",
}

_regex_shortest = {
    "+": "+?",
    "*": "*?",
}

# Regular expressions for various symbols
REGEXP_FOR_SYMBOLS = {
    SymbolNumberString: r"[-|+]?(\d+(\.\d*)?|\.\d+)?",
    SymbolWhitespace: r"(?u)\s+",
    SymbolDigitCharacter: r"\d",
    SymbolWhitespaceCharacter: r"(?u)\s",
    SymbolWordCharacter: r"(?u)[^\W_]",
    SymbolStartOfLine: r"^",
    SymbolEndOfLine: r"$",
    SymbolStartOfString: r"\A",
    SymbolEndOfString: r"\Z",
    SymbolWordBoundary: r"\b",
    SymbolLetterCharacter: r"(?u)[^\W_0-9]",
    SymbolHexadecimalCharacter: r"[0-9a-fA-F]",
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

    result, global_re_options = to_regex_internal(
        expr, evaluation, q, groups, abbreviated_patterns, global_re_options=""
    )
    if result is None:
        return None

    # FIXME: we probably want global_re_options to be flag values
    # which we then convert into a string. This is cleaner and
    # it ensures we set a global re flag only once.
    return global_re_options + result


# FIXME: fix up to actually set global_re_option flags.
def to_regex_internal(
    expr: Expression,
    evaluation: Evaluation,
    q,
    groups,
    abbreviated_patterns,
    global_re_options: str,
) -> Tuple[Optional[str], str]:
    """
    Internal recursive routine to for to_regex_internal.
    From to_regex,  values have been initialized.
    (None, "") is returned if there is an error of some sort.
    """

    def recurse(x: Expression, quantifiers=q) -> Tuple[Optional[str], str]:
        """
        Shortend way to call to_regexp_internal -
        on the expr and quantifiers change here.
        """
        return to_regex_internal(
            expr=x,
            evaluation=evaluation,
            q=quantifiers,
            groups=groups,
            abbreviated_patterns=abbreviated_patterns,
            global_re_options=global_re_options,
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
        return result, global_re_options

    if expr.has_form("RegularExpression", 1):
        regex = expr.elements[0].get_string_value()
        if regex is None:
            return regex, global_re_options
        try:
            re.compile(regex)
            # Don't return the compiled regex because it may need to composed
            # further e.g. StringExpression["abc", RegularExpression[regex2]].
            return regex, global_re_options
        except re.error:
            return None, ""  # invalid regex

    if isinstance(expr, Symbol):
        return REGEXP_FOR_SYMBOLS.get(expr), global_re_options

    if expr.has_form("CharacterRange", 2):
        (start, stop) = (element.get_string_value() for element in expr.elements)
        if all(x is not None and len(x) == 1 for x in (start, stop)):
            return (
                "[{0}-{1}]".format(re.escape(start), re.escape(stop)),
                global_re_options,
            )

    if expr.has_form("Blank", 0):
        return r"(.|\n)", global_re_options
    if expr.has_form("BlankSequence", 0):
        return r"(.|\n)" + q["+"], global_re_options
    if expr.has_form("BlankNullSequence", 0):
        return r"(.|\n)" + q["*"], global_re_options
    if expr.has_form("Except", 1, 2):
        if len(expr.elements) == 1:
            # TODO: Check if this shouldn't be SymbolBlank
            # instead of SymbolBlank[]
            elements = [expr.elements[0], Expression(SymbolBlank)]
        else:
            elements = [expr.elements[0], expr.elements[1]]
        elements = [recurse(element) for element in elements]
        if all(element is not None for element in elements):
            regexp = [element[0] for element in elements]
            global_re_options += "".join(element[1] for element in elements)
            return "(?!{0}){1}".format(*regexp), global_re_options
    if expr.has_form("Characters", 1):
        element = expr.elements[0].get_string_value()
        if element is not None:
            return "[{0}]".format(re.escape(element)), global_re_options
    if expr.has_form("StringExpression", None):
        elements = [recurse(element) for element in expr.elements]
        if (None, "") in elements:
            return None, ""
        regexp_str = "".join(element[0] for element in elements)
        global_re_options += "".join(element[1] for element in elements)
        return regexp_str, global_re_options
    if expr.has_form("Repeated", 1):
        element, global_re_options = recurse(expr.elements[0])
        if element is None:
            return None, ""
        return "({0})".format(element) + q["+"], global_re_options
    if expr.has_form("RepeatedNull", 1):
        element, global_re_options = recurse(expr.elements[0])
        if element is not None:
            return "({0})".format(element) + q["*"], global_re_options
    if expr.has_form("Alternatives", None):
        elements = [recurse(element) for element in expr.elements]
        if all(element != (None, "") for element in elements):
            regexp_str = "|".join(element[0] for element in elements)
            global_re_options += "".join(element[1] for element in elements)
            return regexp_str, global_re_options
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
            return "(?P=%s)" % _encode_pname(name), global_re_options
        else:
            groups[name] = expr.elements[1]
            result_regexp, global_re_options = recurse(expr.elements[1])
            return (
                "(?P<%s>%s)" % (_encode_pname(name), result_regexp),
                global_re_options,
            )

    return None, ""
