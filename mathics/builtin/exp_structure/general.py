# -*- coding: utf-8 -*-
"""
General Structural Expression Functions
"""

from mathics.builtin.base import BinaryOperator, Builtin, Predefined
from mathics.core.atoms import Integer, Integer0, Integer1, Rational
from mathics.core.exceptions import InvalidLevelspecError
from mathics.core.expression import Evaluation, Expression
from mathics.core.list import ListExpression
from mathics.core.rules import Pattern
from mathics.core.symbols import Atom, Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolMap
from mathics.eval.parts import python_levelspec, walk_levels

SymbolOperate = Symbol("Operate")
SymbolSortBy = Symbol("SortBy")


class ApplyLevel(BinaryOperator):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ApplyLevel.html</url>

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


class BinarySearch(Builtin):
    """
    <url>
    :Binary search algorithm:
    https://en.wikipedia.org/wiki/Binary_search_algorithm</url> (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/BinarySearch.html</url>)

    <dl>
      <dt>'CombinatoricaOld`BinarySearch[$l$, $k$]'
      <dd>searches the list $l$, which has to be sorted, for key $k$ and \
          returns its index in $l$.

          If $k$ does not exist in $l$, 'BinarySearch' returns ($a$ + $b$) / 2, \
          where $a$ and $b$ are the indices between which $k$ would have  \
          to be inserted in order to maintain the sorting order in $l$.

          Please note that $k$ and the elements in $l$ need to be comparable \
          under a <url>
          :strict total order:
          https://en.wikipedia.org/wiki/Total_order</url>.

      <dt>'CombinatoricaOld`BinarySearch[$l$, $k$, $f$]'
      <dd>gives the index of $k$ in the elements of $l$ if $f$ is applied to the \
          latter prior to comparison. Note that $f$ \
          needs to yield a sorted sequence if applied to the elements of $l$.
    </dl>

    Number 100 is found at exactly in the fourth place of the given list:

    >> CombinatoricaOld`BinarySearch[{3, 4, 10, 100, 123}, 100]
     = 4

     Number 7 is found in between the second and third place (3, and 9)\
     of the given list. The numerical difference between 3 and 9 does \
     not figure into the .5 part of 2.5:

    >> CombinatoricaOld`BinarySearch[{2, 3, 9}, 7] // N
     = 2.5

    0.5 is what you get when the item comes before the given list:

    >> CombinatoricaOld`BinarySearch[{-10, 5, 8, 10}, -100] // N
     = 0.5

    And here is what you see when the item comes at the end of the list:

    >> CombinatoricaOld`BinarySearch[{-10, 5, 8, 10}, 20] // N
     = 4.5

    >> CombinatoricaOld`BinarySearch[{{a, 1}, {b, 7}}, 7, #[[2]]&]
     = 2
    """

    context = "CombinatoricaOld`"

    rules = {
        "CombinatoricaOld`BinarySearch[li_List, k_] /; Length[li] > 0": "CombinatoricaOld`BinarySearch[li, k, Identity]"
    }

    summary_text = "search a sorted list for a key"

    def eval(self, li, k, f, evaluation: Evaluation):
        "CombinatoricaOld`BinarySearch[li_List, k_, f_] /; Length[li] > 0"

        elements = li.elements

        lower_index = 1
        upper_index = len(elements)

        if (
            lower_index > upper_index
        ):  # empty list li? Length[l] > 0 condition should guard us, but check anyway
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

    summary_text = "the maximum number of indices to specify any part"

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

        form = Pattern.create(form)
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
    summary_text = "parts specified by a given number of indices"

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

    summary_text = "implicit result for expressions that does not yield a result"


class Operate(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Operate.html</url>

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

    def eval(self, p, expr, n, evaluation: Evaluation):
        "Operate[p_, expr_, Optional[n_, 1]]"

        head_depth = n.get_int_value()
        if head_depth is None or head_depth < 0:
            evaluation.message(
                "Operate", "intnn", Expression(SymbolOperate, p, expr, n), 3
            )
            return

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


class Order(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Order.html</url>

    <dl>
      <dt>'Order[$x$, $y$]'
      <dd>returns a number indicating the canonical ordering of $x$ and $y$. \
         1 indicates that $x$ is before $y$, \-1 that $y$ is before $x$. \
         0 indicates that there is no specific ordering. Uses the same order \
         as 'Sort'.
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

    def eval(self, x, y, evaluation: Evaluation):
        "Order[x_, y_]"
        if x < y:
            return Integer1
        elif x > y:
            return Integer(-1)
        else:
            return Integer0


class OrderedQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/OrderedQ.html</url>

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

    def eval(self, expr, evaluation: Evaluation):
        "OrderedQ[expr_]"

        for index, value in enumerate(expr.elements[:-1]):
            if expr.elements[index] <= expr.elements[index + 1]:
                continue
            else:
                return SymbolFalse
        return SymbolTrue


class PatternsOrderedQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/PatternsOrderedQ.html</url>

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

    def eval(self, p1, p2, evaluation: Evaluation):
        "PatternsOrderedQ[p1_, p2_]"

        if p1.get_sort_key(True) <= p2.get_sort_key(True):
            return SymbolTrue
        else:
            return SymbolFalse


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
            evaluation.message("Sort", "normal")
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


class Through(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Through.html</url>

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

    def eval(self, p, args, x, evaluation: Evaluation):
        "Through[p_[args___][x___]]"

        elements = []
        for element in args.get_sequence():
            elements.append(Expression(element, *x.get_sequence()))
        return Expression(p, *elements)
