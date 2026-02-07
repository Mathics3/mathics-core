# -*- coding: utf-8 -*-
"""
Mathics3 Graphics box rendering to JSON data.

Right now, this happens in graphics primitives.
"""
import json

from mathics.builtin.box.graphics3d import (
    Arrow3DBox,
    Cone3DBox,
    Cuboid3DBox,
    Cylinder3DBox,
    Graphics3DBox,
    Line3DBox,
    Point3DBox,
    Polygon3DBox,
    Sphere3DBox,
    Tube3DBox,
)
from mathics.builtin.box.uniform_polyhedra import UniformPolyhedron3DBox
from mathics.builtin.drawing.graphics3d import Graphics3DElements
from mathics.builtin.graphics import PointSize
from mathics.core.formatter import add_conversion_fn, lookup_method
from mathics.format.box.graphics3d import prepare_elements as prepare_elements3d

# FIXME
# Add 2D elements like DensityPlot


def convert_coord_collection(
    collection: list, object_type: str, color, default_values: dict = {}
) -> list:
    """Convert collection into a list of dictionary items where each item is some sort of lower-level
    JSON object.
    """
    opacity = 1 if len(color) < 4 else color[3]
    data = [
        {
            **default_values,
            "type": object_type,
            "coords": [coords.pos() for coords in items],
            "opacity": opacity,
            "color": color[:3],
        }
        for items in collection
    ]

    # print(data)
    return data


def graphics_3D_elements(box: Graphics3DElements, **options) -> list:
    """Iterates over box.elements to converting each item.
    The list of converted items is returned.
    """
    result = []
    for element in box.elements:
        format_fn = lookup_method(element, "json")
        result += format_fn(element)

    # print("### json Graphics3DElements", result)
    return result


add_conversion_fn(Graphics3DElements, graphics_3D_elements)


def arrow_3d_box(box: Arrow3DBox):
    """
    Compact (lower-level) JSON formatting of a Arrow3DBox.
    """
    # TODO: account for arrow widths and style
    color = box.edge_color.to_rgba()
    data = convert_coord_collection(box.lines, "arrow", color)
    # print("### json Arrow3DBox", data)
    return data


add_conversion_fn(Arrow3DBox, arrow_3d_box)


def cone_3d_box(box: Cone3DBox):
    """
    Compact (lower-level) JSON formatting of a Cone3DBox.
    """
    face_color = box.face_color
    if face_color is not None:
        face_color = face_color.to_js()
    data = convert_coord_collection(
        [box.points],
        "cone",
        face_color,
        {"radius": box.radius},
    )
    # print("### json Cone3DBox", data)
    return data


add_conversion_fn(Cone3DBox, cone_3d_box)


def cuboid_3d_box(box: Cuboid3DBox):
    """
    Compact (lower-level) JSON formatting of a Cuboid3DBox.
    """
    face_color = box.face_color.to_js()
    if len(face_color) < 4 and box.face_opacity:
        face_color = face_color + [box.face_opacity.opacity]
    data = convert_coord_collection(
        [box.points],
        "cuboid",
        face_color,
    )
    # print("### json Cuboid3DBox", data)
    return data


add_conversion_fn(Cuboid3DBox, cuboid_3d_box)


def cylinder_3d_box(box: Cylinder3DBox):
    """
    Compact (lower-level) JSON formatting of a Cylinder3DBox.
    """
    face_color = box.face_color.to_js()
    if len(face_color) < 4 and box.face_opacity:
        face_color = face_color + [box.face_opacity.opacity]
    data = convert_coord_collection(
        [box.points],
        "cylinder",
        face_color,
        {"radius": box.radius},
    )
    # print("### json Cylinder3DBox", data)
    return data


add_conversion_fn(Cylinder3DBox, cylinder_3d_box)


