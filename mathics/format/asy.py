# -*- coding: utf-8 -*-
"""
Format a Mathics object as an Asymptote string
"""

import re

from mathics.builtin.box.graphics import (
    _ArcBox,
    ArrowBox,
    BezierCurveBox,
    FilledCurveBox,
    InsetBox,
    LineBox,
    PointBox,
    PolygonBox,
    RectangleBox,
    _RoundBox,
)

from mathics.builtin.box.graphics3d import (
    Graphics3DElements,
    Arrow3DBox,
    Cone3DBox,
    Cuboid3DBox,
    Cylinder3DBox,
    Line3DBox,
    Point3DBox,
    Polygon3DBox,
    Sphere3DBox,
    Tube3DBox,
)

from mathics.builtin.graphics import (
    DEFAULT_POINT_FACTOR,
    GraphicsElements,
    PointSize,
    RGBColor,
)

from mathics.builtin.box.uniform_polyhedra import UniformPolyhedron3DBox

INVERSE_POINT_FACTOR = 1 / DEFAULT_POINT_FACTOR


from mathics.core.formatter import lookup_method, add_conversion_fn
from mathics.format.asy_fns import (
    asy_add_bezier_fn,
    asy_add_graph_import,
    asy_bezier,
    asy_color,
    asy_create_pens,
    asy_number,
)


class _ASYTransform:
    _template = """
    add(%s * (new picture() {
        picture saved = currentpicture;
        picture transformed = new picture;
        currentpicture = transformed;
        %s
        currentpicture = saved;
        return transformed;
    })());
    """

    def __init__(self):
        self.transforms = []

    def matrix(self, a, b, c, d, e, f):
        # a c e
        # b d f
        # 0 0 1
        # see http://asymptote.sourceforge.net/doc/Transforms.html#Transforms
        # Note that the values a..f go down the rows and then across the columns
        # and not across the columns and then down the rows
        self.transforms.append("(%f, %f, %f, %f, %f, %f)" % (e, f, a, c, b, d))

    def translate(self, x, y):
        self.transforms.append("shift(%f, %f)" % (x, y))

    def scale(self, x, y):
        self.transforms.append("scale(%f, %f)" % (x, y))

    def rotate(self, x):
        self.transforms.append("rotate(%f)" % x)

    def apply(self, asy):
        return self._template % (" * ".join(self.transforms), asy)


def arcbox(self: _ArcBox, **options) -> str:
    """
    Aymptote formatting for an arc of a circle or an ellipse.
    """
    if self.arc is None:
        # We have a doughnut graph and this is the inner blank hole of that.
        # It is an empty circle
        return _roundbox(self)

    x, y, rx, ry, sx, sy, ex, ey, large_arc = self._arc_params()

    ry = max(ry, 0.1)  # Avoid division by 0
    yscale = ry / rx

    def create_arc_path(is_closed: bool, yscale: float) -> str:
        """Constructs arc path taking into account whether the path
        is closed and the scaling along the Y dimension (i.e. Mathics
        disks support ellipses.

        An Asymptote string for the path is returned.
        """
        arc_path = ""
        if is_closed:
            arc_path = "(%s,%s)--(%s,%s)--" % tuple(
                asy_number(t) for t in (x, y, sx, sy)
            )

        arc_path += "arc((%s,%s), (%s, %s), (%s, %s))" % tuple(
            asy_number(t) for t in (x, y, sx, sy, ex, ey)
        )

        if is_closed:
            arc_path += "--cycle"

        if yscale != 1.0:
            arc_path = f"yscale({yscale}) * ({arc_path})"

        return arc_path

    stroke_width = self.style.get_line_width(face_element=self.face_element)
    edge_opacity_value = self.edge_opacity.opacity if self.edge_opacity else None
    face_opacity_value = self.face_opacity.opacity if self.face_opacity else None

    pen = asy_create_pens(
        edge_color=self.edge_color,
        face_color=self.face_color,
        edge_opacity=edge_opacity_value,
        face_opacity=face_opacity_value,
        stroke_width=stroke_width,
        is_face_element=self.face_element,
    )
    command = "filldraw" if self.face_element else "draw"
    arc_path = create_arc_path(self.face_element, yscale)
    asy = f"""// ArcBox
{command}({arc_path}, {pen});"""
    # print("### arcbox", asy)
    return asy


