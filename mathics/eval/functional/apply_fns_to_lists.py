"""
Evaluation routines for mathics.builtin.functional.appy_fns_to_lists
"""

from collections.abc import Sequence
from typing import Optional

from mathics.core.atoms import Integer, Integer1
from mathics.core.atoms.associations import Association
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import InvalidLevelspecError, PartRangeError
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.rules import is_rule
from mathics.core.symbols import Atom, SymbolTrue
from mathics.core.systemsymbols import SymbolAssociation, SymbolMapAt, SymbolRule
from mathics.eval.parts import python_levelspec, walk_levels
from mathics.eval.testing_expressions import eval_ArrayQ


def eval_Map_level(f, expr, levelspec, evaluation: Evaluation, wrap_in_head: bool):
    try:
        start, stop = python_levelspec(levelspec)
    except InvalidLevelspecError:
        evaluation.message("Map", "level", levelspec)
        return

    if isinstance(expr, Association):
        # For Association atoms, create a new association.
        # FIXME: handle wrap_in_head = True
        # FIXME we probably should add another Association constructor that doesn't have to
        # go through Expression(SymbolRule ...).
        rule_list = [
            Expression(SymbolRule, lhs, Expression(f, rhs))
            for lhs, rhs in expr.elements
        ]
        return Association(rule_list)

    is_association = expr.has_form(SymbolAssociation, None)

    def callback(level):
        """
        Map $f$ onto each element (denoted by 'level' here) at this level.
        Except for expr as Association, which is mapped on values only.
        """
        # TODO: This special behavior applies when the whole expression
        # is of the form Association[__(Rule|RuleDelayed)], i.e., when
        # the expression is a well-formatted Association expression.
        # For example,
        # `Map[F, Association[a->1,b->2, NotARule]`
        # produces in WMA
        # `Association[F[a->1], F[b->2], F[NotARule]]`
        # instead of
        # `Association[a->F[1], b->F[2], F[NotARule]`]
        #
        # Fixing this would require a different implementation of this eval_ method.
        #
        if is_association and is_rule(level):
            return Expression(
                level.get_head(),
                level.elements[0],
                Expression(f, level.elements[1]),
            )
        return Expression(f, level)

    result, _ = walk_levels(expr, start, stop, heads=wrap_in_head, callback=callback)

    if isinstance(result, Atom):
        return result
    elem_prop = result.elements_properties
    if elem_prop is not None:
        elem_prop.elements_fully_evaluated = False

    return result


def eval_MapAt(
    f: BaseElement, expr: BaseElement, args, evaluation: Evaluation
) -> Optional[BaseElement]:
    """
    evaluation routine for MapAt[]
    """

    def apply_f(element: BaseElement) -> BaseElement:
        if is_rule(element):
            return Expression(
                element.get_head(),
                element.elements[0],
                Expression(f, element.elements[1]),
            )
        return Expression(f, element)

    def map_at_position(
        part: BaseElement, indices: Sequence[BaseElement], orig_index: BaseElement
    ) -> BaseElement:
        """Return ``part`` with f applied at the position ``indices``
        inside it, keeping the heads of ``part`` and of its subparts.

        ``orig_index`` is the whole position, used for error reporting.
        """
        i_expr = indices[0]
        if not isinstance(i_expr, Integer):
            evaluation.message(
                "MapAt", "psl", args, Expression(SymbolMapAt, f, expr, args)
            )
            raise PartRangeError
        if isinstance(part, Atom):
            evaluation.message("MapAt", "partw", orig_index, expr)
            raise PartRangeError
        elements = list(part.elements)
        i = i_expr.value
        m = len(elements)
        if 1 <= i <= m:
            j = i - 1
        elif -m <= i <= -1:
            j = m + i
        else:
            evaluation.message("MapAt", "partw", orig_index, expr)
            raise PartRangeError

        if len(indices) == 1:
            elements[j] = apply_f(elements[j])
        else:
            elements[j] = map_at_position(elements[j], indices[1:], orig_index)
        if isinstance(part, ListExpression):
            return ListExpression(*elements)
        return Expression(part.get_head(), *elements)

    if isinstance(expr, Association):
        if isinstance(args, Integer):
            i = args.value
            if i > 0:
                i -= 1
            key, value = tuple(expr.items())[i]
            new_value = Expression(f, value)
            update_value = [(key, new_value)]
            expr.update(update_value)
            return expr
    try:
        if isinstance(args, Integer):
            return map_at_position(expr, (args,), ListExpression(args))
        # Is args a vector, i.e. a single position?
        if eval_ArrayQ(args, Integer1, None, evaluation) is SymbolTrue:
            return map_at_position(expr, args.elements, args)
        # Until we can find what's causing Expression, SymbolConstant List from being a ListExpression,
        # we will include Expression below...
        if isinstance(args, (ListExpression, Expression)):
            # A list of positions; each one is a list of indices or an index.
            result = expr
            for item in args.elements:
                if isinstance(item, Atom):
                    result = map_at_position(result, (item,), ListExpression(item))
                else:
                    result = map_at_position(result, item.elements, item)
            return result
        evaluation.message("MapAt", "psl", args, Expression(SymbolMapAt, f, expr, args))
        raise PartRangeError
    except PartRangeError:
        # A message was issued where the error occurred
        return None
