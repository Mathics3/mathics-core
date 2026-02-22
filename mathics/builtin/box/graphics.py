# -*- coding: utf-8 -*-
"""
Boxing Symbols for 2D Graphics
"""
from abc import ABC
from math import atan2, cos, degrees, pi, sin
from typing import Any, Dict, Final, List, Optional, Tuple

from mathics.builtin.box.expression import BoxExpression
from mathics.builtin.colors.color_directives import (
    ColorError,
    Opacity,
    RGBColor,
    _ColorObject,
)
from mathics.builtin.drawing.graphics_internals import GLOBALS
from mathics.builtin.graphics import (
    DEFAULT_POINT_FACTOR,
    Arrowheads,
    Graphics,
    PointSize,
    _BezierCurve,
    _Line,
    _norm,
    _to_float,
)
from mathics.core.atoms import Integer, Real
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED, A_READ_PROTECTED
from mathics.core.element import BaseElement
from mathics.core.exceptions import BoxExpressionError
from mathics.core.expression import Expression
from mathics.core.formatter import lookup_method
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolInsetBox, SymbolTraditionalForm
from mathics.format.box import format_element
from mathics.format.box.common import elements_to_expressions
from mathics.format.box.graphics import Coords, _data_and_options, coords

# No user docs here: Box primitives aren't documented.
no_doc = True

SymbolRegularPolygonBox = Symbol("RegularPolygonBox")


class GraphicsElementBox(BoxExpression, ABC):
    def init(self, graphics, item=None, style={}, opacity=1.0):
        if item is not None and not item.has_form(self.get_name(), None):
            raise BoxExpressionError
        self.graphics = graphics
        self.style = style
        self.opacity = opacity
        self.is_completely_visible = False  # True for axis elements


# GraphicsElementBox Builtin class that should not get added as a definition,
# and therefore not added to to external documentation.

DOES_NOT_ADD_BUILTIN_DEFINITION: Final[List[BoxExpression]] = [GraphicsElementBox]


class _Polyline(GraphicsElementBox):
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


# Note: has to come before ArcBox
class RoundBox(GraphicsElementBox):
    face_element: Optional[bool] = None

    def init(self, graphics, style, item):
        super().init(graphics, item, style)
        if len(item.elements) not in (1, 2):
            raise BoxExpressionError
        self.edge_color, self.face_color = style.get_style(
            _ColorObject, face_element=self.face_element
        )
        self.edge_opacity, self.face_opacity = style.get_style(
            Opacity, face_element=self.face_element
        )
        self.c = Coords(graphics, item.elements[0])
        if len(item.elements) == 1:
            rx = ry = 1
        elif len(item.elements) == 2:
            r = item.elements[1]
            if r.has_form("List", 2):
                rx = r.elements[0].round_to_float()
                ry = r.elements[1].round_to_float()
            else:
                rx = ry = r.round_to_float()
        self.r = self.c.add(rx, ry)

    def extent(self) -> list:
        """
        Compute the bounding box for RoundBox. Note that
        We handle ellipses here too.
        """
        line_width = self.style.get_line_width(face_element=self.face_element) / 2
        x, y = self.c.pos()
        rx, ry = self.r.pos()
        rx -= x
        ry = y - ry
        rx += line_width
        ry += line_width
        return [(x - rx, y - ry), (x - rx, y + ry), (x + rx, y - ry), (x + rx, y + ry)]


class ArcBox(RoundBox):
    def init(self, graphics, style, item):
        if len(item.elements) == 3:
            arc_expr = item.elements[2]
            if arc_expr.get_head_name() != "System`List":
                raise BoxExpressionError
            arc = arc_expr.elements
            pi2 = 2 * pi

            start_angle = arc[0].round_to_float()
            end_angle = arc[1].round_to_float()

            if start_angle is None or end_angle is None:
                raise BoxExpressionError
            elif end_angle >= start_angle + pi2:  # full circle?
                self.arc = None
            else:
                if end_angle <= start_angle:
                    self.arc = (end_angle, start_angle)
                else:
                    self.arc = (start_angle, end_angle)

            item = Expression(Symbol(item.get_head_name()), *item.elements[:2])
        else:
            self.arc = None
        super().init(graphics, style, item)

    def _arc_params(self):
        x, y = self.c.pos()
        rx, ry = self.r.pos()

        rx -= x
        ry -= y

        start_angle, end_angle = self.arc

        if end_angle - start_angle <= pi:
            large_arc = 0
        else:
            large_arc = 1

        sx = x + rx * cos(start_angle)
        sy = y + ry * sin(start_angle)

        ex = x + rx * cos(end_angle)
        ey = y + ry * sin(end_angle)

        return x, y, abs(rx), abs(ry), sx, sy, ex, ey, large_arc


