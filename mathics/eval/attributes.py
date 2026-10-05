"""
Evaluation functions for builtins in mathics.core.builtin.attributes
"""

from typing import Callable, Optional

from mathics.core.assignment import get_symbol_list
from mathics.core.atoms import String
from mathics.core.attributes import (
    A_LOCKED,
    A_NO_ATTRIBUTES,
    attribute_string_to_number,
    attributes_bitset_to_list,
)
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolNull
from mathics.core.systemsymbols import SymbolFailed, SymbolHoldPattern


def eval_Attributes(name_symbol, evaluation: Evaluation):
    name = name_symbol.get_symbol_definition_name()

    attributes = attributes_bitset_to_list(evaluation.definitions.get_attributes(name))
    attributes_symbols = [Symbol(attribute) for attribute in attributes]
    return ListExpression(*attributes_symbols)


def attributes_to_bitcode(
    attrs: BaseElement,
    message_callback: Callable,
    valid_name: Callable = lambda x: x,
    stop_on_failure=True,
) -> Optional[int]:
    """Convert a list of attribute names into a bitcode"""
    attr_names = get_symbol_list(
        attrs,
        message_callback,
        valid_name=valid_name,
        stop_on_failure=stop_on_failure,
    )
    if attr_names is None:
        return None

    result = 0
    for value in attr_names:
        try:
            result |= attribute_string_to_number[value]
        except KeyError:
            message_callback(value)
            if stop_on_failure:
                return None
    return result


def eval_ClearAttributes(symbols, attributes, evaluation: Evaluation):
    """ClearAttributes[symbols_, attributes_]"""
    defs = evaluation.definitions

    def wrong_symbol(item: str):
        evaluation.message("ClearAttributes", "sym", item, 1)

    def wrong_attribute(item: str):
        evaluation.message("ClearAttributes", "sym", item, 2)

    def definition_name(item: str) -> Optional[str]:
        try:
            return defs.get_definition(item, only_if_exists=True).name
        except KeyError:
            wrong_symbol(item)
            return None

    # Process values
    attr_mask = attributes_to_bitcode(attributes, wrong_attribute)
    if attr_mask is None:
        return

    attr_mask = ~attr_mask

    # Process symbols
    symbols = get_symbol_list(
        symbols,
        wrong_symbol,
        valid_name=definition_name,
        stop_on_failure=False,
    )
    for symbol in symbols:
        definition = defs.get_user_definition(symbol)
        if definition.attributes & A_LOCKED:
            evaluation.message("ClearAttributes", "locked", Symbol(symbol))
            continue
        definition.attributes &= attr_mask
        defs.mark_changed(definition)
        defs.clear_definitions_cache(symbol)
    return SymbolNull


def eval_SetAttributes(symbols, attributes, evaluation: Evaluation):
    """SetAttributes[symbols_, attributes_]"""
    defs = evaluation.definitions

    def wrong_symbol(item):
        evaluation.message("SetAttributes", "sym", item, 1)

    def wrong_attribute(item):
        evaluation.message("SetAttributes", "sym", item, 2)

    def definition_name(item: str) -> Optional[str]:
        try:
            return defs.get_definition(item, only_if_exists=True).name
        except KeyError:
            wrong_symbol(item)
            return None

    # Process values
    attr_mask = attributes_to_bitcode(attributes, wrong_attribute)

    if attr_mask is None:
        return
    symbols = get_symbol_list(
        symbols,
        wrong_symbol,
        valid_name=definition_name,
        stop_on_failure=False,
    )
    for symbol in symbols:
        definition = defs.get_user_definition(symbol)
        if definition.attributes & A_LOCKED:
            evaluation.message("ClearAttributes", "locked", Symbol(symbol))
            continue
        definition.attributes |= attr_mask
        defs.mark_changed(definition)
        defs.clear_definitions_cache(symbol)
    return SymbolNull


def eval_SetOperator_Attributes(
    symb, rhs, is_delayed: bool, evaluation: Evaluation
) -> BaseElement:
    # Indepentently of the success, if this is called from an non-delayed set operator
    # return the rhs. For Delayed operators, return SymbolNull on success, and
    # SymbolFailed on errors.
    # Determine the default case:
    default_result = SymbolFailed if is_delayed else rhs
    defs = evaluation.definitions

    ## Determine the attributes to set

    # If one of the attributes in the RHS is wrong, the assignment fails.
    # Notice that this is different to what happens with SetAttributes.
    def valid_name(name):
        evaluation.message("Attributes", "attnf", name)
        return None

    attributes: Optional[int] = attributes_to_bitcode(
        rhs,
        lambda item: evaluation.message("Attributes", "attnf", item),
        valid_name=valid_name,
    )
    if attributes is None:
        return default_result

    # Determine the target definition:
    if isinstance(symb, Symbol):
        tag = symb.name
    elif isinstance(symb, String):
        try:
            tag = defs.get_definition(symb.value, only_if_exists=True).name
        except KeyError:
            evaluation.message("Attributes", "notfound", symb)
            return default_result
    elif symb.has_form(SymbolHoldPattern, 1):
        symb = symb.elements[0]
        if isinstance(symb, Symbol):
            tag = symb.name
        else:
            evaluation.message("Attributes", "fnsym", symb)
            return default_result
    else:
        evaluation.message("Attributes", "fnsym", symb)
        return default_result

    definition = defs.get_definition(tag)
    if A_LOCKED & definition.attributes:
        evaluation.message("Attributes", "locked", Symbol(tag))
        return default_result

    definition.attributes = attributes
    defs.mark_changed(definition)
    defs.clear_definitions_cache(tag)

    if default_result is SymbolFailed:
        return SymbolNull
    return default_result


def eval_Unset_Attributes(symb, evaluation: Evaluation) -> BaseElement:
    """Attributes[symb]=."""
    defs = evaluation.definitions

    # Determine the target definition:
    if isinstance(symb, Symbol):
        tag = symb.name
    elif isinstance(symb, String):
        try:
            tag = defs.get_definition(symb.value, only_if_exists=True).name
        except KeyError:
            evaluation.message("Attributes", "notfound", symb)
            return SymbolFailed
    elif symb.has_form(SymbolHoldPattern, 1):
        symb = symb.elements[0]
        if isinstance(symb, Symbol):
            tag = symb.name
        else:
            evaluation.message("Attributes", "fnsym", symb)
            return SymbolFailed
    else:
        evaluation.message("Attributes", "fnsym", symb)
        return SymbolFailed

    definition = defs.get_definition(tag)
    if A_LOCKED & definition.attributes:
        evaluation.message("Attributes", "locked", Symbol(tag))
        return SymbolFailed

    definition.attributes = A_NO_ATTRIBUTES
    defs.mark_changed(definition)
    defs.clear_definitions_cache(tag)

    return SymbolNull
