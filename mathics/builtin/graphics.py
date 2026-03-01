# -*- coding: utf-8 -*-
# cython: language_level=3

"""
Drawing Graphics
"""
from math import sqrt

from mathics.builtin.colors.color_directives import (
    CMYKColor,
    GrayLevel,
    Hue,
    LABColor,
    LCHColor,
    LUVColor,
    Opacity,
    RGBColor,
    XYZColor,
)
from mathics.builtin.drawing.graphics_internals import GLOBALS, _GraphicsDirective
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Integer, Rational, Real
from mathics.core.attributes import A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.exceptions import BoxExpressionError
from mathics.core.symbols import Symbol, SymbolList, symbol_set, system_symbols_dict
from mathics.core.systemsymbols import (
    SymbolEdgeForm,
    SymbolFaceForm,
    SymbolInset,
    SymbolLine,
    SymbolPoint,
    SymbolPolygon,
    SymbolRule,
    SymbolStyle,
    SymbolText,
)
from mathics.eval.nevaluator import eval_N

# This following line tells documentation how to sort this module
sort_order = "mathics.builtin.drawing-graphics"

GRAPHICS_SYMBOLS = {}
GRAPHICS_OPTIONS = {
    "AlignmentPoint": "Center",
    "AspectRatio": "Automatic",
    "Axes": "False",
    "AxesLabel": "None",
    "AxesOrigin": "Automatic",
    "AxesStyle": "{}",
    "Background": "Automatic",
    "BaseStyle": "{}",
    "BaselinePosition": "Automatic",
    "ContentSelectable": "Automatic",
    "CoordinatesToolOptions": "Automatic",
    "Epilog": "{}",
    "FormatType": "TraditionalForm",
    "Frame": "False",
    "FrameLabel": "None",
    "FrameStyle": "{}",
    "FrameTicks": "Automatic",
    "FrameTicksStyle": "{}",
    "GridLines": "None",
    "GridLinesStyle": "{}",
    "ImageMargins": "0.",
    "ImagePadding": "All",
    "ImageSize": "Automatic",
    "LabelStyle": "{}",
    "LogPlot": "False",  # not standard afaics
    "Method": "Automatic",
    "PlotLabel": "None",
    "PlotRange": "Automatic",
    "PlotRangeClipping": "False",
    "PlotRangePadding": "Automatic",
    "PlotRegion": "Automatic",
    "PreserveImageOptions": "Automatic",
    "Prolog": "{}",
    "RotateLabel": "True",
    "Ticks": "Automatic",
    "TicksStyle": "{}",
    "$OptionSyntax": "Ignore",
}

# fraction of point relative canvas width
DEFAULT_POINT_FACTOR = 0.007


def _to_float(x):
    x = x.round_to_float()
    if x is None:
        raise BoxExpressionError
    return x


