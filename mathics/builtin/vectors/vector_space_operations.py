# -*- coding: utf-8 -*-

"""
Vector Space Operations
"""

from mathics.builtin.base import Builtin
from mathics.core.atoms import Integer, Integer0, Integer1
from mathics.core.list import ListExpression


class Normalize(Builtin):
    """
    <dl>
      <dt>'Normalize[$v$]'
      <dd>calculates the normalized vector $v$.

      <dt>'Normalize[$z$]'
      <dd>calculates the normalized complex number $z$.
    </dl>

    >> Normalize[{1, 1, 1, 1}]
     = {1 / 2, 1 / 2, 1 / 2, 1 / 2}

    >> Normalize[1 + I]
     = (1 / 2 + I / 2) Sqrt[2]

    #> Normalize[0]
     = 0

    #> Normalize[{0}]
     = {0}

    #> Normalize[{}]
     = {}
    """

    rules = {"Normalize[v_]": "Module[{norm = Norm[v]}, If[norm == 0, v, v / norm, v]]"}
    summary_text = "normalizes a vector"


class UnitVector(Builtin):
    """
    <dl>
      <dt>'UnitVector[$n$, $k$]'
      <dd>returns the $n$-dimensional unit vector with a 1 in position $k$.

      <dt>'UnitVector[$k$]'
      <dd>is equivalent to 'UnitVector[2, $k$]'.
    </dl>

    >> UnitVector[2]
     = {0, 1}
    >> UnitVector[4, 3]
     = {0, 0, 1, 0}
    """

    messages = {
        "nokun": "There is no unit vector in direction `1` in `2` dimensions.",
    }

    rules = {
        "UnitVector[k_Integer]": "UnitVector[2, k]",
    }
    summary_text = "unit vector along a coordinate direction"

    def apply(self, n: Integer, k: Integer, evaluation):
        "UnitVector[n_Integer, k_Integer]"

        py_n = n.value
        py_k = k.value
        if py_n is None or py_k is None:
            return
        if not 1 <= py_k <= py_n:
            evaluation.message("UnitVector", "nokun", k, n)
            return

        def item(i):
            if i == py_k:
                return Integer1
            else:
                return Integer0

        return ListExpression(*(item(i) for i in range(1, py_n + 1)))


class VectorAngle(Builtin):
    """
    <dl>
      <dt>'VectorAngle[$u$, $v$]'
      <dd>gives the angles between vectors $u$ and $v$
    </dl>

    >> VectorAngle[{1, 0}, {0, 1}]
     = Pi / 2

    >> VectorAngle[{1, 2}, {3, 1}]
     = Pi / 4

    >> VectorAngle[{1, 1, 0}, {1, 0, 1}]
     = Pi / 3

    #> VectorAngle[{0, 1}, {0, 1}]
     = 0
    """

    rules = {"VectorAngle[u_, v_]": "ArcCos[u.v / (Norm[u] Norm[v])]"}
    summary_text = "angle between vectors"


# TODO: Projection, Orthogonalize, KroneckerProduct
