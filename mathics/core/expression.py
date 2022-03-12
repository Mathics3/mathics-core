# cython: language_level=3
# -*- coding: utf-8 -*-

import sympy
import math
import time

import typing
from typing import Any, Optional
from itertools import chain
from bisect import bisect_left

from mathics.core.atoms import from_python, Number, Integer
from mathics.core.convert import sympy_symbol_prefix, SympyExpression
from mathics.core.element import ensure_context
from mathics.core.evaluation import Evaluation
from mathics.core.interrupt import ReturnInterrupt
from mathics.core.number import dps
from mathics.core.symbols import (
    Atom,
    BaseElement,
    Monomial,
    NumericOperators,
    Symbol,
    SymbolList,
    SymbolN,
    system_symbols,
)
from mathics.core.systemsymbols import SymbolSequence

from mathics.core.attributes import (
    flat,
    hold_all,
    hold_all_complete,
    hold_first,
    hold_rest,
    listable,
    nothing,
    numeric_function,
    orderless,
    sequence_hold,
)


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
#   or (2) None, if the current expression has not yet been evaluated (i.e. is new or
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
    def union(expressions, evaluation) -> Optional["ExpressionCache"]:
        definitions = evaluation.definitions

        for expr in expressions:
            if not hasattr(expr, "_cache") or expr.is_uncertain_final_definitions(
                definitions
            ):
                return None

        # FIXME: this is workaround the current situtation that some
        # Atoms, like String, have a cache even though they don't need
        # it, by virtue of this getting set up in
        # BaseElement.__init__. Removing the self._cache in there the
        # causes Boxing to mess up. Untangle this mess.
        if expr._cache is None:
            return None

        symbols = set.union(*[expr._cache.symbols for expr in expressions])

        return ExpressionCache(
            definitions.now, symbols, None if "System`Sequence" in symbols else tuple()
        )


