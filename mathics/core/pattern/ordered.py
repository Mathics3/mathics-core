# cython: language_level=3
# cython: profile=False
# -*- coding: utf-8 -*-
"""
Non-Orderless ExpressionPatterns

Specialized ExpressionPatterns for the case of expressions with a head
that do not have the Orderless attribute.

"""

from typing import Callable, Optional, Tuple, Union

from mathics.core.attributes import A_FLAT, A_ONE_IDENTITY, A_ORDERLESS
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.interrupt import TimeoutInterrupt
from mathics.core.systemsymbols import SymbolSequence
from mathics.core.util import subranges

from .base import (
    AtomPattern,
    BasePattern,
    ExpressionPattern,
    StopGenerator_ExpressionPattern_match,
)
from .common import match_expression_with_one_identity, match_fixed_blank_tuple


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


class OrderedExpressionPattern(ExpressionPattern):
    """
    ExpressionPattern for a head without the Orderless
    attribute. Only constructed via make_expression_pattern() /
    DeferredExpressionPattern, where `attributes` is already known.

    This is the general non-Orderless case, including Flat and/or
    OneIdentity heads. For the common sub-case where NEITHER Flat nor
    OneIdentity is set either, make_expression_pattern() constructs
    SimpleOrderedExpressionPattern (below) instead, which skips the
    Flat/OneIdentity-related runtime checks this class still needs and
    adds the fixed-arity Blank-tuple fast path.

    No method overrides needed beyond match(): ExpressionPattern's own
    `_yield_sequence_wrappings`/`_regular_match_element_sets` already
    implement the non-Orderless behavior (see class-split note above).
    """

    get_pre_choices = staticmethod(get_pre_choices_with_order)

    def __init__(
        self,
        expression: Expression,
        attributes: int,
        evaluation: Optional[Evaluation] = None,
    ):
        super().__init__(expression, attributes, evaluation)
        self.attributes = attributes
        if not (A_ONE_IDENTITY + A_FLAT) & attributes:
            self.isliteral = self.head.isliteral and all(
                element.isliteral for element in self.elements
            )
        # self.__set_pattern_attributes__(attributes)

    def _regular_match_element_sets(
        self,
        element: "BasePattern",
        rest_elements: tuple,
        candidates: tuple,
        element_candidates: Union[tuple, set],
        set_lengths: Tuple[int, int],
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


class SimpleOrderedExpressionPattern(OrderedExpressionPattern):
    """
    Specialization of OrderedExpressionPattern for a head with NONE of
    Orderless, Flat, OneIdentity -- the common case, since most heads
    declare no special attributes at all. Only constructed via
    make_expression_pattern(), which is the sole place that decides
    between this class and the general OrderedExpressionPattern (used
    when Flat and/or OneIdentity IS present).

    Skips the Flat/OneIdentity-related runtime checks that
    OrderedExpressionPattern.match still needs
    (`if not A_FLAT & attributes: fully = True`,
    `if A_ONE_IDENTITY & attributes: match_expression_with_one_identity(...)`)
    -- for this class they always resolve the same way, so they're
    simply absent rather than evaluated every match() call.

    """

    def __init__(
        self,
        expression: Expression,
        attributes: int,
        evaluation: Optional[Evaluation] = None,
    ):
        super().__init__(expression, attributes, evaluation)

    def match(self, expression: BaseElement, pattern_context: dict):
        """
        Try to match the pattern against an Expression, for a head
        known to have none of Orderless/Flat/OneIdentity.
        """
        from mathics.core.atoms.associations import Association

        evaluation = pattern_context["evaluation"]
        yield_func = pattern_context["yield_func"]
        vars_dict = pattern_context["vars_dict"]

        evaluation.check_stopped()
        if self.isliteral:
            if expression.sameQ(self.expr):
                yield_func(vars_dict, None)
            return

        # --- use mutation with undo instead of copy ---
        old_fully = pattern_context.get("fully")
        old_attributes = pattern_context.get("attributes")
        old_head = pattern_context.get("head")
        old_element_index = pattern_context.get("element_index")
        old_element_count = pattern_context.get("element_count")
        try:
            # No A_FLAT here (guaranteed by construction), so fully is
            # unconditionally True -- unlike the general
            # OrderedExpressionPattern.match, there's no runtime check
            # to make.
            pattern_context["fully"] = True
            pattern_context["attributes"] = self.attributes
            pattern_context["head"] = None
            pattern_context["element_index"] = None
            pattern_context["element_count"] = None

            if isinstance(expression, Association):
                expression = expression.expr

            if isinstance(expression, Expression):
                try:
                    basic_match_expression(self, expression, pattern_context)
                except (StopGenerator_ExpressionPattern_match, TimeoutInterrupt):
                    return
            # No A_ONE_IDENTITY check -- guaranteed absent for this class.
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


class FixedBlankTupleExpressionPattern(ExpressionPattern):
    """
    ExpressionPattern for a LITERAL (bare Symbol) head applied to a
    fixed-length tuple of elements that are ALL bare or named Blanks
    -- head[_], head[_,_], head[_,_,_], head[_String], head[_List],
    head[_Integer], head[a_,b_], head[a_,a_], etc. (see
    classify_fixed_blank_tuple in common.py for the exact shape).

    Only ever constructed by make_expression_pattern(), which performs
    the classification BEFORE building any pattern objects -- directly
    on the raw, not-yet-wrapped expr.elements (classify_fixed_blank_tuple
    is duck-typed to work on either raw Expression children or
    BasePattern-wrapped ones).

    For this shape there is exactly ONE possible match: a positional,
    slot-by-slot check (arity + per-slot does_match/match), with zero
    ambiguity for Sequence[...]/subranges/subsets to search over --
    so match() below IS the whole algorithm, not a fast path in front
    of a fallback. There is deliberately no fallback to
    basic_match_expression: nothing it could find that this doesn't
    already decide.

    """

    def __init__(
        self,
        expression: Expression,
        attributes: int,
        evaluation: Optional[Evaluation] = None,
    ):
        super().__init__(expression, attributes, evaluation)
        assert isinstance(self.elements, tuple)
        self.attributes = attributes

    def match(self, expression: BaseElement, pattern_context: dict):
        """
        The one and only match algorithm for this shape: positional,
        slot-by-slot, via match_fixed_blank_tuple (see its docstring
        in common.py for why it threads vars_dict through each slot's
        own match()/yield_func rather than using does_match(), which
        would silently drop any binding a named
        Pattern[name, Blank[...]] slot produces).
        """
        from mathics.core.atoms.associations import Association

        evaluation = pattern_context["evaluation"]
        yield_func = pattern_context["yield_func"]
        vars_dict = pattern_context["vars_dict"]

        evaluation.check_stopped()

        if isinstance(expression, Association):
            expression = expression.expr

        if not isinstance(expression, Expression):
            return

        expr_elements = expression.elements
        if len(expr_elements) != len(self.elements):
            return
        # self.head is guaranteed (by make_expression_pattern's
        # isinstance(expr.head, Symbol) check, before this class is
        # ever constructed) to be an AtomPattern wrapping a Symbol --
        # whose own match_symbol() is exactly `expression is self.atom`
        # (see base.py). does_match() would get to the same answer,
        # but only after building its own pattern_context, defining a
        # closure, and raising+catching StopGenerator_Pattern to turn
        # that into a bool -- a full exception round trip to compute
        # an identity check. Skip all of that.
        self_head = self.head
        if (
            not isinstance(self_head, AtomPattern)
            or expression.get_head() is not self_head.atom
        ):
            return

        result_vars = match_fixed_blank_tuple(
            self.elements, expr_elements, vars_dict, evaluation
        )
        if result_vars is not None:
            yield_func(result_vars, None)


class SingleSequenceExpressionPattern(ExpressionPattern):
    """
    ExpressionPattern for a LITERAL (bare Symbol) head applied to
    EXACTLY ONE element, which is a NAMED BlankSequence or
    BlankNullSequence, typed or not -- head[s__], head[s__HEAD],
    head[s___], head[s___HEAD] (see classify_single_sequence in
    common.py for the exact shape and the profiling numbers that
    motivate this class).

    Only ever constructed by make_expression_pattern(), which performs
    the classification BEFORE building any pattern objects, same
    convention as FixedBlankTupleExpressionPattern.

    For this shape there is exactly ONE possible match: the single
    (Blank)(Null)Sequence element must absorb the expression's entire
    element tuple (empty, one, or many elements) or the match fails --
    there is no other pattern element to backtrack against, so no
    subranges()/get_wrappings/match_element search is needed. match()
    below goes straight from "is this the right head" to "hand the
    whole element tuple to the wrapped Pattern[name, ...] and let IT
    do the (unavoidable) per-element type check exactly once" --
    skipping the redundant double candidate-scan
    (get_match_candidates_count then get_match_candidates, both doing
    the same O(n) type check for a typed s__HEAD, only for
    match_element's `included` argument that the Ordered path's
    subranges() doesn't even consult -- see subranges()'s own
    docstring/TODO) and the extra Expression(Sequence, *items)
    (re)allocation that get_wrappings/_yield_sequence_wrappings would
    otherwise perform on top of the one this class already needs.

    Deliberately preserves the exact binding shape a named
    (Blank)(Null)Sequence produces via the ordinary path (see
    get_wrappings): zero expression elements bind the name to an empty
    Sequence[], exactly one binds the name to that RAW element itself
    (never wrapped), and two or more bind the name to
    Sequence[elem1, ..., elemN] -- this matters for typed patterns
    like x_Integer nested inside a rule using this binding downstream,
    which check the head of whatever they're handed.
    """

    def __init__(
        self,
        expression: Expression,
        attributes: int,
        evaluation: Optional[Evaluation] = None,
    ):
        super().__init__(expression, attributes, evaluation)
        assert len(self.elements) == 1
        self.attributes = attributes

    def match(self, expression: BaseElement, pattern_context: dict):
        """
        The one and only match algorithm for this shape: check the
        head, then hand the expression's entire element tuple --
        wrapped exactly the way get_wrappings would wrap it -- to the
        single wrapped Pattern[name, Blank(Null)Sequence[...]] element,
        and let its own match() (which only ever needs `yield_func`
        and `vars_dict` from pattern_context -- see
        composite.py:Pattern.match and basic.py:BlankSequence.match /
        BlankNullSequence.match) do the actual type check and binding.
        """
        from mathics.core.atoms.associations import Association

        evaluation = pattern_context["evaluation"]
        yield_func = pattern_context["yield_func"]
        vars_dict = pattern_context["vars_dict"]

        evaluation.check_stopped()

        if isinstance(expression, Association):
            expression = expression.expr

        if not isinstance(expression, Expression):
            return

        # Same head-identity fast check as FixedBlankTupleExpressionPattern
        # (see its match() for why does_match() would be strictly more
        # expensive here): self.head is guaranteed to be an AtomPattern
        # wrapping a Symbol by make_expression_pattern's
        # isinstance(expr.head, Symbol) check, done before this class
        # is ever constructed.
        self_head = self.head
        if (
            not isinstance(self_head, AtomPattern)
            or expression.get_head() is not self_head.atom
        ):
            return

        expr_elements = expression.elements
        if len(expr_elements) == 1:
            # Bind the raw element itself, not Sequence[element] -- see
            # class docstring and get_wrappings' own len(items) == 1
            # special case, which this replicates.
            matched = expr_elements[0]
        else:
            # Zero elements (empty Sequence[], only reachable when the
            # wrapped pattern is a BlankNullSequence -- a BlankSequence
            # will simply fail to match an empty Sequence[], same as
            # it fails today) or two-or-more: wrap exactly as
            # ExpressionPattern._yield_sequence_wrappings would.
            matched = Expression(SymbolSequence, *expr_elements)
            matched.pattern_sequence = True

        self.elements[0].match(
            matched,
            {
                "yield_func": yield_func,
                "vars_dict": vars_dict,
                "evaluation": evaluation,
                "fully": True,
            },
        )
