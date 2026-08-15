"""
Evaluation routines for builtin function in mathics.core.builtin.symbol.properties.
"""

from functools import cache
from typing import Final

from mathics.core.assignment import get_symbol_values
from mathics.core.atoms import String
from mathics.core.atoms.associations import (
    Association,
    association_from_mathics3_kv_dict,
)
from mathics.core.attributes import A_READ_PROTECTED
from mathics.core.convert.python import association_from_dict
from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import RewriteRule
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolAttributes,
    SymbolDownValues,
    SymbolInformationData,
    SymbolInformationDataGrid,
    SymbolMessageName,
    SymbolMissing,
    SymbolNone,
    SymbolNValues,
    SymbolOptions,
    SymbolOwnValues,
    SymbolSubValues,
    SymbolUnknownProperty,
    SymbolUnknownSymbol,
    SymbolUpValues,
)
from mathics.doc.online import get_builtin_class, get_builtin_documentation
from mathics.eval.attributes import eval_Attributes
from mathics.eval.options import eval_Options

ALL_PROPERTIES: Final[ListExpression] = ListExpression(
    String("Attributes"),
    String("DefaultValues"),
    String("Definitions"),
    String("Documentation"),
    String("DownValues"),
    String("FormatValues"),
    String("FullName"),
    String("NValues"),
    String("ObjectType"),
    String("Options"),
    String("Ownvalues"),
    String("SubValues"),
    String("UpValues"),
    String("Usage"),
)


def eval_Information(name, evaluation: Evaluation):
    """
    Evaluation routine for: Information[name]
    """
    if isinstance(name, String):
        names: list[str] = get_matching_names(name.value, evaluation)
        if len(names) > 1:
            return Expression(SymbolInformationDataGrid, *[String(n) for n in names])
        name_symbol = Symbol(names[0])
    elif isinstance(name, Symbol):
        name_symbol = name
    else:
        return None
    # name is now a Symbol
    name_str = name_symbol.name
    info_data = {
        Symbol("ObjectType"): String("Symbol"),
        Symbol("Usage"): information_usage(
            name_symbol, name_str, evaluation.definitions
        ),
        Symbol("Documentation"): information_documentation(
            name_str, evaluation.definitions
        ),
        Symbol("FullName"): String(name_str),
        SymbolAttributes: eval_Attributes(name, evaluation),
        SymbolOptions: eval_Options(name_symbol, evaluation, empty_is_none=True),
        Symbol("DefaultValues"): information_values(
            name_symbol, name_str, evaluation, "DefaultValues"
        ),
        SymbolDownValues: information_values(
            name_symbol, name_str, evaluation, "DownValues"
        ),
        Symbol("FormatValues"): information_values(
            name_symbol, name_str, evaluation, "FormatValues"
        ),
        SymbolNValues: information_values(name_symbol, name_str, evaluation, "NValues"),
        SymbolOwnValues: information_values(
            name_symbol, name_str, evaluation, "OwnValues"
        ),
        SymbolSubValues: information_values(
            name_symbol, name_str, evaluation, "SubValues"
        ),
        SymbolUpValues: information_values(
            name_symbol, name_str, evaluation, "UpValues"
        ),
    }
    association: Association = association_from_mathics3_kv_dict(info_data)
    return Expression(SymbolInformationData, association)


def eval_Information_with_property(name, property_name: str, evaluation: Evaluation):
    """
    Evaluation routine for: Information[name, property]

    We do not handle:
       * Knowledgebase Entity,
       * Resource Function or
       * a Fitted Module Object.
    """

    # If "name" is String, look up the name to get its Symbol.
    if isinstance(name, String):
        name_symbol = Symbol(evaluation.definitions.lookup_name(name.value))
    elif isinstance(name, Symbol):
        name_symbol = name
    else:
        # We only handle Symbols and Strings for now.
        return None

    # Symbol's "name" field should have the fully qualified string value.
    # This full-qualified string value (not its short name),
    # is used in various property subroutines.
    name_str = name_symbol.name

    match property_name:
        case "Attributes":
            return eval_Attributes(name_symbol, evaluation)
        case (
            "DefaultValues"
            | "DownValues"
            | "FormatValues"
            | "NValues"
            | "OwnValues"
            | "SubValues"
            | "UpValues"
        ):
            return information_values(name_symbol, name_str, evaluation, property_name)
            # case "Definitions":
            #     return information_values(expr, evaluation.definitions, "defaultvalues")
        case "Documentation":
            return information_documentation(name_str, evaluation.definitions)
        case "FullName":
            return String(name_str)
        case "ObjectType":
            # This needs filling out when we handle Knowledgebase Entity, etc
            # return information_object_type(name_symbol, name_str, evaluation.definitions)
            return information_object_type()
        case "Options":
            name_symbol = (
                Symbol(evaluation.definitions.lookup_name(name_str))
                if isinstance(name, String)
                else name
            )
            return eval_Options(name_symbol, evaluation, empty_is_none=True)
        case "Properties":
            # TODO: The property names change depending on "name"
            # However for now we do not handle Knowledgebase Entity,
            # Resource Function or a Fitted Module Object.
            # So for now, we can return a static list.
            return ALL_PROPERTIES
        case "Usage":
            return information_usage(name_symbol, name_str, evaluation.definitions)
        case _:
            return missing_property(property_name)


