# -*- coding: utf-8 -*-
"""
Structural Expression Functions
"""

from mathics.core.atoms import Integer, Integer1
from mathics.core.builtin import Builtin, InfixOperator, Predefined
from mathics.core.exceptions import InvalidLevelspecError
from mathics.core.expression import Evaluation, Expression
from mathics.core.list import ListExpression
from mathics.core.rules import BasePattern
from mathics.core.symbols import Atom, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolMap, SymbolSortBy
from mathics.eval.parts import python_levelspec, walk_levels


class MapApply(InfixOperator):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MapApply.html</url>

    <dl>
      <dt>'MapApply[$f$, $expr$]'

      <dt>'$f$ @@@ $expr$'
      <dd>is equivalent to 'Apply[$f$, $expr$, {1}]'.
    </dl>

    >> f @@@ {{a, b}, {c, d}}
     = {f[a, b], f[c, d]}
    """

    grouping = "Right"
    operator = "@@@"

    rules = {
        "MapApply[f_, expr_]": "Apply[f, expr, {1}]",
    }

    summary_text = "apply a function to a list, at the top level"


class Depth(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Depth.html</url>

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

    summary_text = "get maximum number of indices to specify any part"

    def eval(self, expr, evaluation: Evaluation):
        "Depth[expr_]"
        expr, depth = walk_levels(expr)
        return Integer(depth + 1)


class FreeQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/FreeQ.html</url>

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

    def eval(self, expr, form, evaluation: Evaluation):
        "FreeQ[expr_, form_]"

        form = BasePattern.create(form, evaluation=evaluation)
        if expr.is_free(form, evaluation):
            return SymbolTrue
        else:
            return SymbolFalse


class Level(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Level.html</url>

    <dl>
      <dt>'Level[$expr$, $levelspec$]'
      <dd>gives a list of all subexpressions of $expr$ at the
        level(s) specified by $levelspec$.
    </dl>

    Level uses standard level specifications:

    <dl>
      <dt>$n$
      <dd>levels 1 through $n$
      <dt>'Infinity'
      <dd>all levels from level 1
      <dt>'{$n$}'
      <dd>level $n$ only
      <dt>'{$m$, $n$}'
      <dd>levels $m$ through $n$
    </dl>

    Level 0 corresponds to the whole expression.

    A negative level '-$n$' consists of parts with depth $n$.

    Level -1 is the set of atoms in an expression:
    >> Level[a + b ^ 3 * f[2 x ^ 2], {-1}]
     = {a, b, 3, 2, x, 2}

    >> Level[{{{{a}}}}, 3]
     = {{a}, {{a}}, {{{a}}}}
    >> Level[{{{{a}}}}, -4]
     = {{{{a}}}}
    >> Level[{{{{a}}}}, -5]
     = {}

    >> Level[h0[h1[h2[h3[a]]]], {0, -1}]
     = {a, h3[a], h2[h3[a]], h1[h2[h3[a]]], h0[h1[h2[h3[a]]]]}

    Use the option 'Heads -> True' to include heads:
    >> Level[{{{{a}}}}, 3, Heads -> True]
     = {List, List, List, {a}, {{a}}, {{{a}}}}
    >> Level[x^2 + y^3, 3, Heads -> True]
     = {Plus, Power, x, 2, x ^ 2, Power, y, 3, y ^ 3}

    >> Level[a ^ 2 + 2 * b, {-1}, Heads -> True]
     = {Plus, Power, a, 2, Times, 2, b}
    >> Level[f[g[h]][x], {-1}, Heads -> True]
     = {f, g, h, x}
    >> Level[f[g[h]][x], {-2, -1}, Heads -> True]
     = {f, g, h, g[h], x, f[g[h]][x]}
    """

    options = {
        "Heads": "False",
    }
    summary_text = "get parts specified by a given number of indices"

    def eval(self, expr, ls, evaluation, options={}):
        "Level[expr_, ls_, OptionsPattern[Level]]"

        try:
            start, stop = python_levelspec(ls)
        except InvalidLevelspecError:
            evaluation.message("Level", "level", ls)
            return
        result = []

        def callback(level):
            result.append(level)
            return level

        heads = self.get_option(options, "Heads", evaluation) is SymbolTrue
        walk_levels(expr, start, stop, heads=heads, callback=callback)
        return ListExpression(*result)


class Null(Predefined):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Null.html</url>

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

    summary_text = "implicit result for expressions that do not yield a result"


class SortBy(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SortBy.html</url>

    <dl>
      <dt>'SortBy[$list$, $f$]'
      <dd>sorts $list$ (or the elements of any other expression) according to \
         canonical ordering of the keys that are extracted from the $list$'s \
         elements using $f. Chunks of elements that appear the same under $f \
         are sorted according to their natural order (without applying $f).

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

    def eval(self, li, f, evaluation: Evaluation):
        "SortBy[li_, f_]"

        if isinstance(li, Atom):
            evaluation.message(
                "Sort", "normal", Integer1, Expression(SymbolSortBy, li, f)
            )
            return
        elif li.get_head_name() != "System`List":
            expr = Expression(SymbolSortBy, li, f)
            evaluation.message(self.get_name(), "list", expr, 1)
            return
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
                evaluation.message("SortBy", "func", expr, 2)
                return

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
