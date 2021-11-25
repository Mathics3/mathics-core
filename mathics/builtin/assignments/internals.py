# -*- coding: utf-8 -*-


from mathics.algorithm.parts import walk_parts
from mathics.core.evaluation import MAX_RECURSION_DEPTH, set_python_recursion_limit
from mathics.core.expression import Expression
from mathics.core.rules import Rule
from mathics.core.symbols import (
    Symbol,
    SymbolList,
    SymbolN,
    system_symbols,
    valid_context_name,
)
from mathics.core.systemsymbols import (
    SymbolAnd,
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolCondition,
    SymbolHistoryLength,
    SymbolHoldPattern,
    SymbolInfinity,
    SymbolIterationLimit,
    SymbolLine,
    SymbolLocked,
    SymbolMachinePrecision,
    SymbolMaxPrecision,
    SymbolMinPrecision,
    SymbolModuleNumber,
    SymbolOptionValue,
    SymbolPart,
    SymbolPattern,
    SymbolProtected,
    SymbolRuleDelayed,
    SymbolRecursionLimit,
)


class AssignmentException(Exception):
    def __init__(self, lhs, rhs) -> None:
        super().__init__(" %s cannot be assigned to %s" % (rhs, lhs))
        self.lhs = lhs
        self.rhs = rhs


def assign_store_rules_by_tag(self, lhs, rhs, evaluation, tags, upset=None):
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    count = 0
    defs = evaluation.definitions
    ignore_protection, tags = process_assign_other(
        self, lhs, rhs, evaluation, tags, upset
    )
    lhs, rhs = process_rhs_conditions(lhs, rhs, condition, evaluation)
    count = 0
    rule = Rule(lhs, rhs)
    position = "up" if upset else None
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation, ignore_protection):
            continue
        count += 1
        defs.add_rule(tag.name, rule, position=position)
    return count > 0


def build_rulopc(optval):
    return Rule(
        Expression(
            "OptionValue",
            Expression(SymbolPattern, Symbol("$cond$"), Expression(SymbolBlank)),
        ),
        Expression(SymbolOptionValue, optval, Symbol("$cond$")),
    )


def get_symbol_list(list, error_callback):
    if list.has_form("List", None):
        list = list.leaves
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
    leaves = []
    for rule in definition.get_values_list(position):
        if isinstance(rule, Rule):
            pattern = rule.pattern
            if pattern.has_form("HoldPattern", 1):
                pattern = pattern.expr
            else:
                pattern = Expression(SymbolHoldPattern, pattern.expr)
            leaves.append(Expression(SymbolRuleDelayed, pattern, rule.replace))
    return Expression(SymbolList, *leaves)


def is_protected(tag, defin):
    return SymbolProtected in defin.get_attributes(tag.name)


def repl_pattern_by_symbol(expr):
    leaves = expr.get_leaves()
    if len(leaves) == 0:
        return expr

    head = expr.get_head()
    if head is SymbolPattern:
        return leaves[0]

    changed = False
    newleaves = []
    for leave in leaves:
        leaf = repl_pattern_by_symbol(leave)
        if not (leaf is leave):
            changed = True
        newleaves.append(leaf)
    if changed:
        return Expression(head, *newleaves)
    else:
        return expr


# Here are the functions related to assign_elementary

# Auxiliary routines


def rejected_because_protected(self, lhs, tag, evaluation, ignore=False):
    defs = evaluation.definitions
    if not ignore and is_protected(tag, defs):
        if lhs is tag:
            evaluation.message(self.get_name(), "wrsym", tag)
        else:
            evaluation.message(self.get_name(), "write", tag, lhs)
        return True
    return False


def find_tag_and_check(lhs, tags, evaluation):
    head = lhs.get_head()
    if len(lhs.leaves) != 1:
        evaluation.message_args(head.get_name(), len(lhs.leaves), 1)
        raise AssignmentException(lhs, None)
    tag = lhs.leaves[0]
    if not tag.is_symbol():
        evaluation.message(head.get_name(), "sym", tag, 1)
        raise AssignmentException(lhs, None)
    if tags is not None and tags != [tag]:
        evaluation.message(head.get_name(), "tag", head, tag)
        raise AssignmentException(lhs, None)
    if is_protected(tag, evaluation.definitions):
        evaluation.message(head.get_name(), "wrsym", tag)
        raise AssignmentException(lhs, None)
    return tag


