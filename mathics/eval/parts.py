# -*- coding: utf-8 -*-

"""
Evaluation methods for accessing and manipulating elements in nested lists / expressions
"""

from typing import List, Optional, Tuple

from mathics.core.atoms import Integer
from mathics.core.convert.expression import make_expression
from mathics.core.element import BaseElement, BoxElementMixin
from mathics.core.exceptions import (
    InvalidLevelspecError,
    PartDepthError,
    PartRangeError,
)
from mathics.core.expression import Expression
from mathics.core.expression_predefined import MATHICS3_INFINITY
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol, SymbolList
from mathics.core.systemsymbols import SymbolNothing
from mathics.eval.patterns import Matcher


def get_part(expression: BaseElement, indices: List[int]) -> BaseElement:
    """Extract part of ``expression`` specified by ``indices`` and
    return that.
    """

    def get_subpart(sub_expression: BaseElement, sub_indices: List[int]) -> BaseElement:
        """Recursive work-horse portion of ``get_part()`` that extracts pieces
        of ``sub_expression`` as directed by ``sub_indices``.

        The variables ``sub_expression`` and ``sub_indices`` are smaller parts of
        ``expression`` and ``indices`` respectively, which are defined in the outer level.
        """
        if not sub_indices:
            return sub_expression

        if isinstance(sub_expression, Atom):
            raise PartDepthError(sub_indices[0])

        pos = sub_indices[0]
        elements = sub_expression.elements
        try:
            if pos > 0:
                part = elements[pos - 1]
            elif pos == 0:
                part = sub_expression.get_head()
            else:
                part = elements[pos]
        except IndexError:
            raise PartRangeError
        return get_subpart(part, sub_indices[1:])

    return get_subpart(expression, indices).copy()


def set_part(expression, indices: List[int], new_atom: Atom) -> BaseElement:
    """Replace all parts of ``expression`` specified by ``indices`` with
    ``new_atom`. Return the modified compound expression.
    """

    def set_subpart(sub_expression, sub_indices: List[int]) -> BaseElement:
        """
        Recursive work-horse portion of ``set_part()`` that replaces those pieces
        of ``sub_expression`` with outer variable ``new_atom`` as directed by ``sub_indices``.

        The variables ``sub_expression`` and ``sub_indices`` are smaller parts of
        ``expression`` and ``indices`` respectively, which are defined in the outer level.
        """
        if len(sub_indices) > 1:
            pos = sub_indices[0]
            if isinstance(sub_expression, Atom):
                raise PartDepthError
            try:
                if pos > 0:
                    part = sub_expression.elements[pos - 1]
                elif pos == 0:
                    part = sub_expression.get_head()
                else:
                    part = sub_expression.elements[pos]
            except IndexError:
                raise PartRangeError
            set_subpart(part, sub_indices[1:])
            return sub_expression
        elif len(sub_indices) == 1:
            pos = sub_indices[0]
            if isinstance(sub_expression, Atom):
                raise PartDepthError
            try:
                if pos > 0:
                    sub_expression.set_element(pos - 1, new_atom)
                elif pos == 0:
                    # We may have to replace the entire ``expression``
                    # variable when changing position 0 or Head. This
                    # happens when the before and after are
                    # class objects are different.

                    # Right now, we need to only worry about
                    # converting between ``Expression`` and
                    # ``ListExpression`` or vice vera.  In the code
                    # below, we make use of the fact that a
                    # ``ListExpression``'s Head is ``SymbolList``.
                    head = sub_expression.head
                    if head == new_atom:
                        # Nothing to modify
                        pass
                    elif new_atom == SymbolList and head != SymbolList:
                        sub_expression = ListExpression(*sub_expression.elements)
                    elif new_atom not in (SymbolList,) and head in (SymbolList,):
                        sub_expression = Expression(new_atom, *sub_expression.elements)
                    else:
                        # Both ``head`` and ``new_atom`` should be the head of
                        # an Expression and not some specialization of that.
                        # Here, we can set or change the head element.
                        sub_expression.set_head(new_atom)
                else:
                    sub_expression.set_element(pos, new_atom)
            except IndexError:
                raise PartRangeError
            return sub_expression

    return set_subpart(expression, indices)


def is_in_level(current, depth, start=1, stop=None) -> bool:
    if stop is None:
        stop = current
    if start < 0:
        start += current + depth + 1
    if stop < 0:
        stop += current + depth + 1
    return start <= current <= stop


def walk_levels(
    expr,
    start=1,
    stop=None,
    current=0,
    heads=False,
    callback=lambda p: p,
    include_pos=False,
    cur_pos=[],
):
    if isinstance(expr, BoxElementMixin):
        expr = expr.to_expression()
    if isinstance(expr, Atom):
        depth = 0
        new_expr = expr
    else:
        depth = 0
        if heads:
            head, _ = walk_levels(
                expr.head,
                start,
                stop,
                current + 1,
                heads,
                callback,
                include_pos,
                cur_pos + [0],
            )
        else:
            head = expr.head

        # FIXME: we could keep track of elements properties here.
        elements = []
        for index, element in enumerate(expr.elements):
            element, element_depth = walk_levels(
                element,
                start,
                stop,
                current + 1,
                heads,
                callback,
                include_pos,
                cur_pos + [index + 1],
            )
            depth = max(element_depth + 1, depth)
            elements.append(element)
        new_expr = make_expression(head, *elements)

    if is_in_level(current, depth, start, stop):
        if include_pos:
            new_expr = callback(new_expr, cur_pos)
        else:
            new_expr = callback(new_expr)
    return new_expr, depth


