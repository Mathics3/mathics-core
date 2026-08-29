"""
DeferredExpressionPattern

Implement an ExpressionPattern with a lazzy implementation of its `match` method.

"""

from typing import Optional

from mathics.core.attributes import A_ORDERLESS
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression

from .base import BasePattern, ExpressionPattern
from .ordered import OrderedExpressionPattern
from .orderless import OrderlessExpressionPattern


class DeferredExpressionPattern(ExpressionPattern):
    """
    Wraps an expression whose head's attributes (and therefore whether
    it should be an OrderedExpressionPattern or an
    OrderlessExpressionPattern) aren't known yet -- e.g. during
    Definitions bootstrap, before all SetAttributes[] calls have run, or
    for a nested sub-pattern built without an `evaluation` context.

    On first real use (the first .match() call, since that's the first
    point an Evaluation is guaranteed to be available), it resolves to
    the correct concrete pattern via make_expression_pattern(), caches
    it, and delegates to it from then on.

    Every other BasePattern method (sameQ, pattern_precedence,
    element_order, get_head_name, get_lookup_name, ...) is answered
    directly by the BasePattern base class from self.expr, without
    needing resolution -- none of those depend on Orderless-ness. This
    was verified against every caller of those methods that can run
    before an Evaluation exists (Definitions.insert_rule,
    BaseRule.element_order/pattern_precedence, eval.patterns.Matcher).
    Do not add new pre-match behavior here without checking that it's
    similarly attribute-independent, or route it through _resolve()
    instead.

    Resolution happens once, lazily, on first real use (whichever
    .match() call comes first), and is then frozen for the rest of this
    object's life. This matters concretely for `Dispatch[]`: its whole
    point is to compile a pattern once and reuse it, deliberately
    NOT re-deriving attributes on subsequent uses even if SetAttributes
    changes them later (a freshly-typed `expr /. rule`, by contrast,
    builds a brand new pattern object from scratch every time, so it
    naturally sees current attributes without any special
    re-derivation logic here).
    """

    def __init__(self, expr: Expression):
        self.expr: Expression = expr
        self.location = expr.location if hasattr(expr, "location") else None
        # Built without an evaluation, same as ExpressionPattern.__init__
        # would -- these may themselves come back as further
        # DeferredExpressionPattern instances if their own heads'
        # attributes aren't knowable yet either. Needed for
        # pattern_precedence (see _build_pattern_sort_key below), which
        # is purely structural and must work even before resolution.
        self.head = BasePattern.create(expr.head)
        self.elements = [BasePattern.create(element) for element in expr.elements]
        self._impl: Optional[ExpressionPattern] = None

    def _resolve(self, evaluation: Evaluation) -> ExpressionPattern:
        if self._impl is None:
            attributes = self.expr.get_head().get_attributes(evaluation.definitions)
            self._impl = make_expression_pattern(self.expr, attributes, evaluation)
        return self._impl

    def match(self, expression: BaseElement, pattern_context: dict):
        return self._resolve(pattern_context["evaluation"]).match(
            expression, pattern_context
        )

    def __repr__(self):
        return f"<DeferredExpressionPattern: {self.expr}>"


def make_expression_pattern(
    expr: Expression, attributes: int, evaluation: Optional[Evaluation] = None
) -> ExpressionPattern:
    """
    Factory: given `expr` and its head's ALREADY-KNOWN `attributes` int,
    construct the correct concrete pattern class directly -- no
    deferral, no later branching on A_ORDERLESS needed.

    Use this whenever attributes are on hand already (e.g. a Builtin
    class that declares its own attributes statically in Python, or any
    call site that already has an `evaluation` to look them up). For the
    case where attributes are NOT yet knowable (system bootstrap, before
    Definitions is fully populated), use DeferredExpressionPattern
    instead.
    """
    cls = (
        OrderlessExpressionPattern
        if A_ORDERLESS & attributes
        else OrderedExpressionPattern
    )
    return cls(expr, attributes, evaluation)
