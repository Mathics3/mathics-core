# -*- coding: utf-8 -*-
"""
Boxing Symbols for 3D Graphics
"""

import logging
import numbers
from typing import Tuple

from mathics.builtin.colors.color_directives import ColorError, _ColorObject
from mathics.builtin.drawing.graphics3d import Coords3D, Graphics3DElements
from mathics.builtin.drawing.graphics_internals import get_class
from mathics.core.element import BaseElement
from mathics.core.exceptions import BoxExpressionError
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.eval.nevaluator import eval_N
from mathics.format.box.graphics import axis_ticks, get_image_size


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
        axis_ticks(xmin, xmax),
        axis_ticks(ymin, ymax),
        axis_ticks(zmin, zmax),
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


def expr_to_list_of_3d_points(expr: BaseElement) -> Tuple[Coords3D, ...]:
    points = expr.to_python()
    if not all(isinstance(point, (tuple, list)) for point in points):
        points = [points]
    if not all(
        len(point) == 3 and all(isinstance(p, numbers.Real) for p in point)
        for point in points
    ):
        raise BoxExpressionError
    return tuple(Coords3D(pos=point) for point in points)


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


def prepare_elements(self, content, options, max_width=None):
    if not content:
        raise BoxExpressionError

    graphics_options = self.box_options.copy()
    graphics_options.update(options)

    background = graphics_options["System`Background"]
    if isinstance(background, Symbol) and background.get_name() == "System`Automatic":
        self.background_color = None
    else:
        try:
            self.background_color = _ColorObject.create(background)
        except ColorError:
            logging.warning(f"{str(background)} is not a valid color spec.")
            self.background_color = None

    evaluation = options.get("_evaluation", self.evaluation)

    base_width, base_height, size_multiplier, size_aspect = get_image_size(
        options, graphics_options, max_width
    )

    # TODO: Handle ImageScaled[], and Scaled[]
    lighting_option = graphics_options["System`Lighting"]
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
                    self.lighting.append({"type": "Ambient", "color": color.to_rgba()})
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
    viewpoint_option = graphics_options["System`ViewPoint"]
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

    boxratios = graphics_options["System`BoxRatios"].to_python()
    if boxratios == "System`Automatic":
        boxratios = ["System`Automatic"] * 3

    if not isinstance(boxratios, list) or len(boxratios) != 3:
        raise BoxExpressionError

    plot_range = graphics_options["System`PlotRange"].to_python()
    if plot_range == "System`Automatic":
        plot_range = ["System`Automatic"] * 3
    if not isinstance(plot_range, list) or len(plot_range) != 3:
        raise BoxExpressionError

    elements = Graphics3DElements(content, evaluation)
    # If one of the primitives or directives fails to be
    # converted into a box expression, then the background color
    # is set to pink, overwriting the options.
    if hasattr(elements, "background_color"):
        self.background_color = elements.background_color

    def calc_dimensions(final_pass=True):
        # TODO: the code below is broken in any other case but Automatic
        # because it calls elements.translate which is not implemented.
        # Plots may pass specific plot ranges, triggering this deficiency
        # and causing tests to fail The following line avoids this,
        # and it should not change the behavior of any case which did
        # previously fail with an exception.
        #
        # This code should be DRYed (together with the very similar code
        # for the 2d case), and the missing .translate method added.
        plot_range = ["System`Automatic"] * 3

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
            elif isinstance(plot_range[1], list) and len(plot_range[2]) == 2:
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

    axes, ticks, ticks_style = create_axes(
        self,
        elements,
        graphics_options,
        xmin,
        xmax,
        ymin,
        ymax,
        zmin,
        zmax,
        boxscale,
    )

    return elements, axes, ticks, ticks_style, calc_dimensions, boxscale