def eval_values(name, evaluation: Evaluation, attribute: str):
    """
    Evaluation function for xxxValues, e.g. DownValues, UpValues, ...
    """
    # If "name" is String, look up the name to get its Symbol.
    if isinstance(name, String):
        name_symbol = Symbol(evaluation.definitions.lookup_name(name.value))
    elif isinstance(name, Symbol):
        name_symbol = name
    else:
        # We only handle Symbols and Strings.
        return None

    return get_symbol_values(name_symbol, attribute, attribute.lower(), evaluation)


def get_matching_names(symbol_pat: str, evaluation: Evaluation) -> list[str]:
    """Return a list of symbols in eval.definitions matching `symbol_pat`"""
    return evaluation.definitions.get_matching_names(symbol_pat)


def information_documentation(
    name_str: str, definitions: Definitions
) -> Association | Symbol:
    """
    Informaton[symbol, "Documentation"]

    Retrieve symbol's usage URL.

    Parameters
    ----------
    name_str : str
        The symbol that we want "usage" for
    definitions : Definitions
        definitions The evaluation object.

    Returns
    -------
    Association or None
        An association whose values are URLs and the key is some indication of what that URL is for,
        e.g. Web (WMA documentation), Wiki, SymPy, NumPy, etc.
    """

    builtin_class = get_builtin_class(name_str, definitions)
    if builtin_class:
        return get_builtin_documentation(builtin_class)
    return SymbolNone


def information_object_type() -> String:
    """
    Information[symbol, "ObjectType"]

    Parameters
    ----------
    name_str : str
        The symbol that we want "usage" for
    definitions : Definitions
        definitions The evaluation object.

    Returns
    -------
    String "Symbol" for now.

    """

    # For now, we do not distinguish, "Entity", "ResourceFunction", or "DeviceObject"]
    return String("Symbol")


def information_usage(
    name_symbol: Symbol, name_str: str, definitions: Definitions
) -> String:
    """Retrieve symbol's usage message string.

    For user variables, use "usage" message value stored.

    For builtin functions, when "usage" message does not exist, which is probably most of the time,
    for now, we return the "summary_text" class value of the builtin function..

    Parameters
    ----------
    name_symbol : Symbol
        The symbol that we want "usage" for
    name_str : str
        The Python str value for name_symbol. This string has the full context in it.
    definitions : Definitions
        definitions The evaluation object.

    Returns
    -------
    String or Symbol
        The usage string if one exists or the symbol name no usage string.

    """

    definition = definitions.get_definition(name_str)
    if not definition:
        # Definition not found
        return name_symbol

    for rule in definition.get_values_list("messages"):
        if isinstance(rule, RewriteRule) and rule.lhs.get_head() is SymbolMessageName:
            return rule.rhs

    # No "usage" message has been defined on this symbol definition.
    # If the symbol is a builtin-funciton, we should be able to get the "summary_text"
    # value from the Python builtin class that defines the Builtin Function.
    if builtin_class := get_builtin_class(name_str, definitions):
        # I, rocky, take full responsibility for propagating
        # "summary_text", which at the time matched the crappy
        # Django homegrown documentation better.
        return String(builtin_class.summary_text)

    return String(name_symbol)


def information_values(name_symbol: Symbol, name_str: str, evaluation, value_type: str):
    """
    Evaluation function for Information[name, <value_type>Values].
    This is similar to eval_values, however the results change slightly
     1. 'None' returned in the key is not found
     2. The READ_PROTECTED attribute is is respected
     3. Empty values return 'None' instead of {}.

    """

    definitions = evaluation.definitions
    try:
        definition = definitions.get_definition(name_str, only_if_exists=True)
    except KeyError:
        return SymbolNone

    attributes = definition.attributes
    if not A_READ_PROTECTED & attributes:
        return SymbolNone
    values = get_symbol_values(name_symbol, value_type, value_type.lower(), evaluation)
    return SymbolNone if not values else values


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
