# -*- coding: utf-8 -*-

"""Three-Dimensional Graphics

Functions for working with 3D graphics.
"""

from mathics.builtin.colors.color_directives import RGBColor
from mathics.builtin.graphics import (
    CoordinatesError,
    Graphics,
    Style,
    _GraphicsElements,
)
from mathics.core.atoms import Integer, Rational, Real
from mathics.core.builtin import Builtin
from mathics.core.expression import Evaluation, Expression
from mathics.core.symbols import SymbolN
from mathics.eval.nevaluator import eval_N

# This tells documentation how to sort this module
# Here we are also hiding "drawing" since this erroneously appears at the top level.
sort_order = "mathics.builtin.three-dimensional-graphics"


def coords3D(value):
    if value.has_form("List", 3):
        result = (
            value.elements[0].round_to_float(),
            value.elements[1].round_to_float(),
            value.elements[2].round_to_float(),
        )
        if None not in result:
            return result
    raise CoordinatesError


class Coords3D:
    def __init__(self, graphics=None, expr=None, pos=None):
        self.p = pos
        if expr is not None:
            if expr.has_form("Offset", 1, 2):
                if len(expr.elements) > 1:
                    self.p = coords3D(expr.elements[1])
            else:
                self.p = coords3D(expr)

    def pos(self):
        return self.p, None

    def add(self, x, y, z):
        p = (self.p[0] + x, self.p[1] + y, self.p[2] + z)
        return Coords3D(pos=p)

    def scale(self, a):
        self.p = (self.p[0] * a[0], self.p[1] * a[1], self.p[2] * a[2])


class Style3D(Style):
    def get_default_face_color(self):
        return RGBColor(components=(1, 1, 1, 1))


class Graphics3D(Graphics):
    r"""
        <url>:WMA link:https://reference.wolfram.com/language/ref/Graphics3D.html</url>

        <dl>
          <dt>'Graphics3D'[$primitives$, $options$]
          <dd>represents a three-dimensional graphic.

          See <url>:Drawing Option and Option Values:
    /doc/reference-of-built-in-symbols/graphics-and-drawing/drawing-options-and-option-values
    </url> for a list of Plot options.
        </dl>

        >> Graphics3D[Polygon[{{0,0,0}, {0,1,1}, {1,0,0}}]]
         = -Graphics3D-

        The 'Background' option allows to set the color of the background:
        >> Graphics3D[Sphere[], Background->RGBColor[.6, .7, 1.]]
         = -Graphics3D-

        In 'TeXForm', 'Graphics3D' creates Asymptote figures:
        >> Graphics3D[Sphere[]] // TeXForm
         = #<--#
         . \begin{asy}
         . import three;
         . import solids;
         . import tube;
         . size(6.6667cm, 6.6667cm);
         . currentprojection=perspective(2.6,-4.8,4.0);
         . currentlight=light(rgb(0.5,0.5,0.5), specular=red, (2,0,2), (2,2,2), (0,2,2));
         . // Sphere3DBox
         . draw(surface(sphere((0, 0, 0), 1)), rgb(1,1,1)+opacity(1));
         . draw(((-1,-1,-1)--(1,-1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . draw(((-1,1,-1)--(1,1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . draw(((-1,-1,1)--(1,-1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . draw(((-1,1,1)--(1,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . draw(((-1,-1,-1)--(-1,1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . draw(((1,-1,-1)--(1,1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . draw(((-1,-1,1)--(-1,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . draw(((1,-1,1)--(1,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . draw(((-1,-1,-1)--(-1,-1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . draw(((1,-1,-1)--(1,-1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . draw(((-1,1,-1)--(-1,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . draw(((1,1,-1)--(1,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));
         . \end{asy}
    """
    summary_text = "a three-dimensional graphics image wrapper"
    options = Graphics.options.copy()
    options.update(
        {"BoxRatios": "Automatic", "Lighting": "Automatic", "ViewPoint": "{1.3,-2.4,2}"}
    )

    box_suffix = "3DBox"

    messages = {"invlight": "`1` is not a valid list of light sources."}

    rules = {
        "MakeBoxes[Graphics3D[content_, OptionsPattern[Graphics3D]], "
        "        OutputForm]": '"-Graphics3D-"'
    }


def total_extent_3d(extents):
    xmin = xmax = ymin = ymax = zmin = zmax = None
    for extent in extents:
        for x, y, z in extent:
            if xmin is None or x < xmin:
                xmin = x
            if xmax is None or x > xmax:
                xmax = x
            if ymin is None or y < ymin:
                ymin = y
            if ymax is None or y > ymax:
                ymax = y
            if zmin is None or z < zmin:
                zmin = z
            if zmax is None or z > zmax:
                zmax = z
    return xmin, xmax, ymin, ymax, zmin, zmax


