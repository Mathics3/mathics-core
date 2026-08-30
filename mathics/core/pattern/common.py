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
from mathics.core.systemsymbols import SymbolDefault, SymbolOptional

from .base import AtomPattern, BasePattern, ExpressionPattern


def _is_option_like(candidate: BaseElement) -> bool:
    """Same shape check OptionsPattern.get_match_candidates() uses."""
    return candidate.has_form(("Rule", "RuleDelayed"), 2) or candidate.has_form(
        "List", None
    )


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
