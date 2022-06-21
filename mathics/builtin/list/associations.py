# -*- coding: utf-8 -*-

"""
Associations

An Association maps keys to values and is similar to a dictionary in Python; it is often sparse in that their key space is much larger than the number of actual keys found in the collection.
"""


from mathics.builtin.base import (
    Builtin,
    Test,
)
from mathics.builtin.box.inout import RowBox
from mathics.builtin.lists import list_boxes
from mathics.core.atoms import Integer
from mathics.core.attributes import hold_all_complete, protected
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolAssociation,
    SymbolMakeBoxes,
    SymbolMissing,
)


class Association(Builtin):
    """
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

    #> <|a -> x, b -> y, c -> <|d -> t|>|>
     = <|a -> x, b -> y, c -> <|d -> t|>|>
    #> %["s"]
     = Missing[KeyAbsent, s]

    #> <|a -> x, b + c -> y, {<|{}|>, a -> {z}}|>
     = <|a -> {z}, b + c -> y|>
    #> %[a]
     = {z}

    #> <|"x" -> 1, {y} -> 1|>
     = <|x -> 1, {y} -> 1|>
    #> %["x"]
     = 1

    #> <|<|a -> v|> -> x, <|b -> y, a -> <|c -> z|>, {}, <||>|>, {d}|>[c]
     =  Association[Association[a -> v] -> x, Association[b -> y, a -> Association[c -> z], {}, Association[]], {d}][c]

    #> <|<|a -> v|> -> x, <|b -> y, a -> <|c -> z|>, {d}|>, {}, <||>|>[a]
     = Association[Association[a -> v] -> x, Association[b -> y, a -> Association[c -> z], {d}], {}, Association[]][a]

    #> <|<|a -> v|> -> x, <|b -> y, a -> <|c -> z, {d}|>, {}, <||>|>, {}, <||>|>
     = <|<|a -> v|> -> x, b -> y, a -> Association[c -> z, {d}]|>
    #> %[a]
     = Association[c -> z, {d}]

    #> <|a -> x, b -> y, c -> <|d -> t|>|> // ToBoxes
     = RowBox[{<|, RowBox[{RowBox[{a, ->, x}], ,, RowBox[{b, ->, y}], ,, RowBox[{c, ->, RowBox[{<|, RowBox[{d, ->, t}], |>}]}]}], |>}]

    #> Association[a -> x, b -> y, c -> Association[d -> t, Association[e -> u]]] // ToBoxes
     = RowBox[{<|, RowBox[{RowBox[{a, ->, x}], ,, RowBox[{b, ->, y}], ,, RowBox[{c, ->, RowBox[{<|, RowBox[{RowBox[{d, ->, t}], ,, RowBox[{e, ->, u}]}], |>}]}]}], |>}]
    """

    error_idx = 0

    attributes = hold_all_complete | protected

    summary_text = "an association between keys and values"

    def apply_makeboxes(self, rules, f, evaluation):
        """MakeBoxes[<|rules___|>,
        f:StandardForm|TraditionalForm|OutputForm|InputForm]"""

        def validate(exprs):
            for expr in exprs:
                if expr.has_form(("Rule", "RuleDelayed"), 2):
                    pass
                elif expr.has_form(("List", "Association"), None):
                    if not validate(expr.elements):
                        return False
                else:
                    return False
            return True

        rules = rules.get_sequence()
        if self.error_idx == 0 and validate(rules) is True:
            expr = RowBox(*list_boxes(rules, f, evaluation, "<|", "|>"))
        else:
            self.error_idx += 1
            symbol = Expression(SymbolMakeBoxes, SymbolAssociation, f)
            expr = RowBox(
                symbol.evaluate(evaluation), *list_boxes(rules, f, evaluation, "[", "]")
            )

        if self.error_idx > 0:
            self.error_idx -= 1
        return expr

    def apply(self, rules, evaluation):
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

    def apply_key(self, rules, key, evaluation):
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

    def test(self, expr):
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


