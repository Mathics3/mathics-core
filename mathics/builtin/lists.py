# -*- coding: utf-8 -*-
"""
List Functions - Miscellaneous

Functions here will eventually get moved to more suitable subsections.
"""

from mathics.algorithm.parts import python_levelspec, walk_levels
from mathics.builtin.base import Builtin, Predefined, Test
from mathics.builtin.box.layout import RowBox
from mathics.core.atoms import Integer, Integer1, Integer2, String
from mathics.core.attributes import A_LOCKED, A_PROTECTED
from mathics.core.convert.expression import to_expression
from mathics.core.exceptions import (
    InvalidLevelspecError,
    PartDepthError,
    PartError,
    PartRangeError,
)
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol, SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolKey,
    SymbolMakeBoxes,
    SymbolSequence,
    SymbolSubsetQ,
)


def delete_one(expr, pos):
    if isinstance(expr, Atom):
        raise PartDepthError(pos)
    elements = expr.elements
    if pos == 0:
        return Expression(SymbolSequence, *elements)
    s = len(elements)
    truepos = pos
    if truepos < 0:
        truepos = s + truepos
    else:
        truepos = truepos - 1
    if truepos < 0 or truepos >= s:
        raise PartRangeError
    elements = (
        elements[:truepos]
        + (to_expression("System`Sequence"),)
        + elements[truepos + 1 :]
    )
    return to_expression(expr.get_head(), *elements)


def delete_rec(expr, pos):
    if len(pos) == 1:
        return delete_one(expr, pos[0])
    truepos = pos[0]
    if truepos == 0 or isinstance(expr, Atom):
        raise PartDepthError(pos[0])
    elements = expr.elements
    s = len(elements)
    if truepos < 0:
        truepos = truepos + s
        if truepos < 0:
            raise PartRangeError
        newelement = delete_rec(elements[truepos], pos[1:])
        elements = elements[:truepos] + (newelement,) + elements[truepos + 1 :]
    else:
        if truepos > s:
            raise PartRangeError
        newelement = delete_rec(elements[truepos - 1], pos[1:])
        elements = elements[: truepos - 1] + (newelement,) + elements[truepos:]
    return Expression(expr.get_head(), *elements)


def riffle(items, sep):
    result = items[:1]
    for item in items[1:]:
        result.append(sep)
        result.append(item)
    return result


def list_boxes(items, f, evaluation, open=None, close=None):
    result = [
        Expression(SymbolMakeBoxes, item, f).evaluate(evaluation) for item in items
    ]
    if f.get_name() in ("System`OutputForm", "System`InputForm"):
        sep = ", "
    else:
        sep = ","
    result = riffle(result, String(sep))
    if len(items) > 1:
        result = RowBox(*result)
    elif items:
        result = result[0]
    if result:
        result = [result]
    else:
        result = []
    if open is not None and close is not None:
        return [String(open)] + result + [String(close)]
    else:
        return result


def get_tuples(items):
    if not items:
        yield []
    else:
        for item in items[0]:
            for rest in get_tuples(items[1:]):
                yield [item] + rest


