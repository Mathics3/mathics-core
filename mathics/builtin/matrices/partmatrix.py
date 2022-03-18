# -*- coding: utf-8 -*-

"""
Parts of Matrices

Set of methods for manipulating Matrices.
"""


from mathics.builtin.base import Builtin
from mathics.core.expression import Expression
from mathics.core.symbols import SymbolList


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
    >> Diagonal[{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}, 1]
     = {2, 6}
    """

    rules = {
        "Diagonal[expr_]": "Diagonal[expr, 0]",
    }

    summary_text = "Return a list with the diagonal elements of a given matrix"

    def apply(self, expr, diag, evaluation):
        "Diagonal[expr_List, diag_Integer]"

        result = []

        for count, value in enumerate(expr.elements, start=diag.value):
            if not hasattr(value, "elements") or len(value.elements) <= count:
                break
            if count < 0:
                continue
            result.append(value.elements[count])
        return Expression(SymbolList, *result)


class MatrixQ(Builtin):
    """
    <dl>
    <dt>'MatrixQ[$m$]'
        <dd>returns 'True' if $m$ is a list of equal-length lists.
    <dt>'MatrixQ[$m$, $f$]'
        <dd>only returns 'True' if '$f$[$x$]' returns 'True' for each
        element $x$ of the matrix $m$.
    </dl>

    >> MatrixQ[{{1, 3}, {4.0, 3/2}}, NumberQ]
     = True
    """

    rules = {
        "MatrixQ[expr_]": "ArrayQ[expr, 2]",
        "MatrixQ[expr_, test_]": "ArrayQ[expr, 2, test]",
    }

    summary_text = (
        "Return 'True' if the given argument is a list of equal-length lists."
    )
