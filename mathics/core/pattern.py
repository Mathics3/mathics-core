# cython: language_level=3
# cython: profile=False
# -*- coding: utf-8 -*-
"""Core to Mathics3 are patterns which match symbolic expressions. Patterns
are built up in a custom pattern notation.
The parts of a pattern are called "Pattern Objects".

While there is a built-in function which allows users to match parts of
expressions, patterns are also used in applying transformation
rules and deciding functions that get applied.

See also: mathics.core.rules and
https://reference.wolfram.com/language/tutorial/PatternsAndTransformationRules.html
"""


from abc import ABC
from functools import cached_property
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    overload,
)

from mathics.core.atoms import Integer
from mathics.core.attributes import A_FLAT, A_ONE_IDENTITY, A_ORDERLESS
from mathics.core.element import BaseElement, ensure_context
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.interrupt import TimeoutInterrupt
from mathics.core.keycomparable import (
    BASIC_ATOM_PATTERN_SORT_KEY,
    BASIC_EXPRESSION_PATTERN_SORT_KEY,
    END_OF_LIST_PATTERN_SORT_KEY,
)
from mathics.core.symbols import Atom, Symbol, symbol_set
from mathics.core.systemsymbols import (
    SymbolAlternatives,
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolCondition,
    SymbolDefault,
    SymbolOptional,
    SymbolOptionsPattern,
    SymbolPattern,
    SymbolPatternTest,
    SymbolRepeated,
    SymbolRepeatedNull,
    SymbolSequence,
)
from mathics.core.util import permutations, subranges, subsets

if TYPE_CHECKING:
    from mathics.core.builtin import PatternObject

SYSTEM_SYMBOLS_PATTERNS = symbol_set(
    SymbolAlternatives,
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolCondition,
    SymbolOptional,
    SymbolOptionsPattern,
    SymbolPattern,
    SymbolPatternTest,
    SymbolRepeated,
    SymbolRepeatedNull,
)

pattern_objects: Dict[str, Type["PatternObject"]] = {}


class StopGenerator(Exception):
    """
    StopGenerator is the exception raised when
    an expression matches a pattern.
    The exception holds the attribute `value`
    that is used as a return value in `match`.
    """

    def __init__(self, value=None):
        self.value = value


class StopGenerator_ExpressionPattern_match(StopGenerator):
    """
    Exception raised when an ExpressionPattern matches
    an expression.
    """


class StopGenerator_Pattern(StopGenerator):
    """
    Exception raised when  BasePattern matches
    an expression.
    """


class BasePattern(ABC):
    """
    This is the base class for Mathics3 Pattern objects.

    A Pattern is a way to represent classes of expressions.
    For example, ``F[x_Symbol]`` is a pattern which matches an expression whose
    Head is ``F`` and that has a single parameter which is a kind of Symbol.
    When the pattern matches, the symbol is bound to the parameter ``x``.
    """

    expr: BaseElement

    # This attribute facilitates a faster match algorithm based on sameQ.
    isliteral: bool = False

    # TODO: In WMA, when a BasePattern is created, the attributes
    # from the head are read from the evaluation context and
    # stored as a part of a rule.
    #
    # As BasePatterns are nested structures, the factory not only needs
    # the attributes of the head, but also the full evaluation context
    # which is needed to create patterns for its elements.
    #
    #
    # For instance,  `rule=Times[c__, Plus[Q[a_],Q[b_]]]->Q[c*(a+b)]`
    # builds the pattern `Times[c__, Plus[Q[a_],Q[b_]]]`.
    # The constructor of the pattern then creates recursively
    #     `c__`
    #     `Plus[Q[a_],Q[b_]]`
    #         `Plus`
    #         `Q[a_]`
    #           `Q`
    #           `a_`
    #         `Q[b_]`
    #           `Q`
    #           `b_`
    #
    # Also, when the initial Definitions object for the evaluation
    # context is created, many rules must be created without an
    # evaluation context available. For that case, we still
    # must be able to create Pattern objects without the evaluation context.
    #
    # In any case, just by caching the attributes in the first use of
    # the pattern there is a win ~5% in performance.
    #
    # A better implementation would take into account the attributes
    # to specialize the match method.
    #
    #
    # Corner case: `Alternatives`
    # ===========================
    #
    # Notice also that the case of `Alternatives` is a corner case,
    # where attributes are read at the moment of the rule application:
    #
    # For example, in WMA, let's consider this example
    # ```
    #    In[1]:= SetAttributes[P,Orderless];
    #    In[2]:= rule=Alternatives[P,Q][_Integer,_Symbol]->True;
    # ```
    #
    # At this point, the rule `rule` was created. As the head of the pattern
    # is an expression, it does not provide special attributes to the pattern.
    # As expected, the pattern does not match with `Q[a, 1]` because the order of the
    # parameters:
    # ```
    #    In[3]:= Q[a, 1]/.rule
    #    Out[3]= Q[a, 1]
    # ```
    #
    # On the other hand, it does take into account the attributes of `P`:
    #
    # ```
    #    In[4]:= P[a, 1]/.rule
    #    Out[4]= True
    # ```
    # These attributes are not stored in the rule: if we remove the attribute
    # ```
    #    In[5]:= Attributes[P]={};
    # ```
    #
    # the attribute is not used anymore, and the rule application fails:
    #
    # ```
    #    In[6]:= P[a, 1]/.rule
    #    Out[6]= P[a, 1]
    # ``
    #
    #
    @staticmethod
    def create(
        expr: BaseElement,
        attributes: Optional[int] = None,
        evaluation: Optional[Evaluation] = None,
    ) -> "BasePattern":
        """
        If ``expr`` is listed in ``pattern_object``  return the pattern found there.
        Otherwise, if ``expr`` is an ``Atom``, create and return  ``AtomPattern`` for ``expr``.
        Otherwise, create and return and ``ExpressionPattern`` for ``expr``.
        """

        name = expr.get_head_name()
        pattern_object = pattern_objects.get(name)
        if pattern_object is not None:
            return pattern_object(expr, evaluation=evaluation)
        if isinstance(expr, Atom):
            return AtomPattern(expr, evaluation)
        if isinstance(expr, Expression):
            if attributes is not None:
                # Attributes already known directly -- pick the concrete
                # class immediately, no deferral needed.
                return make_expression_pattern(expr, attributes, evaluation)
            if evaluation is not None:
                # Attributes not given, but resolvable right now.
                resolved_attributes = expr.head.get_attributes(evaluation.definitions)
                return make_expression_pattern(expr, resolved_attributes, evaluation)
            # Neither known nor resolvable yet (e.g. system bootstrap,
            # before Definitions is fully populated) -- defer.
            return DeferredExpressionPattern(expr)
        raise TypeError(f"Cannot create Pattern for {expr}")

    def get_attributes(self, definitions):
        """The attributes of the expression"""
        return self.expr.get_attributes(definitions)

    def get_elements(self):
        """The elements of the expression."""
        return self.expr.get_elements()

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return self.expr.element_order

    def get_head(self):
        """The head of the expression"""
        return self.expr.get_head()

    def get_head_name(self):
        """
        Return the name of the symbol in head.
        If head is not a symbol, return "".
        """
        return self.expr.get_head_name()

    def get_lookup_name(self):
        """
        Return symbol name of leftmost head.
        """
        return self.expr.get_lookup_name()

    def get_name(self, short=False) -> str:
        """Return the name of the expression."""
        name = self.expr.get_name()
        return name.split("`")[-1] if short else name

    def get_option_values(
        self, evaluation: Evaluation, allow_symbols=False, stop_on_error=True
    ) -> Optional[dict]:
        """Option values of the expression"""
        return self.expr.get_option_values(evaluation, allow_symbols, stop_on_error)

    def get_sequence(self):
        """The sequence of elements in the expression"""
        return self.expr.get_sequence()

    def has_form(
        self, heads: Union[Sequence[str], str], *element_counts: Optional[int]
    ) -> bool:
        """Compare the expression against a form"""
        return self.expr.has_form(heads, *element_counts)

    def match(self, expression: BaseElement, pattern_context: dict):
        """
        Check if the expression matches the pattern (self).
        If it does, it calls `yield_func`.
        vars collects subexpressions associated with named subpatterns.
        head: Symbol. Provided by match_element, used by `Optional`.
        element_index: int,  the position
        element_count: int, the number of optional elements. Used by `Optional`
        for calling `get_default_value`.

        Note: this complexity would disappear if `Defaults` were stored as in WMA
        at the creation time of the object.

        fully is used in `match_element`, for the case of Orderless patterns.
        """
        raise NotImplementedError

    def does_match(self, expression: BaseElement, pattern_context: dict) -> bool:
        """returns True if `expression` matches self or we have
        reached the end of the matches, and False if it does not.
        """
        evaluation: Evaluation = pattern_context["evaluation"]
        vars_dict: Optional[dict] = pattern_context.setdefault("vars_dict", {})
        fully: bool = pattern_context.get("fully", True)

        # for sub_vars, rest in self.match(  # nopep8
        #    expression, vars, evaluation, fully=fully):
        #    return True

        def yield_match(sub_vars, rest):
            raise StopGenerator_Pattern(True)

        try:
            self.match(
                expression=expression,
                pattern_context={
                    "yield_func": yield_match,
                    "vars_dict": vars_dict,
                    "evaluation": evaluation,
                    "fully": fully,
                },
            )
        except StopGenerator_Pattern as exc:
            return exc.value
        return False

    def get_match_candidates(
        self, elements: Tuple[BaseElement], pattern_context: dict
    ) -> tuple:
        """
        Get a sub-tuple of elements that are candidates
        matching the pattern.

        Optional parameters provide information
        about the context where the elements and the
        patterns come from.
        """
        return tuple()

    def get_match_count(self, vars_dict: Optional[dict] = None) -> Tuple[int, int]:
        """Subclasses should override this to provide the actual computation."""
        raise NotImplementedError

    def get_match_candidates_count(
        self, elements: Tuple[BaseElement], pattern_context: dict
    ) -> Union[int, tuple]:
        """Return the number of candidates that match the pattern.
        Optimized for common patterns."""
        # Fast path for Blank, BlankSequence, BlankNullSequence
        if isinstance(self, AtomPattern):
            if self.atom.get_head() == SymbolBlank:
                return len(elements)
        elif isinstance(self, ExpressionPattern):
            head = self.expr.get_head()
            if head == SymbolBlankSequence:
                return len(elements)
            if head == SymbolBlankNullSequence:
                return len(elements) + 1
        # Fallback to generic
        return len(self.get_match_candidates(elements, pattern_context))

    @cached_property
    def pattern_precedence(self) -> tuple:
        """
        Return a precedence value, a tuple, which is used in selecting
        which pattern to select when several match.
        Cached per instance.
        """
        return self._build_pattern_sort_key()

    def _build_pattern_sort_key(self):
        raise NotImplementedError

    @overload
    def sameQ(self, other: "BasePattern") -> bool: ...

    @overload
    def sameQ(self, other: BaseElement) -> bool: ...

    def sameQ(self, other) -> bool:
        """Mathics3 SameQ"""
        if isinstance(other, BasePattern):
            return self.expr.sameQ(other.expr)
        return self.expr.sameQ(other)


