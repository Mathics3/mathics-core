# cython: language_level=3
# -*- coding: utf-8 -*-

import sympy
import math

import typing
from typing import Any, Optional
from itertools import chain
from bisect import bisect_left

from mathics.core.atoms import from_python, Number, Integer
from mathics.core.number import dps
from mathics.core.convert import sympy_symbol_prefix, SympyExpression
from mathics.core.symbols import (
    Atom,
    BaseExpression,
    Monomial,
    Symbol,
    SymbolList,
    SymbolN,
    SymbolSequence,
    system_symbols,
    ensure_context,
    strip_context,
)
from mathics.core.systemsymbols import SymbolSequence


SymbolAborted = Symbol("$Aborted")
SymbolAlternatives = Symbol("Alternatives")
SymbolBlank = Symbol("System`Blank")
SymbolBlankSequence = Symbol("System`BlankSequence")
SymbolBlankNullSequence = Symbol("System`BlankNullSequence")
SymbolCompile = Symbol("Compile")
SymbolCompiledFunction = Symbol("CompiledFunction")
SymbolCondition = Symbol("Condition")
SymbolDefault = Symbol("Default")
SymbolDirectedInfinity = Symbol("DirectedInfinity")
SymbolFunction = Symbol("Function")
SymbolOptional = Symbol("Optional")
SymbolOptionsPattern = Symbol("OptionsPattern")
SymbolPattern = Symbol("Pattern")
SymbolPatternTest = Symbol("PatternTest")
SymbolSlot = Symbol("Slot")
SymbolSlotSequence = Symbol("SlotSequence")
SymbolTimes = Symbol("Times")
SymbolVerbatim = Symbol("Verbatim")


symbols_arithmetic_operations = system_symbols(
    "Sqrt",
    "Times",
    "Plus",
    "Subtract",
    "Minus",
    "Power",
    "Abs",
    "Divide",
    "Sin",
)


class BoxError(Exception):
    def __init__(self, box, form) -> None:
        super().__init__("Box %s cannot be formatted as %s" % (box, form))
        self.box = box
        self.form = form


# ExpressionCache keeps track of the following attributes for one Expression instance:

# time: (1) the last time (in terms of Definitions.now) this expression was evaluated
#   or (2) None, if the current expression has not yet been evaluatec (i.e. is new or
#   changed).
# symbols: (1) a set of symbols occuring in this expression's head, its leaves'
#   heads, any of its sub expressions' heads or as Symbol leaves somewhere (maybe deep
#   down) in the expression tree start by this expressions' leaves, or (2) None, if no
#   information on which symbols are contained in this expression is available
# sequences: (1) a list of leaf indices that indicate the position of all Sequence
#   heads that are either in the leaf's head or any of the indicated leaf's sub
#   expressions' heads, or (2) None, if no information is available.


class ExpressionCache:
    def __init__(self, time=None, symbols=None, sequences=None, copy=None):
        if copy is not None:
            time = time or copy.time
            symbols = symbols or copy.symbols
            sequences = sequences or copy.sequences
        self.time = time
        self.symbols = symbols
        self.sequences = sequences

    def copy(self):
        return ExpressionCache(self.time, self.symbols, self.sequences)

    def sliced(self, lower, upper):
        # indicates that the Expression's leaves have been slices with
        # the given indices.

        seq = self.sequences

        if seq:
            a = bisect_left(seq, lower)  # all(val >= i for val in seq[a:])
            b = bisect_left(seq, upper)  # all(val >= j for val in seq[b:])
            new_sequences = tuple(x - lower for x in seq[a:b])
        elif seq is not None:
            new_sequences = tuple()
        else:
            new_sequences = None

        return ExpressionCache(self.time, self.symbols, new_sequences)

    def reordered(self):
        # indicates that the Expression's leaves have been reordered
        # or reduced (i.e. that the leaves have changed, but that
        # no new leaf instances were added).

        sequences = self.sequences

        # note that we keep sequences == [], since they are fine even
        # after having reordered leaves.
        if sequences:
            sequences = None

        return ExpressionCache(None, self.symbols, sequences)

    @staticmethod
    def union(expressions, evaluation):
        definitions = evaluation.definitions

        for expr in expressions:
            if expr.has_changed(definitions):
                return None

        symbols = set.union(*[expr._cache.symbols for expr in expressions])

        return ExpressionCache(
            definitions.now, symbols, None if "System`Sequence" in symbols else tuple()
        )


