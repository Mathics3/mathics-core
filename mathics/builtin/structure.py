# -*- coding: utf-8 -*-
"""
Structural Operations
"""

from typing import Iterable

from mathics.builtin.base import (
    Builtin,
    Predefined,
    BinaryOperator,
    MessageException,
)
from mathics.builtin.exceptions import InvalidLevelspecError, PartRangeError
from mathics.core.atoms import (
    Integer,
    Integer0,
    Integer1,
    Rational,
)
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import Pattern
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolNull,
    SymbolFalse,
    SymbolTrue,
)

from mathics.core.systemsymbols import SymbolDirectedInfinity, SymbolMap, SymbolRule

from mathics.builtin.lists import (
    python_levelspec,
    walk_levels,
    List,
)

import platform

if platform.python_implementation() == "PyPy":
    bytecount_support = False
else:
    from .pympler.asizeof import asizeof as count_bytes

    bytecount_support = True

SymbolMapThread = Symbol("MapThread")
SymbolOperate = Symbol("Operate")
SymbolSortBy = Symbol("SortBy")


class SortBy(Builtin):
    """
    <dl>
    <dt>'SortBy[$list$, $f$]'
    <dd>sorts $list$ (or the elements of any other expression) according to canonical ordering of the keys that are
    extracted from the $list$'s elements using $f. Chunks of elements that appear the same under $f are sorted
    according to their natural order (without applying $f).
    <dt>'SortBy[$f$]'
    <dd>creates an operator function that, when applied, sorts by $f.
    </dl>

    >> SortBy[{{5, 1}, {10, -1}}, Last]
    = {{10, -1}, {5, 1}}

    >> SortBy[Total][{{5, 1}, {10, -9}}]
    = {{10, -9}, {5, 1}}
    """

    messages = {
        "list": "List expected at position `2` in `1`.",
        "func": "Function expected at position `2` in `1`.",
    }

    rules = {
        "SortBy[f_]": "SortBy[#, f]&",
    }

    summary_text = "sort by the values of a function applied to elements"

    def apply(self, li, f, evaluation):
        "SortBy[li_, f_]"

        if isinstance(li, Atom):
            return evaluation.message("Sort", "normal")
        elif li.get_head_name() != "System`List":
            expr = Expression(SymbolSortBy, li, f)
            return evaluation.message(self.get_name(), "list", expr, 1)
        else:
            keys_expr = Expression(SymbolMap, f, li).evaluate(evaluation)  # precompute:
            # even though our sort function has only (n log n) comparisons, we should
            # compute f no more than n times.

            if (
                keys_expr is None
                or keys_expr.get_head_name() != "System`List"
                or len(keys_expr.elements) != len(li.elements)
            ):
                expr = Expression(SymbolSortBy, li, f)
                return evaluation.message("SortBy", "func", expr, 2)

            keys = keys_expr.elements
            raw_keys = li.elements

            class Key:
                def __init__(self, index):
                    self.index = index

                def __gt__(self, other):
                    kx, ky = keys[self.index], keys[other.index]
                    if kx > ky:
                        return True
                    elif kx < ky:
                        return False
                    else:  # if f(x) == f(y), resort to x < y?
                        return raw_keys[self.index] > raw_keys[other.index]

            # we sort a list of indices. after sorting, we reorder the elements.
            new_indices = sorted(list(range(len(raw_keys))), key=Key)
            new_elements = [raw_keys[i] for i in new_indices]  # reorder elements
            return li.restructure(li.head, new_elements, evaluation)


