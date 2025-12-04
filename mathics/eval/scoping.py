"""
Evaluation module corresponding to builtin functions in mathics.builtins.scoping.
"""
import re

from mathics.core.atoms import String
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, fully_qualified_symbol_name


def dynamic_scoping(func, vars, evaluation: Evaluation):
    """
    Changes temporarily the value of a set of symbols listed in vars,
    and evaluates func(evaluation)
    """
    original_definitions = {}

    for var_name, new_def in vars.items():
        assert fully_qualified_symbol_name(var_name)
        original_definitions[var_name] = evaluation.definitions.get_user_definition(
            var_name
        )
        evaluation.definitions.reset_user_definition(var_name)
        if new_def is not None:
            new_def = new_def.evaluate(evaluation)
            evaluation.definitions.set_ownvalue(var_name, new_def)
    try:
        result = func(evaluation)
    finally:
        for name, definition in original_definitions.items():
            evaluation.definitions.add_user_definition(name, definition)
    return result


def eval_contexts(definitions: Definitions) -> ListExpression:
    """
    Corresponding eval routine (sans builtin class boilerplate) for Context[]
    """
    return ListExpression(*sorted(get_contexts(definitions)))


def eval_contexts_with_string(string: str, definitions: Definitions) -> ListExpression:
    """
    Corresponding eval routine (sans builtin class boilerplate) for Context[string]
    """
    contexts = [context.value for context in get_contexts(definitions)]

    short_pattern = (
        string.replace("@", "[^A-Z]+").replace("*", ".*").replace("$", r"\$")
    )
    regex = re.compile("^" + short_pattern + "`$")

    matched_contexts = [String(name) for name in contexts if regex.match(name)]
    return ListExpression(*sorted(matched_contexts))


def get_contexts(definitions) -> set:
    contexts = set()
    for name in definitions.get_names():
        contexts.add(String(name[: name.rindex("`") + 1]))
    return contexts


def get_scoping_vars(var_list, msg_symbol="", evaluation=None):
    def message(tag, *args):
        if msg_symbol and evaluation:
            evaluation.message(msg_symbol, tag, *args)

    if not var_list.has_form("List", None):
        message("lvlist", var_list)
        return
    vars = var_list.elements
    scoping_vars = set()
    for var in vars:
        var_name = None
        if var.has_form("Set", 2):
            var_name = var.elements[0].get_name()
            new_def = var.elements[1]
            if evaluation:
                new_def = new_def.evaluate(evaluation)
        elif isinstance(var, Symbol):
            var_name = var.get_name()
            new_def = None
        if not var_name:
            message("lvsym", var)
            continue
        if var_name in scoping_vars:
            message("dup", Symbol(var_name))
        else:
            scoping_vars.add(var_name)
            yield var_name, new_def
