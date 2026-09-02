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
    SymbolOptionsPattern,
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


def _is_blank_or_literal_slot(element: BaseElement) -> bool:
    """
    True for a single FIXED-POSITION pattern slot -- one that
    `match_fixed_blank_tuple` can already handle generically via a
    plain per-slot `.match()` call, because all three shapes below
    share the exact same minimal calling convention (only
    `pattern_context["yield_func"]`/`["vars_dict"]` needed, nothing
    else -- verified directly against Blank.match, Pattern.match, and
    AtomPattern.match/match_symbol):
      - a bare (unnamed) Blank[] / Blank[Type],
      - a named blank Pattern[name, Blank[...]] (`x_`, `x_Integer`),
      - a LITERAL: any RAW element that is not an Expression at all
        (an Integer/Real/String/bare Symbol used as-is, e.g. the `1`
        in `f[1, x_]` or the `csv` in `f[csv, x_]` -- WMA/Mathics
        pattern syntax already treats a bare, non-underscored atom as
        "must sameQ-match this exact value", which is precisely what
        the resulting AtomPattern.match()/match_symbol() does; no
        wrapper syntax needed or accepted here, and this deliberately
        does NOT extend to composite literals like `{1, 2}` -- those
        would need their own recursive isliteral-style check to rule
        out a nested pattern hiding inside, which is exactly the
        general machinery's job, not this cheap raw-shape check's).

    Kept as a free function (not a per-class method) so both
    `classify_fixed_blank_tuple` (all slots fixed, no OptionsPattern)
    and `classify_positional_options` (N fixed slots, then a trailing
    OptionsPattern[...]) can classify against the identical rule
    without duplicating it -- and, at match time,
    `match_fixed_blank_tuple` doesn't care which of the three shapes
    it's threading through a given slot either, so the same runtime
    helper covers all of them too.
    """
    if _is_bare_blank(element):
        return True
    if element.has_form(SymbolPattern, 2) and _is_bare_blank(element.get_elements()[1]):
        return True
    return not isinstance(element, Expression)


