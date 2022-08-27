# -*- coding: utf-8 -*-
"""
Constructing Matrices

Methods for constructing Matrices.
"""


from mathics.builtin.base import Builtin
from mathics.core.atoms import Integer0
from mathics.core.expression import Expression
from mathics.core.list import ListExpression


class DiagonalMatrix(Builtin):
    """
    <dl>
      <dt>'DiagonalMatrix[$list$]'
      <dd>gives a matrix with the values in $list$ on its diagonal and zeroes elsewhere.
    </dl>

    >> DiagonalMatrix[{1, 2, 3}]
     = {{1, 0, 0}, {0, 2, 0}, {0, 0, 3}}
    >> MatrixForm[%]
     = 1   0   0
     .
     . 0   2   0
     .
     . 0   0   3
    """

    summary_text = "give a diagonal matrix with the elements of a given list"

    def apply(self, list, evaluation):
        "DiagonalMatrix[list_List]"

        result = []
        n = len(list.elements)
        for index, item in enumerate(list.elements):
            row = [Integer0] * n
            row[index] = item
            result.append(ListExpression(*row))
        return ListExpression(*result)


class IdentityMatrix(Builtin):
    """
    <dl>
      <dt>'IdentityMatrix[$n$]'
      <dd>gives the identity matrix with $n$ rows and columns.
    </dl>

    >> IdentityMatrix[3]
     = {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}}
    """

    rules = {
        "IdentityMatrix[n_Integer]": "DiagonalMatrix[Table[1, {n}]]",
    }

    summary_text = "give the identity matrix with a given dimension"
