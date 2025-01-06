# -*- coding: utf-8 -*-
# pylint: disable-msg=too-many-arguments

"""
Support for Set and SetDelayed, and other assignment-like builtins
"""

from typing import Callable, List, Optional, Tuple, cast

from mathics.core.atoms import Atom
from mathics.core.attributes import A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.definitions import Definition, Definitions
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import Rule
from mathics.core.symbols import Symbol, SymbolList
from mathics.core.systemsymbols import (
    SymbolAnd,
    SymbolBlank,
    SymbolCondition,
    SymbolHoldPattern,
    SymbolOptionValue,
    SymbolPart,
    SymbolPattern,
    SymbolRuleDelayed,
)


def build_rulopc(optval: BaseElement) -> Rule:
    """Build an option value rule for optval"""
    return Rule(
        Expression(
            SymbolOptionValue,
            Expression(SymbolPattern, Symbol("$cond$"), SymbolBlank),
        ),
        Expression(SymbolOptionValue, optval, Symbol("$cond$")),
    )


def get_symbol_list(expr: Expression, error_callback: Callable) -> Optional[List[str]]:
    """
    If ``expr`` is of the form ``List[Symbol___]`` returns a list
    with the names of the symbols as elements.
    If `expr` is a ``Symbol``, returns a list with a
    with the name of `expr` as its only element.
    Otherwise, calls `error_callback` over the element,
    and returns None.

    Parameters
    ----------
    expr : Expression
        The expression to be converted.
    error_callback : Callable
        a callback function to call if the conversion fails.

    Returns
    -------
    values : Optional[List[str]]
        a list with the names, or None.

    """
    if expr.has_form("List", None):
        list_expr = expr.elements
    else:
        list_expr = [expr]
    values = []
    for item in list_expr:
        name = item.get_name()
        if name:
            values.append(name)
        else:
            error_callback(item)
            return None
    return values


def get_symbol_values(
    symbol: BaseElement, func_name: str, position: str, evaluation: Evaluation
) -> Optional[ListExpression]:
    """
    Build a ListExpression with the rules associated to `symbol` in the
    `Definitions` object of `evaluation`.

    Parameters
    ----------
    symbol : BaseElement
        The target symbol.
    func_name : str
        the name of the caller.
    position : str
        the kind of rule ('ownvalue', 'downvalue', 'upvalue', 'default', etc)
    evaluation : Evaluation
        The evaluation object.

    Returns
    -------
    Optional[ListExpression]
        A list of rules. None if `symbol` is not a Symbol.

    """
    name = symbol.get_name()
    if not name:
        evaluation.message(func_name, "sym", symbol, 1)
        return None
    definitions = evaluation.definitions
    definition = (
        definitions.get_definition(name)
        if position in ("default",)
        else definitions.get_user_definition(name)
    )
    if definition is None:
        return ListExpression()

    elements = []
    for rule in cast(Definition, definition).get_values_list(position):
        if isinstance(rule, Rule):
            pattern = rule.pattern
            if pattern.has_form("HoldPattern", 1):
                expr_pattern = pattern.expr
            else:
                expr_pattern = Expression(SymbolHoldPattern, pattern.expr)
            elements.append(Expression(SymbolRuleDelayed, expr_pattern, rule.replace))
    return ListExpression(*elements)


def is_protected(tag: str, defin: Definitions) -> bool:
    """Check if the `Symbol` with name `tag`
    is protected in the `Definitions` `defin`"""
    return A_PROTECTED & defin.get_attributes(tag)