add_conversion_fn(_ArcBox, arcbox)


def arrow_box(self: ArrowBox, **options) -> str:
    width = self.style.get_line_width(face_element=False)
    edge_opacity_value = self.edge_opacity.opacity if self.edge_opacity else None
    pen = asy_create_pens(
        edge_color=self.edge_color, stroke_width=width, edge_opacity=edge_opacity_value
    )
    polyline = self.curve.make_draw_asy(pen)

    arrow_pen = asy_create_pens(
        face_color=self.edge_color, stroke_width=width, face_opacity=edge_opacity_value
    )

    def polygon(points):
        yield "filldraw("
        yield "--".join(["(%.5g,%5g)" % xy for xy in points])
        yield "--cycle, % s);" % arrow_pen

    extent = self.graphics.view_width or 0
    default_arrow = self._default_arrow(polygon)
    custom_arrow = self._custom_arrow("asy", _ASYTransform)
    asy = "".join(self._draw(polyline, default_arrow, custom_arrow, extent))
    # print("### arrowbox", asy)
    return asy


add_conversion_fn(ArrowBox, arrow_box)


def build_3d_pen_color(color, opacity=None):
    if len(color) == 4:
        opacity_value = color[3]
        color = color[:3]
    else:
        opacity_value = opacity.opacity if opacity else None
    color_str = "rgb({0},{1},{2})".format(*color)
    if opacity_value:
        color_str = color_str + f"+opacity({opacity_value})"
    return color_str


def arrow3dbox(self, **options) -> str:
    """
    Aymptote 3D formatter for Arrow3DBox
    """

    # Set style parameters.
    edge_opacity_value = self.edge_opacity.opacity if self.edge_opacity else None
    pen = asy_create_pens(
        edge_color=self.edge_color, stroke_width=1, edge_opacity=edge_opacity_value
    )

    # Draw lines between all points except the last.
    lines_str = "--".join(
        ["({0},{1},{2})".format(*(coords.pos()[0])) for coords in self.lines[0][:-1]]
    )
    asy = f"draw({lines_str}, {pen});\n"

    # Draw an arrow between the penultimate and the last point.
    last_line_str = "--".join(
        ["({0},{1},{2})".format(*(coords.pos()[0])) for coords in self.lines[0][-2:]]
    )
    asy += f"draw(({last_line_str}), {pen}, Arrow3);\n"

    # print(asy)
    return asy


add_conversion_fn(Arrow3DBox)


def bezier_curve_box(self: BezierCurveBox, **options) -> str:
    """
    Asymptote formatter for BezierCurveBox.
    """
    line_width = self.style.get_line_width(face_element=False)
    edge_opacity_value = self.edge_opacity.opacity if self.edge_opacity else None
    pen = asy_create_pens(
        edge_color=self.edge_color,
        stroke_width=line_width,
        edge_opacity=edge_opacity_value,
    )

    asy = "// BezierCurveBox\n"
    asy += asy_add_graph_import(self)
    asy += asy_add_bezier_fn(self)
    for i, line in enumerate(self.lines):
        pts = [str(xy.pos()) for xy in line]
        for j in range(1, len(pts) - 1, 3):
            triple = ", ".join(pts[j - 1 : j + 3])
            asy += """pair[] P%d_%d={%s};\n""" % (i, j, triple)
            asy += """pair G%d_%d(real t){return Bezier(P%d_%d,t);}\n""" % (i, j, i, j)
            asy += """draw(shift(0, -2)*graph(G%d_%d,0,1,350), %s);\n""" % (i, j, pen)
    # print("BezierCurveBox: " asy)
    return asy


