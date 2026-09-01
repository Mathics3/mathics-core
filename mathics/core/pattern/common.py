# cython: language_level=3
# cython: profile=False
# -*- coding: utf-8 -*-
"""
Common auxiliary functions for pattern matching.

"""


from typing import Optional

from mathics.core.atoms import Integer
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.rules import is_option_rule
from mathics.core.symbols import SymbolList
from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolDefault,
    SymbolOptional,
    SymbolPattern,
)

from .base import AtomPattern, BasePattern, ExpressionPattern


def _is_option_like(candidate: BaseElement) -> bool:
    """Same shape check OptionsPattern.get_match_candidates() uses."""

    return is_option_rule(candidate) or candidate.has_form(SymbolList, None)


def _unwrap_options_pattern(element: "BasePattern"):
    """
    If `element` is an OptionsPattern[...] -- bare or wrapped in a plain
    Pattern[name, ...] (opt:OptionsPattern[]) -- return the inner
    OptionsPattern object. Otherwise return None.
    """
    from mathics.builtin.patterns.composite import OptionsPattern, Pattern

    inner = element.pattern if isinstance(element, Pattern) else element
    return inner if isinstance(inner, OptionsPattern) else None


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


def _is_bare_blank(element: BaseElement) -> bool:
    """
    True for an unnamed Blank[] or Blank[Type] (0 or 1 sub-elements).

    Deliberately NOT restricted to BasePattern instances: `element` is
    routinely a RAW, not-yet-wrapped Expression/Symbol straight off
    expr.elements (see classify_fixed_blank_tuple's docstring for why
    that matters) -- has_form() answers the same way on both raw
    Expression children and BasePattern-wrapped ones, so an
    isinstance(element, ExpressionPattern) guard here would silently
    reject every RAW element, i.e. every call from
    make_expression_pattern -- which is the only place that matters,
    since that's what decides whether FixedBlankTupleExpressionPattern
    gets built at all.
    """
    return element.has_form(SymbolBlank, 0, 1)


def classify_fixed_blank_tuple(elements: tuple) -> Optional[tuple]:
    """
    If `elements` has AT LEAST TWO entries and every one of them is
    either:
      - a bare (unnamed) Blank[] / Blank[Type], or
      - a named blank Pattern[name, Blank[...]] (`x_`, `x_Integer`, ...)
    return `elements` back unchanged, as a signal that this
    ExpressionPattern has a fixed arity with no possible backtracking
    between slots: matching is exactly "N elements, checked
    positionally, one does_match() per slot, in order", nothing else --
    including the case of a name repeated across slots (`f[a_, a_]`),
    since that's already handled *inside* Pattern.match's own
    already-bound-name check (does_match on the second occurrence will
    correctly require sameQ against the value bound by the first) --
    this fast path doesn't need to special-case it.

    N=1 (head[_], head[x_], ...) is DELIBERATELY excluded, even though
    it's structurally the same shape: benchmarking (Mathics3 built-ins
    like NumericQ[expr_]) showed no measurable speedup over
    SimpleOrderedExpressionPattern's own basic_match_expression for a
    single slot -- for N=1 there's essentially no combinatorial search
    to skip in the first place, so FixedBlankTupleExpressionPattern's
    extra positional-check machinery doesn't pay for itself. N=2/N=3
    (Subtract[x_, y_] and friends) DID show a real, repeatable gain.
    Since a dedicated class is extra surface to reason about when
    debugging rule application, and a simpler implementation is
    preferred whenever it performs the same, N=1 patterns are routed
    to SimpleOrderedExpressionPattern like everything else instead of
    getting their own rarely-distinguishing code path for no payoff.

    Works equally on RAW, not-yet-wrapped Expression/Symbol children
    (e.g. `expr.elements` straight off a Mathics Expression) and on
    BasePattern-wrapped elements: both answer get_head_name()/elements
    the same way (BasePattern proxies these to self.expr -- see
    DeferredExpressionPattern's docstring). This is what lets
    make_expression_pattern() classify the shape BEFORE constructing
    any pattern objects at all.

    Deliberately still excludes:
    - BlankSequence/BlankNullSequence (`__`, `___`) and named sequences
      (`x__`, `x___`): different get_match_count(), handled elsewhere.
    - anything wrapped in Condition/Optional/PatternTest/Alternatives,
      even if it wraps a Blank underneath (e.g. `x_ /; cond`,
      `Optional[x_]`) -- those aren't `Pattern[name, Blank[...]]`
      shaped and are conservatively rejected.

    Returns None (fall through to the general machinery) both for the
    empty tuple (head[] is already handled by isliteral) and for a
    single-element tuple (see N=1 note above).
    """
    if len(elements) < 2:
        return None
    for element in elements:
        if _is_bare_blank(element):
            continue
        if element.has_form(SymbolPattern, 2) and _is_bare_blank(element.elements[1]):
            continue
        return None
    return elements