class BinarySearch(Builtin):
    """
    <dl>
    <dt>'CombinatoricaOld`BinarySearch[$l$, $k$]'
        <dd>searches the list $l$, which has to be sorted, for key $k$ and returns its index in $l$. If $k$ does not
        exist in $l$, 'BinarySearch' returns (a + b) / 2, where a and b are the indices between which $k$ would have
        to be inserted in order to maintain the sorting order in $l$. Please note that $k$ and the elements in $l$
        need to be comparable under a strict total order (see https://en.wikipedia.org/wiki/Total_order).

    <dt>'CombinatoricaOld`BinarySearch[$l$, $k$, $f$]'
        <dd>the index of $k in the elements of $l$ if $f$ is applied to the latter prior to comparison. Note that $f$
        needs to yield a sorted sequence if applied to the elements of $l.
    </dl>

    >> CombinatoricaOld`BinarySearch[{3, 4, 10, 100, 123}, 100]
     = 4

    >> CombinatoricaOld`BinarySearch[{2, 3, 9}, 7] // N
     = 2.5

    >> CombinatoricaOld`BinarySearch[{2, 7, 9, 10}, 3] // N
     = 1.5

    >> CombinatoricaOld`BinarySearch[{-10, 5, 8, 10}, -100] // N
     = 0.5

    >> CombinatoricaOld`BinarySearch[{-10, 5, 8, 10}, 20] // N
     = 4.5

    >> CombinatoricaOld`BinarySearch[{{a, 1}, {b, 7}}, 7, #[[2]]&]
     = 2
    """

    context = "CombinatoricaOld`"

    rules = {
        "CombinatoricaOld`BinarySearch[l_List, k_] /; Length[l] > 0": "CombinatoricaOld`BinarySearch[l, k, Identity]"
    }

    summary_text = "search a sorted list for a key"

    def apply(self, l, k, f, evaluation):
        "CombinatoricaOld`BinarySearch[l_List, k_, f_] /; Length[l] > 0"

        elements = l.elements

        lower_index = 1
        upper_index = len(elements)

        if (
            lower_index > upper_index
        ):  # empty list l? Length[l] > 0 condition should guard us, but check anyway
            return Symbol("$Aborted")

        # "transform" is a handy wrapper for applying "f" or nothing
        if f.get_name() == "System`Identity":

            def transform(x):
                return x

        else:

            def transform(x):
                return Expression(f, x).evaluate(evaluation)

        # loop invariants (true at any time in the following loop):
        # (1) lower_index <= upper_index
        # (2) k > elements[i] for all i < lower_index
        # (3) k < elements[i] for all i > upper_index
        while True:
            pivot_index = (lower_index + upper_index) >> 1  # i.e. a + (b - a) // 2
            # as lower_index <= upper_index, lower_index <= pivot_index <= upper_index
            pivot = transform(elements[pivot_index - 1])  # 1-based to 0-based

            # we assume a trichotomous relation: k < pivot, or k = pivot, or k > pivot
            if k < pivot:
                if pivot_index == lower_index:  # see invariant (2), to see that
                    # k < elements[pivot_index] and k > elements[pivot_index - 1]
                    return Rational((pivot_index - 1) + pivot_index, 2)
                upper_index = pivot_index - 1
            elif k == pivot:
                return Integer(pivot_index)
            else:  # k > pivot
                if pivot_index == upper_index:  # see invariant (3), to see that
                    # k > elements[pivot_index] and k < elements[pivot_index + 1]
                    return Rational(pivot_index + (pivot_index + 1), 2)
                lower_index = pivot_index + 1


class PatternsOrderedQ(Builtin):
    """
    <dl>
    <dt>'PatternsOrderedQ[$patt1$, $patt2$]'
        <dd>returns 'True' if pattern $patt1$ would be applied before
        $patt2$ according to canonical pattern ordering.
    </dl>

    >> PatternsOrderedQ[x__, x_]
     = False
    >> PatternsOrderedQ[x_, x__]
     = True
    >> PatternsOrderedQ[b, a]
     = True
    """

    summary_text = "test whether patterns are canonically sorted"

    def apply(self, p1, p2, evaluation):
        "PatternsOrderedQ[p1_, p2_]"

        if p1.get_sort_key(True) <= p2.get_sort_key(True):
            return SymbolTrue
        else:
            return SymbolFalse


class OrderedQ(Builtin):
    """
    <dl>
    <dt>'OrderedQ[{$a$, $b$}]'
        <dd>is 'True' if $a$ sorts before $b$ according to canonical
        ordering.
    </dl>

    >> OrderedQ[{a, b}]
     = True
    >> OrderedQ[{b, a}]
     = False
    """

    summary_text = "test whether elements are canonically sorted"

    def apply(self, expr, evaluation):
        "OrderedQ[expr_]"

        for index, value in enumerate(expr.elements[:-1]):
            if expr.elements[index] <= expr.elements[index + 1]:
                continue
            else:
                return SymbolFalse
        return SymbolTrue


class Order(Builtin):
    """
    <dl>
    <dt>'Order[$x$, $y$]'
        <dd>returns a number indicating the canonical ordering of $x$ and $y$. 1 indicates that $x$ is before $y$,
        -1 that $y$ is before $x$. 0 indicates that there is no specific ordering. Uses the same order as 'Sort'.
    </dl>

    >> Order[7, 11]
     = 1

    >> Order[100, 10]
     = -1

    >> Order[x, z]
     = 1

    >> Order[x, x]
     = 0
    """

    summary_text = "canonical ordering of expressions"

    def apply(self, x, y, evaluation):
        "Order[x_, y_]"
        if x < y:
            return Integer1
        elif x > y:
            return Integer(-1)
        else:
            return Integer0


class Head(Builtin):
    """
    <dl>
    <dt>'Head[$expr$]'
        <dd>returns the head of the expression or atom $expr$.
    </dl>

    >> Head[a * b]
     = Times
    >> Head[6]
     = Integer
    >> Head[x]
     = Symbol
    """

    summary_text = "the head of the expression"

    def apply(self, expr, evaluation):
        "Head[expr_]"

        return expr.get_head()


class ApplyLevel(BinaryOperator):
    """
    <dl>
      <dt>'ApplyLevel[$f$, $expr$]'

      <dt>'$f$ @@@ $expr$'
      <dd>is equivalent to 'Apply[$f$, $expr$, {1}]'.
    </dl>

    >> f @@@ {{a, b}, {c, d}}
     = {f[a, b], f[c, d]}
    """

    grouping = "Right"
    operator = "@@@"
    precedence = 620

    rules = {
        "ApplyLevel[f_, expr_]": "Apply[f, expr, {1}]",
    }

    summary_text = "apply a function to a list, at the top level"


