# -*- coding: utf-8 -*-
"""
Miscellaneous mathics.core utility functions.
"""

import re
import sys
from collections.abc import Generator, Iterable
from itertools import chain
from pathlib import PureWindowsPath
from platform import python_implementation
from typing import Any, Optional, Tuple

from mathics.core.atoms import MachineReal, NumericArray
from mathics.core.element import BaseElement
from mathics.core.symbols import Symbol

IS_PYPY = python_implementation() == "PyPy"
SUBRANGES_GENERATOR_TYPE = Generator[
    Tuple[
        Tuple[BaseElement, ...], Tuple[Tuple[BaseElement, ...], Tuple[BaseElement, ...]]
    ],
    None,
    None,
]
SUBSETS_GENERATOR_TYPE = Generator[
    Tuple[Tuple[Any, ...], Tuple[Tuple[Any, ...], Tuple[Any, ...]]], None, None
]

EMPTY_TUPLE: tuple = tuple()


def canonic_filename(path: str) -> str:
    """
    Canonicalize path. On Microsoft Windows, use PureWidnowsPath() to
    turn backslash "\" to "/". On other platforms we currently, do
    nothing, but we might in the future canonicalize the filename
    further, e.g. via os.path.normpath().
    """
    if sys.platform.startswith("win"):
        # win32 or win64..
        # PureWindowsPath.as_posix() strips trailing "/" .
        dir_suffix = "/" if path.endswith("/") else ""
        path = PureWindowsPath(path).as_posix() + dir_suffix
    # Should we use "os.path.normpath() here?
    return path


# FIXME: These functions are used pattern.py


def permutations(items):
    if not items:
        yield []
    # already_taken = set()
    # first yield identical permutation without recursion
    yield items
    for index in range(len(items)):
        item = items[index]
        # if item not in already_taken:
        for sub in permutations(items[:index] + items[index + 1 :]):
            yield [item] + list(sub)
            # already_taken.add(item)


def strip_string_quotes(s: str) -> str:
    """
    Remove leading and trailing string quotes if they exist.
    Note: we need this too often probably a bad design decision in String.
    """
    return s[1:-1] if len(s) >= 2 and s[0] == s[-1] == '"' else s


def subsets(
    items, min: int, max: Optional[int], included=None, less_first=False
) -> SUBSETS_GENERATOR_TYPE:
    """
    Generate subsets of `items`, in decreasing (or increasing) order of size,
    together with the elements that were left out.

    Each subset is yielded as ``(chosen, (EMPTY_TUPLE, not_chosen))``, where
    ``chosen`` is a tuple holding the selected elements (in their original
    relative order) and ``not_chosen`` is a tuple holding the remaining
    elements (also in their original relative order). The middle
    ``EMPTY_TUPLE`` slot is always empty; it exists to match the calling
    convention shared with other pattern-matching helpers (e.g.
    `expression_pattern_match_element_orderless`), which expect a
    ``(chosen, (used, remaining))``-shaped result.

    Only subsets whose size lies in ``[min, max]`` are produced. If ``min``
    is 0, the empty subset is included too, and is always yielded last,
    regardless of `less_first`.

    Parameters
    ----------
    items:
        The sequence of candidate elements to choose subsets from.
    min:
        The minimum subset size to generate. If 0, the empty subset is
        also generated (see above).
    max:
        The maximum subset size to generate. If None, defaults to
        ``len(items)``.
    included:
        If given, restricts which elements are eligible to be chosen: only
        subsets consisting entirely of elements found in `included` are
        yielded. If None, any element of `items` may be chosen.
    less_first:
        If True, subsets are yielded in increasing order of size (from
        `min` up to `max`). If False (default), they are yielded in
        decreasing order of size (from `max` down to `min`).

    Yields
    ------
    Tuple[Tuple[Any, ...], Tuple[Tuple[Any, ...], Tuple[Any, ...]]]
        Pairs of ``(chosen, (EMPTY_TUPLE, not_chosen))`` as described above,
        one for every valid subset of `items` (subject to `included`),
        ordered by size according to `less_first`.
    """

    add_empty: bool

    if max is None:
        max = len(items)

    if min == 0:
        add_empty = True
        min = 1
    else:
        add_empty = False

    if less_first:
        lengths = list(range(min, max + 1))
    else:
        lengths = list(range(max, min - 1, -1))

    def decide(
        chosen: Tuple[Any, ...],
        not_chosen: Tuple[Any, ...],
        rest: Tuple[Any, ...],
        count: int,
    ) -> Generator[Tuple[Tuple[Any, ...], Tuple[Any, ...]], None, None]:
        if count < 0 or len(rest) < count:
            return
        if count == 0:
            yield chosen, tuple(chain(not_chosen, rest))
        elif len(rest) == count:
            if included is None or all(item in included for item in rest):
                yield tuple(chain(chosen, rest)), not_chosen
        elif rest:
            item = rest[0]
            if included is None or item in included:
                for set in decide(chosen + (item,), not_chosen, rest[1:], count - 1):
                    yield set
            for set in decide(chosen, not_chosen + (item,), rest[1:], count):
                yield set

    for length in lengths:
        for chosen, not_chosen in decide(EMPTY_TUPLE, EMPTY_TUPLE, items, length):
            yield chosen, (EMPTY_TUPLE, not_chosen)

    if add_empty:
        for chosen, not_chosen in decide(EMPTY_TUPLE, EMPTY_TUPLE, items, 0):
            yield chosen, (EMPTY_TUPLE, not_chosen)


