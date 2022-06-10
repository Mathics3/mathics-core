# -*- coding: utf-8 -*-

"""
Parts of Matrices

Methods for manipulating Matrices.
"""


from mathics.builtin.base import Builtin
from mathics.core.list import ListExpression


class Diagonal(Builtin):
    """
    <dl>
        <dt>'Diagonal[$m$]'
        <dd>gives a list with the values in the diagonal of the matrix $m$.
        <dt>'Diagonal[$m$, $k$]'
        <dd>gives a list with the values in the $k$ diagonal of the matrix $m$.
    </dl>

    >> Diagonal[{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}]
     = {1, 5, 9}

    Get the superdiagonal:
    >> Diagonal[{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}, 1]
     = {2, 6}

    Get the subdiagonal:
    >> Diagonal[{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}, -1]
     = {4, 8}

    Get the diagonal of a nonsquare matrix:
    >> Diagonal[{{1, 2, 3}, {4, 5, 6}}]
     = {1, 5}
    """

    rules = {
        "Diagonal[expr_]": "Diagonal[expr, 0]",
    }

    summary_text = "gives a list with the diagonal elements of a given matrix"

    def apply(self, expr, diag, evaluation):
        "Diagonal[expr_List, diag_Integer]"

        result = []

        for count, value in enumerate(expr.elements, start=diag.value):
            if not hasattr(value, "elements") or len(value.elements) <= count:
                break
            if count < 0:
                continue
            result.append(value.elements[count])
        return ListExpression(*result)


class MatrixQ(Builtin):
    """
    <dl>
      <dt>'MatrixQ[$m$]'
      <dd>gives 'True' if $m$ is a list of equal-length lists.

      <dt>'MatrixQ[$m$, $f$]'
      <dd>gives 'True' only if '$f$[$x$]' returns 'True' for when applied to element $x$ of the matrix $m$.
    </dl>

    >> MatrixQ[{{1, 3}, {4.0, 3/2}}, NumberQ]
     = True

    These are not matrices:
    >> MatrixQ[{{1}, {1, 2}}] (* first row should have length two *)
     = False

    >> MatrixQ[Array[a, {1, 1, 2}]]
     = False

    Supply a test function parameter to generalize and specialize:
    >> MatrixQ[{{1, 2}, {3, 4 + 5}}, Positive]
     = True

    >> MatrixQ[{{1, 2 I}, {3, 4 + 5}}, Positive]
     = False
    """

    rules = {
        "MatrixQ[expr_]": "ArrayQ[expr, 2]",
        "MatrixQ[expr_, test_]": "ArrayQ[expr, 2, test]",
    }

    summary_text = "gives 'True' if the given argument is a list of equal-length lists"