class Show(Builtin):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/Show.html</url>

    <dl>
      <dt>'Show'[$graphics$, $options$]
      <dd>shows a list of graphics with the specified options added.
    </dl>

    >> Show[{Plot[x, {x, 0, 10}], ListPlot[{1,2,3}]}]
     = ...
    """

    options = GRAPHICS_OPTIONS
    summary_text = "display graphic objects"

    def eval(self, graphics, evaluation, options):
        """Show[graphics_, OptionsPattern[%(name)s]]"""

        for option in options:
            if option not in ("System`ImageSize",):
                options[option] = eval_N(options[option], evaluation)

        # The below could probably be done with graphics.filter..
        new_elements = []
        options_set = set(options.keys())
        for element in graphics.elements:
            element_name = element.get_head_name()
            if (
                element_name == "System`Rule"
                and str(element.elements[0]) in options_set
            ):
                continue
            new_elements.append(element)

        new_elements += options_to_rules(options)
        graphics = graphics.restructure(graphics.head, new_elements, evaluation)

        return graphics


class Graphics(Builtin):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/Graphics.html</url>

    <dl>
      <dt>'Graphics'[$primitives$, $options$]
      <dd>represents a graphic.
    </dl>

    Options include:

    <ul>
      <li>Axes
      <li>TicksStyle
      <li>AxesStyle
      <li>LabelStyle
      <li>AspectRatio
      <li>PlotRange
      <li>PlotRangePadding
      <li>ImageSize
      <li>Background
    </ul>

    >> Graphics[{Blue, Line[{{0,0}, {1,1}}]}]
     = -Graphics-

    'Graphics' supports 'PlotRange':
    >> Graphics[{Rectangle[{1, 1}]}, Axes -> True, PlotRange -> {{-2, 1.5}, {-1, 1.5}}]
     = -Graphics-

    >> Graphics[{Rectangle[],Red,Disk[{1,0}]},PlotRange->{{0,1},{0,1}}]
     = -Graphics-

    'Graphics' produces 'GraphicsBox' boxes:
    >> Graphics[Rectangle[]] // ToBoxes // Head
     = GraphicsBox

    The 'Background' option allows to set the color of the background:
    >> Graphics[{Green, Disk[]}, Background->RGBColor[.6, .7, 1.]]
     = -Graphics-

    In 'TeXForm', 'Graphics' produces Asymptote figures:
    >> Graphics[Circle[]] // TeXForm
     = #<--#
     . \begin{asy}
     . usepackage("amsmath");
     . size(5.869cm, 5.8333cm);
     . draw(ellipse((175,175),175,175), rgb(0, 0, 0)+linewidth(1.0667));
     . clip(box((-0.53333,0.53333), (350.53,349.47)));
     . \end{asy}
    """

    options = GRAPHICS_OPTIONS

    box_suffix = "Box"
    summary_text = "general two‐dimensional graphics"

    def eval_makeboxes(self, content, evaluation, options):
        """MakeBoxes[%(name)s[content_, OptionsPattern[%(name)s]],
        StandardForm|TraditionalForm]"""
        from mathics.builtin.box.graphics import GraphicsBox
        from mathics.builtin.box.graphics3d import Graphics3DBox
        from mathics.builtin.drawing.graphics3d import Graphics3D
        from mathics.format.box.graphics import primitives_to_boxes

        for option in options:
            if option not in ("System`ImageSize",):
                options[option] = eval_N(options[option], evaluation)

        if type(self) is Graphics:
            return GraphicsBox(
                primitives_to_boxes(content, evaluation, self.box_suffix),
                _evaluation=evaluation,
                **options,
            )
        elif type(self) is Graphics3D:
            return Graphics3DBox(
                primitives_to_boxes(content, evaluation, self.box_suffix),
                _evaluation=evaluation,
                **options,
            )
        raise BoxExpressionError


class _Size(_GraphicsDirective):
    def init(self, graphics, item=None, value=None):
        super(_Size, self).init(graphics, item)
        if item is not None:
            self.value = item.elements[0].round_to_float() * 0.7
        elif value is not None:
            self.value = value
        else:
            raise BoxExpressionError
        if self.value < 0:
            raise BoxExpressionError


class _Thickness(_Size):
    pass


class AbsoluteThickness(_Thickness):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/AbsoluteThickness.html</url>

    <dl>
      <dt>'AbsoluteThickness'[$p$]
      <dd>sets the line thickness for subsequent graphics primitives to $p$ \
          points.
    </dl>

    >> Graphics[Table[{AbsoluteThickness[t], Line[{{20 t, 10}, {20 t, 80}}], Text[ToString[t]<>"pt", {20 t, 0}]}, {t, 0, 10}]]
     = -Graphics-
    """

    summary_text = "graphics directive for the absolute line thickness"

    def get_thickness(self):
        return self.graphics.translate_absolute((self.value, 0))[0]


class Point(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Point.html</url>

    <dl>
      <dt>'Point'[{$point_1$, $point_2$ ...}]
      <dd>represents the point primitive.
      <dt>'Point'[{{$p_11$, $p_12$, ...}, {$p_21$, $p_22$, ...}, ...}]
      <dd>represents a number of point primitives.
    </dl>

    Points are rendered if possible as circular regions. Their diameters can be specified using 'PointSize'.

    Points can be specified as {$x$, $y$}:

    >> Graphics[Point[{0, 0}]]
    = -Graphics-

    >> Graphics[Point[Table[{Sin[t], Cos[t]}, {t, 0, 2. Pi, Pi / 15.}]]]
    = -Graphics-

    or as {$x$, $y$, $z$}:

    >> Graphics3D[{Orange, PointSize[0.05], Point[Table[{Sin[t], Cos[t], 0}, {t, 0, 2 Pi, Pi / 15.}]]}]
     = -Graphics3D-

    """

    summary_text = "point or list of points graphics object(s) in 2D or 3D"


