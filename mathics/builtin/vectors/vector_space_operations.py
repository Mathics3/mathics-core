# -*- coding: utf-8 -*-

"""
Vector Space Operations
"""

from mathics.builtin.base import Builtin
from mathics.core.atoms import Complex, Integer, Integer0, Integer1, Real
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolDot, SymbolConjugate


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


class Projection(Builtin):
    """
    <dl>
      <dt>'Projection[$u$, $v$]'
      <dd>gives the projection of the vector $u$ onto $v$
    </dl>

    For vectors $u$ and $v$, the projection is taken to be ( $v$ . $u$ / $v$ . $v$ ) $v$

    For complex vectors $u$ and $v$, the projection is taken to be ( $v$* . $u$ / $v$* . $v$ ) $v$ where $v$* is 'Conjugate[v]'.

    Projection of two three-dimensional Integer vectors:
    >> Projection[{5, 6, 7}, {1, 0, 0}]
     = {5, 0, 0}

    Projection of two two-dimensional Integer vectors:
    >> Projection[{2, 3}, {1, 2}]
     = {8 / 5, 16 / 5}

    Projection of a machine-precision vector onto another:
    >> Projection[{1.3, 2.1, 3.1}, {-0.3, 4.2, 5.3}]
     = {-0.162767, 2.27874, 2.87556}

    Projection of two complex vectors:
    >> Projection[{3 + I, 2, 2 - I}, {2, 4, 5 I}]
     = {2 / 5 - 16 I / 45, 4 / 5 - 32 I / 45, 8 / 9 + I}

    Project a symbol vector onto a numeric vector:
    >> Projection[{a, b, c}, {1, 1, 1}]
     = {(a + b + c) / 3, (a + b + c) / 3, (a + b + c) / 3}

    The projection of vector $u$ onto vector $v$ is in the direction of $v$:
    >> {u, v} = RandomReal[1, {2, 6}];
    >> Abs[VectorAngle[Projection[u, v], v]] < 0. + 10^-7
     = True
    """

    summary_text = "find the projection of one vector on another"

    def apply(self, u: ListExpression, v: ListExpression, evaluation):
        "Projection[u_, v_]"

        all_elements = u.elements + v.elements
        v_dot_u, v_dot_v = None, None

        if all(isinstance(ui, (Integer, Real)) for ui in all_elements):
            v_dot_u = Expression(SymbolDot, v, u)
            v_dot_v = Expression(SymbolDot, v, v)
        elif all(
            isinstance(ui, (Complex, Integer, Real, Symbol)) for ui in all_elements
        ):
            conjugate_v = Expression(SymbolConjugate, v)
            v_dot_u = Expression(SymbolDot, Expression(SymbolDot, conjugate_v), u)
            v_dot_v = Expression(SymbolDot, Expression(SymbolDot, conjugate_v), v)

        if v_dot_u:
            return (v_dot_u / v_dot_v) * v


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


# TODO: Orthogonalize, KroneckerProduct
