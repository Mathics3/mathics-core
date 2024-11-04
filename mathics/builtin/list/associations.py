# -*- coding: utf-8 -*-

"""
Associations

An Association maps keys to values and is similar to a dictionary in Python; \
it is often sparse in that their key space is much larger than the number of \
actual keys found in the collection.
"""


from mathics.builtin.box.layout import RowBox
from mathics.builtin.layout import Row
from mathics.core.atoms import Integer, String
from mathics.core.attributes import A_HOLD_ALL_COMPLETE, A_PROTECTED
from mathics.core.builtin import Builtin, Test
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolAssociation,
    SymbolHoldForm,
    SymbolInputForm,
    SymbolMakeBoxes,
    SymbolMathMLForm,
    SymbolMissing,
    SymbolOutputForm,
    SymbolStandardForm,
    SymbolTeXForm,
    SymbolTraditionalForm,
)
from mathics.eval.lists import list_boxes, riffle
from mathics.eval.makeboxes import do_format
from mathics.eval.strings import eval_ToString


class NotAnAssociationItem(Exception):
    pass


SymbolInterpretation = Symbol("System`Interpretation")

ASSOCIATION_DELIMITER_FORMATS = {
    SymbolInputForm: {"start": String("<|"), "sep": String(", "), "end": String("|>")},
    SymbolOutputForm: {"start": String("<|"), "sep": String(","), "end": String("|>")},
    SymbolStandardForm: {
        "start": String("<|"),
        "sep": String(","),
        "end": String("|>"),
    },
    SymbolTraditionalForm: {
        "start": String("<|"),
        "sep": String(","),
        "end": String("|>"),
    },
    SymbolTeXForm: {"start": String("<|"), "sep": String(", "), "end": String("|>")},
    SymbolMathMLForm: {"start": String("<|"), "sep": String(","), "end": String("|>")},
}


def format_association(rules: tuple, evaluation: Evaluation, form: Symbol):
    """Association[rules___]"""
    delimiters = ASSOCIATION_DELIMITER_FORMATS[form]

    def yield_rules(rule_tuple):
        for rule in rule_tuple:
            if rule.has_form(("Rule", "RuleDelayed"), 2):
                yield rule
            elif rule.has_form(
                (
                    "List",
                    "Association",
                ),
                None,
            ):
                for subrule in yield_rules(rule.elements):
                    yield subrule
            else:
                raise NotAnAssociationItem

    try:
        items = riffle(
            [do_format(rule, evaluation, form) for rule in yield_rules(rules)],
            delimiters["sep"],
        )
        return Row(to_mathics_list(delimiters["start"], *items, delimiters["end"]))
    except NotAnAssociationItem:
        return None


