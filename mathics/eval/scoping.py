"""
Evaluation module corresponding to builtin functions in mathics.builtins.scoping.
"""

import re
from typing import Optional

from mathics.core.atoms import String
from mathics.core.definitions import Definitions
from mathics.core.element import fully_qualified_symbol_name
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolList, SymbolSet


def dynamic_scoping(func, vars, evaluation: Evaluation):
    """
    Changes temporarily the value of a set of symbols listed in vars,
    and evaluates func(evaluation)
    """
    # Evaluate the new values before any variable is changed: a value
    # must not see the other variables, nor its own one, already reset.
    # Resetting $RecursionLimit, for instance, would evaluate the value
    # under the default limit.
    new_values = {
        var_name: None if new_def is None else new_def.evaluate(evaluation)
        for var_name, new_def in vars.items()
    }
    original_definitions = {}
    for var_name, new_def in new_values.items():
        assert fully_qualified_symbol_name(var_name)
        original_definitions[var_name] = evaluation.definitions.get_user_definition(
            var_name
        )
        evaluation.definitions.reset_user_definition(var_name)
        if new_def is not None:
            evaluation.definitions.set_ownvalue(var_name, new_def)
    try:
        result = func(evaluation)
    finally:
        for name, definition in original_definitions.items():
            evaluation.definitions.add_user_definition(name, definition)
    return result


def _definition_roots(definition):
    """The expressions a definition holds: both sides of its rules, and its
    option values."""
    lists = [
        definition.ownvalues,
        definition.downvalues,
        definition.subvalues,
        definition.upvalues,
        definition.nvalues,
        definition.defaultvalues,
        definition.messages,
        *definition.formatvalues.values(),
    ]
    for rules in lists:
        for rule in rules:
            yield rule.pattern.expr
            replace = getattr(rule, "replace", None)
            if replace is not None:
                yield replace
    yield from definition.options.values()


# How _find_names walks an element, by its class: 0 skip (an atom without
# symbols), 1 Symbol, 2 Expression, 3 Association, 4 Dispatch, 5 list or
# tuple. Looking the class up here avoids isinstance() on the abstract base
# classes of the elements, which costs more than the rest of the walk.
_walk_kinds: dict = {list: 5, tuple: 5}


def _walk_kind(cls) -> int:
    from mathics.core.atoms.associations import Association
    from mathics.eval.rules import Dispatch

    if issubclass(cls, Symbol):
        kind = 1
    elif issubclass(cls, Expression):
        kind = 2
    elif issubclass(cls, Association):
        kind = 3
    elif issubclass(cls, Dispatch):
        kind = 4
    elif issubclass(cls, (list, tuple)):
        kind = 5
    else:
        kind = 0
    _walk_kinds[cls] = kind
    return kind


class _BudgetExceeded(Exception):
    pass


def _find_names(
    roots, names: set, found: set, seen: set, budget: Optional[list] = None
) -> None:
    """Add to `found` the names in `names` of the symbols that occur in
    `roots`. `seen` holds the ids of the expressions already walked.

    With a `budget` ([number of expressions]), raise _BudgetExceeded when
    more expressions than that would have to be walked."""
    kinds = _walk_kinds
    stack = list(roots)
    pop = stack.pop
    push = stack.append
    extend = stack.extend
    while stack:
        element = pop()
        cls = element.__class__
        kind = kinds.get(cls)
        if kind is None:
            kind = _walk_kind(cls)
        if kind == 0:
            continue
        if kind == 1:
            name = element.name
            if name in names:
                found.add(name)
                if len(found) == len(names):
                    return
            continue
        key = id(element)
        if key in seen:
            continue
        seen.add(key)
        if budget is not None:
            budget[0] -= 1
            if budget[0] < 0:
                raise _BudgetExceeded
        if kind == 2:
            push(element._head)
            extend(element._elements)
        elif kind == 3:
            push(element.expr)
        elif kind == 4:
            push(element.src)
        else:
            extend(element)


def release_module_variables(
    definitions: Definitions,
    names: list,
    changed: list,
    results: list,
    budget: Optional[int] = None,
) -> bool:
    """Remove the definitions of the local variables `names` of a Module
    that nothing references any more, as WMA does with its temporary symbols.

    A variable is still referenced when it occurs in one of `results`
    (what the Module returns, or what an interrupt carries out of it), or
    in a definition that changed while the Module was evaluated (the
    definitions `changed`), or in a kept variable. Nothing that existed
    before the Module can hold one of its variables otherwise.

    Without this, every value given to a Module variable stays in the
    session for good, including the partial values of an aborted Module.

    With a `budget`, give up and return False, removing nothing, when more
    than `budget` expressions would have to be walked to decide; the
    enclosing Module then decides for these variables too. Return True
    otherwise.
    """
    user = definitions.user
    candidates = {
        name: definition for name in names if (definition := user.get(name)) is not None
    }
    if not candidates:
        return True
    pending = set(candidates)
    found: set = set()
    seen: set = set()
    left = None if budget is None else [budget]
    try:
        _find_names(results, pending, found, seen, left)

        walked = set()
        for definition in changed:
            if not pending - found:
                break
            name = definition.name
            if name in candidates or id(definition) in walked:
                continue
            walked.add(id(definition))
            if user.get(name) is not definition:
                continue
            _find_names(_definition_roots(definition), pending, found, seen, left)

        # A kept variable keeps the variables its own definition refers to.
        work = list(found)
        while work and pending - found:
            name = work.pop()
            before = set(found)
            _find_names(_definition_roots(candidates[name]), pending, found, seen, left)
            work.extend(found - before)
    except _BudgetExceeded:
        return False

    for name in pending - found:
        del user[name]
        definitions.clear_cache(name)
    return True


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

    if not var_list.has_form(SymbolList, None):
        message("lvlist", var_list)
        return
    vars = var_list.elements
    scoping_vars = set()
    for var in vars:
        var_name = None
        if var.has_form(SymbolSet, 2):
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