def graphics3d_box_tojson(box: Graphics3DBox, content=None, **options):
    """Turn the Graphics3DBox to into a something JSON like.
    This can be used to embed in something else like MathML or Javascript.

    In contrast to to javascript or MathML, no enclosing tags are included.
    the caller will do that if it is needed.
    """
    assert content is None
    (
        elements,
        axes,
        ticks,
        ticks_style,
        calc_dimensions,
        boxscale,
    ) = prepare_elements3d(box, box.content, options)
    background = "rgba(100.0%, 100.0%, 100.0%, 100.0%)"
    if box.background_color:
        components = box.background_color.to_rgba()
        if len(components) == 3:
            background = "rgb(" + ", ".join(f"{100*c}%" for c in components) + ")"
        else:
            background = "rgba(" + ", ".join(f"{100*c}%" for c in components) + ")"

    tooltip_text = elements.tooltip_text if hasattr(elements, "tooltip_text") else ""

    js_ticks_style = [s.to_js() for s in ticks_style]
    elements._apply_boxscaling(boxscale)

    xmin, xmax, ymin, ymax, zmin, zmax, boxscale, w, h = calc_dimensions()
    elements.view_width = w
    # FIXME: json is the only thing we can convert MathML into.
    # Handle other graphics formats.
    format_fn = lookup_method(elements, "json")

    json_repr = json.dumps(
        {
            "elements": format_fn(elements, **options),
            "background_color": background,
            "tooltip_text": tooltip_text,
            "axes": {
                "hasaxes": axes,
                "ticks": ticks,
                "ticks_style": js_ticks_style,
            },
            "extent": {
                "xmin": xmin,
                "xmax": xmax,
                "ymin": ymin,
                "ymax": ymax,
                "zmin": zmin,
                "zmax": zmax,
            },
            "lighting": box.lighting,
            "viewpoint": box.viewpoint,
            "protocol": "1.1",
        }
    )
    return json_repr


add_conversion_fn(Graphics3DBox, graphics3d_box_tojson)


def line_3d_box(box: Line3DBox):
    """
    Compact (lower-level) JSON formatting of a Line3DBox.
    """
    # TODO: account for line widths and style
    color = box.edge_color.to_rgba()
    if len(color) < 4 and box.edge_opacity:
        color = color + [box.edge_opacity.opacity]
    data = convert_coord_collection(box.lines, "line", color)
    # print("### json Line3DBox", data)
    return data


add_conversion_fn(Line3DBox, line_3d_box)


def point_3d_box(box: Point3DBox) -> list:
    """
    Compact (lower-level) JSON formatting of a Point3DBox.
    """
    # TODO: account for point size

    face_color = box.face_color.to_rgba()
    if len(face_color) < 4 and box.face_opacity:
        face_color = face_color + [box.face_opacity.opacity]

    point_size, _ = box.style.get_style(PointSize, face_element=False)
    relative_point_size = 0.01 if point_size is None else point_size.value

    data = convert_coord_collection(
        box.lines,
        "point",
        face_color,
        {"pointSize": relative_point_size * 0.5},
    )

    # print("### json Point3DBox", data)
    return data


add_conversion_fn(Point3DBox, point_3d_box)


def polygon_3d_box(box: Polygon3DBox) -> list:
    """
    Compact (lower-level) JSON formatting of a Polygon3DBox.
    This format follows an API understood by mathics_threejs_backend.
    """
    # TODO: account for line widths and style
    if box.vertex_colors is None:
        face_color = box.face_color.to_js()
    else:
        face_color = None

    if face_color and len(face_color) < 4 and box.face_opacity:
        face_color = face_color + [box.face_opacity.opacity]
    data = convert_coord_collection(
        box.lines,
        "polygon",
        face_color,
    )
    # print("### json Polygon3DBox", data)
    return data


add_conversion_fn(Polygon3DBox, polygon_3d_box)


def sphere_3d_box(box: Sphere3DBox) -> list:
    face_color = box.face_color.to_js()
    if len(face_color) < 4 and box.face_opacity:
        face_color = face_color + [box.face_opacity.opacity]
    data = convert_coord_collection(
        [box.points],
        "sphere",
        face_color,
        {"radius": box.radius},
    )
    # print("### json Sphere3DBox", data)
    return data


add_conversion_fn(Sphere3DBox, sphere_3d_box)


def uniform_polyhedron_3d_box(box: UniformPolyhedron3DBox) -> list:
    face_color = box.face_color.to_js()
    if len(face_color) < 4 and box.edge_opacity:
        face_color = face_color + [box.face_opacity.opacity]
    data = convert_coord_collection(
        [box.points],
        "uniformPolyhedron",
        face_color,
        {"subType": box.sub_type},
    )
    # print("### json UniformPolyhedron3DBox", data)
    return data


add_conversion_fn(UniformPolyhedron3DBox, uniform_polyhedron_3d_box)


def tube_3d_box(box: Tube3DBox) -> list:
    face_color = box.face_color
    if face_color is not None:
        face_color = face_color.to_js()
        if len(face_color) < 4 and box.edge_opacity:
            face_color = face_color + [box.face_opacity.opacity]
    data = convert_coord_collection(
        [box.points],
        "tube",
        face_color,
        {"radius": box.radius},
    )
    # print("### json Tube3DBox", data)
    return data


add_conversion_fn(Tube3DBox, tube_3d_box)