class AtomPattern(BasePattern):
    """
    A pattern that matches with an atom.
    """

    # Atoms are always literals
    isliteral: bool = True

    def __init__(self, expr: Atom, evaluation: Optional[Evaluation] = None) -> None:
        self.expr = expr
        self.atom = expr
        if isinstance(expr, Symbol):
            self.match = self.match_symbol  # type: ignore[method-assign]
            self.get_match_candidates = self.get_match_symbol_candidates  # type: ignore[method-assign]

    def _build_pattern_sort_key(self) -> tuple:
        return BASIC_ATOM_PATTERN_SORT_KEY

    def __repr__(self):
        return f"<AtomPattern: {self.atom}>"

    def match_symbol(
        self,
        expression: BaseElement,
        pattern_context,
    ):
        """Match against a symbol"""
        assert isinstance(expression, BaseElement)
        if expression is self.atom:
            pattern_context["yield_func"](pattern_context["vars_dict"], None)

    def get_match_symbol_candidates(
        self, elements: tuple, pattern_context: dict
    ) -> tuple:
        """Find the sub-tuple of elements that matches the pattern"""
        return tuple((element for element in elements if element is self.atom))

    def match(self, expression: BaseElement, pattern_context: dict):
        """Try to match the pattern with the expression."""

        if isinstance(expression, Atom) and expression.sameQ(self.atom):
            # yield vars, None
            pattern_context["yield_func"](pattern_context["vars_dict"], None)

    def get_match_candidates(
        self, elements: Tuple[BaseElement], pattern_context: dict
    ) -> tuple:
        """
        Return a sub-tuple of elements that matches the pattern.
        """
        return tuple(
            (
                element
                for element in elements
                if (isinstance(element, Atom) and element.sameQ(self.atom))
            )
        )

    def get_match_count(self, vars_dict: Optional[dict] = None) -> Tuple[int, int]:
        """The number of matches"""
        return (1, 1)

    @property
    def element_order(self) -> tuple:
        """
        Return a tuple value that is used in ordering elements
        of an expression. The tuple is ultimately compared lexicographically.
        """
        return self.expr.element_order

    @property
    def short_name(self) -> str:
        return (
            self.atom.short_name if hasattr(self.atom, "short_name") else str(self.atom)
        )


