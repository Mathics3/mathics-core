# -*- coding: utf-8 -*-
"""
Splines

A Spline is a mathematical function used for interpolation or smoothing. Splines are used both in graphics and computations
"""

# This tells documentation how to sort this module
# Here we are also hiding "drawing" since this can erroneously appear at the top level.
sort_order = "mathics.builtin.splines"

from mathics.builtin.base import Builtin
from mathics.core.attributes import A_LISTABLE, A_NUMERIC_FUNCTION, A_PROTECTED


# For a more generic implementation in Python using scipy,
# sympy and numpy, see:
#  https://github.com/Tarheel-Formal-Methods/kaa
class BernsteinBasis(Builtin):
    """

    <url>:Bernstein polynomial basis: https://en.wikipedia.org/wiki/Bernstein_polynomial</url> (<url>:SciPy: https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.BPoly.html</url> :WMA:

    A Bernstein is a polynomial that is a linear combination of Bernstein basis polynomials.
    With the advent of computer graphics, Bernstein polynomials, restricted to the interval [0, 1], became important in the form of Bézier curves.
    'BernsteinBasis[d,n,x]' equals 'Binomial[d, n] x^n (1-x)^(d-n)' in the interval [0, 1] and zero elsewhere.

    <dl>
      <dt>'BernsteinBasis[$d$,$n$,$x$]'
      <dd>returns the $n$th Bernstein basis of degree $d$ at $x$.
    </dl>

    >> BernsteinBasis[4, 3, 0.5]
     = 0.25
    """

    attributes = A_LISTABLE | A_NUMERIC_FUNCTION | A_PROTECTED
    rules = {
        "BernsteinBasis[d_, n_, x_]": "Piecewise[{{Binomial[d, n] * x ^ n * (1 - x) ^ (d - n), 0 < x < 1}}, 0]"
    }

    summary_text = "The basis of a Bernstein polynomial used in Bézier curves."


class BezierFunction(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/BezierFunction.html</url>
    <dl>
      <dt>'BezierFunction[{$pt_1$, $pt_2$, ...}]'
      <dd>returns a Bézier function for the curve defined by points $pt_i$.
      The embedding dimension for the curve represented by 'BezierFunction[{$pt_1$,$pt_2$,...}]' is given by the length of the lists $pt_i$.
    </dl>

    >> f = BezierFunction[{{0, 0}, {1, 1}, {2, 0}, {3, 2}}];
     =

    >> f[.5]
     = {1.5, 0.625}
    #> Clear[f];
     =

    ## Graphics[{Red, Point[pts], Green, Line[pts]}, Axes -> True]

    Plotting the Bézier Function accoss a Bézier curve:
    >> Module[{p={{0, 0},{1, 1},{2, -1},{4, 0}}}, Graphics[{BezierCurve[p], Red, Point[Table[BezierFunction[p][x], {x, 0, 1, 0.1}]]}]]
     = -Graphics-
    """

    rules = {
        "BezierFunction[p_]": "Function[x, Total[p * BernsteinBasis[Length[p] - 1, Range[0, Length[p] - 1], x]]]"
    }

    summary_text = "underlying function used in a Bézier curve"


class BezierCurve(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/BezierCurve.html</url>

     <dl>
       <dt>'BezierCurve[{$pt_1$, $pt_2$ ...}]'
       <dd>represents a Bézier curve with control points $p_i$.
       <dd>The result is a curve by combining the Bézier curves when points are taken triples at a time.
     </dl>

     Option:
     <ul>
       <li>'SplineDegree->$d$' specifies that the underlying polynomial basis should have maximal degree d.
     </ul>


     Set up some points to form a simple zig-zag...
     >> pts = {{0, 0}, {1, 1}, {2, -1}, {3, 0}};
      =

     >> Graphics[{Line[pts], Red, Point[pts]}]
      = -Graphics-

    A composite Bézier curve, shown in blue, smooths the zig zag. Control points are shown in red:
     >> Graphics[{BezierCurve[pts], Blue, Line[pts], Red, Point[pts]}]
      = -Graphics-

     Extend points...
     >> pts = {{0, 0}, {1, 1}, {2, -1}, {3, 0}, {5, 2}, {6, -1}, {7, 3}};
      =

     A longer composite Bézier curve and its control points:
     >> Graphics[{BezierCurve[pts], Blue, Line[pts], Red, Point[pts]}]
      = -Graphics-

     Notice how the curve from the first to third point is not changed by any points outside the interval. The same is true for points three to five, and so on.

     #> Clear[pts];
    """

    options = {"SplineDegree": "3"}

    summary_text = "composite Bézier curve"