class ArrowBox(_Polyline):
    """
    <dl>
      <dt>'ArrowBox'
      <dd>is the symbol used in boxing 'Arrow' expressions.
    </dl>
    """

    summary_text = "symbol used in boxing 'Arrow' expressions"

    def init(self, graphics, style, item=None):
        if not item:
            raise BoxExpressionError

        super().init(graphics, item, style)

        elements = item.elements
        if len(elements) == 2:
            setback = self._setback_spec(elements[1])
        elif len(elements) == 1:
            setback = (0, 0)
        else:
            raise BoxExpressionError

        curve = elements[0]

        curve_head_name = curve.get_head_name()
        if curve_head_name == "System`List":
            curve_points = curve
            self.curve = _Line()
        elif curve_head_name == "System`Line":
            if len(curve.elements) != 1:
                raise BoxExpressionError
            curve_points = curve.elements[0]
            self.curve = _Line()
        elif curve_head_name == "System`BezierCurve":
            if len(curve.elements) != 1:
                raise BoxExpressionError
            curve_points = curve.elements[0]
            self.curve = _BezierCurve()
        else:
            raise BoxExpressionError

        self.setback = setback
        self.do_init(graphics, curve_points)
        self.graphics = graphics
        self.edge_color, _ = style.get_style(_ColorObject, face_element=False)
        self.edge_opacity, _ = style.get_style(Opacity, face_element=False)
        self.heads, _ = style.get_style(Arrowheads, face_element=False)

    @staticmethod
    def _setback_spec(expr):
        if expr.get_head_name() == "System`List":
            elements = expr.elements
            if len(elements) != 2:
                raise BoxExpressionError
            return tuple(max(_to_float(w), 0.0) for w in elements)
        else:
            s = max(_to_float(expr), 0.0)
            return s, s

    @staticmethod
    def _default_arrow(polygon):
        # the default arrow drawn by draw() below looks looks like this:
        #
        #       H
        #      .:.
        #     . : .
        #    .  :  .
        #   .  .B.  .
        #  . .  :  . .
        # S.    E    .S
        #       :
        #       :
        #       :
        #
        # the head H is where the arrow's point is. at base B, the arrow spreads out at right angles from the line
        # it attaches to. the arrow size 's' given in the Arrowheads specification always specifies the length H-B.
        #
        # the spread out points S are defined via two constants: arrow_edge (which defines the factor to get from
        # H-B to H-E) and arrow_spread (which defines the factor to get from H-B to E-S).

        arrow_spread = 0.3
        arrow_edge = 1.1

        def draw(px, py, vx, vy, t1, s):
            hx = px + t1 * vx  # compute H
            hy = py + t1 * vy

            t0 = t1 - s
            bx = px + t0 * vx  # compute B
            by = py + t0 * vy

            te = t1 - arrow_edge * s
            ex = px + te * vx  # compute E
            ey = py + te * vy

            ts = arrow_spread * s
            sx = -vy * ts
            sy = vx * ts

            head_points = ((hx, hy), (ex + sx, ey + sy), (bx, by), (ex - sx, ey - sy))

            for shape in polygon(head_points):
                yield shape

        return draw

    def _draw(self, polyline, default_arrow, custom_arrow, extent):
        if self.heads:
            heads = list(self.heads.heads(extent, default_arrow, custom_arrow))
            heads = sorted(heads, key=lambda spec: spec[1])  # sort by pos
        else:
            heads = ((extent * Arrowheads.default_size, 1, default_arrow),)

        def setback(p, q, d):
            dx, dy, length = _norm(p, q)
            if d >= length:
                return None, length
            else:
                s = d / length
                return (s * dx, s * dy), d

        def shrink_one_end(line, s):
            while s > 0.0:
                if len(line) < 2:
                    return []
                xy, length = setback(line[0].p, line[1].p, s)
                if xy is not None:
                    line[0] = line[0].add(*xy)
                else:
                    line = line[1:]
                s -= length
            return line

        def shrink(line, s1, s2):
            return list(
                reversed(
                    shrink_one_end(list(reversed(shrink_one_end(line[:], s1))), s2)
                )
            )

        for line in self.lines:
            if len(line) < 2:
                continue

            # note that shrinking needs to happen in the Graphics[] coordinate space, whereas the
            # subsequent position calculation needs to happen in pixel space.

            transformed_points = [xy.pos() for xy in shrink(line, *self.setback)]

            for s in polyline(transformed_points):
                yield s

            for s in self.curve.arrows(transformed_points, heads):
                yield s

    def _custom_arrow(self, format, format_transform):
        from mathics.format.box.graphics import _extract_graphics

        def make(graphics):
            xmin, xmax, ymin, ymax, ox, oy, ex, ey, code = _extract_graphics(
                graphics, format, self.graphics.evaluation
            )
            boxw = xmax - xmin
            boxh = ymax - ymin

            def draw(px, py, vx, vy, t1, s):
                t0 = t1
                cx = px + t0 * vx
                cy = py + t0 * vy

                transform = format_transform()
                transform.translate(cx, cy)
                transform.scale(-s / boxw * ex, -s / boxh * ey)
                transform.rotate(90 + degrees(atan2(vy, vx)))
                transform.translate(-ox, -oy)
                yield transform.apply(code)

            return draw

        return make

    def extent(self):
        width = self.style.get_line_width(face_element=False)

        def polyline(points):
            for p in points:
                x, y = p
                yield x - width, y - width
                yield x - width, y + width
                yield x + width, y - width
                yield x + width, y + width

        def polygon(points):
            for p in points:
                yield p

        def default_arrow(px, py, vx, vy, t1, s):
            yield px, py

        return list(self._draw(polyline, default_arrow, None, 0))


