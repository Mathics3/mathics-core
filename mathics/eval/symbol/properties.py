"""
Evaluation routines for builtin function in mathics.core.builtin.symbol.properties.
"""

from functools import cache
from typing import Final

from mathics.core.atoms import String
from mathics.core.attributes import A_READ_PROTECTED
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolMissing,
    SymbolNone,
    SymbolUnknownProperty,
    SymbolUnknownSymbol,
)
from mathics.eval.assignments.upvalues import eval_UpValues
from mathics.eval.attributes import eval_Attributes
from mathics.eval.options import eval_Options

ALL_PROPERTIES: Final[ListExpression] = ListExpression(
    # The ordering below is the ordering WMA reports when asking for a list of
    # Properties.
    String("Usage"),
    String("Ownvalues"),
    String("UpValues"),
    String("DownValues"),
    String("SubValues"),
    String("Formatalues"),
    String("Options"),
    String("Attributes"),
    String("FullName"),
)


def eval_Information_with_property(expr, property: str, evaluation: Evaluation):
    # FIXME: start here.
    match property:
        case "Attributes":
            return eval_Attributes(expr, evaluation)
        case "DownValues":
            return information_downvalues(expr, evaluation.definitions)
        case "FullName":
            return information_fullname(expr)
        case "Options":
            return eval_Options(expr, evaluation)
        case "OwnValues":
            # return eval_OwnValues(expr, evaluation)
            return eval_Options(expr, evaluation)
        case "Properties":
            return ALL_PROPERTIES
        case "SubValues":
            # return eval_SubValues(expr, evaluation)
            return eval_UpValues(expr, evaluation)
        case "FormatValues":
            # return eval_FormatValues(expr, evaluation)
            return eval_UpValues(expr, evaluation)
        case "UpValues":
            return eval_UpValues(expr, evaluation)
        case _:
            return missing_property(property)
    return


# FIXME write/use eval_Downvalues
def information_downvalues(symbol: Symbol, definitions):
    name = definitions.lookup_name(symbol.name)
    try:
        definition = definitions.get_definition(name, only_if_exists=True)
    except KeyError:
        return SymbolNone

    attributes = definition.attributes
    if not A_READ_PROTECTED & attributes:
        return SymbolNone
    downvalues = definition.downvalues()
    return SymbolNone if downvalues is None else downvalues


# FIXME there should be an eval_Fullname for this.
def information_fullname(symbol: Symbol):
    return String(symbol)


@cache
def missing_property(property) -> Expression:
    return Expression(SymbolMissing, SymbolUnknownProperty, Symbol(property))


@cache
def missing_symbol(expression) -> Expression:
    return Expression(SymbolMissing, SymbolUnknownSymbol, expression)


# The stuff below is from old Mathics code and needs to be revised
# and rewritten.

# def gather_and_format_definition_rules(
#     symbol: Symbol, evaluation: Evaluation
# ) -> Optional[list[Expression]]:
#     """Return a list of lines describing the definition of `symbol`"""
#     lines = []

#     def rhs_format(expr):
#         if expr.has_form("Infix", None):
#             expr = Expression(Expression(SymbolHoldForm, expr.head), *expr.elements)
#         return expr

#     def format_rule(
#         rule: RewriteRule,
#         up: bool = False,
#         lhs: Callable = lambda k: k,
#         rhs: Callable = lambda r: r,
#     ):
#         """
#         Add a line showing `rule`
#         """
#         evaluation.check_stopped()
#         if isinstance(rule, RewriteRule):
#             lhs_pat = Expression(SymbolInputForm, lhs(rule.pattern.expr))
#             repl_expr = rhs(
#                 rule.replace.replace_vars(
#                     {"System`Definition": Expression(SymbolHoldForm, SymbolDefinition)}
#                 )
#             )
#             repl_expr = Expression(SymbolInputForm, repl_expr)
#             lines.append(
#                 Expression(
#                     SymbolHoldForm,
#                     Expression(up and SymbolUpSet or SymbolSet, lhs_pat, repl_expr),
#                 )
#             )

#     def gather_rules(definition: Definition):
#         """
#         Add to the description all the rules associated
#         to a definition object
#         """
#         for rule in definition.ownvalues:
#             format_rule(rule)
#         for rule in definition.downvalues:
#             format_rule(rule)
#         for rule in definition.subvalues:
#             format_rule(rule)
#         for rule in definition.upvalues:
#             format_rule(rule, up=True)
#         for rule in definition.nvalues:
#             format_rule(rule)
#         formats = sorted(definition.formatvalues.items())
#         for form_name, rules in formats:
#             for rule in rules:

