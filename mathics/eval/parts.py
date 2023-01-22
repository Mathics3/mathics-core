# -*- coding: utf-8 -*-

"""
Evaluation methods for accessing and manipulating elements in nested lists / expressions
"""

from typing import List

from mathics.core.atoms import Integer, Integer1
from mathics.core.convert.expression import make_expression
from mathics.core.element import BaseElement, BoxElementMixin
from mathics.core.exceptions import (
    InvalidLevelspecError,
    MessageException,
    PartDepthError,
    PartRangeError,
)
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.subexpression import SubExpression
from mathics.core.symbols import Atom, Symbol, SymbolList
from mathics.core.systemsymbols import (
    SymbolDirectedInfinity,
    SymbolInfinity,
    SymbolNothing,
)
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
    """Replace all parts of ``expression`` specified by ``indicies`` with
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


def _parts_all_selector():
    """
    Selector for `System`All` as a part specification.
    """
    start = 1
    stop = None
    step = 1

    def select(inner):
        if isinstance(inner, Atom):
            raise MessageException("Part", "partd")
        py_slice = python_seq(start, stop, step, len(inner.elements))
        if py_slice is None:
            raise MessageException("Part", "take", start, stop, inner)
        return inner.elements[py_slice]

    return select


def _parts_span_selector(pspec):
    """
    Selector for `System`Span` part specification
    """
    if len(pspec.elements) > 3:
        raise MessageException("Part", "span", pspec)
    start = 1
    stop = None
    step = 1
    if len(pspec.elements) > 0:
        start = pspec.elements[0].get_int_value()
    if len(pspec.elements) > 1:
        stop = pspec.elements[1].get_int_value()
        if stop is None:
            if pspec.elements[1].get_name() == "System`All":
                stop = None
            else:
                raise MessageException("Part", "span", pspec)
    if len(pspec.elements) > 2:
        step = pspec.elements[2].get_int_value()

    if start == 0 or stop == 0:
        # index 0 is undefined
        raise MessageException("Part", "span", 0)

    if start is None or step is None:
        raise MessageException("Part", "span", pspec)

    def select(inner):
        if isinstance(inner, Atom):
            raise MessageException("Part", "partd")
        py_slice = python_seq(start, stop, step, len(inner.elements))
        if py_slice is None:
            raise MessageException("Part", "take", start, stop, inner)
        return inner.elements[py_slice]

    return select


def _parts_sequence_selector(pspec):
    """
    Selector for `System`Sequence` part specification
    """
    if not isinstance(pspec, (tuple, list)):
        indices = [pspec]
    else:
        indices = pspec

    for index in indices:
        if not isinstance(index, Integer):
            raise MessageException("Part", "pspec", pspec)

    def select(inner):
        if isinstance(inner, Atom):
            raise MessageException("Part", "partd")

        elements = inner.elements
        n = len(elements)

        for index in indices:
            int_index = index.value

            if int_index == 0:
                yield inner.head
            elif 1 <= int_index <= n:
                yield elements[int_index - 1]
            elif -n <= int_index <= -1:
                yield elements[int_index]
            else:
                raise MessageException("Part", "partw", index, inner)

    return select


def _part_selectors(indices):
    """
    _part_selectors returns a suitable `selector` function according to
    the kind of specifications in `indices`.
    """
    for index in indices:
        if index.has_form("Span", None):
            yield _parts_span_selector(index)
        elif index.get_name() == "System`All":
            yield _parts_all_selector()
        # FIXME: test/package/test_combinatorica.py in the benchmarking+futher-improvements
        # fails with the below test. Isolate and fix.
        # elif isinstance(index, ListExpression):
        elif index.has_form("List", None):
            yield _parts_sequence_selector(index.elements)
        elif isinstance(index, Integer):
            yield _parts_sequence_selector(index), lambda x: x[0]
        else:
            raise MessageException("Part", "pspec", index)


def _list_parts(exprs, selectors, evaluation):
    """
    _list_parts returns a generator of Expressions using selectors to pick out parts of `exprs`.
    If `selectors` is empty then a generator of items is returned.

    If a selector in `selectors` is a tuple it consists of a function to determine whether or
    not to select an expression and a optional function to unwrap the resulting selected expressions.

    `evaluation` is used in  expression restructuring an unwrapped expression when the there a
    unwrapping function in the selector.
    """
    if not selectors:
        for expr in exprs:
            yield expr
    else:
        selector = selectors[0]
        if isinstance(selector, tuple):
            select, unwrap = selector
        else:
            select = selector
            unwrap = None

        for expr in exprs:
            selected = list(select(expr))

            picked = list(_list_parts(selected, selectors[1:], evaluation))

            if unwrap is None:
                expr = expr.restructure(expr.head, picked, evaluation)
                yield expr
            else:
                yield unwrap(picked)


def parts(expr, selectors, evaluation) -> list:
    """
    Select from the `Expression` expr those elements indicated by
    the `selectors`.
    """
    return list(_list_parts([expr], list(selectors), evaluation))[0]


