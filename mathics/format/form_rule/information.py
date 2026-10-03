from typing import Callable, Optional

from mathics_scanner.tokeniser import NAMES_WILDCARDS

from mathics.core.atoms import String
from mathics.core.attributes import A_READ_PROTECTED, attributes_bitset_to_list
from mathics.core.convert.expression import to_mathics_list
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import RewriteRule
from mathics.core.symbols import Symbol, SymbolUpSet
from mathics.core.systemsymbols import (
    SymbolAttributes,
    SymbolDefinition,
    SymbolFormat,
    SymbolGrid,
    SymbolHoldForm,
    SymbolInfix,
    SymbolInputForm,
    SymbolLeft,
    SymbolOptions,
    SymbolRule,
    SymbolSet,
)
from mathics.doc.online import online_doc_string


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

    if is_long_form and (
        info := gather_and_format_definition_rules(symbol, evaluation)
    ):
        lines.extend(info)

    infoshow = Expression(
        SymbolGrid,
        ListExpression(*(line for line in lines)),
        Expression(SymbolRule, Symbol("ColumnAlignments"), SymbolLeft),
    )
    return infoshow


# FIXME: gather_and_format_definition_rules is crap and needs to be revised, rewritten and put in
# mathics.eval.symbols.properties
def gather_and_format_definition_rules(
    symbol: Symbol, evaluation: Evaluation
) -> Optional[list[Expression]]:
    """Return a list of lines describing the definition of `symbol`"""
    lines = []

    def rhs_format(expr):
        if expr.has_form(SymbolInfix, None):
            expr = Expression(Expression(SymbolHoldForm, expr.head), *expr.elements)
        return expr

    def format_rule(
        rule: RewriteRule,
        up: bool = False,
        lhs: Callable = lambda k: k,
        rhs: Callable = lambda r: r,
    ):
        """
        Add a line showing `rule`
        """
        evaluation.check_stopped()
        if isinstance(rule, RewriteRule):
            lhs_pat = Expression(SymbolInputForm, lhs(rule.pattern.expr))
            repl_expr = rhs(
                rule.replace.replace_vars(
                    {"System`Definition": Expression(SymbolHoldForm, SymbolDefinition)}
                )
            )
            repl_expr = Expression(SymbolInputForm, repl_expr)
            lines.append(
                Expression(
                    SymbolHoldForm,
                    Expression(up and SymbolUpSet or SymbolSet, lhs_pat, repl_expr),
                )
            )

    def gather_rules(definition):
        """
        Add to the description all the rules associated
        to a definition object
        """
        for rule in definition.ownvalues:
            format_rule(rule)
        for rule in definition.downvalues:
            format_rule(rule)
        for rule in definition.subvalues:
            format_rule(rule)
        for rule in definition.upvalues:
            format_rule(rule, up=True)
        for rule in definition.nvalues:
            format_rule(rule)
        formats = sorted(definition.formatvalues.items())
        for form_name, rules in formats:
            for rule in rules:

                def lhs_format(expr):
                    return Expression(SymbolFormat, expr, Symbol(form_name))

                format_rule(rule, lhs=lhs_format, rhs=rhs_format)

    name = symbol.get_name()
    if not name:
        evaluation.message("Definition", "sym", symbol, 1)
        return None

    try:
        all = evaluation.definitions.get_definition(name)
        attributes = all.attributes
        all_options = all.options
        all_defaultvalues = all.defaultvalues

        if attributes:
            attributes_list = attributes_bitset_to_list(attributes)
            lines.append(
                Expression(
                    SymbolHoldForm,
                    Expression(
                        SymbolSet,
                        Expression(SymbolAttributes, symbol),
                        to_mathics_list(
                            *attributes_list, elements_conversion_fn=Symbol
                        ),
                    ),
                )
            )
    except KeyError:
        attributes = 0
        all_options = {}
        all_defaultvalues = []

    if not A_READ_PROTECTED & attributes:
        try:
            gather_rules(evaluation.definitions.get_user_definition(name, create=False))
        except KeyError:
            pass

    for rule in all_defaultvalues:
        format_rule(rule)
    if all_options:
        options = sorted(all_options.items())
        lines.append(
            Expression(
                SymbolHoldForm,
                Expression(
                    SymbolSet,
                    Expression(SymbolOptions, symbol),
                    ListExpression(
                        *(
                            Expression(SymbolRule, Symbol(name), Symbol(value))
                            for name, value in options
                        )
                    ),
                ),
            )
        )
    return lines
