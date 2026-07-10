from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import SymbolKeyAbsent, SymbolMissing


def eval_Lookup(assoc, key, default, evaluation: Evaluation):
    """Evaluation method for Lookup."""

    if assoc.has_form("Association", None):
        # Search through association elements (rules)
        for element in assoc.elements:
            if element.has_form(("Rule", "RuleDelayed"), 2):
                if element.elements[0] == key:
                    return element.elements[1]

        # Key not found
        if default is not None:
            return default
        else:
            return Expression(SymbolMissing, SymbolKeyAbsent, key)

    elif isinstance(assoc, ListExpression):
        # Search through list of rules
        for element in assoc.elements:
            if element.has_form(("Rule", "RuleDelayed"), 2):
                if element.elements[0] == key:
                    return element.elements[1]

        # Key not found
        if default is not None:
            return default
        else:
            return Expression(SymbolMissing, SymbolKeyAbsent, key)

    elif assoc.has_form(("Rule", "RuleDelayed"), 2):
        if assoc.elements[0] == key:
            return assoc.elements[1]
        return None

    else:
        evaluation.message("Lookup", "invrl", assoc)
        # Should we return SymbolFailed?
        return None


def eval_Lookup_assocs_list_key(assocs, key, default, evaluation: Evaluation):
    """Evaluation method for Lookup with a list of associations and a single key.

    Looks up the key in each association and returns a list of values.
    """
    if not isinstance(assocs, ListExpression):
        evaluation.message("Lookup", "invrl", assocs)
        return None

    results = [
        eval_Lookup(assoc, key, default, evaluation) for assoc in assocs.elements
    ]
    return ListExpression(*results)


def eval_Lookup_multiple_keys(assoc, keys, default, evaluation: Evaluation):
    """Evaluation method for Lookup with multiple keys, threading over the key list."""
    results = [eval_Lookup(assoc, key, default, evaluation) for key in keys.elements]
    return ListExpression(*results)


def eval_assocs_list_key(self, assocs, key, evaluation: Evaluation):
    """Lookup[assocs_List, key_]"""
    return eval_Lookup_assocs_list_key(assocs, key, None, evaluation)


def eval_assocs_list_key_default(self, assocs, key, default, evaluation: Evaluation):
    """Lookup[assocs_List, key_, default_]"""
    return eval_Lookup_assocs_list_key(assocs, key, default, evaluation)
