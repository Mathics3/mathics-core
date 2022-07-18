# -*- coding: utf-8 -*-

"""
Mathematical Operations
"""

import sympy

from mathics.builtin.base import Builtin
from mathics.core.convert.sympy import from_sympy, to_sympy_matrix


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