class Graphics3DElements(_GraphicsElements):
    coords = Coords3D
    style_class = Style3D

    def __init__(self, content, evaluation, neg_y=False):
        super(Graphics3DElements, self).__init__(content, evaluation)
        self.neg_y = neg_y
        self.xmin = (
            self.ymin
        ) = (
            self.pixel_width
        ) = self.pixel_height = self.extent_width = self.extent_height = None
        self.view_width = None
        self.content = content

    def extent(self, completely_visible_only=False):
        return total_extent_3d([element.extent() for element in self.elements])

    def _apply_boxscaling(self, boxscale):
        for element in self.elements:
            element._apply_boxscaling(boxscale)


class Cone(Builtin):
    """
    <url>:Cone:https://en.wikipedia.org/wiki/Cone</url> (<url>
    :WMA:https://reference.wolfram.com/language/ref/Cone.html</url>)

    <dl>
      <dt>'Cone'[]
      <dd>is a cone of radius 1 and height 2 oriented in the upward $z$ direction.

      <dt>'Cone'[{{$x_1$, $y_1$, $z_1$}, {$x_2$, $y_2$, $z_2$}}, $r$]
      <dd>is a cone of radius $r$ starting at ($x_1$, $y_1$, $z_1$) and ending at \
          ($x_2$, $y_2$, $z_2$).

      <dt>'Cone'[{{$x_1$, $y_1$, $z_1$}, {$x_2$, $y_2$, $z_2$}, ... }, $r$]
      <dd>is a collection cones of radius $r$.
    </dl>

    >> Graphics3D[Cone[]]
     = -Graphics3D-

    >> Graphics3D[Cone[{{0, 0, 0}, {1, 1, 1}}, 1]]
     = -Graphics3D-

    >> Graphics3D[{Yellow, Cone[{{-1, 0, 0}, {1, 0, 0}, {0, 0, Sqrt[3]}, {1, 1, Sqrt[3]}}, 1]}]
     = -Graphics3D-
    """

    summary_text = "represent a cone"
    messages = {
        "oddn": "The number of points must be even.",
        "nrr": "The radius must be a real number",
    }

    rules = {
        "Cone[]": "Cone[{{0, 0, 0}, {0, 0, 2}}, 1]",
        "Cone[positions_List]": "Cone[positions, 1]",
    }

    def eval_check(self, positions, radius, evaluation: Evaluation):
        "Cone[positions_List, radius_]"

        if len(positions.elements) % 2 == 1:
            # The number of points is odd, so abort.
            evaluation.error("Cone", "oddn", positions)
        if not isinstance(radius, (Integer, Rational, Real)):
            nradius = Expression(SymbolN, radius).evaluate(evaluation)
            if not isinstance(nradius, (Integer, Rational, Real)):
                evaluation.error("Cone", "nrr", radius)

        return


class Cuboid(Builtin):
    """
    <url>:Cuboid:
      https://en.wikipedia.org/wiki/Cuboid</url> (<url>
      :WMA:https://reference.wolfram.com/language/ref/Cuboid.html</url>)

    Cuboid also known as interval, rectangle, square, cube, rectangular parallelepiped, \
    tesseract, orthotope, and box.
    <dl>
      <dt>'Cuboid'[$p_{min}$]
      <dd>is a unit cube/square with its lower corner at point $p_{min}$.

      <dt>'Cuboid'[$p_{min}$, $p_{max}$]
      <dd>is a 2d square with with lower corner $p_{min}$ and upper corner $p_{max}$.

      <dt>'Cuboid'[{$p_{min}$, $p_{max}$}]
      <dd>is a cuboid with lower corner $p_{min}$ and upper corner $p_{max}$.

      <dt>'Cuboid'[{$p1_{min}$, $p1_{max}$, ...}]
      <dd>is a collection of cuboids.

      <dt>'Cuboid[]' is equivalent to 'Cuboid'[{0,0,0}].
    </dl>

    >> Graphics3D[Cuboid[{0, 0, 1}]]
     = -Graphics3D-

    >> Graphics3D[{Red, Cuboid[{{0, 0, 0}, {1, 1, 0.5}}], Blue, Cuboid[{{0.25, 0.25, 0.5}, {0.75, 0.75, 1}}]}]
     = -Graphics3D-

    >> Graphics[Cuboid[{0, 0}]]
     = -Graphics-
    """

    messages = {"oddn": "The number of points must be even."}

    rules = {
        "Cuboid[]": "Cuboid[{{0, 0, 0}, {1, 1, 1}}]",
        "Cuboid[{xmin_?NumberQ, ymin_?NumberQ}]": "Rectangle[{xmin, ymin}, {xmin + 1, ymin + 1}]",
        "Cuboid[{xmin_, ymin_}, {xmax_, ymax_}]": "Rectangle[{xmin, ymin}, {xmax, ymax}]",
        "Cuboid[{xmin_, ymin_, zmin_}]": "Cuboid[{{xmin, ymin, zmin}, {xmin + 1, ymin + 1, zmin + 1}}]",
    }

    summary_text = "represent a unit cube"

    def eval_check(self, positions, evaluation: Evaluation):
        "Cuboid[positions_List]"

        if len(positions.elements) % 2 == 1:
            # The number of points is odd, so abort.
            evaluation.error("Cuboid", "oddn", positions)

        return


