# -*- coding: utf-8 -*-
"""
Support for Set and SetDelayed, and other assignment-like builtins
"""

from typing import Optional, Tuple

from mathics.algorithm.parts import walk_parts
from mathics.core.atoms import Atom, Integer
from mathics.core.definitions import get_tag_position
from mathics.core.element import BaseElement
from mathics.core.evaluation import MAX_RECURSION_DEPTH, set_python_recursion_limit
from mathics.core.expression import Expression, SymbolDefault
from mathics.core.list import ListExpression
from mathics.core.pattern import Pattern
from mathics.core.rules import Rule
from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolList,
    SymbolMinPrecision,
    SymbolMaxPrecision,
    SymbolN,
    SymbolTrue,
    valid_context_name,
)
from mathics.core.systemsymbols import (
    SymbolAnd,
    SymbolBlank,
    SymbolCondition,
    SymbolHoldPattern,
    SymbolMachinePrecision,
    SymbolOptionValue,
    SymbolPart,
    SymbolPattern,
    SymbolRuleDelayed,
    SymbolSet,
    SymbolSetDelayed,
    SymbolTagSet,
    SymbolTagSetDelayed,
    SymbolUpSet,
    SymbolUpSetDelayed,
)


from mathics.core.attributes import attribute_string_to_number, A_LOCKED, A_PROTECTED

from functools import reduce


# In Set* operators, the default behavior is that the
# elements of the LHS are evaluated before the assignment.
# So, if we define
#
# F[x_]:=G[x]
#
# and then
#
# M[F[x_]]:=x^2
#
# The rule that is stored is
#
# M[G[x_]]->x^2
#
#
# This behaviour does not aplies to a reduces subset of expressions, like
# in
#
# A={1,2,3}
# Part[A,1]:=s
#
# in a way that the result of the second line is to change a part of `A`
# A->{s, 2, 3}
#
# instead of trying to assign 1:=s
#
# Something similar happens with the Set* expressions. For example,
# the expected behavior of
#
#  Set[F[x_],rhs_]:=Print["Do not set to F"]
#
#  is not to forbid assignments to `G`, but to F:
#
#  G[x_]:=x^4
#  still set the rule G[x_]->x^2
#
#  while
#
#  F[x_]:=x^4
#  just will print the warning "Do not set to F".
#
#
NOT_EVALUATE_ELEMENTS_IN_ASSIGNMENTS = (
    SymbolSet,
    SymbolSetDelayed,
    SymbolUpSet,
    SymbolUpSetDelayed,
    SymbolTagSet,
    SymbolTagSetDelayed,
    SymbolList,
    SymbolPart,
)


class AssignmentException(Exception):
    def __init__(self, lhs, rhs) -> None:
        super().__init__(" %s cannot be assigned to %s" % (rhs, lhs))
        self.lhs = lhs
        self.rhs = rhs


def assign_store_rules_by_tag(self, lhs, rhs, evaluation, tags, upset=None):
    """
    This is the default assignment. Stores a rule of the form lhs->rhs
    as a value associated to each symbol listed in tags.
    For special cases, such like conditions or patterns in the lhs,
    lhs and rhs are rewritten in a normal form, where
    conditions are associated to the lhs.
    """
    condition = None
    defs = evaluation.definitions
    tags, focus = process_tags_and_upset(tags, upset, self, lhs, evaluation)
    # TODO: check if we can invert the order, and call this just
    # in the special cases
    ignore_protection = process_assign_side_effects(
        self, lhs, rhs, focus, evaluation, tags, upset
    )
    # In WMA, this does not happens. However, if we remove this,
    # some combinatorica tests fail.
    # Also, should not be at the begining?
    lhs, rhs = process_rhs_conditions(lhs, rhs, evaluation)
    count = 0
    rule = Rule(lhs, rhs)
    position = "up" if upset else None
    for tag in tags:
        if not ignore_protection and rejected_because_protected(
            self, lhs, tag, evaluation
        ):
            continue
        count += 1
        defs.add_rule(tag, rule, position=position)
    return count > 0


