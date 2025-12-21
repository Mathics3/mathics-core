# -*- coding: utf-8 -*-
# pylint: disable-msg=too-many-arguments

"""
evaluation routines for Set and SetDelayed, and Builtin functions
found in module mathics.builtin.assignments.assignment
"""

from functools import reduce
from typing import List, Optional, Tuple

from mathics.core.assignment import (
    get_symbol_list,
    is_protected,
    pop_reference_head,
    rejected_because_protected,
)
from mathics.core.atoms import Integer, Integer1
from mathics.core.attributes import A_LOCKED, attribute_string_to_number
from mathics.core.builtin import Builtin
from mathics.core.element import BaseElement
from mathics.core.evaluation import (
    MAX_RECURSION_DEPTH,
    Evaluation,
    set_python_recursion_limit,
)
from mathics.core.expression import Expression
from mathics.core.rules import Rule
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolFalse,
    SymbolMaxPrecision,
    SymbolMinPrecision,
    SymbolN,
    SymbolTrue,
    valid_context_name,
)
from mathics.core.systemsymbols import (
    SymbolCondition,
    SymbolDefault,
    SymbolHoldPattern,
    SymbolMachinePrecision,
    SymbolPatternTest,
)
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
    # An expression can be wrapped inside structures like `Condition[...]`
    # or HoldPattern[...]. The `lhs_reference` is the head of the expression once
    # we strip out all these wrappings.
    lhs_reference_expr = get_reference_expression(lhs)
    lhs_reference = (
        lhs_reference_expr
        if isinstance(lhs_reference_expr, Symbol)
        else lhs_reference_expr.get_head()
    )
    if isinstance(lhs_reference_expr, Symbol):
        if upset:
            evaluation.message(self.get_name(), "nosym", lhs)
        if tags and lhs_reference_expr.get_name() not in tags:
            evaluation.message("tagnf", lhs_reference_expr, lhs)

        try:
            return eval_assign_to_symbol(self, lhs, lhs_reference_expr, rhs, evaluation)
        except AssignmentException:
            return False

    try:
        # Handle special cases using the lookup name associated to the lhs_reference
        lookup_name = lhs_reference_expr.get_lookup_name()
        assignment_func = ASSIGNMENT_FUNCTION_MAP.get(lookup_name, None)
        if assignment_func:
            return assignment_func(
                self, lhs, lhs_reference, rhs, evaluation, tags, upset
            )
        if isinstance(lhs, Expression) and not lhs.has_form("System`HoldPattern", 1):
            lhs = lhs.evaluate_elements(evaluation)
            lhs_reference_expr = get_reference_expression(lhs)
            lhs_reference = (
                lhs_reference_expr
                if isinstance(lhs_reference_expr, Symbol)
                else lhs_reference_expr.get_head()
            )

        return eval_assign_store_rules_by_tag(
            self, lhs, lhs_reference, rhs, evaluation, tags, upset
        )
    except AssignmentException:
        return False


def eval_assign_attributes(
    self: Builtin,
    lhs: BaseElement,
    lhs_reference: BaseElement,
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
    lhs_reference: BaseElement
        The head of the expression after `Condition`,
        `PatternTest` and `HoldPattern` wrappers are
        stripped out.
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
    # UpSet and TagSet for this symbol are handled in
    # the standard way. The same if the expression is wrapped:
    if lhs.get_head() is not lhs_reference:
        return eval_assign_store_rules_by_tag(self, lhs, lhs_reference, rhs, evaluation)

    name = lhs_reference.get_head_name()
    if len(lhs.elements) != 1:
        evaluation.message_args(name, len(lhs.elements), 1)
        raise AssignmentException(lhs, rhs)

    tag_expr = get_reference_expression(lhs.elements[0])
    tag = tag_expr.get_lookup_name()
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
    lhs_reference: BaseElement,
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
    lhs_reference: BaseElement
        The lhs expression stripped from conditions and
        wrappers.
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
    # UpSet and TagSet for this symbol are handled in
    # the standard way. The same if the expression is wrapped:
    if lhs.get_head() is not lhs_reference:
        return eval_assign_store_rules_by_tag(self, lhs, lhs_reference, rhs, evaluation)

    count = 0
    defs = evaluation.definitions

    if len(lhs.elements) not in (1, 2, 3):
        evaluation.message_args(SymbolDefault, len(lhs.elements), 1, 2, 3)
        raise AssignmentException(lhs, None)
    lhs_reference = get_reference_expression(lhs.elements[0])
    lhs_reference = (
        lhs_reference if isinstance(lhs_reference, Symbol) else lhs_reference.get_head()
    )
    tags = process_tags_and_upset_dont_allow_custom(
        tags, upset, self, lhs, lhs_reference, evaluation
    )
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
    lhs_reference: BaseElement,
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
    if lhs.get_head() is not lhs_reference:
        return eval_assign_store_rules_by_tag(self, lhs, lhs_reference, rhs, evaluation)

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
    lhs_reference: BaseElement,
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
    lhs = pop_reference_head(lhs, lhs_reference)
    lhs = lhs.evaluate_elements(evaluation)
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
    lhs = lhs.elements[0]
    lhs_reference = get_reference_expression(lhs)
    lhs_reference = (
        lhs_reference.get_head()
        if not isinstance(lhs_reference, Symbol)
        else lhs_reference
    )
    tags = process_tags_and_upset_dont_allow_custom(
        tags, upset, self, lhs, lhs_reference, evaluation
    )
    rule = Rule(lhs, rhs)
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation):
            continue
        count += 1
        defs.add_format(tag, rule, form_name)
    return count > 0


