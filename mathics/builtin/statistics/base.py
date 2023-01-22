"""
Base classes for Descriptive Statistics
"""
from mathics.builtin.base import Builtin
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol

# No user docs here.
no_doc = True


class NotRectangularException(Exception):
    pass


class Rectangular(Builtin):
    """
    A base class for statics builtin functions X that allow X[{a1, a2, ...}, {b1, b2, ...}, ...]
    to be evaluated as
    {X[{a1, b1, ...}, {a1, b2, ...}, ...]}.
    """

    no_doc = True

    def rect(self, element: ListExpression):
        lengths = [len(element.elements) for element in element.elements]
        if all(length == 0 for length in lengths):
            return  # leave as is, without error

        n_columns = lengths[0]
        if any(length != n_columns for length in lengths[1:]):
            raise NotRectangularException()

        transposed = [
            [element.elements[i] for element in element.elements]
            for i in range(n_columns)
        ]

        return ListExpression(
            *[
                Expression(Symbol(self.get_name()), ListExpression(*items))
                for items in transposed
            ],
        )
