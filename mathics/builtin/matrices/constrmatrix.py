# -*- coding: utf-8 -*-

from mathics.builtin.base import Builtin
from mathics.core.expression import Expression
from mathics.core.atoms import Integer0


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

    #> DiagonalMatrix[a + b]
     = DiagonalMatrix[a + b]
    """

    summary_text = "gives a diagonal matrix with the elements of a given list"

    def apply(self, list, evaluation):
        "DiagonalMatrix[list_List]"

        result = []
        n = len(list.leaves)
        for index, item in enumerate(list.leaves):
            row = [Integer0] * n
            row[index] = item
            result.append(Expression("List", *row))
        return Expression("List", *result)


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

    summary_text = "gives the identity matrix with a given dimension"
