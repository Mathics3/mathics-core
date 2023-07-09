# -*- coding: utf-8 -*-
# cython: language_level=3

"""
Drawing Graphics
"""

# This following line tells documentation how to sort this module
sort_order = "mathics.builtin.drawing-graphics"

from math import sqrt

from mathics.builtin.base import Builtin
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
    _ColorObject,
)
from mathics.builtin.drawing.graphics_internals import (
    GLOBALS,
    _GraphicsDirective,
    _GraphicsElementBox,
    get_class,
)
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Integer, Rational, Real
from mathics.core.attributes import A_PROTECTED, A_READ_PROTECTED
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.exceptions import BoxExpressionError
from mathics.core.expression import Expression
from mathics.core.formatter import lookup_method
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Symbol,
    SymbolList,
    SymbolNull,
    symbol_set,
    system_symbols_dict,
)
from mathics.core.systemsymbols import (
    SymbolEdgeForm,
    SymbolFaceForm,
    SymbolMakeBoxes,
    SymbolRule,
)
from mathics.eval.nevaluator import eval_N

GRAPHICS_OPTIONS = {
    "AspectRatio": "Automatic",
    "Axes": "False",
    "AxesStyle": "{}",
    "Background": "Automatic",
    "ImageSize": "Automatic",
    "LabelStyle": "{}",
    "PlotRange": "Automatic",
    "PlotRangePadding": "Automatic",
    "TicksStyle": "{}",
    "$OptionSyntax": "Ignore",
}

# fraction of point relative canvas width
DEFAULT_POINT_FACTOR = 0.005


class CoordinatesError(BoxExpressionError):
    pass


def coords(value):
    if value.has_form("List", 2):
        x, y = value.elements[0].round_to_float(), value.elements[1].round_to_float()
        if x is None or y is None:
            raise CoordinatesError
        return (x, y)
    raise CoordinatesError


class Coords:
    def __init__(self, graphics, expr=None, pos=None, d=None):
        self.graphics = graphics
        self.p = pos
        self.d = d
        if expr is not None:
            if expr.has_form("Offset", 1, 2):
                self.d = coords(expr.elements[0])
                if len(expr.elements) > 1:
                    self.p = coords(expr.elements[1])
                else:
                    self.p = None
            else:
                self.p = coords(expr)

    def pos(self):
        p = self.graphics.translate(self.p)
        p = (cut(p[0]), cut(p[1]))
        if self.d is not None:
            d = self.graphics.translate_absolute(self.d)
            return (p[0] + d[0], p[1] + d[1])
        return p

    def add(self, x, y):
        p = (self.p[0] + x, self.p[1] + y)
        return Coords(self.graphics, pos=p, d=self.d)


def cut(value):
    "Cut values in graphics primitives (not displayed otherwise in SVG)"
    border = 10**8
    if value < -border:
        value = -border
    elif value > border:
        value = border
    return value


def _to_float(x):
    x = x.round_to_float()
    if x is None:
        raise BoxExpressionError
    return x


def _data_and_options(elements, defined_options):
    data = []
    options = defined_options.copy()
    for element in elements:
        if element.get_head_name() == "System`Rule":
            if len(element.elements) != 2:
                raise BoxExpressionError
            name, value = element.elements
            name_head = name.get_head_name()
            if name_head == "System`Symbol":
                py_name = name.get_name()
            elif name_head == "System`String":
                py_name = "System`" + name.get_string_value()
            else:  # unsupported name type
                raise BoxExpressionError
            options[py_name] = value
        else:
            data.append(element)
    return data, options


