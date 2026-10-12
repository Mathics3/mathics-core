"""
Partial order between rules, based on set inclusion of the expressions
that each rule can match.

Mathematica does not sort DownValues with a total order. A rule is
moved before another one only when it is *strictly more specific*
(everything it matches is also matched by the other one). Rules that
are not comparable keep the order in which they were defined. Packages
such as Combinatorica rely on that.

``rule_le(r, e)`` is True when it can be proved that the set of
expressions matched by rule ``r`` is contained in the one matched by
``e``. The test is conservative: when it is unsure, it answers False,
which means "not comparable".

A rule is analyzed into a ``RuleShape``:

  * ``head``: the head of the left-hand side;
  * ``items``: the arguments, each one a tuple ``(kind, ...)``;
  * ``restrictions``: opaque conditions (``/;`` in the left or right
    hand side, ``?test``, repeated pattern names). A rule with
    restrictions matches a subset of what the same rule without them
    would match, but nothing can be said about two different
    restrictions.

If some part of a pattern is not understood (``Alternatives``,
``Except``, ``Optional``, ...), ``analyze_rule`` returns None and the
caller should fall back to the old sort keys.
"""

from enum import Enum
from typing import FrozenSet, List, Optional, Tuple

from mathics.core.expression import Expression
from mathics.core.symbols import Atom
from mathics.core.systemsymbols import (
    SymbolBlank,
    SymbolBlankNullSequence,
    SymbolBlankSequence,
    SymbolCondition,
    SymbolPattern,
    SymbolPatternTest,
)


# Kinds of items
class ItemType(Enum):
    LIT = "lit"  # ("lit", expr)                      exactly one element: expr
    ONE = "one"  # ("one", head_or_None, restr)       Blank
    PLUS = "plus"  # ("plus", head_or_None, restr)    BlankSequence
    STAR = "star"  # ("star", head_or_None, restr)    BlankNullSequence
    EXPR = "expr"  # ("expr", head, items, restr)     compound subpattern


_BLANKS = {
    SymbolBlank: ItemType.ONE,
    SymbolBlankSequence: ItemType.PLUS,
    SymbolBlankNullSequence: ItemType.STAR,
}


class RuleShape:
    __slots__ = ("head", "items", "restrictions")

    def __init__(self, head, items, restrictions):
        self.head = head
        self.items = items
        self.restrictions = restrictions


class _Unsupported(Exception):
    pass


_SPECIAL_HEADS = {
    "Alternatives",
    "Except",
    "Optional",
    "Repeated",
    "RepeatedNull",
    "Longest",
    "Shortest",
    "Verbatim",
    "PatternSequence",
    "OptionsPattern",
    "Default",
    "HoldPattern",
}


def _is_special(head) -> bool:
    name = head.get_name() if hasattr(head, "get_name") else ""
    return name.startswith("System`") and name[7:] in _SPECIAL_HEADS


def _is_pattern_free(expr) -> bool:
    """True if `expr` contains no pattern constructs at all."""
    if isinstance(expr, Atom):
        return True
    head = expr.head
    if head in (
        SymbolBlank,
        SymbolBlankSequence,
        SymbolBlankNullSequence,
        SymbolPattern,
        SymbolCondition,
        SymbolPatternTest,
    ):
        return False
    if _is_special(head):
        return False
    return _is_pattern_free(head) and all(_is_pattern_free(e) for e in expr.elements)


def _item(expr) -> tuple:
    """Convert one argument of a pattern into an item tuple."""
    restr: List = []
    while isinstance(expr, Expression):
        head = expr.head
        if head is SymbolPattern and len(expr.elements) == 2:
            expr = expr.elements[1]
        elif head is SymbolPatternTest and len(expr.elements) == 2:
            restr.append(("test", expr.elements[1]))
            expr = expr.elements[0]
        elif head is SymbolCondition and len(expr.elements) == 2:
            restr.append(("cond", expr.elements[1]))
            expr = expr.elements[0]
        else:
            break
    restr_set = frozenset(restr)
    if isinstance(expr, Expression) and expr.head in _BLANKS:
        kind = _BLANKS[expr.head]
        if len(expr.elements) == 0:
            return (kind, None, restr_set)
        if len(expr.elements) == 1:
            return (kind, expr.elements[0], restr_set)
        raise _Unsupported
    if _is_pattern_free(expr):
        if restr_set:
            raise _Unsupported
        return (ItemType.LIT, expr)
    if (
        isinstance(expr, Expression)
        and _is_pattern_free(expr.head)
        and not _is_special(expr.head)
    ):
        items = tuple(_item(e) for e in expr.elements)
        return (ItemType.EXPR, expr.head, items, restr_set)
    raise _Unsupported


def _repeated_names(elements) -> FrozenSet:
    """Repeated names among the top level arguments, as a restriction."""
    groups: dict = {}
    for i, e in enumerate(elements):
        if isinstance(e, Expression) and e.head is SymbolPattern:
            groups.setdefault(e.elements[0], []).append(i)
    return frozenset(("same", tuple(ix)) for ix in groups.values() if len(ix) > 1)