def unroll_patterns(lhs, rhs, evaluation):
    if type(lhs) is Symbol:
        return lhs, rhs
    symbol = lhs.get_head()
    lhsleaves = lhs._leaves
    if symbol is SymbolPattern:
        lhs = lhsleaves[1]
        rulerepl = (lhsleaves[0], repl_pattern_by_symbol(lhs))
        rhs, status = rhs.apply_rules([Rule(*rulerepl)], evaluation)
        symbol = lhs.get_head()

    if symbol is SymbolHoldPattern:
        lhs = lhsleaves[0]
    return lhs, rhs


def unroll_conditions(lhs):
    condition = None
    if type(lhs) is Symbol:
        return lhs, None
    else:
        head, lhs_leaves = lhs.get_head(), lhs._leaves
    condition = []
    # This handle the case of many sucesive conditions:
    # f[x_]/; cond1 /; cond2 ... ->  f[x_]/; And[cond1, cond2, ...]
    while head is SymbolCondition and len(lhs.leaves) == 2:
        condition.append(lhs_leaves[1])
        lhs = lhs_leaves[0]
        head, lhs_leaves = lhs.get_head(), lhs._leaves
    if len(condition) == 0:
        return lhs, None
    if len(condition) > 1:
        condition = Expression(SymbolAnd, *condition)
    else:
        condition = condition[0]
    condition = Expression(SymbolCondition, lhs, condition)
    lhs._format_cache = None
    return lhs, condition


# Here starts the functions that implement `assign_elementary` for different
# kind of expressions. Maybe they should be put in a separated module or
# maybe they should be member functions of _SetOperator.


def process_assign_recursion_limit(lhs, rhs, evaluation):
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


def process_assign_iteration_limit(lhs, rhs, evaluation):
    rhs_int_value = rhs.get_int_value()
    if (not rhs_int_value or rhs_int_value < 20) and rhs is not SymbolInfinity:
        evaluation.message("$IterationLimit", "limset", rhs)
        raise AssignmentException(lhs, None)
    return False


def process_assign_module_number(lhs, rhs, evaluation):
    rhs_int_value = rhs.get_int_value()
    if not rhs_int_value or rhs_int_value <= 0:
        evaluation.message("$ModuleNumber", "set", rhs)
        raise AssignmentException(lhs, None)
    return False


def process_assign_line_number_and_history_length(
    self, lhs, rhs, evaluation, tags, upset
):
    rhs_int_value = rhs.get_int_value()
    if rhs_int_value is None or rhs_int_value < 0:
        evaluation.message(lhs.get_name(), "intnn", rhs)
        raise AssignmentException(lhs, None)
    return False


def process_assign_random_state(self, lhs, rhs, evaluation, tags, upset):
    # TODO: allow setting of legal random states!
    # (but consider pickle's insecurity!)
    evaluation.message("$RandomState", "rndst", rhs)
    raise AssignmentException(lhs, None)


def process_assign_context(self, lhs, rhs, evaluation, tags, upset):
    new_context = rhs.get_string_value()
    if new_context is None or not valid_context_name(
        new_context, allow_initial_backquote=True
    ):
        evaluation.message(lhs.get_name(), "cxset", rhs)
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
    currContext = evaluation.definitions.get_current_context()
    context_path = [s.get_string_value() for s in rhs.get_leaves()]
    context_path = [
        s if (s is None or s[0] != "`") else currContext[:-1] + s for s in context_path
    ]
    if rhs.has_form("List", None) and all(valid_context_name(s) for s in context_path):
        evaluation.definitions.set_context_path(context_path)
        return True
    else:
        evaluation.message(lhs.get_name(), "cxlist", rhs)
        raise AssignmentException(lhs, None)


def process_assign_minprecision(self, lhs, rhs, evaluation, tags, upset):
    rhs_int_value = rhs.get_int_value()
    # $MinPrecision = Infinity is not allowed
    if rhs_int_value is not None and rhs_int_value >= 0:
        max_prec = evaluation.definitions.get_config_value("$MaxPrecision")
        if max_prec is not None and max_prec < rhs_int_value:
            evaluation.message("$MinPrecision", "preccon", SymbolMinPrecision)
            raise AssignmentException(lhs, None)
        return False
    else:
        evaluation.message(lhs.get_name(), "precset", lhs, rhs)
        raise AssignmentException(lhs, None)


def process_assign_maxprecision(self, lhs, rhs, evaluation, tags, upset):
    rhs_int_value = rhs.get_int_value()
    if rhs.has_form("DirectedInfinity", 1) and rhs.leaves[0].get_int_value() == 1:
        return False
    elif rhs_int_value is not None and rhs_int_value > 0:
        min_prec = evaluation.definitions.get_config_value("$MinPrecision")
        if min_prec is not None and rhs_int_value < min_prec:
            evaluation.message("$MaxPrecision", "preccon", SymbolMaxPrecision)
            raise AssignmentException(lhs, None)
        return False
    else:
        evaluation.message(lhs.get_name(), "precset", lhs, rhs)
        raise AssignmentException(lhs, None)


