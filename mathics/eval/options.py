from typing import Optional

from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer1
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRuleDelayed


def eval_Options(f, evaluation: Evaluation) -> Optional[ListExpression]:
    name = f.get_name()
    if not name:
        if isinstance(f, Image):
            # FIXME ColorSpace, MetaInformation
            options = f.metadata
        else:
            evaluation.message("Options", "sym", f, Integer1)
            return
    else:
        options = evaluation.definitions.get_options(name)
    result = []
    for option, value in sorted(options.items(), key=lambda item: item[0]):
        # Don't use HoldPattern, since the returned List should be
        # assignable to Options again!
        result.append(Expression(SymbolRuleDelayed, Symbol(option), value))
    return ListExpression(*result)
