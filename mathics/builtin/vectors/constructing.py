# -*- coding: utf-8 -*-

"""
Constructing Vectors

Functions for constructing lists of various sizes and structure.

See also Constructing Lists.
"""

from mathics.builtin.base import Builtin


class AngleVector(Builtin):
    """
    <dl>
      <dt>'AngleVector[$phi$]'
      <dd>returns the point at angle $phi$ on the unit circle.

      <dt>'AngleVector[{$r$, $phi$}]'
      <dd>returns the point at angle $phi$ on a circle of radius $r$.

      <dt>'AngleVector[{$x$, $y$}, $phi$]'
      <dd>returns the point at angle $phi$ on a circle of radius 1 centered at {$x$, $y$}.

      <dt>'AngleVector[{$x$, $y$}, {$r$, $phi$}]'
      <dd>returns point at angle $phi$ on a circle of radius $r$ centered at {$x$, $y$}.
    </dl>

    >> AngleVector[90 Degree]
     = {0, 1}

    >> AngleVector[{1, 10}, a]
     = {1 + Cos[a], 10 + Sin[a]}
    """

    rules = {
        "AngleVector[phi_]": "{Cos[phi], Sin[phi]}",
        "AngleVector[{r_, phi_}]": "{r * Cos[phi], r * Sin[phi]}",
        "AngleVector[{x_, y_}, phi_]": "{x + Cos[phi], y + Sin[phi]}",
        "AngleVector[{x_, y_}, {r_, phi_}]": "{x + r * Cos[phi], y + r * Sin[phi]}",
    }

    summary_text = "create a vector at a specified angle"


# TODO: FromPolarCoordinates, CirclePoints
