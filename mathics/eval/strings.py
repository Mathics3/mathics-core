"""
String-related evaluation functions.
"""

import re

from mathics_scanner.characters import replace_box_unicode_with_ascii

from mathics.builtin.box.layout import RowBox
from mathics.core.atoms import Integer, Integer0, Integer1, Integer3, String
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_bool
from mathics.core.convert.regex import to_regex
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.expression_predefined import MATHICS3_INFINITY
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.format.box import format_element


def eval_ToString(
    expr: BaseElement, form: Symbol, encoding: String, evaluation: Evaluation
) -> String:
    boxes = format_element(expr, evaluation, form, encoding=encoding)
    text = boxes.to_text(evaluation=evaluation)
    return String(text)


def eval_StringContainsQ(name, string, patt, evaluation, options, matched):
    # Get the pattern list and check validity for each
    if patt.has_form("List", None):
        patts = patt.elements
    else:
        patts = [patt]
    re_patts = []
    for p in patts:
        py_p = to_regex(p, show_message=evaluation.message)
        if py_p is None:
            evaluation.message("StringExpression", "invld", p, patt)
            return
        re_patts.append(py_p)

    flags = re.MULTILINE
    if options["System`IgnoreCase"] is SymbolTrue:
        flags = flags | re.IGNORECASE

    def _search(patts, str, flags, matched):
        if any(re.search(p, str, flags=flags) for p in patts):
            return from_bool(matched)
        return from_bool(not matched)

    # Check string validity and perform regex searchhing
    if string.has_form("List", None):
        py_s = [s.get_string_value() for s in string.elements]
        if any(s is None for s in py_s):
            evaluation.message(
                name, "strse", Integer1, Expression(Symbol(name), string, patt)
            )
            return
        return to_mathics_list(*[_search(re_patts, s, flags, matched) for s in py_s])
    else:
        py_s = string.get_string_value()
        if py_s is None:
            evaluation.message(
                name, "strse", Integer1, Expression(Symbol(name), string, patt)
            )
            return
        return _search(re_patts, py_s, flags, matched)


def eval_StringFind(self, string, rule, n, evaluation, options, cases):
    if n.sameQ(Symbol("System`Private`Null")):
        expr = Expression(Symbol(self.get_name()), string, rule)
        n = None
    else:
        expr = Expression(Symbol(self.get_name()), string, rule, n)

    # convert string
    if isinstance(string, ListExpression):
        py_strings = [stri.get_string_value() for stri in string.elements]
        if None in py_strings:
            evaluation.message(self.get_name(), "strse", Integer1, expr)
            return
    else:
        py_strings = string.get_string_value()
        if py_strings is None:
            evaluation.message(self.get_name(), "strse", Integer1, expr)
            return

    # convert rule
    def convert_rule(r):
        if r.has_form("Rule", None) and len(r.elements) == 2:
            py_s = to_regex(r.elements[0], show_message=evaluation.message)
            if py_s is None:
                evaluation.message(
                    "StringExpression", "invld", r.elements[0], r.elements[0]
                )
                return
            py_sp = r.elements[1]
            return py_s, py_sp
        elif cases:
            py_s = to_regex(r, show_message=evaluation.message)
            if py_s is None:
                evaluation.message("StringExpression", "invld", r, r)
                return
            return py_s, None

        evaluation.message(self.get_name(), "srep", r)
        return

    if rule.has_form("List", None):
        py_rules = [convert_rule(r) for r in rule.elements]
    else:
        py_rules = [convert_rule(rule)]
    if None in py_rules:
        return None

    # convert n
    if n is None:
        py_n = 0
    elif n.sameQ(MATHICS3_INFINITY):
        py_n = 0
    else:
        py_n = n.get_int_value()
        if py_n is None or py_n < 0:
            evaluation.message(self.get_name(), "innf", Integer3, expr)
            return

    # flags
    flags = re.MULTILINE
    if options["System`IgnoreCase"] is SymbolTrue:
        flags = flags | re.IGNORECASE

    if isinstance(py_strings, list):
        return to_mathics_list(
            *[
                self._find(py_stri, py_rules, py_n, flags, evaluation)
                for py_stri in py_strings
            ]
        )
    else:
        return self._find(py_strings, py_rules, py_n, flags, evaluation)


def safe_backquotes(string: str):
    """Handle escaped backquotes."""
    # TODO: Fix in the scanner how escaped backslashes
    # are parsed.
    # "\\`" must be parsed as "\\`" in order this
    # works properly, but the parser converts `\\`
    # into `\`.
    string = string.replace(r"\\", r"\[RawBackslash]")
    string = string.replace(r"\`", r"\[RawBackquote]")
    string = string.replace(r"\[RawBackslash]", r"\\")
    return string


def eval_StringForm_MakeBoxes(strform: String, items, form, evaluation: Evaluation):
    """MakeBoxes[StringForm[s_String, items___], form_]"""

    if not isinstance(strform, String):
        raise ValueError

    items = [format_element(item, evaluation, form) for item in items]

    curr_indx = 0
    strform_str = safe_backquotes(replace_box_unicode_with_ascii(strform.value))

    parts = strform_str.split("`")

    # Rocky: This looks like a hack to me: is it needed?
    parts = [part.replace(r"\[RawBackquote]", "`") for part in parts]

    result = [String(parts[0])]
    if len(parts) <= 1:
        return result[0]

    quote_open = True
    remaining = len(parts) - 1
    num_items = len(items)
    for part in parts[1:]:
        remaining -= 1
        # If quote_open, the part must be a placeholder
        if quote_open:
            # If not remaining, there is a not closed '`'
            # character:
            if not remaining:
                evaluation.message("StringForm", "sfq", strform)
                return strform.value

            # part must be an index or an empty string.
            # If is an empty string, pick the next element:
            if part == "":
                if curr_indx >= num_items:
                    evaluation.message(
                        "StringForm",
                        "sfr",
                        Integer(num_items + 1),
                        Integer(num_items),
                        strform,
                    )
                    return strform.value

                result.append(items[curr_indx])
                curr_indx += 1
                quote_open = False
                continue
            # Otherwise, must be a positive integer:
            try:
                indx = int(part)
            except ValueError:
                evaluation.message(
                    "StringForm", "sfr", Integer0, Integer(num_items), strform
                )
                return strform.value

            # indx must be greater than 0, and not greater than
            # the number of items
            if indx <= 0 or indx > len(items):
                evaluation.message(
                    "StringForm", "sfr", Integer(indx), Integer(len(items)), strform
                )
                return strform.value

            result.append(items[indx - 1])
            curr_indx = indx
            quote_open = False
            continue

        result.append(String(part))
        quote_open = True

    return RowBox(ListExpression(*result))