add_conversion_fn(BezierCurveBox, bezier_curve_box)


def cone3dbox(self: Cone3DBox, **options) -> str:
    face_color = self.face_color.to_js() if self.face_color else (1, 1, 1)
    opacity = self.face_opacity
    color_str = build_3d_pen_color(face_color, opacity)

    # FIXME: currently always drawing around the axis X+Y
    axes_point = (1, 1, 0)

    asy = "// Cone3DBox\n"
    i = 0
    while i < len(self.points) / 2:
        try:
            point1 = self.points[i * 2].pos()[0]
            point2 = self.points[i * 2 + 1].pos()[0]

            # Compute distance between start point and end point.
            distance = (
                (point1[0] - point2[0]) ** 2
                + (point1[1] - point2[1]) ** 2
                + (point1[2] - point2[2]) ** 2
            ) ** 0.5

            asy += (
                f"draw(surface(cone({tuple(point1)}, {self.radius}, {distance}, {axes_point})), {color_str});"
                + "\n"
            )
        except:  # noqa
            pass

        i += 1

    # print(asy)
    return asy


add_conversion_fn(Cone3DBox)


def cuboid3dbox(self: Cuboid3DBox, **options) -> str:
    face_color = self.face_color.to_js() if self.face_color else (1, 1, 1)
    opacity = self.face_opacity
    color_str = build_3d_pen_color(face_color, opacity)
    asy = "// Cuboid3DBox\n"

    i = 0
    while i < len(self.points) / 2:
        try:
            point1 = self.points[i * 2].pos()[0]
            point2 = self.points[i * 2 + 1].pos()[0]

            asy += f"""
                draw(shift({point1[0]}, {point1[1]}, {point1[2]}) * scale(
                    {point2[0] - point1[0]},
                    {point2[1] - point1[1]},
                    {point2[2] - point1[2]}
                ) * unitcube, {color_str});
            """

        except:  # noqa
            pass

        i += 1

    # Strip \n followed by blanks, since that can
    # confuse "asy" inside mathicsccript and give syntax errors.
    asy = re.sub(r"\n[ ]+", "", asy)
    # print(asy)
    return asy


add_conversion_fn(Cuboid3DBox)


def cylinder3dbox(self: Cylinder3DBox, **options) -> str:
    face_color = self.face_color.to_js() if self.face_color else (1, 1, 1)
    opacity = self.face_opacity
    color_str = build_3d_pen_color(face_color, opacity)

    asy = "// Cylinder3DBox\n"
    # asy += "currentprojection=orthographic(3,1,4,center=true,zoom=.9);\n"
    i = 0
    while i < len(self.points) / 2:
        try:
            point1 = self.points[i * 2].pos()[0]
            point2 = self.points[i * 2 + 1].pos()[0]
            asy += f"real r={self.radius};\n"
            asy += f"triple A={tuple(point1)}, B={tuple(point2)};\n"
            asy += "real h=abs(A-B);\n"
            asy += "revolution cyl=cylinder(A,r,h,B-A);\n"
            asy += f"draw(surface(cyl),{color_str});\n"

            # The above is an open cylinder. Draw the ends.
            asy += f"draw(surface(circle(A,r,normal=B-A)),{color_str});\n"
            asy += f"draw(surface(circle(B,r,normal=B-A)),{color_str});\n"
        except:  # noqa
            pass

        i += 1

    # print(asy)
    return asy


add_conversion_fn(Cylinder3DBox)


