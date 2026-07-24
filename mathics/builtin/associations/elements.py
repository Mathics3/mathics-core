# -*- coding: utf-8 -*-

"""
Elements of Associations
"""

from mathics.core.attributes import A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.eval.associations.elements import (
    eval_KeyExistsQ,
    eval_Keys,
    eval_Keys_with_Head,
    eval_Lookup,
    eval_Lookup_assocs_list_key,
    eval_Lookup_multiple_keys,
    eval_Values,
    eval_Values_with_Head,
)


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

    def eval(self, expr, evaluation: Evaluation):
        "Keys[expr_]"
        return eval_Keys(expr, evaluation)

    def eval_with_head(self, expr, head, evaluation: Evaluation):
        "Keys[expr_, head_]"
        return eval_Keys_with_Head(expr, head, evaluation)


class KeyExistsQ(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/KeyExistsQ.html</url>

    <dl>
      <dt>'KeyExistsQ'[$assoc$, $key$]
      <dd>returns True if $key$ exists in $assoc$ (an Association or association-like expression), and False otherwise.
    </dl>

    >> KeyExistsQ[<|a -> x, b -> y, c -> z|>, a]
     = True

    >> KeyExistsQ[<|a -> x, b -> y, c -> z|>, d]
     = False
    """

    attributes = A_PROTECTED

    summary_text = "test whether a key exists in an association"

    # Patterns implemented as method names:
    def eval_assoc_key(self, assoc, key: BaseElement, evaluation: Evaluation):
        "KeyExistsQ[assoc_Association, key_]"

        return eval_KeyExistsQ(assoc, key, evaluation)


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

    def eval(self, expr, evaluation: Evaluation):
        "Values[expr_]"
        return eval_Values(expr, evaluation)

    def eval_with_head(self, expr, head, evaluation: Evaluation):
        "Values[expr_, head_]"
        return eval_Values_with_Head(expr, head, evaluation)
