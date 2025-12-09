# -*- coding: utf-8 -*-
"""
Miscellaneous mathics.core utility functions.
"""

import sys
from itertools import chain
from pathlib import PureWindowsPath
from platform import python_implementation
from typing import Optional

from mathics.core.atoms import NumericArray, MachineReal
from mathics.core.symbols import Symbol

IS_PYPY = python_implementation() == "PyPy"


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


def subsets(items, min: int, max: Optional[int], included=None, less_first=False):
    if max is None:
        max = len(items)
    lengths = list(range(min, max + 1))
    if not less_first:
        lengths = list(reversed(lengths))
    if lengths and lengths[0] == 0:
        lengths = lengths[1:] + [0]

    def decide(chosen, not_chosen, rest, count):
        if count < 0 or len(rest) < count:
            return
        if count == 0:
            yield chosen, list(chain(not_chosen, rest))
        elif len(rest) == count:
            if included is None or all(item in included for item in rest):
                yield list(chain(chosen, rest)), not_chosen
        elif rest:
            item = rest[0]
            if included is None or item in included:
                for set in decide(chosen + [item], not_chosen, rest[1:], count - 1):
                    yield set
            for set in decide(chosen, not_chosen + [item], rest[1:], count):
                yield set

    for length in lengths:
        for chosen, not_chosen in decide([], [], items, length):
            yield chosen, ([], not_chosen)


def subranges(
    items, min_count, max, flexible_start=False, included=None, less_first=False
):
    """
    generator that yields possible divisions of items as
    ([items_inside],([previos_items],[remaining_items]))
    with items_inside of variable lengths.
    If flexible_start, then [previos_items] also has a variable size.
    """
    # TODO: take into account included

    if max is None:
        max = len(items)
    max = min(max, len(items))
    if flexible_start:
        starts = list(range(len(items) - max + 1))
    else:
        starts = (0,)
    for start in starts:
        lengths = list(range(min_count, max + 1))
        if not less_first:
            lengths = reversed(lengths)
        lengths = list(lengths)
        if lengths == [0, 1]:
            lengths = [1, 0]
        for length in lengths:
            yield (
                items[start : start + length],
                (items[:start], items[start + length :]),
            )


def print_expression_tree(expr, indent="", marker=lambda expr: "", file=None):
    """
    Print a Mathics Expression as an indented tree.
    Caller may supply a marker function that computes a marker
    to be displayed in the tree for the given node.
    """
    if file is None:
        file = sys.stdout
    if isinstance(expr, Symbol):
        print(f"{indent}{marker(expr)}{expr}", file=file)
    elif not hasattr(expr, "elements"):
        if isinstance(expr, MachineReal):
            value = f"{expr.value:.8g}"
        else:
            value = str(expr)
        print(f"{indent}{marker(expr)}{expr.get_head()} {value}", file=file)
        if isinstance(expr, NumericArray):
            # numpy provides an abbreviated version of the array
            na_str = str(expr.value)
            i = indent + "  "
            na_str = i + na_str.replace("\n", "\n" + i)
            print(na_str, file=file)
    else:
        print(f"{indent}{marker(expr)}{expr.head}", file=file)
        for elt in expr.elements:
            print_expression_tree(elt, indent + "  ", marker=marker, file=file)


def print_sympy_tree(expr, indent=""):
    """Print a SymPy Expression as an indented tree"""
    if expr.args:
        print(f"{indent}{expr.func.__name__}")
        for i, arg in enumerate(expr.args):
            print_sympy_tree(arg, indent + "    ")
    else:
        print(f"{indent}{expr.func.__name__}({str(expr)})")