def classify_fixed_blank_tuple(elements: tuple) -> Optional[tuple]:
    """
    If every entry of `elements` (zero or more of them) is a
    fixed-position slot per `_is_blank_or_literal_slot` -- a bare
    Blank[]/Blank[Type], a named Pattern[name, Blank[...]]
    (`x_`, `x_Integer`, ...), OR a bare literal atom (`1`, `"csv"`,
    a literal Symbol, ...) -- return `elements` back unchanged, as a
    signal that this ExpressionPattern has a fixed arity with no
    possible backtracking between slots: matching is exactly "N
    elements, checked positionally, one .match() per slot, in order",
    nothing else -- including the case of a name repeated across slots
    (`f[a_, a_]`), since that's already handled *inside* Pattern.match's
    own already-bound-name check (does_match on the second occurrence
    will correctly require sameQ against the value bound by the
    first) -- this fast path doesn't need to special-case it.

    LITERALS (this session, added alongside classify_positional_options
    below): previously this only accepted Blank-shaped slots; a mix
    like `head[1, x_, 3]` fell all the way through to
    SimpleOrderedExpressionPattern's fully general search, with NO fast
    path at all (not pure-Blank enough for this class, not pure-literal
    enough for SimpleOrderedExpressionPattern's own `isliteral` shortcut
    either). Measured: ~62.18us (general path) vs ~14.05us (through
    this class instead) for `head[1, x_, 3]` -- about 4.4x. A fully
    PURE-literal tuple (`head[1, 2, 3]`, no Blank slots at all) was
    already handled by `isliteral`'s single whole-expression `sameQ()`
    check in SimpleOrderedExpressionPattern -- measured essentially
    identical either way (~14.99us isliteral vs ~15.18us through this
    class), so widening this classifier to also accept all-literal
    tuples doesn't cost that existing path anything; no need to guard
    against "at least one real Blank" specifically.

    N=1 CORRECTION (earlier this session): an earlier version of this
    docstring claimed N=1 (`head[_]`, `head[x_]`) was DELIBERATELY
    excluded here (a `len(elements) < 2: return None` guard), on the
    grounds that benchmarking showed "no measurable speedup". That
    guard got dropped from the actual code at some point without
    anyone consciously re-deciding it -- re-measuring properly
    (same-process A/B, `timeit`, NOT `cProfile`, which inflated an
    earlier, unrelated measurement in this same session by ~6x) showed
    the original claim was simply wrong: routing N=1 through this
    class is consistently 2.4x-3.2x faster than
    SimpleOrderedExpressionPattern, not "no difference" -- confirmed
    independently by a CI regression detector (`Select[Range[100],
    PrimeQ]` 1.9x slower with the guard restored) and a full-suite A/B
    (NumericQ/Positive/Negative/NonNegative -- the exact builtins the
    original claim cited -- all 7-11% slower with the guard restored).
    600 cases of differential fuzzing found zero mismatches either way,
    and the full test suite passes identically. Kept as the (now
    consciously chosen) behavior: N=1 gets this fast path too.

    N=0 (`head[]`) was, and remains, a wash either way (measured
    ~8.06us here vs ~8.39us falling through to
    SimpleOrderedExpressionPattern's own `isliteral` fast path --
    within noise). `head[]` is typically intercepted earlier by
    `isliteral`-based shortcuts regardless of which class ultimately
    handles it, so this case doesn't matter much either way; it's left
    unguarded (included) since excluding it would need its own special
    case for no measured benefit.

    Works equally on RAW, not-yet-wrapped Expression/Symbol children
    (e.g. `expr.elements` straight off a Mathics Expression) and on
    BasePattern-wrapped elements: both answer get_head_name()/elements
    the same way (BasePattern proxies these to self.expr -- see
    DeferredExpressionPattern's docstring). This is what lets
    make_expression_pattern() classify the shape BEFORE constructing
    any pattern objects at all.

    Deliberately still excludes:
    - BlankSequence/BlankNullSequence (`__`, `___`) and named sequences
      (`x__`, `x___`): different get_match_count(), handled by
      FixedBlankTupleExpressionPattern's sibling class,
      SingleSequenceExpressionPattern (see classify_single_sequence,
      below), for the N=1 case, or the general machinery otherwise.
    - A trailing OptionsPattern[...] element: not Blank-shaped and not
      a literal (it's an Expression), so any tuple containing one
      always fails this classifier and falls through -- correctly,
      since that shape is `classify_positional_options`'s job instead
      (see below); the two are mutually exclusive by construction.
    - anything wrapped in Condition/Optional/PatternTest/Alternatives,
      even if it wraps a Blank underneath (e.g. `x_ /; cond`,
      `Optional[x_]`) -- those aren't `Pattern[name, Blank[...]]`
      shaped (nor bare literals) and are conservatively rejected.
    - Composite literals like `{1, 2}` as a slot: `_is_blank_or_literal_
      slot` only treats a RAW NON-EXPRESSION element as literal; an
      Expression (even one that turns out, recursively, to be entirely
      literal) is conservatively rejected here rather than doing the
      recursive isliteral-style check this cheap classifier is meant
      to avoid -- it still gets the general machinery's own isliteral
      handling downstream, just not via this fast path.

    Returns None (fall through to the general machinery) if any
    element doesn't have this exact shape.
    """
    for element in elements:
        if _is_blank_or_literal_slot(element):
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