def subranges(
    items: Tuple[BaseElement],
    min_count: int,
    max: int,
    *,
    flexible_start: bool = False,
    included: Optional[Iterable] = None,
    less_first: bool = False,
) -> SUBRANGES_GENERATOR_TYPE:
    """
    generator that yields possible divisions of items as
    ([items_inside],([previos_items],[remaining_items]))
    with items_inside of variable lengths.
    If flexible_start, then [previos_items] also has a variable size.
    """
    # TODO: take into account included
    if max is None:
        max = len(items)
    else:
        max = min(max, len(items))

    # Special case: for some reason, here does not work
    # to send the zero length case to the end in general.
    # In particular if we use the same approach that in subsets,
    # this test fails:
    # ReplaceList[{a, b, c}, {___, x__, ___} -> {x}]
    # = {{a}, {a, b}, {a, b, c}, {b}, {b, c}, {c}}
    # With the approach in subsets, we would get
    # = {{b}, {b, c}, {c}, {a}, {a, b}, {a, b, c}}
    #
    if min_count == 0 and max == 1:
        less_first = False

    if less_first:
        lengths_range = range(min_count, max + 1)
    else:
        lengths_range = range(max, min_count - 1, -1)

    if flexible_start:
        lengths = list(lengths_range)
        for start in range(len(items) - max + 1):
            for length in lengths:
                yield (
                    items[start : start + length],
                    (items[:start], items[start + length :]),
                )
    else:
        for length in lengths_range:
            yield (
                items[0:length],
                (items[:0], items[length:]),
            )


def print_expression_tree(
    expr, indent="", marker=lambda expr: "", file=None, approximate=False
):
    """
    Print a Mathics3 Expression as an indented tree.
    Caller may supply a marker function that computes a marker
    to be displayed in the tree for the given node.
    The approximate flag causes numbers to be printed with fewer digits
    and the number of bits of precision (i.e. Real32 vs Real64) to be
    omitted from printing for numpy arrays, to faciliate comparisons
    across systems.
    """
    if file is None:
        file = sys.stdout

    if isinstance(expr, Symbol):
        print(f"{indent}{marker(expr)}{expr}", file=file)
    elif not hasattr(expr, "elements"):
        if isinstance(expr, MachineReal) and approximate:
            # fewer digits
            value = str(round(expr.value * 1e6) / 1e6)
        elif isinstance(expr, NumericArray) and approximate:
            # Real32/64->Real*, Integer32/64->Integer*
            value = re.sub("[0-9]+,", "*,", str(expr))
        else:
            value = str(expr)
        print(f"{indent}{marker(expr)}{expr.get_head()} {value}", file=file)
        if isinstance(expr, NumericArray):
            # numpy provides an abbreviated version of the array
            # it is inherently approximated (i.e. limited precision) in its own way
            na_str = str(expr.value)
            i = indent + "  "
            na_str = i + na_str.replace("\n", "\n" + i)
            print(na_str, file=file)
    else:
        print(f"{indent}{marker(expr)}{expr.head}", file=file)
        for elt in expr.elements:
            print_expression_tree(
                elt, indent + "  ", marker=marker, file=file, approximate=approximate
            )


def print_sympy_tree(expr, indent=""):
    """Print a SymPy Expression as an indented tree"""
    if expr.args:
        print(f"{indent}{expr.func.__name__}")
        for i, arg in enumerate(expr.args):
            print_sympy_tree(arg, indent + "    ")
    else:
        print(f"{indent}{expr.func.__name__}({str(expr)})")
