# cython: language_level=3
"""
This module provides some infrastructure to deal with SubExpressions.

"""


from mathics.core.atoms import Integer
from mathics.core.exceptions import MessageException
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol, SymbolList
from mathics.core.systemsymbols import SymbolSpan


def _pspec_span_to_tuple(pspec, expr):
    """
    This function takes an expression and a Mathics
    `Span` Expression and returns a tuple with the 0-based positions
    of the elements.

    As in WMA, an end that is left out or given as `All` is -1, the last
    position, whatever the step: `{1, 2, 3}[[;; ;; -1]] = ...` cannot take
    positions 1 through -1. A span may select nothing only next to the
    elements (`3;;2`, `6;;5` and `1;;-6` in a list of 5); anything else
    that reaches outside the list raises `Part::take`.
    """
    elements = pspec.elements
    if len(elements) > 3:
        raise MessageException("Part", "span", pspec)
    length = len(expr.elements)
    start = elements[0].int_value if len(elements) > 0 else 1
    stop = -1
    if len(elements) > 1 and elements[1].get_name() != "System`All":
        stop = elements[1].int_value
    step = elements[2].int_value if len(elements) > 2 else 1

    if start is None or stop is None or step is None or step == 0:
        raise MessageException("Part", "span", pspec)

    # Negative positions count from the end.
    first = start + length + 1 if start < 0 else start
    last = stop + length + 1 if stop < 0 else stop
    direction = 1 if step > 0 else -1
    if last == first - direction:
        in_range = 1 <= first <= length + 1 and 0 <= last <= length + 1
    else:
        in_range = (
            1 <= first <= length
            and 1 <= last <= length
            and (last - first) * direction >= 0
        )
    if not in_range:
        raise MessageException(
            "Part", "take", Integer(start), Integer(stop), _message_target(expr)
        )
    return tuple(k - 1 for k in range(first, last + direction, step))


def _message_target(expr):
    """The expression to show in a message about the parts of `expr`."""
    if type(expr) is ExpressionPointer:
        return expr.parent if expr.position is None else expr.to_expression()
    return expr


def _copy(expr: Expression) -> Expression:
    """A new expression with the head and elements of `expr`, to be changed
    in place of `expr`."""
    if isinstance(expr, ListExpression):
        # What is known of the elements stays true of the copy, and
        # ListExpression.set_element keeps it up to date.
        return expr.shallow_copy()
    # Expression.set_element drops the elements properties and the cache
    # of the copy, so Expression.shallow_copy, which rebuilds the cache,
    # would only do work that is thrown away.
    return Expression(expr.head, *expr.elements)


def _is_atom(expr) -> bool:
    """`expr` is an atom; `expr` may also be an `ExpressionPointer` or a `SubExpression`."""
    if isinstance(expr, (ExpressionPointer, SubExpression)):
        return expr.is_atom()
    return isinstance(expr, Atom)