class ExpressionPattern(BasePattern):
    """
    Pattern that matches with an Expression.
    """

    # get_pre_choices = pattern_nocython.get_pre_choices
    # match = pattern_nocython.match

    attributes: Optional[int] = None

    def __init__(
        self,
        expr: Expression,
        attributes: Optional[int] = None,
        evaluation: Optional[Evaluation] = None,
    ):
        self.expr = expr
        self.location = expr.location if hasattr(expr, "location") else None
        head = expr.head
        if attributes is None and evaluation:
            attributes = head.get_attributes(evaluation.definitions)
        self.head = BasePattern.create(head, evaluation=evaluation)
        self.elements = [
            BasePattern.create(element, evaluation=evaluation)
            for element in expr.elements
        ]
        self.__set_pattern_attributes__(attributes)

    def __set_pattern_attributes__(self, attributes):
        if attributes is None or self.attributes is not None:
            self.get_pre_choices = self._get_pre_choices
            return

        self.attributes = attributes
        if A_ORDERLESS & attributes:
            self.sort()
            self.get_pre_choices = get_pre_choices_orderless
        else:
            self.get_pre_choices = get_pre_choices_with_order
            if not (A_ONE_IDENTITY + A_FLAT) & attributes:
                self.isliteral = self.head.isliteral and all(
                    element.isliteral for element in self.elements
                )

    def _build_pattern_sort_key(self) -> tuple:
        return (
            BASIC_EXPRESSION_PATTERN_SORT_KEY,
            self.head.pattern_precedence,
            tuple(
                chain(
                    (element.pattern_precedence for element in self.elements),
                    (END_OF_LIST_PATTERN_SORT_KEY,),
                )
            ),
        )

    def match(self, expression: BaseElement, pattern_context: dict):
        """Try to match the pattern against an Expression"""
        from mathics.core.atoms.associations import Association

        evaluation = pattern_context["evaluation"]
        yield_func = pattern_context["yield_func"]
        vars_dict = pattern_context["vars_dict"]
        fully = pattern_context.get("fully", True)

        evaluation.check_stopped()
        if self.isliteral:
            if expression.sameQ(self.expr):
                # yield vars, None
                yield_func(vars_dict, None)
            return

        if self.attributes is None:
            self.__set_pattern_attributes__(
                self.head.get_attributes(evaluation.definitions)
            )
        assert self.attributes is not None
        attributes = self.attributes

        if not A_FLAT & attributes:
            fully = True

        # --- use mutation with undo instead of copy ---
        old_fully = pattern_context.get("fully")
        old_attributes = pattern_context.get("attributes")
        old_head = pattern_context.get("head")
        old_element_index = pattern_context.get("element_index")
        old_element_count = pattern_context.get("element_count")
        try:
            pattern_context["fully"] = fully
            pattern_context["attributes"] = attributes
            pattern_context["head"] = None
            pattern_context["element_index"] = None
            pattern_context["element_count"] = None

            if isinstance(expression, Association):
                # FIXME: Provide something like this?
                # try:
                #     basic_match_association(self, expression, parms)
                # except (StopGenerator_ExpressionPattern_match, TimeoutInterrupt):
                #     return
                expression = expression.expr

            if isinstance(expression, Expression):
                try:
                    basic_match_expression(self, expression, pattern_context)
                except (StopGenerator_ExpressionPattern_match, TimeoutInterrupt):
                    return

            if A_ONE_IDENTITY & attributes:
                match_expression_with_one_identity(self, expression, pattern_context)
        finally:
            # restore old values
            if old_fully is not None:
                pattern_context["fully"] = old_fully
            else:
                pattern_context.pop("fully", None)
            if old_attributes is not None:
                pattern_context["attributes"] = old_attributes
            else:
                pattern_context.pop("attributes", None)
            if old_head is not None:
                pattern_context["head"] = old_head
            else:
                pattern_context.pop("head", None)
            if old_element_index is not None:
                pattern_context["element_index"] = old_element_index
            else:
                pattern_context.pop("element_index", None)
            if old_element_count is not None:
                pattern_context["element_count"] = old_element_count
            else:
                pattern_context.pop("element_count", None)

    def _get_pre_choices(
        self, expression: Expression, yield_choice: Callable, pattern_context: dict
    ):
        """
        If not Orderless, call yield_choice with vars as the parameter.
        """
        attributes = pattern_context.get("attributes")
        assert isinstance(attributes, int)
        if A_ORDERLESS & attributes:
            get_pre_choices_orderless(self, expression, pattern_context)
        else:
            pattern_context["yield_choice"](pattern_context["vars_dict"])

    def filter_elements(self, head_name: str):
        """Filter the elements with a given head_name"""
        head_name = ensure_context(head_name)
        return [
            element for element in self.elements if element.get_head_name() == head_name
        ]

    def __repr__(self):
        return f"<ExpressionPattern: {self.expr}>"

    def get_wrappings(self, yield_func: Callable, items: Tuple, pattern_context: dict):
        """
        Get the possible wrappings

        If items has length 1, apply yield_func to the unique element.
        Otherwise, apply it to a sequence -- see `_yield_sequence_wrappings`,
        overridden per-class for the Ordered/Orderless split. Finally, if
        the expression is `Flat`, and the parameter `include_flattened`
        is `True`, apply yield_func to the expression with the head of the original
        expression applied to the original sequence.
        """
        if len(items) == 1:
            yield_func(items[0])
        else:
            max_count: Optional[int] = pattern_context["max_count"]
            expression: Expression = pattern_context["expression"]
            attributes: int = pattern_context["attributes"]
            include_flattened: bool = pattern_context.get("include_flattened", True)
            if max_count is None or len(items) <= max_count:
                self._yield_sequence_wrappings(items, yield_func)
            # TODO: check if this should not be applied to each possible
            # orders if A_ORDERLESS.
            if A_FLAT & attributes and include_flattened:
                yield_func(Expression(expression.get_head(), *items))

    def _yield_sequence_wrappings(self, items: Tuple, yield_func: Callable):
        """
        Default (non-Orderless) case: a single Sequence[...] wrapping in
        the given, fixed order. OrderlessExpressionPattern overrides this
        to yield one Sequence[...] per permutation of `items` instead.

        This is only ever invoked on a concrete OrderedExpressionPattern
        or OrderlessExpressionPattern instance (see the module-level note
        on the Ordered/Orderless class split): BasePattern.create() never
        constructs a plain ExpressionPattern directly, so this base
        implementation effectively serves as the Ordered case's body.
        """
        sequence = Expression(SymbolSequence, *items)
        sequence.pattern_sequence = True
        yield_func(sequence)

    def match_element(
        self,
        element: BasePattern,
        pattern_context,
    ):
        """Try to match an element."""
        attributes: int = pattern_context["attributes"]
        evaluation: Evaluation = pattern_context["evaluation"]
        expression: BaseElement = pattern_context["expression"]
        first: bool = pattern_context.setdefault("first", False)
        fully: bool = pattern_context.setdefault("fully", True)
        vars_dict: dict = pattern_context["vars_dict"]
        rest_expression: tuple = pattern_context["rest_expression"]
        rest_elements: tuple = pattern_context["rest_elements"]
        if rest_expression is None:
            rest_expression = ([], [])

        evaluation.check_stopped()

        match_count = element.get_match_count(vars_dict)
        element_candidates = element.get_match_candidates(
            tuple(rest_expression[1]), pattern_context  # element.candidates,
        )

        if len(element_candidates) < match_count[0]:
            return

        candidates = tuple(rest_expression[1])

        # "Artificially" only use more elements than specified for some kind
        # of pattern.
        # TODO: This could be further optimized!
        try_flattened = A_FLAT & attributes and (
            element.get_head() in SYSTEM_SYMBOLS_PATTERNS
        )

        set_lengths: Tuple[int, Optional[int]]
        if try_flattened:
            set_lengths = (match_count[0], None)
        else:
            set_lengths = match_count

        # try_flattened is used later to decide whether wrapping of elements
        # into one operand may occur.
        # This can of course also be when flat and same head.
        try_flattened = try_flattened or (
            A_FLAT & attributes and element.get_head() == expression.get_head()
        )

        less_first = len(rest_elements) > 0

        def _regular_sets():
            return self._regular_match_element_sets(
                element,
                rest_elements,
                candidates,
                element_candidates,
                set_lengths,
                less_first,
                pattern_context,
            )

        options_sets = _options_pattern_split(element, rest_elements, candidates)
        if options_sets is not None:
            # Try the WMA-consistent OptionsPattern[] split first (see
            # _options_pattern_split), but keep the regular search
            # available right behind it as a lazy fallback: if the
            # preferred split doesn't lead anywhere (e.g. a later,
            # non-OptionsPattern element actually needed one of the
            # candidates this element would otherwise have skipped),
            # backtracking continues into the regular search exactly as
            # if this fast path didn't exist. Since matches short-circuit
            # via StopGenerator on first full success, this fallback is
            # never even evaluated in the common (successful) case --
            # itertools.chain doesn't touch _regular_sets() until the
            # first iterable is exhausted.
            sets = chain(options_sets, _regular_sets())
        else:
            sets = _regular_sets()

        # --- avoid copy of pattern_context: mutate and undo ---
        old_depth = pattern_context.get("depth", 1)
        old_next_index = pattern_context.get("next_index", 1)
        old_try_flattened = pattern_context.get("try_flattened")
        old_match_count = pattern_context.get("match_count")
        old_element = pattern_context.get("element")
        old_pattern = pattern_context.get("pattern")
        old_element_index = pattern_context.get("element_index")
        try:
            pattern_context["depth"] = old_depth + 1
            pattern_context["next_index"] = old_next_index + 1
            pattern_context["try_flattened"] = try_flattened
            pattern_context["match_count"] = match_count
            pattern_context["element"] = element
            pattern_context["pattern"] = self
            if "element_index" not in pattern_context:
                pattern_context["element_index"] = 0

            if rest_elements:
                pattern_context["next_element"] = rest_elements[0]
                pattern_context["next_rest_elements"] = rest_elements[1:]

            for items, items_rest in sets:
                expression_pattern_match_element_process_items(
                    items, items_rest, pattern_context
                )
        finally:
            pattern_context["depth"] = old_depth
            pattern_context["next_index"] = old_next_index

            if old_try_flattened is not None:
                pattern_context["try_flattened"] = old_try_flattened
            else:
                pattern_context.pop("try_flattened", None)
            if old_match_count is not None:
                pattern_context["match_count"] = old_match_count
            else:
                pattern_context.pop("match_count", None)
            if old_element is not None:
                pattern_context["element"] = old_element
            else:
                pattern_context.pop("element", None)
            if old_pattern is not None:
                pattern_context["pattern"] = old_pattern
            else:
                pattern_context.pop("pattern", None)
            if old_element_index is not None:
                pattern_context["element_index"] = old_element_index
            else:
                pattern_context.pop("element_index", None)
            pattern_context.pop("next_element", None)
            pattern_context.pop("next_rest_elements", None)

    def _regular_match_element_sets(
        self,
        element: "BasePattern",
        rest_elements: tuple,
        candidates: tuple,
        element_candidates: Union[tuple, set],
        set_lengths: Tuple[int, Optional[int]],
        less_first: bool,
        pattern_context: dict,
    ):
        """
        Default (non-Orderless) search for match_element's `sets`: the
        literal-lookahead fast path (see `_leading_literal_split_points`)
        when it applies, falling back to the general subranges()-based
        search otherwise. OrderlessExpressionPattern overrides this with
        `expression_pattern_match_element_orderless` instead -- the
        literal fast path assumes a fixed left-to-right element order,
        which Orderless doesn't have.

        This is only ever invoked on a concrete OrderedExpressionPattern
        or OrderlessExpressionPattern instance -- see the module-level
        note on the Ordered/Orderless class split.
        """
        first: bool = pattern_context.get("first", False)
        fully: bool = pattern_context.get("fully", True)
        evaluation: Evaluation = pattern_context["evaluation"]
        vars_dict: dict = pattern_context["vars_dict"]

        if (
            not (first and not fully)
            and (
                literal_split_points := _leading_literal_split_points(
                    element,
                    rest_elements,
                    candidates,
                    set_lengths,
                    evaluation,
                    vars_dict,
                )
            )
            is not None
        ):
            # Fast path: current element is an unconstrained
            # BlankSequence/BlankNullSequence immediately followed by
            # a literal, so only try lengths that place the literal
            # right after the block -- see _leading_literal_split_points
            # for why every other length is guaranteed to fail anyway.
            ordered_points = (
                literal_split_points
                if less_first
                else list(reversed(literal_split_points))
            )
            return ((candidates[:p], ([], candidates[p:])) for p in ordered_points)
        # a generator that yields partitions of
        # candidates as [before | block | after ]
        return subranges(
            candidates,
            *set_lengths,
            flexible_start=(first and not fully),
            included=element_candidates,
            less_first=less_first,
        )

    def get_match_candidates(
        self, elements: Tuple[BaseElement], pattern_context
    ) -> tuple:
        """
        Finds possible elements that could match the pattern, ignoring future
        pattern variable definitions, but taking into account already fixed
        variables.
        """
        # TODO: fixed_vars!
        evaluation: Evaluation = pattern_context["evaluation"]
        vars_dict: Optional[dict] = pattern_context.setdefault("vars_dict", {})
        return tuple(
            (
                element
                for element in elements
                if self.does_match(
                    element, {"evaluation": evaluation, "vars_dict": vars_dict}
                )
            )
        )

    def get_match_count(self, vars_dict: Optional[dict] = None) -> Tuple[int, int]:
        return (1, 1)

    def sort(self):
        """Sort the elements according to their sort key"""
        self.elements.sort(key=lambda e: e.pattern_precedence)