class Cylinder(Builtin):
    """
    <url>:Cylinder:
    https://en.wikipedia.org/wiki/Cylinder</url> (<url>
    :WMA:https://reference.wolfram.com/language/ref/Cylinder.html</url>)

    <dl>
      <dt>'Cylinder'[{{$x_1$, $y_1$, $z_1$}, {$x_2$, $y_2$, $z_2$}}]
      <dd>represents a cylinder of radius 1.

      <dt>'Cylinder'[{{$x_1$, $y_1$, $z_1$}, {$x_2$, $y_2$, $z_2$}}, $r$]
      <dd>represents a cylinder of radius $r$ starting at ($x_1$, $y_1$, $z_1$) and ending at \
          ($x_2$, $y_2$, $z_2$).

      <dt>'Cylinder'[{{$x_1$, $y_1$, $z_1$}, {$x_2$, $y_2$, $z_2$}, ... }, $r$]
      <dd>represents is a collection cylinders of radius $r$.
    </dl>

    >> Graphics3D[Cylinder[{{0, 0, 0}, {1, 1, 1}}, 1]]
     = -Graphics3D-

    >> Graphics3D[{Yellow, Cylinder[{{-1, 0, 0}, {1, 0, 0}, {0, 0, Sqrt[3]}, {1, 1, Sqrt[3]}}, 1]}]
     = -Graphics3D-
    """

    summary_text = "represent a cylinder"
    messages = {
        "oddn": "The number of points must be even.",
        "nrr": "The radius must be a real number",
    }

    rules = {
        "Cylinder[]": "Cylinder[{{0, 0, 0}, {1, 1, 1}}, 1]",
        "Cylinder[positions_List]": "Cylinder[positions, 1]",
    }

    def eval_check(self, positions, radius, evaluation: Evaluation):
        "Cylinder[positions_List, radius_]"

        if len(positions.elements) % 2 == 1:
            # The number of points is odd, so abort.
            evaluation.error("Cylinder", "oddn", positions)
        if not isinstance(radius, (Integer, Rational, Real)):
            nradius = eval_N(radius, evaluation)
            if not isinstance(nradius, (Integer, Rational, Real)):
                evaluation.error("Cylinder", "nrr", radius)

        return


class Sphere(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Sphere.html</url>

    <dl>
    <dt>'Sphere'[{$x$, $y$, $z$}]
        <dd>is a sphere of radius 1 centered at the point {$x$, $y$, $z$}.
    <dt>'Sphere'[{$x$, $y$, $z$}, $r$]
        <dd>is a sphere of radius $r$ centered at the point {$x$, $y$, $z$}.
    <dt>'Sphere'[{{$x_1$, $y_1$, $z_1$}, {$x_2$, $y_2$, $z_2$}, ... }, $r$]
        <dd>is a collection spheres of radius $r$ centered at the points \
            {$x_1$, $y_2$, $z_2$}, {$x_2$, $y_2$, $z_2$}, ...
    </dl>

    >> Graphics3D[Sphere[{0, 0, 0}, 1]]
     = -Graphics3D-

    >> Graphics3D[{Yellow, Sphere[{{-1, 0, 0}, {1, 0, 0}, {0, 0, Sqrt[3.]}}, 1]}]
     = -Graphics3D-
    """

    summary_text = "represent a sphere"
    rules = {
        "Sphere[]": "Sphere[{0, 0, 0}, 1]",
        "Sphere[positions_]": "Sphere[positions, 1]",
    }


class Tube(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Tube.html</url>

    <dl>
      <dt>'Tube'[{$p_1$, $p_2$, ...}]
      <dd>represents a tube passing through $p_1$, $p_2$, ... with radius 1.

      <dt>'Tube'[{$p_1$, $p_2$, ...}, $r$]
      <dd>represents a tube with radius $r$.
    </dl>

    >> Graphics3D[Tube[{{0,0,0}, {1,1,1}}]]
    = -Graphics3D-

    >> Graphics3D[Tube[{{0,0,0}, {1,1,1}, {0, 0, 1}}, 0.1]]
    = -Graphics3D-
    """

    summary_text = "represent a tube"
    rules = {
        "Tube[]": "Tube[{{0, 0, 0}, {1, 1, 1}}, 1]",
        "Tube[positions_]": "Tube[positions, 1]",
    }
