# -*- coding: utf-8 -*-
# pylint: disable-msg=too-many-arguments

"""
evaluation routines for Set and SetDelayed, and Builtin functions
found in module mathics.builtin.assigments.assignment
"""

from functools import reduce
from typing import List, Optional, Tuple

from mathics.core.assignment import (
    build_rulopc,
    get_symbol_list,
    is_protected,
    normalize_lhs,
    rejected_because_protected,
    unroll_conditions,
    unroll_patterns,
)
from mathics.core.atoms import Atom, Integer, Integer1
from mathics.core.attributes import A_LOCKED, attribute_string_to_number
from mathics.core.builtin import Builtin
from mathics.core.element import BaseElement
from mathics.core.evaluation import (
    MAX_RECURSION_DEPTH,
    Evaluation,
    set_python_recursion_limit,
)
from mathics.core.expression import Expression, SymbolDefault
from mathics.core.rules import Rule
from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolMaxPrecision,
    SymbolMinPrecision,
    SymbolN,
    SymbolTrue,
    valid_context_name,
)
from mathics.core.systemsymbols import SymbolCondition, SymbolMachinePrecision
from mathics.eval.list.eol import eval_Part


class AssignmentException(Exception):
    """Exception raised when Assignment fails"""

    def __init__(self, lhs, rhs) -> None:
        super().__init__(f" {rhs} cannot be assigned to {lhs}")
        self.lhs = lhs
        self.rhs = rhs


def eval_assign(
    self,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: Optional[list] = None,
    upset: bool = False,
) -> bool:
    """
    Method that implements the assignment.

    Parameters
    ----------
    lhs : BaseElement
        The expression to be assigned.
    rhs : BaseElement
        the RHS.
    evaluation : Evaluation
        The evaluation object.
    tags : Optional[list], optional
        The list of symbol names for which the rule must be associated.
        The default is None.
    upset : bool, optional
        If true, the assignment is to an UpsetValue. The default is False.

    Returns
    -------
    bool:
        True if the assignment was successful.

    """
    lhs, lookup_name = normalize_lhs(lhs, evaluation)
    try:
        # Using a builtin name, find which assignment procedure to perform,
        # and then call that function.
        assignment_func = ASSIGNMENT_FUNCTION_MAP.get(lookup_name, None)
        if assignment_func:
            return assignment_func(self, lhs, rhs, evaluation, tags, upset)

        return eval_assign_store_rules_by_tag(self, lhs, rhs, evaluation, tags, upset)
    except AssignmentException:
        return False