class Expression(BaseExpression):
    head: "Symbol"
    leaves: typing.List[Any]
    _sequences: Any

    def __new__(cls, head, *leaves, **kwargs) -> "Expression":
        self = super().__new__(cls)
        if isinstance(head, str):
            head = Symbol(head)
        self._head = head
        self._leaves = tuple(from_python(leaf) for leaf in leaves)
        self._sequences = None
        self._format_cache = None
        return self

    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, value):
        raise ValueError("Expression.head is write protected.")

    @property
    def leaves(self):
        return self._leaves

    @leaves.setter
    def leaves(self, value):
        raise ValueError("Expression.leaves is write protected.")

    def equal2(self, rhs: Any) -> Optional[bool]:
        """Mathics two-argument Equal (==)
        returns True if self and rhs are identical.
        """
        if self.sameQ(rhs):
            return True
        # if rhs is an Atom, return None
        elif isinstance(rhs, Atom):
            return None

        head = self._head
        # Here we only need to deal with Expressions.
        equal_heads = head.equal2(rhs._head)
        if not equal_heads:
            return equal_heads
        # From here, we can assume that both heads are the same
        if head in (SymbolList, SymbolSequence):
            if len(self._leaves) != len(rhs._leaves):
                return False
            for item1, item2 in zip(self._leaves, rhs._leaves):
                result = item1.equal2(item2)
                if not result:
                    return result
            return True
        elif head in (SymbolDirectedInfinity,):
            return self._leaves[0].equal2(rhs._leaves[0])
        return None

    def slice(self, head, py_slice, evaluation):
        # faster equivalent to: Expression(head, *self.leaves[py_slice])
        return structure(head, self, evaluation).slice(self, py_slice)

    def filter(self, head, cond, evaluation):
        # faster equivalent to: Expression(head, [leaf in self.leaves if cond(leaf)])
        return structure(head, self, evaluation).filter(self, cond)

    def restructure(self, head, leaves, evaluation, structure_cache=None, deps=None):
        # faster equivalent to: Expression(head, *leaves)

        # the caller guarantees that _all_ elements in leaves are either from
        # self.leaves (or its sub trees) or from one of the expression given
        # in the tuple "deps" (or its sub trees).

        # if this method is called repeatedly, and the caller guarantees
        # that no definitions change between subsequent calls, then heads_cache
        # may be passed an initially empty dict to speed up calls.

        if deps is None:
            deps = self
        s = structure(head, deps, evaluation, structure_cache=structure_cache)
        return s(list(leaves))

    def _no_symbol(self, symbol_name):
        # if this return True, it's safe to say that self.leaves or its
        # sub leaves contain no Symbol with symbol_name. if this returns
        # False, such a Symbol might or might not exist.

        cache = self._cache
        if cache is None:
            return False

        symbols = cache.symbols
        if symbols is not None and symbol_name not in symbols:
            return True
        else:
            return False

    def sequences(self):
        cache = self._cache
        if cache:
            seq = cache.sequences
            if seq is not None:
                return seq

        return self._rebuild_cache().sequences

    def _flatten_sequence(self, sequence, evaluation) -> "Expression":
        indices = self.sequences()
        if not indices:
            return self

        leaves = self._leaves

        flattened = []
        extend = flattened.extend

        k = 0
        for i in indices:
            extend(leaves[k:i])
            extend(sequence(leaves[i]))
            k = i + 1
        extend(leaves[k:])

        return self.restructure(self._head, flattened, evaluation)

    def flatten_sequence(self, evaluation):
        def sequence(leaf):
            if leaf.get_head_name() == "System`Sequence":
                return leaf._leaves
            else:
                return [leaf]

        return self._flatten_sequence(sequence, evaluation)

    def flatten_pattern_sequence(self, evaluation):
        def sequence(leaf):
            flattened = leaf.flatten_pattern_sequence(evaluation)
            if leaf.get_head() is SymbolSequence and leaf.pattern_sequence:
                return flattened._leaves
            else:
                return [flattened]

        expr = self._flatten_sequence(sequence, evaluation)
        if hasattr(self, "options"):
            expr.options = self.options
        return expr

    def _rebuild_cache(self):
        cache = self._cache

        if cache is None:
            time = None
        elif cache.symbols is None:
            time = cache.time
        elif cache.sequences is None:
            time = cache.time
        else:
            return cache

        sym = set((self.get_head_name(),))
        seq = []

        for i, leaf in enumerate(self._leaves):
            if isinstance(leaf, Expression):
                leaf_symbols = leaf._rebuild_cache().symbols
                sym.update(leaf_symbols)
                if "System`Sequence" in leaf_symbols:
                    seq.append(i)
            elif isinstance(leaf, Symbol):
                sym.add(leaf.get_name())

        cache = ExpressionCache(time, sym, seq)
        self._cache = cache
        return cache

    def has_changed(self, definitions):
        cache = self._cache

        if cache is None:
            return True

        time = cache.time

        if time is None:
            return True

        if cache.symbols is None:
            cache = self._rebuild_cache()

        return definitions.has_changed(time, cache.symbols)

    def _timestamp_cache(self, evaluation):
        self._cache = ExpressionCache(evaluation.definitions.now, copy=self._cache)

    def copy(self, reevaluate=False) -> "Expression":
        expr = Expression(self._head.copy(reevaluate))
        expr._leaves = tuple(leaf.copy(reevaluate) for leaf in self._leaves)
        if not reevaluate:
            # rebuilding the cache in self speeds up large operations, e.g.
            # First[Timing[Fold[#1+#2&, Range[750]]]]
            expr._cache = self._rebuild_cache()
        expr.options = self.options
        expr.original = self
        expr._sequences = self._sequences
        expr._format_cache = self._format_cache
        return expr

    def do_format(self, evaluation, form):
        if self._format_cache is None:
            self._format_cache = {}
        if isinstance(form, str):

            raise Exception("Expression.do_format\n", form, " should be a Symbol")
            form = Symbol(form)

        last_evaluated, expr = self._format_cache.get(form, (None, None))
        if last_evaluated is not None and expr is not None:
            symbolname = expr.get_name()
            if symbolname != "":
                if not evaluation.definitions.has_changed(
                    last_evaluated, (symbolname,)
                ):
                    return expr
        expr = super().do_format(evaluation, form)
        self._format_cache[form] = (evaluation.definitions.now, expr)
        return expr

    def shallow_copy(self) -> "Expression":
        # this is a minimal, shallow copy: head, leaves are shared with
        # the original, only the Expression instance is new.
        expr = Expression(self._head)
        expr._leaves = self._leaves
        # rebuilding the cache in self speeds up large operations, e.g.
        # First[Timing[Fold[#1+#2&, Range[750]]]]
        expr._cache = self._rebuild_cache()
        expr.options = self.options
        # expr.last_evaluated = self.last_evaluated
        return expr

    def get_head(self):
        return self._head

    def get_head_name(self):
        return self._head.name if isinstance(self._head, Symbol) else ""

    def set_head(self, head):
        self._head = head
        self._cache = None

    def get_leaves(self):
        return self._leaves

    def get_mutable_leaves(self):  # shallow, mutable copy of the leaves array
        return list(self._leaves)

    def set_leaf(self, index, value):  # leaves are removed, added or replaced
        leaves = list(self._leaves)
        leaves[index] = value
        self._leaves = tuple(leaves)
        self._cache = None

    def set_reordered_leaves(self, leaves):  # same leaves, but in a different order
        self._leaves = tuple(leaves)
        if self._cache:
            self._cache = self._cache.reordered()

    def get_attributes(self, definitions):
        if self.get_head() is SymbolFunction and len(self._leaves) > 2:
            res = self._leaves[2]
            if res.is_symbol():
                return (str(res),)
            elif res.has_form("List", None):
                return set(str(a) for a in res._leaves)
        return set()

    def get_lookup_name(self) -> bool:
        return self._head.get_lookup_name()

    def has_form(self, heads, *leaf_counts):
        """
        leaf_counts:
            (,):        no leaves allowed
            (None,):    no constraint on number of leaves
            (n, None):  leaf count >= n
            (n1, n2, ...):    leaf count in {n1, n2, ...}
        """

        head_name = self._head.get_name()
        if isinstance(heads, (tuple, list, set)):
            if head_name not in [ensure_context(h) for h in heads]:
                return False
        else:
            if head_name != ensure_context(heads):
                return False
        if not leaf_counts:
            return False
        if leaf_counts and leaf_counts[0] is not None:
            count = len(self._leaves)
            if count not in leaf_counts:
                if (
                    len(leaf_counts) == 2
                    and leaf_counts[1] is None  # noqa
                    and count >= leaf_counts[0]
                ):
                    return True
                else:
                    return False
        return True

    def has_symbol(self, symbol_name) -> bool:
        if self._no_symbol(symbol_name):
            return False
        return self._head.has_symbol(symbol_name) or any(
            leaf.has_symbol(symbol_name) for leaf in self._leaves
        )

    def _as_sympy_function(self, **kwargs) -> sympy.Function:
        sym_args = [leaf.to_sympy(**kwargs) for leaf in self.leaves]

        if None in sym_args:
            return None

        f = sympy.Function(str(sympy_symbol_prefix + self.get_head_name()))
        return f(*sym_args)

    def to_sympy(self, **kwargs):
        from mathics.builtin import mathics_to_sympy

        if "convert_all_global_functions" in kwargs:
            if len(self.leaves) > 0 and kwargs["convert_all_global_functions"]:
                if self.get_head_name().startswith("Global`"):
                    return self._as_sympy_function(**kwargs)

        if "converted_functions" in kwargs:
            functions = kwargs["converted_functions"]
            if len(self._leaves) > 0 and self.get_head_name() in functions:
                sym_args = [leaf.to_sympy() for leaf in self._leaves]
                if None in sym_args:
                    return None
                func = sympy.Function(str(sympy_symbol_prefix + self.get_head_name()))(
                    *sym_args
                )
                return func

        lookup_name = self.get_lookup_name()
        builtin = mathics_to_sympy.get(lookup_name)
        if builtin is not None:
            sympy_expr = builtin.to_sympy(self, **kwargs)
            if sympy_expr is not None:
                return sympy_expr

        return SympyExpression(self)

    def to_python(self, *args, **kwargs):
        """
        Convert the Expression to a Python object:
        List[...]  -> Python list
        DirectedInfinity[1] -> inf
        DirectedInfinity[-1] -> -inf
        True/False -> True/False
        Null       -> None
        Symbol     -> '...'
        String     -> '"..."'
        Function   -> python function
        numbers    -> Python number
        If kwarg n_evaluation is given, apply N first to the expression.
        """
        from mathics.builtin.base import mathics_to_python

        n_evaluation = kwargs.get("n_evaluation")
        head = self._head
        if n_evaluation is not None:
            if head is SymbolFunction:
                compiled = Expression(SymbolCompile, *(self._leaves))
                compiled = compiled.evaluate(n_evaluation)
                if compiled.get_head() is SymbolCompiledFunction:
                    return compiled.leaves[2].cfunc
            value = Expression(SymbolN, self).evaluate(n_evaluation)
            return value.to_python()

        if head is SymbolDirectedInfinity and len(self._leaves) == 1:
            direction = self._leaves[0].get_int_value()
            if direction == 1:
                return math.inf
            if direction == -1:
                return -math.inf
        elif head is SymbolList:
            return [leaf.to_python(*args, **kwargs) for leaf in self._leaves]

        head_name = head.get_name()
        if head_name in mathics_to_python:
            py_obj = mathics_to_python[head_name]
            # Start here
            # if inspect.isfunction(py_obj) or inspect.isbuiltin(py_obj):
            #     args = [leaf.to_python(*args, **kwargs) for leaf in self._leaves]
            #     return ast.Call(
            #         func=py_obj.__name__,
            #         args=args,
            #         keywords=[],
            #         )
            return py_obj
        return self

    def get_sort_key(self, pattern_sort=False):

        if pattern_sort:
            """
            Pattern sort key structure:
            0: 0/2:        Atom / Expression
            1: pattern:    0 / 11-31 for blanks / 1 for empty Alternatives /
                               40 for OptionsPattern
            2: 0/1:        0 for PatternTest
            3: 0/1:        0 for Pattern
            4: 0/1:        1 for Optional
            5: head / 0 for atoms
            6: leaves / 0 for atoms
            7: 0/1:        0 for Condition
            """

            head = self._head
            pattern = 0
            if head is SymbolBlank:
                pattern = 1
            elif head is SymbolBlankSequence:
                pattern = 2
            elif head is SymbolBlankNullSequence:
                pattern = 3
            if pattern > 0:
                if self._leaves:
                    pattern += 10
                else:
                    pattern += 20
            if pattern > 0:
                return [
                    2,
                    pattern,
                    1,
                    1,
                    0,
                    head.get_sort_key(True),
                    tuple(leaf.get_sort_key(True) for leaf in self._leaves),
                    1,
                ]

            if head is SymbolPatternTest:
                if len(self._leaves) != 2:
                    return [3, 0, 0, 0, 0, head, self._leaves, 1]
                sub = self._leaves[0].get_sort_key(True)
                sub[2] = 0
                return sub
            elif head is SymbolCondition:
                if len(self._leaves) != 2:
                    return [3, 0, 0, 0, 0, head, self._leaves, 1]
                sub = self._leaves[0].get_sort_key(True)
                sub[7] = 0
                return sub
            elif head is SymbolPattern:
                if len(self._leaves) != 2:
                    return [3, 0, 0, 0, 0, head, self._leaves, 1]
                sub = self._leaves[1].get_sort_key(True)
                sub[3] = 0
                return sub
            elif head is SymbolOptional:
                if len(self._leaves) not in (1, 2):
                    return [3, 0, 0, 0, 0, head, self._leaves, 1]
                sub = self._leaves[0].get_sort_key(True)
                sub[4] = 1
                return sub
            elif head is SymbolAlternatives:
                min_key = [4]
                min = None
                for leaf in self._leaves:
                    key = leaf.get_sort_key(True)
                    if key < min_key:
                        min = leaf
                        min_key = key
                if min is None:
                    # empty alternatives -> very restrictive pattern
                    return [2, 1]
                return min_key
            elif head is SymbolVerbatim:
                if len(self._leaves) != 1:
                    return [3, 0, 0, 0, 0, head, self._leaves, 1]
                return self._leaves[0].get_sort_key(True)
            elif head is SymbolOptionsPattern:
                return [2, 40, 0, 1, 1, 0, head, self._leaves, 1]
            else:
                # Append [4] to leaves so that longer expressions have higher
                # precedence
                return [
                    2,
                    0,
                    1,
                    1,
                    0,
                    head.get_sort_key(True),
                    tuple(
                        chain(
                            (leaf.get_sort_key(True) for leaf in self._leaves), ([4],)
                        )
                    ),
                    1,
                ]
        else:
            exps = {}
            head = self._head
            if head is SymbolTimes:
                for leaf in self._leaves:
                    name = leaf.get_name()
                    if leaf.has_form("Power", 2):
                        var = leaf._leaves[0].get_name()
                        exp = leaf._leaves[1].round_to_float()
                        if var and exp is not None:
                            exps[var] = exps.get(var, 0) + exp
                    elif name:
                        exps[name] = exps.get(name, 0) + 1
            elif self.has_form("Power", 2):
                var = self._leaves[0].get_name()
                exp = self._leaves[1].round_to_float()
                if var and exp is not None:
                    exps[var] = exps.get(var, 0) + exp
            if exps:
                return [
                    1 if self.is_numeric() else 2,
                    2,
                    Monomial(exps),
                    1,
                    head,
                    self._leaves,
                    1,
                ]
            else:
                return [1 if self.is_numeric() else 2, 3, head, self._leaves, 1]

    def sameQ(self, other: BaseExpression) -> bool:
        """Mathics SameQ"""
        if not isinstance(other, Expression):
            return False
        if self is other:
            return True
        if not self._head.sameQ(other.get_head()):
            return False
        if len(self._leaves) != len(other.get_leaves()):
            return False
        return all(
            (id(leaf) == id(oleaf) or leaf.sameQ(oleaf))
            for leaf, oleaf in zip(self._leaves, other.get_leaves())
        )

    def flatten(
        self, head, pattern_only=False, callback=None, level=None
    ) -> "Expression":
        if level is not None and level <= 0:
            return self
        if self._no_symbol(head.get_name()):
            return self
        sub_level = None if level is None else level - 1
        do_flatten = False
        for leaf in self._leaves:
            if leaf.get_head().sameQ(head) and (
                not pattern_only or leaf.pattern_sequence
            ):
                do_flatten = True
                break
        if do_flatten:
            new_leaves = []
            for leaf in self._leaves:
                if leaf.get_head().sameQ(head) and (
                    not pattern_only or leaf.pattern_sequence
                ):
                    new_leaf = leaf.flatten(
                        head, pattern_only, callback, level=sub_level
                    )
                    if callback is not None:
                        callback(new_leaf._leaves, leaf)
                    new_leaves.extend(new_leaf._leaves)
                else:
                    new_leaves.append(leaf)
            return Expression(self._head, *new_leaves)
        else:
            return self

    def evaluate(self, evaluation) -> typing.Union["Expression", "Symbol"]:
        from mathics.core.evaluation import ReturnInterrupt

        if evaluation.timeout:
            return

        expr = self
        reevaluate = True
        limit = None
        iteration = 1
        names = set()
        definitions = evaluation.definitions

        old_options = evaluation.options
        evaluation.inc_recursion_depth()
        if evaluation.definitions.show_steps:
            evaluation.print_out(
                "  " * evaluation.recursion_depth + "Evaluating: %s" % expr
            )
        try:
            while reevaluate:
                # changed before last evaluated?
                if not expr.has_changed(definitions):
                    break

                names.add(expr.get_lookup_name())

                if hasattr(expr, "options") and expr.options:
                    evaluation.options = expr.options

                expr, reevaluate = expr.evaluate_next(evaluation)
                if not reevaluate:
                    break
                if evaluation.definitions.show_steps:
                    evaluation.print_out(
                        "  " * evaluation.recursion_depth + "-> %s" % expr
                    )
                iteration += 1

                if limit is None:
                    limit = definitions.get_config_value("$IterationLimit")
                    if limit is None:
                        limit = "inf"
                if limit != "inf" and iteration > limit:
                    evaluation.error("$IterationLimit", "itlim", limit)
                    return SymbolAborted

        # "Return gets discarded only if it was called from within the r.h.s.
        # of a user-defined rule."
        # http://mathematica.stackexchange.com/questions/29353/how-does-return-work
        # Otherwise it propogates up.
        #
        except ReturnInterrupt as ret:
            if names.intersection(definitions.user.keys()):
                return ret.expr
            else:
                raise ret
        finally:
            evaluation.options = old_options
            evaluation.dec_recursion_depth()

        return expr

    def evaluate_next(self, evaluation) -> typing.Tuple["Expression", bool]:
        from mathics.builtin.base import BoxConstruct

        head = self._head.evaluate(evaluation)
        attributes = head.get_attributes(evaluation.definitions)
        leaves = self.get_mutable_leaves()

        def rest_range(indices):
            if "System`HoldAllComplete" not in attributes:
                if self._no_symbol("System`Evaluate"):
                    return
                for index in indices:
                    leaf = leaves[index]
                    if leaf.has_form("Evaluate", 1):
                        leaves[index] = leaf.evaluate(evaluation)

        def eval_range(indices):
            for index in indices:
                leaf = leaves[index]
                if not leaf.has_form("Unevaluated", 1):
                    leaf = leaf.evaluate(evaluation)
                    if leaf:
                        leaves[index] = leaf

        if "System`HoldAll" in attributes or "System`HoldAllComplete" in attributes:
            # eval_range(range(0, 0))
            rest_range(range(len(leaves)))
        elif "System`HoldFirst" in attributes:
            rest_range(range(0, min(1, len(leaves))))
            eval_range(range(1, len(leaves)))
        elif "System`HoldRest" in attributes:
            eval_range(range(0, min(1, len(leaves))))
            rest_range(range(1, len(leaves)))
        else:
            eval_range(range(len(leaves)))
            # rest_range(range(0, 0))

        new = Expression(head)
        new._leaves = tuple(leaves)

        if (
            "System`SequenceHold" not in attributes
            and "System`HoldAllComplete" not in attributes  # noqa
        ):
            new = new.flatten_sequence(evaluation)
            leaves = new._leaves

        for leaf in leaves:
            leaf.unevaluated = False

        if "System`HoldAllComplete" not in attributes:
            dirty_leaves = None

            for index, leaf in enumerate(leaves):
                if leaf.has_form("Unevaluated", 1):
                    if dirty_leaves is None:
                        dirty_leaves = list(leaves)
                    dirty_leaves[index] = leaf._leaves[0]
                    dirty_leaves[index].unevaluated = True

            if dirty_leaves:
                new = Expression(head)
                new._leaves = tuple(dirty_leaves)
                leaves = dirty_leaves

        def flatten_callback(new_leaves, old):
            for leaf in new_leaves:
                leaf.unevaluated = old.unevaluated

        if "System`Flat" in attributes:
            new = new.flatten(new._head, callback=flatten_callback)
        if "System`Orderless" in attributes:
            new.sort()

        new._timestamp_cache(evaluation)

        if "System`Listable" in attributes:
            done, threaded = new.thread(evaluation)
            if done:
                if threaded.sameQ(new):
                    new._timestamp_cache(evaluation)
                    return new, False
                else:
                    return threaded, True

        def rules():
            rules_names = set()
            if "System`HoldAllComplete" not in attributes:
                for leaf in leaves:
                    name = leaf.get_lookup_name()
                    if len(name) > 0:  # only lookup rules if this is a symbol
                        if name not in rules_names:
                            rules_names.add(name)
                            for rule in evaluation.definitions.get_upvalues(name):
                                yield rule
            lookup_name = new.get_lookup_name()
            if lookup_name == new.get_head_name():
                for rule in evaluation.definitions.get_downvalues(lookup_name):
                    yield rule
            else:
                for rule in evaluation.definitions.get_subvalues(lookup_name):
                    yield rule

        for rule in rules():
            result = rule.apply(new, evaluation, fully=False)
            if result is not None:
                if isinstance(result, BoxConstruct):
                    return result, False
                if result.sameQ(new):
                    new._timestamp_cache(evaluation)
                    return new, False
                else:
                    return result, True

        dirty_leaves = None

        # Expression did not change, re-apply Unevaluated
        for index, leaf in enumerate(new._leaves):
            if leaf.unevaluated:
                if dirty_leaves is None:
                    dirty_leaves = list(new._leaves)
                dirty_leaves[index] = Expression("Unevaluated", leaf)

        if dirty_leaves:
            new = Expression(head)
            new._leaves = tuple(dirty_leaves)

        new.unformatted = self.unformatted
        new._timestamp_cache(evaluation)
        return new, False

    def evaluate_leaves(self, evaluation) -> "Expression":
        leaves = [leaf.evaluate(evaluation) for leaf in self._leaves]
        head = self._head.evaluate_leaves(evaluation)
        return Expression(head, *leaves)

    def __str__(self) -> str:
        return "%s[%s]" % (
            self._head,
            ", ".join([leaf.__str__() for leaf in self._leaves]),
        )

    def __repr__(self) -> str:
        return "<Expression: %s>" % self

    def process_style_box(self, options):
        if self.has_form("StyleBox", 1, None):
            rules = self._leaves[1:]
            for rule in rules:
                if rule.has_form("Rule", 2):
                    name = rule._leaves[0].get_name()
                    value = rule._leaves[1]
                    if name == "System`ShowStringCharacters":
                        value = value.is_true()
                        options = options.copy()
                        options["show_string_characters"] = value
                    elif name == "System`ImageSizeMultipliers":
                        if value.has_form("List", 2):
                            m1 = value._leaves[0].round_to_float()
                            m2 = value._leaves[1].round_to_float()
                            if m1 is not None and m2 is not None:
                                options = options.copy()
                                options["image_size_multipliers"] = (m1, m2)
            return True, options
        else:
            return False, options

    def boxes_to_text(self, **options) -> str:
        is_style, options = self.process_style_box(options)
        if is_style:
            return self._leaves[0].boxes_to_text(**options)
        if self.has_form("RowBox", 1) and self._leaves[0].has_form(  # nopep8
            "List", None
        ):
            return "".join(
                [leaf.boxes_to_text(**options) for leaf in self._leaves[0]._leaves]
            )
        elif self.has_form("SuperscriptBox", 2):
            return "^".join([leaf.boxes_to_text(**options) for leaf in self._leaves])
        elif self.has_form("FractionBox", 2):
            return "/".join(
                [" ( " + leaf.boxes_to_text(**options) + " ) " for leaf in self._leaves]
            )
        else:
            raise BoxError(self, "text")

    def boxes_to_mathml(self, **options) -> str:
        is_style, options = self.process_style_box(options)
        if is_style:
            return self._leaves[0].boxes_to_mathml(**options)
        name = self._head.get_name()
        if (
            name == "System`RowBox"
            and len(self._leaves) == 1
            and self._leaves[0].get_head() is SymbolList  # nopep8
        ):
            result = []
            inside_row = options.get("inside_row")
            # inside_list = options.get('inside_list')
            options = options.copy()

            def is_list_interior(content):
                if content.has_form("List", None) and all(
                    leaf.get_string_value() == "," for leaf in content._leaves[1::2]
                ):
                    return True
                return False

            is_list_row = False
            if (
                len(self._leaves[0]._leaves) == 3
                and self._leaves[0]._leaves[0].get_string_value() == "{"  # nopep8
                and self._leaves[0]._leaves[2].get_string_value() == "}"
                and self._leaves[0]._leaves[1].has_form("RowBox", 1)
            ):
                content = self._leaves[0]._leaves[1]._leaves[0]
                if is_list_interior(content):
                    is_list_row = True

            if not inside_row and is_list_interior(self._leaves[0]):
                is_list_row = True

            if is_list_row:
                options["inside_list"] = True
            else:
                options["inside_row"] = True

            for leaf in self._leaves[0].get_leaves():
                result.append(leaf.boxes_to_mathml(**options))
            return "<mrow>%s</mrow>" % " ".join(result)
        else:
            options = options.copy()
            options["inside_row"] = True
            if name == "System`SuperscriptBox" and len(self._leaves) == 2:
                return "<msup>%s %s</msup>" % (
                    self._leaves[0].boxes_to_mathml(**options),
                    self._leaves[1].boxes_to_mathml(**options),
                )
            if name == "System`SubscriptBox" and len(self._leaves) == 2:
                return "<msub>%s %s</msub>" % (
                    self._leaves[0].boxes_to_mathml(**options),
                    self._leaves[1].boxes_to_mathml(**options),
                )
            if name == "System`SubsuperscriptBox" and len(self._leaves) == 3:
                return "<msubsup>%s %s %s</msubsup>" % (
                    self._leaves[0].boxes_to_mathml(**options),
                    self._leaves[1].boxes_to_mathml(**options),
                    self._leaves[2].boxes_to_mathml(**options),
                )
            elif name == "System`FractionBox" and len(self._leaves) == 2:
                return "<mfrac>%s %s</mfrac>" % (
                    self._leaves[0].boxes_to_mathml(**options),
                    self._leaves[1].boxes_to_mathml(**options),
                )
            elif name == "System`SqrtBox" and len(self._leaves) == 1:
                return "<msqrt>%s</msqrt>" % (
                    self._leaves[0].boxes_to_mathml(**options)
                )
            elif name == "System`GraphBox":
                return "<mi>%s</mi>" % (self._leaves[0].boxes_to_mathml(**options))
            else:
                raise BoxError(self, "xml")

    def boxes_to_tex(self, **options) -> str:
        def block(tex, only_subsup=False):
            if len(tex) == 1:
                return tex
            else:
                if not only_subsup or "_" in tex or "^" in tex:
                    return "{%s}" % tex
                else:
                    return tex

        is_style, options = self.process_style_box(options)
        if is_style:
            return self._leaves[0].boxes_to_tex(**options)
        name = self._head.get_name()
        if (
            name == "System`RowBox"
            and len(self._leaves) == 1
            and self._leaves[0].get_head_name() == "System`List"  # nopep8
        ):
            return "".join(
                [leaf.boxes_to_tex(**options) for leaf in self._leaves[0].get_leaves()]
            )
        elif name == "System`SuperscriptBox" and len(self._leaves) == 2:
            tex1 = self._leaves[0].boxes_to_tex(**options)
            sup_string = self._leaves[1].get_string_value()
            if sup_string == "\u2032":
                return "%s'" % tex1
            elif sup_string == "\u2032\u2032":
                return "%s''" % tex1
            else:
                return "%s^%s" % (
                    block(tex1, True),
                    block(self._leaves[1].boxes_to_tex(**options)),
                )
        elif name == "System`SubscriptBox" and len(self._leaves) == 2:
            return "%s_%s" % (
                block(self._leaves[0].boxes_to_tex(**options), True),
                block(self._leaves[1].boxes_to_tex(**options)),
            )
        elif name == "System`SubsuperscriptBox" and len(self._leaves) == 3:
            return "%s_%s^%s" % (
                block(self._leaves[0].boxes_to_tex(**options), True),
                block(self._leaves[1].boxes_to_tex(**options)),
                block(self._leaves[2].boxes_to_tex(**options)),
            )
        elif name == "System`FractionBox" and len(self._leaves) == 2:
            return "\\frac{%s}{%s}" % (
                self._leaves[0].boxes_to_tex(**options),
                self._leaves[1].boxes_to_tex(**options),
            )
        elif name == "System`SqrtBox" and len(self._leaves) == 1:
            return "\\sqrt{%s}" % self._leaves[0].boxes_to_tex(**options)
        else:
            raise BoxError(self, "tex")

    def default_format(self, evaluation, form) -> str:
        return "%s[%s]" % (
            self._head.default_format(evaluation, form),
            ", ".join([leaf.default_format(evaluation, form) for leaf in self._leaves]),
        )

    def sort(self, pattern=False):
        "Sort the leaves according to internal ordering."
        leaves = list(self._leaves)
        if pattern:
            leaves.sort(key=lambda e: e.get_sort_key(pattern_sort=True))
        else:
            leaves.sort()
        self.set_reordered_leaves(leaves)

    def filter_leaves(self, head_name):
        # TODO: should use sorting
        head_name = ensure_context(head_name)

        if self._no_symbol(head_name):
            return []
        else:
            return [leaf for leaf in self._leaves if leaf.get_head_name() == head_name]

    def apply_rules(self, rules, evaluation, level=0, options=None):
        """for rule in rules:
        result = rule.apply(self, evaluation, fully=False)
        if result is not None:
            return result"""

        # to be able to access it inside inner function
        new_applied = [False]

        def apply_leaf(leaf):
            new, sub_applied = leaf.apply_rules(rules, evaluation, level + 1, options)
            new_applied[0] = new_applied[0] or sub_applied
            return new

        def descend(expr):
            return Expression(expr._head, *[apply_leaf(leaf) for leaf in expr._leaves])

        if options is None:  # default ReplaceAll mode; replace breadth first
            result, applied = super().apply_rules(rules, evaluation, level, options)
            if applied:
                return result, True
            head, applied = self._head.apply_rules(rules, evaluation, level, options)
            new_applied[0] = applied
            return descend(Expression(head, *self._leaves)), new_applied[0]
        else:  # Replace mode; replace depth first
            expr = descend(self)
            expr, applied = super(Expression, expr).apply_rules(
                rules, evaluation, level, options
            )
            new_applied[0] = new_applied[0] or applied
            if not applied and options["heads"]:
                # heads in Replace are treated at the level of the arguments, i.e. level + 1
                head, applied = expr._head.apply_rules(
                    rules, evaluation, level + 1, options
                )
                new_applied[0] = new_applied[0] or applied
                expr = Expression(head, *expr._leaves)
            return expr, new_applied[0]

    def replace_vars(
        self, vars, options=None, in_scoping=True, in_function=True
    ) -> "Expression":
        from mathics.builtin.scoping import get_scoping_vars

        if not in_scoping:
            if (
                self._head.get_name()
                in ("System`Module", "System`Block", "System`With")
                and len(self._leaves) > 0
            ):  # nopep8

                scoping_vars = set(
                    name for name, new_def in get_scoping_vars(self._leaves[0])
                )
                """for var in new_vars:
                    if var in scoping_vars:
                        del new_vars[var]"""
                vars = {
                    var: value for var, value in vars.items() if var not in scoping_vars
                }

        leaves = self._leaves
        if in_function:
            if (
                self._head is SymbolFunction
                and len(self._leaves) > 1
                and (
                    self._leaves[0].has_form("List", None) or self._leaves[0].get_name()
                )
            ):
                if self._leaves[0].get_name():
                    func_params = [self._leaves[0].get_name()]
                else:
                    func_params = [leaf.get_name() for leaf in self._leaves[0]._leaves]
                if "" not in func_params:
                    body = self._leaves[1]
                    replacement = {name: Symbol(name + "$") for name in func_params}
                    func_params = [Symbol(name + "$") for name in func_params]
                    body = body.replace_vars(replacement, options, in_scoping)
                    leaves = chain(
                        [Expression(SymbolList, *func_params), body], self._leaves[2:]
                    )

        if not vars:  # might just be a symbol set via Set[] we looked up here
            return self.shallow_copy()

        return Expression(
            self._head.replace_vars(vars, options=options, in_scoping=in_scoping),
            *[
                leaf.replace_vars(vars, options=options, in_scoping=in_scoping)
                for leaf in leaves
            ]
        )

    def replace_slots(self, slots, evaluation):
        if self._head is SymbolSlot:
            if len(self._leaves) != 1:
                evaluation.message_args("Slot", len(self._leaves), 1)
            else:
                slot = self._leaves[0].get_int_value()
                if slot is None or slot < 0:
                    evaluation.message("Function", "slot", self._leaves[0])
                elif slot > len(slots) - 1:
                    evaluation.message("Function", "slotn", slot)
                else:
                    return slots[int(slot)]
        elif self._head is SymbolSlotSequence:
            if len(self._leaves) != 1:
                evaluation.message_args("SlotSequence", len(self._leaves), 1)
            else:
                slot = self._leaves[0].get_int_value()
                if slot is None or slot < 1:
                    evaluation.error("Function", "slot", self._leaves[0])
            return Expression(SymbolSequence, *slots[slot:])
        elif self._head is SymbolFunction and len(self._leaves) == 1:
            # do not replace Slots in nested Functions
            return self
        return Expression(
            self._head.replace_slots(slots, evaluation),
            *[leaf.replace_slots(slots, evaluation) for leaf in self._leaves]
        )

    def thread(self, evaluation, head=None) -> typing.Tuple[bool, "Expression"]:
        if head is None:
            head = SymbolList

        items = []
        dim = None
        for leaf in self._leaves:
            if leaf.get_head().sameQ(head):
                if dim is None:
                    dim = len(leaf._leaves)
                    items = [(items + [innerleaf]) for innerleaf in leaf._leaves]
                elif len(leaf._leaves) != dim:
                    evaluation.message("Thread", "tdlen")
                    return True, self
                else:
                    for index in range(dim):
                        items[index].append(leaf._leaves[index])
            else:
                if dim is None:
                    items.append(leaf)
                else:
                    for item in items:
                        item.append(leaf)
        if dim is None:
            return False, self
        else:
            leaves = [Expression(self._head, *item) for item in items]
            return True, Expression(head, *leaves)

    def is_numeric(self, evaluation=None) -> bool:
        if evaluation:
            if "System`NumericFunction" not in evaluation.definitions.get_attributes(
                self._head.get_name()
            ):
                return False
            for leaf in self._leaves:
                if not leaf.is_numeric(evaluation):
                    return False
            return True
            # return all(leaf.is_numeric(evaluation) for leaf in self._leaves)
        else:
            return self._head in symbols_arithmetic_operations and all(
                leaf.is_numeric() for leaf in self._leaves
            )

    def numerify(self, evaluation) -> "Expression":
        _prec = None
        for leaf in self._leaves:
            if leaf.is_inexact():
                leaf_prec = leaf.get_precision()
                if _prec is None or leaf_prec < _prec:
                    _prec = leaf_prec
        if _prec is not None:
            new_leaves = self.get_mutable_leaves()
            for index in range(len(new_leaves)):
                leaf = new_leaves[index]
                # Don't "numerify" numbers: they should be numerified
                # automatically by the processing function,
                # and we don't want to lose exactness in e.g. 1.0+I.
                if not isinstance(leaf, Number):
                    n_expr = Expression(SymbolN, leaf, Integer(dps(_prec)))
                    n_result = n_expr.evaluate(evaluation)
                    if isinstance(n_result, Number):
                        new_leaves[index] = n_result
            return Expression(self._head, *new_leaves)
        else:
            return self

    def get_atoms(self, include_heads=True):
        if include_heads:
            atoms = self._head.get_atoms()
        else:
            atoms = []
        for leaf in self._leaves:
            atoms.extend(leaf.get_atoms())
        return atoms

    def __hash__(self):
        return hash(("Expression", self._head) + tuple(self._leaves))

    def user_hash(self, update):
        update(("%s>%d>" % (self.get_head_name(), len(self._leaves))).encode("utf8"))
        for leaf in self._leaves:
            leaf.user_hash(update)

    def __getnewargs__(self):
        return (self._head, self._leaves)


