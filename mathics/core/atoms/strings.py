"""
Mathics3 String
"""

# Note: Python warns of ambiguity Python's module string if we name this file this string.py

import math

import sympy

from mathics.core.element import BoxElementMixin
from mathics.core.keycomparable import BASIC_ATOM_STRING_ELT_ORDER
from mathics.core.symbols import Atom, Symbol, SymbolFalse, SymbolTrue, symbol_set
from mathics.core.systemsymbols import SymbolFullForm, SymbolInputForm

SymbolString = Symbol("String")

SYSTEM_SYMBOLS_INPUT_OR_FULL_FORM = symbol_set(SymbolInputForm, SymbolFullForm)


class String(Atom, BoxElementMixin):
    value: str
    class_head_name = "System`String"
    hash: int

    def __new__(cls, value):
        self = super().__new__(cls)
        self.value = str(value)
        # Set a value for self.__hash__() once so that every time
        # it is used this is fast.
        self.hash = hash(("String", self.value))
        return self

    def __hash__(self) -> int:
        return self.hash

    def __str__(self) -> str:
        return '"%s"' % self.value

    def atom_to_boxes(self, f, evaluation):
        from mathics.format.box import _boxed_string

        inner = str(self.value)
        if f in SYSTEM_SYMBOLS_INPUT_OR_FULL_FORM:
            inner = inner.replace("\\", "\\\\")
            inner = inner.replace('"', '\\"')
            inner = f'"{inner}"'
            return _boxed_string(
                inner,
                **{
                    "System`NumberMarks": SymbolTrue,
                    "System`ShowSpecialCharacters": SymbolFalse,
                    "System`ShowStringCharacters": SymbolTrue,
                },
            )
        return String('"' + inner + '"')

    def do_copy(self) -> "String":
        return String(self.value)

    def default_format(self, evaluation, form) -> str:
        value = self.value.replace("\\", "\\\\").replace('"', '\\"')
        return '"%s"' % value

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return (
            BASIC_ATOM_STRING_ELT_ORDER,
            self.value,
            0,
            1,
        )

    @property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        """
        return super().pattern_precedence

    def get_string_value(self) -> str:
        return self.value

    @property
    def is_literal(self) -> bool:
        """For a String, the value can't change and has a Python representation,
        i.e. a value is set and it does not depend on definition
        bindings. So we say it is a literal.
        """
        return True

    @property
    def is_multiline(self) -> bool:
        return "\n" in self.value

    def sameQ(self, rhs) -> bool:
        """Mathics SameQ"""
        return isinstance(rhs, String) and self.value == rhs.value

    def to_expression(self):
        return self

    def to_sympy(self, **kwargs):
        return None

    def to_python(self, *args, **kwargs) -> str:
        if kwargs.get("string_quotes", True):
            return '"%s"' % self.value  # add quotes to distinguish from Symbols
        else:
            return self.value

    def user_hash(self, update):
        # hashing a String is the one case where the user gets the untampered
        # hash value of the string's text. this corresponds to MMA behavior.
        update(self.value.encode("utf8"))

    def __getnewargs__(self) -> tuple:
        return (self.value,)


class StringFromPython(String):
    def __new__(cls, value):
        self = super().__new__(cls, value)
        if isinstance(value, sympy.NumberSymbol):
            self.value = "sympy." + str(value)

        # Note that the test is done with math.inf first.
        # This is to use float's ==, which may not strictly be necessary.
        if math.inf == value:
            self.value = "math.inf"
        return self