def match_expression_with_one_identity(
    self: ExpressionPattern,
    expression: BaseElement,
    parms: dict,
):
    """
    Process expressions with the attribute OneIdentity.
    """
    # This is all about the pattern. We do this
    # each time because at some point we should need
    # to check the default values each time...

    # This tries to reduce the pattern to a non-empty
    # set of default values, and a single pattern.
    from mathics.builtin.patterns.composite import Pattern
    from mathics.core.builtin import PatternObject

    vars_dict: dict = parms["vars_dict"]
    evaluation: Evaluation = parms["evaluation"]

    default_indx: int = 0
    optionals: dict = {}
    new_pattern: Optional[BasePattern] = None
    pattern_head: BaseElement = self.head.expr
    for pat_elem in self.elements:
        default_indx += 1
        if isinstance(pat_elem, AtomPattern):
            if new_pattern is not None:
                return
            new_pattern = pat_elem
            # TODO: check into account the second argument,
            # and if there is a default value...
        elif (
            isinstance(pat_elem, PatternObject)
            and pat_elem.get_head() == SymbolOptional
        ):
            if optionals:
                # A default pattern already exists
                # Do not use the second one
                if new_pattern is None:
                    new_pattern = pat_elem
            elif len(pat_elem.elements) == 2:
                pat, value = pat_elem.elements
                if isinstance(pat, Pattern):
                    key = pat.elements[0].atom.name  # type: ignore[attr-defined]
                else:
                    # if the first element of the Optional
                    # is not a `Pattern`, then we need to
                    # store an empty element.
                    key = ""
                optionals[key] = value
            elif len(pat_elem.elements) == 1:
                pat = pat_elem.elements[0]
                if isinstance(pat, Pattern):
                    key = pat.elements[0].atom.name  # type: ignore[attr-defined]
                else:
                    key = ""
                # Now, determine the default value
                defaultvalue_expr = Expression(
                    SymbolDefault, pattern_head, Integer(default_indx)
                )
                result = defaultvalue_expr.evaluate(evaluation)
                assert result is not None
                if result.sameQ(defaultvalue_expr):
                    if new_pattern is None:
                        # The optional pattern has no default value
                        # for the given position
                        new_pattern = pat_elem
                else:
                    optionals[key] = result
            else:
                return
        elif new_pattern is not None:
            return
        else:
            new_pattern = pat_elem

    # If there is not optional values in the pattern, then
    # it can not match any expression as a OneIdentity pattern:
    if len(optionals) == 0:
        return

    # Remove the empty key and load the default values in vars
    if "" in optionals:
        del optionals[""]
    # --- use undo for optionals ---
    old_values = {k: vars_dict.get(k, None) for k in optionals}
    try:
        vars_dict.update(optionals)
        assert new_pattern is not None
        new_pattern.match(expression=expression, pattern_context=parms)
    finally:
        for k, old in old_values.items():
            if old is None:
                vars_dict.pop(k, None)
            else:
                vars_dict[k] = old


