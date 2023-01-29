# -*- coding: utf-8 -*-
"""
Rearranging and Restructuring Lists

These functions reorder and rearrange lists.
"""

import functools
from collections import defaultdict
from itertools import chain
from typing import Callable

from mathics.builtin.base import Builtin, MessageException
from mathics.core.atoms import Integer, Integer0, Integer1
from mathics.core.attributes import A_FLAT, A_ONE_IDENTITY, A_PROTECTED
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression, structure
from mathics.core.list import ListExpression
from mathics.core.symbols import Atom, Symbol, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolDirectedInfinity,
    SymbolMap,
    SymbolReverse,
    SymbolSplit,
)
from mathics.eval.parts import walk_levels


def _test_pair(test, a, b, evaluation, name):
    test_expr = Expression(test, a, b)
    result = test_expr.evaluate(evaluation)
    if not (
        isinstance(result, Symbol)
        and (result.has_symbol("True") or result.has_symbol("False"))
    ):
        evaluation.message(name, "smtst", test_expr, result)
    return result is SymbolTrue


def _is_sameq(same_test):
    # System`SameQ is protected, so nobody should ever be able to change
    # it (see Set::wrsym). We just check for its name here thus.
    return isinstance(same_test, Symbol) and same_test.get_name() == "System`SameQ"


class _FastEquivalence:
    """
    Models an equivalence relation using SameQ. for n distinct elements (each
    in its own bin), we expect to make O(n) comparisons (if the hash function
    does not fail us by distributing items very unevenly).

    IMPORTANT NOTE ON ATOM'S HASH FUNCTIONS / this code relies on this assumption:
       if SameQ[a, b] == true then hash(a) == hash(b)

    Specifically, this code bins items based on their hash code, and only if
    the hash code matches, is SameQ evoked.

    This assumption has been checked for these types: Integer, Real, Complex,
    String, Rational (*), Expression, Image; new atoms need proper hash functions

    (*) Rational values are sympy Rationals which are always held in reduced form
    and thus are hashed correctly (see sympy/core/number.py:Rational.__eq__()).
    """

    def __init__(self):
        self._hashes = defaultdict(list)

    def select(self, elem):
        return self._hashes[hash(elem)]

    def sameQ(self, a, b) -> bool:
        """Mathics SameQ"""
        return a.sameQ(b)


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

    def eval_zero(self, element, n, evaluation: Evaluation):
        "%(name)s[element_, n_]"
        return self._pad(
            element,
            n,
            Integer0,
            Integer0,
            evaluation,
            lambda: Expression(self.get_name(), element, n),
        )

    def eval(self, element, n, x, evaluation: Evaluation):
        "%(name)s[element_, n_, x_]"
        return self._pad(
            element,
            n,
            x,
            Integer0,
            evaluation,
            lambda: Expression(self.get_name(), element, n, x),
        )

    def eval_margin(self, element, n, x, m, evaluation: Evaluation):
        "%(name)s[element_, n_, x_, m_]"
        return self._pad(
            element,
            n,
            x,
            m,
            evaluation,
            lambda: Expression(self.get_name(), element, n, x, m),
        )


class _SlowEquivalence:
    # models an equivalence relation through a user defined test function. for n
    # distinct elements (each in its own bin), we need sum(1, .., n - 1) = O(n^2)
    # comparisons.

    def __init__(self, test, evaluation, name):
        self._groups = []
        self._test = test
        self._evaluation = evaluation
        self._name = name

    def select(self, elem):
        return self._groups

    def sameQ(self, a, b) -> bool:
        """Mathics SameQ"""
        return _test_pair(self._test, a, b, self._evaluation, self._name)


class _DeleteDuplicatesBin:
    def __init__(self, item):
        self._item = item
        self.add_to = lambda elem: None

    def from_python(self):
        return self._item


class _GatherBin:
    def __init__(self, item):
        self._items = [item]
        self.add_to = self._items.append

    def from_python(self):
        return ListExpression(*self._items)