class Apply(BinaryOperator):
    """
    <dl>
      <dt>'Apply[$f$, $expr$]'

      <dt>'$f$ @@ $expr$'
      <dd>replaces the head of $expr$ with $f$.

      <dt>'Apply[$f$, $expr$, $levelspec$]'
      <dd>applies $f$ on the parts specified by $levelspec$.
    </dl>

    >> f @@ {1, 2, 3}
     = f[1, 2, 3]
    >> Plus @@ {1, 2, 3}
     = 6

    The head of $expr$ need not be 'List':
    >> f @@ (a + b + c)
     = f[a, b, c]

    Apply on level 1:
    >> Apply[f, {a + b, g[c, d, e * f], 3}, {1}]
     = {f[a, b], f[c, d, e f], 3}
    The default level is 0:
    >> Apply[f, {a, b, c}, {0}]
     = f[a, b, c]

    Range of levels, including negative level (counting from bottom):
    >> Apply[f, {{{{{a}}}}}, {2, -3}]
     = {{f[f[{a}]]}}

    Convert all operations to lists:
    >> Apply[List, a + b * c ^ e * f[g], {0, Infinity}]
     = {a, {b, {g}, {c, e}}}

    #> Apply[f, {a, b, c}, x+y]
     : Level specification x + y is not of the form n, {n}, or {m, n}.
     = Apply[f, {a, b, c}, x + y]
    """

    summary_text = "apply a function to a list, at specified levels"
    operator = "@@"
    precedence = 620
    grouping = "Right"

    options = {
        "Heads": "False",
    }

    def apply_invalidlevel(self, f, expr, ls, evaluation, options={}):
        "Apply[f_, expr_, ls_, OptionsPattern[Apply]]"

        evaluation.message("Apply", "level", ls)

    def apply(self, f, expr, ls, evaluation, options={}):
        """Apply[f_, expr_, Optional[Pattern[ls, _?LevelQ], {0}],
        OptionsPattern[Apply]]"""

        try:
            start, stop = python_levelspec(ls)
        except InvalidLevelspecError:
            evaluation.message("Apply", "level", ls)
            return

        def callback(level):
            if isinstance(level, Atom):
                return level
            else:
                return Expression(f, *level.elements)

        heads = self.get_option(options, "Heads", evaluation) is SymbolTrue
        result, depth = walk_levels(expr, start, stop, heads=heads, callback=callback)

        return result


class Map(BinaryOperator):
    """
    <dl>
      <dt>'Map[$f$, $expr$]' or '$f$ /@ $expr$'
      <dd>applies $f$ to each part on the first level of $expr$.

      <dt>'Map[$f$, $expr$, $levelspec$]'
      <dd>applies $f$ to each level specified by $levelspec$ of $expr$.
    </dl>

    >> f /@ {1, 2, 3}
     = {f[1], f[2], f[3]}
    >> #^2& /@ {1, 2, 3, 4}
     = {1, 4, 9, 16}

    Map $f$ on the second level:
    >> Map[f, {{a, b}, {c, d, e}}, {2}]
     = {{f[a], f[b]}, {f[c], f[d], f[e]}}

    Include heads:
    >> Map[f, a + b + c, Heads->True]
     = f[Plus][f[a], f[b], f[c]]

    #> Map[f, expr, a+b, Heads->True]
     : Level specification a + b is not of the form n, {n}, or {m, n}.
     = Map[f, expr, a + b, Heads -> True]
    """

    summary_text = "map a function over a list, at specified levels"
    operator = "/@"
    precedence = 620
    grouping = "Right"

    options = {
        "Heads": "False",
    }

    def apply_invalidlevel(self, f, expr, ls, evaluation, options={}):
        "Map[f_, expr_, ls_, OptionsPattern[Map]]"

        evaluation.message("Map", "level", ls)

    def apply_level(self, f, expr, ls, evaluation, options={}):
        """Map[f_, expr_, Optional[Pattern[ls, _?LevelQ], {1}],
        OptionsPattern[Map]]"""

        try:
            start, stop = python_levelspec(ls)
        except InvalidLevelspecError:
            evaluation.message("Map", "level", ls)
            return

        def callback(level):
            return Expression(f, level)

        heads = self.get_option(options, "Heads", evaluation) is SymbolTrue
        result, depth = walk_levels(expr, start, stop, heads=heads, callback=callback)

        return result


