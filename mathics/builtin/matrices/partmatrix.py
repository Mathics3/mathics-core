# -*- coding: utf-8 -*-

"""
Parts of Matrices

Methods for manipulating Matrices.
"""


from mathics.builtin.base import Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression


class Diagonal(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Diagonal.html</url>

    <dl>
        <dt>'Diagonal[$m$]'
        <dd>gives a list with the values in the diagonal of the matrix $m$.

        <dt>'Diagonal[$m$, $k$]'
        <dd>gives a list with the values in the $k$ diagonal of the \
            matrix $m$.
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

    def eval(self, expr, diag, evaluation: Evaluation):
        "Diagonal[expr_List, diag_Integer]"

        result = []

        for count, value in enumerate(expr.elements, start=diag.value):
            if not hasattr(value, "elements") or len(value.elements) <= count:
                break
            if count < 0:
                continue
            result.append(value.elements[count])
        return ListExpression(*result)


# TODO: add ArrayRules, Indexed, LowerTriangularize, UpperTriangularize