class _GatherOperation(Builtin):
    rules = {"%(name)s[list_]": "%(name)s[list, SameQ]"}

    messages = {
        "normal": "Nonatomic expression expected at position `1` in `2`.",
        "list": "List expected at position `2` in `1`.",
        "smtst": (
            "Application of the SameTest yielded `1`, which evaluates "
            "to `2`. The SameTest must evaluate to True or False at "
            "every pair of elements."
        ),
    }

    def eval(self, values, test, evaluation: Evaluation):
        "%(name)s[values_, test_]"
        if not self._check_list(values, test, evaluation):
            return

        if _is_sameq(test):
            return self._gather(values, values, _FastEquivalence())
        else:
            return self._gather(
                values, values, _SlowEquivalence(test, evaluation, self.get_name())
            )

    def _check_list(self, values, arg2, evaluation: Evaluation):
        if isinstance(values, Atom):
            expr = Expression(Symbol(self.get_name()), values, arg2)
            evaluation.message(self.get_name(), "normal", 1, expr)
            return False

        if values.get_head_name() != "System`List":
            expr = Expression(Symbol(self.get_name()), values, arg2)
            evaluation.message(self.get_name(), "list", expr, 1)
            return False

        return True

    def _gather(self, keys, values, equivalence):
        bins = []
        Bin = self._bin

        for key, value in zip(keys.elements, values.elements):
            selection = equivalence.select(key)
            for prototype, add_to_bin in selection:  # find suitable bin
                if equivalence.sameQ(prototype, key):
                    add_to_bin(value)  # add to existing bin
                    break
            else:
                new_bin = Bin(value)  # create new bin
                selection.append((key, new_bin.add_to))
                bins.append(new_bin)

        return ListExpression(*[b.from_python() for b in bins])


class _Rotate(Builtin):
    messages = {"rspec": "`` should be an integer or a list of integers."}

    def _rotate(self, expr, n, evaluation: Evaluation):
        if not isinstance(expr, Expression):
            return expr

        elements = expr.elements
        if not elements:
            return expr

        index = (self._sign * n[0]) % len(elements)  # with Python's modulo: index >= 1
        new_elements = chain(elements[index:], elements[:index])

        if len(n) > 1:
            new_elements = [
                self._rotate(item, n[1:], evaluation) for item in new_elements
            ]

        return expr.restructure(expr.head, new_elements, evaluation)

    def eval_one(self, expr, evaluation: Evaluation):
        "%(name)s[expr_]"
        return self._rotate(expr, [1], evaluation)

    def eval(self, expr, n, evaluation: Evaluation):
        "%(name)s[expr_, n_]"
        if isinstance(n, Integer):
            py_cycles = [n.get_int_value()]
        elif n.get_head_name() == "System`List" and all(
            isinstance(x, Integer) for x in n.elements
        ):
            py_cycles = [x.get_int_value() for x in n.elements]
            if not py_cycles:
                return expr
        else:
            evaluation.message(self.get_name(), "rspec", n)
            return

        return self._rotate(expr, py_cycles, evaluation)


class _SetOperation(Builtin):
    messages = {
        "normal": "Non-atomic expression expected at position `1` in `2`.",
        "heads": (
            "Heads `1` and `2` at positions `3` and `4` are expected " "to be the same."
        ),
        "smtst": (
            "Application of the SameTest yielded `1`, which evaluates "
            "to `2`. The SameTest must evaluate to True or False at "
            "every pair of elements."
        ),
    }

    options = {
        "SameTest": "SameQ",
    }

    @staticmethod
    def _remove_duplicates(arg, same_test):
        "removes duplicates from a single operand"
        result = []
        for a in arg:
            if not any(same_test(a, b) for b in result):
                result.append(a)
        return result

    def eval(self, lists, evaluation, options={}):
        "%(name)s[lists__, OptionsPattern[%(name)s]]"

        seq = lists.get_sequence()

        for pos, e in enumerate(seq):
            if isinstance(e, Atom):
                evaluation.message(
                    self.get_name(),
                    "normal",
                    pos + 1,
                    Expression(Symbol(self.get_name()), *seq),
                )
                return

        for pos, e in enumerate(zip(seq, seq[1:])):
            e1, e2 = e
            if e1.head != e2.head:
                evaluation.message(
                    self.get_name(), "heads", e1.head, e2.head, pos + 1, pos + 2
                )
                return

        same_test = self.get_option(options, "SameTest", evaluation)
        operands = [li.elements for li in seq]
        if not _is_sameq(same_test):

            def sameQ(a, b):
                return _test_pair(same_test, a, b, evaluation, self.get_name())

            operands = [self._remove_duplicates(op, sameQ) for op in operands]
            items = functools.reduce(
                lambda a, b: [e for e in self._elementwise(a, b, sameQ)], operands
            )
        else:
            items = list(
                functools.reduce(getattr(set, self._operation), map(set, operands))
            )

        return Expression(seq[0].get_head(), *sorted(items))


