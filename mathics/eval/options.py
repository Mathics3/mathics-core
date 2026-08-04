"""
Evaluation functions for mathics.builtin.options
"""

from typing import Optional

from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer1
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolNone, SymbolRuleDelayed


def eval_Options(
    symbol: Symbol, evaluation: Evaluation, empty_is_none: bool = False
) -> Optional[ListExpression]:
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
        result.append(Expression(SymbolRuleDelayed, Symbol(option), value))
    if not result and empty_is_none:
        return SymbolNone
    return ListExpression(*result)


def eval_Option_with_names(
    symbol: Symbol, name, evaluation: Evaluation
) -> Optional[ListExpression]:
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
        result.append(Expression(SymbolRuleDelayed, Symbol(option), value))
    return ListExpression(*result)
