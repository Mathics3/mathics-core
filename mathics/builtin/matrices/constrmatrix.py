# -*- coding: utf-8 -*-
"""
Constructing Matrices

Methods for constructing Matrices.
"""
import math

from mathics.builtin.base import Builtin
from mathics.core.atoms import Integer0, Integer1
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression


def _matrix(rows):
    return ListExpression(*[ListExpression(*r) for r in rows])


class BoxMatrix(Builtin):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/BoxMatrix.html</url>

    <dl>
      <dt>'BoxMatrix[$s]'
      <dd>Gives a box shaped kernel of size 2 $s$ + 1.
    </dl>

    >> BoxMatrix[3]
     = {{1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}}
    """

    summary_text = "create a matrix with all its entries set to 1"

    def eval(self, r, evaluation: Evaluation):
        "BoxMatrix[r_?RealNumberQ]"
        py_r = abs(r.round_to_float())
        s = int(math.floor(1 + 2 * py_r))
        return _matrix([[Integer1] * s] * s)


class DiagonalMatrix(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/DiagonalMatrix.html</url>

    <dl>
      <dt>'DiagonalMatrix[$list$]'
      <dd>gives a matrix with the values in $list$ on its diagonal and \
      zeroes elsewhere.
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

    def eval(self, list, evaluation):
        "DiagonalMatrix[list_List]"

        result = []
        n = len(list.elements)
        for index, item in enumerate(list.elements):
            row = [Integer0] * n
            row[index] = item
            result.append(ListExpression(*row))
        return ListExpression(*result)


class DiamondMatrix(Builtin):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/DiamondMatrix.html</url>

    <dl>
      <dt>'DiamondMatrix[$s]'
      <dd>Gives a diamond shaped kernel of size 2 $s$ + 1.
    </dl>

    >> DiamondMatrix[3]
     = {{0, 0, 0, 1, 0, 0, 0}, {0, 0, 1, 1, 1, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {1, 1, 1, 1, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 1, 1, 1, 0, 0}, {0, 0, 0, 1, 0, 0, 0}}
    """

    summary_text = "create a matrix with 1 in a diamond-shaped region, and 0 outside"

    def eval(self, r, evaluation: Evaluation):
        "DiamondMatrix[r_?RealNumberQ]"
        py_r = abs(r.round_to_float())
        t = int(math.floor(0.5 + py_r))

        zero = Integer0
        one = Integer1

        def rows():
            for d in range(0, t):
                p = [zero] * (t - d)
                yield p + ([one] * (1 + d * 2)) + p

            yield [one] * (2 * t + 1)

            for d in reversed(range(0, t)):
                p = [zero] * (t - d)
                yield p + ([one] * (1 + d * 2)) + p

        return _matrix(rows())


class DiskMatrix(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/DiskMatrix.html</url>

    <dl>
      <dt>'DiskMatrix[$s]'
      <dd>Gives a disk shaped kernel of size 2 $s$ + 1.
    </dl>

    >> DiskMatrix[3]
     = {{0, 0, 1, 1, 1, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 1, 1, 1, 0, 0}}
    """

    summary_text = "create a matrix with 1 in a disk-shaped region, and 0 outside"

    def eval(self, r, evaluation: Evaluation):
        "DiskMatrix[r_?RealNumberQ]"
        py_r = abs(r.round_to_float())
        s = int(math.floor(0.5 + py_r))

        m = (Integer0, Integer1)
        r_sqr = (py_r + 0.5) * (py_r + 0.5)

        def rows():
            for y in range(-s, s + 1):
                yield [m[int((x) * (x) + (y) * (y) <= r_sqr)] for x in range(-s, s + 1)]

        return _matrix(rows())


class IdentityMatrix(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/IdentityMatrix.html</url>

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