def python_levelspec(levelspec) -> Tuple[int, Optional[int]]:
    def value_to_level(expr) -> Optional[int]:
        value = expr.get_int_value()
        if value is None:
            if expr.sameQ(MATHICS3_INFINITY):
                return None
            else:
                raise InvalidLevelspecError
        else:
            return value

    # FIXME: Something in ExportString prevents using isinstance(levelspec, ListExpression).
    # Track this down and fix.
    if levelspec.has_form("List", None):
        values = [value_to_level(element) for element in levelspec.elements]
        if len(values) == 1:
            return values[0], values[0]
        elif len(values) == 2:
            return values[0], values[1]
        else:
            raise InvalidLevelspecError
    elif isinstance(levelspec, Symbol) and levelspec.get_name() == "System`All":
        return 0, None
    else:
        return 1, value_to_level(levelspec)


def deletecases_with_levelspec(expr, pattern, evaluation, levelspec=1, n=-1):
    """
    This function walks the expression `expr` and deleting occurrences of `pattern`

    If levelspec specifies a number, only those positions with
    `levelspec` "coordinates" are return. By default, it just return
    occurrences in the first level.

    If a tuple (nmin, nmax) is provided, it just return those
    occurrences with a number of "coordinates" between nmin and nmax.
    n indicates the number of occurrences to return. By default, it
    returns all the occurrences.
    """
    nothing = SymbolNothing

    match = Matcher(pattern, evaluation)
    match = match.match
    if type(levelspec) is int:
        lsmin = 1
        lsmax = levelspec + 1
    else:
        lsmin = levelspec[0]
        if levelspec[1]:
            lsmax = levelspec[1] + 1
        else:
            lsmax = -1
    tree = [[expr]]
    changed_marks = [
        [False],
    ]
    curr_index = [0]

    while curr_index[0] != 1:
        # If the end of the branch is reached, or no more elements to delete out
        if curr_index[-1] == len(tree[-1]) or n == 0:
            elements = tree[-1]
            tree.pop()
            # check if some of the elements was changed
            changed = any(changed_marks[-1])
            changed_marks.pop()
            if changed:
                elements = [element for element in elements if element is not nothing]
            curr_index.pop()
            if len(curr_index) == 0:
                break
            idx = curr_index[-1]
            changed = changed or changed_marks[-1][idx]
            changed_marks[-1][idx] = changed
            if changed:
                head = tree[-1][curr_index[-1]].get_head()
                tree[-1][idx] = make_expression(head, *elements)
            if len(curr_index) == 0:
                break
            curr_index[-1] = curr_index[-1] + 1
            continue
        curr_element = tree[-1][curr_index[-1]]
        if match(curr_element, evaluation) and (len(curr_index) > lsmin):
            tree[-1][curr_index[-1]] = nothing
            changed_marks[-1][curr_index[-1]] = True
            curr_index[-1] = curr_index[-1] + 1
            n = n - 1
            continue
        if isinstance(curr_element, Atom) or lsmax == len(curr_index):
            curr_index[-1] = curr_index[-1] + 1
            continue
        else:
            tree.append(list(curr_element.elements))
            changed_marks.append([False for s in tree[-1]])
            curr_index.append(0)
    return tree[0][0]


def find_matching_indices_with_levelspec(expr, pattern, evaluation, levelspec=1, n=-1):
    """
    This function walks the expression `expr` looking for a pattern `pattern`
    and returns the positions of each occurrence.

    If levelspec specifies a number, only those positions with
    `levelspec` "coordinates" are return. By default, it just return
    occurrences in the first level.

    If a tuple (nmin, nmax) is provided, it just return those
    occurrences with a number of "coordinates" between nmin and nmax.
    n indicates the number of occurrences to return. By default, it
    returns all the occurrences.
    """

    match = Matcher(pattern, evaluation)
    match = match.match
    if type(levelspec) is int:
        lsmin = 0
        lsmax = levelspec
    else:
        lsmin = levelspec[0]
        lsmax = levelspec[1]
    tree = [expr.elements]
    curr_index = [0]
    found = []
    while len(tree) > 0:
        if n == 0:
            break
        if curr_index[-1] == len(tree[-1]):
            curr_index.pop()
            tree.pop()
            if len(curr_index) != 0:
                curr_index[-1] = curr_index[-1] + 1
            continue
        curr_element = tree[-1][curr_index[-1]]
        if match(curr_element, evaluation) and (len(curr_index) >= lsmin):
            found.append([Integer(i) for i in curr_index])
            curr_index[-1] = curr_index[-1] + 1
            n = n - 1
            continue
        if isinstance(curr_element, Atom) or lsmax == len(curr_index):
            curr_index[-1] = curr_index[-1] + 1
            continue
        else:
            tree.append(curr_element.elements)
            curr_index.append(0)
    return found