class MapAt(Builtin):
    """
    <dl>
      <dt>'MapAt[$f$, $expr$, $n$]'
      <dd>applies $f$ to the element at position $n$ in $expr$. If $n$ is negative, the position is counted from the end.

      <dt>'MapAt[f, $exp$r, {$i$, $j$ ...}]'
      <dd>applies $f$ to the part of $expr$ at position {$i$, $j$, ...}.

      <dt>'MapAt[$f$,$pos$]'
      <dd>represents an operator form of MapAt that can be applied to an expression.
    </dl>

    Map $f$ onto the part at position 2:
    >> MapAt[f, {a, b, c, d}, 2]
     = {a, f[b], c, d}

    Map $f$ onto multiple parts:
    >> MapAt[f, {a, b, c, d}, {{1}, {4}}]
     = {f[a], b, c, f[d]}

    Map $f$ onto the at the end:
    >> MapAt[f, {a, b, c, d}, -1]
     = {a, b, c, f[d]}

     Map $f$ onto an association:
    >> MapAt[f, <|"a" -> 1, "b" -> 2, "c" -> 3, "d" -> 4, "e" -> 5|>, 3]
     = {a -> 1, b -> 2, c -> f[3], d -> 4, e -> 5}

    Use negative position in an association:
    >> MapAt[f, <|"a" -> 1, "b" -> 2, "c" -> 3, "d" -> 4|>, -3]
     = {a -> 1, b -> f[2], c -> 3, d -> 4}

    Use the operator form of MapAt:
    >> MapAt[f, 1][{a, b, c, d}]
     = {f[a], b, c, d}
    """

    summary_text = "map a function at particular positions"
    rules = {
        "MapAt[f_, pos_][expr_]": "MapAt[f, expr, pos]",
    }

    def apply(self, f, expr, args, evaluation, options={}):
        "MapAt[f_, expr_, args_]"

        m = len(expr.elements)

        def map_at_one(i, elements):
            if 1 <= i <= m:
                j = i - 1
            elif -m <= i <= -1:
                j = m + i
            else:
                raise PartRangeError
            replace_element = new_elements[j]
            if hasattr(replace_element, "head") and replace_element.head is Symbol(
                "System`Rule"
            ):
                new_elements[j] = Expression(
                    SymbolRule,
                    replace_element.elements[0],
                    Expression(f, replace_element.elements[1]),
                )
            else:
                new_elements[j] = Expression(f, replace_element)
            return new_elements

        a = args.to_python()
        if isinstance(a, int):
            new_elements = list(expr.elements)
            new_elements = map_at_one(a, new_elements)
            return List(*new_elements)
        elif isinstance(a, list):
            new_elements = list(expr.elements)
            for item in a:
                if len(item) == 1 and isinstance(item[0], int):
                    new_elements = map_at_one(item[0], new_elements)
            return List(*new_elements)


class Scan(Builtin):
    """
    <dl>
      <dt>'Scan[$f$, $expr$]'
      <dd>applies $f$ to each element of $expr$ and returns 'Null'.

      <dt>'Scan[$f$, $expr$, $levelspec$]
      <dd>applies $f$ to each level specified by $levelspec$ of $expr$.
    </dl>

    >> Scan[Print, {1, 2, 3}]
     | 1
     | 2
     | 3

    #> Scan[Print, f[g[h[x]]], 2]
     | h[x]
     | g[h[x]]

    #> Scan[Print][{1, 2}]
     | 1
     | 2

    #> Scan[Return, {1, 2}]
     = 1
    """

    summary_text = "scan over every element of a list, applying a function"
    options = {
        "Heads": "False",
    }

    rules = {
        "Scan[f_][expr_]": "Scan[f, expr]",
    }

    def apply_invalidlevel(self, f, expr, ls, evaluation, options={}):
        "Scan[f_, expr_, ls_, OptionsPattern[Map]]"

        return evaluation.message("Map", "level", ls)

    def apply_level(self, f, expr, ls, evaluation, options={}):
        """Scan[f_, expr_, Optional[Pattern[ls, _?LevelQ], {1}],
        OptionsPattern[Map]]"""

        try:
            start, stop = python_levelspec(ls)
        except InvalidLevelspecError:
            evaluation.message("Map", "level", ls)
            return

        def callback(level):
            Expression(f, level).evaluate(evaluation)
            return level

        heads = self.get_option(options, "Heads", evaluation) is SymbolTrue
        result, depth = walk_levels(expr, start, stop, heads=heads, callback=callback)

        return SymbolNull