class Association(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Association.html</url>

    <dl>
      <dt>'Association[$key1$ -> $val1$, $key2$ -> $val2$, ...]'
      <dt>'<|$key1$ -> $val1$, $key2$ -> $val2$, ...|>'
      <dd> represents an association between keys and values.
    </dl>

    'Association' is the head of associations:
    >> Head[<|a -> x, b -> y, c -> z|>]
     = Association

    >> <|a -> x, b -> y|>
     = <|a -> x, b -> y|>

    >> Association[{a -> x, b -> y}]
     = <|a -> x, b -> y|>

    Associations can be nested:
    >> <|a -> x, b -> y, <|a -> z, d -> t|>|>
     = <|a -> z, b -> y, d -> t|>
    """

    error_idx = 0

    attributes = A_HOLD_ALL_COMPLETE | A_PROTECTED

    summary_text = "an association between keys and values"

    def format_association_input(self, rules, evaluation: Evaluation, expression):
        """InputForm: Association[rules___]"""
        print("format association input", rules)
        formatted = format_association(
            rules.get_sequence(), evaluation, SymbolInputForm
        )
        if formatted is None:
            return None
        print("   formatted elements:")
        elements = formatted.elements[0].elements
        for elem in elements:
            print("   ", elem)
        elems = tuple(
            (
                eval_ToString(elem, SymbolOutputForm, "unicode", evaluation).value
                for elem in elements
            )
        )
        elems = tuple((elem[1:-1] if elem[0] == '"' else elem for elem in elems))
        print("   elems", elems)
        result_str = "".join(elems)
        result = Expression(SymbolOutputForm, String(result_str))
        print("      result->", result)
        return result

    def format_association_output(self, rules, evaluation: Evaluation):
        """OutputForm: Association[rules___]"""
        return format_association(rules.get_sequence(), evaluation, SymbolOutputForm)

    def format_association_standard(self, rules, evaluation: Evaluation):
        """StandardForm: Association[rules___]"""
        return format_association(rules.get_sequence(), evaluation, SymbolStandardForm)

    def format_association_traditional(self, rules, evaluation: Evaluation):
        """TraditionalForm: Association[rules___]"""
        return format_association(
            rules.get_sequence(), evaluation, SymbolTraditionalForm
        )

    def format_association_tex(self, rules, evaluation: Evaluation):
        """TeXForm: Association[rules___]"""
        return format_association(rules.get_sequence(), evaluation, SymbolTeXForm)

    def format_association_mathml(self, rules, evaluation: Evaluation):
        """MathMLForm: Association[rules___]"""
        return format_association(rules.get_sequence(), evaluation, SymbolMathMLForm)

    def eval(self, rules, evaluation: Evaluation):
        "Association[rules__]"

        def make_flatten(exprs, rules_dictionary: dict = {}):
            for expr in exprs:
                if expr.has_form(("Rule", "RuleDelayed"), 2):
                    elements = expr.elements
                    key = elements[0].evaluate(evaluation)
                    value = elements[1].evaluate(evaluation)
                    rules_dictionary[key] = Expression(expr.get_head(), key, value)
                elif expr.has_form(("List", "Association"), None):
                    make_flatten(expr.elements, rules_dictionary)
                else:
                    raise TypeError
            return rules_dictionary.values()

        try:
            return Expression(SymbolAssociation, *make_flatten(rules.get_sequence()))
        except TypeError:
            return None

    def eval_key(self, rules, key, evaluation: Evaluation):
        "Association[rules__][key_]"

        def find_key(exprs, rules_dictionary: dict = {}):
            for expr in exprs:
                if expr.has_form(("Rule", "RuleDelayed"), 2):
                    if expr.elements[0] == key:
                        rules_dictionary[key] = expr.elements[1]
                elif expr.has_form(("List", "Association"), None):
                    find_key(expr.elements)
                else:
                    raise TypeError
            return rules_dictionary

        try:
            result = find_key(rules.get_sequence())
            return (
                result[key]
                if result
                else Expression(SymbolMissing, Symbol("KeyAbsent"), key)
            )
        except TypeError:
            return None


class AssociationQ(Test):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/AssociationQ.html</url>

    <dl>
      <dt>'AssociationQ[$expr$]'
      <dd>return True if $expr$ is a valid Association object, and False otherwise.
    </dl>

    >> AssociationQ[<|a -> 1, b :> 2|>]
     = True

    >> AssociationQ[<|a, b|>]
     = False
    """

    summary_text = "test if an expression is a valid association"

    def test(self, expr) -> bool:
        def validate(elements):
            for element in elements:
                if element.has_form(("Rule", "RuleDelayed"), 2):
                    pass
                elif element.has_form(("List", "Association"), None):
                    if not validate(element.elements):
                        return False
                else:
                    return False
            return True

        return expr.get_head_name() == "System`Association" and validate(expr.elements)


class Key(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Key.html</url>

    <dl>
      <dt>Key[$key$]
      <dd> represents a key used to access a value in an association.
      <dt>Key[$key$][$assoc$]
      <dd>
    </dl>
    """

    rules = {
        "Key[key_][assoc_Association]": "assoc[key]",
    }
    summary_text = "indicate a key within a part specification"


class Keys(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Keys.html</url>

    <dl>
      <dt>'Keys[<|$key1$ -> $val1$, $key2$ -> $val2$, ...|>]'
      <dd>return a list of the keys $keyi$ in an association.

      <dt>'Keys[{$key1$ -> $val1$, $key2$ -> $val2$, ...}]'
      <dd>return a list of the $keyi$ in a list of rules.
    </dl>

    >> Keys[<|a -> x, b -> y|>]
     = {a, b}

    >> Keys[{a -> x, b -> y}]
     = {a, b}

    Keys automatically threads over lists:
    >> Keys[{<|a -> x, b -> y|>, {w -> z, {}}}]
     = {{a, b}, {w, {}}}

    Keys are listed in the order of their appearance:
    >> Keys[{c -> z, b -> y, a -> x}]
     = {c, b, a}
    """

    attributes = A_PROTECTED

    messages = {
        "argx": "Keys called with `1` arguments; 1 argument is expected.",
        "invrl": "The argument `1` is not a valid Association or a list of rules.",
    }

    summary_text = "list association keys"

    def eval(self, rules, evaluation: Evaluation):
        "Keys[rules___]"

        def get_keys(expr):
            if expr.has_form(("Rule", "RuleDelayed"), 2):
                return expr.elements[0]
            elif expr.has_form("List", None) or (
                expr.has_form("Association", None)
                and AssociationQ(expr).evaluate(evaluation) is SymbolTrue
            ):
                return to_mathics_list(*expr.elements, elements_conversion_fn=get_keys)
            else:
                evaluation.message("Keys", "invrl", expr)
                raise TypeError

        rules = rules.get_sequence()
        if len(rules) != 1:
            evaluation.message("Keys", "argx", Integer(len(rules)))
            return

        try:
            return get_keys(rules[0])
        except TypeError:
            return None


class Lookup(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Lookup.html</url>

    <dl>
      <dt>Lookup[$assoc$, $key$]
      <dd>looks up the value associated with $key$ in the association $assoc$, \
          or Missing[$KeyAbsent$].
    </dl>
    """

    attributes = A_HOLD_ALL_COMPLETE
    rules = {
        "Lookup[assoc_?AssociationQ, key_, default_]": "FirstCase[assoc, _[Verbatim[key], val_] :> val, default]",
        "Lookup[assoc_?AssociationQ, key_]": 'Lookup[assoc, key, Missing["KeyAbsent", key]]',
    }

    summary_text = "perform lookup of a value by key, returning a specified default if it is not found"


class Missing(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Missing.html</url>

    <dl>
      <dd>'Missing[]'
      <dt> represents a data that is missing.
    </dl>

    >> ElementData["Meitnerium","MeltingPoint"]
     = Missing[NotAvailable]
    """

    summary_text = "symbolic representation of missing data"


class Values(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Values.html</url>

    <dl>
      <dt>'Values[<|$key1$ -> $val1$, $key2$ -> $val2$, ...|>]'
      <dd>return a list of the values $vali$ in an association.

      <dt>'Values[{$key1$ -> $val1$, $key2$ -> $val2$, ...}]'
      <dd>return a list of the $vali$ in a list of rules.
    </dl>

    >> Values[<|a -> x, b -> y|>]
     = {x, y}

    >> Values[{a -> x, b -> y}]
     = {x, y}

    Values automatically threads over lists:
    >> Values[{<|a -> x, b -> y|>, {c -> z, {}}}]
     = {{x, y}, {z, {}}}

    Values are listed in the order of their appearance:
    >> Values[{c -> z, b -> y, a -> x}]
     = {z, y, x}

    """

    attributes = A_PROTECTED

    messages = {
        "argx": "Values called with `1` arguments; 1 argument is expected.",
        "invrl": "The argument `1` is not a valid Association or a list of rules.",
    }

    summary_text = "list association values"

    def eval(self, rules, evaluation: Evaluation):
        "Values[rules___]"

        def get_values(expr):
            if expr.has_form(("Rule", "RuleDelayed"), 2):
                return expr.elements[1]
            elif expr.has_form("List", None) or (
                expr.has_form("Association", None)
                and AssociationQ(expr).evaluate(evaluation) is SymbolTrue
            ):
                return to_mathics_list(
                    *expr.elements, elements_conversion_fn=get_values
                )
            else:
                raise TypeError

        rules = rules.get_sequence()
        if len(rules) != 1:
            evaluation.message("Values", "argx", Integer(len(rules)))
            return

        try:
            return get_values(rules[0])
        except TypeError:
            evaluation.message("Values", "invrl", rules[0])
