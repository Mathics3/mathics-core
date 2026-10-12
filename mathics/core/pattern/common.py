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
    SymbolBlankNullSequence,
    SymbolBlankSequence,
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
    """
    return element.has_form(SymbolBlank, 0, 1)


def classify_fixed_blank_tuple(elements: tuple) -> Optional[tuple]:
    """
    If every entry of `elements` (zero or more of them) is either:
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

    Returns None (fall through to the general machinery) if any
    element doesn't have this exact shape.
    """
    for element in elements:
        if _is_bare_blank(element):
            continue
        if element.has_form(SymbolPattern, 2) and _is_bare_blank(element.elements[1]):
            continue
        return None
    return elements


def classify_single_sequence(elements: tuple) -> Optional[BaseElement]:
    """
    If `elements` is a 1-tuple whose sole entry is a NAMED
    BlankSequence or BlankNullSequence -- `Pattern[name, BlankSequence[...]]`
    (`s__`, `s__Integer`) or `Pattern[name, BlankNullSequence[...]]`
    (`s___`, `s___Integer`) -- return that raw `Pattern[...]` element
    unchanged, as a signal that this ExpressionPattern has exactly ONE
    possible match: there is nothing else in the pattern to backtrack
    against, so the whole expression's elements (however many there
    are) are the only candidate for this single (Blank)(Null)Sequence.

    BARE (unnamed) `__`/`___` are deliberately NOT included here, even
    though structurally similar: as the sole element of a pattern with
    no `rest_elements` after it, `less_first` is already `False` in
    `_regular_match_element_sets`, so `subranges()` tries the
    full-length split FIRST and succeeds immediately there -- no
    combinatorial search actually happens for the bare case today, so
    a dedicated class has nothing measurable to save (confirmed by
    benchmarking: near-identical timings with/without this
    classification for `head[__]`/`head[___]`, both typed and
    untyped).

    The NAMED case is different: profiling `head[s__Integer]` (see
    session notes) against a matched Range[6000] showed the actual,
    unavoidable per-element type check (`BlankSequence.match` itself)
    takes about 15% of the total match time; the other ~85% is spent
    BEFORE `match_element`'s `subranges()` call even gets to try
    anything -- `basic_match_expression.yield_choice`'s pre-check via
    `get_match_candidates_count`, followed by `match_element` building
    `element_candidates` via `get_match_candidates` AGAIN (the exact
    same O(n) type-scan, discarded immediately after: `subranges()` --
    unlike `subsets()`, used by the Orderless path -- never even
    consults its `included` argument, see its module docstring), plus
    the `Expression(Sequence, *items)` (re)allocation in
    `_yield_sequence_wrappings`. All of that exists to support
    backtracking against OTHER elements/candidates that, for this
    exact shape, don't exist: there is exactly one pattern element and
    it must absorb the entire (possibly empty, possibly
    single-element, possibly multi-element) sequence of expression
    elements, or the match fails outright -- no split to search for.

    Deliberately still excludes:
    - Anything wrapped in Condition/Optional/PatternTest/Alternatives
      around the (Blank)(Null)Sequence -- not exactly
      `Pattern[name, Blank(Null)Sequence[...]]` shaped, conservatively
      rejected (same policy as `classify_fixed_blank_tuple`).
    - More than one element (`head[s__, t_]`, etc.) -- there IS
      backtracking to do there (where does `s__`'s block end?), so
      this fast path does not apply; that shape stays on the general
      `subranges()`-based search.

    Returns None (fall through to the general machinery) if `elements`
    doesn't have exactly this shape.
    """
    if len(elements) != 1:
        return None
    element = elements[0]
    if not element.has_form(SymbolPattern, 2):
        return None
    inner = element.elements[1]
    if inner.has_form(SymbolBlankSequence, 0, 1) or inner.has_form(
        SymbolBlankNullSequence, 0, 1
    ):
        return element
    return None


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
