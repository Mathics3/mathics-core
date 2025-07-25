# cython: language_level=3
# -*- coding: utf-8 -*-

import math
from bisect import bisect_left
from itertools import chain
from types import MethodType
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

import sympy
from mathics_scanner.location import SourceRange, SourceRange2

from mathics.core.atoms import Integer1, String
from mathics.core.attributes import (
    A_FLAT,
    A_HOLD_ALL,
    A_HOLD_ALL_COMPLETE,
    A_HOLD_FIRST,
    A_HOLD_REST,
    A_LISTABLE,
    A_NO_ATTRIBUTES,
    A_NUMERIC_FUNCTION,
    A_ORDERLESS,
    A_SEQUENCE_HOLD,
    attribute_string_to_number,
)
from mathics.core.convert.python import from_python
from mathics.core.element import ElementsProperties, EvalMixin, ensure_context
from mathics.core.evaluation import Evaluation
from mathics.core.interrupt import ReturnInterrupt
from mathics.core.structure import LinkedStructure
from mathics.core.symbols import (
    Atom,
    BaseElement,
    Monomial,
    NumericOperators,
    Symbol,
    SymbolAbs,
    SymbolDivide,
    SymbolList,
    SymbolN,
    SymbolPlus,
    SymbolTimes,
    SymbolTrue,
    symbol_set,
)
from mathics.core.systemsymbols import (
    SymbolAborted,
    SymbolAlternatives,
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolCondition,
    SymbolDirectedInfinity,
    SymbolFunction,
    SymbolMinus,
    SymbolOptional,
    SymbolOptionsPattern,
    SymbolOverflow,
    SymbolPattern,
    SymbolPatternTest,
    SymbolPower,
    SymbolSequence,
    SymbolSin,
    SymbolSlot,
    SymbolSqrt,
    SymbolSubtract,
    SymbolUnevaluated,
)
from mathics.eval.tracing import trace_evaluate

# from mathics.timing import timeit

SymbolEvaluate = Symbol("System`Evaluate")
SymbolSlotSequence = Symbol("SlotSequence")
SymbolVerbatim = Symbol("Verbatim")


symbols_arithmetic_operations = symbol_set(
    SymbolAbs,
    SymbolDivide,
    SymbolMinus,
    SymbolPlus,
    SymbolPower,
    SymbolSin,
    SymbolSqrt,
    SymbolSubtract,
    SymbolTimes,
)


def eval_SameQ(self, other):
    """
    Iterative implementation of SameQ[].

    Tree traversal comparison between `self` and `other`.
    Return `True` if both tree structures are equal.

    This non-recursive implementation reduces the Python stack needed
    in evaluation. Staring in Python 3.12 there is a limit on the
    recursion level.
    """

    len_elements = len(self.elements)
    if len(other._elements) != len_elements:
        return False

    # Initializing a "stack"
    parents = [
        (
            self,
            other,
        )
    ]
    current = (self._head, other._head)
    pos = [0]

    # The next element in the tree. Maybe should be an iterator?
    def next_elem():
        nonlocal len_elements

        while pos and pos[-1] == len_elements:
            pos.pop()
            parents.pop()
            assert len(pos) == len(parents)
            if len(pos) > 0:
                len_elements = len(parents[-1][0]._elements)
                assert len(parents[-1][1]._elements) == len_elements

        if len(pos) == 0:
            return None

        current = tuple(p._elements[pos[-1]] for p in parents[-1])
        pos[-1] += 1
        return current

    while current:
        if current[0] is current[1]:
            current = next_elem()
        elif all(isinstance(elem, Atom) for elem in current):
            if not current[0].sameQ(current[1]):
                return False
            current = next_elem()
        elif all(isinstance(elem, Expression) for elem in current):
            len_elements = len(current[0]._elements)
            if len_elements != len(current[1]._elements):
                return False
            parents.append(current)
            current = tuple((c._head for c in current))
            pos.append(0)
        else:  # Atom is not the same than an expression
            return False

    return True


class BoxError(Exception):
    def __init__(self, box, form) -> None:
        super().__init__("Box %s cannot be formatted as %s" % (box, form))
        self.box = box
        self.form = form


# ExpressionCache keeps track of the following attributes for one Expression instance:

# time: (1) the last time (in terms of Definitions.now) this expression was evaluated
#   or (2) None, if the current expression has not yet been evaluated (i.e. is new or
#   changed).
# symbols: (1) a set of symbols occurring in this expression's head, its elements'
#   heads, any of its sub expressions' heads or as Symbol elements somewhere (maybe deep
#   down) in the expression tree start by this expressions' elements, or (2) None, if no
#   information on which symbols are contained in this expression is available
# sequences: (1) a list of element indices that indicate the position of all Sequence
#   heads that are either in the element's head or any of the indicated elements's sub
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
        # indicates that the Expression's elements have been slices with
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
        # indicates that the Expression's elements have been reordered
        # or reduced (i.e. that the elements have changed, but that
        # no new element instances were added).

        sequences = self.sequences

        # note that we keep sequences == [], since they are fine even
        # after having reordered elements.
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

        symbols = set.union(*[expr._cache.symbols for expr in expressions])

        return ExpressionCache(
            definitions.now, symbols, None if "System`Sequence" in symbols else tuple()
        )


