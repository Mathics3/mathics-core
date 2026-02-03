# -*- coding: utf-8 -*-
"""
Mathics3 Graphics box rendering to SVG strings.
"""

from mathics.builtin.box.graphics import (
    ArcBox,
    ArrowBox,
    BezierCurveBox,
    FilledCurveBox,
    GraphicsBox,
    InsetBox,
    LineBox,
    PointBox,
    PolygonBox,
    RectangleBox,
    RoundBox,
)
from mathics.builtin.drawing.graphics3d import Graphics3DElements
from mathics.builtin.graphics import DEFAULT_POINT_FACTOR, PointSize, _svg_bezier
from mathics.core.formatter import add_conversion_fn, lookup_method
from mathics.format.box.graphics import (
    GraphicsElements,
    prepare_elements as prepare_elements2d,
)


class _SVGTransform:
    def __init__(self):
        self.transforms = []

    def matrix(self, a, b, c, d, e, f):
        # a c e
        # b d f
        # 0 0 1
        self.transforms.append(f"matrix({a:f}, {b:f}, {c:f}, {d:f}, {e:f}, {f:f})")

    def translate(self, x, y):
        self.transforms.append(f"translate({x:f}, {y:f})")

    def scale(self, x, y):
        self.transforms.append(f"scale({x:f}, {y:f})")

    def rotate(self, x):
        self.transforms.append(f"rotate({x:f})")

    def apply(self, svg):
        return f"""<g transform="{' '.join(self.transforms)}">{svg}</g>"""


def create_css(
    edge_color=None,
    face_color=None,
    stroke_width=None,
    font_color=None,
    edge_opacity=None,
    face_opacity=None,
    opacity=1.0,
) -> str:
    """
    Return a string suitable for CSS inclusion setting the various parameters passed.
    """
    css = []
    edge_opacity_level = edge_opacity.to_css() if edge_opacity else None
    face_opacity_level = face_opacity.to_css() if face_opacity else None

    if edge_color is not None:
        color, stroke_opacity = edge_color.to_css()
        css.append(f"stroke: {color}")
        if stroke_opacity:
            css.append(f"stroke-opacity: {stroke_opacity}")
        elif edge_opacity:
            css.append(f"stroke-opacity: {edge_opacity_level}")
    else:
        css.append("stroke: none")
    if stroke_width is not None:
        css.append(f"stroke-width: {stroke_width:f}px")
    if face_color is not None:
        color, fill_opacity = face_color.to_css()
        css.append(f"fill: {color}")
        if fill_opacity:
            css.append(f"fill-opacity: {fill_opacity}")
        elif face_opacity:
            css.append(f"fill-opacity: {face_opacity_level}")
    else:
        css.append("fill: none")
    if font_color is not None:
        color, _ = font_color.to_css()
        css.append(f"color: {color}")
    if edge_opacity is None:
        css.append(f"opacity: {opacity}")
    return "; ".join(css)


def arcbox(box: ArcBox, **options) -> str:
    """
    SVG formatting for arc of a circle.
    """
    if box.arc is None:
        # We have a doughnut graph and this is the inner blank hole of that.
        # It is an empty circle
        return roundbox(box)

    x, y, rx, ry, sx, sy, ex, ey, large_arc = box._arc_params()

    def path(closed):
        if closed:
            yield f"M {x:f},{y:f}"
            yield f"L {sx:f},{sy:f}"
        else:
            yield f"M {sx:f},{sy:f}"

        yield "A %f,%f,0,%d,0,%f,%f" % (rx, ry, large_arc, ex, ey)

        if closed:
            yield "Z"

    line_width = box.style.get_line_width(face_element=box.face_element)
    style = create_css(
        box.edge_color,
        box.face_color,
        stroke_width=line_width,
        edge_opacity=box.edge_opacity,
        face_opacity=box.face_opacity,
    )
    svg = f"<path d=\"{' '.join(path(box.face_element))}\" style=\"{style}\" />"
    # print("_Arcbox: ", svg)
    return svg


add_conversion_fn(ArcBox, arcbox)


def arrow_box(box: ArrowBox, **options) -> str:
    width = box.style.get_line_width(face_element=False)
    style = create_css(
        box.edge_color, stroke_width=width, edge_opacity=box.edge_opacity
    )
    polyline = box.curve.make_draw_svg(style)

    arrow_style = create_css(face_color=box.edge_color, stroke_width=width)

    def polygon(points):
        yield '<polygon points="'
        yield " ".join("%f,%f" % xy for xy in points)
        yield f'" style="{arrow_style}" />'

    extent = box.graphics.view_width or 0
    default_arrow = box._default_arrow(polygon)
    custom_arrow = box._custom_arrow("svg", _SVGTransform)
    svg = "\n".join(box._draw(polyline, default_arrow, custom_arrow, extent))
    # print("ArrowBox: ", svg)
    return svg