def _part_positions(pspec, expr):
    """
    Convert the part specification `pspec` of `expr` into a 1-based
    position (0 is the head) when it selects a single part, or into a
    tuple of 1-based positions when it selects several (`All`, a list of
    integers or a `Span`). Negative positions count from the end.

    Raises `Part::partw` for a position that `expr` does not have.
    """
    length = 0 if _is_atom(expr) else len(expr.elements)

    def checked(k: int) -> int:
        position = length + 1 + k if k < 0 else k
        # Position 0 is the head; a negative position never reaches it:
        # -4 in a list of 3 does not exist.
        if not (1 if k < 0 else 0) <= position <= length:
            raise MessageException("Part", "partw", Integer(k), _message_target(expr))
        return position

    if type(pspec) is Integer:
        return checked(pspec.value)
    if isinstance(pspec, Symbol) and pspec.get_name() == "System`All":
        return tuple(range(1, length + 1))
    if isinstance(pspec, Expression):
        if pspec.has_form(SymbolList, None):
            if not all(type(element) is Integer for element in pspec.elements):
                raise MessageException("Part", "pkspec1", pspec)
            return tuple(checked(element.value) for element in pspec.elements)
        if pspec.has_form(SymbolSpan, None):
            return tuple(checked(k + 1) for k in _pspec_span_to_tuple(pspec, expr))
    raise MessageException("Part", "pspec", pspec)


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
            return self.parent.head.elements
        return self.parent.elements[pos - 1].elements

    @elements.setter
    def elements(self, value):
        raise ValueError("ExpressionPointer.elements is write protected.")

    def get_head_name(self):
        return self.head.get_name()

    def is_atom(self):
        pos = self.position
        if pos is None:
            return _is_atom(self.parent)
        elif pos == 0:
            return _is_atom(self.parent.head)
        return _is_atom(self.parent.elements[pos - 1])

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

    def replace(self, new, copied: dict | None = None):
        """
        This method replaces the value pointed out by a `new` value.

        `copied` maps the id of each expression that this assignment has
        already copied to that copy: the copy is not shared, so it is
        changed in place rather than copied again for each part assigned
        (as in m[[1, All]] = 0). The copies are kept in the dict so that
        their ids cannot be reused by other objects.
        """
        if copied is None:
            copied = {}
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
        # Variables to track the parent and the position of that parent.
        current = parent
        current_parent = None
        current_index = None

        # Each expression on the way down is replaced by a copy before it
        # is changed: it may be shared with another value or definition,
        # as in b = a; b[[2, 1]] = x, which must leave a as it was.
        try:
            while pos:
                current_parent = current
                current_index = i
                if i == 0:
                    current = current._head
                    if (
                        isinstance(current, Expression)
                        and copied.get(id(current)) is not current
                    ):
                        current = _copy(current)
                        copied[id(current)] = current
                        current_parent.set_head(current)
                else:
                    current = current.elements[i - 1]
                    if (
                        isinstance(current, Expression)
                        and copied.get(id(current)) is not current
                    ):
                        current = _copy(current)
                        copied[id(current)] = current
                        current_parent.set_element(i - 1, current)
                i = pos.pop()
        except IndexError:
            raise MessageException("Part", "span", pos)

        # Now, current is the subexpression to be modified, and current_parent
        # is the expression that holds it (if exists).
        if i != 0:
            current.set_element(i - 1, new)
        elif isinstance(current, ListExpression) or new is SymbolList:
            # A List cannot take another head, nor an Expression the head
            # List: a new expression takes the place of the old one.
            replacement = Expression(new, *current.elements)
            if new is SymbolList:
                replacement = ListExpression(*current.elements)
            if current_parent is None or not current_index:
                raise MessageException("Part", "partw", Integer(0), current)
            current_parent.set_element(current_index - 1, replacement)
        else:
            current.set_head(new)

        # If the modified subexpression is not the root,
        # invalidate the parent cache.
        if current_parent is not None:
            current_parent._cache = None


class SubExpression:
    """
    This class represents a Subexpression of an existing Expression.
    Assignment to a subexpression results in the change of the original Expression.
    """

    _headp: ExpressionPointer
    _elementsp: list

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

        # Convert the part specification into a 1-based position (0 is
        # the head), or a tuple of them. Every position is checked here,
        # before anything is replaced, so that a part that does not exist
        # leaves the expression unchanged.
        if pos is not None:
            pos = _part_positions(pos, expr)

        if pos is None or type(pos) is int:
            if rem_pos is None:
                return ExpressionPointer(expr, pos)
            else:
                return SubExpression(ExpressionPointer(expr, pos), rem_pos)
        else:
            self = super(SubExpression, cls).__new__(cls)
            self._headp = ExpressionPointer(expr.head, 0)
            self._elementsp = [
                SubExpression(ExpressionPointer(expr, k), rem_pos) for k in pos
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

    def to_expression(self):
        return Expression(
            self._headp.to_expression(),
            *(element.to_expression() for element in self._elementsp),
        )

    def replace(self, new, copied: dict | None = None):
        """
        Assigns `new` to the subexpression, according to the logic of `mathics.eval.list.eol.eval_Part`.

        `copied` is passed on to each `ExpressionPointer.replace`, so that
        an expression on the way to several of the parts is copied once.
        """
        if copied is None:
            copied = {}
        if (
            new.has_form(SymbolList, None) or new.get_head_name() == "System`List"
        ) and len(new.elements) == len(self._elementsp):
            for element, sub_new in zip(self._elementsp, new.elements):
                element.replace(sub_new, copied)
        else:
            for element in self._elementsp:
                element.replace(new, copied)
