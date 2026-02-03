# -*- coding: utf-8 -*-
"""
Boxing Symbols for 3D Graphics
"""


from mathics.builtin.box.graphics import (
    ArrowBox,
    GraphicsBox,
    LineBox,
    PointBox,
    PolygonBox,
    _GraphicsElementBox,
)
from mathics.builtin.colors.color_directives import Opacity, RGBColor, _ColorObject
from mathics.builtin.drawing.graphics3d import Graphics3D, Style3D
from mathics.builtin.drawing.graphics_internals import GLOBALS3D
from mathics.core.exceptions import BoxExpressionError
from mathics.core.symbols import Symbol
from mathics.format.box.graphics3d import expr_to_list_of_3d_points

# No user docs here - Box primitives aren't documented.
no_doc = True


class Graphics3DBox(GraphicsBox):
    """
    <dl>
      <dt>'Graphics3DBox'
      <dd>is the symbol used in boxing 'Graphics3D' expressions.
    </dl>
    """

    options = Graphics3D.options
    summary_text = "symbol used boxing Graphics3D expressions"

    def init(self, *items, **kwargs):
        super().init(*items, **kwargs)
        self.lighting = []
        self.viewpoint = [1.3, -2.4, 2]

    def _prepare_elements(self, elements, options, max_width=None):
        from mathics.format.box.graphics3d import prepare_elements

        return prepare_elements(self, elements, options, max_width)

    def boxes_to_js(self, elements=None, **options):
        """Turn the Graphics3DBox to into a something javascript-ish
        We include enclosing script tagging.
        """
        from mathics.format.render.json import graphics3d_boxes_to_json

        json_repr = graphics3d_boxes_to_json(self, elements, **options)
        js = f"<graphics3d data='{json_repr}'/>"
        return js


class Arrow3DBox(ArrowBox):
    # We have no documentation for this (yet).
    no_doc = True

    def init(self, *args, **kwargs):
        super(Arrow3DBox, self).init(*args, **kwargs)

    def process_option(self, name, value):
        super(Arrow3DBox, self).process_option(name, value)

    def extent(self):
        result = [coordinate.pos()[0] for line in self.lines for coordinate in line]
        return result

    def _apply_boxscaling(self, boxscale):
        for line in self.lines:
            for coords in line:
                coords.scale(boxscale)


class Cone3DBox(_GraphicsElementBox):
    # """
    # Internal Python class used when Boxing a 'Cone' object.
    # """

    # We have no documentation for this (yet).
    no_doc = True

    def init(self, graphics, style, item):
        self.edge_color, self.face_color = style.get_style(
            _ColorObject, face_element=True
        )
        self.edge_opacity, self.face_opacity = style.get_style(
            Opacity, face_element=True
        )
        if len(item.elements) != 2:
            raise BoxExpressionError

        self.points = expr_to_list_of_3d_points(item.elements[0])
        self.radius = item.elements[1].to_python()

    def extent(self):
        result = []
        # FIXME: the extent is roughly wrong. It is using the extent of a sphere at each coordinate.
        # Anyway, it is very difficult to calculate the extent of a cone.
        result.extend(
            [
                coords.add(self.radius, self.radius, self.radius).pos()[0]
                for coords in self.points
            ]
        )
        result.extend(
            [
                coords.add(-self.radius, -self.radius, -self.radius).pos()[0]
                for coords in self.points
            ]
        )
        return result

    def _apply_boxscaling(self, boxscale):
        # TODO
        pass


class Cuboid3DBox(_GraphicsElementBox):
    # """
    # Internal Python class used when Boxing a 'Cuboid' object.
    # """

    # We have no documentation for this (yet).
    no_doc = True

    def init(self, graphics, style, item):
        self.edge_color, self.face_color = style.get_style(
            _ColorObject, face_element=True
        )
        self.edge_opacity, self.face_opacity = style.get_style(
            Opacity, face_element=True
        )
        if len(item.elements) != 1:
            raise BoxExpressionError

        self.points = expr_to_list_of_3d_points(item.elements[0])

    def extent(self):
        return [coords.pos()[0] for coords in self.points]

    def _apply_boxscaling(self, boxscale):
        # TODO
        pass


class Cylinder3DBox(_GraphicsElementBox):
    # """
    # Internal Python class used when Boxing a 'Cylinder' object.
    # """

    # We have no documentation for this (yet).
    no_doc = True

    def init(self, graphics, style, item):
        self.edge_color, self.face_color = style.get_style(
            _ColorObject, face_element=True
        )
        self.edge_opacity, self.face_opacity = style.get_style(
            Opacity, face_element=True
        )
        if len(item.elements) != 2:
            raise BoxExpressionError

        self.points = expr_to_list_of_3d_points(item.elements[0])
        self.radius = item.elements[1].to_python()

    def extent(self):
        result = []
        # FIXME: instead of `coords.add(±self.radius, ±self.radius, ±self.radius)` we should do:
        # coords.add(transformation_vector.x * ±self.radius, transformation_vector.y * ±self.radius, transformation_vector.z * ±self.radius)
        result.extend(
            [
                coords.add(self.radius, self.radius, self.radius).pos()[0]
                for coords in self.points
            ]
        )
        result.extend(
            [
                coords.add(-self.radius, -self.radius, -self.radius).pos()[0]
                for coords in self.points
            ]
        )
        return result

    def _apply_boxscaling(self, boxscale):
        # TODO
        pass