add_conversion_fn(ArrowBox, arrow_box)


def bezier_curve_box(box: BezierCurveBox, **options) -> str:
    """
    SVG formatter for BezierCurveBox.
    """
    line_width = box.style.get_line_width(face_element=False)
    style = create_css(
        edge_color=box.edge_color,
        stroke_width=line_width,
        edge_opacity=box.edge_opacity,
    )
    svg = "<!--BezierCurveBox-->\n"
    for line in box.lines:
        s = "\n".join(_svg_bezier((box.spline_degree, [xy.pos() for xy in line])))
        svg += f'<path d="{s}" style="{style}"/>'
    # print("BezierCurveBox: ", svg)
    return svg


add_conversion_fn(BezierCurveBox, bezier_curve_box)


def density_plot_box(box, **options):
    """
    SVG formatter for DensityPlotBox.
    """
    # A DensityPlot is a just a list of triangles each of which have its density color.
    #
    # So this code is similar to PolygonBox.
    #
    # However note that many of the PolygonBox features are a little
    # different here. First, everything is a triangle, so there the
    # notion of odd/even crossing with holes doesn't apply.  Second
    # since each each point/triangle could be a different color, we'll
    # have to write out a separate polygon for each.

    # There is a lot of fanciness one could do here, like sort points into those that have
    # the same color and put all of those into a single polygonbox.

    # Here is an even more elaborate scheme which I won't use, but
    # since it is a cute idea, it is worthy of comment space...  Put
    # two triangles together to get a parallelogram. Compute the
    # midpoint color in the enter and along all four sides. Then use
    # two overlaid rectangular gradients each at opacity 0.5
    # to go from the center to each of the (square) sides.

    svg_data = ["<!--DensityPlot-->"]
    for index, triangle_coords in enumerate(box.lines):
        triangle = [coords.pos() for coords in triangle_coords]
        colors = [rgb.to_js() for rgb in box.vertex_colors[index]]
        r = (colors[0][0] + colors[1][0] + colors[2][0]) / 3
        g = (colors[0][1] + colors[1][1] + colors[2][1]) / 3
        b = (colors[0][2] + colors[1][2] + colors[2][1]) / 3
        mid_color = r"rgb(%f, %f, %f)" % (r * 255, g * 255, b * 255)

        points = " ".join(f"{point[0]:f},{point[1]:f}" for point in triangle)
        svg_data.append(f'<polygon points="{points}" fill="{mid_color}" />')

    svg = "\n".join(svg_data)
    # print("DensityPlot: ", svg)
    return svg


# No add_conversion_fn since this is a hacken-on polygonbox


def filled_curve_box(box: FilledCurveBox, **options):
    line_width = box.style.get_line_width(face_element=False)
    style = create_css(
        edge_color=box.edge_color, face_color=box.face_color, stroke_width=line_width
    )
    style = create_css(
        edge_color=box.edge_color,
        face_color=box.face_color,
        stroke_width=line_width,
        edge_opacity=box.edge_opacity,
        face_opacity=box.edge_opacity,
    )

    def components():
        for component in box.components:
            transformed = [(k, [xy.pos() for xy in p]) for k, p in component]
            yield " ".join(_svg_bezier(*transformed)) + " Z"

    # print("FilledCurveBox: ", components)
    return '<path d="%s" style="%s" fill-rule="evenodd"/>' % (
        " ".join(components()),
        style,
    )


add_conversion_fn(FilledCurveBox, filled_curve_box)