def basic_match_expression(
    self: ExpressionPattern, expression: Expression, parms: dict
):
    """
    Try to match a pattern with an expression
    """
    # don't do this here, as self.get_pre_choices changes the
    # ordering of the elements!
    # if self.elements:
    #    next_element = self.elements[0]
    #    next_elements = self.elements[1:]
    yield_func: Callable = parms["yield_func"]
    vars_dict: dict = parms["vars_dict"]
    evaluation: Evaluation = parms["evaluation"]
    attributes: int = parms["attributes"]
    fully: bool = parms["fully"]

    def yield_choice(pre_vars):
        next_element = self.elements[0]
        next_elements = self.elements[1:]

        # "leading_blanks" below handles expressions with leading Blanks H[x_, y_, ...]
        # much more efficiently by not calling get_match_candidates_count() on elements
        # that have already been matched with one of the leading Blanks. this approach
        # is only valid for Expressions that are not Orderless (as with Orderless, the
        # concept of leading items does not exist).
        #
        # simple performance test case:
        #
        # f[x_, {a__, b_}] = 0;
        # f[x_, y_] := y + Total[x];
        # First[Timing[f[Range[5000], 1]]]"
        #
        # without "leading_blanks", Range[5000] will be tested against {a__, b_} in a
        # call to get_match_candidates_count(), which is slow.

        unmatched_elements = expression.elements
        leading_blanks = not A_ORDERLESS & attributes

        for element in self.elements:
            match_count = element.get_match_count()

            if leading_blanks:
                if tuple(match_count) == (
                    1,
                    1,
                ):  # Blank? (i.e. length exactly 1?)
                    if not unmatched_elements:
                        raise StopGenerator_ExpressionPattern_match()
                    if not element.does_match(
                        unmatched_elements[0],
                        {"evaluation": evaluation, "vars_dict": pre_vars},
                    ):
                        raise StopGenerator_ExpressionPattern_match()
                    unmatched_elements = unmatched_elements[1:]
                else:
                    leading_blanks = False

            if not leading_blanks:
                candidates = element.get_match_candidates_count(
                    unmatched_elements,
                    {
                        "expression": expression,
                        "attributes": attributes,
                        "vars_dict": pre_vars,
                        "evaluation": evaluation,
                    },
                )
                if candidates < match_count[0]:
                    raise StopGenerator_ExpressionPattern_match()

        # for new_vars, rest in self.match_element(    # nopep8
        #    self.elements[0], self.elements[1:], ([], expression.elements),
        #    pre_vars, expression, attributes, evaluation, first=True,
        #    fully=fully, element_count=len(self.elements)):
        # def yield_element(new_vars, rest):
        #    yield_func(new_vars, rest)
        self.match_element(
            element=next_element,
            pattern_context={
                "yield_func": yield_func,
                "rest_elements": tuple(next_elements),
                "rest_expression": ([], expression.elements),
                "vars_dict": pre_vars,
                "expression": expression,
                "attributes": attributes,
                "evaluation": evaluation,
                "first": True,
                "fully": fully,
                "element_count": len(self.elements),
                "element_index": 0,
            },
        )

    # for head_vars, _ in self.head.match(expression.get_head(), vars,
    # evaluation):
    def yield_head(head_vars, _):
        if self.elements:
            # pre_choices = self.get_pre_choices(
            #    expression, attributes, head_vars)
            # for pre_vars in pre_choices:

            self.get_pre_choices(
                self,
                expression,
                {
                    "yield_choice": yield_choice,
                    "attributes": attributes,
                    "vars_dict": head_vars,
                    "evaluation": evaluation,
                },
            )
        else:
            if not expression.elements:
                yield_func(head_vars, None)
            else:
                return

    self.head.match(
        expression.get_head(),
        {
            "yield_func": yield_head,
            "vars_dict": vars_dict,
            "evaluation": evaluation,
        },
    )


def _unwrap_unconstrained_blank_sequence(element: "BasePattern"):
    """
    If `element` is an untyped BlankSequence[]/BlankNullSequence[] -- bare
    (___, __) or wrapped in a plain Pattern[name, ...] (a_, a__, a___) with
    no type restriction, no Condition, no PatternTest -- return the inner
    Blank*Sequence* pattern object. Otherwise return None.

    Used by match_element's literal-lookahead fast path (see there): only
    triggers on exactly this narrow, easy-to-verify shape, so anything
    wrapped in additional constraints (a Condition that might depend on
    exactly which elements got captured, a type restriction that might
    reject some candidates, etc.) safely falls through to the regular
    subranges()-based search instead.
    """
    from mathics.builtin.patterns.basic import BlankNullSequence, BlankSequence
    from mathics.builtin.patterns.composite import Pattern

    inner = element.pattern if isinstance(element, Pattern) else element
    if isinstance(inner, (BlankSequence, BlankNullSequence)) and not inner.target_head:
        return inner
    return None


def _leading_literal_split_points(
    element: "BasePattern",
    rest_elements: tuple,
    candidates: tuple,
    set_lengths: Tuple[int, Optional[int]],
    evaluation: Evaluation,
    vars_dict: dict,
):
    """
    Fast path for `match_element`'s non-Orderless branch: when the current
    element is an unconstrained BlankSequence/BlankNullSequence (see
    `_unwrap_unconstrained_blank_sequence`) and it is immediately followed
    by a literal pattern element (a plain value, no wildcards), only ONE
    thing can make any given trial length succeed: the literal must be
    found at the position right after the block ends -- matching any other
    length is guaranteed to fail as soon as the literal element is tried
    next (AtomPattern.match does an exact `sameQ`/identity check against a
    single candidate). The regular subranges()-based search doesn't know
    this and blindly tries every length from `set_lengths[1]` (or the end
    of `candidates`) down to `set_lengths[0]`, which costs O(n) per element
    and, chained across a backtracking search, O(n^2) overall.

    Returns a list of valid block lengths (positions of the literal in
    `candidates`, filtered to respect `set_lengths`), in the same
    trial-order subranges() would have used, or None if the fast path
    doesn't apply here (caller should fall back to subranges()).
    """
    if not rest_elements or not getattr(rest_elements[0], "isliteral", False):
        return None
    if _unwrap_unconstrained_blank_sequence(element) is None:
        return None

    min_len, max_len = set_lengths
    # This fast path only targets the common, unbounded case. A bounded
    # max_len can hit subranges()'s own [0, 1] -> [1, 0] quirk (see
    # util.subranges); rather than replicate that here too, just fall
    # back to the regular search in that case.
    if max_len is not None:
        return None

    literal_element = rest_elements[0]
    pattern_context = {"evaluation": evaluation, "vars_dict": vars_dict}
    positions = [
        i
        for i, candidate in enumerate(candidates)
        if i >= min_len and literal_element.does_match(candidate, pattern_context)
    ]
    return positions


