# -*- coding: utf-8 -*-
from typing import Any, Callable, Union

from mathics.core.convert.python import from_python
from mathics.core.expression import Expression, convert_expression_elements
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolList


def to_expression(
    head: Union[str, Symbol],
    *elements: Any,
    elements_conversion_fn: Callable = from_python
) -> Expression:
    """
    This is an expression constructor that can be used when the Head and elements are not Mathics
    objects. For example to_expression("Plus", 1, 2, 3)
    """
    if isinstance(head, str):
        head = Symbol(head)

    # # The below code should disappear after we have gone over the entire code base
    # # to replace all calls of the form ListExpression(...) or
    # # to_expression("List", ...)
    # if head is SymbolList:
    #    from mathics.core.convert.expression import to_mathics_list
    #    return to_mathics_list(elements)

    elements_tuple, elements_properties = convert_expression_elements(
        elements, elements_conversion_fn
    )

    return Expression(head, *elements_tuple, elements_properties=elements_properties)


def to_mathics_list(
    *elements: Any, elements_conversion_fn: Callable = from_python, is_literal=False
) -> Expression:
    """
    This is an expression constructor for list that can be used when the elements are not Mathics
    objects. For example:
       to_mathics_list(1, 2, 3)
       to_mathics_list(1, 2, 3, elements_conversion_fn=Integer, is_literal=True)
    """
    elements_tuple, elements_properties = convert_expression_elements(
        elements, elements_conversion_fn
    )
    list_expression = ListExpression(
        *elements_tuple, elements_properties=elements_properties
    )
    if is_literal:
        list_expression.python_list = elements
    return list_expression


expression_constructor_map = {
    SymbolList: lambda head, *args, **kwargs: ListExpression(*args, **kwargs)
}


def make_expression(head, *elements, **kwargs) -> Expression:
    """
    Use this to create the right kind of *customized* Expression, e.g. a ListExpression
    for a given head.
    """
    constructor_fn = expression_constructor_map.get(head, Expression)
    return constructor_fn(head, *elements, **kwargs)
