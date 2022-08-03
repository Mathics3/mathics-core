# -*- coding: utf-8 -*-
"""
Boxing Routines for 2D Graphics
"""

import base64
from math import atan2, ceil, cos, degrees, floor, log10, pi, sin

from mathics.builtin.base import (
    BoxConstruct,
    BoxConstructError,
)

from mathics.builtin.colors.color_directives import (
    _ColorObject,
    ColorError,
    Opacity,
    RGBColor,
)
from mathics.builtin.drawing.graphics_internals import _GraphicsElementBox, GLOBALS

from mathics.builtin.graphics import (
    Arrowheads,
    Coords,
    DEFAULT_POINT_FACTOR,
    Graphics,
    GraphicsElements,
    PointSize,
    _BezierCurve,
    _Line,
    _Polyline,
    _data_and_options,
    _extract_graphics,
    _norm,
    _to_float,
    coords,
)


from mathics.core.atoms import (
    Integer,
    Real,
    String,
)

from mathics.core.attributes import hold_all, protected, read_protected
from mathics.core.expression import Expression
from mathics.core.formatter import lookup_method
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.core.systemsymbols import SymbolAutomatic, SymbolTraditionalForm

from mathics.core.formatter import format_element

from mathics.format.asy_fns import asy_color, asy_number

SymbolRegularPolygonBox = Symbol("RegularPolygonBox")
SymbolStandardForm = Symbol("StandardForm")

# Note: has to come before _ArcBox
class _RoundBox(_GraphicsElementBox):
    face_element = None

    def init(self, graphics, style, item):
        super(_RoundBox, self).init(graphics, item, style)
        if len(item.elements) not in (1, 2):
            raise BoxConstructError
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
        Compute the bounding box for _RoundBox. Note that
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


class _ArcBox(_RoundBox):
    def init(self, graphics, style, item):
        if len(item.elements) == 3:
            arc_expr = item.elements[2]
            if arc_expr.get_head_name() != "System`List":
                raise BoxConstructError
            arc = arc_expr.elements
            pi2 = 2 * pi

            start_angle = arc[0].round_to_float()
            end_angle = arc[1].round_to_float()

            if start_angle is None or end_angle is None:
                raise BoxConstructError
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
        super(_ArcBox, self).init(graphics, style, item)

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
    <dt>'ArrowBox[...]'
    <dd>is a box structure for 'Arrow' elements.
    </dl>
    """

    def init(self, graphics, style, item=None):
        if not item:
            raise BoxConstructError

        super(ArrowBox, self).init(graphics, item, style)

        elements = item.elements
        if len(elements) == 2:
            setback = self._setback_spec(elements[1])
        elif len(elements) == 1:
            setback = (0, 0)
        else:
            raise BoxConstructError

        curve = elements[0]

        curve_head_name = curve.get_head_name()
        if curve_head_name == "System`List":
            curve_points = curve
            self.curve = _Line()
        elif curve_head_name == "System`Line":
            if len(curve.elements) != 1:
                raise BoxConstructError
            curve_points = curve.elements[0]
            self.curve = _Line()
        elif curve_head_name == "System`BezierCurve":
            if len(curve.elements) != 1:
                raise BoxConstructError
            curve_points = curve.elements[0]
            self.curve = _BezierCurve()
        else:
            raise BoxConstructError

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
                raise BoxConstructError
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
    <dt>'BezierCurveBox[...]'
    <dd>is a box structure for a 'BezierCurve' element.
    </dl>
    """

    def init(self, graphics, style, item, options):
        super(BezierCurveBox, self).init(graphics, item, style)
        if len(item.elements) != 1 or item.elements[0].get_head_name() != "System`List":
            raise BoxConstructError
        self.edge_color, _ = style.get_style(_ColorObject, face_element=False)
        self.edge_opacity, _ = style.get_style(Opacity, face_element=False)
        points = item.elements[0]
        self.do_init(graphics, points)
        spline_degree = options.get("System`SplineDegree")
        if not isinstance(spline_degree, Integer):
            raise BoxConstructError
        self.spline_degree = spline_degree.get_int_value()


