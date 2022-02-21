# -*- coding: utf-8 -*-
# FIXME: decide on whether we want mathics.core.expression.Atom vs. mathics.core.parser.Atom
# both having Atom at the end. Or should one subclass the other?
"""
Classes and Objects that the parser uses to create an initial Expression (an M-Expression).

The parser's AST is an M-Expression.

Note that some of these classes also appear with the same name in the mathics.core.expression module.
So we have mathics.core.expression.Atom vs. mathics.core.parser.Atom
"""


class Node:
    """
    The base class for a node or "elements" of an M-Expression.
    Really there are only two kinds of nodes: Atoms which are the
    expression's leaves and a non-leaf nodes.
    """

    def __init__(self, head, *children):
        if isinstance(head, Node):
            self.head = head
        else:
            self.head = Symbol(head)
        self.value = None
        self.children = list(children)
        self.parenthesised = False

    def get_head_name(self):
        if isinstance(self.head, Symbol):
            return self.head.value
        else:
            return ""

    def __repr__(self):
        return "%s[%s]" % (self.head, ", ".join(str(child) for child in self.children))

    def __eq__(self, other):
        if not isinstance(other, Node):
            raise TypeError()
        return (
            (self.get_head_name() == other.get_head_name())
            and (len(self.children) == len(other.children))
            and all(cs == co for cs, co in zip(self.children, other.children))
        )

    def flatten(self):
        head_name = self.get_head_name()
        new_children = []
        for child in self.children:
            if child.get_head_name() == head_name and not child.parenthesised:
                new_children.extend(child.children)
            else:
                new_children.append(child)
        self.children = new_children
        return self


class Atom(Node):
    """
    Atoms form the leaves of an M-Expression and have no internal structure of
    their own. You can however compare Atoms for equality.
    """

    def __init__(self, value):
        self.head = Symbol(self.__class__.__name__)
        self.value = value
        self.children = []
        self.parenthesised = False

    def __repr__(self):
        return "%s[%s]" % (self.head, self.value)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.value == other.value


# What remains below are all of the different kinds of Atoms.
class Number(Atom):
    """
    An Atom with a numeric value. Later on though in evaluation, a Number can get refined into
    a particular kind of number such as an Integer or a Real. Note that these too
    are Atoms.
    """

    def __init__(
        self, value: str, sign: int = 1, base: int = 10, suffix=None, exp: int = 0
    ):
        assert isinstance(value, str)
        assert sign in (-1, 1)
        assert isinstance(base, int)
        assert 2 <= base <= 36
        assert isinstance(exp, int)
        assert suffix is None or isinstance(suffix, str)
        super(Number, self).__init__(None)
        self.value = value
        self.sign = sign
        self.base = base
        self.suffix = suffix
        self.exp = exp

    def __repr__(self):
        result = self.value
        if self.base != 10:
            result = "%i^^%s" % (self.base, result)
        if self.sign == -1:
            result = "-%s" % result
        if self.suffix is not None:
            result = "%s`%s" % (result, self.suffix)
        if self.exp != 0:
            result = "%s*^%i" % (result, self.exp)
        return result

    def __eq__(self, other):
        return isinstance(other, Number) and repr(self) == repr(other)


class Symbol(Atom):
    """
    Symbols are like variables in a programming language.

    But initially in an M-Expression the only properties it has is its name
    and a representation of its name.

    Devoid of a binding to the Symbol, which is done via a Definition, Symbols
    are unique as they are say in Lisp, or Python.
    """

    def __init__(self, value: str, context="System"):
        self.context = context
        self.value = value
        self.children = []

    # avoids recursive definition
    @property
    def head(self):
        return Symbol(self.__class__.__name__)

    def __repr__(self):
        return self.value


class String(Atom):
    """
    A string is is pretty much the same as in any other programming language, a sequence of characters.
    Having this in a class is useful so that we can distinguish it from Symbols.
    The display of a String is surrounded by double quotes.
    """

    def __repr__(self):
        return '"' + self.value + '"'


class Filename(Atom):
    """
    A filename is printed the same way a Symbol prints, in contrast to a String.
    However, like String, it doesn't have any other properties.
    """

    def __repr__(self):
        return self.value