def normalize_lhs(lhs, evaluation):
    """
    Process the lhs in a way that
    * if it is a conditional expression, reduce it to
      a shallow conditional expression
      ( Conditional[Conditional[...],tst] -> Conditional[stripped_lhs, tst])
      with `stripped_lhs` the result of strip all the conditions from lhs.
    * if ``stripped_lhs`` is not a ``List`` or a ``Part`` expression, evaluate the
      elements.

    returns a tuple with the normalized lhs, and the lookup_name of the head in stripped_lhs.
    """
    cond = None
    if lhs.get_head() is SymbolCondition:
        lhs, cond = unroll_conditions(lhs)

    lookup_name = lhs.get_lookup_name()
    # In WMA, before the assignment, the elements of the (stripped) LHS are evaluated.
    if isinstance(lhs, Expression) and lhs.get_head() not in (SymbolList, SymbolPart):
        lhs = lhs.evaluate_elements(evaluation)
    # If there was a conditional expression, rebuild it with the processed lhs
    if cond:
        lhs = Expression(cond.get_head(), lhs, cond.elements[1])
    return lhs, lookup_name


def repl_pattern_by_symbol(expr: BaseElement) -> BaseElement:
    """
    If `expr` is a named pattern expression `Pattern[symb, pat]`,
    return `symb`. Otherwise, return `expr`.
    """
    elements = expr.get_elements()
    if len(elements) == 0:
        return expr

    head = expr.get_head()
    head_name = head.get_name()
    if head_name == "System`Pattern":
        return elements[0]

    changed = False
    new_elements = []
    for _element in elements:
        element = repl_pattern_by_symbol(_element)
        if element is not _element:
            changed = True
        new_elements.append(element)
    if changed:
        return Expression(head, *new_elements)
    return expr


# Here are the functions related to assign

# Auxiliary routines


def rejected_because_protected(
    self: Builtin,
    lhs: BaseElement,
    tag: str,
    evaluation: Evaluation,
    ignore: bool = False,
) -> bool:
    """


    Parameters
    ----------
    lhs : BaseElement
        DESCRIPTION.
    tag : str
        DESCRIPTION.
    evaluation : Evaluation
        DESCRIPTION.
    ignore : bool, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    bool
        DESCRIPTION.

    """
    defs = evaluation.definitions
    if not ignore and is_protected(tag, defs):
        if lhs.get_name() == tag:
            evaluation.message(self.get_name(), "wrsym", Symbol(tag))
        else:
            evaluation.message(self.get_name(), "write", Symbol(tag), lhs)
        return True
    return False


def unroll_conditions(lhs: BaseElement) -> Tuple[BaseElement, Optional[Expression]]:
    """
    If `element` is a nested `Condition` expression,
    gather all the conditions in a single one, and returns a tuple
    with the `element` stripped from the conditions and the shallow condition.
    If there is not any condition, returns the lhs and None
    """
    if isinstance(lhs, Symbol):
        return lhs, None

    expr: Expression = cast(Expression, lhs)
    name, lhs_elements = expr.get_head_name(), expr.get_elements()
    conditions = []
    # This handle the case of many successive conditions:
    # f[x_]/; cond1 /; cond2 ... ->  f[x_]/; And[cond1, cond2, ...]
    while name == "System`Condition" and len(lhs_elements) == 2:
        conditions.append(lhs_elements[1])
        lhs = lhs_elements[0]
        if isinstance(lhs, Atom):
            break
        expr = cast(Expression, lhs)
        name, lhs_elements = expr.get_head_name(), expr.elements
    if len(conditions) == 0:
        return lhs, None

    condition: BaseElement = (
        Expression(SymbolAnd, *conditions) if len(conditions) > 1 else conditions[0]
    )
    condition = Expression(SymbolCondition, lhs, condition)
    return lhs, condition


def unroll_patterns(
    lhs: BaseElement, rhs: BaseElement, evaluation: Evaluation
) -> Tuple[BaseElement, BaseElement]:
    """
    Pattern[symb, pat]=rhs -> pat = (rhs/.(symb->pat))
    HoldPattern[lhs] = rhs -> lhs = rhs
    """
    if isinstance(lhs, Atom):
        return lhs, rhs
    name = lhs.get_head_name()
    lhs_elements = cast(Expression, lhs).elements
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
