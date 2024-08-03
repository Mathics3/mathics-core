# -*- coding: utf-8 -*-
"""
Support for Set and SetDelayed, and other assignment-like builtins
"""

from functools import reduce
from typing import Optional, Tuple

from mathics.core.atoms import Atom, Integer
from mathics.core.attributes import A_LOCKED, A_PROTECTED, attribute_string_to_number
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.pattern import Pattern
from mathics.core.rules import Rule
from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolList,
    SymbolMaxPrecision,
    SymbolMinPrecision,
    SymbolN,
    SymbolTrue,
    valid_context_name,
)
from mathics.core.systemsymbols import (
    SymbolAnd,
    SymbolBlank,
    SymbolCondition,
    SymbolHoldPattern,
    SymbolOptionValue,
    SymbolPattern,
    SymbolRuleDelayed,
)
from mathics.eval.parts import walk_parts


class AssignmentException(Exception):
    def __init__(self, lhs, rhs) -> None:
        super().__init__(" %s cannot be assigned to %s" % (rhs, lhs))
        self.lhs = lhs
        self.rhs = rhs


# This also is going to be removed after #621

def build_rulopc(optval):
    return Rule(
        Expression(
            SymbolOptionValue,
            Expression(SymbolPattern, Symbol("$cond$"), SymbolBlank),
        ),
        Expression(SymbolOptionValue, optval, Symbol("$cond$")),
    )


def find_focus(focus):
    """
    Recursively, look for the (true) focus expression, i.e.,
    the expression after strip it from Condition, Pattern and HoldPattern
    wrapping expressions.
    """
    name = focus.get_lookup_name()
    if isinstance(focus, Pattern):
        return find_focus(focus.expr)
    if name == "System`HoldPattern":
        if len(focus.elements) == 1:
            return find_focus(focus.elements[0])
        # If HoldPattern appears with more than one element,
        # the message
        # "HoldPattern::argx: HoldPattern called with 2 arguments; 1 argument is expected."
        # must be shown.
        raise AssignmentException(focus, None)
    if focus.has_form("System`Condition", 2):
        return find_focus(focus.elements[0])
    if name == "System`Optional":
        return None
    if name == "System`Pattern" and len(focus.elements) == 2:
        pat = focus.elements[1]
        if pat.get_head_name() in (
            "System`Blank",
            "System`BlankSequence",
            "System`BlankNullSequence",
        ):
            elems = pat.elements
            if len(elems) == 0:
                return None
            return find_focus(elems[0])
        else:
            return find_focus(pat)
    return focus


def find_tag_and_check(lhs, tags, evaluation):
    name = lhs.get_head_name()
    if len(lhs.elements) != 1:
        evaluation.message_args(name, len(lhs.elements), 1)
        raise AssignmentException(lhs, None)
    tag = lhs.elements[0].get_name()
    if not tag:
        evaluation.message(name, "sym", lhs.elements[0], 1)
        raise AssignmentException(lhs, None)
    if tags is not None and tags != [tag]:
        evaluation.message(name, "tag", Symbol(name), Symbol(tag))
        raise AssignmentException(lhs, None)
    if is_protected(tag, evaluation.definitions):
        evaluation.message(name, "wrsym", Symbol(tag))
        raise AssignmentException(lhs, None)
    return tag


def get_symbol_list(list, error_callback):
    if list.has_form("List", None):
        list = list.elements
    else:
        list = [list]
    values = []
    for item in list:
        name = item.get_name()
        if name:
            values.append(name)
        else:
            error_callback(item)
            return None
    return values


# used in ``mathics.builtin.assignment.types`` and
# ``mathics.builtin.atomic.symbols``.
def get_symbol_values(symbol, func_name, position, evaluation):
    name = symbol.get_name()
    if not name:
        evaluation.message(func_name, "sym", symbol, 1)
        return
    if position in ("default",):
        definition = evaluation.definitions.get_definition(name)
    else:
        definition = evaluation.definitions.get_user_definition(name)
    elements = []
    for rule in definition.get_values_list(position):
        if isinstance(rule, Rule):
            pattern = rule.pattern
            if pattern.has_form("HoldPattern", 1):
                pattern = pattern.expr
            else:
                pattern = Expression(SymbolHoldPattern, pattern.expr)
            elements.append(Expression(SymbolRuleDelayed, pattern, rule.replace))
    return ListExpression(*elements)


def is_protected(tag, defin):
    return A_PROTECTED & defin.get_attributes(tag)


# Used in unroll_patterns
def repl_pattern_by_symbol(expr):
    elements = expr.get_elements()
    if len(elements) == 0:
        return expr

    headname = expr.get_head_name()
    if headname == "System`Pattern":
        return elements[0]

    changed = False
    new_elements = []
    for _element in elements:
        element = repl_pattern_by_symbol(_element)
        if element is not _element:
            changed = True
        new_elements.append(element)
    if changed:
        return Expression(headname, *new_elements)
    else:
        return expr


# Here are the functions related to assign

# Auxiliary routines


def rejected_because_protected(self, lhs, tag, evaluation):
    defs = evaluation.definitions
    if is_protected(tag, defs):
        if lhs.get_name() == tag:
            evaluation.message(self.get_name(), "wrsym", Symbol(tag))
        else:
            evaluation.message(self.get_name(), "write", Symbol(tag), lhs)
        return True
    return False


def unroll_patterns(lhs, rhs, evaluation) -> Tuple[BaseElement, BaseElement]:
    """
    Pattern[symb, pat]=rhs -> pat = (rhs/.(symb->pat))
    HoldPattern[lhs] = rhs -> lhs = rhs
    """
    if isinstance(lhs, Atom):
        return lhs, rhs
    name = lhs.get_head_name()
    lhs_elements = lhs.elements
    if name == "System`Pattern":
        lhs = lhs_elements[1]
        rulerepl = (lhs_elements[0], repl_pattern_by_symbol(lhs))
        # Maybe this replamement should be delayed instead,
        # like
        # rhs = Expression(Symbol("System`Replace"), Rule(*rulerepl))
        # TODO: check if this is the correct behavior.
        rhs, _ = rhs.do_apply_rules([Rule(*rulerepl)], evaluation)
        name = lhs.get_head_name()
    elif name == "System`HoldPattern":
        lhs = lhs_elements[0]
    return lhs, rhs


def unroll_conditions(lhs) -> Tuple[BaseElement, Optional[Expression]]:
    """
    If lhs is a nested `Condition` expression,
    gather all the conditions in a single one, and returns a tuple
    with the lhs stripped from the conditions and the shallow condition.
    If there is not any condition, returns the lhs and None
    """
    if isinstance(lhs, Symbol):
        return lhs, None
    else:
        name, lhs_elements = lhs.get_head_name(), lhs.get_elements()
    condition = []
    # This handle the case of many sucesive conditions:
    # f[x_]/; cond1 /; cond2 ... ->  f[x_]/; And[cond1, cond2, ...]
    while name == "System`Condition" and len(lhs.elements) == 2:
        condition.append(lhs_elements[1])
        lhs = lhs_elements[0]
        if isinstance(lhs, Atom):
            break
        name, lhs_elements = lhs.get_head_name(), lhs.elements
    if len(condition) == 0:
        return lhs, None
    if len(condition) > 1:
        condition = Expression(SymbolAnd, *condition)
    else:
        condition = condition[0]
    condition = Expression(SymbolCondition, lhs, condition)
    # lhs._format_cache = None
    return lhs, condition


# Here starts the functions that implement `assign` for different
# kind of expressions. Maybe they should be put in a separated module, or
# maybe they should be member functions of _SetOperator.