def _create_expression(self, head, *leaves):
    return Expression(head, *leaves)


BaseExpression.create_expression = _create_expression


def get_default_value(name, evaluation, k=None, n=None):
    pos = []
    if k is not None:
        pos.append(k)
    if n is not None:
        pos.append(n)
    for pos_len in reversed(list(range(len(pos) + 1))):
        # Try patterns from specific to general
        defaultexpr = Expression(
            SymbolDefault, Symbol(name), *[Integer(index) for index in pos[:pos_len]]
        )
        result = evaluation.definitions.get_value(
            name, "System`DefaultValues", defaultexpr, evaluation
        )
        if result is not None:
            if result.sameQ(defaultexpr):
                result = result.evaluate(evaluation)
            return result
    return None


def print_parenthesizes(
    precedence, outer_precedence=None, parenthesize_when_equal=False
) -> bool:
    return outer_precedence is not None and (
        outer_precedence > precedence
        or (outer_precedence == precedence and parenthesize_when_equal)
    )


def _is_neutral_symbol(symbol_name, cache, evaluation):
    # a symbol is neutral if it does not invoke any rules, but is sure to make its Expression stay
    # the way it is (e.g. List[1, 2, 3] will always stay List[1, 2, 3], so long as nobody defines
    # a rule on this).

    if cache:
        r = cache.get(symbol_name)
        if r is not None:
            return r

    definitions = evaluation.definitions

    definition = definitions.get_definition(symbol_name, only_if_exists=True)
    if definition is None:
        r = True
    else:
        r = all(
            len(definition.get_values_list(x)) == 0
            for x in ("up", "sub", "down", "own")
        )

    if cache:
        cache[symbol_name] = r

    return r


