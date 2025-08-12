# -*- coding: utf-8 -*-
"""
Applying Functions to Lists

Many computations can be conveniently specified in terms of applying functions \
in parallel to many elements in a list.

Many mathematical functions are automatically taken to be "listable", so that \
they are always applied to every element in a list.
"""

from typing import Iterable

from mathics.core.atoms import Integer, Integer0, Integer1, Integer3
from mathics.core.builtin import Builtin, InfixOperator
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import InvalidLevelspecError, MessageException
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, SymbolNull, SymbolTrue
from mathics.core.systemsymbols import SymbolMapThread
from mathics.eval.functional.apply_fns_to_lists import eval_MapAt
from mathics.eval.parts import python_levelspec, walk_levels
from mathics.eval.patterns import param_and_option_from_optional_place

# This tells documentation how to sort this module
sort_order = "mathics.builtin.applying-functions-to-lists"


class Apply(InfixOperator):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/Apply.html</url>


    <dl>
      <dt>'Apply'[$f$, $expr$]

      <dt>'$f$ @@ $expr$'
      <dd>replaces the head of $expr$ with $f$.

      <dt>'Apply'[$f$, $expr$, $levelspec$]
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
    """

    summary_text = "apply a function to a list, at specified levels"
    grouping = "Right"

    options = {
        "Heads": "False",
    }

    def eval(self, f, expr, levelspec, evaluation, options={}):
        """Apply[f_, expr_, Optional[levelspec_, {0}],
        OptionsPattern[Apply]]"""

        levelspec = param_and_option_from_optional_place(
            levelspec, options, "System`Apply", evaluation
        ) or ListExpression(Integer0)

        try:
            start, stop = python_levelspec(levelspec)
        except InvalidLevelspecError:
            evaluation.message("Apply", "level", levelspec)
            return

        def callback(level):
            if isinstance(level, Atom):
                return level
            else:
                return Expression(f, *level.elements)

        heads = self.get_option(options, "Heads", evaluation) is SymbolTrue
        result, _ = walk_levels(expr, start, stop, heads=heads, callback=callback)

        return result


class Map(InfixOperator):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/Map.html</url>

    <dl>
      <dt>'Map'[$f$, $expr$] or '$f$ /@ $expr$'
      <dd>applies $f$ to each part on the first level of $expr$.

      <dt>'Map'[$f$, $expr$, $levelspec$]
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
    """

    summary_text = "map a function over a list, at specified levels"
    grouping = "Right"

    options = {
        "Heads": "False",
    }

    def eval_level(self, f, expr, levelspec, evaluation, options={}):
        """Map[f_, expr_, Optional[levelspec_, {1}],
        OptionsPattern[Map]]"""

        levelspec = param_and_option_from_optional_place(
            levelspec, options, "System`Map", evaluation
        ) or ListExpression(Integer1)
        try:
            start, stop = python_levelspec(levelspec)
        except InvalidLevelspecError:
            evaluation.message("Map", "level", levelspec)
            return

        def callback(level):
            return Expression(f, level)

        heads = self.get_option(options, "Heads", evaluation) is SymbolTrue
        result, _ = walk_levels(expr, start, stop, heads=heads, callback=callback)

        return result