class Expression(BaseElement, NumericOperators):
    head: "Symbol"
    leaves: typing.List[Any]
    _sequences: Any

    # __new__ seems to be used because BaseElement does some
    # questionable stuff using new.
    # See if there's a way to get rid of this, or ensure that this isn't causing
    # a garbage collection problem.
    def __new__(cls, head, *leaves, **kwargs) -> "Expression":
        self = super().__new__(cls)
        if isinstance(head, str):
            head = Symbol(head)
        self._head = head
        self._elements = tuple(from_python(element) for element in leaves)
        self._sequences = None
        # comment @mmatera: this cache should be useful in BoxConstruct, but not
        # here...
        self._format_cache = None
        return self

    def __getnewargs__(self):
        return (self._head, self._elements)

    def __hash__(self):
        return hash(("Expression", self._head) + tuple(self._elements))

    def __repr__(self) -> str:
        return "<Expression: %s>" % self

    def __str__(self) -> str:
        return "%s[%s]" % (
            self._head,
            ", ".join([element.__str__() for element in self._elements]),
        )

    def _as_sympy_function(self, **kwargs) -> sympy.Function:
        sym_args = [leaf.to_sympy(**kwargs) for leaf in self.leaves]

        if None in sym_args:
            return None

        f = sympy.Function(str(sympy_symbol_prefix + self.get_head_name()))
        return f(*sym_args)

    def _flatten_sequence(self, sequence, evaluation) -> "Expression":
        indices = self.sequences()
        if not indices:
            return self

        elements = self._elements

        flattened = []
        extend = flattened.extend

        k = 0
        for i in indices:
            extend(elements[k:i])
            extend(sequence(elements[i]))
            k = i + 1
        extend(elements[k:])

        return self.restructure(self._head, flattened, evaluation)

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

        for i, element in enumerate(self._elements):
            if isinstance(element, Expression):
                element_symbols = element._rebuild_cache().symbols
                sym.update(element_symbols)
                if "System`Sequence" in element_symbols:
                    seq.append(i)
            elif isinstance(element, Symbol):
                sym.add(element.get_name())

        cache = ExpressionCache(time, sym, seq)
        self._cache = cache
        return cache

    def _timestamp_cache(self, evaluation):
        self._cache = ExpressionCache(evaluation.definitions.now, copy=self._cache)

    # comment @mmatera: I think that the methods ``boxes_to_`` does not belong
    # here but to a specialized class for holding ``Box*`` expressions.
    # Box expressions shouldn't be evaluated, because are a kind of Literal, describing
    # a way in which certain expression should be shown.
    # In this PR (#181) I propose a basic implementation of a ``BoxExpression`` class.
    # ``BoxExpression``  shouldn't implement many of the methods related to ``evaluation``
    # and rewritting. Also, BoxExpressions must be build just from other ``BoxExpression``,
    # ``String`` and ``Lists``.

    def boxes_to_text(self, **options) -> str:
        """
        From a Boxed expression, produces a text representation.
        """
        # Idea @mmatera: All the Boxes expressions should be implemented as a different class
        # which implements these ``boxes_to_*`` methods.

        is_style, options = self.process_style_box(options)
        if is_style:
            return self._elements[0].boxes_to_text(**options)
        if self.has_form("RowBox", 1) and self._elements[0].has_form(  # nopep8
            "List", None
        ):
            return "".join(
                [
                    element.boxes_to_text(**options)
                    for element in self._elements[0]._elements
                ]
            )
        elif self.has_form("SuperscriptBox", 2):
            return "^".join(
                [element.boxes_to_text(**options) for element in self._elements]
            )
        elif self.has_form("FractionBox", 2):
            return "/".join(
                [
                    " ( " + element.boxes_to_text(**options) + " ) "
                    for element in self._elements
                ]
            )
        else:
            raise BoxError(self, "text")

    def boxes_to_mathml(self, **options) -> str:
        is_style, options = self.process_style_box(options)
        if is_style:
            return self._elements[0].boxes_to_mathml(**options)
        name = self._head.get_name()
        if (
            name == "System`RowBox"
            and len(self._elements) == 1
            and self._elements[0].get_head() is SymbolList  # nopep8
        ):
            result = []
            inside_row = options.get("inside_row")
            # inside_list = options.get('inside_list')
            options = options.copy()

            def is_list_interior(content):
                if content.has_form("List", None) and all(
                    element.get_string_value() == ","
                    for element in content._elements[1::2]
                ):
                    return True
                return False

            is_list_row = False
            if (
                len(self._elements[0]._elements) == 3
                and self._elements[0]._elements[0].get_string_value() == "{"  # nopep8
                and self._elements[0]._elements[2].get_string_value() == "}"
                and self._elements[0]._elements[1].has_form("RowBox", 1)
            ):
                content = self._elements[0]._elements[1]._elements[0]
                if is_list_interior(content):
                    is_list_row = True

            if not inside_row and is_list_interior(self._elements[0]):
                is_list_row = True

            if is_list_row:
                options["inside_list"] = True
            else:
                options["inside_row"] = True

            for element in self._elements[0].get_elements():
                result.append(element.boxes_to_mathml(**options))
            return "<mrow>%s</mrow>" % " ".join(result)
        else:
            options = options.copy()
            options["inside_row"] = True
            if name == "System`SuperscriptBox" and len(self._elements) == 2:
                return "<msup>%s %s</msup>" % (
                    self._elements[0].boxes_to_mathml(**options),
                    self._elements[1].boxes_to_mathml(**options),
                )
            if name == "System`SubscriptBox" and len(self._elements) == 2:
                return "<msub>%s %s</msub>" % (
                    self._elements[0].boxes_to_mathml(**options),
                    self._elements[1].boxes_to_mathml(**options),
                )
            if name == "System`SubsuperscriptBox" and len(self._elements) == 3:
                return "<msubsup>%s %s %s</msubsup>" % (
                    self._elements[0].boxes_to_mathml(**options),
                    self._elements[1].boxes_to_mathml(**options),
                    self._elements[2].boxes_to_mathml(**options),
                )
            elif name == "System`FractionBox" and len(self._elements) == 2:
                return "<mfrac>%s %s</mfrac>" % (
                    self._elements[0].boxes_to_mathml(**options),
                    self._elements[1].boxes_to_mathml(**options),
                )
            elif name == "System`SqrtBox" and len(self._elements) == 1:
                return "<msqrt>%s</msqrt>" % (
                    self._elements[0].boxes_to_mathml(**options)
                )
            elif name == "System`GraphBox":
                return "<mi>%s</mi>" % (self._elements[0].boxes_to_mathml(**options))
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
            return self._elements[0].boxes_to_tex(**options)
        name = self._head.get_name()
        if (
            name == "System`RowBox"
            and len(self._elements) == 1
            and self._elements[0].get_head_name() == "System`List"  # nopep8
        ):
            return "".join(
                [
                    element.boxes_to_tex(**options)
                    for element in self._elements[0].get_elements()
                ]
            )
        elif name == "System`SuperscriptBox" and len(self._elements) == 2:
            tex1 = self._elements[0].boxes_to_tex(**options)
            sup_string = self._elements[1].get_string_value()
            if sup_string == "\u2032":
                return "%s'" % tex1
            elif sup_string == "\u2032\u2032":
                return "%s''" % tex1
            else:
                return "%s^%s" % (
                    block(tex1, True),
                    block(self._elements[1].boxes_to_tex(**options)),
                )
        elif name == "System`SubscriptBox" and len(self._elements) == 2:
            return "%s_%s" % (
                block(self._elements[0].boxes_to_tex(**options), True),
                block(self._elements[1].boxes_to_tex(**options)),
            )
        elif name == "System`SubsuperscriptBox" and len(self._elements) == 3:
            return "%s_%s^%s" % (
                block(self._elements[0].boxes_to_tex(**options), True),
                block(self._elements[1].boxes_to_tex(**options)),
                block(self._elements[2].boxes_to_tex(**options)),
            )
        elif name == "System`FractionBox" and len(self._elements) == 2:
            return "\\frac{%s}{%s}" % (
                self._elements[0].boxes_to_tex(**options),
                self._elements[1].boxes_to_tex(**options),
            )
        elif name == "System`SqrtBox" and len(self._elements) == 1:
            return "\\sqrt{%s}" % self._elements[0].boxes_to_tex(**options)
        else:
            raise BoxError(self, "tex")

    def clear_cache(self):
        self._cache = None

    def copy(self, reevaluate=False) -> "Expression":
        expr = Expression(self._head.copy(reevaluate))
        expr._elements = tuple(element.copy(reevaluate) for element in self._elements)
        if not reevaluate:
            # rebuilding the cache in self speeds up large operations, e.g.
            # First[Timing[Fold[#1+#2&, Range[750]]]]
            expr._cache = self._rebuild_cache()
        expr.options = self.options
        expr.original = self
        expr._sequences = self._sequences
        expr._format_cache = self._format_cache
        return expr

    def default_format(self, evaluation, form) -> str:
        return "%s[%s]" % (
            self._head.default_format(evaluation, form),
            ", ".join(
                [element.default_format(evaluation, form) for element in self._elements]
            ),
        )

    def do_format(self, evaluation, form):
        if self._format_cache is None:
            self._format_cache = {}
        if isinstance(form, str):

            raise Exception("Expression.do_format\n", form, " should be a Symbol")
            form = Symbol(form)

        last_evaluated_time, expr = self._format_cache.get(form, (None, None))
        if last_evaluated_time is not None and expr is not None:
            symbolname = expr.get_name()
            if symbolname != "":
                if not evaluation.definitions.is_uncertain_final_value(
                    last_evaluated_time, set((symbolname,))
                ):
                    return expr
        expr = super().do_format(evaluation, form)
        self._format_cache[form] = (evaluation.definitions.now, expr)
        return expr

    @property
    def elements(self):
        return self._elements

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
            if len(self._elements) != len(rhs._elements):
                return False
            for item1, item2 in zip(self._elements, rhs._elements):
                result = item1.equal2(item2)
                if not result:
                    return result
            return True
        elif head in (SymbolDirectedInfinity,):
            return self._elements[0].equal2(rhs._elements[0])
        return None

    # Note that the return type is some subclass of BaseElement, it could be
    # a Real, an Expression, etc. It probably will *not* be a BaseElement since
    # the point of evaluation when there is not an error is to produce a concrete result.
    def evaluate(
        self,
        evaluation: Evaluation,
    ) -> typing.Type["BaseElement"]:
        """Apply transformation rules and expression evaluation to `evaluation` via
        `rewrite_apply_eval_step()` until it tells us to stop or we hit some limit.

        Note that this is a recusive process and
        `rewrite_apply_eval_step()` may call us recursively.

        Limits are either an evaluation iteration count or a timeout value.

        """
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
        if evaluation.definitions.trace_evaluation:
            if evaluation.definitions.timing_trace_evaluation:
                evaluation.print_out(time.time() - evaluation.start_time)
            evaluation.print_out(
                "  " * evaluation.recursion_depth + "Evaluating: %s" % expr
            )
        try:
            # Evaluation loop:
            while reevaluate:
                # changed before last evaluated?
                # This prevents to reevaluate expressions that
                # have been already evaluated. This uses Expression._cache
                if not expr.is_uncertain_final_definitions(definitions):
                    break

                # Here the names of the lookupname of the expression
                # are stored. This is necesary for the implementation
                # of the builtin `Return[]`
                names.add(expr.get_lookup_name())

                # This loads the default options associated
                # to the expression
                if hasattr(expr, "options") and expr.options:
                    evaluation.options = expr.options

                # This calls evaluate_next. This routine implements a single
                # step in the evaluation, and determines if a fixed point
                # was reached (reevaluate->False).
                # Notice that evaluate_next calls ``evaluate``
                # for the other ``BaseElement`` subclasses.
                expr, reevaluate = expr.rewrite_apply_eval_step(evaluation)

                if not reevaluate:
                    break

                # Trace evaluation...
                if evaluation.definitions.trace_evaluation:
                    evaluation.print_out(
                        "  " * evaluation.recursion_depth + "-> %s" % expr
                    )
                iteration += 1
                # Check if the iterationlimit was reached.
                # we need to check on each step, in case that the expression
                # changes its value. Maybe there is another way, for example,
                # keeping the index in the Evaluation object.
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
            # Restores the state
            evaluation.options = old_options
            evaluation.dec_recursion_depth()

        return expr

    def evaluate_elements(self, evaluation) -> "Expression":
        elements = [element.evaluate(evaluation) for element in self._elements]
        head = self._head.evaluate_elements(evaluation)
        return Expression(head, *elements)

    def filter(self, head, cond, evaluation):
        # faster equivalent to: Expression(head, [element in self.leaves if cond(element)])
        return structure(head, self, evaluation).filter(self, cond)

    def flatten(
        self, head, pattern_only=False, callback=None, level=None
    ) -> "Expression":
        """
        Flatten elements in nested expressions

        head: head of the leaves to be flatten
        callback:  a callback function called each time a element is flattened.
        level:   maximum deep to flatten
        pattern_only: if True, just apply to elements that are pattern_sequence (see ExpressionPattern.get_wrappings)

        For example if head=G,
        F[G[a,G[s,y],t],...]->F[G[a,s,y,t],...]

        """
        if level is not None and level <= 0:
            return self
        if self._no_symbol(head.get_name()):
            return self
        sub_level = None if level is None else level - 1
        do_flatten = False
        for element in self._elements:
            if element.get_head().sameQ(head) and (
                not pattern_only or element.pattern_sequence
            ):
                do_flatten = True
                break
        if do_flatten:
            new_elements = []
            for element in self._elements:
                if element.get_head().sameQ(head) and (
                    not pattern_only or element.pattern_sequence
                ):
                    new_element = element.flatten(
                        head, pattern_only, callback, level=sub_level
                    )
                    if callback is not None:
                        callback(new_element._elements, element)
                    new_elements.extend(new_element._elements)
                else:
                    new_elements.append(element)
            return Expression(self._head, *new_elements)
        else:
            return self

    def flatten_pattern_sequence(self, evaluation):
        def sequence(element):
            flattened = element.flatten_pattern_sequence(evaluation)
            if element.get_head() is SymbolSequence and element.pattern_sequence:
                return flattened._elements
            else:
                return [flattened]

        expr = self._flatten_sequence(sequence, evaluation)
        if hasattr(self, "options"):
            expr.options = self.options
        return expr

    def flatten_sequence(self, evaluation):
        def sequence(element):
            if element.get_head_name() == "System`Sequence":
                return element._elements
            else:
                return [element]

        return self._flatten_sequence(sequence, evaluation)

    def get_atoms(self, include_heads=True):
        """Returns a list of atoms involved in the expression."""
        # Comment @mmatera: maybe, what we really want here are the Symbol's
        # involved in the expression, not the atoms.
        if include_heads:
            atoms = self._head.get_atoms()
        else:
            atoms = []
        for element in self._elements:
            atoms.extend(element.get_atoms())
        return atoms

    def get_attributes(self, definitions):
        if self._head is SymbolFunction and len(self._elements) > 2:
            res = self._elements[2]
            if isinstance(res, Symbol):
                return (str(res),)
            elif res.has_form("List", None):
                return set(str(a) for a in res._elements)
        return nothing

    def get_elements(self):
        return self._elements

    # Compatibily with old code. Deprecated, but remove after a little bit
    get_leaves = get_elements

    def get_head(self):
        return self._head

    def get_head_name(self):
        return self._head.name if isinstance(self._head, Symbol) else ""

    def get_lookup_name(self) -> bool:
        lookup_symbol = self._head
        while True:
            if isinstance(lookup_symbol, Symbol):
                return lookup_symbol.name
            if isinstance(lookup_symbol, Atom):
                return lookup_symbol.get_head().name
            lookup_symbol = lookup_symbol._head

    def get_mutable_elements(self) -> list:
        """
        Return a shallow mutable copy of the elements
        """
        return list(self._elements)

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
                if self._elements:
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
                    tuple(element.get_sort_key(True) for element in self._elements),
                    1,
                ]

            if head is SymbolPatternTest:
                if len(self._elements) != 2:
                    return [3, 0, 0, 0, 0, head, self._elements, 1]
                sub = self._elements[0].get_sort_key(True)
                sub[2] = 0
                return sub
            elif head is SymbolCondition:
                if len(self._elements) != 2:
                    return [3, 0, 0, 0, 0, head, self._elements, 1]
                sub = self._elements[0].get_sort_key(True)
                sub[7] = 0
                return sub
            elif head is SymbolPattern:
                if len(self._elements) != 2:
                    return [3, 0, 0, 0, 0, head, self._elements, 1]
                sub = self._elements[1].get_sort_key(True)
                sub[3] = 0
                return sub
            elif head is SymbolOptional:
                if len(self._elements) not in (1, 2):
                    return [3, 0, 0, 0, 0, head, self._elements, 1]
                sub = self._elements[0].get_sort_key(True)
                sub[4] = 1
                return sub
            elif head is SymbolAlternatives:
                min_key = [4]
                min = None
                for element in self._elements:
                    key = element.get_sort_key(True)
                    if key < min_key:
                        min = element
                        min_key = key
                if min is None:
                    # empty alternatives -> very restrictive pattern
                    return [2, 1]
                return min_key
            elif head is SymbolVerbatim:
                if len(self._elements) != 1:
                    return [3, 0, 0, 0, 0, head, self._elements, 1]
                return self._elements[0].get_sort_key(True)
            elif head is SymbolOptionsPattern:
                return [2, 40, 0, 1, 1, 0, head, self._elements, 1]
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
                            (element.get_sort_key(True) for element in self._elements),
                            ([4],),
                        )
                    ),
                    1,
                ]
        else:
            exps = {}
            head = self._head
            if head is SymbolTimes:
                for element in self._elements:
                    name = element.get_name()
                    if element.has_form("Power", 2):
                        var = element._elements[0].get_name()
                        exp = element._elements[1].round_to_float()
                        if var and exp is not None:
                            exps[var] = exps.get(var, 0) + exp
                    elif name:
                        exps[name] = exps.get(name, 0) + 1
            elif self.has_form("Power", 2):
                var = self._elements[0].get_name()
                exp = self._elements[1].round_to_float()
                if var and exp is not None:
                    exps[var] = exps.get(var, 0) + exp
            if exps:
                return [
                    1 if self.is_numeric() else 2,
                    2,
                    Monomial(exps),
                    1,
                    head,
                    self._elements,
                    1,
                ]
            else:
                return [1 if self.is_numeric() else 2, 3, head, self._elements, 1]

    def is_uncertain_final_definitions(self, definitions) -> bool:
        """
        Used in Expression.evaluate() to determine if we need to reevaluate
        an expression.
        """

        # Some Atoms just don't have a cache.
        if not hasattr(self, "_cache"):
            return False

        cache = self._cache

        # FIXME: why do we return True when no cache is found? Explain.
        if cache is None:
            return True

        time = cache.time

        if time is None:
            return True

        if cache.symbols is None:
            cache = self._rebuild_cache()

        return definitions.is_uncertain_final_value(time, cache.symbols)

    def has_form(self, heads, *element_counts):
        """
        element_counts:
            (,):        no elements allowed
            (None,):    no constraint on number of elements
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
        if not element_counts:
            return False
        if element_counts and element_counts[0] is not None:
            count = len(self._elements)
            if count not in element_counts:
                if (
                    len(element_counts) == 2
                    and element_counts[1] is None  # noqa
                    and count >= element_counts[0]
                ):
                    return True
                else:
                    return False
        return True

    def has_symbol(self, symbol_name) -> bool:
        if self._no_symbol(symbol_name):
            return False
        return self._head.has_symbol(symbol_name) or any(
            element.has_symbol(symbol_name) for element in self._elements
        )

    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, value):
        raise ValueError("Expression.head is write protected.")

    # Deprecated - remove eventually
    @property
    def leaves(self):
        return self._elements

    # Deprecated - remove eventually
    @leaves.setter
    def leaves(self, value):
        raise ValueError("Expression.leaves is write protected.")

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

    def rewrite_apply_eval_step(self, evaluation) -> typing.Tuple["Expression", bool]:
        """Perform a single rewrite/apply/eval step of the bigger
        Expression.evaluate() process.

        We return the Expression as well as a Boolean which indicates
        whether the caller `evaluate()` should consider reevaluating
        the expression.

        Note that this is a recursive process: we may call something
        that may call our parent: evaluate() which calls us again.

        Also note that this step is time consuming, complicated, and involved.

        Therefore, subclasses of the BaseEvaluation class may decide
        to specialize this code so that it is simpler and faster. In
        particular, a specialization for a particular kind of object
        like a particular kind of Atom, may decide it does not need to
        do the rule rewriting step. Or that it knows that after
        performing this step no further transformation is needed.

        See also https://mathics-development-guide.readthedocs.io/en/latest/extending/code-overview/evaluation.html#detailed-rewrite-apply-eval-process
        """
        from mathics.builtin.base import BoxConstruct

        # Step 1 : evaluate the Head and get its Attributes. These attributes, used later, include
        # HoldFirst / HoldAll / HoldRest / HoldAllComplete.

        # Note: self._head can be not just a symbol, but some arbitrary expression.
        # This is what makes expressions in Mathics be M-expressions rather than
        # S-expressions.
        head = self._head.evaluate(evaluation)

        attributes = head.get_attributes(evaluation.definitions)
        elements = self.get_mutable_elements()

        # The rest of the evaluation is very time-consuming.

        # One reason for this is that we evaluate each element,
        # independently of the kind of element. Strings, numbers, and
        # symbols are treated the same in evaluation. So F[1,2,3,...]
        # takes more or less the same time that F[a1,a2,a3,..]  and
        # F[a1,a1,a1,a1] whether or not a1... have assigned a value.
        # However there is an expression cache.

        # Functions Evaluate[] / Unevaluated[] found in the Expression alter evaluation
        def rest_range(indices):
            if not hold_all_complete & attributes:
                if self._no_symbol("System`Evaluate"):
                    return
                for index in indices:
                    element = elements[index]
                    if element.has_form("Evaluate", 1):
                        elements[index] = element.evaluate(evaluation)

        def eval_range(indices):
            for index in indices:
                element = elements[index]
                if not element.has_form("Unevaluated", 1):
                    element = element.evaluate(evaluation)
                    if element:
                        elements[index] = element

        if (hold_all | hold_all_complete) & attributes:
            # eval_range(range(0, 0))
            rest_range(range(len(elements)))
        elif hold_first & attributes:
            rest_range(range(0, min(1, len(elements))))
            eval_range(range(1, len(elements)))
        elif hold_rest & attributes:
            eval_range(range(0, min(1, len(elements))))
            rest_range(range(1, len(elements)))
        else:
            eval_range(range(len(elements)))
            # rest_range(range(0, 0))

        # Step 2: Build a new expression. Notice that elements are given
        # after creating the object, to avoid to call `from_python` on each element.
        new = Expression(head)
        new._elements = tuple(elements)

        # Step 3: Now, process the attributes of head
        # If there are sequence, flatten them if the attributes allow it.
        if not (sequence_hold | hold_all_complete) & attributes:
            # This step is applied to most of the expressions
            # and could be heavy for expressions with many elements (like long lists)
            # however, most of the times, expressions does not have `Sequence` expressions
            # inside. Now this is handled by caching the sequences.
            new = new.flatten_sequence(evaluation)
            elements = new._elements

        # comment @mmatera: I think this is wrong now, because alters singletons... (see PR #58)
        # The idea is to mark which elements was marked as "Unevaluated"
        # Also, this consumes time for long lists, and is useful just for a very unfrequent
        # expressions, involving `Unevaluated` elements.
        for element in elements:
            element.unevaluated = False

        # If HoldAllComplete is not an attribute,
        # and the expression has elements of the form  `Unevaluated[element]`
        # change them to `element` and set a flag `unevaluated=True`
        # If the evaluation fails, use this flag to restore back the initial form
        # Unevaluated[element]

        # comment @mmatera:
        # what we need here is some way to track which elements are marked as
        # Unevaluated, that propagates by flatten, and at the end,
        # to recover a list of positions that (eventually)
        # must be marked again as Unevaluated.

        if not hold_all_complete & attributes:
            dirty_elements = None

            for index, element in enumerate(elements):
                if element.has_form("Unevaluated", 1):
                    if dirty_elements is None:
                        dirty_elements = list(elements)
                    dirty_elements[index] = element._elements[0]
                    dirty_elements[index].unevaluated = True

            if dirty_elements:
                new = Expression(head)
                new._elements = tuple(dirty_elements)
                elements = dirty_elements

        # If the attribute Flat is set, calls flatten with a callback
        # that set elements as unevaluated too.
        def flatten_callback(new_elements, old):
            for element in new_elements:

                element.unevaluated = old.unevaluated

        if flat & attributes:
            new = new.flatten(new._head, callback=flatten_callback)

        # If the attribute `Orderless` is set, sort the elements, according to the
        # `get_sort` criteria.
        # the most expensive part of this is to build the sort key.
        if orderless & attributes:
            new.sort()

        # Step 4:  Rebuild the ExpressionCache, which tracks which symbols
        # where involved, the Sequence`s present, and the last time they have changed.

        new._timestamp_cache(evaluation)

        # Step 5: Must we need to thread-rewrite the expression?
        #
        # Threading is needed when head has the ``Listable``
        # Attribute.  ``Expression.thread`` rewrites the expression:
        #  ``F[{a,b,c,...}]`` as:
        #  ``{F[a], F[b], F[c], ...}``.

        # Note: Threading here is different from Python or OS threads,
        # even though the intent of this attribute was to allow for
        # hardware threading to make use of more cores.
        #
        # Right now, we do not make use of Python thread or hardware
        # threading.  Still, we need to perform this rewrite to
        # maintain correct semantic behavior.
        if listable & attributes:
            done, threaded = new.thread(evaluation)
            if done:
                if threaded.sameQ(new):
                    new._timestamp_cache(evaluation)
                    return new, False
                else:
                    return threaded, True

        # Step 6: Now,the next step is to look at the rules associated to
        # 1. the upvalues of each element
        # 2. the downvalues / subvalues associated to the lookup_name
        # if the lookup values matches or not the head.
        # For example for an expression F[a, 1, b,a]
        #
        # first look for upvalue rules associated to a.
        # If it finds it, try to apply the corresponding rule.
        #    If it success, (the result is not None)
        #      returns  result, reevaluate. reevaluate is True if the result is a different expression, and is not a BoxConstruct.
        #    If the rule fails, continues with the next element.
        #
        # The next element is a number, so do not have upvalues. Then tries with upvalues from b.
        # If it does not have  success, tries look at the next element. but the next element is again a. So, it skip it.
        # Then, as new.head_name() == new.get_lookup_name(),  (because F is a symbol) tryies with the
        # downvalues rules. If instead of "F[a, 1, a, c]" we had  "Q[s][a,1,a,c]",
        # the routine would look for the subvalues of `Q`.
        #
        # For `Plus` and `Times`, WMA behaves slightly different when deals with numbers. For example,
        # ```
        # Unprotect[Plus];
        # Plus[2,3]:=fish;
        # Plus[2,3]
        # ```
        # in mathics results in  `fish`, but in WL results in  `5`. This special behaviour suggests
        # that WMA process in a different way certain symbols.

        def rules():
            rules_names = set()
            if not hold_all_complete & attributes:
                for element in elements:
                    name = element.get_lookup_name()
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
                # Subvalues applies for expressions of the form `D[1][f][x]`
                # For this expression, the `head` would be `D[1][f]`
                # while its `lookup_name` would be `D`.
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

        # Step 7: If we are here, is because we didn't find any rule that matches with the expression.

        dirty_elements = None

        # Expression did not change, re-apply Unevaluated
        for index, element in enumerate(new._elements):
            if element.unevaluated:
                if dirty_elements is None:
                    dirty_elements = list(new._elements)
                dirty_elements[index] = Expression("Unevaluated", element)

        if dirty_elements:
            new = Expression(head)
            new._elements = tuple(dirty_elements)

        # Step 8:updates the cache and returns the new form, with the reevaluate flag to false.
        new._timestamp_cache(evaluation)
        return new, False

    #  Now, let's see how much take each step for certain typical expressions:
    #  (assuming that "F" and "a1", ... "a100" are undefined symbols, and n0->0, n1->1,..., n99->99)
    #
    #  Expr1: Expression("F", 1)                       (trivial evaluation to a short expression)
    #  Expr2: Expression("F", 0, 1, 2, .... 99)        (trivial evaluation to a long expression, with just numbers)
    #  Expr3: Expression("F", a0, a2, ...., a99)       (trivial evaluation to a long expression, with just undefined symbols)
    #  Expr4: Expression("F", n0, n2, ...., n99)       (trivial evaluation to a long expression, with just undefined symbols)
    #  Expr5: Expression("Plus", 99,..., 0)            (nontrivial evaluation to a long expression, with just undefined symbols)
    #  Expr6: Expression("Plus", a99,..., a0)          (nontrivial evaluation to a long expression, with just undefined symbols)
    #  Expr7: Expression("Plus", n99,..., n0)          (nontrivial evaluation to a long expression, with just undefined symbols)
    #  Expr8: Expression("Plus", n1,..., n1)           (nontrivial evaluation to a long expression, with just undefined symbols)
    #

    def round_to_float(self, evaluation=None, permit_complex=False) -> Optional[float]:
        """
        Round to a Python float. Return None if rounding is not possible.
        This can happen if self or evaluation is NaN.
        """

        if evaluation is None:
            value = self
        elif isinstance(evaluation, sympy.core.numbers.NaN):
            return None
        else:
            value = self.create_expression(SymbolN, self).evaluate(evaluation)
        if hasattr(value, "round") and hasattr(value, "get_float_value"):
            value = value.round()
            return value.get_float_value(permit_complex=permit_complex)
        return None

    def sameQ(self, other: BaseElement) -> bool:
        """Mathics SameQ"""
        if not isinstance(other, Expression):
            return False
        if self is other:
            return True
        if not self._head.sameQ(other.get_head()):
            return False
        if len(self._elements) != len(other.get_elements()):
            return False
        return all(
            (id(element) == id(oelement) or element.sameQ(oelement))
            for element, oelement in zip(self._elements, other.get_elements())
        )

    def sequences(self):
        cache = self._cache
        if cache:
            seq = cache.sequences
            if seq is not None:
                return seq

        return self._rebuild_cache().sequences

    def set_head(self, head):
        self._head = head
        self._cache = None

    def set_element(self, index: int, value):
        """
        Update element[i] with value
        """
        elements = list(self._elements)
        elements[index] = value
        self._elements = tuple(elements)
        self._cache = None

    def shallow_copy(self) -> "Expression":
        # this is a minimal, shallow copy: head, elements are shared with
        # the original, only the Expression instance is new.
        expr = Expression(self._head)
        expr._elements = self._elements
        # rebuilding the cache in self speeds up large operations, e.g.
        # First[Timing[Fold[#1+#2&, Range[750]]]]
        expr._cache = self._rebuild_cache()
        expr.options = self.options
        # expr.last_evaluated = self.last_evaluated
        return expr

    def slice(self, head, py_slice, evaluation):
        # faster equivalent to: Expression(head, *self.leaves[py_slice])
        return structure(head, self, evaluation).slice(self, py_slice)

    def to_mpmath(self):
        return None

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
                compiled = Expression(SymbolCompile, *(self._elements))
                compiled = compiled.evaluate(n_evaluation)
                if compiled.get_head() is SymbolCompiledFunction:
                    return compiled.leaves[2].cfunc
            value = Expression(SymbolN, self).evaluate(n_evaluation)
            return value.to_python()

        if head is SymbolDirectedInfinity and len(self._elements) == 1:
            direction = self._elements[0].get_int_value()
            if direction == 1:
                return math.inf
            if direction == -1:
                return -math.inf
        elif head is SymbolList:
            return [element.to_python(*args, **kwargs) for element in self._elements]

        head_name = head.get_name()
        if head_name in mathics_to_python:
            py_obj = mathics_to_python[head_name]
            # Start here
            # if inspect.isfunction(py_obj) or inspect.isbuiltin(py_obj):
            #     args = [element.to_python(*args, **kwargs) for element in self._elements]
            #     return ast.Call(
            #         func=py_obj.__name__,
            #         args=args,
            #         keywords=[],
            #         )
            return py_obj
        return self

    def to_sympy(self, **kwargs):
        from mathics.builtin import mathics_to_sympy

        if "convert_all_global_functions" in kwargs:
            if len(self.leaves) > 0 and kwargs["convert_all_global_functions"]:
                if self.get_head_name().startswith("Global`"):
                    return self._as_sympy_function(**kwargs)

        if "converted_functions" in kwargs:
            functions = kwargs["converted_functions"]
            if len(self._elements) > 0 and self.get_head_name() in functions:
                sym_args = [element.to_sympy() for element in self._elements]
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

    def process_style_box(self, options):
        if self.has_form("StyleBox", 1, None):
            rules = self._elements[1:]
            for rule in rules:
                if rule.has_form("Rule", 2):
                    name = rule._elements[0].get_name()
                    value = rule._elements[1]
                    if name == "System`ShowStringCharacters":
                        value = value.is_true()
                        options = options.copy()
                        options["show_string_characters"] = value
                    elif name == "System`ImageSizeMultipliers":
                        if value.has_form("List", 2):
                            m1 = value._elements[0].round_to_float()
                            m2 = value._elements[1].round_to_float()
                            if m1 is not None and m2 is not None:
                                options = options.copy()
                                options["image_size_multipliers"] = (m1, m2)
            return True, options
        else:
            return False, options

    def sort(self, pattern=False):
        """
        Sort the elements using the Python's list-method sort.
        `get_sort_key() is used for comparison if `pattern` is True.
        Otherwise use the the default Python 3.x compare function,
        `__lt__()` that is found in each element.

        `self._cache` is updated if that is not None.
        """
        # It is stupid to sort 0 or 1 elements.
        if len(self._elements) < 2:
            return

        # There is no in-place sort method on a tuple, because tuples are not
        # mutable. So we turn into a elments into list and use Python's
        # list sort method. Another approach would be to use sorted().
        elements = list(self._elements)
        if pattern:
            elements.sort(key=lambda e: e.get_sort_key(pattern_sort=True))
        else:
            elements.sort()

        # update `self._elements` and self._cache with the possible permuted order.
        self._elements = tuple(elements)
        if self._cache:
            self._cache = self._cache.reordered()

    def apply_rules(self, rules, evaluation, level=0, options=None):
        """for rule in rules:
        result = rule.apply(self, evaluation, fully=False)
        if result is not None:
            return result"""

        # to be able to access it inside inner function
        new_applied = [False]

        def apply_element(element):
            new, sub_applied = element.apply_rules(
                rules, evaluation, level + 1, options
            )
            new_applied[0] = new_applied[0] or sub_applied
            return new

        def descend(expr):
            return Expression(
                expr._head, *[apply_element(element) for element in expr._elements]
            )

        if options is None:  # default ReplaceAll mode; replace breadth first
            result, applied = super().apply_rules(rules, evaluation, level, options)
            if applied:
                return result, True
            head, applied = self._head.apply_rules(rules, evaluation, level, options)
            new_applied[0] = applied
            return descend(Expression(head, *self._elements)), new_applied[0]
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
                expr = Expression(head, *expr._elements)
            return expr, new_applied[0]

    def replace_vars(
        self, vars, options=None, in_scoping=True, in_function=True
    ) -> "Expression":
        """
        Replace the symbols in the expression by the expressions given in the vars dictionary.
        in_scoping: if `False`, avoid to replace those symbols that are declared internal to the scope.
        in_function: if `True`, and the Expression is of the form Function[{args},body], changes the names of the args
        to avoid replacing them.
        """
        from mathics.builtin.scoping import get_scoping_vars

        if not in_scoping:
            if (
                self._head.get_name()
                in ("System`Module", "System`Block", "System`With")
                and len(self._elements) > 0
            ):  # nopep8

                scoping_vars = set(
                    name for name, new_def in get_scoping_vars(self._elements[0])
                )
                """for var in new_vars:
                    if var in scoping_vars:
                        del new_vars[var]"""
                vars = {
                    var: value for var, value in vars.items() if var not in scoping_vars
                }

        elements = self._elements
        if in_function:
            if (
                self._head is SymbolFunction
                and len(self._elements) > 1
                and (
                    self._elements[0].has_form("List", None)
                    or self._elements[0].get_name()
                )
            ):
                if self._elements[0].get_name():
                    func_params = [self._elements[0].get_name()]
                else:
                    func_params = [
                        element.get_name() for element in self._elements[0]._elements
                    ]
                if "" not in func_params:
                    body = self._elements[1]
                    replacement = {name: Symbol(name + "$") for name in func_params}
                    func_params = [Symbol(name + "$") for name in func_params]
                    body = body.replace_vars(replacement, options, in_scoping)
                    elements = chain(
                        [Expression(SymbolList, *func_params), body], self._elements[2:]
                    )

        if not vars:  # might just be a symbol set via Set[] we looked up here
            return self.shallow_copy()

        return Expression(
            self._head.replace_vars(vars, options=options, in_scoping=in_scoping),
            *[
                element.replace_vars(vars, options=options, in_scoping=in_scoping)
                for element in elements
            ]
        )

    def replace_slots(self, slots, evaluation):
        """
        Replaces Slots (#1, ##, etc) by the corresponding values in `slots`
        """
        if self._head is SymbolSlot:
            if len(self._elements) != 1:
                evaluation.message_args("Slot", len(self._elements), 1)
            else:
                slot = self._elements[0].get_int_value()
                if slot is None or slot < 0:
                    evaluation.message("Function", "slot", self._elements[0])
                elif slot > len(slots) - 1:
                    evaluation.message("Function", "slotn", slot)
                else:
                    return slots[int(slot)]
        elif self._head is SymbolSlotSequence:
            if len(self._elements) != 1:
                evaluation.message_args("SlotSequence", len(self._elements), 1)
            else:
                slot = self._elements[0].get_int_value()
                if slot is None or slot < 1:
                    evaluation.error("Function", "slot", self._elements[0])
            return Expression(SymbolSequence, *slots[slot:])
        elif self._head is SymbolFunction and len(self._elements) == 1:
            # do not replace Slots in nested Functions
            return self
        return Expression(
            self._head.replace_slots(slots, evaluation),
            *[element.replace_slots(slots, evaluation) for element in self._elements]
        )

    def thread(self, evaluation, head=None) -> typing.Tuple[bool, "Expression"]:
        """
        Thread over expressions with head as Head:
        Thread[F[{a,b},{c,d}, G[z,q]],G] -> newexpr = G[F[{a, b}, {c, d}, z], F[{a, b}, {c, d}, q]]

        By default, head=SymbolList

        If the expression has changes, returns True, newexpr
        otherwise, return False, self
        """
        if head is None:
            head = SymbolList

        items = []
        dim = None
        for element in self._elements:
            if element.get_head().sameQ(head):
                if dim is None:
                    dim = len(element._elements)
                    items = [
                        (items + [innerelement]) for innerelement in element._elements
                    ]
                elif len(element._elements) != dim:
                    evaluation.message("Thread", "tdlen")
                    return True, self
                else:
                    for index in range(dim):
                        items[index].append(element._elements[index])
            else:
                if dim is None:
                    items.append(element)
                else:
                    for item in items:
                        item.append(element)
        if dim is None:
            return False, self
        else:
            elements = [Expression(self._head, *item) for item in items]
            return True, Expression(head, *elements)

    def is_numeric(self, evaluation=None) -> bool:
        if evaluation:
            if not numeric_function & evaluation.definitions.get_attributes(
                self._head.get_name()
            ):
                return False
            for element in self._elements:
                if not element.is_numeric(evaluation):
                    return False
            return True
            # return all(element.is_numeric(evaluation) for element in self._elements)
        else:
            return self._head in symbols_arithmetic_operations and all(
                element.is_numeric() for element in self._elements
            )

    def numerify(self, evaluation) -> "BaseElement":
        """
        Produces a new expression equivalent to the original,
        s.t. inexact numeric elements are reduced to Real numbers with
        the same precision.
        This is used in arithmetic evaluations (like `Plus`, `Times`, and `Power` )
        and in iterators.
        """
        _prec = None
        for element in self._elements:
            if element.is_inexact():
                element_prec = element.get_precision()
                if _prec is None or element_prec < _prec:
                    _prec = element_prec
        if _prec is not None:
            new_elements = self.get_mutable_elements()
            for index in range(len(new_elements)):
                element = new_elements[index]
                # Don't "numerify" numbers: they should be numerified
                # automatically by the processing function,
                # and we don't want to lose exactness in e.g. 1.0+I.
                # Also, for compatibility with WMA, numerify just the elements
                # s.t. ``NumericQ[element]==True``
                if not isinstance(element, Number) and element.is_numeric(evaluation):
                    n_expr = Expression(SymbolN, element, Integer(dps(_prec)))
                    n_result = n_expr.evaluate(evaluation)
                    if isinstance(n_result, Number):
                        new_elements[index] = n_result
                        continue
                    # If Nvalues are not available, just tries to do
                    # a regular evaluation
                    n_result = element.evaluate(evaluation)
                    if isinstance(n_result, Number):
                        new_elements[index] = n_result
            result = Expression(self._head)
            result._elements = tuple(new_elements)
            return result

        else:
            return self

    def user_hash(self, update):
        update(("%s>%d>" % (self.get_head_name(), len(self._elements))).encode("utf8"))
        for element in self._elements:
            element.user_hash(update)


