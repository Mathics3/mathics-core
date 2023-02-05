# -*- coding: utf-8 -*-

"""
Mathematical Operations
"""

import sympy

from mathics.builtin.base import Builtin, SympyFunction
from mathics.core.attributes import A_PROTECTED
from mathics.core.convert.sympy import from_sympy, to_sympy_matrix
from mathics.eval.math_ops import eval_Norm, eval_Norm_p


class Cross(Builtin):
    """
    <url>
    :Cross product:
    https://en.wikipedia.org/wiki/Cross_product</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/physics/vector/api/functions.html#sympy.physics.vector.functions.cross</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Cross.html</url>)

    <dl>
      <dt>'Cross[$a$, $b$]'
      <dd>computes the vector cross product of $a$ and $b$.
    </dl>

    Three-dimensional cross product:

    >> Cross[{x1, y1, z1}, {x2, y2, z2}]
     = {y1 z2 - y2 z1, -x1 z2 + x2 z1, x1 y2 - x2 y1}

    'Cross' is antisymmetric, so:

    >> Cross[{x, y}]
     = {-y, x}

    Graph two-Dimensional cross product:

    >> v1 = {1, Sqrt[3]}; v2 = Cross[v1]
     = {-Sqrt[3], 1}

    Visualize this:

    >> Graphics[{Arrow[{{0, 0}, v1}], Red, Arrow[{{0, 0}, v2}]}, Axes -> True]
     = -Graphics-

    #> Clear[v1, v2];

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
    summary_text = "get vector cross product"

    def eval(self, a, b, evaluation):
        "Cross[a_, b_]"
        a = to_sympy_matrix(a)
        b = to_sympy_matrix(b)

        if a is None or b is None:
            evaluation.message("Cross", "nonn1")
            return

        try:
            res = a.cross(b)
        except sympy.ShapeError:
            evaluation.message("Cross", "nonn1")
            return
        return from_sympy(res)


class Curl(SympyFunction):
    """
    <url>
    :Curl:
    https://en.wikipedia.org/wiki/Curl_(mathematics)</url> (<url>
    :SymPy: https://docs.sympy.org/latest/modules/vector/api/vectorfunctions.html#sympy.vector.curl</url>, <url>
    :WMA: https://reference.wolfram.com/language/ref/Curl.html</url>)

    <dl>
      <dt>'Curl[{$f1$, $f2$}, {$x1$, $x2$}]'
      <dd>returns the curl $df2$/$dx1$ - $df1$/$dx2$

      <dt>'Curl[{$f1$, $f2$, $f3} {$x1$, $x2$, $x3}]'
      <dd>returns the curl ($df3$/$dx2$ - $df2$/$dx3$, $dx3$/$df$3 - $df3$/$dx1$, $df2$/$df1$ - $df1$/$dx2$)
    </dl>

    Two-dimensional 'Curl':

    >> Curl[{y, -x}, {x, y}]
     = -2

    >> v[x_, y_] := {Cos[x] Sin[y], Cos[y] Sin[x]}
    >> Curl[v[x, y], {x, y}]
     = 0

    Three-dimensional 'Curl':
    >> Curl[{y, -x, 2 z}, {x, y, z}]
     = {0, 0, -2}

    #> Clear[v];
    """

    attributes = A_PROTECTED
    rules = {
        "Curl[{f1_, f2_}, {x1_, x2_}]": " D[f2, x1] - D[f1, x2]",
        "Curl[{f1_, f2_, f3_}, {x1_, x2_, x3_}]": """{
           D[f3, x2] - D[f2, x3],
           D[f1, x3] - D[f3, x1],
           D[f2, x1] - D[f1, x2]
         }""",
    }
    summary_text = "get vector curl"
    sympy_name = "curl"


class Norm(Builtin):
    """
    <url>
    :Matrix norms induced by vector p-norms:
    https://en.wikipedia.org/wiki/Matrix_norm#Matrix_norms_induced_by_vector_p-norms</url> (<url>
    :SymPy:
    https://docs.sympy.org/latest/modules/matrices/matrices.html#sympy.matrices.matrices.MatrixBase.norm</url>, <url>
    :WMA:
    https://reference.wolfram.com/language/ref/Norm.html</url>)

    <dl>
      <dt>'Norm[$m$, $p$]'
      <dd>computes the p-norm of matrix m.

      <dt>'Norm[$m$]'
     <dd>computes the 2-norm of matrix m.
    </dl>

    The 'Norm' of of a vector is its Euclidean distance:
    >> Norm[{x, y, z}]
     = Sqrt[Abs[x] ^ 2 + Abs[y] ^ 2 + Abs[z] ^ 2]

    By default, 2-norm is used for vectors, but you can be explicit:
    >> Norm[{3, 4}, 2]
     = 5

    The 1-norm is the sum of the values:
    >> Norm[{10, 100, 200}, 1]
     = 310

    >> Norm[{x, y, z}, Infinity]
     = Max[{Abs[x], Abs[y], Abs[z]}]

    >> Norm[{-100, 2, 3, 4}, Infinity]
     = 100

    For complex numbers, 'Norm[$z$]' is 'Abs[$z$]':
    >> Norm[1 + I]
     = Sqrt[2]
    So the norm is always real, even when the input is complex.


    'Norm'[$m$,"Frobenius"] gives the Frobenius norm of $m$:
    >> Norm[Array[Subscript[a, ##] &, {2, 2}], "Frobenius"]
     = Sqrt[Abs[Subscript[a, 1, 1]] ^ 2 + Abs[Subscript[a, 1, 2]] ^ 2 + Abs[Subscript[a, 2, 1]] ^ 2 + Abs[Subscript[a, 2, 2]] ^ 2]

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
    summary_text = "get norm of a vector or matrix"

    def eval(self, m, evaluation):
        "Norm[m_]"
        return eval_Norm(m, evaluation)

    def eval_with_p(self, m, p, evaluation):
        "Norm[m_, p_]"
        return eval_Norm_p(m, p, evaluation)


# TODO: Div