def build_rulopc(optval):
    return Rule(
        Expression(
            SymbolOptionValue,
            Expression(SymbolPattern, Symbol("$cond$"), SymbolBlank),
        ),
        Expression(SymbolOptionValue, optval, Symbol("$cond$")),
    )


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
    if (
        isinstance(lhs, Expression)
        and lhs.get_head() not in NOT_EVALUATE_ELEMENTS_IN_ASSIGNMENTS
    ):
        lhs = lhs.evaluate_elements(evaluation)
    # If there was a conditional expression, rebuild it with the processed lhs
    if cond:
        lhs = Expression(cond.get_head(), lhs, cond.elements[1])
    return lhs, lookup_name


def repl_pattern_by_symbol(expr):
    elements = expr.get_elements()
    if len(elements) == 0:
        return expr

    headname = expr.get_head_name()
    if headname == "System`Pattern":
        return elements[0]

    changed = False
    new_elements = []
    for element in elements:
        element = repl_pattern_by_symbol(element)
        if not (element is element):
            changed = True
        new_elements.append(element)
    if changed:
        return Expression(headname, *new_elements)
    else:
        return expr


# Here are the functions related to assign

# Auxiliary routines


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
        rhs, status = rhs.do_apply_rules([Rule(*rulerepl)], evaluation)
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


def process_assign_attributes(self, lhs, rhs, evaluation, tags, upset):
    """
    Process the case where lhs is of the form
    `Attribute[symbol]`
    """
    name = lhs.get_head_name()
    if len(lhs.elements) != 1:
        evaluation.message_args(name, len(lhs.elements), 1)
        raise AssignmentException(lhs, rhs)
    tag = lhs.elements[0].get_name()
    if not tag:
        evaluation.message(name, "sym", lhs.elements[0], 1)
        raise AssignmentException(lhs, rhs)
    if tags is not None and tags != [tag]:
        evaluation.message(name, "tag", Symbol(name), Symbol(tag))
        raise AssignmentException(lhs, rhs)
    attributes_list = get_symbol_list(
        rhs, lambda item: evaluation.message(name, "sym", item, 1)
    )
    if attributes_list is None:
        raise AssignmentException(lhs, rhs)
    if A_LOCKED & evaluation.definitions.get_attributes(tag):
        evaluation.message(name, "locked", Symbol(tag))
        raise AssignmentException(lhs, rhs)

    def reduce_attributes_from_list(x: int, y: str) -> int:
        try:
            return x | attribute_string_to_number[y]
        except KeyError:
            evaluation.message("SetAttributes", "unknowattr", y)
            return x

    attributes = reduce(
        reduce_attributes_from_list,
        attributes_list,
        0,
    )

    evaluation.definitions.set_attributes(tag, attributes)

    return True


def process_assign_context(self, lhs, rhs, evaluation, tags, upset):
    lhs_name = lhs.get_head_name()
    new_context = rhs.get_string_value()
    if new_context is None or not valid_context_name(
        new_context, allow_initial_backquote=True
    ):
        evaluation.message(lhs_name, "cxset", rhs)
        raise AssignmentException(lhs, None)

    # With $Context in Mathematica you can do some strange
    # things: e.g. with $Context set to Global`, something
    # like:
    #    $Context = "`test`"; newsym
    # is accepted and creates Global`test`newsym.
    # Implement this behaviour by interpreting
    #    $Context = "`test`"
    # as
    #    $Context = $Context <> "test`"
    #
    if new_context.startswith("`"):
        new_context = evaluation.definitions.get_current_context() + new_context.lstrip(
            "`"
        )

    evaluation.definitions.set_current_context(new_context)
    return True


def process_assign_context_path(self, lhs, rhs, evaluation, tags, upset):
    lhs_name = lhs.get_name()
    currContext = evaluation.definitions.get_current_context()
    context_path = [s.get_string_value() for s in rhs.get_elements()]
    context_path = [
        s if (s is None or s[0] != "`") else currContext[:-1] + s for s in context_path
    ]
    if rhs.has_form("List", None) and all(valid_context_name(s) for s in context_path):
        evaluation.definitions.set_context_path(context_path)
        return True
    else:
        evaluation.message(lhs_name, "cxlist", rhs)
        raise AssignmentException(lhs, None)