class Keys(Builtin):
    """
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

    #> Keys[a -> x]
     = a

    #> Keys[{a -> x, a -> y, {a -> z, <|b -> t|>, <||>, {}}}]
     = {a, a, {a, {b}, {}, {}}}

    #> Keys[{a -> x, a -> y, <|a -> z, {b -> t}, <||>, {}|>}]
     = {a, a, {a, b}}

    #> Keys[<|a -> x, a -> y, <|a -> z, <|b -> t|>, <||>, {}|>|>]
     = {a, b}

    #> Keys[<|a -> x, a -> y, {a -> z, {b -> t}, <||>, {}}|>]
     = {a, b}

    #> Keys[<|a -> x, <|a -> y, b|>|>]
     : The argument Association[a -> x, Association[a -> y, b]] is not a valid Association or a list of rules.
     = Keys[Association[a -> x, Association[a -> y, b]]]

    #> Keys[<|a -> x, {a -> y, b}|>]
     : The argument Association[a -> x, {a -> y, b}] is not a valid Association or a list of rules.
     = Keys[Association[a -> x, {a -> y, b}]]

    #> Keys[{a -> x, <|a -> y, b|>}]
     : The argument Association[a -> y, b] is not a valid Association or a list of rules.
     = Keys[{a -> x, Association[a -> y, b]}]

    #> Keys[{a -> x, {a -> y, b}}]
     : The argument b is not a valid Association or a list of rules.
     = Keys[{a -> x, {a -> y, b}}]

    #> Keys[a -> x, b -> y]
     : Keys called with 2 arguments; 1 argument is expected.
     = Keys[a -> x, b -> y]
    """

    attributes = protected

    messages = {
        "argx": "Keys called with `1` arguments; 1 argument is expected.",
        "invrl": "The argument `1` is not a valid Association or a list of rules.",
    }

    summary_text = "list association keys"

    def apply(self, rules, evaluation):
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
            return evaluation.message("Keys", "argx", Integer(len(rules)))

        try:
            return get_keys(rules[0])
        except TypeError:
            return None


class Lookup(Builtin):
    """
    <dl>
      <dt>Lookup[$assoc$, $key$]
      <dd> looks up the value associated with $key$ in the association $assoc$, or Missing[$KeyAbsent$].
    </dl>
    """

    attributes = hold_all_complete
    rules = {
        "Lookup[assoc_?AssociationQ, key_, default_]": "FirstCase[assoc, _[Verbatim[key], val_] :> val, default]",
        "Lookup[assoc_?AssociationQ, key_]": 'Lookup[assoc, key, Missing["KeyAbsent", key]]',
    }

    summary_text = "perform lookup of a value by key, returning a specified default if it is not found"


class Missing(Builtin):
    """
    <dl>
    <dd>'Missing[]'
    <dt> represents a data that is misssing.
    </dl>
    >> ElementData["Meitnerium","MeltingPoint"]
     = Missing[NotAvailable]
    """

    summary_text = "symbolic representation of missing data"


class Values(Builtin):
    """
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

    #> Values[a -> x]
     = x

    #> Values[{a -> x, a -> y, {a -> z, <|b -> t|>, <||>, {}}}]
     = {x, y, {z, {t}, {}, {}}}

    #> Values[{a -> x, a -> y, <|a -> z, {b -> t}, <||>, {}|>}]
     = {x, y, {z, t}}

    #> Values[<|a -> x, a -> y, <|a -> z, <|b -> t|>, <||>, {}|>|>]
     = {z, t}

    #> Values[<|a -> x, a -> y, {a -> z, {b -> t}, <||>, {}}|>]
     = {z, t}

    #> Values[<|a -> x, <|a -> y, b|>|>]
     : The argument Association[a -> x, Association[a -> y, b]] is not a valid Association or a list of rules.
     = Values[Association[a -> x, Association[a -> y, b]]]

    #> Values[<|a -> x, {a -> y, b}|>]
     : The argument Association[a -> x, {a -> y, b}] is not a valid Association or a list of rules.
     = Values[Association[a -> x, {a -> y, b}]]

    #> Values[{a -> x, <|a -> y, b|>}]
     : The argument {a -> x, Association[a -> y, b]} is not a valid Association or a list of rules.
     = Values[{a -> x, Association[a -> y, b]}]

    #> Values[{a -> x, {a -> y, b}}]
     : The argument {a -> x, {a -> y, b}} is not a valid Association or a list of rules.
     = Values[{a -> x, {a -> y, b}}]

    #> Values[a -> x, b -> y]
     : Values called with 2 arguments; 1 argument is expected.
     = Values[a -> x, b -> y]
    """

    attributes = protected

    messages = {
        "argx": "Values called with `1` arguments; 1 argument is expected.",
        "invrl": "The argument `1` is not a valid Association or a list of rules.",
    }

    summary_text = "list association values"

    def apply(self, rules, evaluation):
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
            return evaluation.message("Values", "argx", Integer(len(rules)))

        try:
            return get_values(rules[0])
        except TypeError:
            return evaluation.message("Values", "invrl", rules[0])
