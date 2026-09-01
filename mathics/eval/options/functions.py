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


def _get_known_options(head, evaluation: Evaluation) -> dict:
    """Fetch defined options for head, if head has Options defined."""
    # Query evaluation definitions for Options[head]
    # Return a set/dict of option names if available, else empty dict
    opts = evaluation.definitions.get_options(head)
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


def eval_CheckArguments(
    expr, min_arg: int, max_arg: int, evaluation: Evaluation
) -> BooleanType:

    head = expr.head
    args = expr.elements  # tuple of argument Expression nodes

    pos_args, opt_args = _partition_arguments(args, evaluation)

    num_pos = len(pos_args)

    if num_pos < min_arg or num_pos > max_arg:
        # FIXME: should be distingish between
        #   CheckArguments[x[], 1] and CheckArguments[x[], {1, 1}]
        # kinds of errors?
        evaluation.message(
            "CheckArguments", "argx", head, Integer(num_pos), Integer(max_arg)
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


def _partition_arguments(args, evaluation: Evaluation):
    """
    Split args into positional arguments and trailing options/rules.
    Returns (pos_args, opt_args, isValidOptions).
    """
    pos_args = []
    opt_args = []

    # Trailing rules matching OptionsPattern are treated as options
    # if `known_options` is not empty, or trailing rules are encountered.
    for arg in reversed(args):
        # Check if arg is Rule[k, v], RuleDelayed[k, v], or List of Rules
        if is_option_pattern(arg, evaluation):
            opt_args.insert(0, args)
        else:
            # Once a non-option argument is encountered from the right,
            # remaining items to the left are all positional arguments.
            break

    pos_args = list(args[: len(args) - len(opt_args)])
    return pos_args, opt_args