def process_assign_default(self, lhs, rhs, evaluation, tags, upset):
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    count = 0
    defs = evaluation.definitions

    if len(lhs.elements) not in (1, 2, 3):
        evaluation.message_args(SymbolDefault, len(lhs.elements), 1, 2, 3)
        raise AssignmentException(lhs, None)
    focus = lhs.elements[0]
    tags, focus = process_tags_and_upset(tags, upset, self, lhs, evaluation, focus)
    lhs, rhs = process_rhs_conditions(lhs, rhs, evaluation, condition)
    rule = Rule(lhs, rhs)
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation):
            continue
        count += 1
        defs.add_default(tag, rule)
    return count > 0


def process_assign_definition_values(self, lhs, rhs, evaluation, tags, upset):
    name = lhs.get_head_name()
    tag = find_tag_and_check(lhs, tags, evaluation)
    rules = rhs.get_rules_list()
    if rules is None:
        evaluation.message(name, "vrule", lhs, rhs)
        raise AssignmentException(lhs, None)
    evaluation.definitions.set_values(tag, name, rules)
    return True


def process_assign_format(self, lhs, rhs, evaluation, tags, upset):
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    count = 0
    defs = evaluation.definitions

    if len(lhs.elements) not in (1, 2):
        evaluation.message_args("Format", len(lhs.elements), 1, 2)
        raise AssignmentException(lhs, None)
    if len(lhs.elements) == 2:
        form = lhs.elements[1]
        form_name = form.get_name()
        if not form_name:
            evaluation.message("Format", "fttp", lhs.elements[1])
            raise AssignmentException(lhs, None)
        # If the form is not in defs.printforms / defs.outputforms
        # add it.
        for form_list in (defs.outputforms, defs.printforms):
            if form not in form_list:
                form_list.append(form)
    else:
        form_name = [
            "System`StandardForm",
            "System`TraditionalForm",
            "System`OutputForm",
            "System`TeXForm",
            "System`MathMLForm",
        ]
    lhs = focus = lhs.elements[0]
    tags, focus = process_tags_and_upset(tags, upset, self, lhs, evaluation, focus)
    lhs, rhs = process_rhs_conditions(lhs, rhs, evaluation, condition)
    rule = Rule(lhs, rhs)
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation):
            continue
        count += 1
        defs.add_format(tag, rule, form_name)
    return count > 0


def process_assign_iteration_limit(lhs, rhs, evaluation):
    """
    Set ownvalue for the $IterationLimit symbol.
    """

    rhs_int_value = rhs.get_int_value()
    if (
        not rhs_int_value or rhs_int_value < 20
    ) and not rhs.get_name() == "System`Infinity":
        evaluation.message("$IterationLimit", "limset", rhs)
        raise AssignmentException(lhs, None)
    return False


def process_assign_line_number_and_history_length(
    self, lhs, rhs, evaluation, tags, upset
):
    """
    Set ownvalue for the $Line and $HistoryLength symbols.
    """

    lhs_name = lhs.get_name()
    rhs_int_value = rhs.get_int_value()
    if rhs_int_value is None or rhs_int_value < 0:
        evaluation.message(lhs_name, "intnn", rhs)
        raise AssignmentException(lhs, None)
    return False


def process_assign_list(self, lhs, rhs, evaluation, tags, upset):
    if not (
        rhs.get_head_name() == "System`List" and len(lhs.elements) == len(rhs.elements)
    ):  # nopep8
        evaluation.message(self.get_name(), "shape", lhs, rhs)
        return False
    result = True
    for left, right in zip(lhs.elements, rhs.elements):
        if not self.assign(left, right, evaluation):
            result = False
    return result


def process_assign_makeboxes(self, lhs, rhs, evaluation, tags, upset):
    # FIXME: the below is a big hack.
    # Currently MakeBoxes boxing is implemented as a bunch of rules.
    # See mathics.builtin.base contribute().
    # I think we want to change this so it works like normal SetDelayed
    # That is:
    #   MakeBoxes[CubeRoot, StandardForm] := RadicalBox[3, StandardForm]
    # rather than:
    #   MakeBoxes[CubeRoot, StandardForm] -> RadicalBox[3, StandardForm]

    makeboxes_rule = Rule(lhs, rhs, system=False)
    definitions = evaluation.definitions
    definitions.add_rule("System`MakeBoxes", makeboxes_rule, "down")
    #    makeboxes_defs = evaluation.definitions.builtin["System`MakeBoxes"]
    #    makeboxes_defs.add_rule(makeboxes_rule)
    return True


