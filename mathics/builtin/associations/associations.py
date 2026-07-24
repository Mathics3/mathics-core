# -*- coding: utf-8 -*-

"""
Associations and Parts
"""

from mathics.builtin.box.layout import RowBox
from mathics.core.atoms.associations import Association
from mathics.core.attributes import A_HOLD_ALL_COMPLETE, A_PROTECTED
from mathics.core.builtin import Builtin, Test
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.rules import is_rule
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolAssociation, SymbolMakeBoxes, SymbolMissing
from mathics.eval.list.associations import eval_AssociationQ
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
        return eval_AssociationQ(expr)


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