class BezierCurveBox(_Polyline):
    """
    <dl>
      <dt>'BezierCurveBox'
      <dd>is the symbol used in boxing 'BezierCurve' expressions.
    </dl>
    """

    summary_text = "symbol used in boxing 'BezierCurve' expressions"

    def init(self, graphics, style, item, options):
        super(BezierCurveBox, self).init(graphics, item, style)
        if len(item.elements) != 1 or item.elements[0].get_head_name() != "System`List":
            raise BoxExpressionError
        self.edge_color, _ = style.get_style(_ColorObject, face_element=False)
        self.edge_opacity, _ = style.get_style(Opacity, face_element=False)
        points = item.elements[0]
        self.do_init(graphics, points)
        spline_degree = options.get("System`SplineDegree")
        if not isinstance(spline_degree, Integer):
            raise BoxExpressionError
        self.spline_degree = spline_degree.get_int_value()


class CircleBox(ArcBox):
    """
    <dl>
      <dt>'CircleBox'
      <dd>is the symbol used in boxing 'Circle' expressions.
    </dl>
    """

    face_element = False
    summary_text = "is the symbol used in boxing 'Circle' expressions"


class DiskBox(ArcBox):
    """
    <dl>
      <dt>'DiskBox'
      <dd>is the symbol used in boxing 'Disk' expressions.
    </dl>
    """

    face_element = True
    summary_text = "symbol used in boxing 'Disk' expressions"