def eval_assign_attributes(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Process the case where lhs is of the form
    `Attribute[symbol]`

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

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

    def reduce_attributes_from_list(x_att: int, y_att: str) -> int:
        try:
            return x_att | attribute_string_to_number[y_att]
        except KeyError:
            evaluation.message("SetAttributes", "unknowattr", y_att)
            return x_att

    attributes = reduce(
        reduce_attributes_from_list,
        attributes_list,
        0,
    )

    evaluation.definitions.set_attributes(tag, attributes)

    return True


def eval_assign_context(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: List,
    upset: bool,
) -> bool:
    """
    Process the case where lhs is ``$Context``

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
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


def eval_assign_context_path(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Assignment to the `$ContextPath` variable.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    lhs_name = lhs.get_name()
    curr_context = evaluation.definitions.get_current_context()
    context_path = [s.get_string_value() for s in rhs.get_elements()]
    context_path = [
        s if (s is None or s[0] != "`") else curr_context[:-1] + s for s in context_path
    ]
    if rhs.has_form("List", None) and all(valid_context_name(s) for s in context_path):
        evaluation.definitions.set_context_path(context_path)
        return True

    evaluation.message(lhs_name, "cxlist", rhs)
    raise AssignmentException(lhs, None)


def eval_assign_default(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Process the assignment of ``DefaultValues`` of a symbol.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    count = 0
    defs = evaluation.definitions

    if len(lhs.elements) not in (1, 2, 3):
        evaluation.message_args(SymbolDefault, len(lhs.elements), 1, 2, 3)
        raise AssignmentException(lhs, None)
    focus = lhs.elements[0]
    tags = process_tags_and_upset_dont_allow_custom(
        tags, upset, self, lhs, focus, evaluation
    )
    lhs, rhs = process_rhs_conditions(lhs, rhs, condition, evaluation)
    rule = Rule(lhs, rhs)
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation):
            continue
        count += 1
        defs.add_default(tag, rule)
    return count > 0


def eval_assign_definition_values(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """

    Implements the assignment to the Definitions attribute of a symbol.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    name = lhs.get_head_name()
    tag = find_tag_and_check(lhs, tags, evaluation)
    rules = rhs.get_rules_list()
    if rules is None:
        evaluation.message(name, "vrule", lhs, rhs)
        raise AssignmentException(lhs, None)
    evaluation.definitions.set_values(tag, name, rules)
    return True


def eval_assign_format(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """

    Implements the assignment to Format

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
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
    tags = process_tags_and_upset_dont_allow_custom(
        tags, upset, self, lhs, focus, evaluation
    )
    lhs, rhs = process_rhs_conditions(lhs, rhs, condition, evaluation)
    rule = Rule(lhs, rhs)
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation):
            continue
        count += 1
        defs.add_format(tag, rule, form_name)
    return count > 0


def eval_assign_iteration_limit(
    lhs: BaseElement, rhs: BaseElement, evaluation: Evaluation
) -> bool:
    """
    Set ownvalue for the $IterationLimit symbol.
    """

    rhs_int_value = rhs.get_int_value()
    if (
        not rhs_int_value or rhs_int_value < 20
    ) and not rhs.get_name() == "System`Infinity":
        evaluation.message("$IterationLimit", "limset", rhs)
        raise AssignmentException(lhs, None)
    return True


def eval_assign_line_number_and_history_length(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Set ownvalue for the $Line and $HistoryLength symbols.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """

    lhs_name = lhs.get_name()
    rhs_int_value = rhs.get_int_value()
    if rhs_int_value is None or rhs_int_value < 0:
        evaluation.message(lhs_name, "intnn", rhs)
        raise AssignmentException(lhs, None)
    return False


def eval_assign_list(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Implement the assignment to a List expression.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    if not (
        rhs.get_head_name() == "System`List" and len(lhs.elements) == len(rhs.elements)
    ):  # nopep8
        evaluation.message(self.get_name(), "shape", lhs, rhs)
        return False
    result = True
    for left, right in zip(lhs.elements, rhs.elements):
        if not eval_assign(self, left, right, evaluation):
            result = False
    return result


def eval_assign_makeboxes(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Implement the assignment to a MakeBoxes expression.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    # FIXME: the below is a big hack.
    # Currently MakeBoxes boxing is implemented as a bunch of rules.
    # See mathics.core.builtin contribute().
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


def eval_assign_minprecision(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Implement the assignment to the `$MinPrecision` symbol.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    lhs_name = lhs.get_name()
    rhs_int_value = rhs.get_int_value()
    # $MinPrecision = Infinity is not allowed
    if rhs_int_value is not None and rhs_int_value >= 0:
        max_prec = evaluation.definitions.get_config_value("$MaxPrecision")
        if max_prec is not None and max_prec < rhs_int_value:
            evaluation.message("$MinPrecision", "preccon", SymbolMinPrecision)
            raise AssignmentException(lhs, None)
        return False

    evaluation.message(lhs_name, "precset", lhs, rhs)
    raise AssignmentException(lhs, None)


def eval_assign_maxprecision(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Implement the assignment to the `$MaxPrecision` symbol.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    lhs_name = lhs.get_name()
    rhs_int_value = rhs.get_int_value()
    if rhs.has_form("DirectedInfinity", 1) and rhs.elements[0].get_int_value() == 1:
        return False
    if rhs_int_value is not None and rhs_int_value > 0:
        min_prec = evaluation.definitions.get_config_value("$MinPrecision")
        if min_prec is not None and rhs_int_value < min_prec:
            evaluation.message("$MaxPrecision", "preccon", SymbolMaxPrecision)
            raise AssignmentException(lhs, None)
        return False

    evaluation.message(lhs_name, "precset", lhs, rhs)
    raise AssignmentException(lhs, None)


def eval_assign_messagename(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """

    Implement the assignment to `Message[...]` expressions.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    count = 0
    defs = evaluation.definitions
    if len(lhs.elements) != 2:
        evaluation.message_args("MessageName", len(lhs.elements), 2)
        raise AssignmentException(lhs, None)
    focus = lhs.elements[0]
    tags = process_tags_and_upset_dont_allow_custom(
        tags, upset, self, lhs, focus, evaluation
    )
    lhs, rhs = process_rhs_conditions(lhs, rhs, condition, evaluation)
    rule = Rule(lhs, rhs)
    for tag in tags:
        # Messages can be assigned even if the symbol is protected...
        # if rejected_because_protected(self, lhs, tag, evaluation):
        #    continue
        count += 1
        defs.add_message(tag, rule)
    return count > 0


def eval_assign_module_number(
    lhs: BaseElement, rhs: BaseElement, evaluation: Evaluation
) -> bool:
    """
    Set ownvalue for the $ModuleNumber symbol.
    """
    rhs_int_value = rhs.get_int_value()
    if not rhs_int_value or rhs_int_value <= 0:
        evaluation.message("$ModuleNumber", "set", rhs)
        raise AssignmentException(lhs, None)
    return False


def eval_assign_options(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Implement the assignment to `OptionValues`.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
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


def eval_assign_numericq(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Assign to expressions of the form `NumericQ[expr_]`.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    # lhs, condition = unroll_conditions(lhs)
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
        try:
            definition = evaluation.definitions.get_definition(name)
            definition.is_numeric = rhs is SymbolTrue
        except KeyError:
            pass
        return True

    evaluation.message("NumericQ", "set", lhs, rhs)
    raise AssignmentException(lhs, rhs)


def eval_assign_n(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Assign to expressions of the form `N[expr_]`.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    defs = evaluation.definitions
    # If we try to set `N=4`, (issue #210) just deal with it as with a generic expression:
    if lhs is SymbolN:
        return eval_assign_store_rules_by_tag(self, lhs, rhs, evaluation, tags, upset)

    if len(lhs.elements) not in (1, 2):
        evaluation.message_args("N", len(lhs.elements), 1, 2)
        raise AssignmentException(lhs, None)
    if len(lhs.elements) == 1:
        nprec = SymbolMachinePrecision
    else:
        nprec = lhs.elements[1]
    focus = lhs.elements[0]
    lhs = Expression(SymbolN, focus, nprec)
    tags = process_tags_and_upset_dont_allow_custom(
        tags, upset, self, lhs, focus, evaluation
    )
    count = 0
    lhs, rhs = process_rhs_conditions(lhs, rhs, condition, evaluation)
    rule = Rule(lhs, rhs)
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation):
            continue
        count += 1
        defs.add_nvalue(tag, rule)
    return count > 0


def eval_assign_other(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: Optional[list] = None,
    upset: bool = False,
) -> Tuple[bool, list]:
    """
    Process special cases, performing certain side effects, like modifying
    the value of internal variables that are not stored as rules.

    The function returns a tuple of a bool value and a list of tags.
    If lhs is one of the special cases, then the bool variable is
    True, meaning that the `Protected` attribute should not be taken
    into account.
    Otherwise, the value is False.


    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    tags, _ = process_tags_and_upset_allow_custom(
        tags, upset, self, lhs, rhs, evaluation
    )
    lhs_name = lhs.get_name()
    if lhs_name == "System`$RecursionLimit":
        eval_assign_recursion_limit(lhs, rhs, evaluation)
    elif lhs_name in ("System`$Line", "System`$HistoryLength"):
        eval_assign_line_number_and_history_length(
            self, lhs, rhs, evaluation, tags, upset
        )
    elif lhs_name == "System`$IterationLimit":
        eval_assign_iteration_limit(lhs, rhs, evaluation)
    elif lhs_name == "System`$ModuleNumber":
        eval_assign_module_number(lhs, rhs, evaluation)
    elif lhs_name == "System`$MinPrecision":
        eval_assign_minprecision(self, lhs, rhs, evaluation, tags, upset)
    elif lhs_name == "System`$MaxPrecision":
        eval_assign_maxprecision(self, lhs, rhs, evaluation, tags, upset)
    else:
        return False, tags
    return True, tags


def eval_assign_part(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: Optional[List],
    upset: bool,
):
    """
    Special case `A[[i,j,...]]=....`

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

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
    return eval_Part([rule.replace], indices, evaluation, rhs)


def eval_assign_random_state(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
    tags: list,
    upset: bool,
) -> bool:
    """
    Assign to expressions of the form `$RandomState`.

    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    # By a design decision, Mathics3 does not allow to
    # modify this variable.
    # To change this behaviour we should
    #
    # * Base `get_random_state` and `set_random_state` in a
    #   safer serialization mechanism. The branch
    #   origin/setteable_randomstate has a proposal for this.
    # * Modify the behaviour of
    #   `mathics.builtin.numbers.randomnumbers.RandomEnvBase`
    # * Uncomment the following lines:
    #
    # from call here mathics.builtin.numbers.randomnumbers import (
    # set_random_state,
    # )
    # set_random_state(rhs.get_int_value())
    #
    evaluation.message("$RandomState", "rndst", rhs)
    return False


def eval_assign_recursion_limit(lhs, rhs, evaluation):
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
        # TODO: Show a Message
        raise AssignmentException(lhs, None)
    return True


def eval_assign_store_rules_by_tag(
    self, lhs, rhs, evaluation, tags, upset=False
) -> bool:
    """
    This is the default assignment. Stores a rule of the form lhs->rhs
    as a value associated to each symbol listed in tags.
    For special cases, such like conditions or patterns in the lhs,
    lhs and rhs are rewritten in a normal form, where
    conditions are associated to the lhs.


    Parameters
    ----------
    self : Builtin
        The builtin assignment operator
    lhs : BaseElement
        The pattern of the rule to be assigned.
    rhs : BaseElement
        the expression representing the replacement.
    evaluation : Evaluation
        DESCRIPTION.
    tags : list
        the list of symbols to be associated to the rule.
    upset : bool
        `True` if the rule is an Up value.

    Raises
    ------
    AssignmentException

    Returns
    -------
    bool
        True if the assignment was successful.

    """
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    defs = evaluation.definitions
    ignore_protection, tags = eval_assign_other(self, lhs, rhs, evaluation, tags, upset)
    # In WMA, this does not happens. However, if we remove this,
    # some combinatorica tests fail.
    # Also, should not be at the beginning?
    lhs, rhs = process_rhs_conditions(lhs, rhs, condition, evaluation)
    count = 0
    rule = Rule(lhs, rhs)
    position = "up" if upset else None
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation, ignore_protection):
            continue
        count += 1
        defs.add_rule(tag, rule, position=position)
    return count > 0


def find_tag_and_check(
    lhs: BaseElement, tags: Optional[List[str]], evaluation: Evaluation
) -> str:
    """
    Deduce the `tag` from the lhs. If a list of `tags` is provided,
    it must coincide with `[tag]`.

    Parameters
    ----------
    lhs : BaseElement
        The LHS of the assignment expression.
    tags : Optional[List[str]]
        A list of tags.
    evaluation : Evaluation
        The evaluation object.

    Raises
    ------
    AssignmentException

    Returns
    -------
    str
        the tag associated to the expression.

    """
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


def process_rhs_conditions(
    lhs: BaseElement, rhs: BaseElement, condition: Expression, evaluation: Evaluation
) -> Tuple[BaseElement, Optional[BaseElement]]:
    """
    lhs = Condition[rhs, test] -> Condition[lhs, test]  = rhs
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


def process_tags_and_upset_dont_allow_custom(
    tags: Optional[list],
    upset: bool,
    self: Builtin,
    lhs: BaseElement,
    focus: BaseElement,
    evaluation: Evaluation,
) -> list:
    """
    If `upset` is `True`,  collect a list of tag candidates from the elements of
    the lhs.
    If `upset` is `False`, and `tags` is given, check if the elements
    in `tags` are all names of symbols in the `lhs` elements. If `tags` is
    `None`, the list of tags contains just the `lookup_name` of the LHS.

    Parameters
    ----------
    tags : Optional[List]
        The list of symbols to which the rule must be associated.
    upset : bool
        If `True`, assign as an UpValue.
    self : Builtin
        The Assignment operator object that started the call.
    lhs : BaseElement
        The LHS of the assignment.
    rhs : BaseElement
        The RHS of the assignment.
    evaluation : Evaluation
        The evaluation object.

    Raises
    ------
    AssignmentException

    Returns
    -------
    tags: list
        the list of allowed tags.

    """
    if isinstance(focus, Expression):
        focus = focus.evaluate_elements(evaluation)
    name = lhs.get_head_name()
    if upset:
        tags = [focus.get_lookup_name()]
    elif tags is None:
        name = focus.get_lookup_name()
        if not name:
            evaluation.message(self.get_name(), "setraw", focus)
            raise AssignmentException(lhs, None)
        tags = [name]
    else:
        allowed_names = [focus.get_lookup_name()]
        for name in tags:
            if name not in allowed_names:
                evaluation.message(self.get_name(), "tagnfd", Symbol(name))
                raise AssignmentException(lhs, None)
    return tags


def process_tags_and_upset_allow_custom(
    tags: Optional[List],
    upset: bool,
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
) -> Tuple[list, BaseElement]:
    """
    If `upset` is `True`,  collect a list of tag candidates from the elements of
    the lhs.
    If `upset` is `False`, and `tags` is given, check if the elements
    in `tags` are all names of symbols in the `lhs` elements. If `tags` is
    `None`, the list of tags contains just the `lookup_name` of the LHS.

    Parameters
    ----------
    tags : Optional[List]
        The list of symbols to which the rule must be associated.
    upset : bool
        If `True`, assign as an UpValue.
    self : Builtin
        The Assignment operator object that started the call.
    lhs : BaseElement
        The LHS of the assignment.
    rhs : BaseElement
        The RHS of the assignment.
    evaluation : Evaluation
        The evaluation object.

    Raises
    ------
    AssignmentException.

    Returns
    -------
    (tags, focus,): Tuple[list, BaseElement]
        tags: the list of symbols to which the rule must be associated.
        focus: the lhs

    """
    name = lhs.get_head_name()
    focus = lhs
    if isinstance(focus, Expression):
        focus = focus.evaluate_elements(evaluation)

    if upset:
        tags = []
        if isinstance(focus, Atom):
            symbol_name = self.get_name()
            evaluation.message(
                symbol_name,
                "normal",
                Integer1,
                Expression(Symbol(symbol_name), lhs, rhs),
            )
            raise AssignmentException(lhs, None)
        for element in focus.get_elements():
            name = element.get_lookup_name()
            tags.append(name)
        return tags, focus

    if tags is None:
        name = focus.get_lookup_name()
        if not name:
            evaluation.message(self.get_name(), "setraw", focus)
            raise AssignmentException(lhs, None)
        tags = [name]
    else:
        allowed_names = [focus.get_lookup_name()]
        for element in focus.get_elements():
            if not isinstance(element, Symbol) and element.get_head_name() in (
                "System`HoldPattern",
            ):
                element = element.get_element(0)
            if not isinstance(element, Symbol) and element.get_head_name() in (
                "System`Pattern",
            ):
                element = element.get_element(1)
            if not isinstance(element, Symbol) and element.get_head_name() in (
                "System`Blank",
                "System`BlankSequence",
                "System`BlankNullSequence",
            ):
                if len(element.get_elements()) == 1:
                    element = element.get_element(0)

            allowed_names.append(element.get_lookup_name())
        for name in tags:
            if name not in allowed_names:
                evaluation.message(self.get_name(), "tagnfd", Symbol(name))
                raise AssignmentException(lhs, None)

    return tags, focus


# Below is a mapping from Symbol name (as a string) into an assignment eval function.
ASSIGNMENT_FUNCTION_MAP = {
    "System`$Context": eval_assign_context,
    "System`$ContextPath": eval_assign_context_path,
    "System`$RandomState": eval_assign_random_state,
    "System`Attributes": eval_assign_attributes,
    "System`Default": eval_assign_default,
    "System`DefaultValues": eval_assign_definition_values,
    "System`DownValues": eval_assign_definition_values,
    "System`Format": eval_assign_format,
    "System`List": eval_assign_list,
    "System`MakeBoxes": eval_assign_makeboxes,
    "System`MessageName": eval_assign_messagename,
    "System`Messages": eval_assign_definition_values,
    "System`N": eval_assign_n,
    "System`NValues": eval_assign_definition_values,
    "System`NumericQ": eval_assign_numericq,
    "System`Options": eval_assign_options,
    "System`OwnValues": eval_assign_definition_values,
    "System`Part": eval_assign_part,
    "System`SubValues": eval_assign_definition_values,
    "System`UpValues": eval_assign_definition_values,
}
