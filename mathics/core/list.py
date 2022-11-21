# -*- coding: utf-8 -*-

import reprlib
from typing import Optional, Tuple

from mathics.core.element import ElementsProperties
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import EvalMixin, Symbol, SymbolList


class ListExpression(Expression):
    """
    A Mathics List-Expression.

    A Mathics List is a specialization of Expression where the head is SymbolList.

    positional Arguments:
        - *elements - optional: the remaining elements

    Keyword Arguments:
        - element_properties -- properties of the collection of elements
        - literal_values -- if this is not None, then it is a tuple of Python values
    """

    def __init__(
        self,
        *elements,
        elements_properties: Optional[ElementsProperties] = None,
        literal_values: Optional[tuple] = None,
    ):
        self.options = None
        self.pattern_sequence = False
        self._head = SymbolList

        # For debugging:

        # if literal_values is not None:
        #     import inspect

        #     curframe = inspect.currentframe()
        #     call_frame = inspect.getouterframes(curframe, 2)
        #     print("caller name:", call_frame[1][3])

        # from mathics.core.element import BaseElement
        # for element in elements:
        #     if not isinstance(element, BaseElement):
        #          from trepan.api import debug; debug()

        self._elements = elements
        self.value = literal_values

        # Check for literalness if it is not known
        if literal_values is None:
            self._is_literal = True
            values = []
            for element in elements:
                if element.is_literal:
                    values.append(element.value)
                else:
                    self._is_literal = False
                    break
            if self._is_literal:
                self.value = tuple(values)

        self.elements_properties = elements_properties

        # FIXME: get rid of this junk
        self._sequences = None
        self._cache = None

    def __getitem__(self, index: int):
        """
        Allows ListExpression elements to accessed via [], e.g.
        ListExpression[Integer1, Integer0][0] == Integer1
        """
        return self._elements[index]

    def __repr__(self) -> str:
        """(reprlib.repr)-limited display or ListExpression"""
        list_data = reprlib.repr(self._elements)
        return f"<ListExpression: {list_data}>"

    def __str__(self) -> str:
        """str() representation of ListExpression. May be longer than repr()"""
        return f"<ListExpression: {self._elements}>"

    # @timeit
    def evaluate_elements(self, evaluation: Evaluation) -> Expression:
        """
        return a new expression with the same head, and the
        evaluable elements evaluated.
        """
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

        if not elements_changed:
            return self

        new_list = ListExpression(*elements)
        # TODO: we could have a specialized version of this
        # that keeps self.value up to date when that is
        # easy to do. That is left of some future time to
        # decide whether doing this this is warranted.
        new_list._build_elements_properties()
        new_list.value = None
        return new_list

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
            new = self.shallow_copy()
            new = new.evaluate_elements(evaluation)
            return new, False
        return self, False

    def set_head(self, head: Symbol):
        """
        Change the Head of an Expression.
        Unless this is a ListExpression, this is forbidden here.
        """
        if head != SymbolList:
            raise TypeError("Attempt to modify the Head of a ListExpression")

    def shallow_copy(self) -> "ListExpression":
        """
        For an Expression this does something with its cache.
        Here this does not need that complication.
        """
        return ListExpression(
            *self._elements, elements_properties=self.elements_properties
        )

    def copy(self, reevaluate=False) -> "Expression":
        expr = ListExpression(self._head.copy(reevaluate))
        expr._elements = tuple(element.copy(reevaluate) for element in self._elements)
        expr.options = self.options
        expr.original = self
        expr._sequences = self._sequences
        return expr