class GraphicsBox(BoxExpression):
    """
    <dl>
      <dt>'GraphicsBox'
      <dd>is the symbol used in boxing 'Graphics'.
    </dl>
    """

    attributes = A_HOLD_ALL | A_PROTECTED | A_READ_PROTECTED
    options = Graphics.options
    summary_text = "symbol used in boxing 'Graphics'"

    def init(self, *items, **kwargs):
        self._elements: Optional[Tuple[BaseElement], ...] = None
        self.content = items[0]
        self.box_options: Dict[str, Any] = kwargs
        self.background_color = None
        self.tooltip_text: Optional[str] = None
        self.evaluation = kwargs.pop("_evaluation", None)
        self.boxwidth: int = -1
        self.boxheight: int = -1
        self.boxes: list = []

    @property
    def elements(self):
        if self._elements is None:
            self._elements = elements_to_expressions(
                self,
                (self.content,),
                self.box_options,
            )
        return self._elements

    @elements.setter
    def elements(self, value):
        self._elements = value
        return self._elements

    def to_svg(self, elements=None, **options) -> str:
        """This is the top-level function that converts a Mathics Expression
        in to something suitable for SVG rendering.
        """
        assert elements is None

        elements = self.content

        format_fn = lookup_method(self, "svg")
        svg_body = format_fn(self, **options)
        return svg_body


class FilledCurveBox(GraphicsElementBox):
    """
    <dl>
      <dt>'FilledCurveBox'
      <dd>is the symbol used in boxing 'FilledCurve' expressions.
    </dl>
    """

    def init(self, graphics, style, item=None):
        super(FilledCurveBox, self).init(graphics, item, style)
        self.edge_color, self.face_color = style.get_style(
            _ColorObject, face_element=True
        )
        self.edge_opacity, self.face_opacity = style.get_style(
            Opacity, face_element=True
        )
        if (
            item is not None
            and item.elements
            and item.elements[0].has_form("List", None)
        ):
            if len(item.elements) != 1:
                raise BoxExpressionError
            elements = item.elements[0].elements

            def parse_component(segments):
                for segment in segments:
                    head = segment.get_head_name()

                    if head == "System`Line":
                        k = 1
                        parts = segment.elements
                    elif head == "System`BezierCurve":
                        parts, options = _data_and_options(segment.elements, {})
                        spline_degree = options.get("SplineDegree", Integer(3))
                        if not isinstance(spline_degree, Integer):
                            raise BoxExpressionError
                        k = spline_degree.get_int_value()
                    elif head == "System`BSplineCurve":
                        raise NotImplementedError  # FIXME convert bspline to bezier here
                        # parts = segment.elements
                    else:
                        raise BoxExpressionError

                    coords = []

                    for part in parts:
                        if part.get_head_name() != "System`List":
                            raise BoxExpressionError
                        coords.extend(
                            [graphics.coords(graphics, xy) for xy in part.elements]
                        )

                    yield k, coords

            if all(x.get_head_name() == "System`List" for x in elements):
                self.components = [list(parse_component(x)) for x in elements]
            else:
                self.components = [list(parse_component(elements))]
        else:
            raise BoxExpressionError

    def extent(self):
        lw = self.style.get_line_width(face_element=False)
        result = []
        for component in self.components:
            for _, points in component:
                for p in points:
                    x, y = p.pos()
                    result.extend(
                        [
                            (x - lw, y - lw),
                            (x - lw, y + lw),
                            (x + lw, y - lw),
                            (x + lw, y + lw),
                        ]
                    )
        return result


class InsetBox(GraphicsElementBox):
    # We have no documentation for this (yet).
    no_doc = True

    def init(
        self,
        graphics,
        style,
        item=None,
        content=None,
        pos=None,
        opos=(0, 0),
        opacity=None,
        alignment=None,
    ):
        super(InsetBox, self).init(graphics, item, style)

        self.color = self.style.get_option("System`FontColor")
        if self.color is None:
            self.color, _ = style.get_style(_ColorObject, face_element=False)

        if opacity is None:
            opacity, _ = style.get_style(Opacity, face_element=False)
        else:
            opacity = Opacity(opacity)

        if opacity is None:
            opacity = Opacity(1.0)

        self.opacity = opacity
        self.alignment = alignment

        if item is not None:
            if len(item.elements) not in (1, 2, 3):
                raise BoxExpressionError
            content = item.elements[0]
            self.content = format_element(
                content, graphics.evaluation, SymbolTraditionalForm
            )
            if len(item.elements) > 1:
                self.pos = Coords(graphics, item.elements[1])
            else:
                self.pos = Coords(graphics, pos=(0, 0))
            if len(item.elements) > 2:
                self.opos = coords(item.elements[2])
            else:
                self.opos = (0, 0)
        else:
            self.content = content
            self.pos = pos
            self.opos = opos

        # if isinstance(self.content, String):
        #    self.content = self.content.atom_to_boxes(
        #        SymbolStandardForm, evaluation=self.graphics.evaluation
        #    )
        self.content_text = self.content.to_text(evaluation=self.graphics.evaluation)

    def extent(self):
        p = self.pos.pos()
        h = 25
        w = len(self.content_text) * 7  # rough approximation by numbers of characters
        opos = self.opos
        x = p[0] - w / 2.0 - opos[0] * w / 2.0
        y = p[1] - h / 2.0 + opos[1] * h / 2.0
        return [(x, y), (x + w, y + h)]