def _create_expression(self, head, *elements):
    return Expression(head, *elements)


BaseElement.create_expression = _create_expression


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
    def __call__(self, elements):
        # create an Expression with the given list "elements" as elements.
        # NOTE: the caller guarantees that "elements" only contains items that are from "origins".
        raise NotImplementedError

    def filter(self, expr, cond):
        # create an Expression with a subset of "expr".elements (picked out by the filter "cond").
        # NOTE: the caller guarantees that "expr" is from "origins".
        raise NotImplementedError

    def slice(self, expr, py_slice):
        # create an Expression, using the given slice of "expr".elements as elements.
        # NOTE: the caller guarantees that "expr" is from "origins".
        raise NotImplementedError


# UnlinkedStructure produces Expressions that are not linked to "origins" in terms of cache.
# This produces the same thing as doing Expression(head, *elements).


class UnlinkedStructure(Structure):
    def __init__(self, head):
        self._head = head
        self._cache = None

    def __call__(self, elements):
        expr = Expression(self._head)
        expr._elements = tuple(elements)
        return expr

    def filter(self, expr, cond):
        return self([element for element in expr._elements if cond(element)])

    def slice(self, expr, py_slice):
        elements = expr._elements
        lower, upper, step = py_slice.indices(len(elements))
        if step != 1:
            raise ValueError("Structure.slice only supports slice steps of 1")
        return self(elements[lower:upper])


