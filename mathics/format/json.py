# -*- coding: utf-8 -*-
"""
Lower-level formatter of Mathics objects as JSON data.

Right now this happens mostly for graphics primitives.
"""

from mathics.builtin.box.graphics3d import (
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
from mathics.builtin.box.uniform_polyhedra import UniformPolyhedron3DBox
from mathics.builtin.drawing.graphics3d import Graphics3DElements
from mathics.builtin.graphics import PointSize
from mathics.core.formatter import add_conversion_fn, lookup_method

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


def graphics_3D_elements(self, **options) -> list:
    """Iterates over self.elements to convert each item.
    The list of converted items is returned.
    """
    result = []
    for element in self.elements:
        format_fn = lookup_method(element, "json")
        result += format_fn(element)

    # print("### json Graphics3DElements", result)
    return result


add_conversion_fn(Graphics3DElements, graphics_3D_elements)


def arrow_3d_box(self):
    """
    Compact (lower-level) JSON formatting of a Arrow3DBox.
    """
    # TODO: account for arrow widths and style
    color = self.edge_color.to_rgba()
    data = convert_coord_collection(self.lines, "arrow", color)
    # print("### json Arrow3DBox", data)
    return data


add_conversion_fn(Arrow3DBox, arrow_3d_box)


def cone_3d_box(self):
    """
    Compact (lower-level) JSON formatting of a Cone3DBox.
    """
    face_color = self.face_color
    if face_color is not None:
        face_color = face_color.to_js()
    data = convert_coord_collection(
        [self.points],
        "cone",
        face_color,
        {"radius": self.radius},
    )
    # print("### json Cone3DBox", data)
    return data


add_conversion_fn(Cone3DBox, cone_3d_box)


def cuboid_3d_box(self):
    """
    Compact (lower-level) JSON formatting of a Cuboid3DBox.
    """
    face_color = self.face_color.to_js()
    if len(face_color) < 4 and self.face_opacity:
        face_color = face_color + [self.face_opacity.opacity]
    data = convert_coord_collection(
        [self.points],
        "cuboid",
        face_color,
    )
    # print("### json Cuboid3DBox", data)
    return data


add_conversion_fn(Cuboid3DBox, cuboid_3d_box)


def cylinder_3d_box(self):
    """
    Compact (lower-level) JSON formatting of a Cylinder3DBox.
    """
    face_color = self.face_color.to_js()
    if len(face_color) < 4 and self.face_opacity:
        face_color = face_color + [self.face_opacity.opacity]
    data = convert_coord_collection(
        [self.points],
        "cylinder",
        face_color,
        {"radius": self.radius},
    )
    # print("### json Cylinder3DBox", data)
    return data


add_conversion_fn(Cylinder3DBox, cylinder_3d_box)


def line_3d_box(self):
    """
    Compact (lower-level) JSON formatting of a Line3DBox.
    """
    # TODO: account for line widths and style
    color = self.edge_color.to_rgba()
    if len(color) < 4 and self.edge_opacity:
        color = color + [self.edge_opacity.opacity]
    data = convert_coord_collection(self.lines, "line", color)
    # print("### json Line3DBox", data)
    return data


add_conversion_fn(Line3DBox, line_3d_box)


def point_3d_box(self) -> list:
    """
    Compact (lower-level) JSON formatting of a Point3DBox.
    """
    # TODO: account for point size

    face_color = self.face_color.to_rgba()
    if len(face_color) < 4 and self.face_opacity:
        face_color = face_color + [self.face_opacity.opacity]

    point_size, _ = self.style.get_style(PointSize, face_element=False)
    relative_point_size = 0.01 if point_size is None else point_size.value

    data = convert_coord_collection(
        self.lines,
        "point",
        face_color,
        {"pointSize": relative_point_size * 0.5},
    )

    # print("### json Point3DBox", data)
    return data


add_conversion_fn(Point3DBox, point_3d_box)


def polygon_3d_box(self) -> list:
    """
    Compact (lower-level) JSON formatting of a Polygon3DBox.
    This format follows an API understood by mathics_threejs_backend.
    """
    # TODO: account for line widths and style
    if self.vertex_colors is None:
        face_color = self.face_color.to_js()
    else:
        face_color = None

    if face_color and len(face_color) < 4 and self.face_opacity:
        face_color = face_color + [self.face_opacity.opacity]
    data = convert_coord_collection(
        self.lines,
        "polygon",
        face_color,
    )
    # print("### json Polygon3DBox", data)
    return data


add_conversion_fn(Polygon3DBox, polygon_3d_box)


def sphere_3d_box(self) -> list:
    face_color = self.face_color.to_js()
    if len(face_color) < 4 and self.face_opacity:
        face_color = face_color + [self.face_opacity.opacity]
    data = convert_coord_collection(
        [self.points],
        "sphere",
        face_color,
        {"radius": self.radius},
    )
    # print("### json Sphere3DBox", data)
    return data


add_conversion_fn(Sphere3DBox, sphere_3d_box)


def uniform_polyhedron_3d_box(self) -> list:
    face_color = self.face_color.to_js()
    if len(face_color) < 4 and self.edge_opacity:
        face_color = face_color + [self.face_opacity.opacity]
    data = convert_coord_collection(
        [self.points],
        "uniformPolyhedron",
        face_color,
        {"subType": self.sub_type},
    )
    # print("### json UniformPolyhedron3DBox", data)
    return data


add_conversion_fn(UniformPolyhedron3DBox, uniform_polyhedron_3d_box)


def tube_3d_box(self) -> list:
    face_color = self.face_color
    if face_color is not None:
        face_color = face_color.to_js()
        if len(face_color) < 4 and self.edge_opacity:
            face_color = face_color + [self.face_opacity.opacity]
    data = convert_coord_collection(
        [self.points],
        "tube",
        face_color,
        {"radius": self.radius},
    )
    # print("### json Tube3DBox", data)
    return data


add_conversion_fn(Tube3DBox, tube_3d_box)
