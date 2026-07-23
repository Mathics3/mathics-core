"""
Mathics3 implementation of an Association atom.
"""

from typing import Any, Iterable, Optional

from mathics.core.atoms import String
from mathics.core.convert.op import operator_to_ascii, operator_to_unicode
from mathics.core.element import BaseElement, BoxElementMixin
from mathics.core.expression import Expression
from mathics.core.keycomparable import BASIC_ATOM_ASSOCIATION_ELT_ORDER
from mathics.core.rules import is_rule
from mathics.core.symbols import Atom, Symbol
from mathics.core.systemsymbols import SymbolAssociation, SymbolRule
from mathics.settings import SYSTEM_CHARACTER_ENCODING

DictKeysType = type({}.keys())
DictValuesType = type({}.values())


class Association(Atom, BoxElementMixin):
    """An Association is an Atom collection that maps keys to values,
    similar to a Python dictionary.

    Each Key-Value mappings of an Association is called a Rule; but
    this kind of Rule is distinct from (or a degenerate form of) the
    pattern-matching RewriteRules found in DelayedRule and Set
    builtins.
    """

    class_head_name = "System`Association"

    def __init__(self, elements: Optional[Iterable], expr: Optional[Expression] = None):

        if expr is None:
            expr = Expression(SymbolAssociation, *elements)

        # Save the Expression form rewrite rule or pattern matching.
        self._expr = expr

        self.collection = {}
        if elements:
            for rule_expr in elements:
                if not is_rule(rule_expr):
                    raise TypeError(f"Association keys must be Rules, got {rule_expr}")
                self.collection[rule_expr.elements[0]] = rule_expr.elements[1]

        self.update_for_change()
        return

    # Add some dictionary like methods so that we can treat an Association object
    # as we would a dictionary.

    def __delitem__(self, key: BaseElement) -> None:
        """Remove a key-value pair from the association.

        Args:
            key: The key to remove.

        Raises:
            KeyError: If the key is not found in the association.

        Side effects:
            Updates self.collection
        """
        if key not in self.collection:
            raise KeyError(key)

        self.deletes.append[key]
        del self.collection[key]

    def __eq__(self, other: Any) -> bool:
        """Check equality with another Association."""
        if not isinstance(other, Association):
            return False

        if len(self.collection) != len(other.collection):
            return False

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

    def __getitem__(self, key: Any) -> Any:
        """Retrieve a value from the association by key.

        Args:
            key: The key to look up in the association.

        Returns:
            The value associated with the given key.

        Raises:
            KeyError: If the key is not found in the association.
        """
        if key in self.collection:
            return self.collection[key]
        raise KeyError(key)

    def __hash__(self) -> int:
        return self._hash

    def __setitem__(self, key: BaseElement, value: BaseElement) -> None:
        """Set or update a key-value pair in the association.

        Args:
            key: The key to set or update.
            value: The value to associate with the key.

        Side effects:
            Updates self.collection
        """
        self.collection[key] = value

    def __str__(self) -> str:
        """Return string representation of the Association."""

        if SYSTEM_CHARACTER_ENCODING == "ASCII":
            operator = operator_to_ascii.get("Rule", "->")
        else:
            operator = operator_to_unicode.get("Rule", "⇾")

        items = [f"{k} {operator} {v}" for k, v in self.collection.items()]
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

    @property
    def expr(self) -> Expression:
        """
        Convert internal form to M-expression Expression.
        This is useful, for example, in Form handling.
        """
        if self._expr is None:
            elements = []
            for key, value in self.collection.items():
                elements.append(Expression(SymbolRule, key, value))
            return Expression(SymbolAssociation, *elements)

        return self._expr

    def get(self, key: BaseElement, default: BaseElement = None) -> BaseElement:
        """Return the value for key if key is in the association, else default.

        Behaves like dict.get().
        """
        return self.collection.get(key, default)

    def get_elements(self) -> Any:
        return tuple(self.collection.items())

    get_string_value = __str__

    def keys(self) -> DictKeysType:
        """Return the keys of an the association.
        Behaves like dict.keys().
        """
        return self.collection.keys()

    @property
    def head(self) -> Symbol:
        return SymbolRule

    def items(self) -> tuple:
        """Return the values of an the association.
        Behaves like dict.items().
        """
        return self.collection.items()

    def sameQ(self, other: Any) -> bool:
        """
        Mathics3 SameQ comparison.
        Two Associations are SameQ if they have the same keys and values in the same order.
        """
        if not isinstance(other, Association):
            return False

        if len(self.collection) != len(other.collection):
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
        # FIXME
        return None

    def to_sympy(self, **kwargs):
        return None

    def values(self) -> DictValuesType:
        """Return the values of an the association.
        Behaves like dict.values().
        """
        return self.collection.values()

    def update(self, e: Iterable):
        """Return the values of an the association.
        Behaves like dict.update() except we return the update object
        value
        """
        self.collection.update(e)
        self.update_for_change()
        self._expr = None

    def update_for_change(self):
        """
        Things we have to do when the Association is changed.
        """
        hash_elements = []
        for key, value in self.collection.items():
            # Update hash component
            hash_elements.append((hash(key), hash(value)))

        self._hash = hash(("Association", tuple(hash_elements)))
