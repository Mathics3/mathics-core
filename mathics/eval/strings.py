"""
String-related evaluation functions.
"""
import re

from mathics.core.atoms import Integer1, Integer3, String
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_bool
from mathics.core.convert.regex import to_regex
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.expression_predefined import MATHICS3_INFINITY
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.eval.makeboxes import format_element


# A better thing to do would be to write a pymathics module that
def eval_ToString(
    expr: BaseElement, form: Symbol, encoding: String, evaluation: Evaluation
) -> String:
    boxes = format_element(expr, evaluation, form, encoding=encoding)
    text = boxes.boxes_to_text(evaluation=evaluation)
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