#                 def lhs_format(expr):
#                     return Expression(SymbolFormat, expr, Symbol(form_name))

#                 format_rule(rule, lhs=lhs_format, rhs=rhs_format)

#     name = symbol.get_name()
#     if not name:
#         evaluation.message("Definition", "sym", symbol, 1)
#         return

#     try:
#         all = evaluation.definitions.get_definition(name)
#         attributes = all.attributes
#         all_options = all.options
#         all_defaultvalues = all.defaultvalues

#         if attributes:
#             attributes_list = attributes_bitset_to_list(attributes)
#             lines.append(
#                 Expression(
#                     SymbolHoldForm,
#                     Expression(
#                         SymbolSet,
#                         Expression(SymbolAttributes, symbol),
#                         to_mathics_list(
#                             *attributes_list, elements_conversion_fn=Symbol
#                         ),
#                     ),
#                 )
#             )
#     except KeyError:
#         attributes = 0
#         all_options = {}
#         all_defaultvalues = []

#     if not A_READ_PROTECTED & attributes:
#         try:
#             gather_rules(evaluation.definitions.get_user_definition(name, create=False))
#         except KeyError:
#             pass

#     for rule in all_defaultvalues:
#         format_rule(rule)
#     if all_options:
#         options = sorted(all_options.items())
#         lines.append(
#             Expression(
#                 SymbolHoldForm,
#                 Expression(
#                     SymbolSet,
#                     Expression(SymbolOptions, symbol),
#                     ListExpression(
#                         *(
#                             Expression(SymbolRule, Symbol(name), value)
#                             for name, value in options
#                         )
#                     ),
#                 ),
#             )
#         )
#     return lines


# def build_list_of_matching_symbols(
#     self, symbol_pat: str, evaluation: Evaluation, options: dict, grid: bool = True
# ):
#     """Return a list of symbols compatible with symbol_pat"""
#     definitions = evaluation.definitions
#     names = definitions.get_matching_names(symbol_pat)
#     if len(names) == 1:
#         return self.format_information_symbol(
#             Symbol(definitions.lookup_name(names[0])), evaluation, options
#         )
#     rows = []
#     curr_row = []
#     for name in names:
#         curr_row.append(String(definitions.shorten_name(name)))
#         if len(curr_row) == 3:
#             rows.append(ListExpression(*curr_row))
#             curr_row = []
#     if curr_row:
#         curr_row = curr_row + (3 - len(curr_row)) * [String("")]
#         rows.append(ListExpression(*curr_row))

#     # Build Association with Information fields for each matching symbol
#     associations = []
#     for name in names:
#         symbol = Symbol(definitions.lookup_name(name))

#         # Get symbol definition to extract attributes and values
#         try:
#             definition = definitions.get_definition(name)
#         except KeyError:
#             definition = None

#         # Extract components for Association
#         assoc_items = [
#             Expression(SymbolRule, String("FullName"), String(name)),
#         ]

#         # Add Attributes
#         if definition and definition.attributes:
#             attributes_list = attributes_bitset_to_list(definition.attributes)
#             assoc_items.append(
#                 Expression(
#                     SymbolRule,
#                     String("Attributes"),
#                     to_mathics_list(
#                         *attributes_list, elements_conversion_fn=Symbol
#                     ),
#                 )
#             )

#         # Add Definitions (downvalues, ownvalues, upvalues)
#         definition_rules = gather_and_format_definition_rules(symbol, evaluation)
#         if definition_rules:
#             assoc_items.append(
#                 Expression(
#                     SymbolRule,
#                     String("Definitions"),
#                     ListExpression(*definition_rules),
#                 )
#             )

#         # Add OwnValues
#         ownvalues = get_symbol_values(symbol, "OwnValues", "ownvalues", evaluation)
#         if ownvalues:
#             assoc_items.append(
#                 Expression(SymbolRule, String("OwnValues"), ownvalues)
#             )

#         # Add DownValues
#         downvalues = get_symbol_values(
#             symbol, "DownValues", "downvalues", evaluation
#         )
#         if downvalues:
#             assoc_items.append(
#                 Expression(SymbolRule, String("DownValues"), downvalues)
#             )

#         associations.append(Expression(SymbolAssociation, *assoc_items))

#     result = ListExpression(*associations)
#     return result