class MapIndexed(Builtin):
    """
    <dl>
      <dt>'MapIndexed[$f$, $expr$]'
      <dd>applies $f$ to each part on the first level of $expr$, including the part positions in the call to $f$.

      <dt>'MapIndexed[$f$, $expr$, $levelspec$]'
      <dd>applies $f$ to each level specified by $levelspec$ of $expr$.
    </dl>

    >> MapIndexed[f, {a, b, c}]
     = {f[a, {1}], f[b, {2}], f[c, {3}]}

    Include heads (index 0):
    >> MapIndexed[f, {a, b, c}, Heads->True]
     = f[List, {0}][f[a, {1}], f[b, {2}], f[c, {3}]]

    Map on levels 0 through 1 (outer expression gets index '{}'):
    >> MapIndexed[f, a + b + c * d, {0, 1}]
     = f[f[a, {1}] + f[b, {2}] + f[c d, {3}], {}]

    Get the positions of atoms in an expression (convert operations to 'List' first
    to disable 'Listable' functions):
    >> expr = a + b * f[g] * c ^ e;
    >> listified = Apply[List, expr, {0, Infinity}];
    >> MapIndexed[#2 &, listified, {-1}]
     = {{1}, {{2, 1}, {{2, 2, 1}}, {{2, 3, 1}, {2, 3, 2}}}}
    Replace the heads with their positions, too:
    >> MapIndexed[#2 &, listified, {-1}, Heads -> True]
     = {0}[{1}, {2, 0}[{2, 1}, {2, 2, 0}[{2, 2, 1}], {2, 3, 0}[{2, 3, 1}, {2, 3, 2}]]]
    The positions are given in the same format as used by 'Extract'.
    Thus, mapping 'Extract' on the indices given by 'MapIndexed' re-constructs the original expression:
    >> MapIndexed[Extract[expr, #2] &, listified, {-1}, Heads -> True]
     = a + b f[g] c ^ e

    #> MapIndexed[f, {1, 2}, a+b]
     : Level specification a + b is not of the form n, {n}, or {m, n}.
     = MapIndexed[f, {1, 2}, a + b]
    """

    summary_text = "map a function, including index information"
    options = {
        "Heads": "False",
    }

    def apply_invalidlevel(self, f, expr, ls, evaluation, options={}):
        "MapIndexed[f_, expr_, ls_, OptionsPattern[MapIndexed]]"

        evaluation.message("MapIndexed", "level", ls)

    def apply_level(self, f, expr, ls, evaluation, options={}):
        """MapIndexed[f_, expr_, Optional[Pattern[ls, _?LevelQ], {1}],
        OptionsPattern[MapIndexed]]"""

        try:
            start, stop = python_levelspec(ls)
        except InvalidLevelspecError:
            evaluation.message("MapIndexed", "level", ls)
            return

        def callback(level, pos: Iterable):
            return Expression(
                f, level, to_mathics_list(*pos, elements_conversion_fn=Integer)
            )

        heads = self.get_option(options, "Heads", evaluation) is SymbolTrue
        result, depth = walk_levels(
            expr, start, stop, heads=heads, callback=callback, include_pos=True
        )

        return result


class MapThread(Builtin):
    """
    <dl>
      <dt>'MapThread[$f$, {{$a1$, $a2$, ...}, {$b1$, $b2$, ...}, ...}]
      <dd>returns '{$f$[$a1$, $b1$, ...], $f$[$a2$, $b2$, ...], ...}'.

      <dt>'MapThread[$f$, {$expr1$, $expr2$, ...}, $n$]'
      <dd>applies $f$ at level $n$.
    </dl>

    >> MapThread[f, {{a, b, c}, {1, 2, 3}}]
     = {f[a, 1], f[b, 2], f[c, 3]}

    >> MapThread[f, {{{a, b}, {c, d}}, {{e, f}, {g, h}}}, 2]
     = {{f[a, e], f[b, f]}, {f[c, g], f[d, h]}}

    #> MapThread[f, {{a, b}, {c, d}}, {1}]
     : Non-negative machine-sized integer expected at position 3 in MapThread[f, {{a, b}, {c, d}}, {1}].
     = MapThread[f, {{a, b}, {c, d}}, {1}]

    #> MapThread[f, {{a, b}, {c, d}}, 2]
     : Object {a, b} at position {2, 1} in MapThread[f, {{a, b}, {c, d}}, 2] has only 1 of required 2 dimensions.
     = MapThread[f, {{a, b}, {c, d}}, 2]

    #> MapThread[f, {{a}, {b, c}}]
     : Incompatible dimensions of objects at positions {2, 1} and {2, 2} of MapThread[f, {{a}, {b, c}}]; dimensions are 1 and 2.
     = MapThread[f, {{a}, {b, c}}]

    #> MapThread[f, {}]
     = {}

    #> MapThread[f, {a, b}, 0]
     = f[a, b]
    #> MapThread[f, {a, b}, 1]
     :  Object a at position {2, 1} in MapThread[f, {a, b}, 1] has only 0 of required 1 dimensions.
     = MapThread[f, {a, b}, 1]

    ## Behaviour extends MMA
    #> MapThread[f, {{{a, b}, {c}}, {{d, e}, {f}}}, 2]
     = {{f[a, d], f[b, e]}, {f[c, f]}}
    """

    summary_text = "map a function across corresponding elements in multiple lists"
    messages = {
        "intnm": "Non-negative machine-sized integer expected at position `2` in `1`.",
        "mptc": "Incompatible dimensions of objects at positions {2, `1`} and {2, `2`} of `3`; dimensions are `4` and `5`.",
        "mptd": "Object `1` at position {2, `2`} in `3` has only `4` of required `5` dimensions.",
        "list": "List expected at position `2` in `1`.",
    }

    def apply(self, f, expr, evaluation):
        "MapThread[f_, expr_]"

        return self.apply_n(f, expr, None, evaluation)

    def apply_n(self, f, expr, n, evaluation):
        "MapThread[f_, expr_, n_]"

        if n is None:
            n = 1
            full_expr = Expression(SymbolMapThread, f, expr)
        else:
            full_expr = Expression(SymbolMapThread, f, expr, n)
            n = n.get_int_value()

        if n is None or n < 0:
            return evaluation.message("MapThread", "intnm", full_expr, 3)

        if expr.has_form("List", 0):
            return ListExpression()
        if not expr.has_form("List", None):
            return evaluation.message("MapThread", "list", 2, full_expr)

        heads = expr.elements

        def walk(args, depth=0):
            "walk all trees concurrently and build result"
            if depth == n:
                return Expression(f, *args)
            else:
                dim = None
                for i, arg in enumerate(args):
                    if not arg.has_form("List", None):
                        raise MessageException(
                            "MapThread", "mptd", heads[i], i + 1, full_expr, depth, n
                        )
                    if dim is None:
                        dim = len(arg.elements)
                    if dim != len(arg.elements):
                        raise MessageException(
                            "MapThread",
                            "mptc",
                            1,
                            i + 1,
                            full_expr,
                            dim,
                            len(arg.elements),
                        )
                return ListExpression(
                    *[
                        walk([arg.elements[i] for arg in args], depth + 1)
                        for i in range(dim)
                    ]
                )

        try:
            return walk(heads)
        except MessageException as e:
            return e.message(evaluation)


