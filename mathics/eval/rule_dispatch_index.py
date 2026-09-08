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
from mathics.core.symbols import Atom

# How many leading argument positions we bother building an index for.
# Diminishing returns further in, and it keeps build cost/memory bounded.
MAX_INDEXED_POSITIONS = 2

# A discriminator key is either:
#   ("lit", <atom>)   -- position requires sameQ-equality with a literal
#   ("head", <Symbol>) -- position requires Head[arg] is exactly this Symbol
DiscriminatorKey = Tuple[str, object]


def _unwrap_named(sub_pattern: BasePattern) -> BasePattern:
    """If `sub_pattern` is a named Pattern[name, inner], return `inner`.
    Otherwise return `sub_pattern` unchanged."""
    from mathics.builtin.patterns.composite import Pattern as PatternObj

    if isinstance(sub_pattern, PatternObj):
        return sub_pattern.pattern
    return sub_pattern


def _is_variable_length(sub_pattern: BasePattern) -> bool:
    """
    True if this compiled sub-pattern can consume a number of source
    elements other than exactly one (zero, or an unbounded sequence).
    Such a pattern breaks the notion of "argument position N" for the
    *whole rule*, not just for this position, since every element to
    its right shifts.
    """
    from mathics.builtin.patterns.basic import BlankNullSequence, BlankSequence
    from mathics.builtin.patterns.composite import Repeated
    from mathics.builtin.patterns.defaults import Optional

    inner = _unwrap_named(sub_pattern)
    return isinstance(inner, (BlankSequence, BlankNullSequence, Optional, Repeated))


def _discriminator(sub_pattern: BasePattern) -> Optional[DiscriminatorKey]:
    """
    Return a *necessary* condition for a match at this position, or
    None if the position can't be used to prefilter (it structurally
    accepts more than exactly one concrete value/type at this spot --
    untyped Blank, PatternTest, Condition, Alternatives, Except, a
    nested compound sub-pattern, etc.) This function is conservative on
    purpose: returning None just means "no filtering help from this
    position", never "reject". Only AtomPattern (literal, via sameQ)
    and a head-typed Blank (`_h`, `x_h`) are ever used as
    discriminators, because both are conditions the real matcher
    enforces unconditionally, regardless of any other clause -- so
    excluding based on them can never throw away a true match.
    """
    from mathics.builtin.patterns.basic import Blank

    inner = _unwrap_named(sub_pattern)
    if isinstance(inner, AtomPattern) and inner.isliteral:
        return ("lit", inner.atom)
    if isinstance(inner, Blank) and inner.target_head is not None:
        return ("head", inner.target_head)
    return None


class RuleDispatchIndex:
    """
    Wraps a flat, ordered list of RewriteRule (as built by Dispatch[])
    and offers `candidates(expr)` as a fast, sound prefilter. Also
    supports plain iteration/len so existing call sites that treat it
    as "the list of rules" keep working unchanged (just without the
    speedup) if they don't call `candidates()`.

    Unlike a naive per-position filter, this builds ONE combined key per
    rule -- the tuple of per-position discriminators (using an explicit
    ("wild",) marker for positions that don't discriminate) -- and
    stores rules in a single dict keyed by that tuple. A query doesn't
    intersect sets across positions; it computes, for the actual
    expression, the (small) Cartesian product of "what this position
    could plausibly be filed under" -- its literal value, its head type,
    and always the wildcard marker -- and does direct dict lookups for
    each resulting combined key. This mirrors how Dispatch[] in WMA
    resolves an expression to the handful of hash buckets relevant to
    it, rather than filtering position-by-position.
    """

    def __init__(self, rules: List[RewriteRule]):
        self._rules = rules
        self._fallback_ids: Set[int] = set()
        # (head, arity) -> { combined_signature_tuple -> [rule_id, ...] }
        self._groups: Dict[Tuple[object, int], Dict[Tuple, List[int]]] = {}
        self._build()

    def __iter__(self):
        return iter(self._rules)

    def __len__(self):
        return len(self._rules)

    def _build(self) -> None:
        for i, rule in enumerate(self._rules):
            pattern = rule.pattern
            if not isinstance(pattern, OrderedExpressionPattern):
                # OrderlessExpressionPattern (position isn't a stable
                # concept) or, defensively, a still-Deferred pattern.
                self._fallback_ids.add(i)
                continue
            if A_FLAT & pattern.attributes:
                # Flat can regroup elements before matching begins;
                # "argument position N" isn't a fixed slot. Fallback
                # for now -- revisit with evidence if it turns out
                # Flat-without-Orderless still has stable positions.
                self._fallback_ids.add(i)
                continue
            elements = pattern.elements
            if any(_is_variable_length(e) for e in elements):
                self._fallback_ids.add(i)
                continue

            key = (pattern.head.expr, len(elements))
            n_positions = min(len(elements), MAX_INDEXED_POSITIONS)
            signature = tuple(
                _discriminator(elements[pos]) or ("wild",) for pos in range(n_positions)
            )
            table = self._groups.setdefault(key, {})
            table.setdefault(signature, []).append(i)

    def candidates(self, expr) -> List[RewriteRule]:
        """
        Return, in original order, a superset of the rules that could
        match `expr`. Always includes every non-indexable (fallback)
        rule; additionally includes indexable rules reachable from one
        of the combined keys derived from `expr`.
        """
        if not self._groups:
            return self._rules

        eligible: Set[int] = set(self._fallback_ids)

        head = getattr(expr, "head", None)
        elements = getattr(expr, "elements", None)
        if head is not None and elements is not None:
            table = self._groups.get((head, len(elements)))
            if table is not None:
                n_positions = min(len(elements), MAX_INDEXED_POSITIONS)
                options_per_position = []
                for pos in range(n_positions):
                    arg = elements[pos]
                    opts = [("wild",)]
                    if isinstance(arg, Atom):
                        opts.append(("lit", arg))
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
        return [rule for i, rule in enumerate(self._rules) if i in eligible]