def match_fixed_blank_tuple(
    blanks: tuple,
    expr_elements: tuple,
    vars_dict: dict,
    evaluation: Evaluation,
) -> Optional[dict]:
    """
    Positionally match `blanks[i]` against `expr_elements[i]` for every
    i, threading vars_dict THROUGH EACH SLOT'S OWN yield_func -- same
    protocol basic_match_expression/match_element use everywhere else
    in this package -- rather than mutating a single shared dict in
    place.

    This distinction matters concretely for named slots
    (Pattern[name, Blank[...]]): Pattern.match binds a name by
    constructing a *new* vars_dict (with the name added) and handing it
    to its own yield_func as the `sub_vars` argument -- it does not
    mutate the vars_dict it was given. A caller that reads bindings off
    the ORIGINAL dict object it passed in (e.g. via does_match(), whose
    yield_match callback discards sub_vars and returns only True/False)
    will silently lose every binding a named slot produced. That was
    exactly the bug this function replaces: an earlier version of this
    fast path called does_match() per slot and returned the untouched
    original vars_dict on "success", which happened to work for
    Pattern-free bare Blanks (whose match() does pass the same object
    through) but dropped bindings the moment any slot was a named
    Pattern[name, Blank[...]] -- e.g. Set[lhs_, rhs_] would structurally
    "match" while `lhs`/`rhs` never made it into the substitution vars.

    NO EXCEPTIONS ARE USED HERE, deliberately -- an earlier version
    threaded slots via a recursive step()/yield_one() chain that raised
    a control-flow exception on success (mirroring the
    StopGenerator-based convention this package uses elsewhere for
    general backtracking search). Profiling showed that exception
    raise+unwind cost measurably more than the combinatorial search it
    was replacing, for exactly the small fixed arities
    (classify_fixed_blank_tuple targets N=1,2,3-ish) this function
    exists for -- Python 3.11's "zero-cost exceptions" only removes the
    overhead of a try block that DOESN'T raise; it does nothing for the
    raise+catch itself, which this function's success path hit on
    every single call. That's fine to avoid entirely here: every shape
    classify_fixed_blank_tuple accepts (bare or named Blank) is a
    single, non-backtracking check whose match() calls yield_func AT
    MOST ONCE -- there is no case where a slot could deliver a second,
    different sub_vars we'd need to fall back and try, so a plain loop
    with a mutable one-slot box, checked after each match() call, is
    both correct and exception-free.

    Returns the fully-threaded vars_dict on success (a dict that may or
    may not be `is vars_dict`, depending on what each slot's match()
    did), or None if any slot failed to match. Never mutates the
    `vars_dict` object passed in.
    """
    current_vars = vars_dict
    for blank, elt in zip(blanks, expr_elements):
        result_box: list = []
        blank.match(
            elt,
            {
                "yield_func": lambda sub_vars, _rest, _box=result_box: _box.append(
                    sub_vars
                ),
                "vars_dict": current_vars,
                "evaluation": evaluation,
                "fully": True,
            },
        )
        if not result_box:
            return None
        current_vars = result_box[0]
    return current_vars


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
