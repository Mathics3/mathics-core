# -*- coding: utf-8 -*-

import re
import sys
from itertools import chain

# Remove "try"  below and adjust return type after Python 3.6 support is dropped.
try:
    from re import Pattern
except ImportError:
    Pattern = re._pattern_type


IS_PYPY = "__pypy__" in sys.builtin_module_names

# FIXME: These functions are used pattern.py


def permutations(items, without_duplicates=True):
    if not items:
        yield []
    # already_taken = set()
    # first yield identical permutation without recursion
    yield items
    for index in range(len(items)):
        item = items[index]
        # if item not in already_taken:
        for sub in permutations(items[:index] + items[index + 1 :]):
            yield [item] + sub
            # already_taken.add(item)


def subsets(items, min, max, included=None, less_first=False):
    if max is None:
        max = len(items)
    lengths = list(range(min, max + 1))
    if not less_first:
        lengths = reversed(lengths)
    lengths = list(lengths)
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
