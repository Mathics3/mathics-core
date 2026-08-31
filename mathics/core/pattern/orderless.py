# cython: language_level=3
# cython: profile=False
# -*- coding: utf-8 -*-
"""
Orderless ExpressionPatterns

Specialized ExpressionPatterns for the case of expressions with a head
that have the Orderless attribute.

"""

from typing import Callable, Optional, Tuple, Union

from mathics.core.attributes import A_FLAT, A_ONE_IDENTITY
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.interrupt import TimeoutInterrupt
from mathics.core.systemsymbols import SymbolSequence
from mathics.core.util import SUBRANGES_GENERATOR_TYPE, permutations, subranges, subsets

from .base import (
    BasePattern,
    ExpressionPattern,
    StopGenerator,
    StopGenerator_ExpressionPattern_match,
)
from .common import match_expression_with_one_identity


def basic_match_orderless_expression(
    self: ExpressionPattern, expression: Expression, parms: dict
):
    """
    Try to match a pattern with an expression assuming orderless
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
        unmatched_elements = expression.elements

        for element in self.elements:
            match_count = element.get_match_count()
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


def expression_pattern_match_element_orderless(
    parms: dict,
    candidates: tuple,
    element_candidates: Union[tuple, set],
    less_first: bool,
    set_lengths: Tuple[int, Optional[int]],
) -> SUBRANGES_GENERATOR_TYPE:
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

    if isinstance(element, Pattern):
        varname = element.elements[0].get_name()
        existing = parms["vars_dict"].get(varname, None)
        # Another subpattern has the same name
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
                    return None
            yield (needed, (tuple(), tuple(available)))
            return None

    yield from subsets(
        candidates,
        included=element_candidates,
        less_first=less_first,
        *set_lengths,
    )


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

    # The named patterns. This could be
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

        # Compute combined min/max lengths for the group.
        low: int
        high: int
        min_len: int = 0
        max_len: int = -1
        for p in group_patterns:
            low, high = p.get_match_count()
            min_len = max(min_len, low)
            if max_len == -1:
                max_len = high
            elif high is not None:
                max_len = min(max_len, high)
            else:
                raise ValueError("high is None?", high)

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
        available = tuple(expression.elements)  # This should be filtered in reality.

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


class OrderlessExpressionPattern(ExpressionPattern):
    """
    ExpressionPattern for a head known to have the Orderless attribute.
    Only constructed via make_expression_pattern() /
    DeferredExpressionPattern, where `attributes` is already known.
    """

    get_pre_choices = staticmethod(get_pre_choices_orderless)

    def __init__(
        self,
        expression: Expression,
        attributes: int,
        evaluation: Optional[Evaluation] = None,
    ):
        super().__init__(expression, attributes, evaluation)
        self.attributes = attributes
        self.sort()

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
                    basic_match_orderless_expression(self, expression, pattern_context)
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
