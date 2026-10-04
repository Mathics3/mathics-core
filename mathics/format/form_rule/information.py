from typing import Callable, Optional

from mathics_scanner.tokeniser import NAMES_WILDCARDS

from mathics.core.atoms import String
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolGrid, SymbolLeft, SymbolRule
from mathics.doc.online import online_doc_string
from mathics.eval.symbol.properties import eval_Definition


def format_information_generic(
    expr: BaseElement,
    evaluation: Evaluation,
    grid: bool = True,
):
    "(StandardForm,TraditionalForm,InputForm,OutputForm,): Information[expr_, OptionsPattern[Information]]"
    # expr is not a Symbol. We should leave unchanged and let other formatting rules kick in.
    return None


def format_information_string(
    self, strpat: String, evaluation: Evaluation, options: dict, grid: bool = True
) -> Expression | Symbol:
    "(StandardForm,TraditionalForm,InputForm,OutputForm,): Information[strpat_String, OptionsPattern[Information]]"
    definitions = evaluation.definitions
    string_str = strpat.value
    if any(char in string_str for char in NAMES_WILDCARDS):
        return self.build_list_of_matching_symbols(
            string_str, evaluation, options, grid
        )
    try:
        symbol_name = definitions.get_definition(string_str, only_if_exists=True).name
    except KeyError:
        return self.build_missing(strpat)
    return self.format_information_symbol(Symbol(symbol_name), evaluation, options)


def format_information_symbol(
    self, symbol: Symbol, evaluation: Evaluation, options: dict, grid: bool = True
) -> Expression | Symbol:
    "(StandardForm,TraditionalForm,InputForm,OutputForm,): Information[symbol_Symbol, OptionsPattern[Information]]"
    definitions = evaluation.definitions
    try:
        definitions.get_definition(symbol.name, True)
    except KeyError:
        return self.build_missing(symbol)

    lines: list[Expression | String] = []
    # Print the "usage" message if available.
    # is_long_form = self.get_option(options, "LongForm", evaluation).to_python()
    is_long_form = True  # In WMA >=12.0 this option does not make much difference--
    usagetext = online_doc_string(symbol, evaluation.definitions, is_long_form)
    if usagetext:
        lines.append(String(usagetext))
    else:
        lines.append(String(symbol.get_name()))

    if is_long_form and (info := eval_Definition(symbol, evaluation)):
        lines.extend(info)

    infoshow = Expression(
        SymbolGrid,
        ListExpression(*(line for line in lines)),
        Expression(SymbolRule, Symbol("ColumnAlignments"), SymbolLeft),
    )
    return infoshow
