# -*- coding: utf-8 -*-
"""
A purely additive, hash-based prefilter for the flat list of RewriteRule
objects held by a Dispatch[] atom.

Design invariant (the only thing that must never break): `candidates(expr)`
always returns a superset, in original relative order, of the rules in
`rules` that could possibly match `expr`. The index is never consulted
in place of the real matcher -- `rule.pattern.match()` always runs on
whatever `candidates()` returns and is the sole source of truth for
whether a rule actually applies. On any doubt about whether a rule can
be soundly indexed, it goes to the always-tried fallback list instead.

This is deliberately scoped to Dispatch[]/Replace[]/ReplaceAll[]/
ReplaceRepeated[] -- NOT to Definitions/downvalues -- so it never has to
deal with rule-list mutation or cache invalidation. A Dispatch[] rule
list is fixed at construction time, and (after the eager-resolution fix)
each rule's compiled pattern is already OrderedExpressionPattern or
OrderlessExpressionPattern by the time this index is built -- never
DeferredExpressionPattern.
"""

from itertools import product
from typing import Dict, List, Optional, Set, Tuple

from mathics.core.attributes import A_FLAT
from mathics.core.pattern.base import AtomPattern, BasePattern
from mathics.core.pattern.ordered import OrderedExpressionPattern
from mathics.core.rules import RewriteRule

# How many leading argument positions we bother building an index for.
# Diminishing returns further in, and it keeps build cost/memory bounded.
MAX_INDEXED_POSITIONS = 2

# Cap on how many keys a single Alternatives position may expand into
# (and, transitively, on the per-rule signature explosion below) --
# keeps pathological `a|b|c|...` lists from blowing up build time/memory.
MAX_ALTERNATIVES_BRANCHES = 16

# Tier 0 (see RuleDispatchIndex docstring): rules where *every* position
# discriminates (no wildcards anywhere) get indexed across their FULL
# arity, not just MAX_INDEXED_POSITIONS -- bounded by these caps so a
# rule with many positions and/or heavy Alternatives use doesn't blow up
# build time/memory. Rules that don't fit stay in the Tier 1 scheme.
FULL_INDEX_MAX_ARITY = 8
FULL_INDEX_MAX_COMBOS_PER_RULE = 64

# A discriminator key is either:
#   ("lit", <atom>)   -- position requires sameQ-equality with a literal
#   ("head", <Symbol>) -- position requires Head[arg] is exactly this Symbol
DiscriminatorKey = Tuple[str, object]


def _unwrap_transparent(sub_pattern: BasePattern) -> BasePattern:
    """
    Peel off any leading, structurally-transparent wrapper -- named
    Pattern[name, inner], Condition[inner, test], PatternTest[inner,
    test] -- to reach the real pattern underneath, for indexing
    purposes only (mirrors the set of headers that
    mathics.eval.assignments.assignment.get_reference_expression
    treats as transparent for classifying a rule, plus named Pattern).

    Deliberately does NOT unwrap Verbatim[inner]: unlike the others,
    Verbatim changes the meaning of what's inside (it stops being a
    pattern and becomes literal data to compare against), so looking
    "through" it would be wrong, not just overly cautious.
    """
    from mathics.builtin.patterns.composite import Pattern as PatternObj
    from mathics.builtin.patterns.restrictions import Condition, PatternTest

    while isinstance(sub_pattern, (PatternObj, Condition, PatternTest)):
        sub_pattern = sub_pattern.pattern
    return sub_pattern


def _is_variable_length(sub_pattern: BasePattern) -> bool:
    """
    True if this compiled sub-pattern can consume a number of source
    elements other than exactly one (zero, or an unbounded sequence).
    Such a pattern breaks the notion of "argument position N" for the
    *whole rule*, not just for this position, since every element to
    its right shifts.

    Recurses into Alternatives: `x__ | y_` is variable-length overall
    even though one of its branches (`y_`) isn't, because *some* match
    of this position could still consume more than one element.
    """
    from mathics.builtin.patterns.basic import BlankNullSequence, BlankSequence
    from mathics.builtin.patterns.composite import Alternatives, Repeated
    from mathics.builtin.patterns.defaults import Optional

    inner = _unwrap_transparent(sub_pattern)
    if isinstance(inner, (BlankSequence, BlankNullSequence, Optional, Repeated)):
        return True
    if isinstance(inner, Alternatives):
        return any(_is_variable_length(branch) for branch in inner.alternatives)
    return False


