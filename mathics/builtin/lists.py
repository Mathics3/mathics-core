# -*- coding: utf-8 -*-
"""
List Functions - Miscellaneous
"""

import heapq
import sympy

from itertools import chain


from mathics.algorithm.clusters import (
    AutomaticMergeCriterion,
    AutomaticSplitCriterion,
    LazyDistances,
    PrecomputedDistances,
    agglomerate,
    kmeans,
    optimize,
)
from mathics.algorithm.parts import (
    python_levelspec,
    walk_levels,
)

from mathics.builtin.base import (
    Builtin,
    CountableInteger,
    MessageException,
    NegativeIntegerException,
    Predefined,
    SympyFunction,
    Test,
)

from mathics.builtin.box.inout import RowBox

from mathics.builtin.exceptions import (
    InvalidLevelspecError,
    PartDepthError,
    PartError,
    PartRangeError,
)

from mathics.builtin.numbers.algebra import cancel
from mathics.builtin.options import options_to_rules
from mathics.builtin.scoping import dynamic_scoping

from mathics.core.atoms import (
    Integer,
    Integer0,
    Integer1,
    Integer2,
    Number,
    Real,
    String,
    machine_precision,
    min_prec,
)
from mathics.core.attributes import (
    flat,
    hold_all,
    locked,
    one_identity,
    protected,
    read_protected,
)
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.convert.sympy import from_sympy
from mathics.core.evaluators import eval_N
from mathics.core.expression import Expression, structure

from mathics.core.interrupt import BreakInterrupt, ContinueInterrupt, ReturnInterrupt
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolFalse,
    SymbolPlus,
    SymbolTrue,
    strip_context,
)

from mathics.core.systemsymbols import (
    SymbolAlternatives,
    SymbolFailed,
    SymbolGreaterEqual,
    SymbolLess,
    SymbolLessEqual,
    SymbolMakeBoxes,
    SymbolMatchQ,
    SymbolRule,
    SymbolSequence,
    SymbolSubsetQ,
)


SymbolClusteringComponents = Symbol("ClusteringComponents")
SymbolContainsOnly = Symbol("ContainsOnly")
SymbolFindClusters = Symbol("FindClusters")
SymbolKey = Symbol("Key")
SymbolSplit = Symbol("Split")


class All(Predefined):
    """
    <dl>
      <dt>'All'
      <dd>is a possible option value for 'Span', 'Quiet', 'Part' and related functions. 'All' specifies all parts at a particular level.
    </dl>
    """

    summary_text = "all the parts in the level"


class ContainsOnly(Builtin):
    """
    <dl>
    <dt>'ContainsOnly[$list1$, $list2$]'
        <dd>yields True if $list1$ contains only elements that appear in $list2$.
    </dl>

    >> ContainsOnly[{b, a, a}, {a, b, c}]
     = True

    The first list contains elements not present in the second list:
    >> ContainsOnly[{b, a, d}, {a, b, c}]
     = False

    >> ContainsOnly[{}, {a, b, c}]
     = True

    #> ContainsOnly[1, {1, 2, 3}]
     : List or association expected instead of 1.
     = ContainsOnly[1, {1, 2, 3}]

    #> ContainsOnly[{1, 2, 3}, 4]
     : List or association expected instead of 4.
     = ContainsOnly[{1, 2, 3}, 4]

    Use Equal as the comparison function to have numerical tolerance:
    >> ContainsOnly[{a, 1.0}, {1, a, b}, {SameTest -> Equal}]
     = True

    #> ContainsOnly[{c, a}, {a, b, c}, IgnoreCase -> True]
     : Unknown option IgnoreCase -> True in ContainsOnly.
     : Unknown option IgnoreCase in .
     = True
    """

    attributes = protected | read_protected

    messages = {
        "lsa": "List or association expected instead of `1`.",
        "nodef": "Unknown option `1` for ContainsOnly.",
        "optx": "Unknown option `1` in `2`.",
    }

    options = {
        "SameTest": "SameQ",
    }

    summary_text = "test if all the elements of a list appears into another list"

    def check_options(self, expr, evaluation, options):
        for key in options:
            if key != "System`SameTest":
                if expr is None:
                    evaluation.message("ContainsOnly", "optx", Symbol(key))
                else:
                    return evaluation.message("ContainsOnly", "optx", Symbol(key), expr)
        return None

    def apply(self, list1, list2, evaluation, options={}):
        "ContainsOnly[list1_List, list2_List, OptionsPattern[ContainsOnly]]"

        same_test = self.get_option(options, "SameTest", evaluation)

        def sameQ(a, b) -> bool:
            """Mathics SameQ"""
            result = Expression(same_test, a, b).evaluate(evaluation)
            return result is SymbolTrue

        self.check_options(None, evaluation, options)
        for a in list1.elements:
            if not any(sameQ(a, b) for b in list2.elements):
                return SymbolFalse
        return SymbolTrue

    def apply_msg(self, e1, e2, evaluation, options={}):
        "ContainsOnly[e1_, e2_, OptionsPattern[ContainsOnly]]"

        opts = (
            options_to_rules(options)
            if len(options) <= 1
            else [ListExpression(*options_to_rules(options))]
        )
        expr = Expression(SymbolContainsOnly, e1, e2, *opts)

        if not isinstance(e1, Symbol) and not e1.has_form("List", None):
            evaluation.message("ContainsOnly", "lsa", e1)
            return self.check_options(expr, evaluation, options)

        if not isinstance(e2, Symbol) and not e2.has_form("List", None):
            evaluation.message("ContainsOnly", "lsa", e2)
            return self.check_options(expr, evaluation, options)

        return self.check_options(expr, evaluation, options)


class Delete(Builtin):
    """
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
        "argr": "Delete called with 1 argument; 2 arguments are expected.",
        "argt": "Delete called with `1` arguments; 2 arguments are expected.",
        "psl": "Position specification `1` in `2` is not a machine-sized integer or a list of machine-sized integers.",
        "pkspec": "The expression `1` cannot be used as a part specification. Use `2` instead.",
    }
    summary_text = "delete elements from a list at given positions"

    def apply_one(self, expr, position: Integer, evaluation):
        "Delete[expr_, position_Integer]"
        pos = position.value
        try:
            return delete_one(expr, pos)
        except PartRangeError:
            evaluation.message("Part", "partw", ListExpression(position), expr)

    def apply(self, expr, positions, evaluation):
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


class Failure(Builtin):
    """
    <dl>
    <dt>Failure[$tag$, $assoc$]
        <dd> represents a failure of a type indicated by $tag$, with details given by the association $assoc$.
    </dl>
    """

    summary_text = "a failure at the level of the interpreter"


# From backports in CellsToTeX. This functions provides compatibility to WMA 10.
#  TODO:
#  * Add doctests
#  * Translate to python the more complex rules
#  * Complete the support.


class Key(Builtin):
    """
    <dl>
    <dt>Key[$key$]
        <dd> represents a key used to access a value in an association.
    <dt>Key[$key$][$assoc$]
        <dd>
    </dl>
    """

    rules = {
        "Key[key_][assoc_Association]": "assoc[key]",
    }
    summary_text = "indicate a key within a part specification"


class Level(Builtin):
    """
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

    def apply(self, expr, ls, evaluation, options={}):
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

    attributes = locked | protected
    summary_text = "specify a list explicitly"

    def apply(self, elements, evaluation):
        """List[elements___]"""
        # Pick out the elements part of the parameter elements;
        # we we will call that `elements_part_of_elements__`.
        # Note that the parameter elements may be wrapped in a Sequence[]
        # so remove that if when it is present.
        elements_part_of_elements__ = elements.get_sequence()
        return ListExpression(*elements_part_of_elements__)

    def apply_makeboxes(self, items, f, evaluation):
        """MakeBoxes[{items___},
        f:StandardForm|TraditionalForm|OutputForm|InputForm|FullForm]"""

        items = items.get_sequence()
        return RowBox(*list_boxes(items, f, evaluation, "{", "}"))


