# cython: language_level=3
# -*- coding: utf-8 -*-


from mathics.core.expression import Expression
from mathics.core.symbols import Atom, Symbol
from mathics.core.atoms import Integer
from mathics.builtin.base import MessageException

"""
This module provides some infrastructure to deal with SubExpressions.

"""


def _pspec_span_to_tuple(pspec, expr):
    """
    This function takes an expression and a Mathics
    `Span` Expression and returns a tuple with the positions
    of the elements.
    """
    start = 1
    stop = None
    step = 1
    elements = pspec.elements
    if len(elements) > 3:
        raise MessageException("Part", "span", elements)
    if len(elements) > 0:
        start = elements[0].get_int_value()
    if len(elements) > 1:
        stop = elements[1].get_int_value()
        if stop is None:
            if elements[1].get_name() == "System`All":
                stop = None
            else:
                raise MessageException("Part", "span", pspec)
        else:
            stop = stop - 1 if stop > 0 else len(expr.elements) + stop

    if len(pspec.elements) > 2:
        step = elements[2].get_int_value()

    if start is None or step is None:
        raise MessageException("Part", "span", pspec)

    if start == 0 or stop == 0:
        # index 0 is undefined
        raise MessageException("Part", "span", Integer(0))

    if start < 0:
        start = len(expr.elements) - start
    else:
        start = start - 1

    if stop is None:
        stop = 0 if step < 0 else len(expr.elements) - 1

    stop = stop + 1 if step > 0 else stop - 1
    return tuple(k for k in range(start, stop, step))


class ExpressionPointer:
    """
    This class represents a reference to a element in an expression.
    Supports a minimal part of the basic interface of `mathics.core.symbols.BaseElement`.
    """

    def __init__(self, expr, pos=None):
        """
        Initializes a ExpressionPointer pointing to the element in position `pos`
        of `expr`.

        expr: can be an Expression, a Symbol, or another ExpressionPointer
        pos: int or None

        If `pos==0`, then the pointer points to the `head` of the expression.
        If `pos` is `None`, it points out the whole expression.

        """
        if pos is None:
            if type(expr) is ExpressionPointer:
                self.parent = expr.parent
                self.position = expr.position
            else:
                self.parent = expr
                self.position = None
        else:
            self.parent = expr
            self.position = pos

    def __str__(self) -> str:
        return "%s[[%s]]" % (self.parent, self.position)

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def original(self):
        return None

    @original.setter
    def original(self, value):
        raise ValueError("Expression.original is write protected.")

    @property
    def head(self):
        pos = self.position
        if pos is None:
            return self.parent.head
        elif pos == 0:
            return self.parent.head.head
        return self.parent.elements[pos - 1].head

    @head.setter
    def head(self, value):
        raise ValueError("ExpressionPointer.head is write protected.")

    @property
    def elements(self):
        pos = self.position
        if pos is None:
            return self.parent.elements
        elif pos == 0:
            self.parent.head.elements
        return self.parent.elements[pos - 1].elements

    @elements.setter
    def elements(self, value):
        raise ValueError("ExpressionPointer.elements is write protected.")

    def get_head_name(self):
        return self.head.get_name()

    def is_atom(self):
        pos = self.position
        if pos is None:
            return self.parent.is_atom()
        elif pos == 0:
            return self.parent.head.is_atom()
        return self.parent.elements[pos - 1].is_atom()

    def to_expression(self):
        parent = self.parent
        p = self.position
        if p == 0:
            if isinstance(parent, Symbol):
                return parent
            else:
                return parent.head.copy()
        else:
            element = self.parent.elements[p - 1]
            if isinstance(element, Atom):
                return element
            else:
                return element.copy()

    def replace(self, new):
        """
        This method replaces the value pointed out by a `new` value.
        """
        # First, look for the ancestor that is not an ExpressionPointer,
        # keeping the positions of each step:
        parent = self.parent
        pos = [self.position]
        while type(parent) is ExpressionPointer:
            position = parent.position
            if position is None:
                parent = parent.parent
                continue
            pos.append(parent.position)
            parent = parent.parent
        # At this point, we hit the expression, and we have
        # the path to reach the position
        i = pos.pop()
        try:
            while pos:
                if i == 0:
                    parent = parent._head
                else:
                    parent = parent.elements[i - 1]
                i = pos.pop()
        except Exception:
            raise MessageException("Part", "span", pos)

        # Now, we have a pointer to an element in a true `Expression`.
        # Now, set it to the new value.
        if i == 0:
            parent.set_head(new)
        else:
            parent.set_element(i - 1, new)


