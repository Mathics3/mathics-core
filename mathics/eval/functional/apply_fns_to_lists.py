"""
Evaluation routines for mathics.builtin.functional.appy_fns_to_lists
"""
from mathics.core.atoms import Integer
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import PartRangeError
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolMapAt, SymbolRule


def eval_MapAt(f, expr, args, evaluation: Evaluation):
    m = len(expr.elements)
    new_elements = list(expr.elements)

    def map_at_replace_one(i: int):
        if 1 <= i <= m:
            j = i - 1
        elif -m <= i <= -1:
            j = m + i
        else:
            evaluation.message("MapAt", "partw", ListExpression(Integer(i)), expr)
            raise PartRangeError
        replace_element = new_elements[j]
        if hasattr(replace_element, "head") and replace_element.head is Symbol(
            "System`Rule"
        ):
            new_elements[j] = Expression(
                SymbolRule,
                replace_element.elements[0],
                Expression(f, replace_element.elements[1]),
            )
        else:
            new_elements[j] = Expression(f, replace_element)

    try:
        if isinstance(args, Integer):
            map_at_replace_one(args.value)
            return ListExpression(*new_elements)
        elif isinstance(args, Expression):
            for item in args.elements:
                # Get value for arg in expr.elemnts
                # Replace value
                if (
                    isinstance(item, Expression)
                    and len(item.elements) == 1
                    and isinstance(item.elements[0], Integer)
                ):
                    map_at_replace_one(item.elements[0].value)
            return ListExpression(*new_elements)
        else:
            evaluation.message(
                "MapAt", "psl", args, Expression(SymbolMapAt, f, expr, args)
            )
    except PartRangeError:
        return