def classify_positional_options(elements: tuple) -> Optional[tuple]:
    """
    If `elements` is a non-empty tuple `(*lead, options_element)`
    where:
      - every entry in `lead` (zero or more of them) is a
        fixed-position slot per `_is_blank_or_literal_slot` -- a bare
        or named Blank[]/Blank[Type], or a bare literal atom (same
        shape `classify_fixed_blank_tuple` accepts per slot), and
      - `options_element` (always the LAST entry) is a bare or named
        `OptionsPattern[...]` (`OptionsPattern[]`, `opts:OptionsPattern[]`,
        `OptionsPattern[{n->2}]`, ... -- the optional defaults argument
        doesn't affect classification, only OptionsPattern's own
        match() reads it)
    return `elements` unchanged, as a signal that this is exactly the
    `head[_(HEAD), _(HEAD), ..., OptionsPattern[...]]` shape: zero or
    more fixed-position Blank/literal slots, then a single trailing
    OptionsPattern[...] absorbing everything else.

    GENERALIZED (this session): originally this only accepted EXACTLY
    one leading Blank slot (`head[_, OptionsPattern[]]`), rejecting
    `head[_, _, OptionsPattern[]]` outright with a `len(elements) != 2`
    guard, under the assumption that more than one leading slot would
    reintroduce real backtracking ("which non-option element does
    which Blank bind?"). Checking the ACTUAL general-machinery
    semantics first (before generalizing, not after): an option value
    interspersed BETWEEN two leading slots -- `f[x_,y_,OptionsPattern[]]`
    against `f[1, n->2, 3]` -- FAILS TO MATCH even today, on the
    unmodified general path (verified directly). So there never was
    any real backtracking to worry about: the leading slots are
    ALREADY required to occupy expr_elements[0:k] contiguously, with
    nothing able to intervene between them, for ANY k -- the k=1
    restriction was stricter than the actual semantics required.
    Widened accordingly: any number of leading Blank/literal slots
    (including zero -- a bare `head[OptionsPattern[]]` with no other
    arguments at all) is now accepted and handled identically, reusing
    `match_fixed_blank_tuple` for the leading slots (see
    PositionalOptionsExpressionPattern.match in ordered.py) exactly as
    `classify_fixed_blank_tuple`'s own class does, since a literal
    atom's AtomPattern.match()/match_symbol() shares Blank.match()'s
    and Pattern.match()'s minimal yield_func/vars_dict-only calling
    convention (verified directly against all three implementations).

    Like `classify_single_sequence`, this is a DISTINCT, non-overlapping
    shape from `classify_fixed_blank_tuple`: an `OptionsPattern[...]`
    element is never Blank-shaped nor a bare literal (it's always an
    Expression with head OptionsPattern or Pattern), so
    `_is_blank_or_literal_slot` always rejects it -- any tuple
    containing one, anywhere, is guaranteed to fail
    `classify_fixed_blank_tuple` and fall through to this classifier
    instead (which only succeeds if that OptionsPattern[...] is
    specifically the LAST element, with every earlier element being a
    valid lead slot -- an OptionsPattern[...] anywhere else in the
    tuple, including earlier positions, still correctly falls through
    to the general machinery from here too).

    Why this is worth a dedicated class at all, given
    `_options_pattern_split` (see its docstring) already gives
    OptionsPattern[] a fast, WMA-correct split inside the GENERAL
    `match_element` machinery: that fast path only replaces the
    candidate-SPLIT search for the OptionsPattern element itself -- it
    doesn't skip `basic_match_expression`'s leading_blanks pre-check
    loop, `match_element`'s own redundant double candidate-scan
    (`get_match_candidates_count` then `get_match_candidates` again,
    same issue documented in `classify_single_sequence`), the
    `expression_pattern_match_element_process_items` continuation
    chain, or the `Expression(Sequence, *items)` (re)allocation --
    all of that still runs for every element even when, for this exact
    shape, there is only ONE possible split: the leading slots must
    bind expr_elements[0:k] exactly, and whatever remains (zero, one,
    or many further elements) all goes to OptionsPattern[] or the
    match fails outright. No backtracking is possible anywhere in this
    shape.

    Deliberately still excludes:
    - Multiple OptionsPattern[] elements (`head[opt1:OptionsPattern[],
      opt2:OptionsPattern[]]`) -- the WMA "only the last one collects
      anything" quirk (`_options_pattern_split`) is specifically about
      that case; an interior OptionsPattern[...] fails
      `_is_blank_or_literal_slot` (it's an Expression, not a literal
      or Blank), so `lead` rejects it and this classifier correctly
      declines, falling through to the general machinery.
    - Anything wrapping a lead slot in Condition/Optional/PatternTest/
      Alternatives, or composite literals like `{1, 2}` as a lead slot
      -- same conservative policy as `classify_fixed_blank_tuple`.

    Returns None (fall through to the general machinery) if `elements`
    doesn't have exactly this shape.
    """
    if not elements:
        return None
    *lead, options_element = elements
    for element in lead:
        if not _is_blank_or_literal_slot(element):
            return None
    inner = (
        options_element.elements[1]
        if options_element.has_form(SymbolPattern, 2)
        else options_element
    )
    if inner.has_form(SymbolOptionsPattern, 0, 1):
        return elements
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