class CircleBox(_ArcBox):
    """
    <dl>
    <dt>'CircleBox[...]'
    <dd>box structure for a 'Circle' element.
    </dl>
    """

    face_element = False
    summary_text = "internal box representation for 'Circle' elements"


class DiskBox(_ArcBox):
    """
    <dl>
    <dt>'DiskBox[...]'
    <dd>box structure for a 'Disk' element.
    </dl>
    """

    face_element = True
    summary_text = "internal box representation for 'Disk' elements"


class GraphicsBox(BoxConstruct):
    """
    <dl>
    <dt>'GraphicsBox[...]'
    <dd>box structure holding a 'Graphics' object.
    </dl>

    Boxing method which get called when Boxing (adding formatting and bounding-box information)
    Graphics.
    """

    attributes = hold_all | protected | read_protected
    options = Graphics.options

    def __new__(cls, *elements, **kwargs):
        instance = super().__new__(cls, *elements, **kwargs)
        instance.evaluation = kwargs.get("evaluation", None)
        instance.elements = elements
        return instance

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, value):
        self._elements = value
        return self._elements

    def _get_image_size(self, options, graphics_options, max_width):
        inside_row = options.pop("inside_row", False)
        inside_list = options.pop("inside_list", False)
        image_size_multipliers = options.pop("image_size_multipliers", None)

        aspect_ratio = graphics_options["System`AspectRatio"]

        if image_size_multipliers is None:
            image_size_multipliers = (0.5, 0.25)

        if aspect_ratio is SymbolAutomatic:
            aspect = None
        else:
            aspect = aspect_ratio.round_to_float()

        image_size = graphics_options["System`ImageSize"]
        if isinstance(image_size, Integer):
            base_width = image_size.get_int_value()
            base_height = None  # will be computed later in calc_dimensions
        elif image_size.has_form("System`List", 2):
            base_width, base_height = (
                [x.round_to_float() for x in image_size.elements] + [0, 0]
            )[:2]
            if base_width is None or base_height is None:
                raise BoxConstructError
            aspect = base_height / base_width
        else:
            image_size = image_size.get_name()
            base_width, base_height = {
                "System`Automatic": (400, 350),
                "System`Tiny": (100, 100),
                "System`Small": (200, 200),
                "System`Medium": (400, 350),
                "System`Large": (600, 500),
            }.get(image_size, (None, None))
        if base_width is None:
            raise BoxConstructError
        if max_width is not None and base_width > max_width:
            base_width = max_width

        if inside_row:
            multi = image_size_multipliers[1]
        elif inside_list:
            multi = image_size_multipliers[0]
        else:
            multi = 1

        return base_width, base_height, multi, aspect

    def _prepare_elements(self, elements, options, neg_y=False, max_width=None):
        if not elements:
            raise BoxConstructError
        self.graphics_options = self.get_option_values(elements[1:], **options)
        background = self.graphics_options["System`Background"]
        if (
            isinstance(background, Symbol)
            and background.get_name() == "System`Automatic"
        ):
            self.background_color = None
        else:
            self.background_color = _ColorObject.create(background)

        base_width, base_height, size_multiplier, size_aspect = self._get_image_size(
            options, self.graphics_options, max_width
        )

        plot_range = self.graphics_options["System`PlotRange"].to_python()
        if plot_range == "System`Automatic":
            plot_range = ["System`Automatic", "System`Automatic"]

        if not isinstance(plot_range, list) or len(plot_range) != 2:
            raise BoxConstructError

        evaluation = options.get("evaluation", None)
        if evaluation is None:
            evaluation = self.evaluation
        elements = GraphicsElements(elements[0], evaluation, neg_y)
        axes = []  # to be filled further down

        def calc_dimensions(final_pass=True):
            """
            calc_dimensions gets called twice: In the first run
            (final_pass = False, called inside _prepare_elements), the extent
            of all user-defined graphics is determined.
            Axes are created accordingly.
            In the second run (final_pass = True, called from outside),
            the dimensions of these axes are taken into account as well.
            This is also important to size absolutely sized objects correctly
            (e.g. values using AbsoluteThickness).
            """

            # always need to compute extent if size aspect is automatic
            if "System`Automatic" in plot_range or size_aspect is None:
                xmin, xmax, ymin, ymax = elements.extent()
            else:
                xmin = xmax = ymin = ymax = None

            if (
                final_pass
                and any(x for x in axes)
                and plot_range != ["System`Automatic", "System`Automatic"]
            ):
                # Take into account the dimensions of axes and axes labels
                # (they should be displayed completely even when a specific
                # PlotRange is given).
                exmin, exmax, eymin, eymax = elements.extent(
                    completely_visible_only=True
                )
            else:
                exmin = exmax = eymin = eymax = None

            def get_range(min, max):
                if max < min:
                    min, max = max, min
                elif min == max:
                    if min < 0:
                        min, max = 2 * min, 0
                    elif min > 0:
                        min, max = 0, 2 * min
                    else:
                        min, max = -1, 1
                return min, max

            try:
                if plot_range[0] == "System`Automatic":
                    if xmin is None and xmax is None:
                        xmin = 0
                        xmax = 1
                    elif xmin == xmax:
                        xmin -= 1
                        xmax += 1
                elif isinstance(plot_range[0], list) and len(plot_range[0]) == 2:
                    xmin, xmax = list(map(float, plot_range[0]))
                    xmin, xmax = get_range(xmin, xmax)
                    xmin = elements.translate((xmin, 0))[0]
                    xmax = elements.translate((xmax, 0))[0]
                    if exmin is not None and exmin < xmin:
                        xmin = exmin
                    if exmax is not None and exmax > xmax:
                        xmax = exmax
                else:
                    raise BoxConstructError

                if plot_range[1] == "System`Automatic":
                    if ymin is None and ymax is None:
                        ymin = 0
                        ymax = 1
                    elif ymin == ymax:
                        ymin -= 1
                        ymax += 1
                elif isinstance(plot_range[1], list) and len(plot_range[1]) == 2:
                    ymin, ymax = list(map(float, plot_range[1]))
                    ymin, ymax = get_range(ymin, ymax)
                    ymin = elements.translate((0, ymin))[1]
                    ymax = elements.translate((0, ymax))[1]
                    if ymin > ymax:
                        ymin, ymax = ymax, ymin
                    if eymin is not None and eymin < ymin:
                        ymin = eymin
                    if eymax is not None and eymax > ymax:
                        ymax = eymax
                else:
                    raise BoxConstructError
            except (ValueError, TypeError):
                raise BoxConstructError

            w = 0 if (xmin is None or xmax is None) else xmax - xmin
            h = 0 if (ymin is None or ymax is None) else ymax - ymin

            if size_aspect is None:
                aspect = h / w
            else:
                aspect = size_aspect

            height = base_height
            if height is None:
                height = base_width * aspect
            width = height / aspect
            if width > base_width:
                width = base_width
                height = width * aspect
            height = height

            width *= size_multiplier
            height *= size_multiplier

            return xmin, xmax, ymin, ymax, w, h, width, height

        xmin, xmax, ymin, ymax, w, h, width, height = calc_dimensions(final_pass=False)

        elements.set_size(xmin, ymin, w, h, width, height)

        xmin -= w * 0.02
        xmax += w * 0.02
        ymin -= h * 0.02
        ymax += h * 0.02

        axes.extend(
            self.create_axes(elements, self.graphics_options, xmin, xmax, ymin, ymax)
        )

        return elements, calc_dimensions

    # FIXME: this doesn't always properly align with overlaid SVG plots
    def axis_ticks(self, xmin, xmax):
        def round_to_zero(value):
            if value == 0:
                return 0
            elif value < 0:
                return ceil(value)
            else:
                return floor(value)

        def round_step(value):
            if not value:
                return 1, 1
            sub_steps = 5
            try:
                shift = 10.0 ** floor(log10(value))
            except ValueError:
                return 1, 1
            value = value / shift
            if value < 1.5:
                value = 1
            elif value < 3:
                value = 2
                sub_steps = 4
            elif value < 8:
                value = 5
            else:
                value = 10
            return value * shift, sub_steps

        step_x, sub_x = round_step((xmax - xmin) / 5.0)
        step_x_small = step_x / sub_x
        steps_x = int(floor((xmax - xmin) / step_x))
        steps_x_small = int(floor((xmax - xmin) / step_x_small))

        start_k_x = int(ceil(xmin / step_x))
        start_k_x_small = int(ceil(xmin / step_x_small))

        if xmin <= 0 <= xmax:
            origin_k_x = 0
        else:
            origin_k_x = start_k_x
        origin_x = origin_k_x * step_x

        ticks = []
        ticks_small = []
        for k in range(start_k_x, start_k_x + steps_x + 1):
            if k != origin_k_x:
                x = k * step_x
                if x > xmax:
                    break
                ticks.append(x)
        for k in range(start_k_x_small, start_k_x_small + steps_x_small + 1):
            if k % sub_x != 0:
                x = k * step_x_small
                if x > xmax:
                    break
                ticks_small.append(x)

        return ticks, ticks_small, origin_x

    def boxes_to_mathml(self, elements=None, **options) -> str:

        # FIXME: SVG is the only thing we can convert MathML into.
        # Handle other graphics formats.
        svg_body = self.boxes_to_svg(elements, **options)

        # mglyph, which is what we have been using, is bad because MathML standard changed.
        # metext does not work because the way in which we produce the svg images is also based on this outdated mglyph behaviour.
        # template = '<mtext width="%dpx" height="%dpx"><img width="%dpx" height="%dpx" src="data:image/svg+xml;base64,%s"/></mtext>'
        template = (
            '<mglyph width="%dpx" height="%dpx" src="data:image/svg+xml;base64,%s"/>'
            # '<mglyph  src="data:image/svg+xml;base64,%s"/>'
        )
        # print(svg_body)
        mathml = template % (
            int(self.width),
            int(self.height),
            base64.b64encode(svg_body.encode("utf8")).decode("utf8"),
        )
        # print("boxes_to_mathml", mathml)
        return mathml

    def boxes_to_svg(self, elements=None, **options) -> str:
        """This is the top-level function that converts a Mathics Expression
        in to something suitable for SVG rendering.
        """
        if not elements:
            elements = self._elements

        elements, calc_dimensions = self._prepare_elements(
            elements, options, neg_y=True
        )
        xmin, xmax, ymin, ymax, w, h, self.width, self.height = calc_dimensions()
        data = (elements, xmin, xmax, ymin, ymax, w, h, self.width, self.height)
        elements.view_width = w

        format_fn = lookup_method(self, "svg")
        svg_body = format_fn(self, elements, data=data, **options)
        return svg_body

    def boxes_to_tex(self, elements=None, **options) -> str:
        """This is the top-level function that converts a Mathics Expression
        in to something suitable for LaTeX.  (Yes, the name "tex" is
        perhaps misleading of vague.)

        However right now the only LaTeX support for graphics is via Asymptote and
        that seems to be the package of choice in general for LaTeX.
        """

        if not elements:
            elements = self._elements
            fields = self._prepare_elements(elements, options, max_width=450)
            if len(fields) == 2:
                elements, calc_dimensions = fields
            else:
                elements, calc_dimensions = fields[0], fields[-2]

        fields = calc_dimensions()
        if len(fields) == 8:
            xmin, xmax, ymin, ymax, w, h, width, height = fields
            elements.view_width = w

        else:
            assert len(fields) == 9
            xmin, xmax, ymin, ymax, _, _, _, width, height = fields
            elements.view_width = width

        asy_completely_visible = "\n".join(
            lookup_method(element, "asy")(element)
            for element in elements.elements
            if element.is_completely_visible
        )

        asy_regular = "\n".join(
            lookup_method(element, "asy")(element)
            for element in elements.elements
            if not element.is_completely_visible
        )

        asy_box = "box((%s,%s), (%s,%s))" % (
            asy_number(xmin),
            asy_number(ymin),
            asy_number(xmax),
            asy_number(ymax),
        )

        if self.background_color is not None:
            color, opacity = asy_color(self.background_color)
            asy_background = "filldraw(%s, %s);" % (asy_box, color)
        else:
            asy_background = ""

        tex = r"""
\begin{asy}
usepackage("amsmath");
size(%scm, %scm);
%s
%s
clip(%s);
%s
\end{asy}
""" % (
            asy_number(width / 60),
            asy_number(height / 60),
            asy_background,
            asy_regular,
            asy_box,
            asy_completely_visible,
        )

        return tex

    def boxes_to_text(self, elements=None, **options) -> str:
        if not elements:
            elements = self._elements

        self._prepare_elements(elements, options)  # to test for Box errors
        return "-Graphics-"

    def create_axes(self, elements, graphics_options, xmin, xmax, ymin, ymax):
        axes = graphics_options.get("System`Axes")
        if axes is SymbolTrue:
            axes = (True, True)
        elif axes.has_form("List", 2):
            axes = (axes.elements[0] is SymbolTrue, axes.elements[1] is SymbolTrue)
        else:
            axes = (False, False)
        ticks_style = graphics_options.get("System`TicksStyle")
        axes_style = graphics_options.get("System`AxesStyle")
        label_style = graphics_options.get("System`LabelStyle")
        if ticks_style.has_form("List", 2):
            ticks_style = ticks_style.elements
        else:
            ticks_style = [ticks_style] * 2
        if axes_style.has_form("List", 2):
            axes_style = axes_style.elements
        else:
            axes_style = [axes_style] * 2

        ticks_style = [elements.create_style(s) for s in ticks_style]
        axes_style = [elements.create_style(s) for s in axes_style]
        label_style = elements.create_style(label_style)
        ticks_style[0].extend(axes_style[0])
        ticks_style[1].extend(axes_style[1])

        def add_element(element):
            element.is_completely_visible = True
            elements.elements.append(element)

        ticks_x, ticks_x_small, origin_x = self.axis_ticks(xmin, xmax)
        ticks_y, ticks_y_small, origin_y = self.axis_ticks(ymin, ymax)

        axes_extra = 6
        tick_small_size = 3
        tick_large_size = 5
        tick_label_d = 2

        ticks_x_int = all(floor(x) == x for x in ticks_x)
        ticks_y_int = all(floor(x) == x for x in ticks_y)

        for (
            index,
            (min, max, p_self0, p_other0, p_origin, ticks, ticks_small, ticks_int),
        ) in enumerate(
            [
                (
                    xmin,
                    xmax,
                    lambda y: (0, y),
                    lambda x: (x, 0),
                    lambda x: (x, origin_y),
                    ticks_x,
                    ticks_x_small,
                    ticks_x_int,
                ),
                (
                    ymin,
                    ymax,
                    lambda x: (x, 0),
                    lambda y: (0, y),
                    lambda y: (origin_x, y),
                    ticks_y,
                    ticks_y_small,
                    ticks_y_int,
                ),
            ]
        ):
            if axes[index]:
                add_element(
                    LineBox(
                        elements,
                        axes_style[index],
                        lines=[
                            [
                                Coords(
                                    elements, pos=p_origin(min), d=p_other0(-axes_extra)
                                ),
                                Coords(
                                    elements, pos=p_origin(max), d=p_other0(axes_extra)
                                ),
                            ]
                        ],
                    )
                )
                ticks_lines = []
                tick_label_style = ticks_style[index].clone()
                tick_label_style.extend(label_style)
                for x in ticks:
                    ticks_lines.append(
                        [
                            Coords(elements, pos=p_origin(x)),
                            Coords(
                                elements, pos=p_origin(x), d=p_self0(tick_large_size)
                            ),
                        ]
                    )
                    if ticks_int:
                        content = String(str(int(x)))
                    elif x == floor(x):
                        content = String("%.1f" % x)  # e.g. 1.0 (instead of 1.)
                    else:
                        content = String("%g" % x)  # fix e.g. 0.6000000000000001
                    add_element(
                        InsetBox(
                            elements,
                            tick_label_style,
                            content=content,
                            pos=Coords(
                                elements, pos=p_origin(x), d=p_self0(-tick_label_d)
                            ),
                            opos=p_self0(1),
                            opacity=1.0,
                        )
                    )
                for x in ticks_small:
                    pos = p_origin(x)
                    ticks_lines.append(
                        [
                            Coords(elements, pos=pos),
                            Coords(elements, pos=pos, d=p_self0(tick_small_size)),
                        ]
                    )
                add_element(LineBox(elements, axes_style[0], lines=ticks_lines))
        return axes

        """if axes[1]:
            add_element(LineBox(elements, axes_style[1], lines=[[Coords(elements, pos=(origin_x,ymin), d=(0,-axes_extra)),
                Coords(elements, pos=(origin_x,ymax), d=(0,axes_extra))]]))
            ticks = []
            tick_label_style = ticks_style[1].clone()
            tick_label_style.extend(label_style)
            for k in range(start_k_y, start_k_y+steps_y+1):
                if k != origin_k_y:
                    y = k * step_y
                    if y > ymax:
                        break
                    pos = (origin_x,y)
                    ticks.append([Coords(elements, pos=pos),
                        Coords(elements, pos=pos, d=(tick_large_size,0))])
                    add_element(InsetBox(elements, tick_label_style, content=Real(y), pos=Coords(elements, pos=pos,
                        d=(-tick_label_d,0)), opos=(1,0)))
            for k in range(start_k_y_small, start_k_y_small+steps_y_small+1):
                if k % sub_y != 0:
                    y = k * step_y_small
                    if y > ymax:
                        break
                    pos = (origin_x,y)
                    ticks.append([Coords(elements, pos=pos),
                        Coords(elements, pos=pos, d=(tick_small_size,0))])
            add_element(LineBox(elements, axes_style[1], lines=ticks))"""