def _discriminator(sub_pattern: BasePattern) -> Optional[DiscriminatorKey]:
    """
    Return a *necessary* condition for a match at this position, or
    None if the position can't be used to prefilter (it structurally
    accepts more than exactly one concrete value/type at this spot --
    untyped Blank, Alternatives, Except, a nested compound sub-pattern,
    etc.) This function is conservative on purpose: returning None just
    means "no filtering help from this position", never "reject". Only
    AtomPattern (literal, via sameQ), a head-typed Blank (`_h`, `x_h`),
    and Verbatim[expr] (literal match against the exact held
    expression, via sameQ) are ever used as discriminators -- all three
    are conditions the real matcher enforces unconditionally regardless
    of any other clause (a wrapping Condition/PatternTest only adds
    constraints, never loosens what's underneath), so excluding based
    on them can never throw away a true match.
    """
    from mathics.builtin.patterns.basic import Blank
    from mathics.builtin.patterns.composite import Verbatim

    inner = _unwrap_transparent(sub_pattern)
    if isinstance(inner, AtomPattern) and inner.isliteral:
        return ("lit", inner.atom)
    if isinstance(inner, Blank) and inner.target_head is not None:
        return ("head", inner.target_head)
    if isinstance(inner, Verbatim) and inner.content is not None:
        return ("lit", inner.content)
    return None


def _discriminator_set(sub_pattern: BasePattern) -> Optional[List[DiscriminatorKey]]:
    """
    Like `_discriminator`, but for Alternatives[p1, p2, ...]: if *every*
    branch has its own valid discriminator, return the list of all of
    them -- the rule can be safely filed under each literal/type key,
    since matching any one alternative is sufficient. If even one
    branch has no discriminator (e.g. `1 | x_`, where `x_` matches
    anything), the whole position degrades to a wildcard: we can't
    enumerate "one specific value, or literally anything else" as a
    finite set of keys, and returning a partial list would silently
    exclude the wildcard branch's matches -- unsound. Capped to avoid
    build-time blowup from large Alternatives lists.
    """
    from mathics.builtin.patterns.composite import Alternatives

    inner = _unwrap_transparent(sub_pattern)
    if isinstance(inner, Alternatives):
        keys: List[DiscriminatorKey] = []
        seen = set()
        for branch in inner.alternatives:
            branch_keys = _discriminator_set(branch)
            if branch_keys is None:
                return None
            for k in branch_keys:
                if k not in seen:
                    seen.add(k)
                    keys.append(k)
            if len(keys) > MAX_ALTERNATIVES_BRANCHES:
                return None
        return keys
    single = _discriminator(sub_pattern)
    return None if single is None else [single]


def _unwrap_hold_pattern(pattern):
    """
    Peel off any leading structurally-transparent wrapper --
    HoldPattern[...], Condition[...], PatternTest[...] -- to reach the
    real compiled Ordered/OrderlessExpressionPattern underneath, for
    indexing purposes only. None of these change how matching itself
    works (their .match() delegates to the inner pattern, possibly
    adding a constraint), so this doesn't change matching semantics --
    it only affects which object we inspect to decide *how* to index
    the rule. This matters in practice for two common shapes:
    `DownValues[f]`/`UpValues[f]`/etc. always come back as
    `HoldPattern[lhs] :> rhs`, and a rule like `f[x_Integer] /; x>0`
    or `f[x_]?test -> rhs` has Condition/PatternTest at the very top.
    Without unwrapping, none of these would ever get indexed.
    """
    from mathics.builtin.patterns.composite import HoldPattern
    from mathics.builtin.patterns.restrictions import Condition, PatternTest

    while isinstance(pattern, (HoldPattern, Condition, PatternTest)):
        pattern = pattern.pattern
    return pattern