class Thread(Builtin):
    """
    <dl>
      <dt>'Thread[$f$[$args$]]'
      <dd>threads $f$ over any lists that appear in $args$.

      <dt>'Thread[$f$[$args$], $h$]'
      <dd>threads over any parts with head $h$.
    </dl>

    >> Thread[f[{a, b, c}]]
     = {f[a], f[b], f[c]}
    >> Thread[f[{a, b, c}, t]]
     = {f[a, t], f[b, t], f[c, t]}
    >> Thread[f[a + b + c], Plus]
     = f[a] + f[b] + f[c]

    Functions with attribute 'Listable' are automatically threaded over lists:
    >> {a, b, c} + {d, e, f} + g
     = {a + d + g, b + e + g, c + f + g}
    """

    messages = {
        "tdlen": "Objects of unequal length cannot be combined.",
    }

    rules = {
        "Thread[f_[args___]]": "Thread[f[args], List]",
    }

    summary_text = '"thread" a function across lists that appear in its arguments'

    def apply(self, f, args, h, evaluation):
        "Thread[f_[args___], h_]"

        args = args.get_sequence()
        expr = Expression(f, *args)
        threaded, result = expr.thread(evaluation, head=h)
        return result


class FreeQ(Builtin):
    """
    <dl>
      <dt>'FreeQ[$expr$, $x$]'
      <dd>returns 'True' if $expr$ does not contain the expression $x$.
    </dl>

    >> FreeQ[y, x]
     = True
    >> FreeQ[a+b+c, a+b]
     = False
    >> FreeQ[{1, 2, a^(a+b)}, Plus]
     = False
    >> FreeQ[a+b, x_+y_+z_]
     = True
    >> FreeQ[a+b+c, x_+y_+z_]
     = False
    >> FreeQ[x_+y_+z_][a+b]
     = True
    """

    rules = {
        "FreeQ[form_][expr_]": "FreeQ[expr, form]",
    }

    summary_text = (
        "test whether an expression is free of subexpressions matching a pattern"
    )

    def apply(self, expr, form, evaluation):
        "FreeQ[expr_, form_]"

        form = Pattern.create(form)
        if expr.is_free(form, evaluation):
            return SymbolTrue
        else:
            return SymbolFalse


