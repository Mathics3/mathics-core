from mathics.core.parser import parse_builtin_rule
from mathics.core.symbols import SymbolList, strip_context


def filter_non_default_values(builtin):
    """
    Return a filter function that removes those
    options which have associated their default values.
    """
    builtin_options = builtin.options
    builtin_options = {
        strip_context(name): parse_builtin_rule(value)
        for name, value in builtin_options.items()
    }

    def filter(name, value):
        name = strip_context(name)
        if name not in builtin_options:
            return True
        if value.sameQ(builtin_options[name]):
            return False
        return True

    return filter