def filled_curve_box(self, **options) -> str:
    line_width = self.style.get_line_width(face_element=False)
    edge_opacity_value = self.edge_opacity.opacity if self.edge_opacity else None
    pen = asy_create_pens(
        edge_color=self.edge_color,
        stroke_width=line_width,
        edge_opacity=edge_opacity_value,
    )

    if not pen:
        pen = "currentpen"

    def components():
        for component in self.components:
            transformed = [(k, [xy.pos() for xy in p]) for k, p in component]
            yield "fill(%s--cycle, %s);" % ("".join(asy_bezier(*transformed)), pen)

    return "".join(components())


add_conversion_fn(FilledCurveBox, filled_curve_box)


def graphics_elements(self, **options) -> str:
    """
    Asymptote formatting on a list of graphics elements.
    """
    result = []
    for element in self.elements:
        try:
            format_fn = lookup_method(element, "asy")
        except Exception:
            # Note error and continue
            result.append(f"""unhandled {element}""")
            continue

        if format_fn is None:
            result.append(element.to_asy(**options))
        else:
            result.append(format_fn(element))

    return "\n".join(result)


add_conversion_fn(GraphicsElements, graphics_elements)
graphics3delements = graphics_elements


add_conversion_fn(Graphics3DElements)


def inset_box(self, **options) -> str:
    """Asymptote formatting for boxing an Inset in a graphic."""
    x, y = self.pos.pos()
    opacity_value = self.opacity.opacity if self.opacity else None
    content = self.content.boxes_to_tex(evaluation=self.graphics.evaluation)
    pen = asy_create_pens(edge_color=self.color, edge_opacity=opacity_value)
    asy = """// InsetBox
label("$%s$", (%s,%s), (%s,%s), %s);\n""" % (
        content,
        x,
        y,
        -self.opos[0],
        -self.opos[1],
        pen,
    )
    return asy


add_conversion_fn(InsetBox, inset_box)


def line3dbox(self, **options) -> str:
    # l = self.style.get_line_width(face_element=False)
    edge_opacity_value = self.edge_opacity.opacity if self.edge_opacity else None
    pen = asy_create_pens(
        edge_color=self.edge_color, stroke_width=1, edge_opacity=edge_opacity_value
    )

    return "".join(
        "// Line3DBox draw({0}, {1});".format(
            "--".join("({0},{1},{2})".format(*coords.pos()[0]) for coords in line),
            pen,
        )
        for line in self.lines
    )


add_conversion_fn(Line3DBox)


def line_box(self: LineBox) -> str:
    line_width = self.style.get_line_width(face_element=False)
    edge_opacity_value = self.edge_opacity.opacity if self.edge_opacity else None
    pen = asy_create_pens(
        edge_color=self.edge_color,
        stroke_width=line_width,
        edge_opacity=edge_opacity_value,
    )
    asy = "// LineBox\n"
    for line in self.lines:
        path = "--".join(["(%.5g,%5g)" % coords.pos() for coords in line])
        asy += "draw(%s, %s);" % (path, pen)
    # print("### linebox", asy)
    return asy


add_conversion_fn(LineBox, line_box)


def point3dbox(self: Point3DBox, **options) -> str:
    """
    Aymptote 3D formatter for Point3DBox
    """

    face_color = self.face_color
    face_opacity_value = face_color.to_rgba()[3]
    if face_opacity_value is None:
        face_opacity_value = self.face_opacity.opacity

    # Tempoary bug fix: default Point color should be black not white
    if list(face_color.to_rgba()[:3]) == [1, 1, 1]:
        face_color = RGBColor(components=(0, 0, 0))

    pen = asy_create_pens(
        face_color=face_color, is_face_element=False, face_opacity=face_opacity_value
    )
    points = []
    for line in self.lines:
        point_coords = "--".join(
            "(%.5g,%.5g,%.5g)" % coords.pos()[0] for coords in line
        )
        point = f"path3 g={point_coords}--cycle;dot(g, {pen});\n"
        points.append(point)

    asy = "// Point3DBox\n" + "\n".join(points)
    # print asy
    return asy


add_conversion_fn(Point3DBox)