def _extract_graphics(graphics, format, evaluation):
    graphics_box = Expression(SymbolMakeBoxes, graphics).evaluate(evaluation)
    # builtin = GraphicsBox(expression=False)
    elements, calc_dimensions = graphics_box._prepare_elements(
        graphics_box.elements, {"evaluation": evaluation}, neg_y=True
    )
    xmin, xmax, ymin, ymax, _, _, _, _ = calc_dimensions()

    # xmin, xmax have always been moved to 0 here. the untransformed
    # and unscaled bounds are found in elements.xmin, elements.ymin,
    # elements.extent_width, elements.extent_height.

    # now compute the position of origin (0, 0) in the transformed
    # coordinate space.

    ex = elements.extent_width
    ey = elements.extent_height

    sx = (xmax - xmin) / ex
    sy = (ymax - ymin) / ey

    ox = -elements.xmin * sx + xmin
    oy = -elements.ymin * sy + ymin

    # generate code for svg or asy.

    if format in ("asy", "svg"):
        format_fn = lookup_method(elements, format)
        code = format_fn(elements)
    else:
        raise NotImplementedError

    return xmin, xmax, ymin, ymax, ox, oy, ex, ey, code


class Show(Builtin):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/Show.html</url>

    <dl>
      <dt>'Show[$graphics$, $options$]'
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
      <dt>'Graphics[$primitives$, $options$]'
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

    In 'TeXForm', 'Graphics' produces Asymptote figures:
    >> Graphics[Circle[]] // TeXForm
     = #<--#
     . \begin{asy}
     . usepackage("amsmath");
     . size(5.8556cm, 5.8333cm);
     . draw(ellipse((175,175),175,175), rgb(0, 0, 0)+linewidth(0.66667));
     . clip(box((-0.33333,0.33333), (350.33,349.67)));
     . \end{asy}
    """

    options = GRAPHICS_OPTIONS

    box_suffix = "Box"
    summary_text = "general two‐dimensional graphics"

    def eval_makeboxes(self, content, evaluation, options):
        """MakeBoxes[%(name)s[content_, OptionsPattern[%(name)s]],
        StandardForm|TraditionalForm|OutputForm]"""

        def convert(content):
            head = content.get_head()

            if head is SymbolList:
                return to_mathics_list(
                    *content.elements, elements_conversion_fn=convert
                )
            elif head is Symbol("System`Style"):
                return to_expression(
                    "StyleBox", *[convert(item) for item in content.elements]
                )

            if head in element_heads:
                if head is Symbol("System`Text"):
                    head = Symbol("System`Inset")
                atoms = content.get_atoms(include_heads=False)
                if any(
                    not isinstance(atom, (Integer, Real))
                    and atom not in GRAPHICS_SYMBOLS
                    for atom in atoms
                ):
                    if head is Symbol("System`Inset"):
                        inset = content.elements[0]
                        if inset.get_head() is Symbol("System`Graphics"):
                            opts = {}
                            # opts = dict(opt._elements[0].name:opt_elements[1]   for opt in  inset._elements[1:])
                            inset = self.eval_makeboxes(
                                inset._elements[0], evaluation, opts
                            )
                        n_elements = [inset] + [
                            eval_N(element, evaluation)
                            for element in content.elements[1:]
                        ]
                    else:
                        n_elements = (
                            eval_N(element, evaluation) for element in content.elements
                        )
                else:
                    n_elements = content.elements
                return Expression(Symbol(head.name + self.box_suffix), *n_elements)
            return content

        for option in options:
            if option not in ("System`ImageSize",):
                options[option] = eval_N(options[option], evaluation)

        from mathics.builtin.box.graphics import GraphicsBox
        from mathics.builtin.box.graphics3d import Graphics3DBox
        from mathics.builtin.drawing.graphics3d import Graphics3D

        if type(self) is Graphics:
            return GraphicsBox(
                convert(content), evaluation=evaluation, *options_to_rules(options)
            )
        elif type(self) is Graphics3D:
            return Graphics3DBox(
                convert(content), evaluation=evaluation, *options_to_rules(options)
            )


class _Polyline(_GraphicsElementBox):
    """
    A structure containing a list of line segments
    stored in ``self.lines`` created from
    a list of points.

    Lines are formed by pairs of consecutive point.
    """

    def do_init(self, graphics, points):
        if not points.has_form("List", None):
            raise BoxExpressionError
        if (
            points.elements
            and points.elements[0].has_form("List", None)
            and all(
                element.has_form("List", None)
                for element in points.elements[0].elements
            )
        ):
            elements = points.elements
            self.multi_parts = True
        elif len(points.elements) == 0:
            # Ensure there are no line segments if there are no points.
            self.lines = []
            return
        else:
            elements = [ListExpression(*points.elements)]
            self.multi_parts = False
        lines = []
        for element in elements:
            if element.has_form("List", None):
                lines.append(element.elements)
            else:
                raise BoxExpressionError
        self.lines = [
            [graphics.coords(graphics, point) for point in line] for line in lines
        ]

    def extent(self) -> list:
        lw = self.style.get_line_width(face_element=False)
        result = []
        for line in self.lines:
            for c in line:
                x, y = c.pos()
                result.extend(
                    [
                        (x - lw, y - lw),
                        (x - lw, y + lw),
                        (x + lw, y - lw),
                        (x + lw, y + lw),
                    ]
                )
        return result


class _Size(_GraphicsDirective):
    def init(self, graphics, item=None, value=None):
        super(_Size, self).init(graphics, item)
        if item is not None:
            self.value = item.elements[0].round_to_float()
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
      <dt>'AbsoluteThickness[$p$]'
      <dd>sets the line thickness for subsequent graphics primitives to $p$ \
          points.
    </dl>

    >> Graphics[Table[{AbsoluteThickness[t], Line[{{20 t, 10}, {20 t, 80}}], Text[ToString[t]<>"pt", {20 t, 0}]}, {t, 0, 10}]]
     = -Graphics-
    """

    summary_text = "graphics directive be specifying absolute line thickness"

    def get_thickness(self):
        return self.graphics.translate_absolute((self.value, 0))[0]


