"""
Evaluation functions for builtins in mathics.core.builtin.attributes
"""

from mathics.core.atoms import String
from mathics.core.attributes import attributes_bitset_to_list
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol


def eval_Attributes(expr, evaluation: Evaluation):
    if isinstance(expr, String):
        expr = Symbol(expr.value)
    name = expr.get_lookup_name()

    attributes = attributes_bitset_to_list(evaluation.definitions.get_attributes(name))
    attributes_symbols = [Symbol(attribute) for attribute in attributes]
    return ListExpression(*attributes_symbols)
