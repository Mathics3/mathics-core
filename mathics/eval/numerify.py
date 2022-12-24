# cython: language_level=3
# -*- coding: utf-8 -*-

"""

Produces a new expression equivalent to the original,
s.t. inexact numeric elements are reduced to Real numbers with
the same precision.
This is used in arithmetic evaluations (like `Plus`, `Times`, and `Power` )
and in iterators.

"""

from mathics.core.atoms import Integer, Number
from mathics.core.element import BaseElement, EvalMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.number import dps
from mathics.eval.nevaluator import eval_N


def numerify(self: BaseElement, evaluation: Evaluation) -> "BaseElement":
    """
    Produces a new expression with the inexact numeric elements reduced to Real
    numbers with the same precision.
    This is used in arithmetic evaluations (like `Plus`, `Times`, and `Power` )
    and in iterators.
    """
    if not isinstance(self, Expression):
        return self
    _prec = None
    for element in self._elements:
        if element.is_inexact():
            element_prec = element.get_precision()
            if _prec is None or element_prec < _prec:
                _prec = element_prec
    if _prec is not None:
        new_elements = self.get_mutable_elements()
        for index in range(len(new_elements)):
            element = new_elements[index]
            # Don't "numerify" numbers: they should be numerified
            # automatically by the processing function,
            # and we don't want to lose exactness in e.g. 1.0+I.
            # Also, for compatibility with WMA, numerify just the elements
            # s.t. ``NumericQ[element]==True``
            if not isinstance(element, Number) and element.is_numeric(evaluation):
                n_result = (
                    eval_N(element, evaluation, Integer(dps(_prec)))
                    if isinstance(element, EvalMixin)
                    else element
                )
                if isinstance(n_result, Number):
                    new_elements[index] = n_result
                    continue
                # If Nvalues are not available, just tries to do
                # a regular evaluation
                n_result = (
                    element.evaluate(evaluation)
                    if isinstance(element, EvalMixin)
                    else element
                )
                if isinstance(n_result, Number):
                    new_elements[index] = n_result
        result = Expression(self._head)
        result.elements = new_elements
        return result

    else:
        return self