class Flatten(Builtin):
    """
    <dl>
      <dt>'Flatten[$expr$]'
      <dd>flattens out nested lists in $expr$.

      <dt>'Flatten[$expr$, $n$]'
      <dd>stops flattening at level $n$.

      <dt>'Flatten[$expr$, $n$, $h$]'
      <dd>flattens expressions with head $h$ instead of 'List'.
    </dl>

    >> Flatten[{{a, b}, {c, {d}, e}, {f, {g, h}}}]
     = {a, b, c, d, e, f, g, h}
    >> Flatten[{{a, b}, {c, {e}, e}, {f, {g, h}}}, 1]
     = {a, b, c, {e}, e, f, {g, h}}
    >> Flatten[f[a, f[b, f[c, d]], e], Infinity, f]
     = f[a, b, c, d, e]

    >> Flatten[{{a, b}, {c, d}}, {{2}, {1}}]
     = {{a, c}, {b, d}}

    >> Flatten[{{a, b}, {c, d}}, {{1, 2}}]
     = {a, b, c, d}

    Flatten also works in irregularly shaped arrays
    >> Flatten[{{1, 2, 3}, {4}, {6, 7}, {8, 9, 10}}, {{2}, {1}}]
     = {{1, 4, 6, 8}, {2, 7, 9}, {3, 10}}

    #> Flatten[{{1, 2}, {3, 4}}, {{-1, 2}}]
     : Levels to be flattened together in {{-1, 2}} should be lists of positive integers.
     = Flatten[{{1, 2}, {3, 4}}, {{-1, 2}}, List]

    #> Flatten[{a, b}, {{1}, {2}}]
     : Level 2 specified in {{1}, {2}} exceeds the levels, 1, which can be flattened together in {a, b}.
     = Flatten[{a, b}, {{1}, {2}}, List]

    ## Check `n` completion
    #> m = {{{1, 2}, {3}}, {{4}, {5, 6}}};
    #> Flatten[m, {{2}, {1}, {3}, {4}}]
     : Level 4 specified in {{2}, {1}, {3}, {4}} exceeds the levels, 3, which can be flattened together in {{{1, 2}, {3}}, {{4}, {5, 6}}}.
     = Flatten[{{{1, 2}, {3}}, {{4}, {5, 6}}}, {{2}, {1}, {3}, {4}}, List]

    ## Test from issue #251
    #> m = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
    #> Flatten[m, {3}]
     : Level 3 specified in {3} exceeds the levels, 2, which can be flattened together in {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}.
     = Flatten[{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}, {3}, List]

    ## Reproduce strange head behaviour
    #> Flatten[{{1}, 2}, {1, 2}]
     : Level 2 specified in {1, 2} exceeds the levels, 1, which can be flattened together in {{1}, 2}.
     = Flatten[{{1}, 2}, {1, 2}, List]
    #> Flatten[a[b[1, 2], b[3]], {1, 2}, b]     (* MMA BUG: {{1, 2}} not {1, 2}  *)
     : Level 1 specified in {1, 2} exceeds the levels, 0, which can be flattened together in a[b[1, 2], b[3]].
     = Flatten[a[b[1, 2], b[3]], {1, 2}, b]

    #> Flatten[{{1, 2}, {3, {4}}}, {{1, 2, 3}}]
     : Level 3 specified in {{1, 2, 3}} exceeds the levels, 2, which can be flattened together in {{1, 2}, {3, {4}}}.
     = Flatten[{{1, 2}, {3, {4}}}, {{1, 2, 3}}, List]
    """

    messages = {
        "flpi": (
            "Levels to be flattened together in `1` "
            "should be lists of positive integers."
        ),
        "flrep": ("Level `1` specified in `2` should not be repeated."),
        "fldep": (
            "Level `1` specified in `2` exceeds the levels, `3`, "
            "which can be flattened together in `4`."
        ),
    }

    rules = {
        "Flatten[expr_]": "Flatten[expr, Infinity, Head[expr]]",
        "Flatten[expr_, n_]": "Flatten[expr, n, Head[expr]]",
    }

    summary_text = "flatten out any sequence of levels in a nested list"

    def apply_list(self, expr, n, h, evaluation):
        "Flatten[expr_, n_List, h_]"

        # prepare levels
        # find max depth which matches `h`
        expr, max_depth = walk_levels(expr)
        max_depth = {"max_depth": max_depth}  # hack to modify max_depth from callback

        def callback(expr, pos):
            if len(pos) < max_depth["max_depth"] and (
                isinstance(expr, Atom) or expr.head != h
            ):
                max_depth["max_depth"] = len(pos)
            return expr

        expr, depth = walk_levels(expr, callback=callback, include_pos=True, start=0)
        max_depth = max_depth["max_depth"]

        levels = n.to_python()

        # mappings
        if isinstance(levels, list) and all(isinstance(level, int) for level in levels):
            levels = [levels]

        # verify levels is list of lists of positive ints
        if not (isinstance(levels, list) and len(levels) > 0):
            evaluation.message("Flatten", "flpi", n)
            return
        seen_levels = []
        for level in levels:
            if not (isinstance(level, list) and len(level) > 0):
                evaluation.message("Flatten", "flpi", n)
                return
            for r in level:
                if not (isinstance(r, int) and r > 0):
                    evaluation.message("Flatten", "flpi", n)
                    return
                if r in seen_levels:
                    # level repeated
                    evaluation.message("Flatten", "flrep", r)
                    return
                seen_levels.append(r)

        # complete the level spec e.g. {{2}} -> {{2}, {1}, {3}}
        for s in range(1, max_depth + 1):
            if s not in seen_levels:
                levels.append([s])

        # verify specified levels are smaller max depth
        for level in levels:
            for s in level:
                if s > max_depth:
                    evaluation.message("Flatten", "fldep", s, n, max_depth, expr)
                    return

        # assign new indices to each element
        new_indices = {}

        def callback(expr, pos):
            if len(pos) == max_depth:
                new_depth = tuple(tuple(pos[i - 1] for i in level) for level in levels)
                new_indices[new_depth] = expr
            return expr

        expr, depth = walk_levels(expr, callback=callback, include_pos=True)

        # build new tree inserting nodes as needed
        elements = sorted(new_indices.items())

        def insert_element(elements):
            # gather elements into groups with the same leading index
            # e.g. [((0, 0), a), ((0, 1), b), ((1, 0), c), ((1, 1), d)]
            # -> [[(0, a), (1, b)], [(0, c), (1, d)]]
            leading_index = None
            grouped_elements = []
            for index, element in elements:
                if index[0] == leading_index:
                    grouped_elements[-1].append((index[1:], element))
                else:
                    leading_index = index[0]
                    grouped_elements.append([(index[1:], element)])
            # for each group of elements we either insert them into the current level
            # or make a new level and recurse
            new_elements = []
            for group in grouped_elements:
                if len(group[0][0]) == 0:  # bottom level element or leaf
                    assert len(group) == 1
                    new_elements.append(group[0][1])
                else:
                    new_elements.append(Expression(h, *insert_element(group)))

            return new_elements

        return Expression(h, *insert_element(elements))

    def apply(self, expr, n, h, evaluation):
        "Flatten[expr_, n_, h_]"

        if n == Expression(SymbolDirectedInfinity, Integer1):
            n = -1  # a negative number indicates an unbounded level
        else:
            n_int = n.get_int_value()
            # Here we test for negative since in Mathics Flatten[] as opposed to flatten_with_respect_to_head()
            # negative numbers (and None) are not allowed.
            if n_int is None or n_int < 0:
                return evaluation.message("Flatten", "flpi", n)
            n = n_int

        return expr.flatten_with_respect_to_head(h, level=n)