def process_assign_definition_values(self, lhs, rhs, evaluation, tags, upset):
    tag = find_tag_and_check(lhs, tags, evaluation)
    rules = rhs.get_rules_list()
    if rules is None:
        evaluation.message(lhs.get_head_name(), "vrule", lhs, rhs)
        raise AssignmentException(lhs, None)
    evaluation.definitions.set_values(tag.name, lhs.get_head_name(), rules)
    return True


def process_assign_options(self, lhs, rhs, evaluation, tags, upset):
    lhs_leaves = lhs.leaves
    if len(lhs_leaves) != 1:
        evaluation.message_args(lhs.get_head_name(), len(lhs_leaves), 1)
        raise AssignmentException(lhs, rhs)
    tag = lhs_leaves[0]
    if not tag.is_symbol():
        evaluation.message(lhs.get_head_name(), "sym", tag, 1)
        raise AssignmentException(lhs, rhs)
    if tags is not None and tags != [tag]:
        evaluation.message(lhs.get_head_name(), "tag", lhs.get_head(), tag)
        raise AssignmentException(lhs, rhs)
    if is_protected(tag, evaluation.definitions):
        evaluation.message(lhs.get_head_name(), "wrsym", tag)
        raise AssignmentException(lhs, None)
    option_values = rhs.get_option_values(evaluation)
    if option_values is None:
        evaluation.message(lhs.get_head_name(), "options", rhs)
        raise AssignmentException(lhs, None)
    evaluation.definitions.set_options(tag.name, option_values)
    return True


def process_assign_n(self, lhs, rhs, evaluation, tags, upset):
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    defs = evaluation.definitions
    if len(lhs.leaves) not in (1, 2):
        evaluation.message_args("N", len(lhs.leaves), 1, 2)
        raise AssignmentException(lhs, None)
    if len(lhs.leaves) == 1:
        nprec = SymbolMachinePrecision
    else:
        nprec = lhs.leaves[1]
    focus = lhs.leaves[0]
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
        defs.add_nvalue(tag.name, rule)
    return count > 0


def process_assign_other(self, lhs, rhs, evaluation, tags=None, upset=False):
    tags, focus = process_tags_and_upset_allow_custom(
        tags, upset, self, lhs, evaluation
    )
    if lhs is SymbolRecursionLimit:
        process_assign_recursion_limit(self, lhs, rhs, evaluation, tags, upset)
    elif lhs in (SymbolLine, SymbolHistoryLength):
        process_assign_line_number_and_history_length(
            self, lhs, rhs, evaluation, tags, upset
        )
    elif lhs is SymbolIterationLimit:
        process_assign_iteration_limit(self, lhs, rhs, evaluation, tags, upset)
    elif lhs is SymbolModuleNumber:
        process_assign_module_number(self, lhs, rhs, evaluation, tags, upset)
    elif lhs is SymbolMinPrecision:
        process_assign_minprecision(self, lhs, rhs, evaluation, tags, upset)
    elif lhs is SymbolMaxPrecision:
        process_assign_maxprecision(self, lhs, rhs, evaluation, tags, upset)
    else:
        return False, tags
    return True, tags


def process_assign_attributes(self, lhs, rhs, evaluation, tags, upset):
    if len(lhs.leaves) != 1:
        evaluation.message_args(lhs.get_head_name(), len(lhs.leaves), 1)
        raise AssignmentException(lhs, rhs)
    tag = lhs.leaves[0]
    if not tag.is_symbol():
        evaluation.message(lhs.get_head_name(), "sym", tag, 1)
        raise AssignmentException(lhs, rhs)
    if tags is not None and tags != [tag]:
        evaluation.message(lhs.get_head_name(), "tag", lhs.get_head(), tag)
        raise AssignmentException(lhs, rhs)
    attributes = get_symbol_list(
        rhs, lambda item: evaluation.message(lhs.get_head_name(), "sym", item, 1)
    )
    if attributes is None:
        raise AssignmentException(lhs, rhs)
    if SymbolLocked in evaluation.definitions.get_attributes(tag.name):
        evaluation.message(lhs.get_head_name(), "locked", tag)
        raise AssignmentException(lhs, rhs)
    evaluation.definitions.set_attributes(tag.name, attributes)
    return True