def graphics_box(box: GraphicsBox, elements=None, **options: dict) -> str:
    """
    Top-level SVG routine takes ``elements`` and ``options`` and turns
    this into a SVG string, including the <svg>..</svg> tag.

    ``elements`` could be a ``GraphicsElements`` object,
    a tuple or a list.

    Options is a dictionary of Graphics options dictionary. Interesting Graphics options keys:

    ``data``: a tuple bounding box information as well as a copy of ``elements``. If given
    this supersedes the information in the ``elements`` parameter.

    ``evaluation``:  an ``Evaluation`` object that can be used when further evaluation is needed.
    """

    assert elements is None
    elements = box.content

    data = options.get("data", None)
    assert data is None
    if data:
        (
            elements,
            xmin,
            xmax,
            ymin,
            ymax,
            box.boxwidth,
            box.boxheight,
            width,
            height,
        ) = data
    else:
        elements, calc_dimensions = prepare_elements2d(
            box, elements, options, neg_y=True
        )
        (
            xmin,
            xmax,
            ymin,
            ymax,
            box.boxwidth,
            box.boxheight,
            width,
            height,
        ) = calc_dimensions()

    elements.view_width = box.boxwidth

    format_fn = lookup_method(elements, "svg")
    if format_fn is not None:
        svg_body = format_fn(elements, **options)
    else:
        svg_body = elements.to_svg(**options)

    box.boxwidth = options.get("width", box.boxwidth)
    box.boxheight = options.get("height", box.boxheight)

    tooltip_text = box.tooltip_text or ""
    if box.background_color is not None:
        # FIXME: tests don't seem to cover this section of code.
        # Wrap svg_elements in a rectangle

        background = "rgba(100%,100%,100%,100%)"
        if box.background_color:
            components = box.background_color.to_rgba()
            if len(components) == 3:
                background = "rgb(" + ", ".join(f"{100*c}%" for c in components) + ")"
            else:
                background = "rgba(" + ", ".join(f"{100*c}%" for c in components) + ")"

        svg_body = f"""
            <rect
                 x="{xmin:f}" y="{ymin:f}"
                 width="{box.boxwidth:f}"
                 height="{box.boxheight:f}"
                 style="fill:{background}"><title>{tooltip_text}</title></rect>
            {svg_body}
           """

    if options.get("noheader", False):
        return svg_body

    svg_main = wrap_svg_body(box.boxwidth, box.boxheight, xmin, ymin, svg_body)
    # print("svg_main", svg_main)
    return svg_main  # , width, height


add_conversion_fn(GraphicsBox, graphics_box)


def graphics_elements(box: GraphicsElements, **options) -> str:
    """
    SVG formatting on a GraphicsElementBox which may contain other GraphicsElementBox's.
    """
    result = ["<!--GraphicsElements-->"]
    for element in box.elements:
        try:
            format_fn = lookup_method(element, "svg")
        except Exception:
            # Note error and continue
            result.append(f"""unhandled {element}""")
            continue

        if format_fn is None:
            result.append(element.to_svg(**options))
        else:
            result.append(format_fn(element, **options))

    svg = "\n".join(result)
    # print("GraphicsElements: ", svg)
    return svg


add_conversion_fn(GraphicsElements, graphics_elements)
graphics3delements = graphics_elements

add_conversion_fn(Graphics3DElements)


def inset_box(box: InsetBox, **options) -> str:
    """
    SVG formatting for boxing an Inset in a graphic.
    """
    x, y = box.pos.pos()
    offset = options.get("offset", None)
    if offset is not None:
        x = x + offset[0]
        y = y + offset[1]
    if hasattr(box.content, "to_svg"):
        content = box.content.to_svg(noheader=True, offset=(x, y))
        svg = "\n" + content + "\n"
    else:
        css_style = create_css(
            font_color=box.color,
            edge_color=box.color,
            face_color=box.color,
            stroke_width=0.2,
            opacity=box.opacity.opacity,
        )
        text_pos_opts = f'x="{x}" y="{y}" ox="{box.opos[0]}" oy="{box.opos[1]}"'

        alignment = " dominant-baseline:hanging;"
        if hasattr(box, "alignment"):
            if box.alignment == "bottom":
                # This is typically done for labels under the x axis.
                alignment = " dominant-baseline:hanging; text-anchor:middle;"
            elif box.alignment == "left":
                # This is typically done for labels to the left of the y axis.
                alignment = " dominant-baseline:middle; text-anchor:end;"

        # FIXME: don't hard code text_style_opts, but allow these to be adjustable.
        text_style_opts = alignment
        content = box.content.boxes_to_text(evaluation=box.graphics.evaluation)
        font_size = f'''font-size="{options.get("point_size", "10px")}"'''
        svg = f'<text {text_pos_opts} {font_size} style="{text_style_opts} {css_style}">{content}</text>'

    # content = box.content.boxes_to_mathml(evaluation=box.graphics.evaluation)
    # style = create_css(font_color=box.color)
    # svg = (
    #    '<foreignObject x="%f" y="%f" ox="%f" oy="%f" style="%s">'
    #    "<math>%s</math></foreignObject>")
    # print(svg)

    return svg


add_conversion_fn(InsetBox, inset_box)


def line_box(box: LineBox, **options) -> str:
    line_width = box.style.get_line_width(face_element=False)
    style = create_css(
        edge_color=box.edge_color,
        stroke_width=line_width,
        edge_opacity=box.edge_opacity,
    )

    # The following line options come from looking at SVG produced from WMA.
    # In the future we may incorporate these into create_css or
    # narrow this based on context.
    style += "; stroke-linecap:square; stroke-linejoin:miter; stroke-miterlimit:3.25"

    svg = "<!--LineBox-->\n"
    for line in box.lines:
        svg += '<polyline points="%s" style="%s" />' % (
            " ".join(["%f,%f" % coords.pos() for coords in line]),
            style,
        )
    # print("LineBox", svg)
    return svg