def _is_neutral_head(head, cache, evaluation):
    if not isinstance(head, Symbol):
        return False

    return _is_neutral_symbol(head.get_name(), cache, evaluation)


# Structure helps implementations make the ExpressionCache not invalidate across simple commands
# such as Take[], Most[], etc. without this, constant reevaluation of lists happens, which results
# in quadratic runtimes for command like Fold[#1+#2&, Range[x]].

# A good performance test case for Structure: x = Range[50000]; First[Timing[Partition[x, 15, 1]]]


class Structure(object):
    def __call__(self, leaves):
        # create an Expression with the given list "leaves" as leaves.
        # NOTE: the caller guarantees that "leaves" only contains items that are from "origins".
        raise NotImplementedError

    def filter(self, expr, cond):
        # create an Expression with a subset of "expr".leaves (picked out by the filter "cond").
        # NOTE: the caller guarantees that "expr" is from "origins".
        raise NotImplementedError

    def slice(self, expr, py_slice):
        # create an Expression, using the given slice of "expr".leaves as leaves.
        # NOTE: the caller guarantees that "expr" is from "origins".
        raise NotImplementedError


# UnlinkedStructure produces Expressions that are not linked to "origins" in terms of cache.
# This produces the same thing as doing Expression(head, *leaves).


class UnlinkedStructure(Structure):
    def __init__(self, head):
        self._head = head
        self._cache = None

    def __call__(self, leaves):
        expr = Expression(self._head)
        expr._leaves = tuple(leaves)
        return expr

    def filter(self, expr, cond):
        return self([leaf for leaf in expr._leaves if cond(leaf)])

    def slice(self, expr, py_slice):
        leaves = expr._leaves
        lower, upper, step = py_slice.indices(len(leaves))
        if step != 1:
            raise ValueError("Structure.slice only supports slice steps of 1")
        return self(leaves[lower:upper])


