from typing import List

from mathics.core.atoms import Integer
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import MessageException
from mathics.core.expression import Expression
from mathics.core.subexpression import SubExpression
from mathics.core.symbols import Atom
from mathics.core.systemsymbols import SymbolInfinity


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


def drop_take_selector(name, seq, sliced):
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


def eval_Part(
    list_of_list: list, indices: List[Integer], evaluation: Evaluation, assign_rhs=None
):
    """
    eval_part takes the first element of `list_of_list`, and builds
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
            result = parts(walk_list, part_selectors(indices), evaluation)
        except MessageException as e:
            e.message(evaluation)
            return False
        return result


def list_parts(exprs, selectors, evaluation):
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

            picked = list(list_parts(selected, selectors[1:], evaluation))

            if unwrap is None and hasattr(expr, "restructure"):
                expr = expr.restructure(expr.head, picked, evaluation)
                yield expr
            else:
                yield unwrap(picked)


def parts_all_selector():
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


def part_selectors(indices):
    """
    part_selectors returns a suitable `selector` function according to
    the kind of specifications in `indices`.
    """
    for index in indices:
        if index.has_form("Span", None):
            yield parts_span_selector(index)
        elif index.get_name() == "System`All":
            yield parts_all_selector()
        # FIXME: test/package/test_combinatorica.py in the benchmarking+futher-improvements
        # fails with the below test. Isolate and fix.
        # elif isinstance(index, ListExpression):
        elif index.has_form("List", None):
            yield parts_sequence_selector(index.elements)
        elif isinstance(index, Integer):
            yield parts_sequence_selector(index), lambda x: x[0]
        else:
            raise MessageException("Part", "pspec", index)


def parts(expr, selectors, evaluation) -> list:
    """
    Select from the `Expression` expr those elements indicated by
    the `selectors`.
    """
    return list(list_parts([expr], list(selectors), evaluation))[0]


def parts_sequence_selector(pspec):
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
        if not hasattr(inner, "elements"):
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


def parts_span_selector(pspec):
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


def python_seq(start: int, stop: int, step: int, length: int):
    """
    Converts Mathics3 sequence tuple to python slice object.

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

    # wrap negative values to positive and convert from 1-based to 0-based
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


def take_span_selector(seq):
    return drop_take_selector("Take", seq, lambda x, s: x[s])


def drop_span_selector(seq):
    def sliced(x, s):
        y = list(x[:])
        del y[s]
        return y

    return drop_take_selector("Drop", seq, sliced)
