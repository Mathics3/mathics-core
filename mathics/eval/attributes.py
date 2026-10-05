"""
Evaluation functions for builtins in mathics.core.builtin.attributes
"""

from typing import Callable, Optional

from mathics.core.assignment import get_symbol_list
from mathics.core.attributes import (
    A_LOCKED,
    attribute_string_to_number,
    attributes_bitset_to_list,
)
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolNull


def eval_Attributes(name_symbol, evaluation: Evaluation):
    name = name_symbol.get_symbol_definition_name()

    attributes = attributes_bitset_to_list(evaluation.definitions.get_attributes(name))
    attributes_symbols = [Symbol(attribute) for attribute in attributes]
    return ListExpression(*attributes_symbols)


def attributes_to_bitcode(
    attrs: BaseElement, callback: Callable, stop_on_failure=True
) -> Optional[int]:
    """Convert a list of attribute names into a bitcode"""
    attr_names = get_symbol_list(
        attrs,
        callback,
        valid_name=lambda x: x,
        stop_on_failure=stop_on_failure,
    )
    if attr_names is None:
        return None

    result = 0
    for value in attr_names:
        try:
            result |= attribute_string_to_number[value]
        except KeyError:
            callback(value)
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
            return defs.get_definition(defs.lookup_name(item), only_if_exists=True).name
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
        return evaluation.message("ClearAttributes", "sym", item, 1)

    def wrong_attribute(item):
        return evaluation.message("ClearAttributes", "sym", item, 2)

    def definition_name(item: str) -> Optional[str]:
        try:
            return defs.get_definition(defs.lookup_name(item), only_if_exists=True).name
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