def process_assign_default(self, lhs, rhs, evaluation, tags, upset):
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    count = 0
    defs = evaluation.definitions

    if len(lhs.leaves) not in (1, 2, 3):
        evaluation.message_args("Default", len(lhs.leaves), 1, 2, 3)
        raise AssignmentException(lhs, None)
    focus = lhs.leaves[0]
    tags = process_tags_and_upset_dont_allow_custom(
        tags, upset, self, lhs, focus, evaluation
    )
    lhs, rhs = process_rhs_conditions(lhs, rhs, condition, evaluation)
    rule = Rule(lhs, rhs)
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation):
            continue
        count += 1
        defs.add_default(tag.name, rule)
    return count > 0


def process_assign_format(self, lhs, rhs, evaluation, tags, upset):
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    count = 0
    defs = evaluation.definitions

    if len(lhs.leaves) not in (1, 2):
        evaluation.message_args("Format", len(lhs.leaves), 1, 2)
        raise AssignmentException(lhs, None)
    if len(lhs.leaves) == 2:
        form = lhs.leaves[1].get_name()
        if not form:
            evaluation.message("Format", "fttp", lhs.leaves[1])
            raise AssignmentException(lhs, None)
    else:
        form = system_symbols(
            "StandardForm",
            "TraditionalForm",
            "OutputForm",
            "TeXForm",
            "MathMLForm",
        )
        form = [f.name for f in form]
    lhs = focus = lhs.leaves[0]
    tags = process_tags_and_upset_dont_allow_custom(
        tags, upset, self, lhs, focus, evaluation
    )
    lhs, rhs = process_rhs_conditions(lhs, rhs, condition, evaluation)
    rule = Rule(lhs, rhs)
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation):
            continue
        count += 1
        defs.add_format(tag.name, rule, form)
    return count > 0


def process_assign_messagename(self, lhs, rhs, evaluation, tags, upset):
    lhs, condition = unroll_conditions(lhs)
    lhs, rhs = unroll_patterns(lhs, rhs, evaluation)
    count = 0
    defs = evaluation.definitions
    if len(lhs.leaves) != 2:
        evaluation.message_args("MessageName", len(lhs.leaves), 2)
        raise AssignmentException(lhs, None)
    focus = lhs.leaves[0]
    tags = process_tags_and_upset_dont_allow_custom(
        tags, upset, self, lhs, focus, evaluation
    )
    lhs, rhs = process_rhs_conditions(lhs, rhs, condition, evaluation)
    rule = Rule(lhs, rhs)
    for tag in tags:
        if rejected_because_protected(self, lhs, tag, evaluation):
            continue
        count += 1
        defs.add_message(tag.name, rule)
    return count > 0


def process_rhs_conditions(lhs, rhs, condition, evaluation):
    # To Handle `OptionValue` in `Condition`
    rulopc = build_rulopc(lhs.get_head())
    rhs_name = rhs.get_head_name()
    while rhs_name == "System`Condition":
        if len(rhs.leaves) != 2:
            evaluation.message_args("Condition", len(rhs.leaves), 2)
            raise AssignmentException(lhs, None)
        lhs = Expression(
            "Condition", lhs, rhs.leaves[1].apply_rules([rulopc], evaluation)[0]
        )
        rhs = rhs.leaves[0]
        rhs_name = rhs.get_head_name()

    # Now, let's add the conditions on the LHS
    if condition:
        lhs = Expression(
            "Condition",
            lhs,
            condition.leaves[1].apply_rules([rulopc], evaluation)[0],
        )
    return lhs, rhs


def process_tags_and_upset_dont_allow_custom(tags, upset, self, lhs, focus, evaluation):
    # TODO: the following provides a hacky fix for 1259. I know @rocky loves
    # this kind of things, but otherwise we need to work on rebuild the pattern
    # matching mechanism...
    flag_ioi, evaluation.ignore_oneidentity = evaluation.ignore_oneidentity, True
    focus = focus.evaluate_leaves(evaluation)
    evaluation.ignore_oneidentity = flag_ioi
    head = lhs.get_head()
    if tags is None and not upset:
        head = focus.get_lookup_symbol()
        if head is None or not head.is_symbol():
            evaluation.message(self.get_name(), "setraw", focus)
            raise AssignmentException(lhs, None)
        tags = [head]
    elif upset:
        tags = [focus.get_lookup_symbol()]
    else:
        allowed_symbols = [focus.get_lookup_symbol()]
        for symbol in tags:
            if symbol not in allowed_symbols:
                evaluation.message(self.get_name(), "tagnfd", symbol)
                raise AssignmentException(lhs, None)
    return tags