class PointSize(_Size):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/PointSize.html</url>

    <dl>
      <dt>'PointSize'[$t$]
      <dd>sets the diameter of points to $t$, which is relative to the overall width.
    </dl>

    'PointSize' can be used for both two- and three-dimensional graphics. \
    The initial default pointsize is 0.008 for two-dimensional graphics and 0.01 for three-dimensional graphics.

    >> Table[Graphics[{PointSize[r], Point[{0, 0}]}], {r, {0.02, 0.05, 0.1, 0.3}}]
     = {-Graphics-, -Graphics-, -Graphics-, -Graphics-}

    >> Table[Graphics3D[{PointSize[r], Point[{0, 0, 0}]}], {r, {0.05, 0.1, 0.8}}]
    = {-Graphics3D-, -Graphics3D-, -Graphics3D-}
    """

    summary_text = "graphics directive for relative sizes of points"

    def get_absolute_size(self):
        if self.graphics.view_width is None:
            self.graphics.view_width = 400
        if self.value is None:
            self.value = DEFAULT_POINT_FACTOR
        return self.graphics.view_width * self.value


# FIXME: We model points as line segments which
# is kind of  wrong.
class Line(Builtin):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/Line.html</url>

    <dl>
      <dt>'Line'[{$point_1$, $point_2$ ...}]
      <dd>represents the line primitive.

      <dt>'Line'[{{$point_{11}$, $point_{12}$, ...}, {$point_{21}$, $point_{22}$, ...}, ...}]
      <dd>represents a number of line primitives.
    </dl>

    >> Graphics[Line[{{0,1},{0,0},{1,0},{1,1}}]]
    = -Graphics-

    >> Graphics3D[Line[{{0,0,0},{0,1,1},{1,0,0}}]]
    = -Graphics3D-
    """

    summary_text = "line graphics object joining a sequence of points in 2D or 3D"


def _svg_bezier(*segments):
    # see https://www.w3.org/TR/SVG/paths.html#PathDataCubicBezierCommands
    # see https://docs.webplatform.org/wiki/svg/tutorials/smarter_svg_shapes

    while segments and not segments[0][1]:
        segments = segments[1:]

    if not segments:
        return

    forms = "LQC"  # SVG commands for line, quadratic bezier, cubic bezier

    def path(max_degree, p):
        max_degree = min(max_degree, len(forms))
        while p:
            n = min(max_degree, len(p))  # 1, 2, or 3
            if n < 1:
                raise BoxExpressionError
            yield forms[n - 1] + " ".join("%f,%f" % xy for xy in p[:n])
            p = p[n:]

    k, p = segments[0]
    yield "M%f,%f" % p[0]

    for s in path(k, p[1:]):
        yield s

    for k, p in segments[1:]:
        for s in path(k, p):
            yield s


class FilledCurve(Builtin):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/FilledCurve.html</url>

    <dl>
      <dt>'FilledCurve'[{$segment_1$, $segment_2$ ...}]
      <dd>represents a filled curve.
    </dl>

    >> Graphics[FilledCurve[{Line[{{0, 0}, {1, 1}, {2, 0}}]}]]
    = -Graphics-

    >> Graphics[FilledCurve[{BezierCurve[{{0, 0}, {1, 1}, {2, 0}}], Line[{{3, 0}, {0, 2}}]}]]
    = -Graphics-
    """

    summary_text = "a filled area with curve segment boundary in 2D"


class Polygon(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Polygon.html</url>

    <dl>
      <dt>'Polygon'[{$point_1$, $point_2$ ...}]
      <dd>represents the filled polygon primitive.

      <dt>'Polygon'[{{$p_11$, $p_12$, ...}, {$p_21$, $p_22$, ...}, ...}]
      <dd>represents a number of filled polygon primitives.
    </dl>

    A Right Triangle:
    >> Graphics[Polygon[{{1,0},{0,0},{0,1}}]]
    = -Graphics-

    Notice that there is a line connecting from the last point to the first one.

    A point is an element of the polygon if a ray from the point in any direction in \
    the plane crosses the boundary line segments an odd number of times.
    >> Graphics[Polygon[{{150,0},{121,90},{198,35},{102,35},{179,90}}]]
    = -Graphics-

    >> Graphics3D[Polygon[{{0,0,0},{0,1,1},{1,0,0}}]]
    = -Graphics3D-
    """

    summary_text = "graphics primitive for a polygon in 2D or 3D"


