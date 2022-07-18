# -*- coding: utf-8 -*-

"""
Mathematical Operations
"""

import sympy

from mathics.builtin.base import Builtin
from mathics.core.atoms import Integer, Integer2, Real
from mathics.core.convert.sympy import from_sympy, to_sympy_matrix
from mathics.core.symbols import Symbol


class Cross(Builtin):
    """
    <dl>
      <dt>'Cross[$a$, $b$]'
      <dd>computes the vector cross product of $a$ and $b$.
    </dl>

    >> Cross[{x1, y1, z1}, {x2, y2, z2}]
     = {y1 z2 - y2 z1, -x1 z2 + x2 z1, x1 y2 - x2 y1}

    >> Cross[{x, y}]
     = {-y, x}

    >> Cross[{1, 2}, {3, 4, 5}]
     : The arguments are expected to be vectors of equal length, and the number of arguments is expected to be 1 less than their length.
     = Cross[{1, 2}, {3, 4, 5}]
    """

    messages = {
        "nonn1": (
            "The arguments are expected to be vectors of equal length, "
            "and the number of arguments is expected to be 1 less than "
            "their length."
        )
    }
    rules = {"Cross[{x_, y_}]": "{-y, x}"}
    summary_text = "vector cross product"

    def apply(self, a, b, evaluation):
        "Cross[a_, b_]"
        a = to_sympy_matrix(a)
        b = to_sympy_matrix(b)

        if a is None or b is None:
            return evaluation.message("Cross", "nonn1")

        try:
            res = a.cross(b)
        except sympy.ShapeError:
            return evaluation.message("Cross", "nonn1")
        return from_sympy(res)


class Norm(Builtin):
    """
    <dl>
      <dt>'Norm[$m$, $l$]'
      <dd>computes the l-norm of matrix m (currently only works for vectors!).

      <dt>'Norm[$m$]'
      <dd>computes the 2-norm of matrix m (currently only works for vectors!).
    </dl>

    >> Norm[{1, 2, 3, 4}, 2]
     = Sqrt[30]

    >> Norm[{10, 100, 200}, 1]
     = 310

    >> Norm[{a, b, c}]
     = Sqrt[Abs[a] ^ 2 + Abs[b] ^ 2 + Abs[c] ^ 2]

    >> Norm[{-100, 2, 3, 4}, Infinity]
     = 100

    >> Norm[1 + I]
     = Sqrt[2]

    #> Norm[{1, {2, 3}}]
     : The first Norm argument should be a number, vector, or matrix.
     = Norm[{1, {2, 3}}]

    #> Norm[{x, y}]
     = Sqrt[Abs[x] ^ 2 + Abs[y] ^ 2]

    #> Norm[{x, y}, p]
     = (Abs[x] ^ p + Abs[y] ^ p) ^ (1 / p)

    #> Norm[{x, y}, 0]
     : The second argument of Norm, 0, should be a symbol, Infinity, or an integer or real number not less than 1 for vector p-norms; or 1, 2, Infinity, or "Frobenius" for matrix norms.
     = Norm[{x, y}, 0]

    #> Norm[{x, y}, 0.5]
     : The second argument of Norm, 0.5, should be a symbol, Infinity, or an integer or real number not less than 1 for vector p-norms; or 1, 2, Infinity, or "Frobenius" for matrix norms.
     = Norm[{x, y}, 0.5]

    #> Norm[{}]
     = Norm[{}]

    #> Norm[0]
     = 0
    """

    messages = {
        "nvm": "The first Norm argument should be a number, vector, or matrix.",
        "ptype": (
            "The second argument of Norm, `1`, should be a symbol, Infinity, "
            "or an integer or real number not less than 1 for vector p-norms; "
            'or 1, 2, Infinity, or "Frobenius" for matrix norms.'
        ),
        "normnotimplemented": "Norm is not yet implemented for matrices.",
    }

    rules = {
        "Norm[m_?NumberQ]": "Abs[m]",
        "Norm[m_?VectorQ, DirectedInfinity[1]]": "Max[Abs[m]]",
    }
    summary_text = "norm of a vector or matrix"

    def apply_single(self, m, evaluation):
        "Norm[m_]"
        return self.apply(m, Integer2, evaluation)

    def apply(self, m, l, evaluation):
        "Norm[m_, l_]"

        if isinstance(l, Symbol):
            pass
        elif isinstance(l, (Real, Integer)) and l.to_python() >= 1:
            pass
        else:
            return evaluation.message("Norm", "ptype", l)

        l = l.to_sympy()
        if l is None:
            return
        matrix = to_sympy_matrix(m)

        if matrix is None:
            return evaluation.message("Norm", "nvm")
        if len(matrix) == 0:
            return

        try:
            res = matrix.norm(l)
        except NotImplementedError:
            return evaluation.message("Norm", "normnotimplemented")

        return from_sympy(res)


# TODO: Curl, Div