# LinkedStructure produces Expressions that are linked to "origins" in terms of cache. This
# carries over information from the cache of the originating Expressions into the Expressions
# that are newly created.


class LinkedStructure(Structure):
    def __init__(self, head, cache):
        self._head = head
        self._cache = cache

    def __call__(self, elements):
        expr = Expression(self._head)
        expr._elements = tuple(elements)
        expr._cache = self._cache.reordered()
        return expr

    def filter(self, expr, cond):
        return self([element for element in expr._elements if cond(element)])

    def slice(self, expr, py_slice):
        elements = expr._elements
        lower, upper, step = py_slice.indices(len(elements))
        if step != 1:
            raise ValueError("Structure.slice only supports slice steps of 1")

        new = Expression(self._head)
        new._elements = tuple(elements[lower:upper])
        if expr._cache:
            new._cache = expr._cache.sliced(lower, upper)

        return new


def structure(head, origins, evaluation, structure_cache=None):
    # creates a Structure for building Expressions with head "head" and elements
    # originating (exclusively) from "origins" (elements are passed into the functions
    # of Structure further down).

    # "origins" may either be an Expression (i.e. all elements must originate from that
    # expression), a Structure (all elements passed in this "self" Structure must be
    # manufactured using that Structure), or a list of Expressions (i.e. all elements
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

        def construct(elements):
            expr = Expression(head)
            expr._elements = list(elements)
            sym = set(chain([head.get_name()], full_atom_names))
            expr._cache = ExpressionCache(evaluation.definitions.now, sym, None)
            return expr

    else:

        def construct(elements):
            expr = Expression(head)
            expr._elements = list(elements)
            return expr

    return construct


def string_list(head, elements, evaluation):
    return atom_list_constructor(evaluation, head, "String")(elements)