class SubExpression:
    """
    This class represents a Subexpression of an existing Expression.
    Assignment to a subexpression results in the change of the original Expression.
    """

    def __new__(cls, expr, pos=None):
        """
        `expr` can be an `Expression`, a `ExpressionPointer` or
        another `SubExpression`
        `pos` can be `None`, an integer value or an `Expression` that
        indicates a subset of elements in the original `Expression`.
        If `pos` points out to a single whole element of `expr`, then
        returns an `ExpressionPointer`.
        """
        # If pos is a list, take the first element, and
        # store the remainder.
        if type(pos) in (tuple, list):
            pos, rem_pos = pos[0], pos[1:]
            if len(rem_pos) == 0:
                rem_pos = None
        else:
            rem_pos = None

        # Trivial conversion: if pos is an `Integer`, convert
        # to a Python native int
        if type(pos) is Integer:
            pos = pos.get_int_value()
        # pos == `System`All`
        elif isinstance(pos, Symbol) and pos.get_name() == "System`All":
            pos = None
        elif type(pos) is Expression:
            if pos.has_form("System`List", None):
                tuple_pos = [i.get_int_value() for i in pos.elements]
                if any([i is None for i in tuple_pos]):
                    raise MessageException("Part", "pspec", pos)
                pos = tuple_pos
            elif pos.has_form("System`Span", None):
                pos = _pspec_span_to_tuple(pos, expr)
            else:
                raise MessageException("Part", "pspec", pos)

        if pos is None or type(pos) is int:
            if rem_pos is None:
                return ExpressionPointer(expr, pos)
            else:
                return SubExpression(ExpressionPointer(expr, pos), rem_pos)
        elif type(pos) is tuple:
            self = super(SubExpression, cls).__new__(cls)
            self._headp = ExpressionPointer(expr.head, 0)
            self._elementsp = [
                SubExpression(ExpressionPointer(expr, k + 1), rem_pos) for k in pos
            ]
            return self

    def is_atom(self):
        return False

    def __str__(self):
        return (
            self.head.__str__()
            + "[\n"
            + ",\n".join(["\t " + element.__str__() for element in self.elements])
            + "\n\t]"
        )

    def __repr__(self):
        return self.__str__()

    @property
    def head(self):
        return self._headp

    @head.setter
    def head(self, value):
        raise ValueError("SubExpression.head is write protected.")

    def get_head_name(self):
        return self._headp.parent.get_head_name()

    @property
    def elements(self):
        return self._elementsp

    @elements.setter
    def elements(self, value):
        raise ValueError("SubExpression.elements is write protected.")

    @property
    def elements(self):
        return self._elementsp

    @elements.setter
    def elements(self, value):
        raise ValueError("SubExpression.elements is write protected.")

    def to_expression(self):
        return Expression(
            self._headp.to_expression(),
            *(element.to_expression() for element in self._elementsp)
        )

    def replace(self, new):
        """
        Asigns `new` to the subexpression, according to the logic of `mathics.core.walk_parts`
        """
        if (new.has_form("List", None) or new.get_head_name() == "System`List") and len(
            new.elements
        ) == len(self._elementsp):
            for element, sub_new in zip(self._elementsp, new.elements):
                element.replace(sub_new)
        else:
            for element in self._elementsp:
                element.replace(new)