def eval_assign_iteration_limit(
    self, lhs: BaseElement, rhs: BaseElement, evaluation: Evaluation
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
    lhs_reference: BaseElement,
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
    lhs_reference: BaseElement,
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
    definitions.add_rule("System`MakeBoxes", makeboxes_rule, "downvalues")
    #    makeboxes_defs = evaluation.definitions.builtin["System`MakeBoxes"]
    #    makeboxes_defs.add_rule(makeboxes_rule)
    return True


def eval_assign_minprecision(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
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
    lhs_reference: BaseElement,
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
    if lhs.get_head() is not lhs_reference:
        return eval_assign_store_rules_by_tag(self, lhs, lhs_reference, rhs, evaluation)

    lhs = pop_reference_head(lhs, lhs_reference)

    count = 0
    defs = evaluation.definitions
    if len(lhs.elements) != 2:
        evaluation.message_args("MessageName", len(lhs.elements), 2)
        raise AssignmentException(lhs, None)
    lhs_reference = lhs.elements[0]
    tags = process_tags_and_upset_dont_allow_custom(
        tags, upset, self, lhs, lhs_reference, evaluation
    )
    rule = Rule(lhs, rhs)
    for tag in tags:
        # Messages can be assigned even if the symbol is protected...
        # if rejected_because_protected(self, lhs, tag, evaluation):
        #    continue
        count += 1
        defs.add_message(tag, rule)
    return count > 0


def eval_assign_module_number(
    self, lhs: BaseElement, rhs: BaseElement, evaluation: Evaluation
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
    lhs_reference: BaseElement,
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
    if lhs.get_head() is not lhs_reference:
        return eval_assign_store_rules_by_tag(self, lhs, lhs_reference, rhs, evaluation)

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
    lhs_reference: BaseElement,
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
    lhs = pop_reference_head(lhs, lhs_reference)

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
    lhs_reference: BaseElement,
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
    lhs_reference: BaseElement
        Expression of the form N[___]
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
    if isinstance(lhs, Expression):
        lhs = lhs.evaluate_elements(evaluation)

    lhs = pop_reference_head(lhs, lhs_reference)
    defs = evaluation.definitions

    if len(lhs.elements) not in (1, 2):
        evaluation.message_args("N", len(lhs.elements), 1, 2)
        raise AssignmentException(lhs, None)

    if len(lhs.elements) == 1:
        nprec = SymbolMachinePrecision
        lhs = Expression(SymbolN, lhs.elements[0], nprec)
    else:
        nprec = lhs.elements[1]

    lhs_reference = get_reference_expression(lhs.elements[0])

    tags = process_tags_and_upset_dont_allow_custom(
        tags, upset, self, lhs, lhs_reference, evaluation
    )
    count = 0
    rule = Rule(lhs, rhs)
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation):
            continue
        count += 1
        defs.add_nvalue(tag, rule)
    return count > 0


def eval_assign_part(
    self: Builtin,
    lhs: BaseElement,
    lhs_reference: BaseElement,
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
    try:
        rule = defs.get_ownvalue(name)
    except ValueError:
        evaluation.message(self.get_name(), "noval", symbol)
        return False
    indices = lhs.elements[1:]
    return eval_Part([rule], indices, evaluation, rhs)


def eval_assign_random_state(
    self: Builtin,
    lhs: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
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


def eval_assign_recursion_limit(self, lhs, rhs, evaluation):
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
    self, lhs, lhs_reference, rhs, evaluation, tags, upset=False
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
    defs = evaluation.definitions
    tags, lhs_reference_expr = process_tags_and_upset_allow_custom(
        tags, upset, self, lhs, rhs, evaluation
    )
    # In WMA, this does not happens. However, if we remove this,
    # some combinatorica tests fail.
    # Also, should not be at the beginning?
    count = 0
    rule = Rule(lhs, rhs)
    position = "upvalues" if upset else None
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation, False):
            continue
        count += 1
        defs.add_rule(tag, rule, position=position)
    return count > 0


def eval_assign_to_symbol(
    self,
    lhs: BaseElement,
    lhs_reference: BaseElement,
    rhs: BaseElement,
    evaluation: Evaluation,
) -> bool:
    """
    self:
        The builtin class.
    lhs : BaseElement
        The pattern of the rule to be included.
    lhs_reference:
        The symbol to be assigned
    rhs : BaseElement.
        the RHS.
    evaluation : Evaluation
        The evaluation object.

    """
    # This is how WMA works: if the LHS is a symbol, do the special
    # evaluation. So, HoldPattern[$RecursionLimit]:=10 set the
    # ownvalue of $RecursionLimit to 10, but in evaluations, $RecursionLimit
    # is not modified.
    special_fn = EVAL_ASSIGN_SPECIAL_SYMBOLS.get(lhs.get_name(), None)
    if special_fn:
        ignore_protection = True
        special_fn(self, lhs, rhs, evaluation)
    else:
        ignore_protection = False

    tag = lhs_reference.get_name()
    if rejected_because_protected(self, lhs, tag, evaluation, ignore_protection):
        return False
    evaluation.definitions.add_rule(tag, Rule(lhs, rhs), position="ownvalues")
    return True


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


def get_lookup_reference_name(expr: BaseElement) -> str:
    """
    Find the lookup name of the reference expression associated to
    `expr`, or None if there is no such a reference.

    In general, the lookup reference name coincides with the lookup_name
    of the expression. However, there are some exceptions:

    * Expressions with heads `HoldPattern`, Condition`, or `PatternTest`
      are not considered *reference* expressions. The reference expression
      is the reference expression of its first element.
    * (named) `Pattern` expressions takes its lookup_reference_name from the
      pattern their hold.
    * `Verbatim` expressions pick the lookup_reference_name from
       the lookup_name of the expression they hold.
    * Blanks pick the lookup_reference_name from the pattern head
      (its unique element if they has one). If the Blank expression does not
      have elements (generic blank) then there is no lookup_reference_name,
      and returns an empty string.
    """
    expr = get_reference_expression(expr)
    if expr.has_form("System`Pattern", 2):
        return get_lookup_reference_name(expr.elements[1])
    if expr.has_form("System`Verbatim", 1):
        # For Verbatim pick the lookup name directly from the expression.
        return expr.elements[0].get_lookup_name()
    if expr.has_form(
        ("System`Blank", "System`BlankSequence", "System`BlankNullSequence"), None
    ):
        if len(expr.elements) == 1:
            return get_lookup_reference_name(expr.elements[0])
        return ""
    return expr.get_lookup_name()


def get_reference_expression(lhs: BaseElement) -> BaseElement:
    """
    Strip `Condition`, `PatternTest` and `HoldPattern` from an expression.
    """
    strip_headers = (
        SymbolHoldPattern,
        SymbolCondition,
        SymbolPatternTest,
    )
    # If atom, just return
    if not hasattr(lhs, "elements"):
        return lhs

    lhs_head = lhs.get_head()
    # If the head is wrapped, strip it

    if lhs_head.get_head() in strip_headers:
        lhs = Expression(get_reference_expression(lhs_head), *lhs.elements)
        lhs_head = lhs.get_head()

    while lhs_head in strip_headers:
        lhs = lhs.elements[0]
        if not hasattr(lhs, "elements"):
            return lhs
        lhs_head = lhs.get_head()
        if lhs_head.get_head() in strip_headers:
            lhs = Expression(get_reference_expression(lhs_head), *lhs.elements)

        lhs_head = lhs.get_head()

    return lhs


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
    (tags, lhs_reference,): Tuple[list, BaseElement]
        tags: the list of symbols to which the rule must be associated.
        lhs_reference: the lhs

    """
    name = lhs.get_head_name()
    lhs_reference_expr = get_reference_expression(lhs)

    if upset:
        tags_set = set()
        if isinstance(lhs_reference_expr, Atom):
            symbol_name = self.get_name()
            evaluation.message(
                symbol_name,
                "normal",
                Integer1,
                Expression(Symbol(symbol_name), lhs, rhs),
            )
            raise AssignmentException(lhs, None)
        for element in lhs_reference_expr.get_elements():
            # elements of the expression can also be wrapped in `HoldPattern`
            # or `Condition`. Tag candidates are obtained by stripping out
            # these wrappers.
            # Still, if the element is a `Blank*`, the reference is
            # set to its argument. If it does not have arguments (or have many)
            # skip it.
            name = get_lookup_reference_name(element)
            if name is not None:
                tags_set.add(name)
        return list(tags_set), lhs_reference_expr

    if tags is None:
        name = get_lookup_reference_name(lhs_reference_expr)
        if not name:
            evaluation.message(self.get_name(), "setraw", lhs_reference_expr)
            raise AssignmentException(lhs, None)
        tags = [name]
    else:
        allowed_names = set()
        name = get_lookup_reference_name(lhs_reference_expr)
        if name:
            allowed_names.add(name)

        for element in lhs_reference_expr.get_elements():
            name = get_lookup_reference_name(element)
            if name:
                allowed_names.add(name)
        for name in tags:
            if name not in allowed_names:
                evaluation.message(self.get_name(), "tagnfd", Symbol(name))
                raise AssignmentException(lhs, None)

    return tags, lhs_reference_expr


def process_tags_and_upset_dont_allow_custom(
    tags: Optional[list],
    upset: bool,
    self: Builtin,
    lhs: BaseElement,
    lhs_reference: BaseElement,
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

    def get_lookup_name(expr):
        expr = get_reference_expression(expr)
        if expr.has_form("System`Pattern", 2):
            return get_lookup_name(expr.elements[1])
        if expr.has_form(
            ("System`Blank", "System`BlankSequence", "System`BlankNullSequence"), None
        ):
            if len(expr.elements) == 1:
                return get_lookup_name(expr.elements[0])
            return None
        return expr.get_lookup_name()

    if isinstance(lhs_reference, Expression):
        lhs_reference = lhs_reference.evaluate_elements(evaluation)
    name = lhs.get_head_name()
    if upset:
        name = get_lookup_name(lhs_reference)
        tags = [name] if name is not None else None
    elif tags is None:
        name = get_lookup_name(lhs_reference)
        if not name:
            evaluation.message(self.get_name(), "setraw", lhs_reference)
            raise AssignmentException(lhs, None)
        tags = [name]
    else:
        name = get_lookup_name(lhs_reference)
        allowed_names = [name] if name else []
        for name in tags:
            if name not in allowed_names:
                evaluation.message(self.get_name(), "tagnfd", Symbol(name))
                raise AssignmentException(lhs, None)
    return tags


# Below is a mapping from Symbol name (as a string) into an assignment eval function.
ASSIGNMENT_FUNCTION_MAP = {
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


EVAL_ASSIGN_SPECIAL_SYMBOLS = {
    "System`$Context": eval_assign_context,
    "System`$ContextPath": eval_assign_context_path,
    "System`$HistoryLength": eval_assign_line_number_and_history_length,
    "System`$IterationLimit": eval_assign_iteration_limit,
    "System`$Line": eval_assign_line_number_and_history_length,
    "System`$MaxPrecision": eval_assign_maxprecision,
    "System`$MinPrecision": eval_assign_minprecision,
    "System`$ModuleNumber": eval_assign_module_number,
    "System`$RandomState": eval_assign_random_state,
    "System`$RecursionLimit": eval_assign_recursion_limit,
}
