# cython: language_level=3
# -*- coding: utf-8 -*-

from mathics.core.symbols import (
    Atom,
)
from mathics.core.expression import Expression
from mathics.core.symbols import SymbolList


class ListExpression(Atom):
    """
    This class implements `List` expressions
    as a simplified kind of  `Expression` that does
    not requires to check for evaluation rules.

    """

    class_head_name = "System`List"

    def __new__(cls, leaves):
        # Here we could check if all the leaves are machinereal,
        # and specialize to something like ListMachineReals
        # or ListMachineComplex  or ListNumpy or whatever...
        self = super().__new__(cls)
        self._leaves = leaves
        return self

    def __str__(self) -> str:
        return "{" + ",".join(leaf.__str__() for leaf in self._leaves) + "}"

    def get_head_name(self):
        return "System`List"

    def boxes_to_text(self, **options) -> str:
        # TODO: take into account the MakeBoxes rules...
        raise NotImplementedError

    def boxes_to_mathml(self, **options) -> str:
        # TODO: take into account the MakeBoxes rules...
        raise NotImplementedError

    def boxes_to_tex(self, **options) -> str:
        # TODO: take into account the MakeBoxes rules...
        raise NotImplementedError

    def to_python(self, *args, **kwargs):
        return [leaf.to_python(*args, **kwargs) for leaf in self._leaves]

    def sameQ(self, other):
        if other is self:
            return True
        if isinstance(other, ListExpression):
            if len(other._leaves) != len(self._leaves):
                return False
            return all(a.sameQ(b) for (a, b) in zip(self._leaves, other._leaves))
        if isinstance(other, Expression) and other._head is SymbolList:
            return all(a.sameQ(b) for (a, b) in zip(self._leaves, other._leaves))

        return False

    def evaluate(self, evaluation):
        # TODO: handle upvalues
        new_leaves = tuple(leaf.evaluate(evaluation) for leaf in self._leaves)
        if all(leaf is None for leaf in new_leaves):
            return None
        return ListExpression(
            tuple(
                oldleaf if newleaf is None else newleaf
                for newleaf, oldleaf in zip(new_leaves, self._leaves)
            )
        )

    @property
    def leaves(self):
        return self._leaves

    @leaves.setter
    def leaves(self, value):
        raise ValueError("Expression.leaves is write protected.")
