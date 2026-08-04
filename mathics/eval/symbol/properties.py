"""
Evaluation routines for builtin function in mathics.core.builtin.symbol.properties.
"""

from functools import cache
from typing import Final

from mathics.core.assignment import get_symbol_values
from mathics.core.atoms import String
from mathics.core.attributes import A_READ_PROTECTED
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.pattern import AtomPattern
from mathics.core.rules import RewriteRule
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolMessageName,
    SymbolMissing,
    SymbolNone,
    SymbolUnknownProperty,
    SymbolUnknownSymbol,
)
from mathics.eval.attributes import eval_Attributes
from mathics.eval.options import eval_Options

ALL_PROPERTIES: Final[ListExpression] = ListExpression(
    String("Attributes"),
    String("DefaultValues"),
    # String("Definitions"),
    String("DownValues"),
    String("FormatValues"),
    String("FullName"),
    String("NValues"),
    String("Options"),
    String("Ownvalues"),
    String("SubValues"),
    String("UpValues"),
    String("Usage"),
)


def eval_Information_with_property(expr, property: str, evaluation: Evaluation):
    match property:
        case "Attributes":
            return eval_Attributes(expr, evaluation)
        case (
            "DefaultValues"
            | "DownValues"
            | "FormatValues"
            | "NValues"
            | "OwnValues"
            | "SubValues"
            | "UpValues"
        ):
            return information_values(expr, evaluation, property)
            # case "Definitions":
            #     return information_values(expr, evaluation.definitions, "defaultvalues")
            return information_fullname(expr)
        case "Options":
            name_symbol = (
                Symbol(evaluation.definitions.lookup_name(expr.value))
                if isinstance(expr, String)
                else expr
            )
            return eval_Options(name_symbol, evaluation)
        case "Properties":
            return ALL_PROPERTIES
        case "Usage":
            return information_usage(expr, evaluation.definitions)
        case _:
            return missing_property(property)
    return


def eval_values(name: Symbol | String, evaluation: Evaluation, attribute: str):
    """
    Evaluation function for xxxValues, e.g. DownValues, UpValues, ...
    """
    name_symbol = (
        Symbol(evaluation.definitions.lookup_name(name.value))
        if isinstance(name, String)
        else name
    )
    return get_symbol_values(name_symbol, attribute, attribute.lower(), evaluation)


def information_values(name: Symbol | String, evaluation, value_type: str):
    """
    Evaluation function for Information[name, xxxValues].
    This is similar to eval_values, however the results change slightly
     1. 'None' returned in the key is not found
     2. The READ_PROTECTED attribute is is respected
     3. Empty values return 'None' instead of {}.

    """
    if isinstance(name, String):
        name_str = name.value
        name_symbol = Symbol(evaluation.definitions.lookup_name(name.value))
    else:
        name_str = name.name
        name_symbol = name

    definitions = evaluation.definitions
    name = definitions.lookup_name(name_str)
    try:
        definition = definitions.get_definition(name_str, only_if_exists=True)
    except KeyError:
        return SymbolNone

    attributes = definition.attributes
    if not A_READ_PROTECTED & attributes:
        return SymbolNone
    values = get_symbol_values(name_symbol, value_type, value_type.lower(), evaluation)
    return SymbolNone if not values else values


# FIXME there should be an eval_Fullname for this.
def information_fullname(symbol: Symbol) -> String:
    """
    Evaluation routine for Information[xxx, "FullName"]
    """
    return String(symbol)


def information_usage(name: Symbol | String, definitions: Definitions) -> String:
    """
    Retrieve symbol's usage message string.

    Parameters
    ----------
    symbol : Symbol
        The symbol that we want "usage" for
    definitions : Definitions
        definitions The evaluation object.

    Returns
    -------
    String
        The usage string if one exists or the symbol name no usage string.

    """
    if isinstance(name, String):
        name_symbol = Symbol(definitions.lookup_name(name.value))
        # Make sure we use fully qualified name, e.g. "System`AtomQ"
        # as opposed a shortname "AtomQ" that might have been given.
        name_str = name_symbol.name
    else:
        name_str = name.name
        name_symbol = name

    try:
        definition = definitions.get_user_definition(name_str, True)
    except KeyError:
        # As a last resort:
        return name_symbol

    for rule in definition.get_values_list("messages"):
        if isinstance(rule, RewriteRule) and isinstance(rule.lhs.head, AtomPattern):
            if rule.lhs.head.expr is SymbolMessageName:
                return rule.rhs

    # No "usage" message has been defined on this symbol definition.
    # If the symbol is a builtin-funciton, we should be able to get the "summary_text"
    # value from the Python builtin class that defines the Builtin Function.

    # I, rocky, take full responsibility for propagating
    # "summary_text", which at the time matched the crappy
    # Django homegrown documentation better.
    if (
        builtin_definition := definitions.builtin.get(name_str)
    ) and builtin_definition.downvalues:
        first_apply_rule = builtin_definition.downvalues[0]
        try:
            # FIXME: This is really weird and hoaky. Is there a better
            # way?  Fnd an apply rule for this builtin. From that take
            # the RHS of the rule, which gives a bound method of some
            # eval method. From the bound eval method we get the self
            # object from which we can find the Buitin class of the
            # object.  And then finally we take its summary text.
            # "summary_text" is the closest we have to "usage".
            return String(first_apply_rule.rhs.__self__.__class__.summary_text)
        except Exception:
            pass

    return name_symbol


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