def _unwrap_options_pattern(element: "BasePattern"):
    """
    If `element` is an OptionsPattern[...] -- bare or wrapped in a plain
    Pattern[name, ...] (opt:OptionsPattern[]) -- return the inner
    OptionsPattern object. Otherwise return None.
    """
    from mathics.builtin.patterns.composite import OptionsPattern, Pattern

    inner = element.pattern if isinstance(element, Pattern) else element
    return inner if isinstance(inner, OptionsPattern) else None


def _is_option_like(candidate: BaseElement) -> bool:
    """Same shape check OptionsPattern.get_match_candidates() uses."""
    return candidate.has_form(("Rule", "RuleDelayed"), 2) or candidate.has_form(
        "List", None
    )


def _options_pattern_split(
    element: "BasePattern", rest_elements: tuple, candidates: tuple
):
    """
    WMA quirk: when a pattern contains more than one OptionsPattern[]
    element, only the LAST one ever collects any option-like arguments --
    every earlier OptionsPattern[] always matches an empty sequence,
    regardless of what option-like values are available. E.g.
    `F[x_Integer, opt1:OptionsPattern[], opt2:OptionsPattern[]]` applied
    to `F[z->p, 2, a->2, m->2]` binds opt1 to `{}` and opt2 to
    `{a->2, m->2, z->p}` in WMA -- never split between the two.

    The general subranges()/subsets()-based search doesn't know this: it
    just finds *some* backtracking split between opt1 and opt2 (both have
    unbounded, untyped match counts, so nothing else disambiguates which
    split "is the one"), which usually isn't the WMA split and is wasted
    search besides.

    Returns a `sets` list (same (items, (before, after)) shape the
    subranges()/subsets()-based paths produce) if `element` is an
    OptionsPattern[] (bare or Pattern-wrapped), or None if this fast path
    doesn't apply (caller should fall through to the regular search).
    """
    if _unwrap_options_pattern(element) is None:
        return None

    is_last = not any(
        _unwrap_options_pattern(rest_element) is not None
        for rest_element in rest_elements
    )
    if not is_last:
        # A later OptionsPattern[] still follows -- this one always
        # matches empty.
        return [((), ([], candidates))]

    # Last (or only) OptionsPattern[] in the chain: grab every
    # option-shaped candidate, wherever it is among `candidates` (options
    # need not be contiguous with each other or with this element's
    # position), preserving encounter order.
    matched = tuple(c for c in candidates if _is_option_like(c))
    remaining = tuple(c for c in candidates if not _is_option_like(c))
    return [(matched, ([], remaining))]


def expression_pattern_match_element_orderless(
    parms: dict,
    candidates: tuple,
    element_candidates: Union[tuple, set],
    less_first: bool,
    set_lengths: Tuple[int, Optional[int]],
):
    """
    match element for orderless expressions
    """
    # we only want element_candidates to be a set if we're orderless.
    # otherwise, constructing a set() is very slow for large lists.
    # performance test case:
    # x = Range[100000]; Timing[Combinatorica`BinarySearch[x, 100]]
    from mathics.builtin.patterns.composite import Pattern

    element: BaseElement = parms["element"]
    element_candidates = set(element_candidates)  # for fast lookup

    sets: Optional[list] = None
    if isinstance(element, Pattern):
        varname = element.elements[0].get_name()
        existing = parms["vars_dict"].get(varname, None)
        if existing is not None:
            head = existing.get_head()
            if head.get_name() == "System`Sequence" or (
                A_FLAT & parms["attributes"] and head == parms["expression"].get_head()
            ):
                needed = existing.elements
            else:
                needed = (existing,)

            available = list(candidates)

            for needed_element in needed:
                if needed_element in available and needed_element in element_candidates:
                    available.remove(needed_element)
                else:
                    return set()
            sets = [
                (
                    needed,
                    (
                        [],
                        available,
                    ),
                )
            ]

    if sets is None:
        sets = subsets(
            candidates,
            included=element_candidates,
            less_first=less_first,
            *set_lengths,
        )
    return sets


def expression_pattern_match_element_process_items(
    items: Union[tuple, list],
    items_rest: Union[tuple, list],
    parms: dict,
):
    """
    Try to match sequences built from items
    against the pattern.
    """
    # Include wrappings like Plus[a, b] only if not all items taken
    # - in that case we would match the same expression over and over.
    element_count: int = parms["element_count"]
    expression: Expression = parms["expression"]
    evaluation: Evaluation = parms["evaluation"]
    fully: bool = parms["fully"]
    pattern: ExpressionPattern = parms["pattern"]
    rest_expression = parms["rest_expression"]
    yield_func: Callable = parms["yield_func"]

    include_flattened: bool = parms["try_flattened"] and 0 < len(items) < len(
        expression.elements
    )

    # Don't try flattened when the expression would remain the same!

    def element_yield(next_vars_parm, next_rest_parm):
        # if next_rest is None:
        #    next_rest = ([], [])
        # yield_func(next_vars, (rest_expression[0] + items_rest[0],
        # next_rest[1]))
        if next_rest_parm is None:
            yield_func(
                next_vars_parm,
                (list(chain(rest_expression[0], items_rest[0])), []),
            )
        else:
            yield_func(
                next_vars_parm,
                (
                    list(chain(rest_expression[0], items_rest[0])),
                    next_rest_parm[1],
                ),
            )

    def match_yield(new_vars, _):
        if parms["rest_elements"]:
            new_parms = parms.copy()
            new_parms["rest_expression"] = items_rest
            new_parms["rest_elements"] = parms["next_rest_elements"]
            new_parms["vars_dict"] = new_vars
            new_parms["element_index"] = parms["element_index"] + 1
            new_parms["yield_func"] = element_yield
            del new_parms["element"]
            pattern.match_element(
                element=parms["next_element"], pattern_context=new_parms
            )
        else:
            if not fully or (not items_rest[0] and not items_rest[1]):
                yield_func(new_vars, items_rest)

    def yield_wrapping(item):
        element_index = parms.get("element_index", 0) + 1
        parms["element"].match(
            item,
            {
                "yield_func": match_yield,
                "vars_dict": parms["vars_dict"],
                "evaluation": evaluation,
                "fully": True,
                "head": expression.head,
                "element_index": element_index,
                "element_count": element_count,
            },
        )

    # parms = parms.copy()
    parms["max_count"] = parms["match_count"][1]
    parms["include_flattened"] = include_flattened
    # {"max_count":parms["match_count"][1],
    #     "expression":expression,
    #    "attributes":attributes,
    #    "include_flattened":include_flattened}
    pattern.get_wrappings(
        yield_func=yield_wrapping, items=tuple(items), pattern_context=parms
    )


