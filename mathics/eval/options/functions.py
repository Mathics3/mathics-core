from typing import Callable, Optional

from mathics.core.atoms import Integer
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import is_option_rule
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
    if is_option_rule(arg):
        # arg is Rule[name, value] or RuleDelayed[name, value]
        option_symbol = arg.elements[0]
        if isinstance(option_symbol, Symbol):
            return option_symbol.name
    elif isinstance(arg, ListExpression):
        # For a list of rules, all must have the same option names
        # or be valid options. We only check the first for now.
        if arg.elements and is_option_rule(arg.elements[0]):
            return _extract_option_name(arg.elements[0])
    return None


def _get_known_options(head, evaluation: Evaluation) -> dict:
    """Fetch defined options for head, if head has Options defined."""
    # Query evaluation definitions for Options[head]
    # Return a set/dict of option names if available, else empty dict
    opts = evaluation.definitions.get_options(head.name)
    return opts if opts else {}


def _parse_spec(self, spec, evaluation: Evaluation) -> tuple:
    """Extract min and max positional argument count from spec."""
    if isinstance(spec, Integer):
        val = spec.value
        return val, val
    elif isinstance(spec, ListExpression):
        if len(spec.elements) == 2:
            min_val = spec.elements[0].to_python()
            max_val = spec.elements[1].to_python()
            if isinstance(min_val, int) and isinstance(max_val, int):
                return min_val, max_val
    return None, None


def _partition_arguments(args: tuple, head, evaluation: Evaluation) -> tuple:
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
    declared_options = _get_known_options(head, evaluation)

    # Trailing rules matching OptionsPattern are treated as options
    # if they match declared options or if they are option patterns.
    for arg in reversed(args):
        # Check if arg is Rule[k, v], RuleDelayed[k, v], or List of Rules
        if is_option_pattern(arg, evaluation):
            # If we have declared options, check if this rule matches a declared option
            if declared_options:
                option_name = _extract_option_name(arg)
                if option_name and option_name in declared_options:
                    option_args.insert(0, arg)
                    options_start_index -= 1
                else:
                    # Not a declared option, so treat as positional argument
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
    expr, min_arg_index: int, max_arg_index: int, evaluation: Evaluation
) -> BooleanType:

    head = expr.head
    args = expr.elements  # tuple of argument Expression nodes

    positional_args, option_args, options_start_index = _partition_arguments(
        args, head, evaluation
    )

    if option_args and options_start_index > min_arg_index:
        evaluation.message(
            "CheckArguments",
            "nonopt",
            args[min_arg_index],
            Integer(min_arg_index),
            expr,
        )
        return SymbolFalse

    len_positional_args = len(positional_args)

    if len_positional_args < min_arg_index or len_positional_args > max_arg_index:
        # FIXME: should be distingish between
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
