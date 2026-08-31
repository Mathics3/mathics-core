"""
Evaluation functions for mathics.builtin.options
"""

from typing import Optional

from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer1, String
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolNone, SymbolRule


def eval_Options(
    symbol: Symbol, evaluation: Evaluation, empty_is_none: bool = False
) -> Optional[ListExpression] | Symbol:
    name = symbol.get_name()
    if not name:
        if isinstance(symbol, Image):
            # FIXME ColorSpace, MetaInformation
            options = symbol.metadata
        else:
            evaluation.message("Options", "sym", symbol, Integer1)
            return
    else:
        options = evaluation.definitions.get_options(name)
    result = []
    for option, value in sorted(options.items(), key=lambda item: item[0]):
        # Don't use HoldPattern, since the returned List should be
        # assignable to Options again!
        result.append(Expression(SymbolRule, Symbol(option), value))
    if not result and empty_is_none:
        return SymbolNone
    return ListExpression(*result)


def eval_Option_with_names(
    symbol: Symbol, option_name, evaluation: Evaluation
) -> Optional[ListExpression]:
    if not option_name:
        if isinstance(symbol, Image):
            # FIXME ColorSpace, MetaInformation
            options = symbol.metadata
        else:
            evaluation.message("Options", "sym", symbol, Integer1)
            return
    else:
        # Check if passed name
        options = evaluation.definitions.get_options(symbol.name)
        if isinstance(option_name, String):
            option_str = evaluation.definitions.lookup_name(option_name.value)
        elif isinstance(option_name, Symbol):
            option_str = option_name.name
        else:
            # ???
            return

        if value := options.get(option_str):
            return ListExpression(Expression(SymbolRule, option_name, value))
        else:
            evaluation.message("Options", "optnf", option_name, symbol)
            return
    result = []
    for option, value in sorted(options.items(), key=lambda item: item[0]):
        # Don't use HoldPattern, since the returned List should be
        # assignable to Options again!
        result.append(Expression(SymbolRule, Symbol(option), value))
    return ListExpression(*result)