class RuleDispatchIndex:
    """
    Wraps a flat, ordered list of RewriteRule (as built by Dispatch[])
    and offers `candidates(expr)` as a fast, sound prefilter. Also
    supports plain iteration/len so existing call sites that treat it
    as "the list of rules" keep working unchanged (just without the
    speedup) if they don't call `candidates()`.

    Two tiers, both keyed by combined tuples (never per-position sets +
    intersection):

    Tier 0 -- full-arity, exact-or-typed dispatch. A rule where *every*
    position discriminates (no wildcards anywhere -- e.g. `F[1,2]`, or
    `F[_Integer,_Integer,_Integer,_Integer]`) is indexed across its
    WHOLE arity, not capped at MAX_INDEXED_POSITIONS. A query first
    tries the expression's own "exact" key (literal values, e.g. the
    `F[1,2]` case) and its "type shape" key (`F[_Integer,_Integer]`,
    i.e. Head of each argument) -- and everything in between, since a
    rule can mix literal and typed positions. This is what actually
    behaves like Dispatch[] in WMA: an expression resolves to a
    hash bucket directly, with no dependence on how many arguments it
    has.

    Tier 1 -- partial dispatch, capped at MAX_INDEXED_POSITIONS. Catches
    everything that doesn't qualify for Tier 0 (some wildcard position,
    or too many positions/Alternatives branches to bound Tier 0's
    combos) but can still be usefully narrowed by looking at its first
    couple of positions, with an explicit ("wild",) marker elsewhere.
    """

    def __init__(self, rules: List[RewriteRule]):
        self._rules = rules
        self._fallback_ids: Set[int] = set()
        # (head, arity) -> { combined_signature_tuple -> [rule_id, ...] }
        self._groups: Dict[Tuple[object, int], Dict[Tuple, List[int]]] = {}
        # Same shape, but keyed across the FULL arity (Tier 0).
        self._full_groups: Dict[Tuple[object, int], Dict[Tuple, List[int]]] = {}
        self._build()

    def __iter__(self):
        return iter(self._rules)

    def __len__(self):
        return len(self._rules)

    def _build(self) -> None:
        for i, rule in enumerate(self._rules):
            pattern = _unwrap_hold_pattern(rule.pattern)
            if not isinstance(pattern, OrderedExpressionPattern):
                # OrderlessExpressionPattern (position isn't a stable
                # concept) or, defensively, a still-Deferred pattern.
                self._fallback_ids.add(i)
                continue
            if A_FLAT & pattern.attributes:
                # Verified empirically (not just by reading the matcher)
                # that this matters: myPlus[a_,b_] with Flat DOES match
                # myPlus[x,y,z] via regrouping (a_=x, b_=myPlus[y,z]),
                # even though len(pattern.elements)=2 != len(expr.elements)=3.
                # Grouping strictly by (head, exact arity) would make
                # this rule unreachable from candidates() for any arity
                # other than its literal one -- a real soundness bug,
                # not just a missed optimization. Fallback for now.
                self._fallback_ids.add(i)
                continue
            elements = pattern.elements
            if any(_is_variable_length(e) for e in elements):
                self._fallback_ids.add(i)
                continue

            key = (pattern.head.expr, len(elements))

            # Tier 0: try full-arity indexing first -- only viable when
            # *every* position has a discriminator (no wildcards) and
            # the resulting combo count is bounded.
            if len(elements) <= FULL_INDEX_MAX_ARITY:
                full_keys = [_discriminator_set(e) for e in elements]
                if all(k is not None for k in full_keys):
                    combos = list(product(*full_keys))
                    if len(combos) <= FULL_INDEX_MAX_COMBOS_PER_RULE:
                        full_table = self._full_groups.setdefault(key, {})
                        for combo in combos:
                            full_table.setdefault(combo, []).append(i)
                        continue

            # Tier 1: partial indexing over the first couple of
            # positions, with an explicit wildcard marker elsewhere.
            n_positions = min(len(elements), MAX_INDEXED_POSITIONS)
            per_position_keys = [
                _discriminator_set(elements[pos]) or [("wild",)]
                for pos in range(n_positions)
            ]
            table = self._groups.setdefault(key, {})
            for signature in product(*per_position_keys):
                table.setdefault(signature, []).append(i)

    def candidates(self, expr) -> List[RewriteRule]:
        """
        Return, in original order, a superset of the rules that could
        match `expr`. Always includes every non-indexable (fallback)
        rule; additionally includes indexable rules reachable from one
        of the combined keys derived from `expr`, from either tier.
        """
        if not self._groups and not self._full_groups:
            return self._rules

        eligible: Set[int] = set(self._fallback_ids)

        head = getattr(expr, "head", None)
        elements = getattr(expr, "elements", None)
        if head is not None and elements is not None:
            arity = len(elements)
            group_key = (head, arity)

            # Tier 0: full arity, exact-value-or-type. No wildcard
            # option here -- Tier 0 never stores a ("wild",) entry, so
            # trying one would only ever be a guaranteed-miss lookup.
            full_table = self._full_groups.get(group_key)
            if full_table is not None:
                options_per_position = []
                for pos in range(arity):
                    arg = elements[pos]
                    opts = [("lit", arg)]
                    arg_head = arg.get_head() if hasattr(arg, "get_head") else None
                    if arg_head is not None:
                        opts.append(("head", arg_head))
                    options_per_position.append(opts)
                for combo in product(*options_per_position):
                    ids = full_table.get(combo)
                    if ids:
                        eligible.update(ids)

            # Tier 1: partial, capped at the first couple of positions,
            # with an explicit wildcard option.
            table = self._groups.get(group_key)
            if table is not None:
                n_positions = min(arity, MAX_INDEXED_POSITIONS)
                options_per_position = []
                for pos in range(n_positions):
                    arg = elements[pos]
                    # Always try the literal key, atomic or not -- a
                    # Verbatim[expr] discriminator can hold a compound
                    # expression, not just an atom.
                    opts = [("wild",), ("lit", arg)]
                    arg_head = arg.get_head() if hasattr(arg, "get_head") else None
                    if arg_head is not None:
                        opts.append(("head", arg_head))
                    options_per_position.append(opts)
                for combo in product(*options_per_position):
                    ids = table.get(combo)
                    if ids:
                        eligible.update(ids)

        if len(eligible) == len(self._rules):
            return self._rules
        return [self._rules[i] for i in sorted(eligible)]