def process_assign_minprecision(self, lhs, rhs, evaluation, tags, upset):
    lhs_name = lhs.get_name()
    rhs_int_value = rhs.get_int_value()
    # $MinPrecision = Infinity is not allowed
    if rhs_int_value is not None and rhs_int_value >= 0:
        max_prec = evaluation.definitions.get_config_value("$MaxPrecision")
        if max_prec is not None and max_prec < rhs_int_value:
            evaluation.message("$MinPrecision", "preccon", SymbolMinPrecision)
            raise AssignmentException(lhs, None)
        return False
    else:
        evaluation.message(lhs_name, "precset", lhs, rhs)
        raise AssignmentException(lhs, None)


def process_assign_maxprecision(self, lhs, rhs, evaluation, tags, upset):
    lhs_name = lhs.get_name()
    rhs_int_value = rhs.get_int_value()
    if rhs.has_form("DirectedInfinity", 1) and rhs.elements[0].get_int_value() == 1:
        return False
    elif rhs_int_value is not None and rhs_int_value > 0:
        min_prec = evaluation.definitions.get_config_value("$MinPrecision")
        if min_prec is not None and rhs_int_value < min_prec:
            evaluation.message("$MaxPrecision", "preccon", SymbolMaxPrecision)
            raise AssignmentException(lhs, None)
        return False
    else:
        evaluation.message(lhs_name, "precset", lhs, rhs)
        raise AssignmentException(lhs, None)


def process_assign_messagename(self, lhs, rhs, evaluation, tags, upset):
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    count = 0
    defs = evaluation.definitions
    if len(lhs.elements) != 2:
        evaluation.message_args("MessageName", len(lhs.elements), 2)
        raise AssignmentException(lhs, None)
    focus = lhs.elements[0]
    tags, focus = process_tags_and_upset(tags, upset, self, lhs, evaluation, focus)
    lhs, rhs = process_rhs_conditions(lhs, rhs, evaluation, condition)
    rule = Rule(lhs, rhs)
    for tag in tags:
        # Messages can be assigned even if the symbol is protected...
        # if rejected_because_protected(self, lhs, tag, evaluation):
        #    continue
        count += 1
        defs.add_message(tag, rule)
    return count > 0


def process_assign_module_number(lhs, rhs, evaluation):
    """
    Set ownvalue for the $ModuleNumber symbol.
    """
    rhs_int_value = rhs.get_int_value()
    if not rhs_int_value or rhs_int_value <= 0:
        evaluation.message("$ModuleNumber", "set", rhs)
        raise AssignmentException(lhs, None)
    return False


def process_assign_options(self, lhs, rhs, evaluation, tags, upset):
    lhs_elements = lhs.elements
    name = lhs.get_head_name()
    if len(lhs_elements) != 1:
        evaluation.message_args(name, len(lhs_elements), 1)
        raise AssignmentException(lhs, rhs)
    tag = lhs_elements[0].get_name()
    if not tag:
        evaluation.message(name, "sym", lhs_elements[0], 1)
        raise AssignmentException(lhs, rhs)
    if tags is not None and tags != [tag]:
        evaluation.message(name, "tag", Symbol(name), Symbol(tag))
        raise AssignmentException(lhs, rhs)
    if is_protected(tag, evaluation.definitions):
        evaluation.message(name, "wrsym", Symbol(tag))
        raise AssignmentException(lhs, None)
    option_values = rhs.get_option_values(evaluation)
    if option_values is None:
        evaluation.message(name, "options", rhs)
        raise AssignmentException(lhs, None)
    evaluation.definitions.set_options(tag, option_values)
    return True


def process_assign_numericq(self, lhs, rhs, evaluation, tags, upset):
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    if rhs not in (SymbolTrue, SymbolFalse):
        evaluation.message("NumericQ", "set", lhs, rhs)
        # raise AssignmentException(lhs, rhs)
        return True
    elements = lhs.elements
    if len(elements) > 1:
        evaluation.message("NumericQ", "argx", Integer(len(elements)))
        # raise AssignmentException(lhs, rhs)
        return True
    target = elements[0]
    if isinstance(target, Symbol):
        name = target.get_name()
        definition = evaluation.definitions.get_definition(name)
        definition.is_numeric = rhs is SymbolTrue
        return True
    else:
        evaluation.message("NumericQ", "set", lhs, rhs)
        # raise AssignmentException(lhs, rhs)
        return True