def pointbox(self: PointBox, **options) -> str:

    point_size, _ = self.style.get_style(PointSize, face_element=False)
    if point_size is None:
        point_size = PointSize(self.graphics, value=DEFAULT_POINT_FACTOR)

    # We'll use the heuristic that the default line width is 1 should correspond
    # to the DEFAULT_POINT_FACTOR
    dotfactor = INVERSE_POINT_FACTOR * point_size.value
    face_opacity_value = self.face_opacity.opacity if self.face_opacity else None
    pen = asy_create_pens(
        face_color=self.face_color,
        is_face_element=False,
        dotfactor=dotfactor,
        face_opacity=face_opacity_value,
    )

    asy = "// PointBox\n"
    for line in self.lines:
        for coords in line:
            asy += "dot(%s, %s);" % (coords.pos(), pen)

    # print(asy)
    return asy


add_conversion_fn(PointBox)


def polygon_3d_box(self: Polygon3DBox, **options) -> str:
    """
    Asymptote formatting of a Polygon3DBox.
    """
    stroke_width = self.style.get_line_width(face_element=True)
    if self.vertex_colors is None:
        face_color = self.face_color
        face_opacity_value = self.face_opacity.opacity if self.face_opacity else None
    else:
        face_color = None
        face_opacity_value = None

    edge_opacity_value = self.edge_opacity.opacity if self.edge_opacity else None
    pen = asy_create_pens(
        edge_color=self.edge_color,
        face_color=face_color,
        edge_opacity=edge_opacity_value,
        face_opacity=face_opacity_value,
        stroke_width=stroke_width,
        is_face_element=True,
    )

    asy = "// Polygon3DBox\n"
    for line in self.lines:
        asy += (
            "path3 g="
            + "--".join(["(%.5g,%.5g,%.5g)" % coords.pos()[0] for coords in line])
            + "--cycle;"
        )
        asy += "draw(surface(g), %s);" % (pen)

    # print(asy)
    return asy


add_conversion_fn(Polygon3DBox, polygon_3d_box)


def polygonbox(self: PolygonBox, **options) -> str:
    line_width = self.style.get_line_width(face_element=True)
    if self.vertex_colors is None:
        face_color = self.face_color
        face_opacity_value = self.face_opacity.opacity if self.face_opacity else None
    else:
        face_color = None
        face_opacity_value = None

    edge_opacity_value = self.edge_opacity.opacity if self.edge_opacity else None
    pens = asy_create_pens(
        edge_color=self.edge_color,
        face_color=face_color,
        edge_opacity=edge_opacity_value,
        face_opacity=face_opacity_value,
        stroke_width=line_width,
        is_face_element=True,
    )
    asy = "// PolygonBox\n"
    if self.vertex_colors is not None:
        paths = []
        colors = []
        edges = []
        for index, line in enumerate(self.lines):
            paths.append(
                "--".join(["(%.5g,%.5g)" % coords.pos() for coords in line]) + "--cycle"
            )

            # ignore opacity
            colors.append(
                ",".join([asy_color(color)[0] for color in self.vertex_colors[index]])
            )

            edges.append(",".join(["0"] + ["1"] * (len(self.vertex_colors[index]) - 1)))

        asy += "gouraudshade(%s, new pen[] {%s}, new int[] {%s});" % (
            "^^".join(paths),
            ",".join(colors),
            ",".join(edges),
        )
    if pens and pens != "nullpen":
        for line in self.lines:
            path = (
                "--".join(["(%.5g,%.5g)" % coords.pos() for coords in line]) + "--cycle"
            )
            asy += "filldraw(%s, evenodd+%s);" % (path, pens)

    # print(asy)
    return asy


add_conversion_fn(PolygonBox)


