# -*- coding: utf-8 -*-

"""
Associations

An Association maps keys to values and is similar to a dictionary in Python.
It is often sparse in that its key space is much larger than the number of \
actual keys found in the collection.
"""

from mathics.builtin.box.layout import RowBox
from mathics.core.atoms import Integer
from mathics.core.atoms.associations import Association
from mathics.core.attributes import A_HOLD_ALL_COMPLETE, A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin, Test
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.rules import is_rule
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.core.systemsymbols import SymbolAssociation, SymbolMakeBoxes, SymbolMissing
from mathics.eval.list.associations import (
    eval_Lookup,
    eval_Lookup_assocs_list_key,
    eval_Lookup_multiple_keys,
)
from mathics.eval.lists import list_boxes


class Association_(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Association.html</url>

    <dl>
      <dt>'Association'[$key_1$ -> $val_1$, $key_2$ -> $val_2$, ...]
      <dt>'<|$key_1$ -> $val_1$, $key_2$ -> $val_2$, ...|>'
      <dd> represents an association between keys and values.
    </dl>

    'Association' is the head of associations:
    >> Head[<|a -> x, b -> y, c -> z|>]
     = Association

    >> <|a -> x, b -> y|>
     = <|a ⇾ x, b ⇾ y|>

    >> Association[{a -> x^2, b -> y}]
     = <|a ⇾ x ^ 2, b ⇾ y|>

    Associations can be nested:
    >> <|a -> x, b -> y, <|a -> z, d -> t|>|>
     = <|a ⇾ z, b ⇾ y, d ⇾ t|>

    Look up a key in multiple associations:
    >> Lookup[{<|a -> 1, b -> 2|>, <|a -> 3, c -> 4|>}, a]
     = {1, 3}
    """

    attributes = A_HOLD_ALL_COMPLETE | A_PROTECTED

    error_idx = 0

    name = "Association"
    summary_text = "make an association between keys and values"

    def eval_makeboxes(self, rules, f, evaluation: Evaluation):
        """MakeBoxes[<|rules___|>,
        (f:StandardForm|TraditionalForm)]"""

        def validate(exprs):
            for expr in exprs:
                if is_rule(expr):
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

    def eval(self, rules, evaluation: Evaluation):
        "Association[rules__]"

        def make_flatten(exprs, rules_dictionary: dict = {}):
            for expr in exprs:
                if is_rule(expr):
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
            elements = make_flatten(rules.get_sequence())
            expr = Expression(SymbolAssociation, *elements)
            return Association(elements, expr=expr)
        except TypeError:
            return None

    def eval_key(self, rules, key, evaluation: Evaluation):
        "Association[rules__][key_]"

        def find_key(exprs, rules_dictionary: dict = {}):
            for expr in exprs:
                if is_rule(expr):
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

    # Define some sort of pattern that matches an association
    # def eval_key(self, rules, key, evaluation: Evaluation):
    #     "Association[rules__][key_]"


class AssociationQ(Test):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/AssociationQ.html</url>

    <dl>
      <dt>'AssociationQ'[$expr$]
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
                if is_rule(element):
                    pass
                elif element.has_form(("List", "Association"), None):
                    if not validate(element.elements):
                        return False
                else:
                    return False
            return True

        if isinstance(expr, Association):
            return True
        # Handle where we still have Expression[SymbolRule, ... ]
        return expr.get_head_name() == "System`Association" and validate(expr.elements)


class Key(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Key.html</url>

    <dl>
      <dt>'Key'[$key$]
      <dd> represents a key used to access a value in an association.
      <dt>'Key'[$key$][$assoc$]
      <dd>
    </dl>

    Get a value from an association as using part:
    >> <|w -> x, y -> z|>[[Key[w]]]
     = x

    Same thing using function application:
    >> <|w -> x, y -> z|>[w]
     = x

    """

    rules = {
        "Key[key_][assoc_Association]": "assoc[key]",
    }
    summary_text = "indicate a key within a part specification"


class Keys(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Keys.html</url>

    <dl>
      <dt>'Keys'['<|' $key_1$ '->' $val_1$, $key_2$ '->' $val_2$, ...'|>']
      <dd>return a list of the keys $keyi$ in an association.

      <dt>'Keys'[{$key_1$ '->' $val_1$, $key_2$ '->' $val_2$, ...}]
      <dd>return a list of the $key_i$ in a list of rules.

      <dt>'Keys'[$expr$, $h$]
      <dd>applies the head $h$ to each key.
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

    Apply a head to each key:
    >> Keys[<|a -> x, b -> y|>, f]
     = {f[a], f[b]}
    """

    attributes = A_PROTECTED

    eval_error = Builtin.generic_argument_error
    expected_args = (1, 2)

    summary_text = "list association keys"

    def eval(self, rules, evaluation: Evaluation):
        "Keys[rules_]"

        def get_keys(expr):
            if is_rule(expr):
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

    def eval_with_head(self, rules, head, evaluation: Evaluation):
        "Keys[rules_, head_]"

        def get_keys_with_head(expr, h):
            if is_rule(expr):
                key = expr.elements[0]
                return Expression(h, key)
            elif expr.has_form("List", None) or (
                expr.has_form("Association", None)
                and AssociationQ(expr).evaluate(evaluation) is SymbolTrue
            ):
                return to_mathics_list(
                    *expr.elements,
                    elements_conversion_fn=lambda e: get_keys_with_head(e, h),
                )
            else:
                evaluation.message("Keys", "invrl", expr)
                raise TypeError

        try:
            return get_keys_with_head(rules, head)
        except TypeError:
            return None


class Lookup(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Lookup.html</url>

    <dl>
      <dt>Lookup[$assoc$, $key$]
      <dd>looks up the value associated with $key$ in the association $assoc$, \
          returning Missing[$KeyAbsent$, $key$] if the key is not found.
      <dt>Lookup[$assoc$, $key$, $default$]
      <dd>looks up the value associated with $key$ in the association $assoc$, \
          returning $default$ if the key is not found.
      <dt>Lookup[$assoc$, {$key_1$, $key_2$, ...}]
      <dd>looks up multiple keys and returns a list of values.
      <dt>Lookup[{$assoc_1$, $assoc_2$, ...}, $key$]
      <dd>looks up $key$ in each association and returns a list of values.
    </dl>

    Look up the value associated with key $a$:
    >> Lookup[<|a -> 1, b -> 2|>, a]
     = 1

    When a key is not found, a Missing object is returned by default:
    >> Lookup[<|a -> 1, b -> 2|>, c]
     = Missing[KeyAbsent, c]

    Provide a default value to be used when the key is not found:
    >> Lookup[<|a -> 1, b -> 2|>, c, -1]
     = -1

    Use the operator form of Lookup:
    >> Lookup[<|a -> 1, b -> 2|>, {a, b}]
     = {1, 2}

    Look up multiple keys at once:
    >> Lookup[<|a -> 1, b -> 2|>, {a, b, c}]
     = {1, 2, Missing[KeyAbsent, c]}

    Provide a default value to be used when the key is not found:
    >> Lookup[<|a -> 1, b -> 2|>, c, 3]
     = 3

    """

    attributes = A_PROTECTED | A_READ_PROTECTED

    eval_error = Builtin.generic_argument_error
    expected_args = range(2, 5)

    summary_text = "perform lookup of a value by key, returning a specified default if it is not found"

    def eval_assoc_key(self, assoc, key, evaluation: Evaluation):
        """Lookup[assoc_Association, key_]"""
        return eval_Lookup(assoc, key, None, evaluation)

    def eval_assoc_key_default(self, assoc, key, default, evaluation: Evaluation):
        """Lookup[assoc_Association, key_, default_]"""
        return eval_Lookup(assoc, key, default, evaluation)

    def eval_assoc_keys(self, assoc, keys, evaluation: Evaluation):
        """Lookup[assoc_Association, keys_List]"""
        return eval_Lookup_multiple_keys(assoc, keys, None, evaluation)

    def eval_assoc_keys_default(self, assoc, keys, default, evaluation: Evaluation):
        """Lookup[assoc_Association, keys_List, default_]"""
        return eval_Lookup_multiple_keys(assoc, keys, default, evaluation)

    def eval_assocs_list_key(self, assocs, key, evaluation: Evaluation):
        """Lookup[assocs_List, key_]"""
        return eval_Lookup_assocs_list_key(assocs, key, None, evaluation)

    def eval_assocs_list_key_default(
        self, assocs, key, default, evaluation: Evaluation
    ):
        """Lookup[assocs_List, key_, default_]"""
        return eval_Lookup_assocs_list_key(assocs, key, default, evaluation)


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
      <dt>'Values'['<|'$key_1$ '->' $val_1$, $key_2$ -> $val_2$, ...'|>']
      <dd>return a list of the values $val_i$ in an association.

      <dt>'Values'[{$key_1$ '->' $val_1$, $key_2$ '->' $val_2$, ...}]
      <dd>return a list of the $val_i$ in a list of rules.

      <dt>'Values'[$expr$, $h$]
      <dd>applies the head $h$ to each value.
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

    Apply a head to each value:
    >> Values[<|a -> x, b -> y|>, f]
     = {f[x], f[y]}
    """

    attributes = A_PROTECTED

    eval_error = Builtin.generic_argument_error
    expected_args = (1, 2)

    summary_text = "list association values"

    def eval(self, rules, evaluation: Evaluation):
        "Values[rules_]"

        def get_values(expr):
            if is_rule(expr):
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

    def eval_with_head(self, rules, head, evaluation: Evaluation):
        "Values[rules_, head_]"

        def get_values_with_head(expr, h):
            if is_rule(expr):
                value = expr.elements[1]
                return Expression(h, value)
            elif expr.has_form("List", None) or (
                expr.has_form("Association", None)
                and AssociationQ(expr).evaluate(evaluation) is SymbolTrue
            ):
                return to_mathics_list(
                    *expr.elements,
                    elements_conversion_fn=lambda e: get_values_with_head(e, h),
                )
            else:
                evaluation.message("Values", "invrl", expr)
                raise TypeError

        try:
            return get_values_with_head(rules, head)
        except TypeError:
            return None
