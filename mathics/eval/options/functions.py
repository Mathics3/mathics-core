from typing import Callable, Optional

from mathics.core.atoms import Integer, String
from mathics.core.atoms.associations import Association
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import is_option_rule, is_rule
from mathics.core.symbols import (
    BooleanType,
    Symbol,
    SymbolFalse,
    SymbolTrue,
    strip_context,
)
from mathics.core.systemsymbols import SymbolRule


def _extract_option_name(arg) -> str | None:
    """
    Extract the option name from a rule or list of rules.
    Returns the option name as a string or None.
    """
    if is_rule(arg):
        # arg is Rule[name, value] or RuleDelayed[name, value] or Expression[SymbolRule..]
        option_symbol = arg.elements[0]
        if isinstance(option_symbol, Symbol):
            return option_symbol.name
    elif isinstance(arg, ListExpression):
        # For a list of rules, all must have the same option names
        # or be valid options. We only check the first for now.
        if arg.elements and is_option_rule(arg.elements[0]):
            return _extract_option_name(arg.elements[0])
    return None


def _partition_arguments(
    args: tuple, head, extra_options: dict, evaluation: Evaluation
) -> tuple:
    """
    An argument is treated as an option if:
    * It matches an option pattern (Rule, RuleDelayed, or List of Rules), and
    * Its left-hand side (option name) is declared in the head's Options

    If no Options are declared for the head, trailing option patterns
    are still recognized as options.
    Split args into positional arguments and trailing options/rules.
    Returns (pos_args, opt_args, isValidOptions).
    """
    positional_args = []
    option_args = []
    options_start_index = len(args)

    # Get the declared options for this head
    declared_options = evaluation.definitions.get_options(head.name) | extra_options

    # Trailing rules matching OptionsPattern are treated as options
    # if they match declared options or if they are option patterns.
    for arg in reversed(args):
        # Check if arg is Rule[k, v], RuleDelayed[k, v], or List of Rules
        if is_option_pattern(arg, evaluation):
            # If we have declared options, check if this rule matches a declared option
            if declared_options:
                option_name = _extract_option_name(arg)
                if option_name:
                    if option_name in declared_options:
                        option_args.insert(0, arg)
                        options_start_index -= 1
                    else:
                        evaluation.message(head.name, "optx", String(option_name), args)
                        return [], [], -1
                else:
                    break
            else:
                # No declared options, so all trailing rules are treated as positional arguments
                break
                # option_args.insert(0, arg)
                # options_start_index -= 1
        else:
            # Once a non-option argument is encountered from the right,
            # remaining items to the left are all positional arguments.
            break

    positional_args = list(args[: len(args) - len(option_args)])
    return positional_args, option_args, options_start_index


def eval_CheckArguments(
    expr,
    min_arg_index: int,
    max_arg_index: int,
    evaluation: Evaluation,
    extra_options: dict = {},
) -> BooleanType:

    head = expr.head
    args = expr.elements  # tuple of argument Expression nodes

    positional_args, option_args, options_start_index = _partition_arguments(
        args, head, extra_options, evaluation
    )

    # -1 is a sentinal that we failed on options checking,
    # and _partition_arguments has already given a message.
    if options_start_index == -1:
        return SymbolFalse

    if option_args and options_start_index > max_arg_index:
        evaluation.message(
            "CheckArguments",
            "nonopt",
            args[min_arg_index],
            Integer(min_arg_index),
            expr,
        )
        return SymbolFalse

    len_positional_args = len(positional_args)

    if not (min_arg_index <= len_positional_args <= max_arg_index):
        # FIXME: should we distingish between
        #   CheckArguments[x[], 1] and CheckArguments[x[], {1, 1}]
        # kinds of errors?
        if max_arg_index == 1:
            evaluation.message(
                "CheckArguments",
                "argx",
                head,
                Integer(len_positional_args),
            )
        else:
            evaluation.message(
                "CheckArguments",
                "argrx",
                head,
                Integer(len_positional_args),
                Integer(max_arg_index),
            )
        return SymbolFalse

    return SymbolTrue


def eval_CheckArguments_with_association(
    expr,
    min_arg_index: int,
    max_arg_index: int,
    assoc: Association,
    evaluation: Evaluation,
) -> BooleanType:

    # Extract ExtraOptions from assoc.
    extra_options_dict = {}
    if isinstance(assoc, Association):
        extra_options = assoc.get(String("ExtraOptions"))
        if isinstance(extra_options, ListExpression):
            for option in extra_options:
                if is_option_rule(option):
                    key, value = option.elements
                    extra_options_dict[key.name] = value
                elif isinstance(option, Symbol):
                    extra_options_dict |= evaluation.definitions.get_options(
                        option.name
                    )

    return eval_CheckArguments(
        expr, min_arg_index, max_arg_index, evaluation, extra_options_dict
    )


def filter_from_iterable(elems) -> Callable:
    """
    Build a filter function from an iterable.
    The filter function returns `True` if
    the name after striping its context is in
    the interable.
    """

    def filter(name, value):
        return strip_context(name) in elems

    return filter


def is_option_pattern(expr, evaluation: Evaluation):
    """Check if an expression is a Rule, RuleDelayed, or List of Rules."""
    if is_option_rule(expr):
        return True
    if isinstance(expr, ListExpression):
        return all(is_option_pattern(e, evaluation) for e in expr.elements)
    return False


def options_to_rules(options, filter: Optional[Callable] = None):
    items = sorted(options.items())
    if filter is not None:
        items = [(name, value) for name, value in items if filter(name, value)]
    return [Expression(SymbolRule, Symbol(name), value) for name, value in items]
