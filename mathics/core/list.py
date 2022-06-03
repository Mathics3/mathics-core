# -*- coding: utf-8 -*-
from mathics.core.expression import Expression, convert_expression_elements
import typing
from typing import Any, Callable, Optional

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

    def rewrite_apply_eval_step(self, evaluation) -> typing.Tuple["Expression", bool]:
        """Perform a single rewrite/apply/eval step of the bigger
        Expression.evaluate() process.

        We return the ListExpression as well as a Boolean which indicates
        whether the caller `evaluate()` should consider reevaluating
        the expression. For lists, once we evaluate a list, we
        never have to re-evaluate it

        Note that this is a recursive process: we may call something
        that may call our parent: evaluate() which calls us again.

        In general that this step is time consuming, complicated, and involved.
        For lists, things are simpler.
        """

        # Step 1 : evaluate the Head and get its Attributes. These attributes, used later, include
        # HoldFirst / HoldAll / HoldRest / HoldAllComplete.

        # Note: self._head can be not just a symbol, but some arbitrary expression.
        # This is what makes expressions in Mathics be M-expressions rather than
        # S-expressions.

        if self.elements_properties is None:
            self._build_elements_properties()

        # @timeit
        def eval_elements():
            # @timeit
            recompute_properties = False
            for index, element in enumerate(elements):
                if not element.has_form("Unevaluated", 1):
                    if isinstance(element, EvalMixin):
                        new_value = element.evaluate(evaluation)
                        # We need id() because != by itself is too permissive
                        if id(element) != id(new_value):
                            recompute_properties = True
                            elements[index] = new_value

            if recompute_properties:
                self._build_elements_properties()

        # Step 2: Build a new expression. If it can be avoided, we take care not
        # to:
        # * evaluate elements,
        # * run to_python() on them in Expression construction, or
        # * convert Expression elements from a tuple to a list and back

        if self.elements_properties.elements_fully_evaluated:
            elements = self._elements
            new = self
        else:
            elements = self.get_mutable_elements()
            # FIXME: see if we can preserve elements properties in eval_elements()
            eval_elements()
            new = ListExpression(*elements)
            new._build_elements_properties()

        # Step 3:  Rebuild the ExpressionCache, which tracks which symbols
        # where involved, the Sequence`s present, and the last time they have changed.

        new._timestamp_cache(evaluation)

        # Step 4: Now,the next step is to look at the rules associated to
        # the upvalues of each element

        def rules():
            rules_names = set()
            for element in elements:
                if not isinstance(element, EvalMixin):
                    continue
                name = element.get_lookup_name()
                if len(name) > 0:  # only lookup rules if this is a symbol
                    if name not in rules_names:
                        rules_names.add(name)
                        for rule in evaluation.definitions.get_upvalues(name):
                            yield rule

        for rule in rules():
            result = rule.apply(new, evaluation, fully=False)
            if result is not None:
                if not isinstance(result, EvalMixin):
                    return result, False
                if result.sameQ(new):
                    new._timestamp_cache(evaluation)
                    return new, False
                else:
                    return result, True

        # Step 7: If we are here, is because we didn't find any rule that matches with the expression.

        dirty_elements = None

        # Expression did not change, re-apply Unevaluated
        for index, element in enumerate(new._elements):
            if hasattr(element, "unevaluated") and element.unevaluated:
                if dirty_elements is None:
                    dirty_elements = list(new._elements)
                dirty_elements[index] = Expression("Unevaluated", element)

        if dirty_elements:
            new = ListExpression(*dirty_elements)

        # Step 8: Update the cache. Return the new compound Expression and indicate that no further evaluation is needed.
        new._timestamp_cache(evaluation)
        return new, False


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