class Line3DBox(LineBox):
    # summary_text = "box representation for a 3D line"

    # We have no documentation for this (yet).
    no_doc = True

    def init(self, *args, **kwargs):
        super(Line3DBox, self).init(*args, **kwargs)

    def process_option(self, name, value):
        super(Line3DBox, self).process_option(name, value)

    def extent(self):
        result = [coordinate.pos()[0] for line in self.lines for coordinate in line]
        return result

    def _apply_boxscaling(self, boxscale):
        for line in self.lines:
            for coords in line:
                coords.scale(boxscale)


class Point3DBox(PointBox):
    # summary_text = "box representation for a 3D point"

    # We have no documentation for this (yet).
    no_doc = True

    def get_default_face_color(self):
        return RGBColor(components=(0, 0, 0, 1))

    def init(self, *args, **kwargs):
        # The default color isn't white as it's for the other 3d primitives
        # here it's black.
        get_default_face_color_copy = Style3D.get_default_face_color

        Style3D.get_default_face_color = self.get_default_face_color
        super(Point3DBox, self).init(*args, **kwargs)
        Style3D.get_default_face_color = get_default_face_color_copy

    def process_option(self, name, value):
        super(Point3DBox, self).process_option(name, value)

    def extent(self):
        result = [coordinate.pos()[0] for line in self.lines for coordinate in line]
        return result

    def _apply_boxscaling(self, boxscale):
        for line in self.lines:
            for coords in line:
                coords.scale(boxscale)


class Polygon3DBox(PolygonBox):
    # summary_text = "box representation for a 3D polygon"

    # We have no documentation for this (yet).
    no_doc = True

    def init(self, *args, **kwargs):
        self.vertex_normals = None
        super(Polygon3DBox, self).init(*args, **kwargs)

    def process_option(self, name, value):
        if name == "System`VertexNormals":
            # TODO: process VertexNormals and use them in rendering
            pass
        else:
            super(Polygon3DBox, self).process_option(name, value)

    def extent(self):
        result = [coordinate.pos()[0] for line in self.lines for coordinate in line]
        return result

    def _apply_boxscaling(self, boxscale):
        for line in self.lines:
            for coords in line:
                coords.scale(boxscale)


class Sphere3DBox(_GraphicsElementBox):
    # summary_text = "box representation for a sphere"

    # We have no documentation for this (yet).
    no_doc = True

    def init(self, graphics, style, item):
        self.edge_color, self.face_color = style.get_style(
            _ColorObject, face_element=True
        )
        self.edge_opacity, self.face_opacity = style.get_style(
            Opacity, face_element=True
        )
        if len(item.elements) != 2:
            raise BoxExpressionError

        self.points = expr_to_list_of_3d_points(item.elements[0])
        self.radius = item.elements[1].to_python()

    def extent(self):
        result = []
        result.extend(
            [
                coords.add(self.radius, self.radius, self.radius).pos()[0]
                for coords in self.points
            ]
        )
        result.extend(
            [
                coords.add(-self.radius, -self.radius, -self.radius).pos()[0]
                for coords in self.points
            ]
        )
        return result

    def _apply_boxscaling(self, boxscale):
        # TODO
        pass


class Tube3DBox(_GraphicsElementBox):
    # summary_text = "box representation for a tube"

    # We have no documentation for this (yet).
    no_doc = True

    def init(self, graphics, style, item):
        self.graphics = graphics
        self.edge_color, self.face_color = style.get_style(
            _ColorObject, face_element=True
        )
        self.edge_opacity, self.face_opacity = style.get_style(
            Opacity, face_element=True
        )
        self.points = expr_to_list_of_3d_points(item.elements[0])
        self.radius = item.elements[1].to_python()

    def extent(self):
        result = []
        result.extend(
            [
                coords.add(self.radius, self.radius, self.radius).pos()[0]
                for coords in self.points
            ]
        )
        result.extend(
            [
                coords.add(-self.radius, -self.radius, -self.radius).pos()[0]
                for coords in self.points
            ]
        )
        return result

    def _apply_boxscaling(self, boxscale):
        # TODO
        pass


# FIXME: GLOBALS3D is a horrible name.
GLOBALS3D.update(
    {
        Symbol("Arrow3DBox"): Arrow3DBox,
        Symbol("Cone3DBox"): Cone3DBox,
        Symbol("Cuboid3DBox"): Cuboid3DBox,
        Symbol("Cylinder3DBox"): Cylinder3DBox,
        Symbol("Line3DBox"): Line3DBox,
        Symbol("Point3DBox"): Point3DBox,
        Symbol("Polygon3DBox"): Polygon3DBox,
        Symbol("Sphere3DBox"): Sphere3DBox,
        Symbol("Tube3DBox"): Tube3DBox,
    }
)