class Expression(BaseElement, NumericOperators, EvalMixin):
    """A Mathics3 (compound) M-Expression.

    A Mathics3 M-Expression is a list where the head is a function
    designator.  (In the more common S-Expression the head is an a
    Symbol. In Mathics3, this can be an expression that acts as a
    function.

    positional Arguments:

    - ``head`` -- The head of the M-Expression
    - ``*elements`` - optional: the remaining elements
    - ``*literal_values`` - optional: if this is not ``None``, then all elements
      are (Python) literal values and ``literal_values`` contains these literals.

    Keyword Arguments:

    - ``elements_properties`` -- properties of the collection of elements

    """

    _head: BaseElement
    _elements: Tuple[BaseElement, ...]
    _sequences: Any
    _cache: Optional[ExpressionCache]
    elements_properties: Optional[ElementsProperties]
    options: Optional[Dict[str, Any]]
    pattern_sequence: bool
    location: Optional[Union[SourceRange, SourceRange2, MethodType]]

    def __init__(
        self,
        head: BaseElement,
        *elements: BaseElement,
        elements_properties: Optional[ElementsProperties] = None,
        literal_values: Optional[tuple] = None,
    ):
        self.options = None
        self.pattern_sequence = False

        # # Uncomment to check for errors:
        # assert isinstance(head, BaseElement)
        # assert isinstance(elements, tuple)
        # assert all(isinstance(e, BaseElement) for e in elements)
        # assert head is BaseElement

        self._head = head
        self._elements = elements
        self.elements_properties = elements_properties
        self.value = literal_values
        self._is_literal = None if literal_values is None else True

        self._sequences = None
        self._cache = None
        self.location = None

        # self.copy creates this
        self.original: Optional[Expression] = None

    def __getnewargs__(self):
        return (self._head, self._elements)

    def __hash__(self):
        return hash(("Expression", self._head) + tuple(self._elements))

    def __repr__(self) -> str:
        return "<Expression: %s[%s]>" % (
            repr(self.head),
            ", ".join([repr(element) for element in self.elements]),
        )

    def __str__(self) -> str:
        return "%s[%s]" % (
            str(self.head),
            ", ".join([str(element) for element in self.elements]),
        )

    def _as_sympy_function(self, **kwargs):
        from mathics.core.convert.sympy import sympy_symbol_prefix

        function_name = str(sympy_symbol_prefix + self.get_head_name())
        f = sympy.Function(function_name)

        if kwargs.get("convert_functions_for_polynomial", False):
            # For polynomials, we ignore the arguments in a PolynomialQ
            return f()

        f = sympy.Function(function_name)
        sym_args = [element.to_sympy(**kwargs) for element in self._elements]

        if None in sym_args:
            return None

        return f(*sym_args)

    # Note: this function is called a *lot* so it needs to be fast.
    def _build_elements_properties(self):
        """
        Compute ElementsProperties and store in self.elements_properties
        """

        # All of the properties start out optimistic (True) and are reset when that proves wrong.
        self.elements_properties = ElementsProperties(True, True, True)

        last_element = None
        values = []
        for element in self._elements:
            # Test for the literalness, and the three properties mentioned above
            if not element.is_literal:
                self.elements_properties.elements_fully_evaluated = False

            if isinstance(element, Expression):
                # "self" can't be flat.
                self.elements_properties.is_flat = False

                # "elements_properties" only exists for Expression types
                # If we haven't set element.elements properties, compute that...
                if element.elements_properties is None:
                    if hasattr(self, "_is_literal"):
                        self._is_literal = False
                    element._build_elements_properties()

                # and now possibly adjust self.elements_properties.elements_fully_evaluted
                if self.elements_properties.elements_fully_evaluated:
                    self._elements_fully_evaluated = (
                        element.elements_properties.elements_fully_evaluated
                    )

            if element.is_literal:
                values.append(element.value)
            else:
                # FIXME: uncommenting this out messes up formatting.
                # File "mathics-core/mathics/core/formatter.py", line 135, in ret_fn
                # return boxes_to_method(elements, **opts)
                # TypeError: boxes_to_text() takes 1 positional argument but 2 were given
                # Why?
                self.elements_properties.elements_fully_evaluated = False

            # Test for ordered property
            if self.elements_properties.is_ordered and last_element is not None:
                try:
                    self.elements_properties.is_ordered = last_element <= element
                except Exception:
                    self.elements_properties.is_ordered = False
            last_element = element

        # self.is_literal should only be True for ListExpression.
        # However we have still some Expression(ListSymbol, ...) around?
        if self.is_literal:
            assert self.elements_properties.elements_fully_evaluated
            self.value = tuple(values)

    def _flatten_sequence(self, sequence, evaluation) -> "Expression":
        indices = self.sequences()
        if not indices:
            return self

        elements = self._elements

        flattened: List[BaseElement] = []

        k = 0
        for i in indices:
            flattened.extend(elements[k:i])
            flattened.extend(sequence(elements[i]))
            k = i + 1
        flattened.extend(elements[k:])

        return self.restructure(self._head, flattened, evaluation)

    def _does_not_contain_symbol(self, symbol_name: str) -> bool:
        """
        Return True if all of elements (at any level) under self cannot contain
        a ``symbol_name``. Otherwise return False if there might be ``symbol``
        name under the elements of ``self``.
        """
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

    def clear_cache(self):
        self._cache = None

    def copy(self, reevaluate=False) -> "Expression":
        expr = Expression(self._head.copy(reevaluate))
        expr.elements = tuple(element.copy(reevaluate) for element in self._elements)
        if not reevaluate:
            # rebuilding the cache in self speeds up large operations, e.g.
            # First[Timing[Fold[#1+#2&, Range[750]]]]
            expr._cache = self._rebuild_cache()
        expr.options = self.options
        expr.original = self
        expr._sequences = self._sequences
        return expr

    def default_format(self, evaluation, form) -> str:
        return "%s[%s]" % (
            self._head.default_format(evaluation, form),
            ", ".join(
                [element.default_format(evaluation, form) for element in self._elements]
            ),
        )

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, values: Iterable):
        self._elements = tuple(values)
        # Set to build self.elements_properties on next evaluation()
        self.elements_properties = None

    def equal2(self, rhs: Any) -> Optional[bool]:
        """Mathics3 two-argument Equal (==)
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
            if len(self.elements) != len(rhs.elements):
                return False
            for item1, item2 in zip(self.elements, rhs.elements):
                result = item1.equal2(item2)
                if not result:
                    return result
            return True
        elif head in (SymbolDirectedInfinity,):
            return self.elements[0].equal2(rhs.elements[0])
        return None

    # Note that the return type is some subclass of BaseElement, it could be
    # a Real, an Expression, etc. It probably will *not* be a BaseElement since
    # the point of evaluation when there is not an error is to produce a concrete result.
    @trace_evaluate
    def evaluate(
        self,
        evaluation: Evaluation,
    ) -> Optional[BaseElement]:
        """
        Apply transformation rules and expression evaluation to ``evaluation`` via
        ``rewrite_apply_eval_step()`` until that method tells us to stop,
        or until we hit an $IterationLimit or TimeConstrained limit.

        Evaluation is recursive:``rewrite_apply_eval_step()`` may call us.
        """
        if evaluation.timeout:
            return None

        expr: Optional[BaseElement] = self
        reevaluate = True
        limit = None
        iteration = 1
        names: Set[str] = set()
        definitions = evaluation.definitions

        old_options = evaluation.options
        evaluation.inc_recursion_depth()
        try:
            # Evaluation loop:
            while reevaluate:
                assert isinstance(expr, EvalMixin)

                # If definitions have not changed in the last evaluation,
                # then evaluating again will produce the same result
                if not expr.is_uncertain_final_definitions(definitions):
                    break
                # Here the names of the lookupname of the expression
                # are stored. This is necessary for the implementation
                # of the builtin `Return[]`
                names.add(expr.get_lookup_name())

                # This loads the default options associated
                # to the expression
                if hasattr(expr, "options") and expr.options:
                    evaluation.options = expr.options

                # ``rewrite_apply_eval_step()`` makes a pass at
                # evaluating the expression. If we know that a further
                # evaluation will not be needed, ``reevaluate`` is set
                # False.  Note that ``rewrite_apply_eval_step()`` can
                # perform further ``evaluate`` and we will recurse
                # back into this routine.
                expr, reevaluate = expr.rewrite_apply_eval_step(evaluation)

                if not reevaluate:
                    break

                # TraceEvaluation[] logging.
                iteration += 1
                # Check whether we have hit $Iterationlimit: is the number of times
                # ``reevaluate`` came back False in this loop.
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
        # Otherwise it propagates up.
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
        """
        return a new expression with the same head, and the
        evaluable elements evaluated.
        """
        elements = []
        for element in self._elements:
            if isinstance(element, EvalMixin):
                result = element.evaluate(evaluation)
                if result is not None:
                    element = result
            elements.append(element)
        head = self._head
        if isinstance(head, Expression):
            head = head.evaluate_elements(evaluation)
        return Expression(head, *elements)

    def filter(self, head, cond, evaluation: Evaluation, count: Optional[int] = None):
        # faster equivalent to: Expression(head, [element in self.elements if cond(element)])
        return structure(head, self, evaluation).filter(self, cond, count)

    # FIXME: go over and preserve elements_properties.
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
        if expr.elements_properties is None:
            expr._build_elements_properties()
        else:
            expr.elements_properties.is_flat = True
        return expr

    def flatten_sequence(self, evaluation):
        def sequence(element):
            if element.get_head_name() == "System`Sequence":
                return element._elements
            else:
                return [element]

        return self._flatten_sequence(sequence, evaluation)

    def flatten_with_respect_to_head(
        self, head: Symbol, pattern_only=False, callback=None, level=100
    ) -> "Expression":
        """
        Flatten elements in ``self`` which have ``head`` in them.

        The idea is that in an expression like:

           Expression(Plus, 1, Expression(Plus, 2, 3), 4)

        when "Plus" is specified as the head, this expression should
        get changed to::

           Expression(Plus, 1, 2, 3, 4)

        In other words, all of the ``Plus`` operands are collected to
        together into one operation.  This is more efficiently
        evaluated. Note that we only flatten ``Plus`` functions, not other
        functions, whether or not they contain ``Plus``.

        So in::

           Expression(Plus, Times(1, 2, Plus(3, 4)))

        the expression is unchanged.

        ``head``: head element to be consider flattening on. Only
              expressions with this will be flattened.  This is always
              the head element or the next head element of the
              expression that the elements are drawn from

        ``callback``: a callback function called each time a element
        is flattened.

        ``level``: maximum depth to flatten. This often isn't used and
                 seems to have been put in as a potential safety
                 measure possibly for the future. If you don't want a
                 limit on flattening pass a negative number.

        ``pattern_only``: if ``True``, just apply to elements that are
        pattern_sequence (see ``ExpressionPattern.get_wrappings``)
        """
        from mathics.core.convert.expression import to_expression_with_specialization

        if level == 0:
            return self
        if self._does_not_contain_symbol(head.get_name()):
            return self
        sub_level = level - 1
        do_flatten = False
        for element in self._elements:
            if (
                isinstance(element, Expression)
                and element.get_head().sameQ(head)
                and (not pattern_only or element.pattern_sequence)
            ):
                do_flatten = True
                break
        if do_flatten:
            new_elements: List[BaseElement] = []
            for element in self._elements:
                if (
                    isinstance(element, Expression)
                    and element.get_head().sameQ(head)
                    and (not pattern_only or element.pattern_sequence)
                ):
                    new_element = element.flatten_with_respect_to_head(
                        head, pattern_only, callback, level=sub_level
                    )
                    if callback is not None:
                        callback(new_element._elements, element)
                    new_elements.extend(new_element._elements)
                else:
                    new_elements.append(element)
            return to_expression_with_specialization(self._head, *new_elements)
        else:
            return self

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
        result = A_NO_ATTRIBUTES
        # Maybe this deserves to specialize Function
        if self._head is SymbolFunction and len(self._elements) == 3:
            res = self._elements[2]
            if res.has_form("List", None):
                attributes = res._elements
            else:
                attributes = (res,)
            for attrib in attributes:
                if not isinstance(attrib, Symbol):
                    # if we had here an evaluation object, instead of
                    # a definition
                    # evaluation.message("Attributes","attnf", a)
                    continue
                result = result | attribute_string_to_number.get(attrib.name, 0)
        return result

    def get_elements(self) -> Sequence[BaseElement]:
        # print("Use of get_elements is deprecated. Use elements instead.")
        return self._elements

    def get_head(self):
        return self._head

    def get_head_name(self):
        return self._head.name if isinstance(self._head, Symbol) else ""

    def get_lookup_name(self) -> str:
        """
        Returns symbol name of leftmost head.
        """
        lookup_symbol = self._head
        while True:
            if isinstance(lookup_symbol, Symbol):
                return lookup_symbol.name
            if isinstance(lookup_symbol, Atom):
                return lookup_symbol.get_head().name
            lookup_symbol = lookup_symbol.get_head()

    def get_mutable_elements(self) -> list:
        """
        Return a shallow mutable copy of the elements
        """
        return list(self._elements)

    def get_option_values(
        self, evaluation: Evaluation, allow_symbols=False, stop_on_error=True
    ) -> Optional[dict]:
        """
        Build a dictionary of options from an expression.
        For example, Symbol("Integrate").get_option_values(evaluation, allow_symbols=True)
        will return a list of options associated to the definition of the symbol "Integrate".
        """
        if self.has_form("List", None):
            values = self.flatten_with_respect_to_head(SymbolList).elements
        else:
            values = [self]
        option_values: Dict[str, Union[str, BaseElement]] = {}
        for option in values:
            symbol_name = option.get_name()
            if allow_symbols and symbol_name:
                option_values.update(evaluation.definitions.get_options(symbol_name))
            else:
                if not option.has_form(("Rule", "RuleDelayed"), 2):
                    if stop_on_error:
                        return None
                    else:
                        continue
                name = option.elements[0].get_name()
                if not name and isinstance(option.elements[0], String):
                    name = ensure_context(option.elements[0].get_string_value())
                if not name:
                    if stop_on_error:
                        return None
                    else:
                        continue
                option_values[name] = option.elements[1]
        return option_values

    # This should only be used in ListExpression. Consider
    # moving it to mathics.core.list after going over
    # test/builtin/atomic/test_assignment.py and
    # ensuring we never use Expression(SymbolList, ...)
    # for ListExpression.
    def get_rules_list(self) -> Optional[list]:
        """
        If the expression is of the form {pat1->expr1,... {pat_2,expr2},...}
        return a (python) list of rules.
        """
        from mathics.core.rules import Rule
        from mathics.core.symbols import SymbolList

        list_expr = self.flatten_with_respect_to_head(SymbolList)
        list = []
        if list_expr.has_form("List", None):
            list.extend(list_expr.elements)
        else:
            list.append(list_expr)
        rules = []
        for item in list:
            if not item.has_form(("Rule", "RuleDelayed"), 2):
                return None
            rule = Rule(item.elements[0], item.elements[1])
            rules.append(rule)
        return rules

    # FIXME: return type should be a specific kind of Tuple, not a tuple.
    def get_sort_key(self, pattern_sort=False) -> tuple:
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
            6: elements / 0 for atoms
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
                return (
                    2,
                    pattern,
                    1,
                    1,
                    0,
                    head.get_sort_key(True),
                    tuple(element.get_sort_key(True) for element in self._elements),
                    1,
                )
            if head is SymbolPatternTest:
                if len(self._elements) != 2:
                    return (3, 0, 0, 0, 0, head, self._elements, 1)
                sub = list(self._elements[0].get_sort_key(True))
                sub[2] = 0
                return tuple(sub)
            elif head is SymbolCondition:
                if len(self._elements) != 2:
                    return (3, 0, 0, 0, 0, head, self._elements, 1)
                sub = list(self._elements[0].get_sort_key(True))
                sub[7] = 0
                return tuple(sub)
            elif head is SymbolPattern:
                if len(self._elements) != 2:
                    return (3, 0, 0, 0, 0, head, self._elements, 1)
                sub = list(self._elements[1].get_sort_key(True))
                sub[3] = 0
                return tuple(sub)
            elif head is SymbolOptional:
                if len(self._elements) not in (1, 2):
                    return (3, 0, 0, 0, 0, head, self._elements, 1)
                sub = list(self._elements[0].get_sort_key(True))
                sub[4] = 1
                return tuple(sub)
            elif head is SymbolAlternatives:
                min_key = (4,)
                min = None
                for element in self._elements:
                    key = element.get_sort_key(True)
                    if key < min_key:
                        min = element
                        min_key = key
                if min is None:
                    # empty alternatives -> very restrictive pattern
                    return (2, 1)
                return min_key
            elif head is SymbolVerbatim:
                if len(self._elements) != 1:
                    return (3, 0, 0, 0, 0, head, self._elements, 1)
                return self._elements[0].get_sort_key(True)
            elif head is SymbolOptionsPattern:
                return (2, 40, 0, 1, 1, 0, head, self._elements, 1)
            else:
                # Append (4,) to elements so that longer expressions have higher
                # precedence
                return (
                    2,
                    0,
                    1,
                    1,
                    0,
                    head.get_sort_key(True),
                    tuple(
                        chain(
                            (element.get_sort_key(True) for element in self._elements),
                            ((4,),),
                        )
                    ),
                    1,
                )
        else:
            """
            General sort key structure:
            0: 1/2:        Numeric / General Expression
            1: 2/3         Special arithmetic (Times / Power) / General Expression
            2: Element:        Head
            3: tuple:        list of Elements
            4: 1:        No clue...
            """
            exps: Dict[str, Union[float, complex]] = {}
            head = self._head
            if head is SymbolTimes:
                for element in self.elements:
                    name = element.get_name()
                    if element.has_form("Power", 2):
                        var = element.get_element(0).get_name()
                        expr = element.get_element(1)
                        assert isinstance(expr, (Expression, NumericOperators))
                        exp = expr.round_to_float()
                        if var and exp is not None:
                            exps[var] = exps.get(var, 0) + exp
                    elif name:
                        exps[name] = exps.get(name, 0) + 1
            elif self.has_form("Power", 2):
                var = self.elements[0].get_name()
                # TODO: Check if this is the expected behaviour.
                # round_to_float is an attribute of Expression,
                # but not for Atoms.
                try:
                    exp = self.elements[1].round_to_float()
                except AttributeError:
                    exp = None
                if var and exp is not None:
                    exps[var] = exps.get(var, 0) + exp
            if exps:
                return (
                    1 if self.is_numeric() else 2,
                    2,
                    Monomial(exps),
                    1,
                    head,
                    self._elements,
                    1,
                )
            else:
                return (
                    1 if self.is_numeric() else 2,
                    3,
                    head,
                    len(self._elements),
                    self._elements,
                    1,
                )

    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, value):
        raise ValueError("Expression.head is write protected.")

    @property
    def is_literal(self) -> bool:
        """
        True if the value doesn't change after evaluation, i.e. a
        value is set and it does not depend on definition
        bindings. That is why, in contrast to
        `is_uncertain_final_definitions()` we don't need a
        `definitions` parameter.
        """
        # Right now we are pessimistic. We might consider changing this for
        # Lists. Lists definitions can't be changed right?
        return False
        # If we have a List we may do something like:
        # return self._elements_fully_evaluated

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
            assert cache is not None

        return definitions.is_uncertain_final_value(time, cache.symbols)

    def has_form(
        self, heads: Union[Sequence[str], str], *element_counts: Optional[int]
    ) -> bool:
        """
        element_counts:
            (,):        no elements allowed
            (None,):    no constraint on number of elements
            (n, None):  element count >= n
            (n1, n2, ...):    element count in {n1, n2, ...}
        """

        head_name = self._head.get_name()

        if isinstance(heads, (tuple, list, set)):
            if head_name not in [ensure_context(h) for h in heads]:
                return False
        elif isinstance(heads, str):
            if head_name != ensure_context(heads):
                return False
        else:
            raise TypeError(
                f"Heads must be a string or a sequence of strings, not {type(heads)}"
            )
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

    def has_symbol(self, symbol_name: str) -> bool:
        """
        Return True if the expression contains ``symbol_name`` in its head or
        any of its elements.

        One place where we want to check for symbols is in to
        determine whether an Expression cache needs to be
        invalidated. Another place is in Series expansion.

        Note that head in an M-Expression can be an expression.
        Derivative and Series are like this.
        """
        if self._does_not_contain_symbol(symbol_name) or not hasattr(
            self._head, "has_symbol"
        ):
            return False
        return self._head.has_symbol(symbol_name) or any(
            element.has_symbol(symbol_name)
            for element in self._elements
            if hasattr(element, "has_symbol")
        )

    def restructure(self, head, elements, evaluation, structure_cache=None, deps=None):
        """Faster equivalent of: ``Expression(head, *elements)``

        The caller guarantees that _all_ elements are either from
        self.elements (or its subtrees) or from one of the expression given
        in the tuple "deps" (or its subtrees).

        If this method is called repeatedly, and the caller guarantees
        that no definitions change between subsequent calls, then heads_cache
        may be passed an initially empty dict to speed up calls.
        """

        if deps is None:
            deps = self
        if structure_cache is None:
            structure_cache = {}

        # FIXME: look over
        s = structure(head, deps, evaluation, structure_cache=structure_cache)
        return s(list(elements))

    @trace_evaluate
    def rewrite_apply_eval_step(self, evaluation) -> Tuple[BaseElement, bool]:
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

        # Step 1 : evaluate the Head and get its Attributes. These attributes,
        # used later, include: HoldFirst / HoldAll / HoldRest / HoldAllComplete.

        # Note: self._head can be not just a symbol, but some arbitrary expression.
        # This is what makes expressions in Mathics3 be M-expressions rather than
        # S-expressions.
        head = self._head
        if isinstance(head, EvalMixin):
            result = head.evaluate(evaluation)
            if result is not None:
                head = result

        attributes = head.get_attributes(evaluation.definitions)

        if self.elements_properties is None:
            self._build_elements_properties()
            assert self.elements_properties is not None

        recompute_properties = False

        # @timeit
        def eval_elements():
            # @timeit
            def eval_range(indices):
                nonlocal recompute_properties
                recompute_properties = False
                for index in indices:
                    element = elements[index]
                    if not (element.is_literal or element.has_form("Unevaluated", 1)):
                        if isinstance(element, EvalMixin):
                            new_value = element.evaluate(evaluation)
                            # We need id() because != by itself is too permissive
                            if id(element) != id(new_value):
                                recompute_properties = True
                                elements[index] = new_value

            # @timeit
            def rest_range(indices):
                nonlocal recompute_properties
                if not A_HOLD_ALL_COMPLETE & attributes:
                    if self._does_not_contain_symbol("System`Evaluate"):
                        return
                    for index in indices:
                        element = elements[index]
                        if not element.is_literal and element.has_form("Evaluate", 1):
                            if isinstance(element, EvalMixin):
                                new_value = element.evaluate(evaluation)
                                # We need id() because != by itself is too permissive
                                if id(new_value) != id(element):
                                    elements[index] = new_value
                                    recompute_properties = True

            if (A_HOLD_ALL | A_HOLD_ALL_COMPLETE) & attributes:
                # eval_range(range(0, 0))
                rest_range(range(len(elements)))
            elif A_HOLD_FIRST & attributes:
                rest_range(range(0, min(1, len(elements))))
                eval_range(range(1, len(elements)))
            elif A_HOLD_REST & attributes:
                eval_range(range(0, min(1, len(elements))))
                rest_range(range(1, len(elements)))
            else:
                eval_range(range(len(elements)))
                # rest_range(range(0, 0))

        # Step 2: Build a new expression. If it can be avoided, we take care not
        # to:
        # * evaluate elements,
        # * run to_python() on them in Expression construction, or
        # * convert Expression elements from a tuple to a list and back
        elements: Sequence[BaseElement]
        if self.elements_properties.elements_fully_evaluated:
            elements = self._elements
        else:
            elements = self.get_mutable_elements()
            # FIXME: see if we can preserve elements properties in eval_elements()
            eval_elements()

        if recompute_properties:
            new = Expression(head, *elements, elements_properties=None)
            new._build_elements_properties()
        else:
            new = Expression(
                head, *elements, elements_properties=self.elements_properties
            )

        if hasattr(self, "location") and self.location is not None:
            new.location = self.location

        # Step 3: Now, process the attributes of head
        # If there are sequence, flatten them if the attributes allow it.
        if (
            new.elements_properties is not None
            and not new.elements_properties.is_flat
            and not (A_SEQUENCE_HOLD | A_HOLD_ALL_COMPLETE) & attributes
        ):
            # This step is applied to most of the expressions
            # and could be heavy for expressions with many elements (like long lists)
            # however, most of the times, expressions does not have `Sequence` expressions
            # inside. Now this is handled by caching the sequences.
            new = new.flatten_sequence(evaluation)
            if new.elements_properties is None:
                new._build_elements_properties()
            elements = new._elements

        # comment @mmatera: I think this is wrong now, because alters
        # singletons... (see PR #58) The idea is to mark which elements was
        # marked as "Unevaluated" Also, this consumes time for long lists, and
        # is useful just for a very unfrequent expressions, involving
        # `Unevaluated` elements.  Notice also that this behaviour is broken
        # when the argument of "Unevaluated" is a symbol (see comment and tests
        # in test/test_unevaluate.py)

        for element in elements:
            element.unevaluated = False

        # If HoldAllComplete Attribute (flag ``A_HOLD_ALL_COMPLETE``) is not set,
        # and the expression has elements of the form  `Unevaluated[element]`
        # change them to `element` and set a flag `unevaluated=True`
        # If the evaluation fails, use this flag to restore back the initial form
        # Unevaluated[element]

        # comment @mmatera:
        # what we need here is some way to track which elements are marked as
        # Unevaluated, that propagates by flatten, and at the end,
        # to recover a list of positions that (eventually)
        # must be marked again as Unevaluated.

        if not A_HOLD_ALL_COMPLETE & attributes:
            dirty_elements = None

            for index, element in enumerate(elements):
                if element.has_form("Unevaluated", 1):
                    if dirty_elements is None:
                        dirty_elements = list(elements)
                    dirty_elements[index] = element.get_element(0)
                    dirty_elements[index].unevaluated = True

            if dirty_elements:
                new = Expression(head, *dirty_elements)
                elements = dirty_elements
                new._build_elements_properties()

        # If the Attribute ``Flat`` (flag ``A_FLAT``) is set, calls
        # flatten with a callback that set elements as unevaluated
        # too.
        def flatten_callback(new_elements, old):
            for element in new_elements:
                element.unevaluated = old.unevaluated

        if A_FLAT & attributes:
            assert isinstance(new._head, Symbol)
            new = new.flatten_with_respect_to_head(new._head, callback=flatten_callback)
            if new.elements_properties is None:
                new._build_elements_properties()

        # If the attribute ``Orderless`` is set, sort the elements, according to the
        # element's ``get_sort_key()`` method.
        # Sorting can be time consuming which is why we note this in ``elements_properties``.
        # Checking for sortedness takes O(n) while sorting take O(n log n).
        if (
            new.elements_properties is not None
            and not new.elements_properties.is_ordered
            and (A_ORDERLESS & attributes)
        ):
            new.sort()

        # Step 4:  Rebuild the ExpressionCache, which tracks which symbols
        # where involved, the Sequence`s present, and the last time they have changed.

        new._timestamp_cache(evaluation)

        # Step 5: Must we need to thread-rewrite the expression?
        #
        # Threading is needed when head has the ``Listable``
        # Attribute (or flag ``A_LISTABLE``).
        # ``Expression.thread`` rewrites the expression:
        #  ``F[{a,b,c,...}]`` as:
        #  ``{F[a], F[b], F[c], ...}``.

        # Note: Threading here is different from Python or OS threads,
        # even though the intent of this attribute was to allow for
        # hardware threading to make use of more cores.
        #
        # Right now, we do not make use of Python thread or hardware
        # threading.  Still, we need to perform this rewrite to
        # maintain correct semantic behavior.
        if A_LISTABLE & attributes:
            done, threaded = new.thread(evaluation)
            if done:
                if threaded.sameQ(new):
                    new._timestamp_cache(evaluation)
                    return new, False
                else:
                    return threaded, True

        # Step 6:
        # Look at the rules associated with:
        #   1. the upvalues of each element
        #   2. the downvalues / subvalues associated with the lookup_name
        #      when the lookup values matches or is not the head.
        #
        # For example, consider expression: F[a, 1, b, a]
        #
        # First look for upvalue rules associated with "a".
        #   If a rule is found, try to apply the corresponding rule.
        #      If that succeeds, (the result is not None) then
        #      return the result. It will be reevaluated when "reevaluate" is True and
        #      the result changes from the input, and is an EvalMixin type.
        #
        # If the rule fails, continue with the next element.
        #
        # The next element, "1", is a number; it does not have upvalues. So skip
        # that and looking at upvalues of "b".
        # If rule matching does not succeed for "b", then look at the next element,
        # "a". However element "a" has been already seen. So, skip it.
        # Finally, because "F" is a symbol,
        # new.head_name() == new.get_lookup_name(); look at downvalue rules.

        # If instead of "F[a, 1, a, c]" we had  "Q[s][a, 1, a, c]",
        # the routine would look for the subvalues of "Q".
        #
        # For "Plus" and "Times", WMA behaves slightly different for numbers.
        # For example consider:
        # ```
        # Unprotect[Plus];
        # Plus[2,3]:=fish;
        # Plus[2,3]
        # ```
        # In Mathics3, the result in  "fish", but WL gives "5".
        # This shows that WMA evaluates certain symbols differently.

        def rules():
            rules_names = set()
            if not A_HOLD_ALL_COMPLETE & attributes:
                for element in elements:
                    if not isinstance(element, EvalMixin):
                        continue
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
            try:
                result = rule.apply(new, evaluation, fully=False)
            except OverflowError:
                evaluation.message("General", "ovfl")
                return Expression(SymbolOverflow), False
            if result is not None:
                if not isinstance(result, EvalMixin):
                    return result, False
                if result.sameQ(new):
                    new._timestamp_cache(evaluation)
                    return new, False
                else:
                    return result, True

        # Step 7: If we are here, is because we didn't find any rule that
        # matches the expression.

        dirty_elements = None

        # Expression did not change, re-apply Unevaluated
        for index, element in enumerate(new._elements):
            if element.unevaluated:
                if dirty_elements is None:
                    dirty_elements = list(new._elements)
                dirty_elements[index] = Expression(SymbolUnevaluated, element)

        if dirty_elements:
            new = Expression(head)
            new.elements = dirty_elements

        # Step 8: Update the cache. Return the new compound Expression and
        #        indicate that no further evaluation is needed.
        new._timestamp_cache(evaluation)
        return new, False

    #  Now, let's see how much take each step for certain typical expressions:
    #  (assuming that "F" and "a1", ... "a100" are undefined symbols, and
    #  n0->0, n1->1,..., n99->99)
    #
    #  Expr1: to_expression("F", 1)                       (trivial evaluation to a short expression)
    #  Expr2: to_expression("F", 0, 1, 2, .... 99)        (trivial evaluation to a long expression, with just numbers)
    #  Expr3: to_expression("F", a0, a2, ...., a99)       (trivial evaluation to a long expression, with just undefined symbols)
    #  Expr4: to_expresion("F", n0, n2, ...., n99)       (trivial evaluation to a long expression, with just undefined symbols)
    #  Expr5: to_expression("Plus", 99,..., 0)            (nontrivial evaluation to a long expression, with just undefined symbols)
    #  Expr6: to_expression("Plus", a99,..., a0)          (nontrivial evaluation to a long expression, with just undefined symbols)
    #  Expr7: to_expression("Plus", n99,..., n0)          (nontrivial evaluation to a long expression, with just undefined symbols)
    #  Expr8: to_expression("Plus", n1,..., n1)           (nontrivial evaluation to a long expression, with just undefined symbols)
    #

    def round_to_float(
        self, evaluation=None, permit_complex=False
    ) -> Optional[Union[float, complex]]:
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
        """Mathics3 SameQ"""
        if not isinstance(other, Expression):
            return False
        if self is other:
            return True

        # All this stuff maybe should be in mathics.eval.expression
        return eval_SameQ(self, other)

    def sequences(self):
        cache = self._cache
        if cache:
            seq = cache.sequences
            if seq is not None:
                return seq

        return self._rebuild_cache().sequences

    def set_head(self, head: Symbol):
        """
        Change the Head of a ListExpression.
        Unless this is a ListExpression, this is forbidden here.
        """
        if head is SymbolList:
            raise TypeError("Attempt to turn an Expression into a ListExpression")
        self._head = head
        self._cache = None

    def set_element(self, index: int, value):
        """
        Update element[i] with value
        """
        elements = list(self._elements)
        elements[index] = value
        self.elements = tuple(elements)
        self._cache = None

    def shallow_copy(self) -> "Expression":
        # this is a minimal, shallow copy: head, elements are shared with
        # the original, only the Expression instance is new.

        expr = Expression(
            self._head, *self._elements, elements_properties=self.elements_properties
        )

        # rebuilding the cache in self speeds up large operations, e.g.
        # First[Timing[Fold[#1+#2&, Range[750]]]]
        expr._cache = self._rebuild_cache()
        expr.options = self.options
        # expr.last_evaluated = self.last_evaluated
        return expr

    def slice(self, head, py_slice, evaluation):
        # faster equivalent to: Expression(head, *self.elements[py_slice])
        return structure(head, self, evaluation).slice(self, py_slice)

    def to_mpmath(self):
        return None

    def to_python(self, *args, **kwargs) -> Any:
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
        from mathics.core.builtin import mathics_to_python

        # When self.value of is None, it might mean either it is
        # not set or it is legitamately the None value.
        # If self.value is legitimately None, we'll
        # catch further down.
        if hasattr(self, "value") and self.value is not None:
            return self.value

        n_evaluation = kwargs.get("n_evaluation", None)
        assert n_evaluation is None

        head = self._head
        if head is SymbolFunction:
            from mathics.core.convert.function import expression_to_callable_and_args

            vars, expr_fn = self.elements
            return expression_to_callable_and_args(expr_fn, vars, n_evaluation)

        if n_evaluation is not None:
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

        # Notice that in this case, `to_python` returns a Mathics3 Expression object,
        # instead of a builtin native object.
        return self

    def to_sympy(self, **kwargs):
        from mathics.core.convert.sympy import expression_to_sympy

        return expression_to_sympy(self, **kwargs)

    def process_style_box(self, options):
        if self.has_form("StyleBox", 1, None):
            rules = self._elements[1:]
            for rule in rules:
                if rule.has_form("Rule", 2):
                    name = rule._elements[0].get_name()
                    value = rule._elements[1]
                    if name == "System`ShowStringCharacters":
                        value = value is SymbolTrue
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
        # There is no in-place sort method on a tuple, because tuples are not
        # mutable. So we turn into a elements into list and use Python's
        # list sort method. Another approach would be to use sorted().
        elements = self.get_mutable_elements()
        if pattern:
            elements.sort(key=lambda e: e.get_sort_key(pattern_sort=True))
        else:
            elements.sort()

        # update `self._elements` and self._cache with the possible permuted order.
        self.elements = elements
        self._build_elements_properties()

        if self._cache:
            self._cache = self._cache.reordered()

    def do_apply_rules(self, rules, evaluation, level=0, options=None):
        """
        .. code-block:: python

            for rule in rules:
                result = rule.apply(self, evaluation, fully=False)
                if result is not None:
                    return result
        """
        from mathics.core.convert.expression import to_expression_with_specialization

        # to be able to access it inside inner function
        new_applied = [False]

        def apply_element(element):
            new, sub_applied = element.do_apply_rules(
                rules, evaluation, level + 1, options
            )
            new_applied[0] = new_applied[0] or sub_applied
            return new

        def descend(expr):
            return to_expression_with_specialization(
                expr.head, *[apply_element(element) for element in expr._elements]
            )

        if options is None:  # default ReplaceAll mode; replace breadth first
            result, applied = super().do_apply_rules(rules, evaluation, level, options)
            if applied:
                return result, True
            head, applied = self._head.do_apply_rules(rules, evaluation, level, options)
            new_applied[0] = applied
            return descend(Expression(head, *self._elements)), new_applied[0]
        else:  # Replace mode; replace depth first
            expr = descend(self)
            expr, applied = super(Expression, expr).do_apply_rules(
                rules, evaluation, level, options
            )
            new_applied[0] = new_applied[0] or applied
            if not applied and options["heads"]:
                # heads in Replace are treated at the level of the arguments,
                # i.e. level + 1
                head, applied = expr._head.do_apply_rules(
                    rules, evaluation, level + 1, options
                )
                new_applied[0] = new_applied[0] or applied
                expr = Expression(head, *expr._elements)
            return expr, new_applied[0]

    def replace_vars(
        self, vars, options=None, in_scoping=True, in_function=True
    ) -> "Expression":
        """
        Replace the symbols in the expression by the expressions given
        in the vars dictionary.

        in_scoping: if `False`, do not replace those symbols that are
                    declared internal to the scope.

        in_function: if `True`, and the Expression is of the form Function[{args},body],
                     change the names of the args instead of replacing them.
        """
        from mathics.builtin.scoping import get_scoping_vars
        from mathics.core.list import ListExpression

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
                        element.get_name()
                        for element in self._elements[0].get_elements()
                    ]
                if "" not in func_params:
                    body = self._elements[1]
                    body = body.replace_vars(
                        {name: Symbol(name + "$") for name in func_params},
                        options,
                        in_scoping,
                    )
                    elements = tuple(
                        chain(
                            [
                                ListExpression(
                                    *[Symbol(name + "$") for name in func_params]
                                ),
                                body,
                            ],
                            self._elements[2:],
                        )
                    )

        if not vars:  # might just be a symbol set via Set[] we looked up here
            return self.shallow_copy()

        return Expression(
            self._head.replace_vars(vars, options=options, in_scoping=in_scoping),
            *[
                element.replace_vars(vars, options=options, in_scoping=in_scoping)
                for element in elements
            ],
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
            *[element.replace_slots(slots, evaluation) for element in self._elements],
        )

    def thread(self, evaluation, head=None) -> Tuple[bool, "Expression"]:
        """
        Thread over expressions with head as Head:
        Thread[F[{a,b},{c,d}, G[z,q]],G] -> newexpr = G[F[{a, b}, {c, d}, z], F[{a, b}, {c, d}, q]]

        By default, head=SymbolList

        If the expression has changes, returns True, newexpr
        otherwise, return False, self
        """
        if head is None:
            head = SymbolList

        prefix: List[BaseElement] = []
        items: List[List[BaseElement]]
        dim = None
        for element in self._elements:
            if element.get_head().sameQ(head):
                if dim is None:
                    dim = len(element.get_elements())
                    items = [
                        (prefix + [innerelement])
                        for innerelement in element.get_elements()
                    ]
                elif len(element._elements) != dim:
                    evaluation.message("Thread", "tdlen")
                    return True, self
                else:
                    for index in range(dim):
                        items[index].append(element._elements[index])
            else:
                if dim is None:
                    prefix.append(element)
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
            if not A_NUMERIC_FUNCTION & evaluation.definitions.get_attributes(
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

    def user_hash(self, update):
        update(("%s>%d>" % (self.get_head_name(), len(self._elements))).encode("utf8"))
        for element in self._elements:
            element.user_hash(update)


def _create_expression(self, head: BaseElement, *elements: BaseElement) -> Expression:
    return Expression(head, *elements)


BaseElement.create_expression = _create_expression


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

    try:
        definition = definitions.get_definition(symbol_name, only_if_exists=True)
        r = all(
            len(definition.get_values_list(x)) == 0
            for x in ("upvalues", "subvalues", "downvalues", "ownvalues")
        )
        if cache:
            cache[symbol_name] = r
        return r
    except KeyError:
        cache[symbol_name] = True
        return True


def _is_neutral_head(head, cache, evaluation):
    if not isinstance(head, Symbol):
        return False

    return _is_neutral_symbol(head.get_name(), cache, evaluation)


def structure(head, origins, evaluation, structure_cache={}):
    """
    Creates a Structure for building Expressions with head "head" and elements
    originating (exclusively) from "origins" (elements are passed into the functions
    of Structure further down).

    "origins" may either be an Expression (i.e. all elements must originate from that
    expression), a Structure (all elements passed in this "self" Structure must be
    manufactured using that Structure), or a list of Expressions (i.e. all elements
    must originate from one of the listed Expressions).
    """
    from mathics.core.structure import Structure, UnlinkedStructure

    if isinstance(head, (str,)):
        head = Symbol(head)

    if isinstance(origins, (Expression, Structure)):
        cache = origins._cache
        if cache and not _is_neutral_head(head, structure_cache, evaluation):
            cache = {}
    elif isinstance(origins, (list, tuple)):
        if _is_neutral_head(head, structure_cache, evaluation):
            cache = ExpressionCache.union(origins, evaluation)
        else:
            cache = {}
    else:
        raise ValueError("expected Expression, Structure, tuple or list as orig param")

    if cache:
        return LinkedStructure(head, cache)
    else:
        return UnlinkedStructure(head)


def atom_list_constructor(evaluation, head, *atom_names):
    # If we encounter an Expression that consists wholly of atoms and those
    # atoms (and the expression's head) have no rules associated with them, we
    # can speed up evaluation.

    # Note that you may use a constructor constructed via
    # atom_list_constructor() only as long as the evaluation's Definitions are
    # guaranteed to not change.

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
            expr.elements = list(elements)
            sym = set(chain([head.get_name()], full_atom_names))
            expr._cache = ExpressionCache(evaluation.definitions.now, sym, None)
            return expr

    else:

        def construct(elements):
            expr = Expression(head)
            expr.elements = list(elements)
            return expr

    return construct


# Note: this function is called a *lot* so it needs to be fast.
def convert_expression_elements(
    elements: Iterable, conversion_fn: Callable = from_python
) -> Tuple[tuple, ElementsProperties, Optional[tuple]]:
    """
    Convert and return tuple of Elements from the Python-like items in
    `elements`, along with elements properties of the elements tuple,
    and a tuple of literal values if it elements are all literal
    otherwise, None.

    The return information is suitable for use to the Expression() constructor.

    """

    # All of the properties start out optimistic (True) and are reset when that
    # proves wrong.
    elements_properties = ElementsProperties(True, True, True)

    is_literal = True
    values = []  # If is_literal, "values" contains the (Python) literal values

    result = []
    last_converted_elt = None
    for element in elements:
        converted_elt = conversion_fn(element)

        # Test for the three properties mentioned above and literalness.
        if is_literal and converted_elt.is_literal:
            values.append(converted_elt.value)
        else:
            elements_properties.elements_fully_evaluated = False
            is_literal = False

        if isinstance(converted_elt, Expression):
            elements_properties.is_flat = False
            if converted_elt.elements_properties is None:
                converted_elt._build_elements_properties()
                assert converted_elt.elements_properties is not None

            if elements_properties.elements_fully_evaluated:
                elements_properties.elements_fully_evaluated = (
                    converted_elt.elements_properties.elements_fully_evaluated
                )

        if elements_properties.is_ordered and last_converted_elt is not None:
            try:
                elements_properties.is_ordered = last_converted_elt <= converted_elt
            except Exception:
                elements_properties.is_ordered = False
        last_converted_elt = converted_elt
        result.append(converted_elt)

    final_values = tuple(values) if is_literal else None
    return tuple(result), elements_properties, final_values


def string_list(head, elements, evaluation):
    return atom_list_constructor(evaluation, head, "String")(elements)


ExpressionInfinity = Expression(SymbolDirectedInfinity, Integer1)