def process_tags_and_upset_allow_custom(tags, upset, self, lhs, evaluation):
    # TODO: the following provides a hacky fix for 1259. I know @rocky loves
    # this kind of things, but otherwise we need to work on rebuild the pattern
    # matching mechanism...
    head = lhs.get_head()
    focus = lhs
    flag_ioi, evaluation.ignore_oneidentity = evaluation.ignore_oneidentity, True
    focus = focus.evaluate_leaves(evaluation)
    evaluation.ignore_oneidentity = flag_ioi
    if tags is None and not upset:
        head = focus.get_lookup_symbol()
        if not head:
            evaluation.message(self.get_name(), "setraw", focus)
            raise AssignmentException(lhs, None)
        tags = [head]
    elif upset:
        tags = []
        if focus.is_atom():
            evaluation.message(self.get_name(), "normal")
            raise AssignmentException(lhs, None)
        for leaf in focus.leaves:
            head = leaf.get_lookup_symbol()
            tags.append(head)
    else:
        allowed_symbols = [focus.get_lookup_symbol()]
        for leaf in focus.get_leaves():
            if not leaf.is_symbol() and leaf.get_head() in (SymbolHoldPattern,):
                leaf = leaf.leaves[0]
            if not leaf.is_symbol() and leaf.get_head() in (SymbolPattern,):
                leaf = leaf.leaves[1]
            if not leaf.is_symbol() and leaf.get_head() in (
                SymbolBlank,
                SymbolBlankSequence,
                SymbolBlankNullSequence,
            ):
                if len(leaf.leaves) == 1:
                    leaf = leaf.leaves[0]

            allowed_symbols.append(leaf.get_lookup_symbol())
        for symbol in tags:
            if symbol not in allowed_symbols:
                evaluation.message(self.get_name(), "tagnfd", symbol)
                raise AssignmentException(lhs, None)

    return tags, focus


class _SetOperator(object):
    special_cases = {
        "System`OwnValues": process_assign_definition_values,
        "System`DownValues": process_assign_definition_values,
        "System`SubValues": process_assign_definition_values,
        "System`UpValues": process_assign_definition_values,
        "System`NValues": process_assign_definition_values,
        "System`DefaultValues": process_assign_definition_values,
        "System`Messages": process_assign_definition_values,
        "System`Attributes": process_assign_attributes,
        "System`Options": process_assign_options,
        "System`$RandomState": process_assign_random_state,
        "System`$Context": process_assign_context,
        "System`$ContextPath": process_assign_context_path,
        "System`N": process_assign_n,
        "System`MessageName": process_assign_messagename,
        "System`Default": process_assign_default,
        "System`Format": process_assign_format,
    }
    messages = {
        "setraw": "Cannot assign to raw object `1`.",
        "shape": "Lists `1` and `2` are not the same shape.",
    }

    def assign_elementary(self, lhs, rhs, evaluation, tags=None, upset=False):
        if type(lhs) is Symbol:
            name = lhs.name
        elif lhs.is_atom():
            evaluation.message(self.get_name(), "setraw", lhs)
            raise AssignmentException(lhs, None)
        else:  # Expression
            name = lhs.get_head_name()
        lhs._format_cache = None
        try:
            # Deal with direct assignation to properties of
            # the definition object
            func = self.special_cases.get(name, None)
            if func:
                return func(self, lhs, rhs, evaluation, tags, upset)
            return assign_store_rules_by_tag(self, lhs, rhs, evaluation, tags, upset)
        except AssignmentException:
            return False

    def assign(self, lhs, rhs, evaluation):
        lhs._format_cache = None
        defs = evaluation.definitions
        if lhs.get_head() is SymbolList:
            if not (rhs.get_head() is SymbolList) or len(lhs.leaves) != len(
                rhs.leaves
            ):  # nopep8

                evaluation.message(self.get_name(), "shape", lhs, rhs)
                return False
            else:
                result = True
                for left, right in zip(lhs.leaves, rhs.leaves):
                    if not self.assign(left, right, evaluation):
                        result = False
                return result
        elif lhs.get_head() is SymbolPart:
            if len(lhs.leaves) < 1:
                evaluation.message(self.get_name(), "setp", lhs)
                return False
            symbol = lhs.leaves[0]
            if not symbol.is_symbol():
                evaluation.message(self.get_name(), "setps", symbol)
                return False
            if is_protected(symbol, defs):
                evaluation.message(self.get_name(), "wrsym", symbol)
                return False
            rule = defs.get_ownvalue(symbol.name)
            if rule is None:
                evaluation.message(self.get_name(), "noval", symbol)
                return False
            indices = lhs.leaves[1:]
            return walk_parts([rule.replace], indices, evaluation, rhs)
        else:
            return self.assign_elementary(lhs, rhs, evaluation)
