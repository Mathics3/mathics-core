from typing import Callable, Optional

from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, strip_context
from mathics.core.systemsymbols import SymbolRule


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


def options_to_rules(options, filter: Optional[Callable] = None):
    items = sorted(options.items())
    if filter is not None:
        items = [(name, value) for name, value in items if filter(name, value)]
    return [Expression(SymbolRule, Symbol(name), value) for name, value in items]