class ListQ(Test):
    """
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


class NotListQ(Test):
    """
    <dl>
    <dt>'NotListQ[$expr$]'
        <dd>returns true if $expr$ is not a list.
    </dl>
    """

    summary_text = "test if an expression is not a list"

    def test(self, expr):
        return expr.get_head_name() != "System`List"


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


class None_(Predefined):
    """
    <dl>
    <dt>'None'
        <dd>is a possible value for 'Span' and 'Quiet'.
    </dl>
    """

    name = "None"
    summary_text = "not any part"


class Split(Builtin):
    """
    <dl>
    <dt>'Split[$list$]'
        <dd>splits $list$ into collections of consecutive identical elements.
    <dt>'Split[$list$, $test$]'
        <dd>splits $list$ based on whether the function $test$ yields
        'True' on consecutive elements.
    </dl>

    >> Split[{x, x, x, y, x, y, y, z}]
     = {{x, x, x}, {y}, {x}, {y, y}, {z}}

    #> Split[{x, x, x, y, x, y, y, z}, x]
     = {{x}, {x}, {x}, {y}, {x}, {y}, {y}, {z}}

    Split into increasing or decreasing runs of elements
    >> Split[{1, 5, 6, 3, 6, 1, 6, 3, 4, 5, 4}, Less]
     = {{1, 5, 6}, {3, 6}, {1, 6}, {3, 4, 5}, {4}}

    >> Split[{1, 5, 6, 3, 6, 1, 6, 3, 4, 5, 4}, Greater]
     = {{1}, {5}, {6, 3}, {6, 1}, {6, 3}, {4}, {5, 4}}

    Split based on first element
    >> Split[{x -> a, x -> y, 2 -> a, z -> c, z -> a}, First[#1] === First[#2] &]
     = {{x -> a, x -> y}, {2 -> a}, {z -> c, z -> a}}

    #> Split[{}]
     = {}

    #> A[x__] := 321 /; Length[{x}] == 5;
    #> Split[A[x, x, x, y, x, y, y, z]]
     = 321
    #> ClearAll[A];
    """

    rules = {
        "Split[list_]": "Split[list, SameQ]",
    }

    messages = {
        "normal": "Nonatomic expression expected at position `1` in `2`.",
    }
    summary_text = "split into runs of identical elements"

    def apply(self, mlist, test, evaluation):
        "Split[mlist_, test_]"

        expr = Expression(SymbolSplit, mlist, test)

        if isinstance(mlist, Atom):
            evaluation.message("Select", "normal", 1, expr)
            return

        if not mlist.elements:
            return Expression(mlist.head)

        result = [[mlist.elements[0]]]
        for element in mlist.elements[1:]:
            applytest = Expression(test, result[-1][-1], element)
            if applytest.evaluate(evaluation) is SymbolTrue:
                result[-1].append(element)
            else:
                result.append([element])

        inner = structure("List", mlist, evaluation)
        outer = structure(mlist.head, inner, evaluation)
        return outer([inner(t) for t in result])


class SplitBy(Builtin):
    """
    <dl>
    <dt>'SplitBy[$list$, $f$]'
        <dd>splits $list$ into collections of consecutive elements
        that give the same result when $f$ is applied.
    </dl>

    >> SplitBy[Range[1, 3, 1/3], Round]
     = {{1, 4 / 3}, {5 / 3, 2, 7 / 3}, {8 / 3, 3}}

    >> SplitBy[{1, 2, 1, 1.2}, {Round, Identity}]
     = {{{1}}, {{2}}, {{1}, {1.2}}}

    #> SplitBy[Tuples[{1, 2}, 3], First]
     = {{{1, 1, 1}, {1, 1, 2}, {1, 2, 1}, {1, 2, 2}}, {{2, 1, 1}, {2, 1, 2}, {2, 2, 1}, {2, 2, 2}}}
    """

    messages = {
        "normal": "Nonatomic expression expected at position `1` in `2`.",
    }

    rules = {
        "SplitBy[list_]": "SplitBy[list, Identity]",
    }

    summary_text = "split based on values of a function applied to elements"

    def apply(self, mlist, func, evaluation):
        "SplitBy[mlist_, func_?NotListQ]"

        expr = Expression(SymbolSplit, mlist, func)

        if isinstance(mlist, Atom):
            evaluation.message("Select", "normal", 1, expr)
            return

        plist = [t for t in mlist.elements]

        result = [[plist[0]]]
        prev = Expression(func, plist[0]).evaluate(evaluation)
        for element in plist[1:]:
            curr = Expression(func, element).evaluate(evaluation)
            if curr == prev:
                result[-1].append(element)
            else:
                result.append([element])
            prev = curr

        inner = structure("List", mlist, evaluation)
        outer = structure(mlist.head, inner, evaluation)
        return outer([inner(t) for t in result])

    def apply_multiple(self, mlist, funcs, evaluation):
        "SplitBy[mlist_, funcs_List]"
        expr = Expression(SymbolSplit, mlist, funcs)

        if isinstance(mlist, Atom):
            evaluation.message("Select", "normal", 1, expr)
            return

        result = mlist
        for f in funcs.elements[::-1]:
            result = self.apply(result, f, evaluation)

        return result


class LeafCount(Builtin):
    """
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

    def apply(self, expr, evaluation):
        "LeafCount[expr___]"

        from mathics.core.atoms import Rational, Complex

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


class Position(Builtin):
    """
    <dl>
    <dt>'Position[$expr$, $patt$]'
        <dd>returns the list of positions for which $expr$ matches $patt$.
    <dt>'Position[$expr$, $patt$, $ls$]'
        <dd>returns the positions on levels specified by levelspec $ls$.
    </dl>

    >> Position[{1, 2, 2, 1, 2, 3, 2}, 2]
     = {{2}, {3}, {5}, {7}}

    Find positions upto 3 levels deep
    >> Position[{1 + Sin[x], x, (Tan[x] - y)^2}, x, 3]
     = {{1, 2, 1}, {2}}

    Find all powers of x
    >> Position[{1 + x^2, x y ^ 2,  4 y,  x ^ z}, x^_]
     = {{1, 2}, {4}}

    Use Position as an operator
    >> Position[_Integer][{1.5, 2, 2.5}]
     = {{2}}
    """

    options = {"Heads": "True"}

    rules = {
        "Position[pattern_][expr_]": "Position[expr, pattern]",
    }
    summary_text = "positions of matching elements"

    def apply_invalidlevel(self, patt, expr, ls, evaluation, options={}):
        "Position[expr_, patt_, ls_, OptionsPattern[Position]]"

        return evaluation.message("Position", "level", ls)

    def apply_level(self, expr, patt, ls, evaluation, options={}):
        """Position[expr_, patt_, Optional[Pattern[ls, _?LevelQ], {0, DirectedInfinity[1]}],
        OptionsPattern[Position]]"""

        try:
            start, stop = python_levelspec(ls)
        except InvalidLevelspecError:
            return evaluation.message("Position", "level", ls)

        from mathics.builtin.patterns import Matcher

        match = Matcher(patt).match
        result = []

        def callback(level, pos):
            if match(level, evaluation):
                result.append(pos)
            return level

        heads = self.get_option(options, "Heads", evaluation) is SymbolTrue
        walk_levels(expr, start, stop, heads=heads, callback=callback, include_pos=True)
        return from_python(result)


class _IterationFunction(Builtin):
    """
    >> Sum[k, {k, Range[5]}]
     = 15
    """

    attributes = hold_all | protected
    allow_loopcontrol = False
    throw_iterb = True

    def get_result(self, items):
        pass

    def apply_symbol(self, expr, iterator, evaluation):
        "%(name)s[expr_, iterator_Symbol]"
        iterator = iterator.evaluate(evaluation)
        if iterator.has_form(["List", "Range", "Sequence"], None):
            elements = iterator.elements
            if len(elements) == 1:
                return self.apply_max(expr, *elements, evaluation)
            elif len(elements) == 2:
                if elements[1].has_form(["List", "Sequence"], None):
                    seq = Expression(SymbolSequence, *(elements[1].elements))
                    return self.apply_list(expr, elements[0], seq, evaluation)
                else:
                    return self.apply_range(expr, *elements, evaluation)
            elif len(elements) == 3:
                return self.apply_iter_nostep(expr, *elements, evaluation)
            elif len(elements) == 4:
                return self.apply_iter(expr, *elements, evaluation)

        if self.throw_iterb:
            evaluation.message(self.get_name(), "iterb")
        return

    def apply_range(self, expr, i, imax, evaluation):
        "%(name)s[expr_, {i_Symbol, imax_}]"
        imax = imax.evaluate(evaluation)
        if imax.has_form("Range", None):
            # FIXME: this should work as an iterator in Python3, not
            # building the sequence explicitly...
            seq = Expression(SymbolSequence, *(imax.evaluate(evaluation).elements))
            return self.apply_list(expr, i, seq, evaluation)
        elif imax.has_form("List", None):
            seq = Expression(SymbolSequence, *(imax.elements))
            return self.apply_list(expr, i, seq, evaluation)
        else:
            return self.apply_iter(expr, i, Integer1, imax, Integer1, evaluation)

    def apply_max(self, expr, imax, evaluation):
        "%(name)s[expr_, {imax_}]"

        # Even though `imax` should be an integeral value, its type does not
        # have to be an Integer.

        result = []

        def do_iteration():
            evaluation.check_stopped()
            try:
                result.append(expr.evaluate(evaluation))
            except ContinueInterrupt:
                if self.allow_loopcontrol:
                    pass
                else:
                    raise
            except BreakInterrupt:
                if self.allow_loopcontrol:
                    raise StopIteration
                else:
                    raise
            except ReturnInterrupt as e:
                if self.allow_loopcontrol:
                    return e.expr
                else:
                    raise

        if isinstance(imax, Integer):
            try:
                for _ in range(imax.value):
                    do_iteration()
            except StopIteration:
                pass

        else:
            imax = imax.evaluate(evaluation)
            imax = imax.numerify(evaluation)
            if isinstance(imax, Number):
                imax = imax.round()
            py_max = imax.get_float_value()
            if py_max is None:
                if self.throw_iterb:
                    evaluation.message(self.get_name(), "iterb")
                return

            index = 0
            try:
                while index < py_max:
                    do_iteration()
                    index += 1
            except StopIteration:
                pass

        return self.get_result(result)

    def apply_iter_nostep(self, expr, i, imin, imax, evaluation):
        "%(name)s[expr_, {i_Symbol, imin_, imax_}]"
        return self.apply_iter(expr, i, imin, imax, Integer1, evaluation)

    def apply_iter(self, expr, i, imin, imax, di, evaluation):
        "%(name)s[expr_, {i_Symbol, imin_, imax_, di_}]"

        if isinstance(self, SympyFunction) and di.get_int_value() == 1:
            whole_expr = to_expression(
                self.get_name(), expr, ListExpression(i, imin, imax)
            )
            sympy_expr = whole_expr.to_sympy(evaluation=evaluation)
            if sympy_expr is None:
                return None

            # apply Together to produce results similar to Mathematica
            result = sympy.together(sympy_expr)
            result = from_sympy(result)
            result = cancel(result)

            if not result.sameQ(whole_expr):
                return result
            return

        index = imin.evaluate(evaluation)
        imax = imax.evaluate(evaluation)
        di = di.evaluate(evaluation)

        result = []
        compare_type = (
            SymbolGreaterEqual
            if Expression(SymbolLess, di, Integer0).evaluate(evaluation).to_python()
            else SymbolLessEqual
        )
        while True:
            cont = Expression(compare_type, index, imax).evaluate(evaluation)
            if cont is SymbolFalse:
                break
            if not cont is SymbolTrue:
                if self.throw_iterb:
                    evaluation.message(self.get_name(), "iterb")
                return

            evaluation.check_stopped()
            try:
                item = dynamic_scoping(expr.evaluate, {i.name: index}, evaluation)
                result.append(item)
            except ContinueInterrupt:
                if self.allow_loopcontrol:
                    pass
                else:
                    raise
            except BreakInterrupt:
                if self.allow_loopcontrol:
                    break
                else:
                    raise
            except ReturnInterrupt as e:
                if self.allow_loopcontrol:
                    return e.expr
                else:
                    raise
            index = Expression(SymbolPlus, index, di).evaluate(evaluation)
        return self.get_result(result)

    def apply_list(self, expr, i, items, evaluation):
        "%(name)s[expr_, {i_Symbol, {items___}}]"
        items = items.evaluate(evaluation).get_sequence()
        result = []
        for item in items:
            evaluation.check_stopped()
            try:
                item = dynamic_scoping(expr.evaluate, {i.name: item}, evaluation)
                result.append(item)
            except ContinueInterrupt:
                if self.allow_loopcontrol:
                    pass
                else:
                    raise
            except BreakInterrupt:
                if self.allow_loopcontrol:
                    break
                else:
                    raise
            except ReturnInterrupt as e:
                if self.allow_loopcontrol:
                    return e.expr
                else:
                    raise
        return self.get_result(result)

    def apply_multi(self, expr, first, sequ, evaluation):
        "%(name)s[expr_, first_, sequ__]"

        sequ = sequ.get_sequence()
        name = self.get_name()
        return to_expression(name, to_expression(name, expr, *sequ), first)


class Join(Builtin):
    """
    <dl>
    <dt>'Join[$l1$, $l2$]'
        <dd>concatenates the lists $l1$ and $l2$.
    </dl>

    'Join' concatenates lists:
    >> Join[{a, b}, {c, d, e}]
     = {a, b, c, d, e}
    >> Join[{{a, b}, {c, d}}, {{1, 2}, {3, 4}}]
     = {{a, b}, {c, d}, {1, 2}, {3, 4}}

    The concatenated expressions may have any head:
    >> Join[a + b, c + d, e + f]
     = a + b + c + d + e + f

    However, it must be the same for all expressions:
    >> Join[a + b, c * d]
     : Heads Plus and Times are expected to be the same.
     = Join[a + b, c d]

    #> Join[x, y]
     = Join[x, y]
    #> Join[x + y, z]
     = Join[x + y, z]
    #> Join[x + y, y z, a]
     : Heads Plus and Times are expected to be the same.
     = Join[x + y, y z, a]
    #> Join[x, y + z, y z]
     = Join[x, y + z, y z]
    """

    attributes = flat | one_identity | protected
    summary_text = "join lists together at any level"

    def apply(self, lists, evaluation):
        "Join[lists___]"

        result = []
        head = None
        sequence = lists.get_sequence()

        for list in sequence:
            if isinstance(list, Atom):
                return
            if head is not None and list.get_head() != head:
                evaluation.message("Join", "heads", head, list.get_head())
                return
            head = list.get_head()
            result.extend(list.elements)

        if result:
            return sequence[0].restructure(head, result, evaluation, deps=sequence)
        else:
            return ListExpression()


class Insert(Builtin):
    """
    <dl>
      <dt>'Insert[$list$, $elem$, $n$]'
      <dd>inserts $elem$ at position $n$ in $list$. When $n$ is negative, the position is counted from the end.
    </dl>

    >> Insert[{a,b,c,d,e}, x, 3]
     = {a, b, x, c, d, e}

    >> Insert[{a,b,c,d,e}, x, -2]
     = {a, b, c, d, x, e}
    """

    summary_text = "insert an element at a given position"

    def apply(self, expr, elem, n: Integer, evaluation):
        "Insert[expr_List, elem_, n_Integer]"

        py_n = n.value
        new_list = list(expr.get_elements())

        position = py_n - 1 if py_n > 0 else py_n + 1
        new_list.insert(position, elem)
        return expr.restructure(expr.head, new_list, evaluation, deps=(expr, elem))


def get_tuples(items):
    if not items:
        yield []
    else:
        for item in items[0]:
            for rest in get_tuples(items[1:]):
                yield [item] + rest


class IntersectingQ(Builtin):
    """
    <dl>
    <dt>'IntersectingQ[$a$, $b$]'
    <dd>gives True if there are any common elements in $a and $b, or False if $a and $b are disjoint.
    </dl>
    """

    rules = {"IntersectingQ[a_List, b_List]": "Length[Intersect[a, b]] > 0"}
    summary_text = "test whether two lists have common elements"


class DisjointQ(Test):
    """
    <dl>
    <dt>'DisjointQ[$a$, $b$]'
    <dd>gives True if $a and $b are disjoint, or False if $a and $b have any common elements.
    </dl>
    """

    rules = {"DisjointQ[a_List, b_List]": "Not[IntersectingQ[a, b]]"}
    summary_text = "test whether two lists do not have common elements"


class Fold(Builtin):
    """
    <dl>
    <dt>'Fold[$f$, $x$, $list$]'
        <dd>returns the result of iteratively applying the binary
        operator $f$ to each element of $list$, starting with $x$.
    <dt>'Fold[$f$, $list$]'
        <dd>is equivalent to 'Fold[$f$, First[$list$], Rest[$list$]]'.
    </dl>

    >> Fold[Plus, 5, {1, 1, 1}]
     = 8
    >> Fold[f, 5, {1, 2, 3}]
     = f[f[f[5, 1], 2], 3]
    """

    rules = {
        "Fold[exp_, x_, head_]": "Module[{list = Level[head, 1], res = x, i = 1}, Do[res = exp[res, list[[i]]], {i, 1, Length[list]}]; res]",
        "Fold[exp_, head_] /; Length[head] > 0": "Fold[exp, First[head], Rest[head]]",
    }
    summary_text = "iterative application of a binary operation over elements of a list"


class FoldList(Builtin):
    """
    <dl>
    <dt>'FoldList[$f$, $x$, $list$]'
        <dd>returns a list starting with $x$, where each element is
        the result of applying the binary operator $f$ to the previous
        result and the next element of $list$.
    <dt>'FoldList[$f$, $list$]'
        <dd>is equivalent to 'FoldList[$f$, First[$list$], Rest[$list$]]'.
    </dl>

    >> FoldList[f, x, {1, 2, 3}]
     = {x, f[x, 1], f[f[x, 1], 2], f[f[f[x, 1], 2], 3]}
    >> FoldList[Times, {1, 2, 3}]
     = {1, 2, 6}
    """

    rules = {
        "FoldList[exp_, x_, head_]": "Module[{i = 1}, Head[head] @@ Prepend[Table[Fold[exp, x, Take[head, i]], {i, 1, Length[head]}], x]]",
        "FoldList[exp_, head_]": "If[Length[head] == 0, head, FoldList[exp, First[head], Rest[head]]]",
    }
    summary_text = "list of the results of applying a binary operation interatively over elements of a list"


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


class _RankedTake(Builtin):
    messages = {
        "intpm": "Expected non-negative integer at position `1` in `2`.",
        "rank": "The specified rank `1` is not between 1 and `2`.",
    }

    options = {
        "ExcludedForms": "Automatic",
    }

    def _compute(self, t, n, evaluation, options, f=None):
        try:
            limit = CountableInteger.from_expression(n)
        except MessageException as e:
            e.message(evaluation)
            return
        except NegativeIntegerException:
            if f:
                args = (3, Expression(self.get_name(), t, f, n))
            else:
                args = (2, Expression(self.get_name(), t, n))
            evaluation.message(self.get_name(), "intpm", *args)
            return

        if limit is None:
            return

        if limit == 0:
            return ListExpression()
        else:
            excluded = self.get_option(options, "ExcludedForms", evaluation)
            if excluded:
                if (
                    isinstance(excluded, Symbol)
                    and excluded.get_name() == "System`Automatic"
                ):

                    def exclude(item):
                        if isinstance(item, Symbol) and item.get_name() in (
                            "System`None",
                            "System`Null",
                            "System`Indeterminate",
                        ):
                            return True
                        elif item.get_head_name() == "System`Missing":
                            return True
                        else:
                            return False

                else:
                    excluded = Expression(SymbolAlternatives, *excluded.elements)

                    def exclude(item):
                        return (
                            Expression(SymbolMatchQ, item, excluded).evaluate(
                                evaluation
                            )
                            is SymbolTrue
                        )

                filtered = [element for element in t.elements if not exclude(element)]
            else:
                filtered = t.elements

            if limit > len(filtered):
                if not limit.is_upper_limit():
                    evaluation.message(
                        self.get_name(), "rank", limit.get_int_value(), len(filtered)
                    )
                    return
                else:
                    py_n = len(filtered)
            else:
                py_n = limit.get_int_value()

            if py_n < 1:
                return ListExpression()

            if f:
                heap = [
                    (Expression(f, element).evaluate(evaluation), element, i)
                    for i, element in enumerate(filtered)
                ]
                element_pos = 1  # in tuple above
            else:
                heap = [(element, i) for i, element in enumerate(filtered)]
                element_pos = 0  # in tuple above

            if py_n == 1:
                result = [self._get_1(heap)]
            else:
                result = self._get_n(py_n, heap)

            return t.restructure("List", [x[element_pos] for x in result], evaluation)


class _RankedTakeSmallest(_RankedTake):
    def _get_1(self, a):
        return min(a)

    def _get_n(self, n, heap):
        return heapq.nsmallest(n, heap)


class _RankedTakeLargest(_RankedTake):
    def _get_1(self, a):
        return max(a)

    def _get_n(self, n, heap):
        return heapq.nlargest(n, heap)


class TakeLargestBy(_RankedTakeLargest):
    """
    <dl>
    <dt>'TakeLargestBy[$list$, $f$, $n$]'
        <dd>returns the a sorted list of the $n$ largest items in $list$
        using $f$ to retrieve the items' keys to compare them.
    </dl>

    For details on how to use the ExcludedForms option, see TakeLargest[].

    >> TakeLargestBy[{{1, -1}, {10, 100}, {23, 7, 8}, {5, 1}}, Total, 2]
     = {{10, 100}, {23, 7, 8}}

    >> TakeLargestBy[{"abc", "ab", "x"}, StringLength, 1]
     = {abc}
    """

    summary_text = "sublist of n largest elements according to a given criteria"

    def apply(self, element, f, n, evaluation, options):
        "TakeLargestBy[element_List, f_, n_, OptionsPattern[TakeLargestBy]]"
        return self._compute(element, n, evaluation, options, f=f)


class TakeSmallestBy(_RankedTakeSmallest):
    """
    <dl>
    <dt>'TakeSmallestBy[$list$, $f$, $n$]'
        <dd>returns the a sorted list of the $n$ smallest items in $list$
        using $f$ to retrieve the items' keys to compare them.
    </dl>

    For details on how to use the ExcludedForms option, see TakeLargest[].

    >> TakeSmallestBy[{{1, -1}, {10, 100}, {23, 7, 8}, {5, 1}}, Total, 2]
     = {{1, -1}, {5, 1}}

    >> TakeSmallestBy[{"abc", "ab", "x"}, StringLength, 1]
     = {x}
    """

    summary_text = "sublist of n largest elements according to a criteria"

    def apply(self, element, f, n, evaluation, options):
        "TakeSmallestBy[element_List, f_, n_, OptionsPattern[TakeSmallestBy]]"
        return self._compute(element, n, evaluation, options, f=f)


class _IllegalPaddingDepth(Exception):
    def __init__(self, level):
        self.level = level


class _Pad(Builtin):
    messages = {
        "normal": "Expression at position 1 in `` must not be an atom.",
        "level": "Cannot pad list `3` which has `4` using padding `1` which specifies `2`.",
        "ilsm": "Expected an integer or a list of integers at position `1` in `2`.",
    }

    rules = {"%(name)s[l_]": "%(name)s[l, Automatic]"}

    @staticmethod
    def _find_dims(expr):
        def dive(expr, level):
            if isinstance(expr, Expression):
                if expr.elements:
                    return max(dive(x, level + 1) for x in expr.elements)
                else:
                    return level + 1
            else:
                return level

        def calc(expr, dims, level):
            if isinstance(expr, Expression):
                for x in expr.elements:
                    calc(x, dims, level + 1)
                dims[level] = max(dims[level], len(expr.elements))

        dims = [0] * dive(expr, 0)
        calc(expr, dims, 0)
        return dims

    @staticmethod
    def _build(
        element, n, x, m, level, mode
    ):  # mode < 0 for left pad, > 0 for right pad
        if not n:
            return element
        if not isinstance(element, Expression):
            raise _IllegalPaddingDepth(level)

        if isinstance(m, (list, tuple)):
            current_m = m[0] if m else 0
            next_m = m[1:]
        else:
            current_m = m
            next_m = m

        def clip(a, d, s):
            assert d != 0
            if s < 0:
                return a[-d:]  # end with a[-1]
            else:
                return a[:d]  # start with a[0]

        def padding(amount, sign):
            if amount == 0:
                return []
            elif len(n) > 1:
                return [
                    _Pad._build(ListExpression(), n[1:], x, next_m, level + 1, mode)
                ] * amount
            else:
                return clip(x * (1 + amount // len(x)), amount, sign)

        elements = element.elements
        d = n[0] - len(elements)
        if d < 0:
            new_elements = clip(elements, d, mode)
            padding_main = []
        elif d >= 0:
            new_elements = elements
            padding_main = padding(d, mode)

        if current_m > 0:
            padding_margin = padding(
                min(current_m, len(new_elements) + len(padding_main)), -mode
            )

            if len(padding_margin) > len(padding_main):
                padding_main = []
                new_elements = clip(
                    new_elements, -(len(padding_margin) - len(padding_main)), mode
                )
            elif len(padding_margin) > 0:
                padding_main = clip(padding_main, -len(padding_margin), mode)
        else:
            padding_margin = []

        if len(n) > 1:
            new_elements = (
                _Pad._build(e, n[1:], x, next_m, level + 1, mode) for e in new_elements
            )

        if mode < 0:
            parts = (padding_main, new_elements, padding_margin)
        else:
            parts = (padding_margin, new_elements, padding_main)

        return Expression(element.get_head(), *list(chain(*parts)))

    def _pad(self, in_l, in_n, in_x, in_m, evaluation, expr):
        if not isinstance(in_l, Expression):
            evaluation.message(self.get_name(), "normal", expr())
            return

        py_n = None
        if isinstance(in_n, Symbol) and in_n.get_name() == "System`Automatic":
            py_n = _Pad._find_dims(in_l)
        elif in_n.get_head_name() == "System`List":
            if all(isinstance(element, Integer) for element in in_n.elements):
                py_n = [element.get_int_value() for element in in_n.elements]
        elif isinstance(in_n, Integer):
            py_n = [in_n.get_int_value()]

        if py_n is None:
            evaluation.message(self.get_name(), "ilsm", 2, expr())
            return

        if in_x.get_head_name() == "System`List":
            py_x = in_x.elements
        else:
            py_x = [in_x]

        if isinstance(in_m, Integer):
            py_m = in_m.get_int_value()
        else:
            if not all(isinstance(x, Integer) for x in in_m.elements):
                evaluation.message(self.get_name(), "ilsm", 4, expr())
                return
            py_m = [x.get_int_value() for x in in_m.elements]

        try:
            return _Pad._build(in_l, py_n, py_x, py_m, 1, self._mode)
        except _IllegalPaddingDepth as e:

            def levels(k):
                if k == 1:
                    return "1 level"
                else:
                    return "%d levels" % k

            evaluation.message(
                self.get_name(),
                "level",
                in_n,
                levels(len(py_n)),
                in_l,
                levels(e.level - 1),
            )
            return None

    def apply_zero(self, element, n, evaluation):
        "%(name)s[element_, n_]"
        return self._pad(
            element,
            n,
            Integer0,
            Integer0,
            evaluation,
            lambda: Expression(self.get_name(), element, n),
        )

    def apply(self, element, n, x, evaluation):
        "%(name)s[element_, n_, x_]"
        return self._pad(
            element,
            n,
            x,
            Integer0,
            evaluation,
            lambda: Expression(self.get_name(), element, n, x),
        )

    def apply_margin(self, element, n, x, m, evaluation):
        "%(name)s[element_, n_, x_, m_]"
        return self._pad(
            element,
            n,
            x,
            m,
            evaluation,
            lambda: Expression(self.get_name(), element, n, x, m),
        )


class PadLeft(_Pad):
    """
    <dl>
    <dt>'PadLeft[$list$, $n$]'
        <dd>pads $list$ to length $n$ by adding 0 on the left.
    <dt>'PadLeft[$list$, $n$, $x$]'
        <dd>pads $list$ to length $n$ by adding $x$ on the left.
    <dt>'PadLeft[$list$, {$n1$, $n2, ...}, $x$]'
        <dd>pads $list$ to lengths $n1$, $n2$ at levels 1, 2, ... respectively by adding $x$ on the left.
    <dt>'PadLeft[$list$, $n$, $x$, $m$]'
        <dd>pads $list$ to length $n$ by adding $x$ on the left and adding a margin of $m$ on the right.
    <dt>'PadLeft[$list$, $n$, $x$, {$m1$, $m2$, ...}]'
        <dd>pads $list$ to length $n$ by adding $x$ on the left and adding margins of $m1$, $m2$, ...
         on levels 1, 2, ... on the right.
    <dt>'PadLeft[$list$]'
        <dd>turns the ragged list $list$ into a regular list by adding 0 on the left.
    </dl>

    >> PadLeft[{1, 2, 3}, 5]
     = {0, 0, 1, 2, 3}
    >> PadLeft[x[a, b, c], 5]
     = x[0, 0, a, b, c]
    >> PadLeft[{1, 2, 3}, 2]
     = {2, 3}
    >> PadLeft[{{}, {1, 2}, {1, 2, 3}}]
     = {{0, 0, 0}, {0, 1, 2}, {1, 2, 3}}
    >> PadLeft[{1, 2, 3}, 10, {a, b, c}, 2]
     = {b, c, a, b, c, 1, 2, 3, a, b}
    >> PadLeft[{{1, 2, 3}}, {5, 2}, x, 1]
     = {{x, x}, {x, x}, {x, x}, {3, x}, {x, x}}
    """

    _mode = -1
    summary_text = "pad out by the left a ragged array to make a matrix"


class PadRight(_Pad):
    """
    <dl>
    <dt>'PadRight[$list$, $n$]'
        <dd>pads $list$ to length $n$ by adding 0 on the right.
    <dt>'PadRight[$list$, $n$, $x$]'
        <dd>pads $list$ to length $n$ by adding $x$ on the right.
    <dt>'PadRight[$list$, {$n1$, $n2, ...}, $x$]'
        <dd>pads $list$ to lengths $n1$, $n2$ at levels 1, 2, ... respectively by adding $x$ on the right.
    <dt>'PadRight[$list$, $n$, $x$, $m$]'
        <dd>pads $list$ to length $n$ by adding $x$ on the left and adding a margin of $m$ on the left.
    <dt>'PadRight[$list$, $n$, $x$, {$m1$, $m2$, ...}]'
        <dd>pads $list$ to length $n$ by adding $x$ on the right and adding margins of $m1$, $m2$, ...
         on levels 1, 2, ... on the left.
    <dt>'PadRight[$list$]'
        <dd>turns the ragged list $list$ into a regular list by adding 0 on the right.
    </dl>

    >> PadRight[{1, 2, 3}, 5]
     = {1, 2, 3, 0, 0}
    >> PadRight[x[a, b, c], 5]
     = x[a, b, c, 0, 0]
    >> PadRight[{1, 2, 3}, 2]
     = {1, 2}
    >> PadRight[{{}, {1, 2}, {1, 2, 3}}]
     = {{0, 0, 0}, {1, 2, 0}, {1, 2, 3}}
    >> PadRight[{1, 2, 3}, 10, {a, b, c}, 2]
     = {b, c, 1, 2, 3, a, b, c, a, b}
    >> PadRight[{{1, 2, 3}}, {5, 2}, x, 1]
     = {{x, x}, {x, 1}, {x, x}, {x, x}, {x, x}}
    """

    _mode = 1
    summary_text = "pad out by the right a ragged array to make a matrix"


class _IllegalDistance(Exception):
    def __init__(self, distance):
        self.distance = distance


class _IllegalDataPoint(Exception):
    pass


def _to_real_distance(d):
    if not isinstance(d, (Real, Integer)):
        raise _IllegalDistance(d)

    mpd = d.to_mpmath()
    if mpd is None or mpd < 0:
        raise _IllegalDistance(d)

    return mpd


class _PrecomputedDistances(PrecomputedDistances):
    # computes all n^2 distances for n points with one big evaluation in the beginning.

    def __init__(self, df, p, evaluation):
        distances_form = [df(p[i], p[j]) for i in range(len(p)) for j in range(i)]
        distances = eval_N(ListExpression(*distances_form), evaluation)
        mpmath_distances = [_to_real_distance(d) for d in distances.elements]
        super(_PrecomputedDistances, self).__init__(mpmath_distances)


class _LazyDistances(LazyDistances):
    # computes single distances only as needed, caches already computed distances.

    def __init__(self, df, p, evaluation):
        super(_LazyDistances, self).__init__()
        self._df = df
        self._p = p
        self._evaluation = evaluation

    def _compute_distance(self, i, j):
        p = self._p
        d = eval_N(self._df(p[i], p[j]), self._evaluation)
        return _to_real_distance(d)


def _dist_repr(p):
    dist_p = repr_p = None
    if p.has_form("Rule", 2):
        if all(q.get_head_name() == "System`List" for q in p.elements):
            dist_p, repr_p = (q.elements for q in p.elements)
        elif (
            p.elements[0].get_head_name() == "System`List"
            and p.elements[1].get_name() == "System`Automatic"
        ):
            dist_p = p.elements[0].elements
            repr_p = [Integer(i + 1) for i in range(len(dist_p))]
    elif p.get_head_name() == "System`List":
        if all(q.get_head_name() == "System`Rule" for q in p.elements):
            dist_p, repr_p = ([q.elements[i] for q in p.elements] for i in range(2))
        else:
            dist_p = repr_p = p.elements
    return dist_p, repr_p


class _Cluster(Builtin):
    options = {
        "Method": "Optimize",
        "DistanceFunction": "Automatic",
        "RandomSeed": "Automatic",
    }

    messages = {
        "amtd": "`1` failed to pick a suitable distance function for `2`.",
        "bdmtd": 'Method in `` must be either "Optimize", "Agglomerate" or "KMeans".',
        "intpm": "Positive integer expected at position 2 in ``.",
        "list": "Expected a list or a rule with equally sized lists at position 1 in ``.",
        "nclst": "Cannot find more clusters than there are elements: `1` is larger than `2`.",
        "xnum": "The distance function returned ``, which is not a non-negative real value.",
        "rseed": "The random seed specified through `` must be an integer or Automatic.",
        "kmsud": "KMeans only supports SquaredEuclideanDistance as distance measure.",
    }

    _criteria = {
        "Optimize": AutomaticSplitCriterion,
        "Agglomerate": AutomaticMergeCriterion,
        "KMeans": None,
    }

    def _cluster(self, p, k, mode, evaluation, options, expr):
        method_string, method = self.get_option_string(options, "Method", evaluation)
        if method_string not in ("Optimize", "Agglomerate", "KMeans"):
            evaluation.message(
                self.get_name(), "bdmtd", Expression(SymbolRule, "Method", method)
            )
            return

        dist_p, repr_p = _dist_repr(p)

        if dist_p is None or len(dist_p) != len(repr_p):
            evaluation.message(self.get_name(), "list", expr)
            return

        if not dist_p:
            return ListExpression()

        if k is not None:  # the number of clusters k is specified as an integer.
            if not isinstance(k, Integer):
                evaluation.message(self.get_name(), "intpm", expr)
                return
            py_k = k.get_int_value()
            if py_k < 1:
                evaluation.message(self.get_name(), "intpm", expr)
                return
            if py_k > len(dist_p):
                evaluation.message(self.get_name(), "nclst", py_k, len(dist_p))
                return
            elif py_k == 1:
                return ListExpression(*repr_p)
            elif py_k == len(dist_p):
                return ListExpression(*[ListExpression(q) for q in repr_p])
        else:  # automatic detection of k. choose a suitable method here.
            if len(dist_p) <= 2:
                return ListExpression(*repr_p)
            constructor = self._criteria.get(method_string)
            py_k = (constructor, {}) if constructor else None

        seed_string, seed = self.get_option_string(options, "RandomSeed", evaluation)
        if seed_string == "Automatic":
            py_seed = 12345
        elif isinstance(seed, Integer):
            py_seed = seed.get_int_value()
        else:
            evaluation.message(
                self.get_name(), "rseed", Expression(SymbolRule, "RandomSeed", seed)
            )
            return

        distance_function_string, distance_function = self.get_option_string(
            options, "DistanceFunction", evaluation
        )
        if distance_function_string == "Automatic":
            from mathics.builtin.tensors import get_default_distance

            distance_function = get_default_distance(dist_p)
            if distance_function is None:
                name_of_builtin = strip_context(self.get_name())
                evaluation.message(
                    self.get_name(),
                    "amtd",
                    name_of_builtin,
                    ListExpression(*dist_p),
                )
                return
        if method_string == "KMeans" and distance_function is not Symbol(
            "SquaredEuclideanDistance"
        ):
            evaluation.message(self.get_name(), "kmsud")
            return

        def df(i, j) -> Expression:
            return Expression(distance_function, i, j)

        try:
            if method_string == "Agglomerate":
                clusters = self._agglomerate(mode, repr_p, dist_p, py_k, df, evaluation)
            elif method_string == "Optimize":
                clusters = optimize(
                    repr_p, py_k, _LazyDistances(df, dist_p, evaluation), mode, py_seed
                )
            elif method_string == "KMeans":
                clusters = self._kmeans(mode, repr_p, dist_p, py_k, py_seed, evaluation)
        except _IllegalDistance as e:
            evaluation.message(self.get_name(), "xnum", e.distance)
            return
        except _IllegalDataPoint:
            name_of_builtin = strip_context(self.get_name())
            evaluation.message(
                self.get_name(),
                "amtd",
                name_of_builtin,
                ListExpression(*dist_p),
            )
            return

        if mode == "clusters":
            return ListExpression(*[ListExpression(*c) for c in clusters])
        elif mode == "components":
            return to_mathics_list(*clusters)
        else:
            raise ValueError("illegal mode %s" % mode)

    def _agglomerate(self, mode, repr_p, dist_p, py_k, df, evaluation):
        if mode == "clusters":
            clusters = agglomerate(
                repr_p, py_k, _PrecomputedDistances(df, dist_p, evaluation), mode
            )
        elif mode == "components":
            clusters = agglomerate(
                repr_p, py_k, _PrecomputedDistances(df, dist_p, evaluation), mode
            )

        return clusters

    def _kmeans(self, mode, repr_p, dist_p, py_k, py_seed, evaluation):
        items = []

        def convert_scalars(p):
            for q in p:
                if not isinstance(q, (Real, Integer)):
                    raise _IllegalDataPoint
                mpq = q.to_mpmath()
                if mpq is None:
                    raise _IllegalDataPoint
                items.append(q)
                yield mpq

        def convert_vectors(p):
            d = None
            for q in p:
                if q.get_head_name() != "System`List":
                    raise _IllegalDataPoint
                v = list(convert_scalars(q.elements))
                if d is None:
                    d = len(v)
                elif len(v) != d:
                    raise _IllegalDataPoint
                yield v

        if dist_p[0].is_numeric(evaluation):
            numeric_p = [[x] for x in convert_scalars(dist_p)]
        else:
            numeric_p = list(convert_vectors(dist_p))

        # compute epsilon similar to Real.__eq__, such that "numbers that differ in their last seven binary digits
        # are considered equal"

        prec = min_prec(*items) or machine_precision
        eps = 0.5 ** (prec - 7)

        return kmeans(numeric_p, repr_p, py_k, mode, py_seed, eps)


class FindClusters(_Cluster):
    """
    <dl>
    <dt>'FindClusters[$list$]'
        <dd>returns a list of clusters formed from the elements of $list$. The number of cluster is determined
        automatically.
    <dt>'FindClusters[$list$, $k$]'
        <dd>returns a list of $k$ clusters formed from the elements of $list$.
    </dl>

    >> FindClusters[{1, 2, 20, 10, 11, 40, 19, 42}]
     = {{1, 2, 20, 10, 11, 19}, {40, 42}}

    >> FindClusters[{25, 100, 17, 20}]
     = {{25, 17, 20}, {100}}

    >> FindClusters[{3, 6, 1, 100, 20, 5, 25, 17, -10, 2}]
     = {{3, 6, 1, 5, -10, 2}, {100}, {20, 25, 17}}

    >> FindClusters[{1, 2, 10, 11, 20, 21}]
     = {{1, 2}, {10, 11}, {20, 21}}

    >> FindClusters[{1, 2, 10, 11, 20, 21}, 2]
     = {{1, 2, 10, 11}, {20, 21}}

    >> FindClusters[{1 -> a, 2 -> b, 10 -> c}]
     = {{a, b}, {c}}

    >> FindClusters[{1, 2, 5} -> {a, b, c}]
     = {{a, b}, {c}}

    >> FindClusters[{1, 2, 3, 1, 2, 10, 100}, Method -> "Agglomerate"]
     = {{1, 2, 3, 1, 2, 10}, {100}}

    >> FindClusters[{1, 2, 3, 10, 17, 18}, Method -> "Agglomerate"]
     = {{1, 2, 3}, {10}, {17, 18}}

    >> FindClusters[{{1}, {5, 6}, {7}, {2, 4}}, DistanceFunction -> (Abs[Length[#1] - Length[#2]]&)]
     = {{{1}, {7}}, {{5, 6}, {2, 4}}}

    >> FindClusters[{"meep", "heap", "deep", "weep", "sheep", "leap", "keep"}, 3]
     = {{meep, deep, weep, keep}, {heap, leap}, {sheep}}

    FindClusters' automatic distance function detection supports scalars, numeric tensors, boolean vectors and
    strings.

    The Method option must be either "Agglomerate" or "Optimize". If not specified, it defaults to "Optimize".
    Note that the Agglomerate and Optimize methods usually produce different clusterings.

    The runtime of the Agglomerate method is quadratic in the number of clustered points n, builds the clustering
    from the bottom up, and is exact (no element of randomness). The Optimize method's runtime is linear in n,
    Optimize builds the clustering from top down, and uses random sampling.
    """

    summary_text = "divide data into lists of similar elements"

    def apply(self, p, evaluation, options):
        "FindClusters[p_, OptionsPattern[%(name)s]]"
        return self._cluster(
            p,
            None,
            "clusters",
            evaluation,
            options,
            Expression(SymbolFindClusters, p, *options_to_rules(options)),
        )

    def apply_manual_k(self, p, k: Integer, evaluation, options):
        "FindClusters[p_, k_Integer, OptionsPattern[%(name)s]]"
        return self._cluster(
            p,
            k,
            "clusters",
            evaluation,
            options,
            Expression(SymbolFindClusters, p, k, *options_to_rules(options)),
        )


class ClusteringComponents(_Cluster):
    """
    <dl>
    <dt>'ClusteringComponents[$list$]'
        <dd>forms clusters from $list$ and returns a list of cluster indices, in which each
        element shows the index of the cluster in which the corresponding element in $list$
        ended up.
    <dt>'ClusteringComponents[$list$, $k$]'
        <dd>forms $k$ clusters from $list$ and returns a list of cluster indices, in which
        each element shows the index of the cluster in which the corresponding element in
        $list$ ended up.
    </dl>

    For more detailed documentation regarding options and behavior, see FindClusters[].

    >> ClusteringComponents[{1, 2, 3, 1, 2, 10, 100}]
     = {1, 1, 1, 1, 1, 1, 2}

    >> ClusteringComponents[{10, 100, 20}, Method -> "KMeans"]
     = {1, 0, 1}
    """

    summary_text = "label data with the index of the cluster it is in"

    def apply(self, p, evaluation, options):
        "ClusteringComponents[p_, OptionsPattern[%(name)s]]"
        return self._cluster(
            p,
            None,
            "components",
            evaluation,
            options,
            Expression(SymbolClusteringComponents, p, *options_to_rules(options)),
        )

    def apply_manual_k(self, p, k: Integer, evaluation, options):
        "ClusteringComponents[p_, k_Integer, OptionsPattern[%(name)s]]"
        return self._cluster(
            p,
            k,
            "components",
            evaluation,
            options,
            Expression(SymbolClusteringComponents, p, k, *options_to_rules(options)),
        )


class Nearest(Builtin):
    """
    <dl>
      <dt>'Nearest[$list$, $x$]'
      <dd>returns the one item in $list$ that is nearest to $x$.

      <dt>'Nearest[$list$, $x$, $n$]'
      <dd>returns the $n$ nearest items.

      <dt>'Nearest[$list$, $x$, {$n$, $r$}]'
      <dd>returns up to $n$ nearest items that are not farther from $x$ than $r$.

      <dt>'Nearest[{$p1$ -> $q1$, $p2$ -> $q2$, ...}, $x$]'
      <dd>returns $q1$, $q2$, ... but measures the distances using $p1$, $p2$, ...

      <dt>'Nearest[{$p1$, $p2$, ...} -> {$q1$, $q2$, ...}, $x$]'
      <dd>returns $q1$, $q2$, ... but measures the distances using $p1$, $p2$, ...
    </dl>

    >> Nearest[{5, 2.5, 10, 11, 15, 8.5, 14}, 12]
     = {11}

    Return all items within a distance of 5:

    >> Nearest[{5, 2.5, 10, 11, 15, 8.5, 14}, 12, {All, 5}]
     = {11, 10, 14}

    >> Nearest[{Blue -> "blue", White -> "white", Red -> "red", Green -> "green"}, {Orange, Gray}]
     = {{red}, {white}}

    >> Nearest[{{0, 1}, {1, 2}, {2, 3}} -> {a, b, c}, {1.1, 2}]
     = {b}
    """

    messages = {
        "amtd": "`1` failed to pick a suitable distance function for `2`.",
        "list": "Expected a list or a rule with equally sized lists at position 1 in ``.",
        "nimp": "Method `1` is not implemented yet.",
    }

    options = {
        "DistanceFunction": "Automatic",
        "Method": '"Scan"',
    }

    rules = {
        "Nearest[list_, pattern_]": "Nearest[list, pattern, 1]",
        "Nearest[pattern_][list_]": "Nearest[list, pattern]",
    }
    summary_text = "the nearest element from a list"

    def apply(self, items, pivot, limit, expression, evaluation, options):
        "Nearest[items_, pivot_, limit_, OptionsPattern[%(name)s]]"

        method = self.get_option(options, "Method", evaluation)
        if not isinstance(method, String) or method.get_string_value() != "Scan":
            evaluation("Nearest", "nimp", method)
            return

        dist_p, repr_p = _dist_repr(items)

        if dist_p is None or len(dist_p) != len(repr_p):
            evaluation.message(self.get_name(), "list", expression)
            return

        if limit.has_form("List", 2):
            up_to = limit.elements[0]
            py_r = limit.elements[1].to_mpmath()
        else:
            up_to = limit
            py_r = None

        if isinstance(up_to, Integer):
            py_n = up_to.get_int_value()
        elif up_to.get_name() == "System`All":
            py_n = None
        else:
            return

        if not dist_p or (py_n is not None and py_n < 1):
            return ListExpression()

        multiple_x = False

        distance_function_string, distance_function = self.get_option_string(
            options, "DistanceFunction", evaluation
        )
        if distance_function_string == "Automatic":
            from mathics.builtin.tensors import get_default_distance

            distance_function = get_default_distance(dist_p)
            if distance_function is None:
                evaluation.message(
                    self.get_name(), "amtd", "Nearest", ListExpression(*dist_p)
                )
                return

            if pivot.get_head_name() == "System`List":
                _, depth_x = walk_levels(pivot)
                _, depth_items = walk_levels(dist_p[0])

                if depth_x > depth_items:
                    multiple_x = True

        def nearest(x) -> ListExpression:
            calls = [Expression(distance_function, x, y) for y in dist_p]
            distances = ListExpression(*calls).evaluate(evaluation)

            if not distances.has_form("List", len(dist_p)):
                raise ValueError()

            py_distances = [
                (_to_real_distance(d), i) for i, d in enumerate(distances.elements)
            ]

            if py_r is not None:
                py_distances = [(d, i) for d, i in py_distances if d <= py_r]

            def pick():
                if py_n is None:
                    candidates = sorted(py_distances)
                else:
                    candidates = heapq.nsmallest(py_n, py_distances)

                for d, i in candidates:
                    yield repr_p[i]

            return ListExpression(*list(pick()))

        try:
            if not multiple_x:
                return nearest(pivot)
            else:
                return ListExpression(*[nearest(t) for t in pivot.elements])
        except _IllegalDistance:
            return SymbolFailed
        except ValueError:
            return SymbolFailed


class SubsetQ(Builtin):
    """
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
        "argr": "SubsetQ called with 1 argument; 2 arguments are expected.",
        "argrx": "SubsetQ called with `1` arguments; 2 arguments are expected.",
        "heads": "Heads `1` and `2` at positions 1 and 2 are expected to be the same.",
        "normal": "Nonatomic expression expected at position `1` in `2`.",
    }
    summary_text = "test if a list is a subset of another list"

    def apply(self, expr, subset, evaluation):
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


#    rules = {'Failure /: MakeBoxes[Failure[tag_, assoc_Association], StandardForm]' :
# 		'With[{msg = assoc["MessageTemplate"], msgParam = assoc["MessageParameters"], type = assoc["Type"]}, ToBoxes @ Interpretation["Failure" @ Panel @ Grid[{{Style["\[WarningSign]", "Message", FontSize -> 35], Style["Message:", FontColor->GrayLevel[0.5]], ToString[StringForm[msg, Sequence @@ msgParam], StandardForm]}, {SpanFromAbove, Style["Tag:", FontColor->GrayLevel[0.5]], ToString[tag, StandardForm]},{SpanFromAbove,Style["Type:", FontColor->GrayLevel[0.5]],ToString[type, StandardForm]}},Alignment -> {Left, Top}], Failure[tag, assoc]] /; msg =!= Missing["KeyAbsent", "MessageTemplate"] && msgParam =!= Missing["KeyAbsent", "MessageParameters"] && msgParam =!= Missing["KeyAbsent", "Type"]]',
#     }