class Point(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Point.html</url>

    <dl>
      <dt>'Point[{$point_1$, $point_2$ ...}]'
      <dd>represents the point primitive.
      <dt>'Point[{{$p_11$, $p_12$, ...}, {$p_21$, $p_22$, ...}, ...}]'
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
      <dt>'PointSize[$t$]'
      <dd>sets the diameter of points to $t$, which is relative to the overall width.
    </dl>
    'PointSize' can be used for both two- and three-dimensional graphics. The initial default pointsize is 0.008 for two-dimensional graphics and 0.01 for three-dimensional graphics.

    >> Table[Graphics[{PointSize[r], Point[{0, 0}]}], {r, {0.02, 0.05, 0.1, 0.3}}]
     = {-Graphics-, -Graphics-, -Graphics-, -Graphics-}

    >> Table[Graphics3D[{PointSize[r], Point[{0, 0, 0}]}], {r, {0.05, 0.1, 0.8}}]
    = {-Graphics3D-, -Graphics3D-, -Graphics3D-}
    """

    summary_text = "graphics directive specifying relative sizes of points"

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
      <dt>'Line[{$point_1$, $point_2$ ...}]'
      <dd>represents the line primitive.

      <dt>'Line[{{$p_11$, $p_12$, ...}, {$p_21$, $p_22$, ...}, ...}]'
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
      <dt>'FilledCurve[{$segment1$, $segment2$ ...}]'
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
      <dt>'Polygon[{$point_1$, $point_2$ ...}]'
      <dd>represents the filled polygon primitive.

      <dt>'Polygon[{{$p_11$, $p_12$, ...}, {$p_21$, $p_22$, ...}, ...}]'
      <dd>represents a number of filled polygon primitives.
    </dl>

    A Right Triangle:
    >> Graphics[Polygon[{{1,0},{0,0},{0,1}}]]
    = -Graphics-

    Notice that there is a line connecting from the last point to the first one.

    A point is an element of the polygon if a ray from the point in any direction in the plane crosses the boundary line segments an odd number of times.
    >> Graphics[Polygon[{{150,0},{121,90},{198,35},{102,35},{179,90}}]]
    = -Graphics-

    >> Graphics3D[Polygon[{{0,0,0},{0,1,1},{1,0,0}}]]
    = -Graphics3D-
    """

    summary_text = "a polygon in 2D or 3D"


class RegularPolygon(Builtin):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/RegularPolygon.html</url>

    <dl>
      <dt>'RegularPolygon[$n$]'
      <dd>gives the regular polygon with $n$ edges.
      <dt>'RegularPolygon[$r$, $n$]'
      <dd>gives the regular polygon with $n$ edges and radius $r$.
      <dt>'RegularPolygon[{$r$, $phi$}, $n$]'
      <dd>gives the regular polygon with radius $r$ with one vertex drawn at angle $phi$.
      <dt>'RegularPolygon[{$x, $y}, $r$, $n$]'
      <dd>gives the regular polygon centered at the position {$x, $y}.
    </dl>

    >> Graphics[RegularPolygon[5]]
    = -Graphics-

    >> Graphics[{Yellow, Rectangle[], Orange, RegularPolygon[{1, 1}, {0.25, 0}, 3]}]
    = -Graphics-
    """

    summary_text = "a regular polygon in 2D"


class Arrow(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Arrow.html</url>

    <dl>
      <dt>'Arrow[{$p1$, $p2$}]'
      <dd>represents a line from $p1$ to $p2$ that ends with an arrow at $p2$.

      <dt>'Arrow[{$p1$, $p2$}, $s$]'
      <dd>represents a line with arrow that keeps a distance of $s$ from $p1$ and $p2$.

      <dt>'Arrow[{$point_1$, $point_2$}, {$s1$, $s2$}]'
      <dd>represents a line with arrow that keeps a distance of $s1$ from $p1$ and a distance of $s2$ from $p2$.

      <dt>'Arrow[{$point_1$, $point_2$}, {$s1$, $s2$}]'
      <dd>represents a line with arrow that keeps a distance of $s1$ from $p1$ and a distance of $s2$ from $p2$.
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

    summary_text = "graphics primitive to specify arbitrary graphical arrows"


class Arrowheads(_GraphicsDirective):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Arrowheads.html</url>

    <dl>
      <dt>'Arrowheads[$s$]'
      <dd>specifies that Arrow[] draws one arrow of size $s$ (relative to width of image, defaults to 0.04).

      <dt>'Arrowheads[{$spec1$, $spec2$, ..., $specn$}]'
      <dd>specifies that Arrow[] draws n arrows as defined by $spec1$, $spec2$, ... $specn$.

      <dt>'Arrowheads[{{$s$}}]'
      <dd>specifies that one arrow of size $s$ should be drawn.

      <dt>'Arrowheads[{{$s$, $pos$}}]'
      <dd>specifies that one arrow of size $s$ should be drawn at position $pos$ (for the arrow to be on the line, $pos$ has to be between 0, i.e. the start for the line, and 1, i.e. the end of the line).

      <dt>'Arrowheads[{{$s$, $pos$, $g$}}]'
      <dd>specifies that one arrow of size $s$ should be drawn at position $pos$ using Graphics $g$.
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

    summary_text = (
        "graphics directive specifying the form and placement of an arrowhead"
    )

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
        from mathics.format.asy_fns import asy_bezier

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


def total_extent(extents):
    xmin = xmax = ymin = ymax = None
    for extent in extents:
        for x, y in extent:
            if xmin is None or x < xmin:
                xmin = x
            if xmax is None or x > xmax:
                xmax = x
            if ymin is None or y < ymin:
                ymin = y
            if ymax is None or y > ymax:
                ymax = y
    return xmin, xmax, ymin, ymax


def _style(graphics, item):
    head = item.get_head()
    if head in style_heads:
        klass = get_class(head)
        style = klass.create_as_style(klass, graphics, item)
    elif head in (SymbolEdgeForm, SymbolFaceForm):
        style = graphics.style_class(
            graphics, edge=head is SymbolEdgeForm, face=head is SymbolFaceForm
        )
        if len(item.elements) > 1:
            raise BoxExpressionError
        if item.elements:
            if item.elements[0].has_form("List", None):
                for dir in item.elements[0].elements:
                    style.append(dir, allow_forms=False)
            else:
                style.append(item.elements[0], allow_forms=False)
    else:
        raise BoxExpressionError
    return style


class Style:
    def __init__(self, graphics, edge=False, face=False):
        self.styles = []
        self.options = {}
        self.graphics = graphics
        self.edge = edge
        self.face = face
        self.klass = graphics.style_class

    def append(self, item, allow_forms=True):
        self.styles.append(_style(self.graphics, item))

    def set_option(self, name, value):
        self.options[name] = value

    def extend(self, style):
        self.styles.extend(style.styles)

    def clone(self):
        result = self.klass(self.graphics, edge=self.edge, face=self.face)
        result.styles = self.styles[:]
        result.options = self.options.copy()
        return result

    def get_default_face_color(self):
        return RGBColor(components=(0, 0, 0, 1))

    def get_default_edge_color(self):
        return RGBColor(components=(0, 0, 0, 1))

    def get_style(
        self, style_class, face_element=None, default_to_faces=True, consider_forms=True
    ):
        if face_element is not None:
            default_to_faces = consider_forms = face_element
        edge_style = face_style = None
        if style_class == _ColorObject:
            if default_to_faces:
                face_style = self.get_default_face_color()
            else:
                edge_style = self.get_default_edge_color()
        elif style_class == _Thickness:
            if not default_to_faces:
                edge_style = AbsoluteThickness(self.graphics, value=0.5)
        for item in self.styles:
            if isinstance(item, style_class):
                if default_to_faces:
                    face_style = item
                else:
                    edge_style = item
            elif isinstance(item, Style):
                if consider_forms:
                    if item.edge:
                        edge_style, _ = item.get_style(
                            style_class, default_to_faces=False, consider_forms=False
                        )
                    elif item.face:
                        _, face_style = item.get_style(
                            style_class, default_to_faces=True, consider_forms=False
                        )
        return edge_style, face_style

    def get_option(self, name):
        return self.options.get(name, None)

    def get_line_width(self, face_element=True):
        if self.graphics.pixel_width is None:
            return 0
        edge_style, _ = self.get_style(
            _Thickness, default_to_faces=face_element, consider_forms=face_element
        )
        if edge_style is None:
            return 0
        return edge_style.get_thickness()


def _flatten(elements):
    for element in elements:
        if element.get_head() is SymbolList:
            flattened = element.flatten_with_respect_to_head(SymbolList)
            if flattened.get_head() is SymbolList:
                for x in flattened.elements:
                    yield x
            else:
                yield flattened
        else:
            yield element


class _GraphicsElements:
    style_class = Style

    def __init__(self, content, evaluation):
        self.evaluation = evaluation
        self.elements = []

        builtins = evaluation.definitions.builtin

        def get_options(name):
            builtin = builtins.get(name)
            if builtin is None:
                return None
            return builtin.options

        def stylebox_style(style, specs):
            new_style = style.clone()
            for spec in _flatten(specs):
                head = spec.get_head()
                if head in style_and_form_heads:
                    new_style.append(spec)
                elif head is Symbol("System`Rule") and len(spec.elements) == 2:
                    option, expr = spec.elements
                    if not isinstance(option, Symbol):
                        raise BoxExpressionError

                    name = option.get_name()
                    create = style_options.get(name, None)
                    if create is None:
                        raise BoxExpressionError

                    new_style.set_option(name, create(style.graphics, expr))
                else:
                    raise BoxExpressionError
            return new_style

        def convert(content, style):
            if content.has_form("List", None):
                items = content.elements
            else:
                items = [content]
            style = style.clone()
            for item in items:
                if item is SymbolNull:
                    continue
                head = item.get_head()
                if head in style_and_form_heads:
                    style.append(item)
                elif head is Symbol("System`StyleBox"):
                    if len(item.elements) < 1:
                        raise BoxExpressionError
                    for element in convert(
                        item.elements[0], stylebox_style(style, item.elements[1:])
                    ):
                        yield element
                elif head.name[-3:] == "Box":  # and head[:-3] in element_heads:
                    element_class = get_class(head)
                    options = get_options(head.name[:-3])
                    if options:
                        data, options = _data_and_options(item.elements, options)
                        new_item = Expression(head, *data)
                        element = element_class(self, style, new_item, options)
                    else:
                        element = element_class(self, style, item)
                    yield element
                elif head is SymbolList:
                    for element in convert(item, style):
                        yield element
                else:
                    raise BoxExpressionError

        self.elements = list(convert(content, self.style_class(self)))

    def create_style(self, expr):
        style = self.style_class(self)

        def convert(expr):
            if expr.has_form(("List", "Directive"), None):
                for item in expr.elements:
                    convert(item)
            else:
                style.append(expr)

        convert(expr)
        return style


class GraphicsElements(_GraphicsElements):
    coords = Coords

    def __init__(self, content, evaluation, neg_y=False):
        super(GraphicsElements, self).__init__(content, evaluation)
        self.neg_y = neg_y
        self.xmin = self.ymin = self.pixel_width = None
        self.pixel_height = self.extent_width = self.extent_height = None
        self.view_width = None
        self.content = content

    def translate(self, coords):
        if self.pixel_width is not None:
            w = self.extent_width if self.extent_width > 0 else 1
            h = self.extent_height if self.extent_height > 0 else 1
            result = [
                (coords[0] - self.xmin) * self.pixel_width / w,
                (coords[1] - self.ymin) * self.pixel_height / h,
            ]
            if self.neg_y:
                result[1] = self.pixel_height - result[1]
            return tuple(result)
        else:
            return (coords[0], coords[1])

    def translate_absolute(self, d):
        if self.pixel_width is None:
            return (0, 0)
        else:
            lw = 96.0 / 72
            return (d[0] * lw, (-1 if self.neg_y else 1) * d[1] * lw)

    def translate_relative(self, x):
        if self.pixel_width is None:
            return 0
        else:
            return x * self.pixel_width

    def extent(self, completely_visible_only=False):
        if completely_visible_only:
            ext = total_extent(
                [
                    element.extent()
                    for element in self.elements
                    if element.is_completely_visible
                ]
            )
        else:
            ext = total_extent([element.extent() for element in self.elements])
        xmin, xmax, ymin, ymax = ext
        if xmin == xmax:
            if xmin is None:
                return 0, 0, 0, 0
            xmin = 0
            xmax *= 2
        if ymin == ymax:
            if ymin is None:
                return 0, 0, 0, 0
            ymin = 0
            ymax *= 2
        return xmin, xmax, ymin, ymax

    def set_size(
        self, xmin, ymin, extent_width, extent_height, pixel_width, pixel_height
    ):

        self.xmin, self.ymin = xmin, ymin
        self.extent_width, self.extent_height = extent_width, extent_height
        self.pixel_width, self.pixel_height = pixel_width, pixel_height


class Circle(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Circle.html</url>

    <dl>
      <dt>'Circle[{$cx$, $cy$}, $r$]'
      <dd>draws a circle with center '($cx$, $cy$)' and radius $r$.

      <dt>'Circle[{$cx$, $cy$}, {$rx$, $ry$}]'
      <dd>draws an ellipse.

      <dt>'Circle[{$cx$, $cy$}]'
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
    summary_text = "empty circle, ellipse, or arc graphics primitive"


class Disk(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Disk.html</url>

    <dl>
      <dt>'Disk[{$cx$, $cy$}, $r$]'
      <dd>fills a circle with center '($cx$, $cy$)' and radius $r$.

      <dt>'Disk[{$cx$, $cy$}, {$rx$, $ry$}]'
      <dd>fills an ellipse.

      <dt>'Disk[{$cx$, $cy$}]'
      <dd>chooses radius 1.

      <dt>'Disk[]'
      <dd>chooses center '(0, 0)' and radius 1.

      <dt>'Disk[{$x$, $y$}, ..., {$t1$, $t2$}]'
      <dd>is a sector from angle $t1$ to $t2$.
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
      <dt> 'EdgeForm[$g$]'
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
      <dt> 'FaceForm[$g$]'
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
      <dt>'Text[$obj$]'
      <dd>represents an object $obj$ inset in a graphic.

      <dt>'Text[$obj$, $pos$]'
      <dd>represents an object $obj$ inset in a graphic at position $pos$.

      <dt>'Text[$obj$, $pos$, $$]'
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

    summary_text = "large size style or option setting"


class Medium(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Medium.html</url>

    <dl>
      <dt>'ImageSize' -> 'Medium'
      <dd>produces a medium-sized image.
    </dl>
    """

    summary_text = "medium size style or option setting"


class Offset(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Offset.html</url>

    <dl>
      <dt>'Offset[{$dx$, $dy$}, $position$]'
      <dd>gives the position of a graphical object obtained by starting at the specified $position$ and then moving by absolute offset {$dx$,$dy$}.
    </dl>
    """

    summary_text = "offset a graphics object by a specified position"


class Rectangle(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Rectangle.html</url>

    <dl>
      <dt>'Rectangle[{$xmin$, $ymin$}]'
      <dd>represents a unit square with bottom-left corner at {$xmin$, $ymin$}.

      <dt>'Rectangle[{$xmin$, $ymin$}, {$xmax$, $ymax$}]
      <dd>is a rectangle extending from {$xmin$, $ymin$} to {$xmax$, $ymax$}.
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
      <dt>'Text["$text$", {$x$, $y$}]'
      <dd>draws $text$ centered on position '{$x$, $y$}'.
    </dl>

    >> Graphics[{Text["First", {0, 0}], Text["Second", {1, 1}]}, Axes->True, PlotRange->{{-2, 2}, {-2, 2}}]
     = -Graphics-

    #> Graphics[{Text[x, {0,0}]}]
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
      <dt>'Thickness[$t$]'
      <dd>sets the line thickness for subsequent graphics primitives to $t$ times the size of the plot area.
    </dl>

    >> Graphics[{Thickness[0.2], Line[{{0, 0}, {0, 5}}]}, Axes->True, PlotRange->{{-5, 5}, {-5, 5}}]
     = -Graphics-
    """

    summary_text = "graphics directive to specify line thicknesses"

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


element_heads = frozenset(
    symbol_set(
        Symbol("System`Arrow"),
        Symbol("System`BezierCurve"),
        Symbol("System`Circle"),
        Symbol("System`Cone"),
        Symbol("System`Cuboid"),
        Symbol("System`Cylinder"),
        Symbol("System`Disk"),
        Symbol("System`FilledCurve"),
        Symbol("System`Inset"),
        Symbol("System`Line"),
        Symbol("System`Point"),
        Symbol("System`Polygon"),
        Symbol("System`Rectangle"),
        Symbol("System`RegularPolygon"),
        Symbol("System`Sphere"),
        Symbol("System`Style"),
        Symbol("System`Text"),
        Symbol("System`Tube"),
        Symbol("System`UniformPolyhedron"),
    )
)

styles = system_symbols_dict(
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

style_options = system_symbols_dict(
    {"FontColor": _style, "ImageSizeMultipliers": (lambda *x: x[1])}
)

style_heads = frozenset(styles.keys())

style_and_form_heads = frozenset(
    style_heads.union(symbol_set(SymbolEdgeForm, SymbolFaceForm))
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

GLOBALS.update(styles)

GRAPHICS_SYMBOLS = {
    SymbolList,
    SymbolRule,
    Symbol("System`VertexColors"),
    *element_heads,
    *[Symbol(element.name + "Box") for element in element_heads],
    *style_heads,
}