# LinkedStructure produces Expressions that are linked to "origins" in terms of cache. This
# carries over information from the cache of the originating Expressions into the Expressions
# that are newly created.


class LinkedStructure(Structure):
    def __init__(self, head, cache):
        self._head = head
        self._cache = cache

    def __call__(self, leaves):
        expr = Expression(self._head)
        expr._leaves = tuple(leaves)
        expr._cache = self._cache.reordered()
        return expr

    def filter(self, expr, cond):
        return self([leaf for leaf in expr._leaves if cond(leaf)])

    def slice(self, expr, py_slice):
        leaves = expr._leaves
        lower, upper, step = py_slice.indices(len(leaves))
        if step != 1:
            raise ValueError("Structure.slice only supports slice steps of 1")

        new = Expression(self._head)
        new._leaves = tuple(leaves[lower:upper])
        if expr._cache:
            new._cache = expr._cache.sliced(lower, upper)

        return new


def structure(head, origins, evaluation, structure_cache=None):
    # creates a Structure for building Expressions with head "head" and leaves
    # originating (exlusively) from "origins" (leaves are passed into the functions
    # of Structure further down).

    # "origins" may either be an Expression (i.e. all leaves must originate from that
    # expression), a Structure (all leaves passed in this "self" Structure must be
    # manufactured using that Structure), or a list of Expressions (i.e. all leaves
    # must originate from one of the listed Expressions).

    if isinstance(head, (str,)):
        head = Symbol(head)

    if isinstance(origins, (Expression, Structure)):
        cache = origins._cache
        if cache is not None and not _is_neutral_head(
            head, structure_cache, evaluation
        ):
            cache = None
    elif isinstance(origins, (list, tuple)):
        if _is_neutral_head(head, structure_cache, evaluation):
            cache = ExpressionCache.union(origins, evaluation)
        else:
            cache = None
    else:
        raise ValueError("expected Expression, Structure, tuple or list as orig param")

    if cache is None:
        return UnlinkedStructure(head)
    else:
        return LinkedStructure(head, cache)


def atom_list_constructor(evaluation, head, *atom_names):
    # if we encounter an Expression that consists wholly of atoms and those atoms (and the
    # expression's head) have no rules associated with them, we can speed up evaluation.

    # note that you may use a constructor constructed via atom_list_constructor() only as
    # long as the evaluation's Definitions are guaranteed to not change.

    if not _is_neutral_head(head, None, evaluation) or any(
        not atom for atom in atom_names
    ):
        optimize = False
    else:
        full_atom_names = [ensure_context(atom) for atom in atom_names]

        if not all(
            _is_neutral_symbol(atom, None, evaluation) for atom in full_atom_names
        ):
            optimize = False
        else:
            optimize = True

    if optimize:

        def construct(leaves):
            expr = Expression(head)
            expr._leaves = list(leaves)
            sym = set(chain([head.get_name()], full_atom_names))
            expr._cache = ExpressionCache(evaluation.definitions.now, sym, None)
            return expr

    else:

        def construct(leaves):
            expr = Expression(head)
            expr._leaves = list(leaves)
            return expr

    return construct


def string_list(head, leaves, evaluation):
    return atom_list_constructor(evaluation, head, "String")(leaves)