def get_pre_choices_with_order(
    pat: ExpressionPattern, expression: Expression, pattern_context
):
    """
    Yield pre choices for expressions without
    the attribute Orderless.

    In this case, all we have to do is to call
    the parameter `yield_choice` with the collected
    var_dict.
    """
    pattern_context["yield_choice"](pattern_context["vars_dict"])


def get_pre_choices_orderless(
    pat: ExpressionPattern, expression: Expression, pattern_context
):
    """
    Yield pre choices for expressions with
    the attribute Orderless.

    This case is more involved, since the pattern can include subpatterns.

    """
    yield_choice: Callable = pattern_context["yield_choice"]
    vars_dict: dict = pattern_context["vars_dict"]

    patterns = pat.filter_elements("Pattern")
    # a dict with entries having patterns with the same name
    # which are not in vars_dict.
    groups: dict = {}
    prev_pattern = prev_name = None
    for pattern in patterns:
        name = pattern.elements[0].get_name()
        existing = vars_dict.get(name, None)
        if existing is None:
            # There's no need for pre-choices if the variable is
            # already set.
            if name == prev_name:
                if name in groups:
                    groups[name].append(pattern)
                else:
                    groups[name] = [prev_pattern, pattern]
            prev_pattern = pattern
            prev_name = name

    # FIX ORDERLESS REPEATED: completely rewritten per_name
    def per_name(yield_name: Callable, groups: Tuple, vars_dict: dict):
        """
        Yields possible variable settings (dictionaries) for the
        remaining pattern groups.
        This version correctly handles groups with multiple patterns
        sharing the same variable name.
        """
        if not groups:
            yield_name(vars_dict)
            return

        name, group_patterns = groups[0]
        remaining_groups = groups[1:]

        # If the variable is already bound, check consistency and move on.
        existing = vars_dict.get(name, None)
        if existing is not None:
            # Verify that existing matches all patterns in the group.
            # Convert to a sequence if needed.
            seq = existing if isinstance(existing, (tuple, list)) else (existing,)
            # Check if the sequence matches each pattern in the group.
            # We need to ensure that the pattern consumes the whole sequence.
            ok = True
            for p in group_patterns:
                # Use a helper that checks if p matches the sequence completely.
                if not sequence_matches(
                    p, seq, vars_dict, pattern_context["evaluation"]
                ):
                    ok = False
                    break
            if ok:
                per_name(yield_name, remaining_groups, vars_dict)
            return

        # Compute combined min/max lengths for the group.
        min_len = 0
        max_len = None
        for p in group_patterns:
            low, high = p.get_match_count()
            min_len = max(min_len, low)
            if max_len is None:
                max_len = high
            elif high is not None:
                max_len = min(max_len, high)

        # If the group can match zero elements and there are elements available,
        # we also need to consider the possibility of matching zero.
        # The subranges call below already handles flexible lengths.

        # Determine which elements are still available.
        # In this context, we haven't consumed any elements yet for this group,
        # but the recursion may have consumed some in previous groups.
        # For simplicity, we use the full expression elements and rely on the
        # fact that later groups will consume the rest.
        # This is a simplification; a production version should track
        # remaining elements via a state.

        # Use subranges to generate all subsequences of available elements.
        # We need to know the available elements; for now, we use the full list.
        available = list(expression.elements)  # This should be filtered in reality.

        # Generate all possible subsequences.
        # We can limit the search by using the computed min/max lengths.
        for seq, rest in subranges(available, min_len, max_len, flexible_start=True):
            ok = True
            for p in group_patterns:
                if not sequence_matches(
                    p, seq, vars_dict, pattern_context["evaluation"]
                ):
                    ok = False
                    break
            if ok:
                # Create a new vars_dict with the assignment.
                new_vars = vars_dict.copy()
                if len(seq) == 1:
                    new_vars[name] = seq[0]
                else:
                    new_vars[name] = Expression(SymbolSequence, *seq)
                per_name(yield_name, remaining_groups, new_vars)

    def sequence_matches(pattern, seq, vars_dict, evaluation):
        """Helper: check if pattern matches the whole sequence."""
        # For a single element, match the bare element directly.
        # Wrapping it in Sequence[...] would make the head of the
        # matched expression "Sequence" instead of the element's own
        # head, which breaks typed patterns like a_Integer (Blank[Integer]
        # checks the head of what it's given -- Sequence[1] has head
        # Sequence, not Integer, even though the untyped Blank[] doesn't
        # care and matches either way).
        if len(seq) == 1:
            match_target = seq[0]
        else:
            match_target = Expression(SymbolSequence, *seq)

        # Use a temporary context to see if the match consumes all.
        consumed = False

        def capture(vars, rest):
            nonlocal consumed
            if rest is None or (len(rest[0]) == 0 and len(rest[1]) == 0):
                consumed = True

        ctx = {
            "yield_func": capture,
            "vars_dict": vars_dict,
            "evaluation": evaluation,
            "fully": True,
        }
        try:
            pattern.match(match_target, ctx)
        except StopGenerator:
            pass
        return consumed

    # Start the recursive generation.
    per_name(yield_choice, tuple(groups.items()), vars_dict)


# --- Ordered/Orderless class split ---
#
# ExpressionPattern above still supports the fully-general case: build it
# without knowing the head's attributes (attributes=None, evaluation=None)
# and it defers, resolving (and caching) A_ORDERLESS on first .match().
# That existing behavior is untouched here -- nothing below changes it.
#
# These two subclasses are for the case where attributes are ALREADY
# known at construction time (either the caller passed them directly, or
# an `evaluation` was available to look them up right away). In that
# case there is no ambiguity to defer, so we can pick the concrete class
# immediately via `make_expression_pattern()` below.
#
# NOTE: these classes intentionally do NOT override __init__ or
# __set_pattern_attributes__. The inherited logic still re-derives
# `get_pre_choices` (and `sort()`/`isliteral`) from the *actual*
# attributes int passed in, which happens to match what the class name
# already promises when built through the factory. Redundant, but zero
# behavior change versus plain ExpressionPattern.
#
# `get_wrappings`/`match_element` on the base ExpressionPattern used to
# each carry their own `A_ORDERLESS & attributes` runtime branch to
# decide between the Orderless and non-Orderless code paths. Since
# BasePattern.create() never constructs a plain ExpressionPattern
# directly -- every live instance reaching these methods is either an
# OrderedExpressionPattern or an OrderlessExpressionPattern, confirmed by
# grep/audit of every call site that reaches get_wrappings/match_element
# -- those branches have been moved into real per-class overrides below:
# `_yield_sequence_wrappings` (single order vs. all permutations) and
# `_regular_match_element_sets` (literal-lookahead/subranges search vs.
# `expression_pattern_match_element_orderless`). The base-class bodies of
# those two hooks are therefore the Ordered/non-Orderless behavior, and
# OrderedExpressionPattern needs no override at all -- it inherits them
# as-is. Only OrderlessExpressionPattern overrides.
class OrderedExpressionPattern(ExpressionPattern):
    """
    ExpressionPattern for a head known NOT to have the Orderless
    attribute. Only constructed via make_expression_pattern() /
    DeferredExpressionPattern, where `attributes` is already known.

    No method overrides needed: ExpressionPattern's own
    `_yield_sequence_wrappings`/`_regular_match_element_sets` already
    implement the non-Orderless behavior (see class-split note above).
    """

    get_pre_choices = staticmethod(get_pre_choices_with_order)