class Null(Predefined):
    """
    <dl>
      <dt>'Null'
      <dd>is the implicit result of expressions that do not yield a result.
    </dl>

    >> FullForm[a:=b]
     = Null

    It is not displayed in StandardForm,
    >> a:=b
    in contrast to the empty string:
    >> ""
     = #<--#
    """

    summary_text = "implicit result for expressions that does not yield a result"


class Depth(Builtin):
    """
    <dl>
      <dt>'Depth[$expr$]'
      <dd>gives the depth of $expr$.
    </dl>

    The depth of an expression is defined as one plus the maximum
    number of 'Part' indices required to reach any part of $expr$,
    except for heads.

    >> Depth[x]
     = 1
    >> Depth[x + y]
     = 2
    >> Depth[{{{{x}}}}]
     = 5

    Complex numbers are atomic, and hence have depth 1:
    >> Depth[1 + 2 I]
     = 1

    'Depth' ignores heads:
    >> Depth[f[a, b][c]]
     = 2
    """

    summary_text = "the maximum number of indices to specify any part"

    def apply(self, expr, evaluation):
        "Depth[expr_]"
        expr, depth = walk_levels(expr)
        return Integer(depth + 1)


class Operate(Builtin):
    """
    <dl>
      <dt>'Operate[$p$, $expr$]'
      <dd>applies $p$ to the head of $expr$.

      <dt>'Operate[$p$, $expr$, $n$]'
      <dd>applies $p$ to the $n$th head of $expr$.
    </dl>

    >> Operate[p, f[a, b]]
     = p[f][a, b]

    The default value of $n$ is 1:
    >> Operate[p, f[a, b], 1]
     = p[f][a, b]

    With $n$=0, 'Operate' acts like 'Apply':
    >> Operate[p, f[a][b][c], 0]
     = p[f[a][b][c]]

    #> Operate[p, f, -1]
     : Non-negative integer expected at position 3 in Operate[p, f, -1].
     = Operate[p, f, -1]
    """

    summary_text = "apply a function to the head of an expression"
    messages = {
        "intnn": "Non-negative integer expected at position `2` in `1`.",
    }

    def apply(self, p, expr, n, evaluation):
        "Operate[p_, expr_, Optional[n_, 1]]"

        head_depth = n.get_int_value()
        if head_depth is None or head_depth < 0:
            return evaluation.message(
                "Operate", "intnn", Expression(SymbolOperate, p, expr, n), 3
            )

        if head_depth == 0:
            # Act like Apply
            return Expression(p, expr)

        if isinstance(expr, Atom):
            return expr

        expr = expr.copy()
        e = expr

        for i in range(1, head_depth):
            e = e.head
            if isinstance(e, Atom):
                # n is higher than the depth of heads in expr: return
                # expr unmodified.
                return expr

        # Otherwise, if we get here, e.head points to the head we need
        # to apply p to. Python's reference semantics mean that this
        # assignment modifies expr as well.
        e.set_head(Expression(p, e.head))

        return expr


class Through(Builtin):
    """
    <dl>
      <dt>'Through[$p$[$f$][$x$]]'
      <dd>gives $p$[$f$[$x$]].
    </dl>

    >> Through[f[g][x]]
     = f[g[x]]
    >> Through[p[f, g][x]]
     = p[f[x], g[x]]
    """

    summary_text = "distribute operators that appears inside the head of expressions"

    def apply(self, p, args, x, evaluation):
        "Through[p_[args___][x___]]"

        elements = []
        for element in args.get_sequence():
            elements.append(Expression(element, *x.get_sequence()))
        return Expression(p, *elements)


class ByteCount(Builtin):
    """
    <dl>
      <dt>'ByteCount[$expr$]'
      <dd>gives the internal memory space used by $expr$, in bytes.
    </dl>

    The results may heavily depend on the Python implementation in use.
    """

    summary_text = "amount of memory used by expr, in bytes"

    def apply(self, expression, evaluation):
        "ByteCount[expression_]"
        if not bytecount_support:
            return evaluation.message("ByteCount", "pypy")
        else:
            return Integer(count_bytes(expression))