def walk_parts(list_of_list, indices, evaluation, assign_rhs=None):
    """
    walk_parts takes the first element of `list_of_list`, and builds
    a subexpression composed of the expressions at the index positions
    listed in `indices`.

    `assign_rhs`, when not empty, indicates where to the store parts of the composed list.

    list_of_list: a list of `Expression`s with a unique element.

    indices: a list of part specification `Expression`s, including
    `Integer` indices,  `Span` `Expression`s, `List` of `Integer`s
    and

    assign_rhs: None or an `Expression` object.
    """
    walk_list = list_of_list[0]
    indices = [index.evaluate(evaluation) for index in indices]
    if assign_rhs is not None:
        try:
            result = SubExpression(walk_list, indices)
            result.replace(assign_rhs.copy())
            result = result.to_expression()
        except MessageException as e:
            e.message(evaluation)
            return False
        if isinstance(result, Expression):
            result.clear_cache()
        return result
    else:
        try:
            result = parts(walk_list, _part_selectors(indices), evaluation)
        except MessageException as e:
            e.message(evaluation)
            return False
        return result


def is_in_level(current, depth, start=1, stop=None):
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
            head, head_depth = walk_levels(
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
            if element_depth + 1 > depth:
                depth = element_depth + 1
            elements.append(element)
        new_expr = make_expression(head, *elements)

    if is_in_level(current, depth, start, stop):
        if include_pos:
            new_expr = callback(new_expr, cur_pos)
        else:
            new_expr = callback(new_expr)
    return new_expr, depth


def python_levelspec(levelspec):
    def value_to_level(expr):
        value = expr.get_int_value()
        if value is None:
            if expr == Expression(SymbolDirectedInfinity, Integer1):
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


def python_seq(start, stop, step, length):
    """
    Converts mathematica sequence tuple to python slice object.

    Based on David Mashburn's generic slice:
    https://gist.github.com/davidmashburn/9764309
    """
    if step == 0:
        return None

    # special empty case
    if stop is None and length is not None:
        empty_stop = length
    else:
        empty_stop = stop
    if start is not None and empty_stop + 1 == start and step > 0:
        return slice(0, 0, 1)

    if start == 0 or stop == 0:
        return None

    # wrap negative values to postive and convert from 1-based to 0-based
    if start < 0:
        start += length
    else:
        start -= 1

    if stop is None:
        if step < 0:
            stop = 0
        else:
            stop = length - 1
    elif stop < 0:
        stop += length
    else:
        assert stop > 0
        stop -= 1

    # check bounds
    if (
        not 0 <= start < length
        or not 0 <= stop < length
        or step > 0
        and start - stop > 1
        or step < 0
        and stop - start > 1
    ):  # nopep8
        return None

    # include the stop value
    if step > 0:
        stop += 1
    else:
        stop -= 1
        if stop == -1:
            stop = None
        if start == 0:
            start = None

    return slice(start, stop, step)


def convert_seq(seq):
    """
    converts a sequence specification into a (start, stop, step) tuple.
    returns None on failure
    """
    start, stop, step = 1, None, 1
    name = seq.get_name()
    value = seq.get_int_value()
    if name == "System`All":
        pass
    elif name == "System`None":
        stop = 0
    elif value is not None:
        if value > 0:
            stop = value
        else:
            start = value
    elif seq.has_form("List", 1, 2, 3):
        if len(seq.elements) == 1:
            start = stop = seq.elements[0].get_int_value()
            if stop is None:
                return None
        else:
            start = seq.elements[0].get_int_value()
            stop = seq.elements[1].get_int_value()
            if start is None or stop is None:
                return None
        if len(seq.elements) == 3:
            step = seq.elements[2].get_int_value()
            if step is None:
                return None
    else:
        return None
    return (start, stop, step)


def _drop_take_selector(name, seq, sliced):
    seq_tuple = convert_seq(seq)
    if seq_tuple is None:
        raise MessageException(name, "seqs", seq)

    def select(inner):
        start, stop, step = seq_tuple
        if isinstance(inner, Atom):
            py_slice = None
        else:
            py_slice = python_seq(start, stop, step, len(inner.elements))
        if py_slice is None:
            if stop is None:
                stop = SymbolInfinity
            raise MessageException(name, name.lower(), start, stop, inner)
        return sliced(inner.elements, py_slice)

    return select


def _take_span_selector(seq):
    return _drop_take_selector("Take", seq, lambda x, s: x[s])


def _drop_span_selector(seq):
    def sliced(x, s):
        y = list(x[:])
        del y[s]
        return y

    return _drop_take_selector("Drop", seq, sliced)


def deletecases_with_levelspec(expr, pattern, evaluation, levelspec=1, n=-1):
    """
    This function walks the expression `expr` and deleting occurrencies of `pattern`

    If levelspec specifies a number, only those positions with
    `levelspec` "coordinates" are return. By default, it just return
    occurrences in the first level.

    If a tuple (nmin, nmax) is provided, it just return those
    occurrences with a number of "coordinates" between nmin and nmax.
    n indicates the number of occurrences to return. By default, it
    returns all the occurrences.
    """
    nothing = SymbolNothing

    match = Matcher(pattern)
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
    from mathics.builtin.patterns import Matcher

    match = Matcher(pattern)
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
