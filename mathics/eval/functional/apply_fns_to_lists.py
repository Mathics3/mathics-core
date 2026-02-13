"""
Evaluation routines for mathics.builtin.functional.appy_fns_to_lists
"""

from typing import Iterable, Optional, Union

from mathics.core.atoms import Integer, Integer1
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import PartRangeError
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolTrue
from mathics.core.systemsymbols import SymbolMapAt, SymbolRule
from mathics.eval.testing_expressions import eval_ArrayQ


def eval_MapAt(
    f: BaseElement, expr: ListExpression, args, evaluation: Evaluation
) -> Optional[ListExpression]:
    """
    evaluation routine for MapAt[]
    """

    def map_at_replace_one(elements: Iterable, index: ListExpression, i: int) -> list:
        """
        Perform a single MapAt[] replacement for elements[i].
        Global "f" is used to compute the replacement value,
        and if there is an error, "expr" is used in the error message.
        """
        m = len(elements)
        if 1 <= i <= m:
            j = i - 1
        elif -m <= i <= -1:
            j = m + i
        else:
            evaluation.message("MapAt", "partw", index, expr)
            raise PartRangeError
        new_elements = list(elements)
        replace_element = elements[j]
        if replace_element.has_form(("Rule", "RuleDelayed"), 2):
            new_elements[j] = Expression(
                replace_element.get_head(),
                replace_element.elements[0],
                Expression(f, replace_element.elements[1]),
            )
        else:
            new_elements[j] = Expression(f, replace_element)
        return new_elements

    def map_at_replace_level(
        elements: list,
        remaining_indices: Union[tuple, Integer],
        orig_index: ListExpression,
    ) -> list:
        """Recursive routine to replace remaining indices inside elements which is a portion at some level of
          expr.elements.

        ``elements`` holds the ListExpression list for the portion of the
         top-level ListExpression where we need to still index into.

        Some part of the original ListExpression may have already been traversed.
        ``remaining_indices`` gives the list of indices we still have to index into,
        these will be a suffix ``orig_index``.

        ``orig_index`` is used for error reporting.
        """
        if isinstance(remaining_indices, Integer):
            remaining_indices = (remaining_indices,)

        i_expr = remaining_indices[0]

        if not isinstance(i_expr, Integer):
            evaluation.message(
                "MapAt", "psl", args, Expression(SymbolMapAt, f, expr, args)
            )
            raise PartRangeError
        i = i_expr.value
        m = len(elements)
        if 1 <= i <= m:
            j = i - 1
        elif -m <= i <= -1:
            j = m + i
        else:
            evaluation.message("MapAt", "partw", orig_index, expr)
            raise PartRangeError

        next_level_elements = elements[j]
        if len(remaining_indices) == 1:
            if isinstance(next_level_elements, ListExpression):
                # TODO: Check type of [0].value
                new_list_expr = map_at_replace_one(
                    next_level_elements.elements, orig_index, remaining_indices[0].value
                )
            else:
                new_list_expr = map_at_replace_one(
                    elements, orig_index, remaining_indices[0].value
                )
            return new_list_expr
        elif not isinstance(next_level_elements, ListExpression):
            # We have run out of nesting for indexing.
            evaluation.message("MapAt", "partw", orig_index, expr)
            raise PartRangeError

        else:
            # len(remaining_indices) > 1 and isinstance(next_level_elements, ListExpression)
            elements[j] = ListExpression(
                *map_at_replace_level(
                    list(next_level_elements.elements),
                    remaining_indices[1:],
                    orig_index,
                )
            )
            return elements

    try:
        if isinstance(args, Integer):
            new_list_expr = map_at_replace_one(
                list(expr.elements), ListExpression(args), args.value
            )
        # Is args a vector?
        elif eval_ArrayQ(args, Integer1, None, evaluation) is SymbolTrue:
            new_list_expr = map_at_replace_level(
                list(expr.elements), args.elements, args
            )
        # Until we can find what's causing Expression, SymbolConstant List from being a ListExpression,
        # we will include Expression below...
        elif isinstance(args, (ListExpression, Expression)):
            new_list_expr = list(expr.elements)
            for item in args.elements:
                if isinstance(item, ListExpression):
                    new_list_expr = map_at_replace_level(
                        new_list_expr, item.elements, item
                    )
                else:
                    new_list_expr = map_at_replace_level(
                        new_list_expr, item.elements, ListExpression(item)
                    )
            return ListExpression(*new_list_expr)
        else:
            evaluation.message(
                "MapAt", "psl", args, Expression(SymbolMapAt, f, expr, args)
            )
            raise PartRangeError
        return ListExpression(*new_list_expr)
    except PartRangeError:
        # A message was issued where the error occurred
        return