class MapAt(Builtin):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/MapAt.html</url>

    <dl>
      <dt>'MapAt'[$f$, $expr$, $n$]
      <dd>applies $f$ to the element at position $n$ in $expr$. If $n$ is negative, the position is counted from the end.

      <dt>'MapAt'[f, $expr$, {$i$, $j$ ...}]
      <dd>applies $f$ to the part of $expr$ at position {$i$, $j$, ...}.

      <dt>'MapAt'[$f$, $pos$]
      <dd>represents an operator form of 'MapAt' that can be applied to an expression.
    </dl>

    Map function $f$ to the second element of an simple flat list:
    >> MapAt[f, {a, b, c}, 2]
     = {a, f[b], c}

    Above, we specified a simple integer value 2. In general, the expression can be an arbitrary vector.

    Using 'MapAt' with 'Function[0]', we can zero a value or values in a vector:

    >> MapAt[0&, {{1, 1}, {1, 1}}, {2, 1}]
     = {{1, 1}, {0, 1}}

    When the dimension of the replacement expression is less than the vector, \
    that element's dimension changes:

    >> MapAt[0&, {{0, 1}, {1, 0}}, 2]
     = {{0, 1}, 0}

    So now compare what happen when using {{2}, {1}} instead of {2, 1} above:
    >> MapAt[0&, {{0, 1}, {1, 0}}, {{2}, {1}}]
     = {0, 0}

    Map $f$ onto the last element of a list:
    >> MapAt[f, {a, b, c}, -1]
     = {a, b, f[c]}

    Same as above, but use the operator form of 'MapAt':
    >> MapAt[f, -1][{a, b, c}]
     = {a, b, f[c]}

    Map $f$ onto at the second position of an association:
    >> MapAt[f, <|"a" -> 1, "b" -> 2, "c" -> 3, "d" -> 4|>, 2]
     = {a -> 1, b -> f[2], c -> 3, d -> 4}

    Same as above, but select the second-from-the-end position:
    >> MapAt[f, <|"a" -> 1, "b" -> 2, "c" -> 3, "d" -> 4|>, -2]
     = {a -> 1, b -> 2, c -> f[3], d -> 4}

    """

    rules = {
        "MapAt[f_, pos_][expr_]": "MapAt[f, expr, pos]",
    }
    summary_text = "map a function at particular positions"

    def eval(self, f, expr, args, evaluation: Evaluation):
        "MapAt[f_, expr_, args_]"
        return eval_MapAt(f, expr, args, evaluation)


class MapIndexed(Builtin):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/MapIndexed.html</url>

    <dl>
      <dt>'MapIndexed'[$f$, $expr$]
      <dd>applies $f$ to each part on the first level of $expr$, including the part positions in the call to $f$.

      <dt>'MapIndexed'[$f$, $expr$, $levelspec$]
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
    """

    summary_text = "map a function, including index information"
    options = {
        "Heads": "False",
    }

    def eval_level(self, f, expr, levelspec, evaluation, options={}):
        """MapIndexed[f_, expr_, Optional[levelspec_, {1}],
        OptionsPattern[MapIndexed]]"""
        levelspec = param_and_option_from_optional_place(
            levelspec, options, "System`MapIndexed", evaluation
        ) or ListExpression(Integer1)
        try:
            start, stop = python_levelspec(levelspec)
        except InvalidLevelspecError:
            evaluation.message("MapIndexed", "level", levelspec)
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
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/MapThread.html</url>

    <dl>
      <dt>'MapThread[$f$, {{$a_1$, $a_2$, ...}, {$b_1$, $b_2$, ...}, ...}]
      <dd>returns '{$f$[$a_1$, $b_1$, ...], $f$[$a_2$, $b_2$, ...], ...}'.

      <dt>'MapThread'[$f$, {$expr_1$, $expr_2$, ...}, $n$]
      <dd>applies $f$ at level $n$.
    </dl>

    >> MapThread[f, {{a, b, c}, {1, 2, 3}}]
     = {f[a, 1], f[b, 2], f[c, 3]}

    >> MapThread[f, {{{a, b}, {c, d}}, {{e, f}, {g, h}}}, 2]
     = {{f[a, e], f[b, f]}, {f[c, g], f[d, h]}}
    """

    summary_text = "map a function across corresponding elements in multiple lists"
    messages = {
        "mptc": "Incompatible dimensions of objects at positions {2, `1`} and {2, `2`} of `3`; dimensions are `4` and `5`.",
        "mptd": "Object `1` at position {2, `2`} in `3` has only `4` of required `5` dimensions.",
        "list": "List expected at position `2` in `1`.",
    }

    def eval(self, f, expr, evaluation):
        "MapThread[f_, expr_]"

        return self.eval_n(f, expr, None, evaluation)

    def eval_n(self, f, expr, n, evaluation):
        "MapThread[f_, expr_, n_]"

        if n is None:
            n = 1
            full_expr = Expression(SymbolMapThread, f, expr)
        else:
            full_expr = Expression(SymbolMapThread, f, expr, n)
            n = n.get_int_value()

        if n is None or n < 0:
            evaluation.message("MapThread", "intnm", Integer3, full_expr)
            return

        if expr.has_form("List", 0):
            return ListExpression()
        if not expr.has_form("List", None):
            evaluation.message("MapThread", "list", 2, full_expr)
            return

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


class Scan(Builtin):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/Scan.html</url>

    <dl>
      <dt>'Scan'[$f$, $expr$]
      <dd>applies $f$ to each element of $expr$ and returns 'Null'.

      <dt>'Scan'[$f$, $expr$, $levelspec$]
      <dd>applies $f$ to each level specified by $levelspec$ of $expr$.
    </dl>

    >> Scan[Print, {1, 2, 3}]
     | 1
     | 2
     | 3
    """

    summary_text = "scan over every element of a list, applying a function"
    options = {
        "Heads": "False",
    }

    rules = {
        "Scan[f_][expr_]": "Scan[f, expr]",
    }

    def eval_level(self, f, expr, levelspec, evaluation, options={}):
        """Scan[f_, expr_, Optional[levelspec_, {1}],
        OptionsPattern[Map]]"""
        levelspec = param_and_option_from_optional_place(
            levelspec, options, "System`Scan", evaluation
        ) or ListExpression(Integer0)
        try:
            start, stop = python_levelspec(levelspec)
        except InvalidLevelspecError:
            evaluation.message("Map", "level", levelspec)
            return

        def callback(level):
            Expression(f, level).evaluate(evaluation)
            return level

        heads = self.get_option(options, "Heads", evaluation) is SymbolTrue
        result, depth = walk_levels(expr, start, stop, heads=heads, callback=callback)

        return SymbolNull


class Thread(Builtin):
    """
    <url>:WMA link:
      https://reference.wolfram.com/language/ref/Thread.html</url>

    <dl>
      <dt>'Thread[$f$'[$args$]]
      <dd>threads $f$ over any lists that appear in $args$.

      <dt>'Thread[$f$'[$args$], $h$]
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

    def eval(self, f, args, h, evaluation: Evaluation):
        "Thread[f_[args___], h_]"

        args = args.get_sequence()
        expr = Expression(f, *args)
        _, result = expr.thread(evaluation, head=h)
        return result