def rectanglebox(self: RectangleBox, **options) -> str:
    line_width = self.style.get_line_width(face_element=True)
    x1, y1 = self.p1.pos()
    x2, y2 = self.p2.pos()
    edge_opacity_value = self.edge_opacity.opacity if self.edge_opacity else None
    face_opacity_value = self.face_opacity.opacity if self.face_opacity else None
    pens = asy_create_pens(
        self.edge_color,
        self.face_color,
        edge_opacity=edge_opacity_value,
        face_opacity=face_opacity_value,
        stroke_width=line_width,
        is_face_element=True,
    )
    x1, x2, y1, y2 = asy_number(x1), asy_number(x2), asy_number(y1), asy_number(y2)
    asy = "// RectangleBox\n"
    asy += "filldraw((%s,%s)--(%s,%s)--(%s,%s)--(%s,%s)--cycle, %s);" % (
        x1,
        y1,
        x2,
        y1,
        x2,
        y2,
        x1,
        y2,
        pens,
    )
    # print("### rectanglebox", asy)
    return asy


add_conversion_fn(RectangleBox)


def _roundbox(self: _RoundBox):
    x, y = self.c.pos()
    rx, ry = self.r.pos()
    rx -= x
    ry -= y
    line_width = self.style.get_line_width(face_element=self.face_element)
    edge_opacity_value = self.edge_opacity.opacity if self.edge_opacity else None
    face_opacity_value = self.face_opacity.opacity if self.face_opacity else None
    pen = asy_create_pens(
        edge_color=self.edge_color,
        face_color=self.face_color,
        edge_opacity=edge_opacity_value,
        face_opacity=face_opacity_value,
        stroke_width=line_width,
        is_face_element=self.face_element,
    )
    cmd = "filldraw" if self.face_element else "draw"
    return "%s(ellipse((%s,%s),%s,%s), %s);" % (
        cmd,
        asy_number(x),
        asy_number(y),
        asy_number(rx),
        asy_number(ry),
        pen,
    )


add_conversion_fn(_RoundBox)


def sphere3dbox(self: Sphere3DBox, **options) -> str:
    # l = self.style.get_line_width(face_element=True)

    face_color = self.face_color.to_js() if self.face_color else (1, 1, 1)
    opacity = self.face_opacity
    color_str = build_3d_pen_color(face_color, opacity)

    return "// Sphere3DBox\n" + "\n".join(
        "draw(surface(sphere({0}, {1})), {2});".format(
            tuple(coord.pos()[0]), self.radius, color_str
        )
        for coord in self.points
    )


add_conversion_fn(Sphere3DBox)


def tube_3d_box(self: Tube3DBox, **options) -> str:
    if not (hasattr(self.graphics, "tube_import_added") and self.tube_import_added):

        self.graphics.tube_import_added = True
        asy_head = "import tube;\n\n"
    else:
        asy_head = ""
    face_color = self.face_color.to_js() if self.face_color else (1, 1, 1)
    opacity = self.face_opacity
    color_str = build_3d_pen_color(face_color, opacity)

    asy = (
        asy_head
        + "// Tube3DBox\n draw(tube({0}, scale({1})*unitcircle), {2});".format(
            "--".join(
                "({0},{1},{2})".format(*coords.pos()[0]) for coords in self.points
            ),
            self.radius,
            color_str,
        )
    )
    return asy


add_conversion_fn(Tube3DBox, tube_3d_box)


def uniform_polyhedron_3d_box(self: RectangleBox, **options) -> str:
    # l = self.style.get_line_width(face_element=True)

    face_color = self.face_color.to_js() if self.face_color else (1, 1, 1)
    opacity = self.face_opacity
    color_str = build_3d_pen_color(face_color, opacity)

    return (
        "// UniformPolyhedron3DBox\n // Still not really implemented. Draw a sphere instead\n"
        + "\n".join(
            "draw(surface(sphere({0}, {1})), {2});".format(
                tuple(coord.pos()[0]), self.edge_length, color_str
            )
            for coord in self.points
        )
    )


add_conversion_fn(UniformPolyhedron3DBox, uniform_polyhedron_3d_box)
