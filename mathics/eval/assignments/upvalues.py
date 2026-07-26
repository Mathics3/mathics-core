from mathics.core.assignment import get_symbol_values
from mathics.core.atoms import Integer1, String
from mathics.core.evaluation import Evaluation
from mathics.core.symbols import Symbol


def eval_UpValues(symbol, evaluation: Evaluation):
    "UpValues[symbol_]"

    # FIXME: Do we have to worry about the ReadProtected attribute?
    # attributes = definition.attributes
    # if not A_READ_PROTECTED & attributes:
    #   return SymbolNone

    if isinstance(symbol, String):
        symbol = Symbol(symbol.value)

    # FIXME: Do we have to worry about returning SymbolNone?
    return get_symbol_values(symbol, "UpValues", "upvalues", evaluation)