class RegularPolygon(Builtin):
    r"""

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/RegularPolygon.html</url>

    <dl>
      <dt>'RegularPolygon'[$n$]
      <dd>gives the regular polygon with $n$ edges.
      <dt>'RegularPolygon'[$r$, $n$]
      <dd>gives the regular polygon with $n$ edges and radius $r$.
      <dt>'RegularPolygon'[{$r$, $\phi$}, $n$]
      <dd>gives the regular polygon with radius $r$ with one vertex drawn at angle $\phi$.
      <dt>'RegularPolygon'[{$x$, $y$}, $r$, $n$]
      <dd>gives the regular polygon centered at the position {$x$, $y$}.
    </dl>

    >> Graphics[RegularPolygon[5]]
    = -Graphics-

    >> Graphics[{Yellow, Rectangle[], Orange, RegularPolygon[{1, 1}, {0.25, 0}, 3]}]
    = -Graphics-
    """

    summary_text = "graphics primitive for a regular polygon in 2D"


class Arrow(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Arrow.html</url>

    <dl>
      <dt>'Arrow'[{$p_1$, $p_2$}]
      <dd>represents a line from $p_1$ to $p_2$ that ends with an arrow at $p_2$.

      <dt>'Arrow'[{$p_1$, $p_2$}, $s$]
      <dd>represents a line with arrow that keeps a distance of $s$ from $p_1$ and $p_2$.

      <dt>'Arrow'[{$point_1$, $point_2$}, {$s_1$, $s_2$}]
      <dd>represents a line with arrow that keeps a distance of $s_1$ from $p_1$ and a \
          distance of $s_2$ from $p_2$.

      <dt>'Arrow'[{$point_1$, $point_2$}, {$s_1$, $s_2$}]
      <dd>represents a line with arrow that keeps a distance of $s_1$ from $p_1$ and a \
          distance of $s_2$ from $p_2$.
    </dl>

    >> Graphics[Arrow[{{0,0}, {1,1}}]]
    = -Graphics-

    >> Graphics[{Circle[], Arrow[{{2, 1}, {0, 0}}, 1]}]
    = -Graphics-

    Arrows can also be drawn in 3D by giving point in three dimensions:

    >> Graphics3D[Arrow[{{1, 1, -1}, {2, 2, 0}, {3, 3, -1}, {4, 4, 0}}]]
     = -Graphics3D-

    Keeping distances may happen across multiple segments:

    >> Table[Graphics[{Circle[], Arrow[Table[{Cos[phi],Sin[phi]},{phi,0,2*Pi,Pi/2}],{d, d}]}],{d,0,2,0.5}]
     = {-Graphics-, -Graphics-, -Graphics-, -Graphics-, -Graphics-}
    """

    summary_text = "graphics primitive for arbitrary graphical arrows"


class Arrowheads(_GraphicsDirective):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Arrowheads.html</url>

    <dl>
      <dt>'Arrowheads'[$s$]
      <dd>specifies that Arrow[] draws one arrow of size $s$ (relative to width of \
          image, defaults to 0.04).

      <dt>'Arrowheads'[{$spec_1$, $spec_2$, ..., $spec_n$}]
      <dd>specifies that Arrow[] draws n arrows as defined by $spec_1$, $spec_2$, \
          ... $spec_n$.

      <dt>'Arrowheads'[{{$s$}}]
      <dd>specifies that one arrow of size $s$ should be drawn.

      <dt>'Arrowheads'[{{$s$, $pos$}}]
      <dd>specifies that one arrow of size $s$ should be drawn at position $pos$ (for \
          the arrow to be on the line, $pos$ has to be between 0, i.e. the start for \
          the line, and 1, i.e. the end of the line).

      <dt>'Arrowheads'[{{$s$, $pos$, $g$}}]
      <dd>specifies that one arrow of size $s$ should be drawn at position $pos$ \
          using Graphics $g$.
    </dl>

    Arrows on both ends can be achieved using negative sizes:

    >> Graphics[{Circle[],Arrowheads[{-0.04, 0.04}], Arrow[{{0, 0}, {2, 2}}, {1,1}]}]
     = -Graphics-

    You may also specify our own arrow shapes:

    >> Graphics[{Circle[], Arrowheads[{{0.04, 1, Graphics[{Red, Disk[]}]}}], Arrow[{{0, 0}, {Cos[Pi/3],Sin[Pi/3]}}]}]
     = -Graphics-

    >> Graphics[{Arrowheads[Table[{0.04, i/10, Graphics[Disk[]]},{i,1,10}]], Arrow[{{0, 0}, {6, 5}, {1, -3}, {-2, 2}}]}]
     = -Graphics-
    """

    default_size = 0.04

    summary_text = "graphics directive for the form and placement of an arrowhead"

    symbolic_sizes = {
        "System`Tiny": 3,
        "System`Small": 5,
        "System`Medium": 9,
        "System`Large": 18,
    }

    def init(self, graphics, item=None):
        super(Arrowheads, self).init(graphics, item)
        if len(item.elements) != 1:
            raise BoxExpressionError
        self.spec = item.elements[0]

    def _arrow_size(self, s, extent):
        if isinstance(s, Symbol):
            size = self.symbolic_sizes.get(s.get_name(), 0)
            return self.graphics.translate_absolute((size, 0))[0]
        else:
            return _to_float(s) * extent

    def heads(self, extent, default_arrow, custom_arrow):
        # see https://reference.wolfram.com/language/ref/Arrowheads.html

        if self.spec.get_head_name() == "System`List":
            elements = self.spec.elements
            if all(x.get_head_name() == "System`List" for x in elements):
                for head in elements:
                    spec = head.elements
                    if len(spec) not in (2, 3):
                        raise BoxExpressionError
                    size_spec = spec[0]
                    if (
                        isinstance(size_spec, Symbol)
                        and size_spec.get_name() == "System`Automatic"
                    ):
                        s = self.default_size * extent
                    elif size_spec.is_numeric():
                        s = self._arrow_size(size_spec, extent)
                    else:
                        raise BoxExpressionError

                    if len(spec) == 3 and custom_arrow:
                        graphics = spec[2]
                        if graphics.get_head_name() != "System`Graphics":
                            raise BoxExpressionError
                        arrow = custom_arrow(graphics)
                    else:
                        arrow = default_arrow

                    if not isinstance(spec[1], (Real, Rational, Integer)):
                        raise BoxExpressionError

                    yield s, _to_float(spec[1]), arrow
            else:
                n = max(1.0, len(elements) - 1.0)
                for i, head in enumerate(elements):
                    yield self._arrow_size(head, extent), i / n, default_arrow
        else:
            yield self._arrow_size(self.spec, extent), 1, default_arrow


def _norm(p, q):
    px, py = p
    qx, qy = q

    dx = qx - px
    dy = qy - py

    length = sqrt(dx * dx + dy * dy)
    return dx, dy, length


# belongs to mathics.format.box.graph?
class _Line:
    def make_draw_svg(self, style):
        def draw(points):
            yield '<polyline points="'
            yield " ".join("%f,%f" % xy for xy in points)
            yield '" style="%s" />' % style

        return draw

    def make_draw_asy(self, pen):
        def draw(points):
            yield "draw("
            yield "--".join(["(%.5g,%5g)" % xy for xy in points])
            yield ", % s);" % pen

        return draw

    def arrows(self, points, heads):  # heads has to be sorted by pos
        def segments(points):
            for i in range(len(points) - 1):
                px, py = points[i]
                dx, dy, dl = _norm((px, py), points[i + 1])
                yield dl, px, py, dx, dy

        seg = list(segments(points))

        if not seg:
            return

        i = 0
        t0 = 0.0
        n = len(seg)
        dl, px, py, dx, dy = seg[i]
        total = sum(segment[0] for segment in seg)

        for s, t, draw in ((s, pos * total - t0, draw) for s, pos, draw in heads):
            if s == 0.0:  # ignore zero-sized arrows
                continue

            if i < n:  # not yet past last segment?
                while t > dl:  # position past current segment?
                    t -= dl
                    t0 += dl
                    i += 1
                    if i == n:
                        px += dx  # move to last segment's end
                        py += dy
                        break
                    else:
                        dl, px, py, dx, dy = seg[i]

            for shape in draw(px, py, dx / dl, dy / dl, t, s):
                yield shape


def _bezier_derivative(p):
    # see http://pomax.github.io/bezierinfo/, Section 12 Derivatives
    n = len(p[0]) - 1
    return [[n * (x1 - x0) for x1, x0 in zip(w, w[1:])] for w in p]


def _bezier_evaluate(p, t):
    # see http://pomax.github.io/bezierinfo/, Section 4 Controlling Bezier Curvatures
    n = len(p[0]) - 1
    if n == 3:
        t2 = t * t
        t3 = t2 * t
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        return [
            w[0] * mt3 + 3 * w[1] * mt2 * t + 3 * w[2] * mt * t2 + w[3] * t3 for w in p
        ]
    elif n == 2:
        t2 = t * t
        mt = 1 - t
        mt2 = mt * mt
        return [w[0] * mt2 + w[1] * 2 * mt * t + w[2] * t2 for w in p]
    elif n == 1:
        mt = 1 - t
        return [w[0] * mt + w[1] * t for w in p]
    else:
        raise ValueError("cannot compute bezier curve of order %d" % n)


class _BezierCurve:
    def __init__(self, spline_degree=3):
        self.spline_degree = spline_degree

    def make_draw_svg(self, style):
        def draw(points):
            s = " ".join(_svg_bezier((self.spline_degree, points)))
            yield '<path d="%s" style="%s"/>' % (s, style)

        return draw

    def make_draw_asy(self, pen):
        from mathics.format.render.asy_fns import asy_bezier

        def draw(points):
            for path in asy_bezier((self.spline_degree, points)):
                yield "draw(%s, %s);" % (path, pen)

        return draw

    def arrows(self, points, heads):  # heads has to be sorted by pos
        if len(points) < 2:
            return

        # FIXME combined curves

        cp = list(zip(*points))
        if len(points) >= 3:
            dcp = _bezier_derivative(cp)
        else:
            dcp = cp

        for s, t, draw in heads:
            if s == 0.0:  # ignore zero-sized arrows
                continue

            px, py = _bezier_evaluate(cp, t)

            tx, ty = _bezier_evaluate(dcp, t)
            tl = -sqrt(tx * tx + ty * ty)
            tx /= tl
            ty /= tl

            for shape in draw(px, py, tx, ty, 0.0, s):
                yield shape


class Circle(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Circle.html</url>

    <dl>
      <dt>'Circle'[{$c_x$, $c_y$}, $r$]
      <dd>draws a circle with center '($c_x$, $c_y$)' and radius $r$.

      <dt>'Circle'[{$c_x$, $c_y$}, {$r_x$, $r_y$}]
      <dd>draws an ellipse.

      <dt>'Circle'[{$c_x$, $c_y$}]
      <dd>chooses radius 1.

      <dt>'Circle[]'
      <dd>chooses center '(0, 0)' and radius 1.
    </dl>

    >> Graphics[{Red, Circle[{0, 0}, {2, 1}]}]
     = -Graphics-
    >> Graphics[{Circle[], Disk[{0, 0}, {1, 1}, {0, 2.1}]}]
     = -Graphics-

    Target practice:
    >> Graphics[Circle[], Axes-> True]
     = -Graphics-
    """

    rules = {"Circle[]": "Circle[{0, 0}]"}
    summary_text = "graphics primitive for an empty circle, ellipse, or arc"


class Disk(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Disk.html</url>

    <dl>
      <dt>'Disk'[{$c_x$, $c_y$}, $r$]
      <dd>fills a circle with center ($c_x$, $c_y$) and radius $r$.

      <dt>'Disk'[{$c_x$, $c_y$}, {$r_x$, $r_y$}]
      <dd>fills an ellipse.

      <dt>'Disk'[{$c_x$, $c_y$}]
      <dd>chooses radius 1.

      <dt>'Disk[]'
      <dd>chooses center $(0, 0)$' and radius 1.

      <dt>'Disk'[{$x$, $y$}, ..., {$t_1$, $t_2$}]
      <dd>is a sector from angle $t_1$ to $t_2$.
    </dl>

    >> Graphics[{Blue, Disk[{0, 0}, {2, 1}]}]
     = -Graphics-
    The outer border can be drawn using 'EdgeForm':
    >> Graphics[{EdgeForm[Black], Red, Disk[]}]
     = -Graphics-

    Disk can also draw sectors of circles and ellipses
    >> Graphics[Disk[{0, 0}, 1, {Pi / 3, 2 Pi / 3}]]
     = -Graphics-
    >> Graphics[{Blue, Disk[{0, 0}, {1, 2}, {Pi / 3, 5 Pi / 3}]}]
     = -Graphics-
    """

    rules = {"Disk[]": "Disk[{0, 0}]"}
    summary_text = "create a filled circle, ellipse or arc graphics object"


class Directive(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Directive.html</url>

    <dl>
      <dt> 'Directive'[$g_1$, $g_2$, ...]
      <dd> represents a single graphics directive composed of the directives $g_1$, $g_2$, ...
    </dl>
    """

    attributes = A_READ_PROTECTED | A_PROTECTED
    summary_text = "compound directive"


class EdgeForm(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/EdgeForm.html</url>

    <dl>
      <dt> 'EdgeForm'[$g$]
      <dd> is a graphics directive that specifies that edges of filled graphics objects are to be drawn using the graphics directive or list of directives $g$.
    </dl>

    >> Graphics[{EdgeForm[{Thick, Green}], Disk[]}]
     = -Graphics-

    >> Graphics[{Style[Disk[],EdgeForm[{Thick,Red}]], Circle[{1,1}]}]
     = -Graphics-
    """

    summary_text = "rendering properties for edges"


class FaceForm(Builtin):
    """
    <url>:WMA link
    :https://reference.wolfram.com/language/ref/FaceForm.html</url>

    <dl>
      <dt> 'FaceForm'[$g$]
      <dd> is a graphics directive that specifies that faces of filled graphics\
           objects are to be drawn using the graphics directive or list of \
           directives $g$.
    </dl>
    """

    summary_text = "rendering properties for faces"


class FontColor(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/FontColor.html</url>

    <dl>
      <dt>'FontColor'
      <dd>is an option for Style to set the font color.
    </dl>
    """

    summary_text = "color of characters"


class Inset(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Inset.html</url>

    <dl>
      <dt>'Text'[$obj$]
      <dd>represents an object $obj$ inset in a graphic.

      <dt>'Text'[$obj$, $pos$]
      <dd>represents an object $obj$ inset in a graphic at position $pos$.

      <dt>'Text'[$obj$, $pos$, $opos$]
      <dd>represents an object $obj$ inset in a graphic at position $pos$, \
          in away that the position $opos$ of $obj$ coincides with $pos$ \
          in the enclosing graphic.
    </dl>
    """

    summary_text = "arbitrary objects in 2D or 3D inset into a larger graphic"


class Large(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Large.html</url>

    <dl>
      <dt>'ImageSize' -> 'Large'
      <dd>produces a large image.
    </dl>
    """

    summary_text = "large size symbol for style or option setting"


class Medium(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Medium.html</url>

    <dl>
      <dt>'ImageSize' -> 'Medium'
      <dd>produces a medium-sized image.
    </dl>
    """

    summary_text = "medium size symbol for style or option setting"


class Offset(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Offset.html</url>

    <dl>
      <dt>'Offset'[{$d_x$, $d_y$}, $position$]
      <dd>gives the position of a graphical object obtained by starting at the specified $position$ and then moving by absolute offset {$d_x$,$d_y$}.
    </dl>
    """

    summary_text = "offset a graphics object by a specified position"


class Rectangle(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Rectangle.html</url>

    <dl>
      <dt>'Rectangle'[{$x_{min}$, $y_{min}$}]
      <dd>represents a unit square with bottom-left corner at {$x_{min}$, $y_{min}$}.
      <dt>'Rectangle[{$x_{min}$, $y_{min}$}, {$x_{max}$, $y_{max}$}]
      <dd>is a rectangle extending from {$x_{min}$, $y_{min}$} to {$x_{max}$, $y_{max}$}.
    </dl>

    >> Graphics[Rectangle[]]
     = -Graphics-

    >> Graphics[{Blue, Rectangle[{0.5, 0}], Orange, Rectangle[{0, 0.5}]}]
     = -Graphics-
    """

    rules = {"Rectangle[]": "Rectangle[{0, 0}]"}
    summary_text = "create a 2D filled rectangle graphical object"


class Small(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Small.html</url>

    <dl>
      <dt>'ImageSize' -> 'Small'
      <dd>produces a small image.
    </dl>
    """

    summary_text = "small size style or option setting"


class Text(Inset):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Text.html</url>

    <dl>
      <dt>'Text'["$text$", {$x$, $y$}]
      <dd>draws $text$ centered on position {$x$, $y$}.
    </dl>

    >> Graphics[{Text["First", {0, 0}], Text["Second", {1, 1}]}, Axes->True, PlotRange->{{-2, 2}, {-2, 2}}]
     = -Graphics-
    """

    summary_text = "arbitrary text or other expressions in 2D or 3D"


class Thick(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Thick.html</url>

    <dl>
      <dt>'Thick'
      <dd>sets the line width for subsequent graphics primitives to 2pt.
    </dl>
    """

    rules = {"Thick": "AbsoluteThickness[2]"}
    summary_text = "graphics directive to make thicker lines"


class Thin(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Thin.html</url>

    <dl>
      <dt>'Thin'
      <dd>sets the line width for subsequent graphics primitives to 0.5pt.
    </dl>
    """

    rules = {"Thin": "AbsoluteThickness[0.5]"}
    summary_text = "graphics directive to make thinner lines"


class Thickness(_Thickness):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Thickness.html</url>

    <dl>
      <dt>'Thickness'[$t$]
      <dd>sets the line thickness for subsequent graphics primitives to $t$ times the size of the plot area.
    </dl>

    >> Graphics[{Thickness[0.2], Line[{{0, 0}, {0, 5}}]}, Axes->True, PlotRange->{{-5, 5}, {-5, 5}}]
     = -Graphics-
    """

    summary_text = "graphics directive for line thicknesses"

    def get_thickness(self):
        return self.graphics.translate_relative(self.value)


class Tiny(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Tiny.html</url>

    <dl>
      <dt>'ImageSize' -> 'Tiny'
      <dd>produces a tiny image.
    </dl>
    """

    summary_text = "tiny size style or option setting"


ELEMENT_HEADS = frozenset(
    symbol_set(
        Symbol("System`Arrow"),
        Symbol("System`BezierCurve"),
        Symbol("System`Circle"),
        Symbol("System`Cone"),
        Symbol("System`Cuboid"),
        Symbol("System`Cylinder"),
        Symbol("System`Disk"),
        Symbol("System`FilledCurve"),
        SymbolInset,
        SymbolLine,
        SymbolPoint,
        SymbolPolygon,
        Symbol("System`Rectangle"),
        Symbol("System`RegularPolygon"),
        Symbol("System`Sphere"),
        SymbolStyle,
        SymbolText,
        Symbol("System`Tube"),
        Symbol("System`UniformPolyhedron"),
    )
)


STYLES = system_symbols_dict(
    {
        "RGBColor": RGBColor,
        "XYZColor": XYZColor,
        "LABColor": LABColor,
        "LCHColor": LCHColor,
        "LUVColor": LUVColor,
        "CMYKColor": CMYKColor,
        "Hue": Hue,
        "GrayLevel": GrayLevel,
        "Thickness": Thickness,
        "AbsoluteThickness": AbsoluteThickness,
        "Thick": Thick,
        "Thin": Thin,
        "PointSize": PointSize,
        "Arrowheads": Arrowheads,
        "Opacity": Opacity,
    }
)


STYLE_HEADS = frozenset(STYLES.keys())
STYLE_AND_FORM_HEADS = frozenset(
    STYLE_HEADS.union(symbol_set(SymbolEdgeForm, SymbolFaceForm))
)
GLOBALS.update(
    system_symbols_dict(
        {
            "Rectangle": Rectangle,
            "Disk": Disk,
            "Circle": Circle,
            "Polygon": Polygon,
            "RegularPolygon": RegularPolygon,
            "Inset": Inset,
            "Text": Text,
        }
    )
)

GLOBALS.update(STYLES)

GRAPHICS_SYMBOLS = {
    SymbolList,
    SymbolRule,
    Symbol("System`VertexColors"),
    *ELEMENT_HEADS,
    *[Symbol(element.name + "Box") for element in ELEMENT_HEADS],
    *STYLE_HEADS,
}