def process_assign_n(self, lhs, rhs, evaluation, tags, upset):
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    defs = evaluation.definitions
    # If we try to set `N=4`, (issue #210) just deal with it as with a generic expression:
    if lhs is SymbolN:
        return assign_store_rules_by_tag(self, lhs, rhs, evaluation, tags, upset)

    if len(lhs.elements) not in (1, 2):
        evaluation.message_args("N", len(lhs.elements), 1, 2)
        raise AssignmentException(lhs, None)
    if len(lhs.elements) == 1:
        nprec = SymbolMachinePrecision
    else:
        nprec = lhs.elements[1]
    focus = lhs.elements[0]
    lhs = Expression(SymbolN, focus, nprec)
    tags, focus = process_tags_and_upset(tags, upset, self, lhs, evaluation, focus)
    count = 0
    lhs, rhs = process_rhs_conditions(lhs, rhs, evaluation, condition)
    rule = Rule(lhs, rhs)
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation):
            continue
        count += 1
        defs.add_nvalue(tag, rule)
    return count > 0


def process_assign_side_effects(
    self, lhs, rhs, focus, evaluation, tags=None, upset=False
) -> bool:
    """
    Process special cases, performing certain side effects, like modifying
    the value of internal variables that are not stored as rules.

    The function returns a a bool value.
    If lhs is one of the special cases, then the bool variable is
    True, meaning that the `Protected` attribute should not be taken into account.
    Otherwise, the value is False.
    """

    lhs_name = lhs.get_name()
    if lhs_name == "System`$RecursionLimit":
        process_assign_recursion_limit(lhs, rhs, evaluation)
    elif lhs_name in ("System`$Line", "System`$HistoryLength"):
        process_assign_line_number_and_history_length(
            self, lhs, rhs, evaluation, tags, upset
        )
    elif lhs_name == "System`$IterationLimit":
        process_assign_iteration_limit(lhs, rhs, evaluation)
    elif lhs_name == "System`$ModuleNumber":
        process_assign_module_number(lhs, rhs, evaluation)
    elif lhs_name == "System`$MinPrecision":
        process_assign_minprecision(self, lhs, rhs, evaluation, tags, upset)
    elif lhs_name == "System`$MaxPrecision":
        process_assign_maxprecision(self, lhs, rhs, evaluation, tags, upset)
    else:
        return False
    return True


def process_assign_part(self, lhs, rhs, evaluation, tags, upset):
    """
    Special case `A[[i,j,...]]=....`
    """
    defs = evaluation.definitions
    if len(lhs.elements) < 1:
        evaluation.message(self.get_name(), "setp", lhs)
        return False
    symbol = lhs.elements[0]
    name = symbol.get_name()
    if not name:
        evaluation.message(self.get_name(), "setps", symbol)
        return False
    if is_protected(name, defs):
        evaluation.message(self.get_name(), "wrsym", symbol)
        return False
    rule = defs.get_ownvalue(name)
    if rule is None:
        evaluation.message(self.get_name(), "noval", symbol)
        return False
    indices = lhs.elements[1:]
    return walk_parts([rule.replace], indices, evaluation, rhs)


def process_assign_random_state(self, lhs, rhs, evaluation, tags, upset):
    # TODO: allow setting of legal random states!
    # (but consider pickle's insecurity!)
    evaluation.message("$RandomState", "rndst", rhs)
    raise AssignmentException(lhs, None)


def process_assign_recursion_limit(lhs, rhs, evaluation):
    """
    Set ownvalue for the $RecursionLimit symbol.
    """
    rhs_int_value = rhs.get_int_value()
    # if (not rhs_int_value or rhs_int_value < 20) and not
    # rhs.get_name() == 'System`Infinity':
    if (
        not rhs_int_value or rhs_int_value < 20 or rhs_int_value > MAX_RECURSION_DEPTH
    ):  # nopep8

        evaluation.message("$RecursionLimit", "limset", rhs)
        raise AssignmentException(lhs, None)
    try:
        set_python_recursion_limit(rhs_int_value)
    except OverflowError:
        # TODO: Message
        raise AssignmentException(lhs, None)
    return False


