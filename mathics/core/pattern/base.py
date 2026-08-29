# cython: language_level=3
# cython: profile=False
# -*- coding: utf-8 -*-


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

from mathics.core.attributes import A_FLAT
from mathics.core.element import BaseElement, ensure_context
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
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
    SymbolOptional,
    SymbolOptionsPattern,
    SymbolPattern,
    SymbolPatternTest,
    SymbolRepeated,
    SymbolRepeatedNull,
    SymbolSequence,
)

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
        from .deferred import DeferredExpressionPattern, make_expression_pattern

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
        """Return the number of candidates that match the pattern."""
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
    Base class for Pattern that matches with an Expression.
    Do not create this class directly. Use `ExpressionPattern.create`,
    which generates the right subclass, according to the
    evaluation object, or the request attributes.
    """

    # get_pre_choices = pattern_nocython.get_pre_choices
    # match = pattern_nocython.match
    attributes: int

    def __init__(
        self,
        expr: Expression,
        attributes: Optional[int] = None,
        evaluation: Optional[Evaluation] = None,
    ):
        self.expr = expr
        self.location = expr.location if hasattr(expr, "location") else None
        head = expr.head
        self.head = BasePattern.create(head, evaluation=evaluation)
        self.elements = [
            BasePattern.create(element, evaluation=evaluation)
            for element in expr.elements
        ]

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
        from .common import _options_pattern_split

        attributes: int = pattern_context["attributes"]
        evaluation: Evaluation = pattern_context["evaluation"]
        expression: BaseElement = pattern_context["expression"]
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