class OrderlessExpressionPattern(ExpressionPattern):
    """
    ExpressionPattern for a head known to have the Orderless attribute.
    Only constructed via make_expression_pattern() /
    DeferredExpressionPattern, where `attributes` is already known.
    """

    get_pre_choices = staticmethod(get_pre_choices_orderless)

    def _yield_sequence_wrappings(self, items: Tuple, yield_func: Callable):
        """Orderless case: one Sequence[...] wrapping per permutation."""
        for perm in permutations(items):
            sequence = Expression(SymbolSequence, *perm)
            sequence.pattern_sequence = True
            yield_func(sequence)

    def _regular_match_element_sets(
        self,
        element: "BasePattern",
        rest_elements: tuple,
        candidates: tuple,
        element_candidates: Union[tuple, set],
        set_lengths: Tuple[int, Optional[int]],
        less_first: bool,
        pattern_context: dict,
    ):
        """Orderless case: delegate to the dedicated subset-based search."""
        return expression_pattern_match_element_orderless(
            {
                "expression": pattern_context["expression"],
                "element": element,
                "vars_dict": pattern_context["vars_dict"],
                "attributes": pattern_context["attributes"],
            },
            candidates,
            element_candidates,
            less_first,
            set_lengths,
        )


def make_expression_pattern(
    expr: Expression, attributes: int, evaluation: Optional[Evaluation] = None
) -> ExpressionPattern:
    """
    Factory: given `expr` and its head's ALREADY-KNOWN `attributes` int,
    construct the correct concrete pattern class directly -- no
    deferral, no later branching on A_ORDERLESS needed.

    Use this whenever attributes are on hand already (e.g. a Builtin
    class that declares its own attributes statically in Python, or any
    call site that already has an `evaluation` to look them up). For the
    case where attributes are NOT yet knowable (system bootstrap, before
    Definitions is fully populated), use DeferredExpressionPattern
    instead.
    """
    cls = (
        OrderlessExpressionPattern
        if A_ORDERLESS & attributes
        else OrderedExpressionPattern
    )
    return cls(expr, attributes, evaluation)


class DeferredExpressionPattern(BasePattern):
    """
    Wraps an expression whose head's attributes (and therefore whether
    it should be an OrderedExpressionPattern or an
    OrderlessExpressionPattern) aren't known yet -- e.g. during
    Definitions bootstrap, before all SetAttributes[] calls have run, or
    for a nested sub-pattern built without an `evaluation` context.

    On first real use (the first .match() call, since that's the first
    point an Evaluation is guaranteed to be available), it resolves to
    the correct concrete pattern via make_expression_pattern(), caches
    it, and delegates to it from then on.

    Every other BasePattern method (sameQ, pattern_precedence,
    element_order, get_head_name, get_lookup_name, ...) is answered
    directly by the BasePattern base class from self.expr, without
    needing resolution -- none of those depend on Orderless-ness. This
    was verified against every caller of those methods that can run
    before an Evaluation exists (Definitions.insert_rule,
    BaseRule.element_order/pattern_precedence, eval.patterns.Matcher).
    Do not add new pre-match behavior here without checking that it's
    similarly attribute-independent, or route it through _resolve()
    instead.

    Resolution happens once, lazily, on first real use (whichever
    .match() call comes first), and is then frozen for the rest of this
    object's life -- mirroring exactly how plain ExpressionPattern's own
    __set_pattern_attributes__ behaves (`if self.attributes is None:
    resolve-and-freeze`, never re-checked again after that). This
    matters concretely for `Dispatch[]`: its whole point is to compile a
    pattern once and reuse it, deliberately NOT re-deriving attributes
    on subsequent uses even if SetAttributes changes them later (a
    freshly-typed `expr /. rule`, by contrast, builds a brand new
    pattern object from scratch every time, so it naturally sees current
    attributes without any special re-derivation logic here).
    """

    def __init__(self, expr: BaseElement):
        self.expr = expr
        self.location = expr.location if hasattr(expr, "location") else None
        # Built without an evaluation, same as ExpressionPattern.__init__
        # would -- these may themselves come back as further
        # DeferredExpressionPattern instances if their own heads'
        # attributes aren't knowable yet either. Needed for
        # pattern_precedence (see _build_pattern_sort_key below), which
        # is purely structural and must work even before resolution.
        self.head = BasePattern.create(expr.head)
        self.elements = [BasePattern.create(element) for element in expr.elements]
        self._impl: Optional[ExpressionPattern] = None

    def _build_pattern_sort_key(self) -> tuple:
        # Mirrors ExpressionPattern._build_pattern_sort_key exactly --
        # structural only, doesn't need attributes/resolution.
        return (
            BASIC_EXPRESSION_PATTERN_SORT_KEY,
            self.head.pattern_precedence,
            tuple(
                chain(
                    (element.pattern_precedence for element in self.elements),
                    (END_OF_LIST_PATTERN_SORT_KEY,),
                )
            ),
        )

    def get_match_count(self, vars_dict: Optional[dict] = None) -> Tuple[int, int]:
        # Mirrors ExpressionPattern.get_match_count exactly -- a generic
        # (non-Blank-family) expression pattern always matches exactly
        # one element, regardless of Orderless-ness. Structural only.
        return (1, 1)

    def get_match_candidates(
        self, elements: Tuple[BaseElement, ...], pattern_context: dict
    ) -> tuple:
        # Mirrors ExpressionPattern.get_match_candidates exactly: this
        # only relies on self.does_match(), which is generic on
        # BasePattern and resolves us correctly -- doesn't depend on
        # Orderless-ness itself. Missing this was a real bug: without
        # it, DeferredExpressionPattern fell back to BasePattern's
        # default (an empty tuple -- "no candidates ever"), which made
        # match_element() silently find nothing to try even though
        # does_match() (used by the separate leading_blanks precheck)
        # correctly said a match was possible.
        evaluation: Evaluation = pattern_context["evaluation"]
        vars_dict: Optional[dict] = pattern_context.setdefault("vars_dict", {})
        return tuple(
            element
            for element in elements
            if self.does_match(
                element, {"evaluation": evaluation, "vars_dict": vars_dict}
            )
        )

    def _resolve(self, evaluation: Evaluation) -> ExpressionPattern:
        if self._impl is None:
            attributes = self.expr.get_head().get_attributes(evaluation.definitions)
            self._impl = make_expression_pattern(self.expr, attributes, evaluation)
        return self._impl

    def match(self, expression: BaseElement, pattern_context: dict):
        return self._resolve(pattern_context["evaluation"]).match(
            expression, pattern_context
        )

    def __repr__(self):
        return f"<DeferredExpressionPattern: {self.expr}>"