class FilledCurveBox(_GraphicsElementBox):
    """
    <dl>
    <dt>'FilledCurveBox[...]'
    <dd>is a box structure for 'FilledCurve' elements.
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
                raise BoxConstructError
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
                            raise BoxConstructError
                        k = spline_degree.get_int_value()
                    elif head == "System`BSplineCurve":
                        raise NotImplementedError  # FIXME convert bspline to bezier here
                        # parts = segment.elements
                    else:
                        raise BoxConstructError

                    coords = []

                    for part in parts:
                        if part.get_head_name() != "System`List":
                            raise BoxConstructError
                        coords.extend(
                            [graphics.coords(graphics, xy) for xy in part.elements]
                        )

                    yield k, coords

            if all(x.get_head_name() == "System`List" for x in elements):
                self.components = [list(parse_component(x)) for x in elements]
            else:
                self.components = [list(parse_component(elements))]
        else:
            raise BoxConstructError

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


class InsetBox(_GraphicsElementBox):
    def init(
        self,
        graphics,
        style,
        item=None,
        content=None,
        pos=None,
        opos=(0, 0),
        opacity=None,
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

        if item is not None:
            if len(item.elements) not in (1, 2, 3):
                raise BoxConstructError
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

        if isinstance(self.content, String):
            self.content = self.content.atom_to_boxes(
                SymbolStandardForm, evaluation=self.graphics.evaluation
            )
        self.content_text = self.content.boxes_to_text(
            evaluation=self.graphics.evaluation
        )

    def extent(self):
        p = self.pos.pos()
        h = 25
        w = len(self.content_text) * 7  # rough approximation by numbers of characters
        opos = self.opos
        x = p[0] - w / 2.0 - opos[0] * w / 2.0
        y = p[1] - h / 2.0 + opos[1] * h / 2.0
        return [(x, y), (x + w, y + h)]


class LineBox(_Polyline):
    # Boxing methods for a list of Line.

    def init(self, graphics, style, item=None, lines=None):
        super(LineBox, self).init(graphics, item, style)
        self.edge_color, _ = style.get_style(_ColorObject, face_element=False)
        self.edge_opacity, _ = style.get_style(Opacity, face_element=False)
        if item is not None:
            if len(item.elements) != 1:
                raise BoxConstructError
            points = item.elements[0]
            self.do_init(graphics, points)
        elif lines is not None:
            self.lines = lines
        else:
            raise BoxConstructError


class PointBox(_Polyline):
    """
    <dl>
    <dt>'PointBox'[{$x$, $y$}]
    <dd> a box construction representing a point in a Graphic.
    <dt>'PointBox'[{$x$, $y$, $z$}]
    <dd> represents a point in a Graphic3D.
    <dt>'PointBox'[{$p_1$, $p_2$,...}]
    <dd> represents a set of points.
    </dl>
    ## Boxing methods for a list of Point.
    ##
    ## object attributes:
    ## edge_color: _ColorObject
    ## point_radius: radius of each point
    """

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
                raise BoxConstructError
            points = item.elements[0]
            if points.has_form("List", None) and len(points.elements) != 0:
                if all(
                    not element.has_form("List", None) for element in points.elements
                ):
                    points = ListExpression(points)
            self.do_init(graphics, points)
        else:
            raise BoxConstructError

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
                raise BoxConstructError
            points = item.elements[0]
            self.do_init(graphics, points)
            self.vertex_colors = None
            for element in item.elements[1:]:
                if not element.has_form("Rule", 2):
                    raise BoxConstructError
                name = element.elements[0].get_name()
                self.process_option(name, element.elements[1])
        else:
            raise BoxConstructError

    def process_option(self, name, value):
        if name == "System`VertexColors":
            if not value.has_form("List", None):
                raise BoxConstructError
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
            raise BoxConstructError


class RectangleBox(_GraphicsElementBox):
    def init(self, graphics, style, item):
        super(RectangleBox, self).init(graphics, item, style)
        if len(item.elements) not in (1, 2):
            raise BoxConstructError
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
    def init(self, graphics, style, item):
        if len(item.elements) in (1, 2, 3) and isinstance(item.elements[-1], Integer):
            r = 1.0
            phi0 = None

            if len(item.elements) >= 2:
                rspec = item.elements[-2]
                if rspec.get_head_name() == "System`List":
                    if len(rspec.elements) != 2:
                        raise BoxConstructError
                    r = rspec.elements[0].round_to_float()
                    phi0 = rspec.elements[1].round_to_float()
                else:
                    r = rspec.round_to_float()

            x = 0.0
            y = 0.0
            if len(item.elements) == 3:
                pos = item.elements[0]
                if not pos.has_form("List", 2):
                    raise BoxConstructError
                x = pos.elements[0].round_to_float()
                y = pos.elements[1].round_to_float()

            n = item.elements[-1].get_int_value()

            if any(t is None for t in (x, y, r)) or n < 0:
                raise BoxConstructError

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
            raise BoxConstructError

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
        Symbol("RegularPolygonBox"): RegularPolygonBox,
        Symbol("PointBox"): PointBox,
        Symbol("InsetBox"): InsetBox,
    }
)