add_conversion_fn(LineBox, line_box)


def pointbox(box: PointBox, **options) -> str:
    point_size, _ = box.style.get_style(PointSize, face_element=False)
    if point_size is None:
        point_size = PointSize(box.graphics, value=DEFAULT_POINT_FACTOR)
    size = point_size.get_absolute_size()

    style = create_css(
        edge_color=box.edge_color,
        stroke_width=0,
        face_color=box.face_color,
        edge_opacity=box.edge_opacity,
        face_opacity=box.face_opacity,
    )

    # The following line options come from looking at SVG produced from WMA.
    # In the future we may incorporate these into create_css or
    style += "; fill-rule:even-odd"

    svg = "<!--PointBox-->"
    for line in box.lines:
        for coords in line:
            svg += f"""
  <circle cx="{coords.pos()[0]:f}" cy="{coords.pos()[1]:f}"
          r="{size:f}" style="{style}"/>"""
    # print("PointBox", svg)
    return svg


add_conversion_fn(PointBox)


def polygonbox(box: PolygonBox, **options):
    """
    SVG formatter for PolygonBox
    """
    line_width = box.style.get_line_width(face_element=True)

    # Hack alert. Currently we encode density plots as a polygon box where
    # each polygon is a triangle with a color. We know we have this case because
    # box.vertex_colors is not empty here.
    if box.vertex_colors:
        return density_plot_box(box, **options)

    style = create_css(
        edge_color=box.edge_color,
        face_color=box.face_color,
        stroke_width=line_width,
        edge_opacity=box.edge_opacity,
        face_opacity=box.face_opacity,
    )

    svg = "<!--PolygonBox-->\n"
    # WL says this about 2D polygons:
    #   A point is an element of the polygon if a ray from the point in any direction in the plane crosses the boundary line segments an odd number of times.
    #
    # In SVG, this is called the "evenodd" fill rule.
    # Perhaps one day we will find it useful to have other fill_rules specified as an option.
    fill_rule = "evenodd"

    for line in box.lines:
        svg += f"""
  <polygon points="{" ".join("%f,%f" % coords.pos() for coords in line)}"
           fill-rule="{fill_rule}"
           style="{style}" />\n"""
    # print("PolygonBox: ", svg)
    return svg


add_conversion_fn(PolygonBox)


def rectanglebox(box: RectangleBox, **options):
    line_width = box.style.get_line_width(face_element=True)
    x1, y1 = box.p1.pos()
    x2, y2 = box.p2.pos()
    xmin = min(x1, x2)
    ymin = min(y1, y2)
    w = max(x1, x2) - xmin
    h = max(y1, y2) - ymin
    offset = options.get("offset", None)
    if offset is not None:
        x1, x2 = x1 + offset[0], x2 + offset[0]
        y1, y2 = y1 + offset[1], y2 + offset[1]
    style = create_css(
        box.edge_color,
        box.face_color,
        line_width,
        edge_opacity=box.edge_opacity,
        face_opacity=box.face_opacity,
    )
    svg = '<rect x="%f" y="%f" width="%f" height="%f" style="%s" />' % (
        xmin,
        ymin,
        w,
        h,
        style,
    )
    # print("RectangleBox", svg)
    return svg


add_conversion_fn(RectangleBox)


def roundbox(box: RoundBox):
    x, y = box.c.pos()
    rx, ry = box.r.pos()
    rx -= x
    ry = y - ry
    line_width = box.style.get_line_width(face_element=box.face_element)
    style = create_css(
        box.edge_color,
        box.face_color,
        stroke_width=line_width,
        edge_opacity=box.edge_opacity,
        face_opacity=box.face_opacity,
    )
    svg = f'<ellipse cx="{x:f}" cy="{y:f}" rx="{rx:f}" ry="{ry:f}" style="{style}" />'
    # print("RoundBox: ", svg)
    return svg


add_conversion_fn(RoundBox)


def wrap_svg_body(
    box_width: float, box_height: float, x_min: float, y_min: float, svg_body: str
) -> str:
    """
    Wraps ``svg`` into an SVG tag <svg> ... </svg>
    ``box_width`` and ``box_height`` are pixel units. These together with
    x_min, and y_min also form the viewBox attribute.

    The wrapped SVG text is returned as a string.
    """
    svg_str = f"""
<svg width="{box_width}px" height="{box_height}px" xmlns:svg="http://www.w3.org/2000/svg"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="{x_min:f} {y_min:f} {box_width:f}, {box_height:f}">
    {svg_body}
</svg>
"""
    # print(svg_str)
    return svg_str