class LineBox(_Polyline):
    """
    <dl>
      <dt>'LineBox'
      <dd>is the symbol used in boxing 'Line' expressions.
    </dl>
    """

    summary_text = "symbol used in boxing 'Line' expressions"

    def init(self, graphics, style, item=None, lines=None):
        super(LineBox, self).init(graphics, item, style)
        self.edge_color, _ = style.get_style(_ColorObject, face_element=False)
        self.edge_opacity, _ = style.get_style(Opacity, face_element=False)
        if item is not None:
            if len(item.elements) != 1:
                raise BoxExpressionError
            points = item.elements[0]
            self.do_init(graphics, points)
        elif lines is not None:
            self.lines = lines
        else:
            raise BoxExpressionError


class PointBox(_Polyline):
    """
    <dl>
      <dt>'PointBox']
      <dd>is the symbol used in boxing 'Point' expressions.
    </dl>

    Options include the edge color and the point radius for each of the points.
    """

    summary_text = "symbol used in boxing 'Point' expressions"

    def init(self, graphics, style, item=None):
        super(PointBox, self).init(graphics, item, style)
        self.edge_color, self.face_color = style.get_style(
            _ColorObject, face_element=True
        )
        self.edge_opacity, self.face_opacity = style.get_style(
            Opacity, face_element=True
        )
        # Handle PointSize in a hacky way for now.
        point_size, _ = style.get_style(PointSize, face_element=False)
        if point_size is None:
            point_size = PointSize(self.graphics, value=DEFAULT_POINT_FACTOR)

        # FIXME: we don't have graphics options. Until we do, we'll
        # just assume an image width of 400
        image_width = 400
        self.point_radius = image_width * point_size.value

        if item is not None:
            if len(item.elements) != 1:
                print("item:", item)
                raise BoxExpressionError
            points = item.elements[0]
            if points.has_form("List", None) and len(points.elements) != 0:
                if all(
                    not element.has_form("List", None) for element in points.elements
                ):
                    points = ListExpression(points)
            self.do_init(graphics, points)
        else:
            raise BoxExpressionError

    def extent(self):
        """Returns a list of bounding-box coordinates each point in the PointBox"""
        rad = self.point_radius
        result = []
        for line in self.lines:
            for c in line:
                x, y = c.pos()
                result.extend(
                    [
                        (x - rad, y - rad),
                        (x - rad, y + rad),
                        (x + rad, y - rad),
                        (x + rad, y + rad),
                    ]
                )
        return result


class PolygonBox(_Polyline):
    # We have no documentation for this (yet).
    no_doc = True

    def init(self, graphics, style, item=None):
        super(PolygonBox, self).init(graphics, item, style)
        self.edge_color, self.face_color = style.get_style(
            _ColorObject, face_element=True
        )
        self.edge_opacity, self.face_opacity = style.get_style(
            Opacity, face_element=True
        )
        if item is not None:
            if len(item.elements) not in (1, 2):
                raise BoxExpressionError
            points = item.elements[0]
            self.do_init(graphics, points)
            self.vertex_colors = None
            for element in item.elements[1:]:
                if not element.has_form("Rule", 2):
                    raise BoxExpressionError
                name = element.elements[0].get_name()
                self.process_option(name, element.elements[1])
        else:
            raise BoxExpressionError

    def process_option(self, name, value):
        if name == "System`VertexColors":
            if not value.has_form("List", None):
                raise BoxExpressionError
            black = RGBColor(components=[0, 0, 0, 1])
            self.vertex_colors = [[black] * len(line) for line in self.lines]
            colors = value.elements
            if not self.multi_parts:
                colors = [ListExpression(*colors)]
            for line_index, line in enumerate(self.lines):
                if line_index >= len(colors):
                    break
                line_colors = colors[line_index]
                if not line_colors.has_form("List", None):
                    continue
                for index, color in enumerate(line_colors.elements):
                    if index >= len(self.vertex_colors[line_index]):
                        break
                    try:
                        self.vertex_colors[line_index][index] = _ColorObject.create(
                            color
                        )
                    except ColorError:
                        continue
        else:
            raise BoxExpressionError


