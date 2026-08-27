# -*- coding: utf-8 -*-

from abc import ABC
from typing import Optional


class Structure(ABC):
    """
    Factory for new Expression objects from existing elements, keeping track of the
    cache metadata when it is required.

    The main contract is that EVERY element in the new expression comes from the origin expression,
    which was passed as arguments when ``Structure`` was built. This ensures that all the symbols
    contained into the new expression are a subset of the original ones, so the cache can be
    safely reused.

    Structure helps implementations make the ExpressionCache not invalidate across simple commands
    such as Take[], Most[], etc. without this, constant reevaluation of lists happens, which results
    in quadratic runtimes for command like Fold[#1+#2&, Range[x]].

    A good performance test case for Structure: x = Range[50000]; First[Timing[Partition[x, 15, 1]]]


    Methods
    -------

    *  ``__call__(elements)``: build a new expression with the given elements.
    *  ``filter(expr, cond, count=None)``: filter elements in ``expr`` according
       the condition ``cond`` and returns a new expression.
    * ``slice(expr, py_slice)``: take an slice of the elements in ``expr`` and returns
      a new expression build on them.

    Note:
    -----
    This mechanism does not modify the original expression; just create new expressions
    sharing the original elements.


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

    This produces the same thing as doing ``Expression(head, *elements)``.
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

    This is crucial for operations like  Take, Drop, Part, Most, Rest, etc.,
    where the elements of the new expression are a subset or reordering of the
    original elements. When the cache is reused, a cache invalidation is avoided,
    and prevent that the metadata be recomputed, reducing the complexity from O(n^2)
    to O(n).


    How the cache is adjusted:

        - In ``__call__`` (for the general re-ordering):
          ``cache.reordered()`` is used, preserving the set of ``symbols``
          but ``sequences`` are marked as ``None`` (because the order have been changed
          and we can not know wheter the indices of elements containing ``Sequence``
          expressions are still valid).
        - In ``slice``: ``cache.sliced(lower, upper)`` is used. It reindex
          the positions of ``Sequence`` elements in the selected range (if ``step==1``)
          keeping the ``symbols`` set without changes.

    RESTRICTION:  ``slice`` just support  ``step=1`` because the reindexing of sequences
    is based on linear indices. For other steps,
    UnlinkedStructure should be used.

    IMPORTANT: even when the cache is inherited, elements_properties are not automatically preserved.
    The new expression will have ``elements_properties=None``, and must be reconstructed on demand,
    at evaluation time. This behavior can be improved.

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
