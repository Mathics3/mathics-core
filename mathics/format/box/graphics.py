# -*- coding: utf-8 -*-
"""
Boxing Symbols for 2D Graphics
"""
import logging
from math import ceil, floor, log10
from typing import Any, List, Optional, Tuple

from mathics.builtin.colors.color_directives import ColorError, RGBColor, _ColorObject
from mathics.builtin.drawing.graphics_internals import get_class
from mathics.builtin.graphics import (
    ELEMENT_HEADS,
    GRAPHICS_SYMBOLS,
    STYLE_AND_FORM_HEADS,
    STYLE_HEADS,
    AbsoluteThickness,
    _Thickness,
)
from mathics.core.atoms import Integer, Real, String
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.element import BaseElement, BoxElementMixin
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import BoxExpressionError
from mathics.core.expression import Expression
from mathics.core.formatter import lookup_method
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolList,
    SymbolNull,
    SymbolTrue,
    system_symbols_dict,
)
from mathics.core.systemsymbols import (
    SymbolAutomatic,
    SymbolEdgeForm,
    SymbolFaceForm,
    SymbolGraphics,
    SymbolInset,
    SymbolStyle,
    SymbolText,
)
from mathics.eval.nevaluator import eval_N
from mathics.format.box.makeboxes import eval_makeboxes

SymbolRegularPolygonBox = Symbol("RegularPolygonBox")

ERROR_BACKGROUND_COLOR = RGBColor(components=[1, 0.3, 0.3, 0.25])


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
                edge_style = AbsoluteThickness(self.graphics, value=1.6)
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

    def get_line_width(self, face_element=True) -> float:
        if self.graphics.pixel_width is None:
            return 0.0
        edge_style, _ = self.get_style(
            _Thickness, default_to_faces=face_element, consider_forms=face_element
        )
        if edge_style is None:
            return 0.0
        return edge_style.get_thickness() / 2.0


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
                if head in STYLE_AND_FORM_HEADS:
                    new_style.append(spec)
                elif head is Symbol("System`Rule") and len(spec.elements) == 2:
                    option, expr = spec.elements
                    if not isinstance(option, Symbol):
                        raise BoxExpressionError

                    name = option.get_name()
                    create = STYLE_OPTIONS.get(name, None)
                    if create is None:
                        raise BoxExpressionError

                    new_style.set_option(name, create(style.graphics, expr))
                else:
                    raise BoxExpressionError
            return new_style

        failed = []

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
                if head in STYLE_AND_FORM_HEADS:
                    try:
                        style.append(item)
                    except ColorError:
                        failed.append(head)
                elif head is Symbol("System`StyleBox"):
                    if len(item.elements) < 1:
                        failed.append(item.head)
                    for element in convert(
                        item.elements[0], stylebox_style(style, item.elements[1:])
                    ):
                        yield element
                elif head.name[-3:] == "Box":  # and head[:-3] in element_heads:
                    element_class = get_class(head)
                    if element_class is None:
                        failed.append(head)
                        continue
                    options = get_options(head.name[:-3])
                    if options:
                        data, options = _data_and_options(item.elements, options)
                        new_item = Expression(head, *data)
                        try:
                            element = element_class(self, style, new_item, options)
                        except (BoxExpressionError, CoordinatesError):
                            failed.append(head)
                            continue
                    else:
                        try:
                            element = element_class(self, style, item)
                        except (BoxExpressionError, CoordinatesError):
                            failed.append(head)
                            continue
                    yield element
                elif head is SymbolList:
                    for element in convert(item, style):
                        yield element
                else:
                    failed.append(head)
                    continue

            # if failed:
            #    yield build_error_box2(style)
            #    raise BoxExpressionError(messages)

        self.elements = list(convert(content, self.style_class(self)))
        if failed:
            messages = "\n".join(
                [f"{str(h)} is not a valid primitive or directive." for h in failed]
            )
            self.tooltip_text = messages
            self.background_color = ERROR_BACKGROUND_COLOR
            logging.warning(messages)

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


