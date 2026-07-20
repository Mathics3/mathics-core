"""
Mathics3 Association
"""

from typing import Any, Iterable, Optional

from mathics.core.atoms import String
from mathics.core.element import BaseElement, BoxElementMixin
from mathics.core.keycomparable import BASIC_ATOM_ASSOCIATION_ELT_ORDER
from mathics.core.rules import is_rule
from mathics.core.symbols import Atom, Symbol
from mathics.core.systemsymbols import SymbolRule


class Association(Atom, BoxElementMixin):
    """An Association is an Atom collection that maps keys to values,
    similar to a Python dictionary.

    Each Key-Value mappings of an Association is called a Rule; but
    this kind of Rule is distinct from (or a degenerate form of) the
    pattern-matching RewriteRules found in DelayedRule and Set
    builtins.
    """

    class_head_name = "System`Association"

    def __init__(self, elements: Optional[Iterable]):

        # When self._value is not {} and is_literal is False, then
        # value when what can be represented in Python without resorting
        # to M-expressions that need to be evaluated. This typically happens when
        # the entire association is a literal value.
        self._value: dict = {}

        self.collection = {}
        if elements:
            for rule_expr in elements:
                if not is_rule(rule_expr):
                    raise TypeError(f"Association keys must be Rules, got {rule_expr}")
                self.collection[rule_expr.elements[0]] = rule_expr.elements[1]

        self.update_for_change()
        return

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: Any) -> bool:
        """Check equality with another Association."""
        if not isinstance(other, Association):
            return False

        if len(self.collection) != len(other.collection):
            return False

        if self._is_literal != other._is_literal:
            return False

        if self.is_literal:
            return self._value == other._value

        # "other" is an Association that is not literal like us,
        # and has the same number items in its collection.
        # Here, we have compare key-value pairs
        return self.collection == other.collection

        # If for some reason the above does not work:
        # for key_repr, (key, value) in self._value.items():
        #     if key_repr not in other._value:
        #         return False
        #     other_key, other_value = other._value[key_repr]
        #     if key != other_key or value != other_value:
        #         return False

        # We can't disprove a difference, so they are the same.
        # return True

    def __str__(self) -> str:
        """Return string representation of the Association."""
        if not self._value:
            return "<||>"
        items = [f"{k} ⇾ {v}" for k, (_, v) in self._value.items()]
        return f"<|{', '.join(items)}|>"

    def atom_to_boxes(self, f, evaluation) -> "BaseElement":
        """
        Produces a Box expression that represents how the Association should be formatted.
        """
        # For now, return a simple string representation
        return String(str(self))

    @property
    def elements(self) -> dict:
        return self.collection.items()

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return (
            BASIC_ATOM_ASSOCIATION_ELT_ORDER,
            SymbolRule,
            len(self.collection),
            self.collection,
        )

    get_string_value = __str__

    @property
    def head(self) -> Symbol:
        return SymbolRule

    @property
    def is_literal(self) -> bool:
        """
        For an Association, it is considered a literal if all its keys and values
        are literals and the structure is fixed. W
        """
        print("XXX1 Association is_literal called")
        return self._is_literal

    def sameQ(self, other: Any) -> bool:
        """
        Mathics3 SameQ comparison.
        Two Associations are SameQ if they have the same keys and values in the same order.
        """
        if not isinstance(other, Association):
            return False

        if len(self.collection) != len(other.collection):
            return False

        if self._is_literal != other._is_literal:
            return False

        if len(self._value) != len(other._value):
            return False

        # Compare all key-value pairs. We can't use == because
        # the keys have to be in the same order

        for key_repr, (key, value) in self.collection.items():
            if key_repr not in other._value:
                return False
            other_key, other_value = other._value[key_repr]
            if key != other_key or value != other_value:
                return False

        # We can't disprove a difference, so they are the same.
        return True

    def to_python(self, *args, **kwargs) -> Optional[dict]:
        return self._value if self._is_literal else None

    def to_sympy(self, **kwargs):
        return None

    @property
    def value(self) -> dict:
        """A Python-friendly replacement value."""
        return self._value

    def update_for_change(self):
        """
        Things we have to do when the Association is changed.
        """
        hash_elements = []
        is_literal: bool = True
        for key, value in self.collection.items():
            if is_literal:
                # Update is_literal, and possibly self._value.
                if (
                    key.is_literal
                    and value.is_literal
                    and (hasattr(key, "value") and hasattr(value, "value"))
                ):
                    self._value[key.value] = value.value
                else:
                    is_literal = False
                    self._value = {}

            # Update hash component
            hash_elements.append((hash(key), hash(value)))

        self._hash = hash(("Association", tuple(hash_elements)))
        self._is_literal = is_literal
