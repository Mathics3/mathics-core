# -*- coding: utf-8 -*-
"""
Boxing Symbols for 3D Graphics
"""
# Docs are not yet ready for prime time. Maybe after release 6.0.0.
no_doc = True

import json
import numbers

from mathics.builtin.box.graphics import (
    ArrowBox,
    GraphicsBox,
    LineBox,
    PointBox,
    PolygonBox,
)
from mathics.builtin.colors.color_directives import Opacity, RGBColor, _ColorObject
from mathics.builtin.drawing.graphics3d import Coords3D, Graphics3DElements, Style3D
from mathics.builtin.drawing.graphics_internals import (
    GLOBALS3D,
    _GraphicsElementBox,
    get_class,
)
from mathics.core.exceptions import BoxExpressionError
from mathics.core.formatter import lookup_method
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.eval.nevaluator import eval_N


class Graphics3DBox(GraphicsBox):
    """
    <dl>
      <dt>'Graphics3DBox'
      <dd>is the symbol used in boxing 'Graphics3D' expressions.
    </dl>
    """

    summary_text = "symbol used boxing Graphics3D expresssions"

    def _prepare_elements(self, elements, options, max_width=None):
        if not elements:
            raise BoxExpressionError

        self.graphics_options = self.get_option_values(elements[1:], **options)

        background = self.graphics_options["System`Background"]
        if (
            isinstance(background, Symbol)
            and background.get_name() == "System`Automatic"
        ):
            self.background_color = None
        else:
            self.background_color = _ColorObject.create(background)

        evaluation = options["evaluation"]

        base_width, base_height, size_multiplier, size_aspect = self._get_image_size(
            options, self.graphics_options, max_width
        )

        # TODO: Handle ImageScaled[], and Scaled[]
        lighting_option = self.graphics_options["System`Lighting"]
        lighting = lighting_option.to_python()  # can take symbols or strings
        self.lighting = []

        if lighting == "System`Automatic":
            self.lighting = [
                {"type": "Ambient", "color": [0.3, 0.2, 0.4]},
                {
                    "type": "Directional",
                    "color": [0.8, 0.0, 0.0],
                    "position": [2, 0, 2],
                },
                {
                    "type": "Directional",
                    "color": [0.0, 0.8, 0.0],
                    "position": [2, 2, 2],
                },
                {
                    "type": "Directional",
                    "color": [0.0, 0.0, 0.8],
                    "position": [0, 2, 2],
                },
            ]
        elif lighting == "Neutral":  # Lighting->"Neutral"
            self.lighting = [
                {"type": "Ambient", "color": [0.3, 0.3, 0.3]},
                {
                    "type": "Directional",
                    "color": [0.3, 0.3, 0.3],
                    "position": [2, 0, 2],
                },
                {
                    "type": "Directional",
                    "color": [0.3, 0.3, 0.3],
                    "position": [2, 2, 2],
                },
                {
                    "type": "Directional",
                    "color": [0.3, 0.3, 0.3],
                    "position": [0, 2, 2],
                },
            ]
        elif lighting == "System`None":
            pass

        elif isinstance(lighting, list) and all(
            isinstance(light, list) for light in lighting
        ):
            for light in lighting:
                if light[0] in ['"Ambient"', '"Directional"', '"Point"', '"Spot"']:
                    try:
                        head = light[1].get_head_name()
                    except AttributeError:
                        break
                    color = get_class(head)(light[1])
                    if light[0] == '"Ambient"':
                        self.lighting.append(
                            {"type": "Ambient", "color": color.to_rgba()}
                        )
                    elif light[0] == '"Directional"':
                        position = [0, 0, 0]
                        if isinstance(light[2], list):
                            if len(light[2]) == 3:
                                position = light[2]
                            if len(light[2]) == 2 and all(  # noqa
                                isinstance(p, list) and len(p) == 3 for p in light[2]
                            ):
                                position = [
                                    light[2][0][i] - light[2][1][i] for i in range(3)
                                ]
                        self.lighting.append(
                            {
                                "type": "Directional",
                                "color": color.to_rgba(),
                                "position": position,
                            }
                        )
                    elif light[0] == '"Point"':
                        position = [0, 0, 0]
                        if isinstance(light[2], list) and len(light[2]) == 3:
                            position = light[2]
                        self.lighting.append(
                            {
                                "type": "Point",
                                "color": color.to_rgba(),
                                "position": position,
                            }
                        )
                    elif light[0] == '"Spot"':
                        position = [0, 0, 1]
                        target = [0, 0, 0]
                        if isinstance(light[2], list):
                            if len(light[2]) == 2:
                                if (
                                    isinstance(light[2][0], list)
                                    and len(light[2][0]) == 3  # noqa
                                ):
                                    position = light[2][0]
                                if (
                                    isinstance(light[2][1], list)
                                    and len(light[2][1]) == 3  # noqa
                                ):
                                    target = light[2][1]
                            if len(light[2]) == 3:
                                position = light[2]
                        angle = light[3]
                        self.lighting.append(
                            {
                                "type": "Spot",
                                "color": color.to_rgba(),
                                "position": position,
                                "target": target,
                                "angle": angle,
                            }
                        )

        else:
            evaluation.message("Graphics3D", "invlight", lighting_option)

        # ViewPoint Option
        viewpoint_option = self.graphics_options["System`ViewPoint"]
        viewpoint = eval_N(viewpoint_option, evaluation).to_python()

        if isinstance(viewpoint, list) and len(viewpoint) == 3:
            if all(isinstance(x, numbers.Real) for x in viewpoint):
                # TODO Infinite coordinates e.g. {0, 0, Infinity}
                pass
        else:
            try:
                viewpoint = {
                    "Above": [0, 0, 2],
                    "Below": [0, 0, -2],
                    "Front": [0, -2, 0],
                    "Back": [0, 2, 0],
                    "Left": [-2, 0, 0],
                    "Right": [2, 0, 0],
                }[viewpoint]
            except KeyError:
                # evaluation.message()
                # TODO
                viewpoint = [1.3, -2.4, 2]

        assert (
            isinstance(viewpoint, list)
            and len(viewpoint) == 3
            and all(isinstance(x, numbers.Real) for x in viewpoint)
        )
        self.viewpoint = viewpoint

        # TODO Aspect Ratio
        # aspect_ratio = self.graphics_options['AspectRatio'].to_python()

        boxratios = self.graphics_options["System`BoxRatios"].to_python()
        if boxratios == "System`Automatic":
            boxratios = ["System`Automatic"] * 3
        else:
            boxratios = boxratios
        if not isinstance(boxratios, list) or len(boxratios) != 3:
            raise BoxExpressionError

        plot_range = self.graphics_options["System`PlotRange"].to_python()
        if plot_range == "System`Automatic":
            plot_range = ["System`Automatic"] * 3
        if not isinstance(plot_range, list) or len(plot_range) != 3:
            raise BoxExpressionError

        elements = Graphics3DElements(elements[0], evaluation)

        def calc_dimensions(final_pass=True):
            if "System`Automatic" in plot_range:
                xmin, xmax, ymin, ymax, zmin, zmax = elements.extent()
            else:
                xmin = xmax = ymin = ymax = zmin = zmax = None

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
                    xmin = elements.translate((xmin, 0, 0))[0]
                    xmax = elements.translate((xmax, 0, 0))[0]
                else:
                    raise BoxExpressionError

                if plot_range[1] == "System`Automatic":
                    if ymin is None and ymax is None:
                        ymin = 0
                        ymax = 1
                    elif ymin == ymax:
                        ymin -= 1
                        ymax += 1
                elif isinstance(plot_range[1], list) and len(plot_range[1]) == 2:
                    ymin, ymax = list(map(float, plot_range[1]))
                    ymin = elements.translate((0, ymin, 0))[1]
                    ymax = elements.translate((0, ymax, 0))[1]
                else:
                    raise BoxExpressionError

                if plot_range[2] == "System`Automatic":
                    if zmin is None and zmax is None:
                        zmin = 0
                        zmax = 1
                    elif zmin == zmax:
                        zmin -= 1
                        zmax += 1
                elif isinstance(plot_range[1], list) and len(plot_range[1]) == 2:
                    zmin, zmax = list(map(float, plot_range[2]))
                    zmin = elements.translate((0, 0, zmin))[2]
                    zmax = elements.translate((0, 0, zmax))[2]
                else:
                    raise BoxExpressionError
            except (ValueError, TypeError):
                raise BoxExpressionError

            boxscale = [1.0, 1.0, 1.0]
            if boxratios[0] != "System`Automatic":
                boxscale[0] = boxratios[0] / (xmax - xmin)
            if boxratios[1] != "System`Automatic":
                boxscale[1] = boxratios[1] / (ymax - ymin)
            if boxratios[2] != "System`Automatic":
                boxscale[2] = boxratios[2] / (zmax - zmin)

            if final_pass:
                xmin *= boxscale[0]
                xmax *= boxscale[0]
                ymin *= boxscale[1]
                ymax *= boxscale[1]
                zmin *= boxscale[2]
                zmax *= boxscale[2]

                # Rescale lighting
                for i, light in enumerate(self.lighting):
                    if self.lighting[i]["type"] != "Ambient":
                        self.lighting[i]["position"] = [
                            light["position"][j] * boxscale[j] for j in range(3)
                        ]
                    if self.lighting[i]["type"] == "Spot":
                        self.lighting[i]["target"] = [
                            light["target"][j] * boxscale[j] for j in range(3)
                        ]

            w = 0 if (xmin is None or xmax is None) else xmax - xmin
            h = 0 if (ymin is None or ymax is None) else ymax - ymin

            return xmin, xmax, ymin, ymax, zmin, zmax, boxscale, w, h

        xmin, xmax, ymin, ymax, zmin, zmax, boxscale, w, h = calc_dimensions(
            final_pass=False
        )

        axes, ticks, ticks_style = self.create_axes(
            elements,
            self.graphics_options,
            xmin,
            xmax,
            ymin,
            ymax,
            zmin,
            zmax,
            boxscale,
        )

        return elements, axes, ticks, ticks_style, calc_dimensions, boxscale

    def boxes_to_js(self, elements=None, **options):
        """Turn the Graphics3DBox to into a something javascript-ish
        We include enclosing script tagging.
        """
        json_repr = self.boxes_to_json(elements, **options)
        js = f"<graphics3d data='{json_repr}'/>"
        return js

    def boxes_to_json(self, elements=None, **options):
        """Turn the Graphics3DBox to into a something JSON like.
        This can be used to embed in something else like MathML or Javascript.

        In contrast to to javascript or MathML, no enclosing tags are included.
        the caller will do that if it is needed.
        """
        if not elements:
            elements = self._elements

        (
            elements,
            axes,
            ticks,
            ticks_style,
            calc_dimensions,
            boxscale,
        ) = self._prepare_elements(elements, options)

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
                "lighting": self.lighting,
                "viewpoint": self.viewpoint,
                "protocol": "1.1",
            }
        )

        return json_repr

    def create_axes(
        self, elements, graphics_options, xmin, xmax, ymin, ymax, zmin, zmax, boxscale
    ):
        axes = graphics_options.get("System`Axes")
        if axes is SymbolTrue:
            axes = (True, True, True)
        elif axes.has_form("List", 3):
            axes = (element is SymbolTrue for element in axes.elements)
        else:
            axes = (False, False, False)
        ticks_style = graphics_options.get("System`TicksStyle")
        axes_style = graphics_options.get("System`AxesStyle")
        label_style = graphics_options.get("System`LabelStyle")

        # FIXME: Doesn't handle GrayScale
        if ticks_style.has_form("List", 1, 2, 3):
            ticks_style = ticks_style.elements
        elif ticks_style.has_form("RGBColor", None):
            ticks_style = [ticks_style] * 3
        else:
            ticks_style = []

        if axes_style.has_form("List", 1, 2, 3):
            axes_style = axes_style.elements
        else:
            axes_style = [axes_style] * 3

        # FIXME: Not quite right. We only handle color
        ticks_style = [
            elements.create_style(s).get_style(_ColorObject, face_element=False)[0]
            for s in ticks_style
        ]

        axes_style = [elements.create_style(s) for s in axes_style]
        label_style = elements.create_style(label_style)

        # For later
        # ticks_style[0].extend(axes_style[0])
        # ticks_style[1].extend(axes_style[1])
        # ticks_style[2].extend(axes_style[2])

        ticks = [
            self.axis_ticks(xmin, xmax),
            self.axis_ticks(ymin, ymax),
            self.axis_ticks(zmin, zmax),
        ]

        # Add zero if required, since axis_ticks does not
        if xmin <= 0 <= xmax:
            ticks[0][0].append(0.0)
        if ymin <= 0 <= ymax:
            ticks[1][0].append(0.0)
        if zmin <= 0 <= zmax:
            ticks[2][0].append(0.0)

        # Convert ticks to nice strings e.g 0.100000000000002 -> '0.1' and
        # scale ticks appropriately
        ticks = [
            [
                [boxscale[i] * x for x in t[0]],
                [boxscale[i] * x for x in t[1]],
                ["%g" % x for x in t[0]],
            ]
            for i, t in enumerate(ticks)
        ]

        return axes, ticks, ticks_style

    def get_boundbox_lines(self, xmin, xmax, ymin, ymax, zmin, zmax):
        return [
            [(xmin, ymin, zmin), (xmax, ymin, zmin)],
            [(xmin, ymax, zmin), (xmax, ymax, zmin)],
            [(xmin, ymin, zmax), (xmax, ymin, zmax)],
            [(xmin, ymax, zmax), (xmax, ymax, zmax)],
            [(xmin, ymin, zmin), (xmin, ymax, zmin)],
            [(xmax, ymin, zmin), (xmax, ymax, zmin)],
            [(xmin, ymin, zmax), (xmin, ymax, zmax)],
            [(xmax, ymin, zmax), (xmax, ymax, zmax)],
            [(xmin, ymin, zmin), (xmin, ymin, zmax)],
            [(xmax, ymin, zmin), (xmax, ymin, zmax)],
            [(xmin, ymax, zmin), (xmin, ymax, zmax)],
            [(xmax, ymax, zmin), (xmax, ymax, zmax)],
        ]


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

        points = item.elements[0].to_python()
        if not all(
            len(point) == 3 and all(isinstance(p, numbers.Real) for p in point)
            for point in points
        ):
            raise BoxExpressionError

        self.points = tuple(Coords3D(graphics, pos=point) for point in points)
        self.radius = item.elements[1].to_python()

    def extent(self):
        result = []
        # FIXME: the extent is roughly wrong. It is using the extent of a shpere at each coordinate.
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

        points = item.elements[0].to_python()
        if not all(
            len(point) == 3 and all(isinstance(p, numbers.Real) for p in point)
            for point in points
        ):
            raise BoxExpressionError

        self.points = tuple(Coords3D(pos=point) for point in points)

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

        points = item.elements[0].to_python()
        if not all(
            len(point) == 3 and all(isinstance(p, numbers.Real) for p in point)
            for point in points
        ):
            raise BoxExpressionError

        self.points = tuple(Coords3D(pos=point) for point in points)
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

        points = item.elements[0].to_python()
        if not all(isinstance(point, list) for point in points):
            points = [points]
        if not all(
            len(point) == 3 and all(isinstance(p, numbers.Real) for p in point)
            for point in points
        ):
            raise BoxExpressionError

        self.points = tuple(Coords3D(pos=point) for point in points)
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
        points = item.elements[0].to_python()
        if not all(
            len(point) == 3 and all(isinstance(p, numbers.Real) for p in point)
            for point in points
        ):
            raise BoxExpressionError

        self.points = [Coords3D(graphics, pos=point) for point in points]
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
