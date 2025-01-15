# -*- coding: utf-8 -*-

from abc import ABC
from typing import Optional


class Structure(ABC):
    """
    Structure helps implementations make the ExpressionCache not invalidate across simple commands
    such as Take[], Most[], etc. without this, constant reevaluation of lists happens, which results
    in quadratic runtimes for command like Fold[#1+#2&, Range[x]].

    A good performance test case for Structure: x = Range[50000]; First[Timing[Partition[x, 15, 1]]]
    """

    def __call__(self, elements):
        """Return an Expression with the given list "elements" as elements.
        The caller guarantees that "elements" only contains items that are from "origins
        """
        raise NotImplementedError

    def filter(self, expr, condition, count: Optional[int] = None):
        """
        Returns self type consisting of `expr` filtered by `condition`.
        If `count` is not None, return at most `count` elements.
        """
        if count is None:
            result = [element for element in expr.elements if condition(element)]
        else:
            result = []
            for element in expr.elements:
                if condition(element):
                    result.append(element)
                    count -= 1
                    if count == 0:
                        break

        return self(result)

    def slice(self, expr, py_slice):
        """create an Expression, using the given slice of "expr".elements as elements.
        The caller guarantees that "expr" is from "origins"."""
        raise NotImplementedError


class UnlinkedStructure(Structure):
    """
    UnlinkedStructure produces Expressions that are not linked to "origins" in terms of cache.
    This produces the same thing as doing Expression(head, *elements).
    """

    def __init__(self, head):
        self._head = head
        self._cache = None

    def __call__(self, elements):
        from mathics.core.expression import Expression

        # FIXME: This is possibly the last remaining place where
        # we seem to to require Expression(System`List, ... )
        # and can't use ListExpression(...).
        # It may be in formatting of RowBoxes, so that may take care of itself
        # when we revise Boxing and formatting.
        # Also make sure to test via test/test_series.py
        # Of course, a failure would would be in something poorly documented and the smells hacky
        # or misguided involving a home-grown caching system.
        return Expression(self._head, *elements)

        # from mathics.core.convert.expression import to_expression_with_specialization
        # return to_expression_with_specialization(self._head, *new_elements)

    def slice(self, expr, py_slice):
        elements = expr.elements
        lower, upper, step = py_slice.indices(len(elements))
        if step != 1:
            raise ValueError("Structure.slice only supports slice steps of 1")
        return self(elements[lower:upper])


class LinkedStructure(Structure):
    """
    LinkedStructure produces Expressions that are linked to "origins" in terms of cache. This
    carries over information from the cache of the originating Expressions into the Expressions
    that are newly created.
    """

    def __init__(self, head, cache):
        self._head = head
        self._cache = cache

    def __call__(self, elements):
        from mathics.core.expression import Expression

        expr = Expression(self._head)
        expr.elements = tuple(elements)
        expr._cache = self._cache.reordered()
        return expr

    def slice(self, expr, py_slice):
        elements = expr.elements
        lower, upper, step = py_slice.indices(len(elements))
        if step != 1:
            raise ValueError("Structure.slice only supports slice steps of 1")

        from mathics.core.expression import Expression

        new = Expression(self._head)
        new.elements = elements[lower:upper]
        if expr._cache:
            new._cache = expr._cache.sliced(lower, upper)

        return new