class CoordinatesError(BoxExpressionError):
    pass


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
    graphics_box = eval_makeboxes(graphics, evaluation)
    # builtin = GraphicsBox(expression=False)
    elements, calc_dimensions = prepare_elements(
        graphics_box, graphics_box.content, {"_evaluation": evaluation}, neg_y=True
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


def _style(graphics, item):
    head = item.get_head()
    if head in STYLE_HEADS:
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


def coords(value):
    if value.has_form("List", 2):
        x, y = value.elements[0].round_to_float(), value.elements[1].round_to_float()
        if x is None or y is None:
            raise CoordinatesError
        return (x, y)
    raise CoordinatesError


def cut(value):
    "Cut values in graphics primitives (not displayed otherwise in SVG)"
    border = 10**8
    if value < -border:
        value = -border
    elif value > border:
        value = border
    return value


# FIXME: this doesn't always properly align with overlaid SVG plots
def axis_ticks(xmin: float, xmax: float) -> Tuple[List[float], List[float], int]:
    """
    Compute the positions of the axis ticks
    """

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


def create_axes(self, elements, graphics_options, xmin, xmax, ymin, ymax) -> tuple:
    # Note that Asymptote has special commands for drawing axes, like "xaxis"
    # "yaxis", "xtick" "labelx", "labely". Extend our language
    # here and use those in render-like routines.
    from mathics.builtin.box.graphics import InsetBox, LineBox

    use_log_for_y_axis = graphics_options.get("System`LogPlot", SymbolFalse).to_python()
    axes_option = graphics_options.get("System`Axes")

    if axes_option is SymbolTrue:
        axes = (True, True)
    elif axes_option.has_form("List", 2):
        axes = (
            axes_option.elements[0] is SymbolTrue,
            axes_option.elements[1] is SymbolTrue,
        )
    else:
        axes = (False, False)

    # The Style option pushes its setting down into graphics components
    # like ticks, axes, and labels.
    ticks_style_option = graphics_options.get("System`TicksStyle")
    axes_style_option = graphics_options.get("System`AxesStyle")
    label_style = graphics_options.get("System`LabelStyle")

    if ticks_style_option.has_form("List", 2):
        ticks_style = ticks_style_option.elements
    else:
        ticks_style = [ticks_style_option] * 2

    if axes_style_option.has_form("List", 2):
        axes_style = axes_style_option.elements
    else:
        axes_style = [axes_style_option] * 2

    ticks_style = [elements.create_style(s) for s in ticks_style]
    axes_style = [elements.create_style(s) for s in axes_style]
    label_style = elements.create_style(label_style)
    ticks_style[0].extend(axes_style[0])
    ticks_style[1].extend(axes_style[1])

    def add_element(element):
        element.is_completely_visible = True
        elements.elements.append(element)

    # Units seem to be in point size units

    ticks_x, ticks_x_small, origin_x = axis_ticks(xmin, xmax)
    ticks_y, ticks_y_small, origin_y = axis_ticks(ymin, ymax)

    axes_extra = 6

    tick_small_size = 3
    tick_large_size = 5

    tick_label_d = 2

    ticks_x_int = all(floor(x) == x for x in ticks_x)
    ticks_y_int = all(floor(x) == x for x in ticks_y)

    for (
        index,
        (
            min,
            max,
            p_self0,
            p_other0,
            p_origin,
            ticks,
            ticks_small,
            ticks_int,
            is_logscale,
        ),
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
                False,
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
                use_log_for_y_axis,
            ),
        ]
    ):
        # Where should the placement of tick mark labels go?
        if index == 0:
            # x labels go under tick marks
            alignment = "bottom"
        elif index == 1:
            # y labels go to the left of tick marks
            alignment = "left"
        else:
            alignment = None

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
                            Coords(elements, pos=p_origin(max), d=p_other0(axes_extra)),
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
                        Coords(elements, pos=p_origin(x), d=p_self0(tick_large_size)),
                    ]
                )

                # FIXME: for log plots we labels should appear
                # as 10^x rather than say 1000000.
                tick_value = 10**x if is_logscale else x
                if ticks_int:
                    content = String(str(int(tick_value)))
                elif tick_value == floor(x):
                    content = String("%.1f" % tick_value)  # e.g. 1.0 (instead of 1.)
                else:
                    content = String("%g" % tick_value)  # fix e.g. 0.6000000000000001

                add_element(
                    InsetBox(
                        elements,
                        tick_label_style,
                        content=content,
                        pos=Coords(elements, pos=p_origin(x), d=p_self0(-tick_label_d)),
                        opos=p_self0(1),
                        opacity=1.0,
                        alignment=alignment,
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

    # Old code?
    # if axes[1]:
    #     add_element(LineBox(elements, axes_style[1], lines=[[Coords(elements, pos=(origin_x,ymin), d=(0,-axes_extra)),
    #         Coords(elements, pos=(origin_x,ymax), d=(0,axes_extra))]]))
    #     ticks = []
    #     tick_label_style = ticks_style[1].clone()
    #     tick_label_style.extend(label_style)
    #     for k in range(start_k_y, start_k_y+steps_y+1):
    #         if k != origin_k_y:
    #             y = k * step_y
    #             if y > ymax:
    #                 break
    #             pos = (origin_x,y)
    #             ticks.append([Coords(elements, pos=pos),
    #                 Coords(elements, pos=pos, d=(tick_large_size,0))])
    #             add_element(InsetBox(elements, tick_label_style, content=Real(y), pos=Coords(elements, pos=pos,
    #                 d=(-tick_label_d,0)), opos=(1,0)))
    #     for k in range(start_k_y_small, start_k_y_small+steps_y_small+1):
    #         if k % sub_y != 0:
    #             y = k * step_y_small
    #             if y > ymax:
    #                 break
    #             pos = (origin_x,y)
    #             ticks.append([Coords(elements, pos=pos),
    #                 Coords(elements, pos=pos, d=(tick_small_size,0))])
    #     add_element(LineBox(elements, axes_style[1], lines=ticks))


def get_image_size(
    options: dict, graphics_options: dict, max_width
) -> Tuple[Optional[int], Optional[int], Any, Any]:
    base_width: Optional[int]
    base_height: Optional[int]
    image_size_multipliers: Optional[Tuple[float, float]]

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
            raise BoxExpressionError
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
        raise BoxExpressionError
    if max_width is not None and base_width > max_width:
        base_width = max_width

    if inside_row:
        multi = image_size_multipliers[1]
    elif inside_list:
        multi = image_size_multipliers[0]
    else:
        multi = 1

    return base_width, base_height, multi, aspect


def prepare_elements(self, content, options, neg_y=False, max_width=None):
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
            pass

    base_width, base_height, size_multiplier, size_aspect = get_image_size(
        options, graphics_options, max_width
    )

    plot_range = graphics_options["System`PlotRange"].to_python()
    if plot_range == "System`Automatic":
        plot_range = ["System`Automatic", "System`Automatic"]

    if not isinstance(plot_range, list) or len(plot_range) != 2:
        raise BoxExpressionError

    evaluation = options.get("_evaluation", None)
    if evaluation is None:
        evaluation = self.evaluation
    elements = GraphicsElements(content, evaluation, neg_y)
    if hasattr(elements, "background_color"):
        self.background_color = elements.background_color
    if hasattr(elements, "tooltip_text"):
        self.tooltip_text = elements.tooltip_text

    axes = []  # to be filled further down

    def calc_dimensions(final_pass=True):
        """
        calc_dimensions gets called twice: In the first run
        (final_pass = False, called inside prepare_elements), the extent
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
            exmin, exmax, eymin, eymax = elements.extent(completely_visible_only=True)
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
                raise BoxExpressionError
        except (ValueError, TypeError):
            raise BoxExpressionError

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

        width *= size_multiplier
        height *= size_multiplier

        return xmin, xmax, ymin, ymax, w, h, width, height

    xmin, xmax, ymin, ymax, w, h, width, height = calc_dimensions(final_pass=False)

    elements.set_size(xmin, ymin, w, h, width, height)

    xmin -= w * 0.02
    xmax += w * 0.02
    ymin -= h * 0.02
    ymax += h * 0.02

    axes.extend(create_axes(self, elements, graphics_options, xmin, xmax, ymin, ymax))

    return elements, calc_dimensions


def primitives_to_boxes(
    content: BaseElement, evaluation: Evaluation, box_suffix: str = "Box"
) -> ListExpression | BoxElementMixin:
    """
    Convert a primitive into the corresponding
    box expression.
    If `content` is a ListExpression containing primitives, return a
    ListExpression of the corresponding BoxElements.
    """

    head = content.get_head()

    if head is SymbolList:
        return to_mathics_list(
            *content.elements,
            elements_conversion_fn=lambda item: primitives_to_boxes(
                item, evaluation, box_suffix
            ),
        )
    elif head is SymbolStyle:
        return to_expression(
            "StyleBox",
            *[
                primitives_to_boxes(item, evaluation, box_suffix)
                for item in content.elements
            ],
        )

    if head in ELEMENT_HEADS:
        if head is SymbolText:
            head = SymbolInset
        atoms = content.get_atoms(include_heads=False)
        if any(
            not isinstance(atom, (Integer, Real)) and atom not in GRAPHICS_SYMBOLS
            for atom in atoms
        ):
            if head is SymbolInset:
                inset = content.elements[0]
                if inset.get_head() is SymbolGraphics:
                    inset = eval_makeboxes(inset.elements[0], evaluation)
                n_elements = [inset] + [
                    eval_N(element, evaluation) for element in content.elements[1:]
                ]
            else:
                n_elements = (
                    eval_N(element, evaluation) for element in content.elements
                )
        else:
            n_elements = content.elements
        return Expression(Symbol(head.name + box_suffix), *n_elements)
    return content


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


STYLE_OPTIONS = system_symbols_dict(
    {"FontColor": _style, "ImageSizeMultipliers": (lambda *x: x[1])}
)