def process_rhs_conditions(lhs, rhs, evaluation, condition=None):
    """
    lhs = Condition[rhs, test] -> Condition[lhs, test]  = rhs

    This function is necesary as a temporal patch for a bug
    in the pattern matching / replacement code.

    In WMA,

    ``f[4]/.(f[x_]:> (p[x]/;x>0))``

    shold return

    ``p[4]``

    while ``f[-4]/.(f[x_]:> (p[x]/;x>0))``
    would result in ``f[-4]``

    In Mathics, the first case results in
    ``p[4]/; 4>0``
    while the second,
    ``p[-4]/; -4>0``

    This should be handled in the apply method of the BaseRule class.
    """
    # To Handle `OptionValue` in `Condition`
    rulopc = build_rulopc(lhs.get_head())
    rhs_name = rhs.get_head_name()
    while rhs_name == "System`Condition":
        if len(rhs.elements) != 2:
            evaluation.message_args("Condition", len(rhs.elements), 2)
            raise AssignmentException(lhs, None)
        lhs = Expression(
            SymbolCondition,
            lhs,
            rhs.elements[1].do_apply_rules([rulopc], evaluation)[0],
        )
        rhs = rhs.elements[0]
        rhs_name = rhs.get_head_name()

    # Now, let's add the conditions on the LHS
    if condition:
        lhs = Expression(
            SymbolCondition,
            lhs,
            condition.elements[1].do_apply_rules([rulopc], evaluation)[0],
        )
    return lhs, rhs


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
            return find_tag(focus.elements[0])
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


def find_tag(focus):
    focus = find_focus(focus)
    if focus is None:
        return None
    return focus.get_lookup_name()


def process_tags_and_upset(tags, upset, self, lhs, evaluation, focus=None):
    if focus is None:
        allow_custom = True
        focus = lhs
    else:
        allow_custom = False

    # Ensures that focus is the actual focus of the expression.
    focus = find_focus(focus)
    if (
        isinstance(focus, Expression)
        and focus.head not in NOT_EVALUATE_ELEMENTS_IN_ASSIGNMENTS
    ):
        focus = focus.evaluate_elements(evaluation)

    if tags is None and not upset:
        name = find_tag(focus)
        if name == "":
            evaluation.message(self.get_name(), "setraw", focus)
            raise AssignmentException(lhs, None)
        tags = [] if name is None else [name]
    elif upset:
        if allow_custom:
            tags = []
            if isinstance(focus, Atom):
                evaluation.message(self.get_name(), "normal")
                raise AssignmentException(lhs, None)
            for element in focus.elements:
                name = find_tag(element)
                if name != "" and name is not None:
                    tags.append(name)
        else:
            name = find_tag(focus)
            tags = [] if name is None else [name]
    else:
        if allow_custom:
            allowed_names = [find_tag(focus)]
            for element in focus.get_elements():
                element_tag = find_tag(element)
                if element_tag is not None and element_tag != "":
                    allowed_names.append(element_tag)
        else:
            name = find_tag(focus)
            allowed_names = [] if name is None else [name]
        for name in tags:
            if name not in allowed_names:
                evaluation.message(self.get_name(), "tagnfd", Symbol(name))
                raise AssignmentException(lhs, None)
    if len(tags) == 0:
        evaluation.message(self.get_name(), "nosym", focus)
        raise AssignmentException(lhs, None)
    return tags, focus


# Below is a mapping from a string Symbol name into an assignment function
ASSIGNMENT_FUNCTION_MAP = {
    "System`$Context": process_assign_context,
    "System`$ContextPath": process_assign_context_path,
    "System`$RandomState": process_assign_random_state,
    "System`Attributes": process_assign_attributes,
    "System`Default": process_assign_default,
    "System`DefaultValues": process_assign_definition_values,
    "System`DownValues": process_assign_definition_values,
    "System`Format": process_assign_format,
    "System`List": process_assign_list,
    "System`MakeBoxes": process_assign_makeboxes,
    "System`MessageName": process_assign_messagename,
    "System`Messages": process_assign_definition_values,
    "System`N": process_assign_n,
    "System`NValues": process_assign_definition_values,
    "System`NumericQ": process_assign_numericq,
    "System`Options": process_assign_options,
    "System`OwnValues": process_assign_definition_values,
    "System`Part": process_assign_part,
    "System`SubValues": process_assign_definition_values,
    "System`UpValues": process_assign_definition_values,
}