class RectangleBox(GraphicsElementBox):
    # We have no documentation for this (yet).
    no_doc = True

    def init(self, graphics, style, item):
        super(RectangleBox, self).init(graphics, item, style)
        if len(item.elements) not in (1, 2):
            raise BoxExpressionError
        self.edge_color, self.face_color = style.get_style(
            _ColorObject, face_element=True
        )
        self.edge_opacity, self.face_opacity = style.get_style(
            Opacity, face_element=True
        )
        self.p1 = Coords(graphics, item.elements[0])
        if len(item.elements) == 1:
            self.p2 = self.p1.add(1, 1)
        elif len(item.elements) == 2:
            self.p2 = Coords(graphics, item.elements[1])

    def extent(self):
        hlw = self.style.get_line_width(face_element=True) / 2
        result = []
        for p in [self.p1, self.p2]:
            x, y = p.pos()
            result.extend(
                [
                    (x - hlw, y - hlw),
                    (x - hlw, y + hlw),
                    (x + hlw, y - hlw),
                    (x + hlw, y + hlw),
                ]
            )
        return result


class RegularPolygonBox(PolygonBox):
    # We have no documentation for this (yet).
    no_doc = True

    def init(self, graphics, style, item):
        if len(item.elements) in (1, 2, 3) and isinstance(item.elements[-1], Integer):
            r = 1.0
            phi0 = None

            if len(item.elements) >= 2:
                rspec = item.elements[-2]
                if rspec.get_head_name() == "System`List":
                    if len(rspec.elements) != 2:
                        raise BoxExpressionError
                    r = rspec.elements[0].round_to_float()
                    phi0 = rspec.elements[1].round_to_float()
                else:
                    r = rspec.round_to_float()

            x = 0.0
            y = 0.0
            if len(item.elements) == 3:
                pos = item.elements[0]
                if not pos.has_form("List", 2):
                    raise BoxExpressionError
                x = pos.elements[0].round_to_float()
                y = pos.elements[1].round_to_float()

            n = item.elements[-1].get_int_value()

            if any(t is None for t in (x, y, r)) or n < 0:
                raise BoxExpressionError

            if phi0 is None:
                phi0 = -pi / 2.0
                if n % 1 == 0 and n > 0:
                    phi0 += pi / n

            pi2 = pi * 2.0

            def vertices():
                for i in range(n):
                    phi = phi0 + pi2 * i / float(n)
                    yield ListExpression(Real(x + r * cos(phi)), Real(y + r * sin(phi)))

            new_item = Expression(
                SymbolRegularPolygonBox, ListExpression(*list(vertices()))
            )
        else:
            raise BoxExpressionError

        super(RegularPolygonBox, self).init(graphics, style, new_item)


# FIXME: GLOBALS is a horrible name.
GLOBALS.update(
    {
        Symbol("RectangleBox"): RectangleBox,
        Symbol("DiskBox"): DiskBox,
        Symbol("LineBox"): LineBox,
        Symbol("BezierCurveBox"): BezierCurveBox,
        Symbol("FilledCurveBox"): FilledCurveBox,
        Symbol("ArrowBox"): ArrowBox,
        Symbol("CircleBox"): CircleBox,
        Symbol("PolygonBox"): PolygonBox,
        SymbolRegularPolygonBox: RegularPolygonBox,
        Symbol("PointBox"): PointBox,
        SymbolInsetBox: InsetBox,
    }
)
