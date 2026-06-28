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