class _TallyBin:
    def __init__(self, item):
        self._item = item
        self._count = 1

    def add_to(self, item):
        self._count += 1

    def from_python(self):
        return ListExpression(self._item, Integer(self._count))


class Catenate(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Catenate.html</url>

    <dl>
      <dt>'Catenate[{$l1$, $l2$, ...}]'
      <dd>concatenates the lists $l1$, $l2$, ...
    </dl>

    >> Catenate[{{1, 2, 3}, {4, 5}}]
     = {1, 2, 3, 4, 5}
    """

    summary_text = "catenate elements from a list of lists"
    messages = {"invrp": "`1` is not a list."}

    def eval(self, lists, evaluation: Evaluation):
        "Catenate[lists_List]"

        def parts():
            for li in lists.elements:
                head_name = li.get_head_name()
                if head_name == "System`List":
                    yield li.elements
                elif head_name != "System`Missing":
                    raise MessageException("Catenate", "invrp", li)

        try:
            result = list(chain(*list(parts())))
            if result:
                return lists.elements[0].restructure(
                    "List", result, evaluation, deps=lists.elements
                )
            else:
                return ListExpression()
        except MessageException as e:
            e.message(evaluation)


class Complement(_SetOperation):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Complement.html</url>

    <dl>
      <dt>'Complement[$all$, $e1$, $e2$, ...]'
      <dd>returns an expression containing the elements in the set $all$ \
          that are not in any of $e1$, $e2$, etc.

      <dt>'Complement[$all$, $e1$, $e2$, ..., SameTest->$test$]'
      <dd>applies $test$ to the elements in $all$ and each of the $ei$ to \
          determine equality.
    </dl>

    The sets $all$, $e1$, etc can have any head, which must all match.

    The returned expression has the same head as the input \
    expressions. The expression will be sorted and each element will \
    only occur once.

    >> Complement[{a, b, c}, {a, c}]
     = {b}
    >> Complement[{a, b, c}, {a, c}, {b}]
     = {}
    >> Complement[f[z, y, x, w], f[x], f[x, z]]
     = f[w, y]
    >> Complement[{c, b, a}]
     = {a, b, c}

    #> Complement[a, b]
     : Non-atomic expression expected at position 1 in Complement[a, b].
     = Complement[a, b]
    #> Complement[f[a], g[b]]
     : Heads f and g at positions 1 and 2 are expected to be the same.
     = Complement[f[a], g[b]]
    #> Complement[{a, b, c}, {a, c}, SameTest->(True&)]
     = {}
    #> Complement[{a, b, c}, {a, c}, SameTest->(False&)]
     = {a, b, c}
    """

    summary_text = "find the complement with respect to a universal set"
    _operation = "difference"

    def _elementwise(self, a, b, sameQ: Callable[..., bool]):
        for ea in a:
            if not any(sameQ(eb, ea) for eb in b):
                yield ea


class DeleteDuplicates(_GatherOperation):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/DeleteDuplicates.html</url>

    <dl>
      <dt>'DeleteDuplicates[$list$]'
      <dd>deletes duplicates from $list$.

      <dt>'DeleteDuplicates[$list$, $test$]'
      <dd>deletes elements from $list$ based on whether the function $test$ yields \
          'True' on pairs of elements.

      'DeleteDuplicates' does not change the order of the remaining elements.
    </dl>

    >> DeleteDuplicates[{1, 7, 8, 4, 3, 4, 1, 9, 9, 2, 1}]
     = {1, 7, 8, 4, 3, 9, 2}

    >> DeleteDuplicates[{3,2,1,2,3,4}, Less]
     = {3, 2, 1}

    #> DeleteDuplicates[{3,2,1,2,3,4}, Greater]
     = {3, 3, 4}

    #> DeleteDuplicates[{}]
     = {}
    """

    summary_text = "delete duplicate elements in a list"
    _bin = _DeleteDuplicatesBin


class Gather(_GatherOperation):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Gather.html</url>

    <dl>
      <dt>'Gather[$list$, $test$]'
      <dd>gathers elements of $list$ into sub lists of items that are the same according to $test$.

      <dt>'Gather[$list$]'
      <dd>gathers elements of $list$ into sub lists of items that are the same.
    </dl>

    The order of the items inside the sub lists is the same as in the original list.

    >> Gather[{1, 7, 3, 7, 2, 3, 9}]
     = {{1}, {7, 7}, {3, 3}, {2}, {9}}

    >> Gather[{1/3, 2/6, 1/9}]
     = {{1 / 3, 1 / 3}, {1 / 9}}
    """

    summary_text = "gather sublists of identical elements"
    _bin = _GatherBin


class Flatten(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Flatten.html</url>

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

    def eval_list(self, expr, n, h, evaluation):
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

    def eval(self, expr, n, h, evaluation):
        "Flatten[expr_, n_, h_]"

        if n == Expression(SymbolDirectedInfinity, Integer1):
            n = -1  # a negative number indicates an unbounded level
        else:
            n_int = n.get_int_value()
            # Here we test for negative since in Mathics Flatten[] as opposed to flatten_with_respect_to_head()
            # negative numbers (and None) are not allowed.
            if n_int is None or n_int < 0:
                evaluation.message("Flatten", "flpi", n)
                return
            n = n_int

        return expr.flatten_with_respect_to_head(h, level=n)


class GatherBy(_GatherOperation):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/GatherBy.html</url>

    <dl>
      <dt>'GatherBy[$list$, $f$]'
      <dd>gathers elements of $list$ into sub lists of items whose image \
      under $f$ identical.

      <dt>'GatherBy[$list$, {$f$, $g$, ...}]'
      <dd>gathers elements of $list$ into sub lists of items whose image \
      under $f$ identical. Then, gathers these sub lists again into sub \
      sub lists, that are identical under $g.
    </dl>

    >> GatherBy[{{1, 3}, {2, 2}, {1, 1}}, Total]
     = {{{1, 3}, {2, 2}}, {{1, 1}}}

    >> GatherBy[{"xy", "abc", "ab"}, StringLength]
     = {{xy, ab}, {abc}}

    >> GatherBy[{{2, 0}, {1, 5}, {1, 0}}, Last]
     = {{{2, 0}, {1, 0}}, {{1, 5}}}

    >> GatherBy[{{1, 2}, {2, 1}, {3, 5}, {5, 1}, {2, 2, 2}}, {Total, Length}]
     = {{{{1, 2}, {2, 1}}}, {{{3, 5}}}, {{{5, 1}}, {{2, 2, 2}}}}
    """

    rules = {
        "GatherBy[l_]": "GatherBy[l, Identity]",
        "GatherBy[l_, {r__, f_}]": "Map[GatherBy[#, f]&, GatherBy[l, {r}], {Length[{r}]}]",
        "GatherBy[l_, {f_}]": "GatherBy[l, f]",
    }
    summary_text = "gather based on values of a function applied to elements"
    _bin = _GatherBin

    def eval(self, values, func, evaluation: Evaluation):
        "%(name)s[values_, func_]"

        if not self._check_list(values, func, evaluation):
            return

        keys = Expression(SymbolMap, func, values).evaluate(evaluation)
        if len(keys.elements) != len(values.elements):
            return

        return self._gather(keys, values, _FastEquivalence())


class Join(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Join.html</url>

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

    attributes = A_FLAT | A_ONE_IDENTITY | A_PROTECTED
    summary_text = "join lists together at any level"

    def eval(self, lists, evaluation: Evaluation):
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


class PadLeft(_Pad):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/PadLeft.html</url>

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
    <url>:WMA link:https://reference.wolfram.com/language/ref/PadRight.html</url>

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


class Partition(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Partition.html</url>

    <dl>
      <dt>'Partition[$list$, $n$]'
      <dd>partitions $list$ into sublists of length $n$.

      <dt>'Parition[$list$, $n$, $d$]'
      <dd>partitions $list$ into sublists of length $n$ which overlap $d$ \
          indices.
    </dl>

    >> Partition[{a, b, c, d, e, f}, 2]
     = {{a, b}, {c, d}, {e, f}}

    >> Partition[{a, b, c, d, e, f}, 3, 1]
     = {{a, b, c}, {b, c, d}, {c, d, e}, {d, e, f}}

    #> Partition[{a, b, c, d, e}, 2]
     = {{a, b}, {c, d}}
    """

    # TODO: Nested list length specifications
    """
    >> Partition[{{11, 12, 13}, {21, 22, 23}, {31, 32, 33}}, {2, 2}, 1]
     = {{{{11, 12}, {21, 22}}, {{12, 13}, {22, 23}}}, {{{21, 22}, {31, 32}}, {{22, 23}, {32, 33}}}}
    """
    summary_text = "partition a list into sublists of a given length"
    rules = {
        "Parition[list_, n_, d_, k]": "Partition[list, n, d, {k, k}]",
    }

    def _partition(self, expr, n, d, evaluation: Evaluation):
        assert n > 0 and d > 0

        inner = structure("List", expr, evaluation)
        outer = structure("List", inner, evaluation)

        make_slice = inner.slice

        def slices():
            elements = expr.elements
            for lower in range(0, len(elements), d):
                upper = lower + n

                chunk = elements[lower:upper]
                if len(chunk) != n:
                    continue

                yield make_slice(expr, slice(lower, upper))

        return outer(slices())

    def eval_no_overlap(self, li, n: Integer, evaluation: Evaluation):
        "Partition[li_List, n_Integer]"
        # TODO: Error checking
        return self._partition(li, n.get_int_value(), n.get_int_value(), evaluation)

    def eval(self, li, n: Integer, d: Integer, evaluation: Evaluation):
        "Partition[li_List, n_Integer, d_Integer]"
        # TODO: Error checking
        return self._partition(li, n.get_int_value(), d.get_int_value(), evaluation)


class Reverse(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Reverse.html</url>

    <dl>
      <dt>'Reverse[$expr$]'
      <dd>reverses the order of $expr$'s items (on the top level)

      <dt>'Reverse[$expr$, $n$]'
      <dd>reverses the order of items in $expr$ on level $n$

      <dt>'Reverse[$expr$, {$n1$, $n2$, ...}]'
      <dd>reverses the order of items in $expr$ on levels $n1$, $n2$, ...
    </dl>

    >> Reverse[{1, 2, 3}]
     = {3, 2, 1}
    >> Reverse[x[a, b, c]]
     = x[c, b, a]
    >> Reverse[{{1, 2}, {3, 4}}, 1]
     = {{3, 4}, {1, 2}}
    >> Reverse[{{1, 2}, {3, 4}}, 2]
     = {{2, 1}, {4, 3}}
    >> Reverse[{{1, 2}, {3, 4}}, {1, 2}]
     = {{4, 3}, {2, 1}}
    """

    summary_text = "reverse a list at any level"
    messages = {
        "ilsmp": "Positive integer or list of positive integers expected at position 2 of ``."
    }

    @staticmethod
    def _reverse(
        expr, level, levels, evaluation
    ):  # depth >= 1, levels are expected to be unique and sorted
        if not isinstance(expr, Expression):
            return expr

        if levels[0] == level:
            expr = expr.restructure(expr.head, reversed(expr.elements), evaluation)

            if len(levels) > 1:
                expr = expr.restructure(
                    expr.head,
                    [
                        Reverse._reverse(element, level + 1, levels[1:], evaluation)
                        for element in expr.elements
                    ],
                    evaluation,
                )
        else:
            expr = expr.restructure(
                expr.head,
                [
                    Reverse._reverse(element, level + 1, levels, evaluation)
                    for element in expr.elements
                ],
                evaluation,
            )

        return expr

    def eval_top_level(self, expr, evaluation: Evaluation):
        "Reverse[expr_]"
        return Reverse._reverse(expr, 1, (1,), evaluation)

    def eval(self, expr, levels, evaluation: Evaluation):
        "Reverse[expr_, levels_]"
        if isinstance(levels, Integer):
            py_levels = [levels.get_int_value()]
        elif levels.get_head_name() == "System`List":
            if not levels.elements:
                return expr
            if any(not isinstance(level, Integer) for level in levels.elements):
                py_levels = None
            else:
                py_levels = sorted(
                    list(set(level.get_int_value() for level in levels.elements))
                )
        else:
            py_levels = None
        if py_levels and py_levels[0] < 1:  # if py_level is not None, it's sorted
            py_levels = None
        if py_levels is None:
            evaluation.message(
                "Reverse", "ilsmp", Expression(SymbolReverse, expr, levels)
            )
        else:
            return Reverse._reverse(expr, 1, py_levels, evaluation)


def riffle_lists(items, seps):
    if len(seps) == 0:  # special case
        seps = [ListExpression()]

    i = 0
    while i < len(items):
        yield items[i]
        if i == len(items) - 1 and len(items) != len(seps):
            return
        yield seps[i % len(seps)]
        i += 1


class Riffle(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Riffle.html</url>

    <dl>
      <dt>'Riffle[$list$, $x$]'
      <dd>inserts a copy of $x$ between each element of $list$.

      <dt>'Riffle[{$a1$, $a2$, ...}, {$b1$, $b2$, ...}]'
      <dd>interelements the elements of both lists, returning '{$a1$, $b1$, $a2$, $b2$, ...}'.
    </dl>

    >> Riffle[{a, b, c}, x]
     = {a, x, b, x, c}
    >> Riffle[{a, b, c}, {x, y, z}]
     = {a, x, b, y, c, z}
    >> Riffle[{a, b, c, d, e, f}, {x, y, z}]
     = {a, x, b, y, c, z, d, x, e, y, f}

    #> Riffle[{1, 2, 3, 4}, {x, y, z, t}]
     = {1, x, 2, y, 3, z, 4, t}
    #> Riffle[{1, 2}, {1, 2, 3}]
     = {1, 1, 2}
    #> Riffle[{1, 2}, {1, 2}]
     = {1, 1, 2, 2}

    #> Riffle[{a,b,c}, {}]
     = {a, {}, b, {}, c}
    #> Riffle[{}, {}]
     = {}
    #> Riffle[{}, {a,b}]
     = {}
    """

    summary_text = "intersperse additional elements"

    def eval(self, list, sep, evaluation: Evaluation):
        "Riffle[list_List, sep_]"

        if sep.has_form("List", None):
            result = riffle_lists(list.elements, sep.elements)
        else:
            result = riffle_lists(list.elements, [sep])

        return list.restructure("List", result, evaluation, deps=(list, sep))


class RotateLeft(_Rotate):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/RotateLeft.html</url>

    <dl>
      <dt>'RotateLeft[$expr$]'
      <dd>rotates the items of $expr$' by one item to the left.

      <dt>'RotateLeft[$expr$, $n$]'
      <dd>rotates the items of $expr$' by $n$ items to the left.

      <dt>'RotateLeft[$expr$, {$n1$, $n2$, ...}]'
      <dd>rotates the items of $expr$' by $n1$ items to the left at \
          the first level, by $n2$ items to the left at the second level, and so on.
    </dl>

    >> RotateLeft[{1, 2, 3}]
     = {2, 3, 1}
    >> RotateLeft[Range[10], 3]
     = {4, 5, 6, 7, 8, 9, 10, 1, 2, 3}
    >> RotateLeft[x[a, b, c], 2]
     = x[c, a, b]
    >> RotateLeft[{{a, b, c}, {d, e, f}, {g, h, i}}, {1, 2}]
     = {{f, d, e}, {i, g, h}, {c, a, b}}
    """

    summary_text = "cyclically rotate lists to the left, at any depth"
    _sign = 1


class RotateRight(_Rotate):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/RotateRight.html</url>

    <dl>
      <dt>'RotateRight[$expr$]'
      <dd>rotates the items of $expr$' by one item to the right.

      <dt>'RotateRight[$expr$, $n$]'
      <dd>rotates the items of $expr$' by $n$ items to the right.

      <dt>'RotateRight[$expr$, {$n1$, $n2$, ...}]'
      <dd>rotates the items of $expr$' by $n1$ items to the right at the first level, by $n2$ items to the right at the second level, and so on.
    </dl>

    >> RotateRight[{1, 2, 3}]
     = {3, 1, 2}
    >> RotateRight[Range[10], 3]
     = {8, 9, 10, 1, 2, 3, 4, 5, 6, 7}
    >> RotateRight[x[a, b, c], 2]
     = x[b, c, a]
    >> RotateRight[{{a, b, c}, {d, e, f}, {g, h, i}}, {1, 2}]
     = {{h, i, g}, {b, c, a}, {e, f, d}}
    """

    summary_text = "cyclically rotate lists to the right, at any depth"
    _sign = -1


class Split(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Split.html</url>

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

    def eval(self, mlist, test, evaluation: Evaluation):
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
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SplitBy.html</url>

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

    def eval(self, mlist, func, evaluation: Evaluation):
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

    def eval_multiple(self, mlist, funcs, evaluation: Evaluation):
        "SplitBy[mlist_, funcs_List]"
        expr = Expression(SymbolSplit, mlist, funcs)

        if isinstance(mlist, Atom):
            evaluation.message("Select", "normal", 1, expr)
            return

        result = mlist
        for f in funcs.elements[::-1]:
            result = self.eval(result, f, evaluation)

        return result


class Tally(_GatherOperation):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Tally.html</url>

    <dl>
      <dt>'Tally[$list$]'
      <dd>counts and returns the number of occurrences of objects and returns \
          the result as a list of pairs {object, count}.

      <dt>'Tally[$list$, $test$]'
      <dd>counts the number of occurrences of objects and uses $test to \
          determine if two objects should be counted in the same bin.
    </dl>

    >> Tally[{a, b, c, b, a}]
     = {{a, 2}, {b, 2}, {c, 1}}

    Tally always returns items in the order as they first appear in $list$:
    >> Tally[{b, b, a, a, a, d, d, d, d, c}]
     = {{b, 2}, {a, 3}, {d, 4}, {c, 1}}
    """

    summary_text = "tally all distinct elements in a list"
    _bin = _TallyBin


class Union(_SetOperation):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Union.html</url>

    <dl>
      <dt>'Union[$a$, $b$, ...]'
      <dd>gives the union of the given set or sets. The resulting list \
          will be sorted and each element will only occur once.
    </dl>

    >> Union[{5, 1, 3, 7, 1, 8, 3}]
     = {1, 3, 5, 7, 8}

    >> Union[{a, b, c}, {c, d, e}]
     = {a, b, c, d, e}

    >> Union[{c, b, a}]
     = {a, b, c}

    >> Union[{{a, 1}, {b, 2}}, {{c, 1}, {d, 3}}, SameTest->(SameQ[Last[#1],Last[#2]]&)]
     = {{b, 2}, {c, 1}, {d, 3}}

    >> Union[{1, 2, 3}, {2, 3, 4}, SameTest->Less]
     = {1, 2, 2, 3, 4}

    #> Union[{1, -1, 2}, {-2, 3}, SameTest -> (Abs[#1] == Abs[#2] &)]
     = {-2, 1, 3}
    """

    summary_text = "enumerate all distinct elements in a list"
    _operation = "union"

    def _elementwise(self, a, b, sameQ: Callable[..., bool]):
        for eb in b:
            yield eb
        for ea in a:
            if not any(sameQ(eb, ea) for eb in b):
                yield ea


class Intersection(_SetOperation):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Intersection.html</url>

    <dl>
      <dt>'Intersection[$a$, $b$, ...]'
      <dd>gives the intersection of the sets. The resulting list \
      will be sorted and each element will only occur once.
    </dl>

    >> Intersection[{1000, 100, 10, 1}, {1, 5, 10, 15}]
     = {1, 10}

    >> Intersection[{{a, b}, {x, y}}, {{x, x}, {x, y}, {x, z}}]
     = {{x, y}}

    >> Intersection[{c, b, a}]
     = {a, b, c}

    >> Intersection[{1, 2, 3}, {2, 3, 4}, SameTest->Less]
     = {3}

    #> Intersection[{1, -1, -2, 2, -3}, {1, -2, 2, 3}, SameTest -> (Abs[#1] == Abs[#2] &)]
     = {-3, -2, 1}
    """

    summary_text = "enumerate common elements"
    _operation = "intersection"

    def _elementwise(self, a, b, sameQ: Callable[..., bool]):
        for ea in a:
            if any(sameQ(eb, ea) for eb in b):
                yield ea
