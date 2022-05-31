# -*- coding: utf-8 -*-
from mathics.core.expression import Expression, convert_expression_elements

from typing import Any, Callable, Optional

from mathics.core.atoms import from_python
from mathics.core.element import ElementsProperties
from mathics.core.symbols import SymbolList


class ListExpression(Expression):
    """
    A Mathics List-Expression.

    A Mathics List is a specialization of Expression where the head is SymbolList.

    positional Arguments:
        - *elements - optional: the remaining elements

    Keyword Arguments:
        - element_properties -- properties of the collection of elements
    """

    def __init__(
        self, *elements, elements_properties: Optional[ElementsProperties] = None
    ):
        self.options = None
        self.pattern_sequence = False
        self._head = SymbolList

        assert isinstance(elements, tuple)
        self._elements = elements
        self._is_literal = False
        self.python_list = None
        self.elements_properties = (
            self._build_elements_properties()
            if elements_properties is None
            else elements_properties
        )

        # FIXME: get rid of this junk
        self._sequences = None
        self._cache = None
        # comment @mmatera: this cache should be useful in BoxConstruct, but not
        # here...
        self._format_cache = None

    # def __repr__(self) -> str:
    #     return "<ListExpression: %s>" % self

    @property
    def is_literal(self) -> bool:
        """
        True if the value can't change, i.e. a value is set and it does not
        depend on definition bindings. That is why, in contrast to
        `is_uncertain_final_definitions()` we don't need a `definitions`
        parameter.
        """
        return self._is_literal


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