def analyze_rule(rule) -> Optional[RuleShape]:
    """Return the RuleShape of `rule`, or None if it is not understood."""
    cached: Optional[RuleShape] | int = getattr(rule, "_specificity_shape", 0)
    if not isinstance(cached, int):
        return cached
    shape = None
    try:
        if type(rule.pattern).__name__ == "OrderlessExpressionPattern":
            raise _Unsupported
        expr = rule.pattern.expr
        restr: List = []
        while (
            isinstance(expr, Expression)
            and expr.head is SymbolCondition
            and len(expr.elements) == 2
        ):
            restr.append(("cond", expr.elements[1]))
            expr = expr.elements[0]
        if (
            isinstance(expr, Expression)
            and _is_pattern_free(expr.head)
            and not _is_special(expr.head)
        ):
            items = tuple(_item(e) for e in expr.elements)
            replace = getattr(rule, "replace", None)
            if (
                replace is not None
                and isinstance(replace, Expression)
                and replace.head is SymbolCondition
                and len(replace.elements) == 2
            ):
                restr.append(("cond", replace.elements[1]))
            restr.extend(_repeated_names(expr.elements))
            shape = RuleShape(expr.head, items, frozenset(restr))
    except _Unsupported:
        shape = None
    try:
        rule._specificity_shape = shape
    except AttributeError:
        pass
    return shape


def _head_of_literal(expr):
    return expr.get_head()


def _head_ok(h_inner, h_outer) -> bool:
    return h_outer is None or (h_inner is not None and h_inner.sameQ(h_outer))


def _item_le(a: tuple, b: tuple) -> bool:
    """Every single element matched by item `a` is matched by item `b`.

    Only the "per element" part is considered here: whether the item is
    one element or a run of elements is handled by `_items_le`.
    """
    ka, kb = a[0], b[0]
    if kb is ItemType.LIT:
        return ka is ItemType.LIT and a[1].sameQ(b[1])
    # restrictions of b must all be present in a
    rb = b[-1]
    ra = a[-1] if ka is not ItemType.LIT else frozenset()
    if not rb <= ra:
        return False
    if kb is ItemType.EXPR:
        if ka is not ItemType.EXPR or not a[1].sameQ(b[1]):
            return False
        return _items_le(a[2], b[2])
    # b is some kind of blank
    hb = b[1]
    if ka is ItemType.LIT:
        return _head_ok(_head_of_literal(a[1]), hb)
    if ka is ItemType.EXPR:
        return _head_ok(a[1], hb)
    return _head_ok(a[1], hb)


def _min_len(it: tuple) -> int:
    return 0 if it[0] is ItemType.STAR else 1


def _is_fixed(it: tuple) -> bool:
    return it[0] in (ItemType.LIT, ItemType.ONE, ItemType.EXPR)


def _items_le(p: Tuple, q: Tuple) -> bool:
    """Every sequence of arguments matched by `p` is matched by `q`.

    Sufficient condition: the arguments of `p` can be assigned, in order,
    to the items of `q`, such that a fixed item of `q` receives exactly
    one fixed item, and variable items of `q` receive items whose
    elements they accept (and a ``__`` receives at least one element).
    """
    n, m = len(p), len(q)
    memo: dict = {}

    def go(i: int, k: int) -> bool:
        if (i, k) in memo:
            return memo[(i, k)]
        if k == m:
            res = i == n
        else:
            qk = q[k]
            res = False
            if _is_fixed(qk):
                res = (
                    i < n
                    and _is_fixed(p[i])
                    and _item_le(p[i], qk)
                    and go(i + 1, k + 1)
                )
            else:
                need = 1 if qk[0] is ItemType.PLUS else 0
                taken_min = 0
                j = i
                # q[k] receives p[i:j]
                while True:
                    if taken_min >= need and go(j, k + 1):
                        res = True
                        break
                    if j >= n or not _item_le(p[j], qk):
                        break
                    taken_min += _min_len(p[j])
                    j += 1
        memo[(i, k)] = res
        return res

    return go(0, 0)


def rule_le(r, e) -> Optional[bool]:
    """
    True if the set matched by rule `r` is provably contained in the set
    matched by rule `e` (including the case where both are equivalent).
    False if it is not provable. None if some rule is not understood.
    """
    sr, se = analyze_rule(r), analyze_rule(e)
    if sr is None or se is None:
        return None
    if not sr.head.sameQ(se.head):
        return False
    if not se.restrictions <= sr.restrictions:
        return False
    return _items_le(sr.items, se.items)


def rule_lt(r, e) -> Optional[bool]:
    """Like `rule_le`, but strict: `r` is contained in `e` and `e` is not
    contained in `r`."""
    a = rule_le(r, e)
    if a is None:
        return None
    return a and not rule_le(e, r)
