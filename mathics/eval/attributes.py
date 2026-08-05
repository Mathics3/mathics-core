"""
Evaluation functions for builtins in mathics.core.builtin.attributes
"""

from mathics.core.attributes import attributes_bitset_to_list
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol


def eval_Attributes(name_symbol, evaluation: Evaluation):
    name = name_symbol.get_lookup_name()

    attributes = attributes_bitset_to_list(evaluation.definitions.get_attributes(name))
    attributes_symbols = [Symbol(attribute) for attribute in attributes]
    return ListExpression(*attributes_symbols)
