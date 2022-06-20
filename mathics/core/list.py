# -*- coding: utf-8 -*-
from mathics.core.expression import Expression, convert_expression_elements

from typing import Any, Callable, Optional, Tuple

from mathics.core.atoms import from_python
from mathics.core.element import ElementsProperties
from mathics.core.symbols import EvalMixin, SymbolList


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

        # For debugging
        # from mathics.core.symbols import BaseElement
        # for element in elements:
        #     if not isinstance(element, BaseElement):
        #          from trepan.api import debug; debug()

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

    # # Add this when it is safe to do.
    # def __repr__(self) -> str:
    #     return "<ListExpression: %s>" % self

    # @timeit
    def evaluate_elements(self, evaluation):
        elements_changed = False
        # Make tuple self._elements mutable by turning it into a list.
        elements = list(self._elements)
        for index, element in enumerate(self._elements):
            if not element.has_form("Unevaluated", 1):
                if isinstance(element, EvalMixin):
                    new_value = element.evaluate(evaluation)
                    # We need id() because != by itself is too permissive
                    if id(element) != id(new_value):
                        elements_changed = True
                        elements[index] = new_value

        if elements_changed:
            # Save changed elements, making them immutable again.
            self._elements = tuple(elements)

            # TODO: we could have a specialized version of this
            # that keeps self.python_list up to date when that is
            # easy to do. That is left of some future time to
            # decide whether doing this this is warranted.
            self._build_elements_properties()
            self.python_list = None

    @property
    def is_literal(self) -> bool:
        """
        True if the value can't change, i.e. a value is set and it does not
        depend on definition bindings. That is why, in contrast to
        `is_uncertain_final_definitions()` we don't need a `definitions`
        parameter.
        """
        return self._is_literal

    def rewrite_apply_eval_step(self, evaluation) -> Tuple[Expression, bool]:
        """
        Perform a single rewrite/apply/eval step of the bigger
        Expression.evaluate() process.

        We return the ListExpression as well as a Boolean False which indicates
        to the caller `evaluate()` that it should consider this a "fixed-point"
        evaluation and not have to iterate calling this routine using the
        returned results.

        Note that this is a recursive process: we may call something
        that may call our parent: evaluate() which calls us again.

        In general, this step is time consuming, complicated, and involved.
        However for a ListExpression, things are much much simpler and faster because
        we don't need the rewrite/apply phases of evaluation.

        """

        if self.elements_properties is None:
            self._build_elements_properties()

        if not self.elements_properties.elements_fully_evaluated:
            self.evaluate_elements(evaluation)

        return self, False


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