class All(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/All.html</url>

    <dl>
      <dt>'All'
      <dd>is a possible option value for 'Span', 'Quiet', 'Part' and related functions. 'All' specifies all parts at a particular level.
    </dl>
    """

    summary_text = "all the parts in the level"


class Delete(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Delete.html</url>

    <dl>
      <dt>'Delete[$expr$, $i$]'
      <dd>deletes the element at position $i$ in $expr$. The position is counted from the end if $i$ is negative.
      <dt>'Delete[$expr$, {$m$, $n$, ...}]'
      <dd>deletes the element at position {$m$, $n$, ...}.
      <dt>'Delete[$expr$, {{$m1$, $n1$, ...}, {$m2$, $n2$, ...}, ...}]'
      <dd>deletes the elements at several positions.
    </dl>

    Delete the element at position 3:
    >> Delete[{a, b, c, d}, 3]
     = {a, b, d}

    Delete at position 2 from the end:
    >> Delete[{a, b, c, d}, -2]
     = {a, b, d}

    Delete at positions 1 and 3:
    >> Delete[{a, b, c, d}, {{1}, {3}}]
     = {b, d}

    Delete in a 2D array:
    >> Delete[{{a, b}, {c, d}}, {2, 1}]
     = {{a, b}, {d}}

    Deleting the head of a whole expression gives a Sequence object:
    >> Delete[{a, b, c}, 0]
     = Sequence[a, b, c]

    Delete in an expression with any head:
    >> Delete[f[a, b, c, d], 3]
     = f[a, b, d]

    Delete a head to splice in its arguments:
    >> Delete[f[a, b, u + v, c], {3, 0}]
     = f[a, b, u, v, c]

    >> Delete[{a, b, c}, 0]
     = Sequence[a, b, c]

    #> Delete[1 + x ^ (a + b + c), {2, 2, 3}]
     = 1 + x ^ (a + b)

    #> Delete[f[a, g[b, c], d], {{2}, {2, 1}}]
     = f[a, d]

    #> Delete[f[a, g[b, c], d], m + n]
     : The expression m + n cannot be used as a part specification. Use Key[m + n] instead.
     = Delete[f[a, g[b, c], d], m + n]

    Delete without the position:
    >> Delete[{a, b, c, d}]
     : Delete called with 1 argument; 2 arguments are expected.
     = Delete[{a, b, c, d}]

    Delete with many arguments:
    >> Delete[{a, b, c, d}, 1, 2]
     : Delete called with 3 arguments; 2 arguments are expected.
     = Delete[{a, b, c, d}, 1, 2]

    Delete the element out of range:
    >> Delete[{a, b, c, d}, 5]
     : Part {5} of {a, b, c, d} does not exist.
     = Delete[{a, b, c, d}, 5]

    #> Delete[{a, b, c, d}, {1, 2}]
     : Part 2 of {a, b, c, d} does not exist.
     = Delete[{a, b, c, d}, {1, 2}]

    Delete the position not integer:
    >> Delete[{a, b, c, d}, {1, n}]
     : Position specification n in {a, b, c, d} is not a machine-sized integer or a list of machine-sized integers.
     = Delete[{a, b, c, d}, {1, n}]

    #> Delete[{a, b, c, d}, {{1}, n}]
     : Position specification {n, {1}} in {a, b, c, d} is not a machine-sized integer or a list of machine-sized integers.
     = Delete[{a, b, c, d}, {{1}, n}]

    #> Delete[{a, b, c, d}, {{1}, {n}}]
     : Position specification n in {a, b, c, d} is not a machine-sized integer or a list of machine-sized integers.
     = Delete[{a, b, c, d}, {{1}, {n}}]
    """

    messages = {
        # FIXME: This message doesn't exist in more modern WMA, and
        # Delete *can* take more than 2 arguments.
        "argr": "Delete called with 1 argument; 2 arguments are expected.",
        "argt": "Delete called with `1` arguments; 2 arguments are expected.",
        "psl": "Position specification `1` in `2` is not a machine-sized integer or a list of machine-sized integers.",
        "pkspec": "The expression `1` cannot be used as a part specification. Use `2` instead.",
    }
    summary_text = "delete elements from a list at given positions"

    def eval_one(self, expr, position: Integer, evaluation):
        "Delete[expr_, position_Integer]"
        pos = position.value
        try:
            return delete_one(expr, pos)
        except PartRangeError:
            evaluation.message("Part", "partw", ListExpression(position), expr)

    def eval(self, expr, positions, evaluation):
        "Delete[expr_, positions___]"
        positions = positions.get_sequence()
        if len(positions) > 1:
            return evaluation.message("Delete", "argt", Integer(len(positions) + 1))
        elif len(positions) == 0:
            return evaluation.message("Delete", "argr")

        positions = positions[0]
        if not positions.has_form("List", None):
            return evaluation.message(
                "Delete", "pkspec", positions, Expression(SymbolKey, positions)
            )

        # Create new python list of the positions and sort it
        positions = (
            [t for t in positions.elements]
            if positions.elements[0].has_form("List", None)
            else [positions]
        )
        positions.sort(key=lambda e: e.get_sort_key(pattern_sort=True))
        newexpr = expr
        for position in positions:
            pos = [p.get_int_value() for p in position.get_elements()]
            if None in pos:
                return evaluation.message(
                    "Delete", "psl", position.elements[pos.index(None)], expr
                )
            if len(pos) == 0:
                return evaluation.message(
                    "Delete", "psl", ListExpression(*positions), expr
                )
            try:
                newexpr = delete_rec(newexpr, pos)
            except PartDepthError as exc:
                return evaluation.message("Part", "partw", Integer(exc.index), expr)
            except PartError:
                return evaluation.message("Part", "partw", ListExpression(*pos), expr)
        return newexpr


class DisjointQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/DisjointQ.html</url>

    <dl>
      <dt>'DisjointQ[$a$, $b$]'
      <dd>gives True if $a$ and $b$ are disjoint, or False if $a$ and \
      $b$ have any common elements.
    </dl>
    """

    rules = {"DisjointQ[a_List, b_List]": "Not[IntersectingQ[a, b]]"}
    summary_text = "test whether two lists do not have common elements"


class Failure(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Failure.html</url>

    <dl>
      <dt>Failure[$tag$, $assoc$]
      <dd> represents a failure of a type indicated by $tag$, with details \
           given by the association $assoc$.
    </dl>
    """

    summary_text = "a failure at the level of the interpreter"


# From backports in CellsToTeX. This functions provides compatibility to WMA 10.
#  TODO:
#  * Add doctests
#  * Translate to python the more complex rules
#  * Complete the support.


class Insert(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Insert.html</url>

    <dl>
      <dt>'Insert[$list$, $elem$, $n$]'
      <dd>inserts $elem$ at position $n$ in $list$. When $n$ is negative, \
          the position is counted from the end.
    </dl>

    >> Insert[{a,b,c,d,e}, x, 3]
     = {a, b, x, c, d, e}

    >> Insert[{a,b,c,d,e}, x, -2]
     = {a, b, c, d, x, e}
    """

    summary_text = "insert an element at a given position"

    def eval(self, expr, elem, n: Integer, evaluation):
        "Insert[expr_List, elem_, n_Integer]"

        py_n = n.value
        new_list = list(expr.get_elements())

        position = py_n - 1 if py_n > 0 else py_n + 1
        new_list.insert(position, elem)
        return expr.restructure(expr.head, new_list, evaluation, deps=(expr, elem))


class IntersectingQ(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/IntersectingQ.html</url>

    <dl>
      <dt>'IntersectingQ[$a$, $b$]'
      <dd>gives True if there are any common elements in $a and $b, or \
          False if $a and $b are disjoint.
    </dl>
    """

    rules = {"IntersectingQ[a_List, b_List]": "Length[Intersect[a, b]] > 0"}
    summary_text = "test whether two lists have common elements"


class LeafCount(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/LeafCount.html</url>

    <dl>
      <dt>'LeafCount[$expr$]'
      <dd>returns the total number of indivisible subexpressions in $expr$.
    </dl>

    >> LeafCount[1 + x + y^a]
     = 6

    >> LeafCount[f[x, y]]
     = 3

    >> LeafCount[{1 / 3, 1 + I}]
     = 7

    >> LeafCount[Sqrt[2]]
     = 5

    >> LeafCount[100!]
     = 1

    #> LeafCount[f[a, b][x, y]]
     = 5

    #> NestList[# /. s[x_][y_][z_] -> x[z][y[z]] &, s[s][s][s[s]][s][s], 4];
    #> LeafCount /@ %
     = {7, 8, 8, 11, 11}

    #> LeafCount[1 / 3, 1 + I]
     : LeafCount called with 2 arguments; 1 argument is expected.
     = LeafCount[1 / 3, 1 + I]
    """

    messages = {
        "argx": "LeafCount called with `1` arguments; 1 argument is expected.",
    }
    summary_text = "the total number of atomic subexpressions"

    def eval(self, expr, evaluation):
        "LeafCount[expr___]"

        from mathics.core.atoms import Complex, Rational

        elements = []

        def callback(level):
            if isinstance(level, Rational):
                elements.extend(
                    [level.get_head(), level.numerator(), level.denominator()]
                )
            elif isinstance(level, Complex):
                elements.extend([level.get_head(), level.real, level.imag])
            else:
                elements.append(level)
            return level

        expr = expr.get_sequence()
        if len(expr) != 1:
            return evaluation.message("LeafCount", "argx", Integer(len(expr)))

        walk_levels(expr[0], start=-1, stop=-1, heads=True, callback=callback)
        return Integer(len(elements))


class Level(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Level.html</url>

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


class LevelQ(Test):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/LevelQ.html</url>

    <dl>
      <dt>'LevelQ[$expr$]'
      <dd>tests whether $expr$ is a valid level specification.
    </dl>

    >> LevelQ[2]
     = True
    >> LevelQ[{2, 4}]
     = True
    >> LevelQ[Infinity]
     = True
    >> LevelQ[a + b]
     = False
    """

    summary_text = "test whether is a valid level specification"

    def test(self, ls):
        try:
            start, stop = python_levelspec(ls)
            return True
        except InvalidLevelspecError:
            return False


class List(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/List.html</url>

    <dl>
      <dt>'List[$e1$, $e2$, ..., $ei$]'
      <dt>'{$e1$, $e2$, ..., $ei$}'
      <dd>represents a list containing the elements $e1$...$ei$.
    </dl>

    'List' is the head of lists:
    >> Head[{1, 2, 3}]
     = List

    Lists can be nested:
    >> {{a, b, {c, d}}}
     = {{a, b, {c, d}}}
    """

    attributes = A_LOCKED | A_PROTECTED
    summary_text = "specify a list explicitly"

    def eval(self, elements, evaluation):
        """List[elements___]"""
        # Pick out the elements part of the parameter elements;
        # we we will call that `elements_part_of_elements__`.
        # Note that the parameter elements may be wrapped in a Sequence[]
        # so remove that if when it is present.
        elements_part_of_elements__ = elements.get_sequence()
        return ListExpression(*elements_part_of_elements__)

    def eval_makeboxes(self, items, f, evaluation):
        """MakeBoxes[{items___},
        f:StandardForm|TraditionalForm|OutputForm|InputForm|FullForm]"""

        items = items.get_sequence()
        return RowBox(*list_boxes(items, f, evaluation, "{", "}"))


class ListQ(Test):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ListQ.html</url>

    <dl>
      <dt>'ListQ[$expr$]'
      <dd>tests whether $expr$ is a 'List'.
    </dl>

    >> ListQ[{1, 2, 3}]
     = True
    >> ListQ[{{1, 2}, {3, 4}}]
     = True
    >> ListQ[x]
     = False
    """

    summary_text = "test if an expression is a list"

    def test(self, expr):
        return expr.get_head_name() == "System`List"


class None_(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/None.html</url>

    <dl>
      <dt>'None'
      <dd>is a possible value for 'Span' and 'Quiet'.
    </dl>
    """

    name = "None"
    summary_text = "not any part"


class NotListQ(Test):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/NotListQ.html</url>

    <dl>
      <dt>'NotListQ[$expr$]'
      <dd>returns true if $expr$ is not a list.
    </dl>
    """

    summary_text = "test if an expression is not a list"

    def test(self, expr):
        return expr.get_head_name() != "System`List"


class _NotRectangularException(Exception):
    pass


class _Rectangular(Builtin):
    # A helper for Builtins X that allow X[{a1, a2, ...}, {b1, b2, ...}, ...] to be evaluated
    # as {X[{a1, b1, ...}, {a1, b2, ...}, ...]}.

    def rect(self, element):
        lengths = [len(element.elements) for element in element.elements]
        if all(length == 0 for length in lengths):
            return  # leave as is, without error

        n_columns = lengths[0]
        if any(length != n_columns for length in lengths[1:]):
            raise _NotRectangularException()

        transposed = [
            [element.elements[i] for element in element.elements]
            for i in range(n_columns)
        ]

        return ListExpression(
            *[
                Expression(Symbol(self.get_name()), ListExpression(*items))
                for items in transposed
            ],
        )


class SubsetQ(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/SubsetQ.html</url>

    <dl>
      <dt>'SubsetQ[$list1$, $list2$]'
      <dd>returns True if $list2$ is a subset of $list1$, and False otherwise.
    </dl>

    >> SubsetQ[{1, 2, 3}, {3, 1}]
     = True

    The empty list is a subset of every list:
    >> SubsetQ[{}, {}]
     = True

    >> SubsetQ[{1, 2, 3}, {}]
     = True

    Every list is a subset of itself:
    >> SubsetQ[{1, 2, 3}, {1, 2, 3}]
     = True

    #> SubsetQ[{1, 2, 3}, {0, 1}]
     = False

    #> SubsetQ[{1, 2, 3}, {1, 2, 3, 4}]
     = False

    #> SubsetQ[{1, 2, 3}]
     : SubsetQ called with 1 argument; 2 arguments are expected.
     = SubsetQ[{1, 2, 3}]

    #> SubsetQ[{1, 2, 3}, {1, 2}, {3}]
     : SubsetQ called with 3 arguments; 2 arguments are expected.
     = SubsetQ[{1, 2, 3}, {1, 2}, {3}]

    #> SubsetQ[a + b + c, {1}]
     : Heads Plus and List at positions 1 and 2 are expected to be the same.
     = SubsetQ[a + b + c, {1}]

    #> SubsetQ[{1, 2, 3}, n]
     : Nonatomic expression expected at position 2 in SubsetQ[{1, 2, 3}, n].
     = SubsetQ[{1, 2, 3}, n]

    #> SubsetQ[f[a, b, c], f[a]]
     = True
    """

    messages = {
        # FIXME: This message doesn't exist in more modern WMA, and
        # Subset *can* take more than 2 arguments.
        "argr": "SubsetQ called with 1 argument; 2 arguments are expected.",
        "argrx": "SubsetQ called with `1` arguments; 2 arguments are expected.",
        "heads": "Heads `1` and `2` at positions 1 and 2 are expected to be the same.",
        "normal": "Nonatomic expression expected at position `1` in `2`.",
    }
    summary_text = "test if a list is a subset of another list"

    def eval(self, expr, subset, evaluation):
        "SubsetQ[expr_, subset___]"

        if isinstance(expr, Atom):
            return evaluation.message(
                "SubsetQ", "normal", Integer1, Expression(SymbolSubsetQ, expr, subset)
            )

        subset = subset.get_sequence()
        if len(subset) > 1:
            return evaluation.message("SubsetQ", "argrx", Integer(len(subset) + 1))
        elif len(subset) == 0:
            return evaluation.message("SubsetQ", "argr")

        subset = subset[0]
        if isinstance(subset, Atom):
            return evaluation.message(
                "SubsetQ", "normal", Integer2, Expression(SymbolSubsetQ, expr, subset)
            )
        if expr.get_head_name() != subset.get_head_name():
            return evaluation.message(
                "SubsetQ", "heads", expr.get_head(), subset.get_head()
            )

        if set(subset.elements).issubset(set(expr.elements)):
            return SymbolTrue
        else:
            return SymbolFalse
