from mathics.core.atoms import Integer
from mathics.core.atoms.associations import Association
from mathics.core.convert.expression import to_mathics_list
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import is_rule
from mathics.core.symbols import SymbolTrue
from mathics.core.systemsymbols import SymbolKeyAbsent, SymbolMissing


def eval_AssociationQ(expr) -> bool:
    def validate(elements: list[BaseElement]) -> bool:
        for element in elements:
            if is_rule(element):
                pass
            elif element.has_form(("List", "Association"), None):
                if not validate(element.elements):
                    return False
            else:
                return False
        return True

    if isinstance(expr, Association):
        return True

    # Handle where we still have Expression[SymbolRule, ... ]
    return expr.get_head_name() == "System`Association" and validate(expr.elements)


def eval_Keys(rules_or_association, evaluation: Evaluation):
    def get_keys(expr):
        if isinstance(expr, Association):
            return ListExpression(*expr.keys())
        if is_rule(expr):
            return expr.elements[0]
        elif expr.has_form("List", None) or (
            expr.has_form("Association", None) and eval_AssociationQ(expr)
        ):
            return to_mathics_list(*expr.elements, elements_conversion_fn=get_keys)
        else:
            evaluation.message("Keys", "invrl", expr)
            raise TypeError

    if isinstance(rules_or_association, Association):
        return ListExpression(*rules_or_association.keys())

    rules = rules_or_association.get_sequence()
    if len(rules) != 1:
        evaluation.message("Keys", "argx", Integer(len(rules)))
        return

    try:
        return get_keys(rules[0])
    except TypeError:
        return None


def eval_Keys_with_Head(
    rules_or_association, head: BaseElement, evaluation: Evaluation
):

    def get_keys_with_head(expr, h: BaseElement) -> BaseElement:
        if isinstance(expr, Association):
            return ListExpression(
                *(Expression(h, key) for key in expr.collection.keys())
            )
        if is_rule(expr):
            key = expr.elements[0]
            return Expression(h, key)
        elif expr.has_form("List", None) or (
            expr.has_form("Association", None) and eval_AssociationQ(expr) is SymbolTrue
        ):
            return to_mathics_list(
                *expr.elements,
                elements_conversion_fn=lambda e: get_keys_with_head(e, h),
            )
        else:
            evaluation.message("Keys", "invrl", expr)
            raise TypeError

    try:
        return get_keys_with_head(rules_or_association, head)
    except TypeError:
        return None


def eval_Lookup(assoc, key: BaseElement, default: BaseElement, evaluation: Evaluation):
    """Evaluation method for Lookup."""

    if default is None:
        default = Expression(SymbolMissing, SymbolKeyAbsent, key)

    if isinstance(assoc, Association):
        return assoc.get(key, default)

    if assoc.has_form("Association", None):
        # Search through association elements (rules)
        for element in assoc.elements:
            if is_rule(element):
                if element.elements[0] == key:
                    return element.elements[1]

        # Key not found
        return default

    elif isinstance(assoc, ListExpression):
        # Search through list of rules
        for element in assoc.elements:
            if is_rule(element):
                if element.elements[0] == key:
                    return element.elements[1]

        # Key not found
        if default is not None:
            return default
        else:
            return Expression(SymbolMissing, SymbolKeyAbsent, key)

    elif is_rule(assoc):
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


def eval_Values(rules_or_association, evaluation: Evaluation):

    def get_values(expr):
        if isinstance(expr, Association):
            return ListExpression(*expr.values())
        if is_rule(expr):
            return expr.elements[1]
        if expr.has_form("List", None) or (
            expr.has_form("Association", None) and eval_AssociationQ(expr)
        ):
            return to_mathics_list(*expr.elements, elements_conversion_fn=get_values)
        else:
            raise TypeError

    rules = rules_or_association.get_sequence()
    if len(rules) != 1:
        evaluation.message("Values", "argx", Integer(len(rules)))
        return

    try:
        return get_values(rules[0])
    except TypeError:
        evaluation.message("Values", "invrl", rules[0])


def eval_Values_with_Head(
    rules_or_association, head: BaseElement, evaluation: Evaluation
):

    def get_values_with_head(expr, h: BaseElement) -> BaseElement:
        if isinstance(expr, Association):
            return ListExpression(
                *(Expression(h, key) for key in expr.collection.values())
            )
        if is_rule(expr):
            value = expr.elements[1]
            return Expression(h, value)
        if expr.has_form("List", None) or (
            expr.has_form("Association", None) and eval_AssociationQ(expr)
        ):
            return to_mathics_list(
                *expr.elements,
                elements_conversion_fn=lambda e: get_values_with_head(e, h),
            )
        else:
            evaluation.message("Values", "invrl", expr)
            raise TypeError

    try:
        return get_values_with_head(rules_or_association, head)
    except TypeError:
        return None


def eval_assocs_list_key(self, assocs, key, evaluation: Evaluation):
    """Lookup[assocs_List, key_]"""
    return eval_Lookup_assocs_list_key(assocs, key, None, evaluation)


def eval_assocs_list_key_default(self, assocs, key, default, evaluation: Evaluation):
    """Lookup[assocs_List, key_, default_]"""
    return eval_Lookup_assocs_list_key(assocs, key, default, evaluation)
