# -*- coding: utf-8 -*-
"""
Plotting Data

Plotting functions take a function as a parameter and data, often a range of \
points, as another parameter, and plot or show the function applied to the data.
"""

import itertools
import numbers
from functools import lru_cache
from math import cos, pi, sin, sqrt
from typing import Callable, Optional

import palettable

from mathics.builtin.base import Builtin
from mathics.builtin.drawing.graphics3d import Graphics3D
from mathics.builtin.graphics import Graphics
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Integer, Integer0, Integer1, MachineReal, Real, String
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED, A_READ_PROTECTED
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolList, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolBlend,
    SymbolColorData,
    SymbolEdgeForm,
    SymbolFunction,
    SymbolGraphics,
    SymbolGraphics3D,
    SymbolGrid,
    SymbolLine,
    SymbolLog10,
    SymbolMap,
    SymbolPolygon,
    SymbolRGBColor,
    SymbolRow,
    SymbolRule,
    SymbolSlot,
    SymbolStyle,
)
from mathics.eval.nevaluator import eval_N
from mathics.eval.plot import (
    compile_quiet_function,
    eval_ListPlot,
    eval_Plot,
    get_plot_range,
)

# This tells documentation how to sort this module
# Here we are also hiding "drawing" since this erroneously appears at the top level.
sort_order = "mathics.builtin.plotting-data"

SymbolColorDataFunction = Symbol("ColorDataFunction")
SymbolDisk = Symbol("Disk")
SymbolFaceForm = Symbol("FaceForm")
SymbolRectangle = Symbol("Rectangle")
SymbolText = Symbol("Text")

TwoTenths = Real(0.2)
MTwoTenths = -TwoTenths


# PlotRange Option
def check_plot_range(range, range_type) -> bool:
    """
    Return True if `range` has two numbers, the first number less than the second number,
    and that both numbers have type `range_type`
    """
    if range in ("System`Automatic", "System`All"):
        return True
    if isinstance(range, list) and len(range) == 2:
        if isinstance(range[0], range_type) and isinstance(range[1], range_type):
            return True
    return False


def gradient_palette(
    color_function, n, evaluation: Evaluation
):  # always returns RGB values
    if isinstance(color_function, String):
        color_data = Expression(SymbolColorData, color_function).evaluate(evaluation)
        if not color_data.has_form("ColorDataFunction", 4):
            return
        name, kind, interval, blend = color_data.elements
        if not isinstance(kind, String) or kind.get_string_value() != "Gradients":
            return
        if not interval.has_form("List", 2):
            return
        x0, x1 = (x.round_to_float() for x in interval.elements)
    else:
        blend = color_function
        x0 = 0.0
        x1 = 1.0

    xd = x1 - x0
    offsets = [MachineReal(x0 + float(xd * i) / float(n - 1)) for i in range(n)]
    colors = Expression(SymbolMap, blend, ListExpression(*offsets)).evaluate(evaluation)
    if len(colors.elements) != n:
        return

    from mathics.builtin.colors.color_directives import ColorError, expression_to_color

    try:
        objects = [expression_to_color(x) for x in colors.elements]
        if any(x is None for x in objects):
            return None
        return [x.to_rgba()[:3] for x in objects]
    except ColorError:
        return


class _Chart(Builtin):
    attributes = A_HOLD_ALL | A_PROTECTED
    never_monochrome = False
    options = Graphics.options.copy()
    options.update(
        {
            "Mesh": "None",
            "PlotRange": "Automatic",
            "ChartLabels": "None",
            "ChartLegends": "None",
            "ChartStyle": "Automatic",
        }
    )

    def _draw(self, data, color, evaluation: Evaluation, options: dict):
        raise NotImplementedError()

    def eval(self, points, evaluation: Evaluation, options: dict):
        "%(name)s[points_, OptionsPattern[%(name)s]]"

        points = points.evaluate(evaluation)

        if points.get_head_name() != "System`List" or not points.elements:
            return

        if points.elements[0].get_head_name() == "System`List":
            if not all(
                group.get_head_name() == "System`List" for group in points.elements
            ):
                return
            multiple_colors = True
            groups = points.elements
        else:
            multiple_colors = False
            groups = [points]

        chart_legends = self.get_option(options, "ChartLegends", evaluation)
        has_chart_legends = chart_legends.get_head_name() == "System`List"
        if has_chart_legends:
            multiple_colors = True

        def to_number(x):
            if isinstance(x, Integer):
                return float(x.get_int_value())
            return x.round_to_float(evaluation=evaluation)

        data = [[to_number(x) for x in group.elements] for group in groups]

        chart_style = self.get_option(options, "ChartStyle", evaluation)
        if (
            isinstance(chart_style, Symbol)
            and chart_style.get_name() == "System`Automatic"
        ):
            chart_style = String("Automatic")

        if chart_style.get_head_name() == "System`List":
            colors = chart_style.elements
            spread_colors = False
        elif isinstance(chart_style, String):
            if chart_style.get_string_value() == "Automatic":
                mpl_colors = palettable.wesanderson.Moonrise1_5.mpl_colors
            else:
                mpl_colors = ColorData.colors(chart_style.get_string_value())
                if mpl_colors is None:
                    return
                multiple_colors = True

            if not multiple_colors and not self.never_monochrome:
                colors = [to_expression(SymbolRGBColor, *mpl_colors[0])]
            else:
                colors = [to_expression(SymbolRGBColor, *c) for c in mpl_colors]
            spread_colors = True
        else:
            return

        def legends(names):
            if not data:
                return

            n = len(data[0])
            for d in data[1:]:
                if len(d) != n:
                    return  # data groups should have same size

            def box(color):
                return Expression(
                    SymbolGraphics,
                    ListExpression(
                        Expression(SymbolFaceForm, color), Expression(SymbolRectangle)
                    ),
                    Expression(
                        SymbolRule,
                        Symbol("ImageSize"),
                        ListExpression(Integer(50), Integer(50)),
                    ),
                )

            rows_per_col = 5

            n_cols = 1 + len(names) // rows_per_col
            if len(names) % rows_per_col == 0:
                n_cols -= 1

            if n_cols == 1:
                n_rows = len(names)
            else:
                n_rows = rows_per_col

            for i in range(n_rows):
                items = []
                for j in range(n_cols):
                    k = 1 + i + j * rows_per_col
                    if k - 1 < len(names):
                        items.extend([box(color(k, n)), names[k - 1]])
                    else:
                        items.extend([String(""), String("")])
                yield ListExpression(*items)

        def color(k, n):
            if spread_colors and n < len(colors):
                index = int(k * (len(colors) - 1)) // n
                return colors[index]
            else:
                return colors[(k - 1) % len(colors)]

        chart = self._draw(data, color, evaluation, options)

        if has_chart_legends:
            grid = Expression(
                SymbolGrid, ListExpression(*list(legends(chart_legends.elements)))
            )
            chart = Expression(SymbolRow, ListExpression(chart, grid))

        return chart


class _GradientColorScheme:
    def color_data_function(self, name):
        colors = ListExpression(
            *[
                to_expression(
                    SymbolRGBColor, *color, elements_conversion_fn=MachineReal
                )
                for color in self.colors()
            ]
        )
        blend = Expression(
            SymbolFunction,
            Expression(SymbolBlend, colors, Expression(SymbolSlot, Integer1)),
        )
        arguments = [
            String(name),
            String("Gradients"),
            ListExpression(Integer0, Integer1),
            blend,
        ]
        return Expression(SymbolColorDataFunction, *arguments)


class _ListPlot(Builtin):
    """
    Base class for ListPlot, and ListLinePlot
    2-Dimensional plot a list of points in some fashion.
    """

    attributes = A_PROTECTED | A_READ_PROTECTED

    messages = {
        "prng": (
            "Value of option PlotRange -> `1` is not All, Automatic or "
            "an appropriate list of range specifications."
        ),
        "joind": "Value of option Joined -> `1` is not True or False.",
    }

    use_log_scale = False

    def eval(self, points, evaluation: Evaluation, options: dict):
        "%(name)s[points_, OptionsPattern[%(name)s]]"

        plot_name = self.get_name()

        # Scale point values down by Log 10. Tick mark values will be adjusted to be 10^n in GraphicsBox.
        if self.use_log_scale:
            points = ListExpression(
                *(
                    Expression(SymbolLog10, point).evaluate(evaluation)
                    for point in points
                )
            )

        all_points = eval_N(points, evaluation).to_python()
        # FIXME: arrange for self to have a .symbolname property or attribute
        expr = Expression(Symbol(self.get_name()), points, *options_to_rules(options))

        plotrange_option = self.get_option(options, "PlotRange", evaluation)
        plotrange = eval_N(plotrange_option, evaluation).to_python()
        if plotrange == "System`All":
            plotrange = ["System`All", "System`All"]
        elif plotrange == "System`Automatic":
            plotrange = ["System`Automatic", "System`Automatic"]
        elif isinstance(plotrange, numbers.Real):
            plotrange = [[-plotrange, plotrange], [-plotrange, plotrange]]
        elif isinstance(plotrange, list) and len(plotrange) == 2:
            if all(isinstance(pr, numbers.Real) for pr in plotrange):
                plotrange = ["System`All", plotrange]
            elif all(check_plot_range(pr, numbers.Real) for pr in plotrange):
                pass
        else:
            evaluation.message(self.get_name(), "prng", plotrange_option)
            plotrange = ["System`Automatic", "System`Automatic"]

        x_range, y_range = plotrange[0], plotrange[1]
        assert x_range in ("System`Automatic", "System`All") or isinstance(
            x_range, list
        )
        assert y_range in ("System`Automatic", "System`All") or isinstance(
            y_range, list
        )

        # Filling option
        # TODO: Fill between corresponding points in two datasets:
        filling_option = self.get_option(options, "Filling", evaluation)
        filling = eval_N(filling_option, evaluation).to_python()
        if filling in [
            "System`Top",
            "System`Bottom",
            "System`Axis",
        ] or isinstance(  # noqa
            filling, numbers.Real
        ):
            pass
        else:
            # Mathematica does not even check that filling is sane
            filling = None

        # Joined Option
        joined_option = self.get_option(options, "Joined", evaluation)
        is_joined_plot = joined_option.to_python()
        if is_joined_plot not in [True, False]:
            evaluation.message(plot_name, "joind", joined_option, expr)
            is_joined_plot = False

        return eval_ListPlot(
            all_points,
            x_range,
            y_range,
            is_discrete_plot=False,
            is_joined_plot=is_joined_plot,
            filling=filling,
            use_log_scale=self.use_log_scale,
            options=options,
        )


class _PalettableGradient(_GradientColorScheme):
    def __init__(self, palette, reversed):
        self.palette = palette
        self.reversed = reversed

    def colors(self):
        colors = self.palette.mpl_colors
        if self.reversed:
            colors = list(reversed(colors))
        return colors


class _Plot(Builtin):

    attributes = A_HOLD_ALL | A_PROTECTED | A_READ_PROTECTED

    expect_list = False

    use_log_scale = False

    messages = {
        "invmaxrec": (
            "MaxRecursion must be a non-negative integer; the recursion value "
            "is limited to `2`. Using MaxRecursion -> `1`."
        ),
        "prng": (
            "Value of option PlotRange -> `1` is not All, Automatic or "
            "an appropriate list of range specifications."
        ),
        "ppts": "Value of option PlotPoints -> `1` is not an integer >= 2.",
        "invexcl": (
            "Value of Exclusions -> `1` is not None, Automatic or an "
            "appropriate list of constraints."
        ),
    }

    options = Graphics.options.copy()
    options.update(
        {
            "Axes": "True",
            "AspectRatio": "1 / GoldenRatio",
            "MaxRecursion": "Automatic",
            "Mesh": "None",
            "PlotRange": "Automatic",
            "PlotPoints": "None",
            "Exclusions": "Automatic",
            "$OptionSyntax": "Strict",
        }
    )

    @lru_cache()
    def _apply_fn(self, f: Callable, x_value):
        value = f(x_value)
        if value is not None:
            return (x_value, value)

    def eval(self, functions, x, start, stop, evaluation: Evaluation, options: dict):
        """%(name)s[functions_, {x_Symbol, start_, stop_},
        OptionsPattern[%(name)s]]"""

        (
            functions,
            x_name,
            py_start,
            py_stop,
            x_range,
            y_range,
            _,
            _,
        ) = self.process_function_and_options(
            functions, x, start, stop, evaluation, options
        )

        # Mesh Option
        mesh_option = self.get_option(options, "Mesh", evaluation)
        mesh = mesh_option.to_python()
        if mesh not in ["System`None", "System`Full", "System`All"]:
            evaluation.message("Mesh", "ilevels", mesh_option)
            mesh = "System`None"

        # PlotPoints Option
        plotpoints_option = self.get_option(options, "PlotPoints", evaluation)
        plotpoints = plotpoints_option.to_python()
        if plotpoints == "System`None":
            plotpoints = 57
        if not (isinstance(plotpoints, int) and plotpoints >= 2):
            evaluation.message(self.get_name(), "ppts", plotpoints)
            return

        # MaxRecursion Option
        max_recursion_limit = 15
        maxrecursion_option = self.get_option(options, "MaxRecursion", evaluation)
        maxrecursion = maxrecursion_option.to_python()
        try:
            if maxrecursion == "System`Automatic":
                maxrecursion = 3
            elif maxrecursion == float("inf"):
                maxrecursion = max_recursion_limit
                raise ValueError
            elif isinstance(maxrecursion, int):
                if maxrecursion > max_recursion_limit:
                    maxrecursion = max_recursion_limit
                    raise ValueError
                if maxrecursion < 0:
                    maxrecursion = 0
                    raise ValueError
            else:
                maxrecursion = 0
                raise ValueError
        except ValueError:
            evaluation.message(
                self.get_name(), "invmaxrec", maxrecursion, max_recursion_limit
            )
        assert isinstance(maxrecursion, int)

        # Exclusions Option
        # TODO: Make exclusions option work properly with ParametricPlot
        def check_exclusion(excl):
            if isinstance(excl, list):
                return all(check_exclusion(e) for e in excl)
            if excl == "System`Automatic":
                return True
            if not isinstance(excl, numbers.Real):
                return False
            return True

        exclusions_option = self.get_option(options, "Exclusions", evaluation)
        exclusions = eval_N(exclusions_option, evaluation).to_python()
        # TODO Turn expressions into points E.g. Sin[x] == 0 becomes 0, 2 Pi...

        if exclusions in ["System`None", ["System`None"]]:
            exclusions = "System`None"
        elif not isinstance(exclusions, list):
            exclusions = [exclusions]

            if isinstance(exclusions, list) and all(  # noqa
                check_exclusion(excl) for excl in exclusions
            ):
                pass

            else:
                evaluation.message(self.get_name(), "invexcl", exclusions_option)
                exclusions = ["System`Automatic"]

        # exclusions is now either 'None' or a list of reals and 'Automatic'
        assert exclusions == "System`None" or isinstance(exclusions, list)

        use_log_scale = self.use_log_scale
        return eval_Plot(
            functions,
            self._apply_fn,
            x_name,
            py_start,
            py_stop,
            x_range,
            y_range,
            plotpoints,
            mesh,
            self.expect_list,
            exclusions,
            maxrecursion,
            use_log_scale,
            options,
            evaluation,
        )

    def get_functions_param(self, functions):
        if functions.has_form("List", None):
            functions = list(functions.elements)
        else:
            functions = [functions]
        return functions

    def get_plotrange(self, plotrange, start, stop):
        x_range = y_range = None
        if isinstance(plotrange, numbers.Real):
            plotrange = ["System`Full", [-plotrange, plotrange]]
        if plotrange == "System`Automatic":
            plotrange = ["System`Full", "System`Automatic"]
        elif plotrange == "System`All":
            plotrange = ["System`All", "System`All"]
        if isinstance(plotrange, list) and len(plotrange) == 2:
            if isinstance(plotrange[0], numbers.Real) and isinstance(  # noqa
                plotrange[1], numbers.Real
            ):
                x_range, y_range = "System`Full", plotrange
            else:
                x_range, y_range = plotrange
            if x_range == "System`Full":
                x_range = [start, stop]
        return x_range, y_range

    def process_function_and_options(
        self, functions, x, start, stop, evaluation: Evaluation, options: dict
    ) -> tuple:

        if isinstance(functions, Symbol) and functions.name is not x.get_name():
            rules = evaluation.definitions.get_ownvalues(functions.name)
            for rule in rules:
                functions = rule.apply(functions, evaluation, fully=True)

        if functions.get_head() == SymbolList:
            functions_param = self.get_functions_param(functions)
            for index, f in enumerate(functions_param):
                if isinstance(f, Symbol) and f.name is not x.get_name():
                    rules = evaluation.definitions.get_ownvalues(f.name)
                    for rule in rules:
                        f = rule.apply(f, evaluation, fully=True)
                functions_param[index] = f

            functions = functions.flatten_with_respect_to_head(SymbolList)

        expr_limits = ListExpression(x, start, stop)
        # FIXME: arrange for self to have a .symbolname property or attribute
        expr = Expression(
            Symbol(self.get_name()), functions, expr_limits, *options_to_rules(options)
        )
        functions = self.get_functions_param(functions)
        x_name = x.get_name()

        py_start = start.round_to_float(evaluation)
        py_stop = stop.round_to_float(evaluation)
        if py_start is None or py_stop is None:
            evaluation.message(self.get_name(), "plln", stop, expr)
            return
        if py_start >= py_stop:
            evaluation.message(self.get_name(), "plld", expr_limits)
            return

        plotrange_option = self.get_option(options, "PlotRange", evaluation)
        plot_range = eval_N(plotrange_option, evaluation).to_python()
        x_range, y_range = self.get_plotrange(plot_range, py_start, py_stop)
        if not check_plot_range(x_range, numbers.Real) or not check_plot_range(
            y_range, numbers.Real
        ):
            evaluation.message(self.get_name(), "prng", plotrange_option)
            x_range, y_range = [start, stop], "Automatic"

        # x_range and y_range are now either Automatic, All, or of the form [min, max]
        assert x_range in ("System`Automatic", "System`All") or isinstance(
            x_range, list
        )
        assert y_range in ("System`Automatic", "System`All") or isinstance(
            y_range, list
        )
        return functions, x_name, py_start, py_stop, x_range, y_range, expr_limits, expr


class _Plot3D(Builtin):
    messages = {
        "invmaxrec": (
            "MaxRecursion must be a non-negative integer; the recursion value "
            "is limited to `2`. Using MaxRecursion -> `1`."
        ),
        "prng": (
            "Value of option PlotRange -> `1` is not All, Automatic or "
            "an appropriate list of range specifications."
        ),
        "invmesh": "Mesh must be one of {None, Full, All}. Using Mesh->None.",
        "invpltpts": (
            "Value of PlotPoints -> `1` is not a positive integer "
            "or appropriate list of positive integers."
        ),
    }

    def eval(
        self,
        functions,
        x,
        xstart,
        xstop,
        y,
        ystart,
        ystop,
        evaluation: Evaluation,
        options: dict,
    ):
        """%(name)s[functions_, {x_Symbol, xstart_, xstop_},
        {y_Symbol, ystart_, ystop_}, OptionsPattern[%(name)s]]"""
        xexpr_limits = ListExpression(x, xstart, xstop)
        yexpr_limits = ListExpression(y, ystart, ystop)
        expr = Expression(
            Symbol(self.get_name()),
            functions,
            xexpr_limits,
            yexpr_limits,
            *options_to_rules(options)
        )

        functions = self.get_functions_param(functions)
        plot_name = self.get_name()

        def convert_limit(value, limits):
            result = value.round_to_float(evaluation)
            if result is None:
                evaluation.message(plot_name, "plln", value, limits)
            return result

        xstart = convert_limit(xstart, xexpr_limits)
        xstop = convert_limit(xstop, xexpr_limits)
        ystart = convert_limit(ystart, yexpr_limits)
        ystop = convert_limit(ystop, yexpr_limits)
        if None in (xstart, xstop, ystart, ystop):
            return

        if ystart >= ystop:
            evaluation.message(plot_name, "plln", ystop, expr)
            return

        if xstart >= xstop:
            evaluation.message(plot_name, "plln", xstop, expr)
            return

        # Mesh Option
        mesh_option = self.get_option(options, "Mesh", evaluation)
        mesh = mesh_option.to_python()
        if mesh not in ["System`None", "System`Full", "System`All"]:
            evaluation.message("Mesh", "ilevels", mesh_option)
            mesh = "System`Full"

        # PlotPoints Option
        plotpoints_option = self.get_option(options, "PlotPoints", evaluation)
        plotpoints = plotpoints_option.to_python()

        def check_plotpoints(steps):
            if isinstance(steps, int) and steps > 0:
                return True
            return False

        if plotpoints == "System`None":
            plotpoints = [7, 7]
        elif check_plotpoints(plotpoints):
            plotpoints = [plotpoints, plotpoints]

        if not (
            isinstance(plotpoints, list)
            and len(plotpoints) == 2
            and check_plotpoints(plotpoints[0])
            and check_plotpoints(plotpoints[1])
        ):
            evaluation.message(self.get_name(), "invpltpts", plotpoints)
            plotpoints = [7, 7]

        # MaxRecursion Option
        maxrec_option = self.get_option(options, "MaxRecursion", evaluation)
        max_depth = maxrec_option.to_python()
        if isinstance(max_depth, int):
            if max_depth < 0:
                max_depth = 0
                evaluation.message(self.get_name(), "invmaxrec", max_depth, 15)
            elif max_depth > 15:
                max_depth = 15
                evaluation.message(self.get_name(), "invmaxrec", max_depth, 15)
            else:
                pass  # valid
        elif max_depth == float("inf"):
            max_depth = 15
            evaluation.message(self.get_name(), "invmaxrec", max_depth, 15)
        else:
            max_depth = 0
            evaluation.message(self.get_name(), "invmaxrec", max_depth, 15)

        # Plot the functions
        graphics = []
        for indx, f in enumerate(functions):
            stored = {}

            compiled_fn = compile_quiet_function(
                f, [x.get_name(), y.get_name()], evaluation, False
            )

            def apply_fn(compiled_fn: Callable, x_value, y_value):
                try:
                    # Try to used cached value first
                    return stored[(x_value, y_value)]
                except KeyError:
                    value = compiled_fn(x_value, y_value)
                    if value is not None:
                        value = float(value)
                    stored[(x_value, y_value)] = value
                    return value

            triangles = []

            split_edges = set()  # subdivided edges

            def triangle(x1, y1, x2, y2, x3, y3, depth=0):
                v1, v2, v3 = (
                    apply_fn(compiled_fn, x1, y1),
                    apply_fn(compiled_fn, x2, y2),
                    apply_fn(compiled_fn, x3, y3),
                )

                if (v1 is v2 is v3 is None) and (depth > max_depth // 2):
                    # fast finish because the entire region is undefined but
                    # recurse 'a little' to avoid missing well defined regions
                    return
                elif v1 is None or v2 is None or v3 is None:
                    # 'triforce' pattern recursion to find the edge of defined region
                    #         1
                    #         /\
                    #      4 /__\ 6
                    #       /\  /\
                    #      /__\/__\
                    #     2   5    3
                    if depth < max_depth:
                        x4, y4 = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
                        x5, y5 = 0.5 * (x2 + x3), 0.5 * (y2 + y3)
                        x6, y6 = 0.5 * (x1 + x3), 0.5 * (y1 + y3)
                        split_edges.add(
                            ((x1, y1), (x2, y2))
                            if (x2, y2) > (x1, y1)
                            else ((x2, y2), (x1, y1))
                        )
                        split_edges.add(
                            ((x2, y2), (x3, y3))
                            if (x3, y3) > (x2, y2)
                            else ((x3, y3), (x2, y2))
                        )
                        split_edges.add(
                            ((x1, y1), (x3, y3))
                            if (x3, y3) > (x1, y1)
                            else ((x3, y3), (x1, y1))
                        )
                        triangle(x1, y1, x4, y4, x6, y6, depth + 1)
                        triangle(x4, y4, x2, y2, x5, y5, depth + 1)
                        triangle(x6, y6, x5, y5, x3, y3, depth + 1)
                        triangle(x4, y4, x5, y5, x6, y6, depth + 1)
                    return
                triangles.append(sorted(((x1, y1, v1), (x2, y2, v2), (x3, y3, v3))))

            # linear (grid) sampling
            numx = plotpoints[0] * 1.0
            numy = plotpoints[1] * 1.0
            for xi in range(plotpoints[0]):
                for yi in range(plotpoints[1]):
                    # Decide which way to break the square grid into triangles
                    # by looking at diagonal lengths.
                    #
                    # 3___4        3___4
                    # |\  |        |  /|
                    # | \ | versus | / |
                    # |__\|        |/__|
                    # 1   2        1   2
                    #
                    # Approaching the boundary of the well defined region is
                    # important too. Use first stategy if 1 or 4 are undefined
                    # and stategy 2 if either 2 or 3 are undefined.
                    #
                    (x1, x2, x3, x4) = (
                        xstart + value * (xstop - xstart)
                        for value in (
                            xi / numx,
                            (xi + 1) / numx,
                            xi / numx,
                            (xi + 1) / numx,
                        )
                    )
                    (y1, y2, y3, y4) = (
                        ystart + value * (ystop - ystart)
                        for value in (
                            yi / numy,
                            yi / numy,
                            (yi + 1) / numy,
                            (yi + 1) / numy,
                        )
                    )

                    v1 = apply_fn(compiled_fn, x1, y1)
                    v2 = apply_fn(compiled_fn, x2, y2)
                    v3 = apply_fn(compiled_fn, x3, y3)
                    v4 = apply_fn(compiled_fn, x4, y4)

                    if v1 is None or v4 is None:
                        triangle(x1, y1, x2, y2, x3, y3)
                        triangle(x4, y4, x3, y3, x2, y2)
                    elif v2 is None or v3 is None:
                        triangle(x2, y2, x1, y1, x4, y4)
                        triangle(x3, y3, x4, y4, x1, y1)
                    else:
                        if abs(v3 - v2) > abs(v4 - v1):
                            triangle(x2, y2, x1, y1, x4, y4)
                            triangle(x3, y3, x4, y4, x1, y1)
                        else:
                            triangle(x1, y1, x2, y2, x3, y3)
                            triangle(x4, y4, x3, y3, x2, y2)

            # adaptive resampling
            # TODO: optimise this
            # Cos of the maximum angle between successive line segments
            ang_thresh = cos(20 * pi / 180)
            for depth in range(1, max_depth):
                needs_removal = set()
                lent = len(triangles)  # number of initial triangles
                for i1 in range(lent):
                    for i2 in range(lent):
                        # find all edge pairings
                        if i1 == i2:
                            continue
                        t1 = triangles[i1]
                        t2 = triangles[i2]

                        edge_pairing = (
                            (t1[0], t1[1]) == (t2[0], t2[1])
                            or (t1[0], t1[1]) == (t2[1], t2[2])
                            or (t1[0], t1[1]) == (t2[0], t2[2])
                            or (t1[1], t1[2]) == (t2[0], t2[1])
                            or (t1[1], t1[2]) == (t2[1], t2[2])
                            or (t1[1], t1[2]) == (t2[0], t2[2])
                            or (t1[0], t1[2]) == (t2[0], t2[1])
                            or (t1[0], t1[2]) == (t2[1], t2[2])
                            or (t1[0], t1[2]) == (t2[0], t2[2])
                        )
                        if not edge_pairing:
                            continue
                        v1 = [t1[1][i] - t1[0][i] for i in range(3)]
                        w1 = [t1[2][i] - t1[0][i] for i in range(3)]
                        v2 = [t2[1][i] - t2[0][i] for i in range(3)]
                        w2 = [t2[2][i] - t2[0][i] for i in range(3)]
                        n1 = (  # surface normal for t1
                            (v1[1] * w1[2]) - (v1[2] * w1[1]),
                            (v1[2] * w1[0]) - (v1[0] * w1[2]),
                            (v1[0] * w1[1]) - (v1[1] * w1[0]),
                        )
                        n2 = (  # surface normal for t2
                            (v2[1] * w2[2]) - (v2[2] * w2[1]),
                            (v2[2] * w2[0]) - (v2[0] * w2[2]),
                            (v2[0] * w2[1]) - (v2[1] * w2[0]),
                        )
                        try:
                            angle = (
                                n1[0] * n2[0] + n1[1] * n2[1] + n1[2] * n2[2]
                            ) / sqrt(
                                (n1[0] ** 2 + n1[1] ** 2 + n1[2] ** 2)
                                * (n2[0] ** 2 + n2[1] ** 2 + n2[2] ** 2)
                            )
                        except ZeroDivisionError:
                            angle = 0.0
                        if abs(angle) < ang_thresh:
                            for i, t in ((i1, t1), (i2, t2)):
                                # subdivide
                                x1, y1 = t[0][0], t[0][1]
                                x2, y2 = t[1][0], t[1][1]
                                x3, y3 = t[2][0], t[2][1]
                                x4, y4 = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
                                x5, y5 = 0.5 * (x2 + x3), 0.5 * (y2 + y3)
                                x6, y6 = 0.5 * (x1 + x3), 0.5 * (y1 + y3)
                                needs_removal.add(i)
                                split_edges.add(
                                    ((x1, y1), (x2, y2))
                                    if (x2, y2) > (x1, y1)
                                    else ((x2, y2), (x1, y1))
                                )
                                split_edges.add(
                                    ((x2, y2), (x3, y3))
                                    if (x3, y3) > (x2, y2)
                                    else ((x3, y3), (x2, y2))
                                )
                                split_edges.add(
                                    ((x1, y1), (x3, y3))
                                    if (x3, y3) > (x1, y1)
                                    else ((x3, y3), (x1, y1))
                                )
                                triangle(x1, y1, x4, y4, x6, y6, depth=depth)
                                triangle(x2, y2, x4, y4, x5, y5, depth=depth)
                                triangle(x3, y3, x5, y5, x6, y6, depth=depth)
                                triangle(x4, y4, x5, y5, x6, y6, depth=depth)
                # remove subdivided triangles which have been divided
                triangles = [
                    t for i, t in enumerate(triangles) if i not in needs_removal
                ]

            # fix up subdivided edges
            #
            # look at every triangle and see if its edges need updating.
            # depending on how many edges require subdivision we proceede with
            # one of two subdivision strategies
            #
            # TODO possible optimisation: don't look at every triangle again
            made_changes = True
            while made_changes:
                made_changes = False
                new_triangles = []
                for i, t in enumerate(triangles):
                    new_points = []
                    if ((t[0][0], t[0][1]), (t[1][0], t[1][1])) in split_edges:
                        new_points.append([0, 1])
                    if ((t[1][0], t[1][1]), (t[2][0], t[2][1])) in split_edges:
                        new_points.append([1, 2])
                    if ((t[0][0], t[0][1]), (t[2][0], t[2][1])) in split_edges:
                        new_points.append([0, 2])

                    if len(new_points) == 0:
                        continue
                    made_changes = True
                    # 'triforce' subdivision
                    #         1
                    #         /\
                    #      4 /__\ 6
                    #       /\  /\
                    #      /__\/__\
                    #     2   5    3
                    # if less than three edges require subdivision bisect them
                    # anyway but fake their values by averaging
                    x4 = 0.5 * (t[0][0] + t[1][0])
                    y4 = 0.5 * (t[0][1] + t[1][1])
                    v4 = stored.get((x4, y4), 0.5 * (t[0][2] + t[1][2]))

                    x5 = 0.5 * (t[1][0] + t[2][0])
                    y5 = 0.5 * (t[1][1] + t[2][1])
                    v5 = stored.get((x5, y5), 0.5 * (t[1][2] + t[2][2]))

                    x6 = 0.5 * (t[0][0] + t[2][0])
                    y6 = 0.5 * (t[0][1] + t[2][1])
                    v6 = stored.get((x6, y6), 0.5 * (t[0][2] + t[2][2]))

                    if not (v4 is None or v6 is None):
                        new_triangles.append(sorted((t[0], (x4, y4, v4), (x6, y6, v6))))
                    if not (v4 is None or v5 is None):
                        new_triangles.append(sorted((t[1], (x4, y4, v4), (x5, y5, v5))))
                    if not (v5 is None or v6 is None):
                        new_triangles.append(sorted((t[2], (x5, y5, v5), (x6, y6, v6))))
                    if not (v4 is None or v5 is None or v6 is None):
                        new_triangles.append(
                            sorted(((x4, y4, v4), (x5, y5, v5), (x6, y6, v6)))
                        )
                    triangles[i] = None

                triangles.extend(new_triangles)
                triangles = [t for t in triangles if t is not None]

            # add the mesh
            mesh_points = []
            if mesh == "System`Full":
                for xi in range(plotpoints[0] + 1):
                    xval = xstart + xi / numx * (xstop - xstart)
                    mesh_row = []
                    for yi in range(plotpoints[1] + 1):
                        yval = ystart + yi / numy * (ystop - ystart)
                        z = stored[(xval, yval)]
                        mesh_row.append((xval, yval, z))
                    mesh_points.append(mesh_row)

                for yi in range(plotpoints[1] + 1):
                    yval = ystart + yi / numy * (ystop - ystart)
                    mesh_col = []
                    for xi in range(plotpoints[0] + 1):
                        xval = xstart + xi / numx * (xstop - xstart)
                        z = stored[(xval, yval)]
                        mesh_col.append((xval, yval, z))
                    mesh_points.append(mesh_col)

                # handle edge subdivisions
                made_changes = True
                while made_changes:
                    made_changes = False
                    for mesh_line in mesh_points:
                        i = 0
                        while i < len(mesh_line) - 1:
                            x1, y1, v1 = mesh_line[i]
                            x2, y2, v2 = mesh_line[i + 1]
                            key = (
                                ((x1, y1), (x2, y2))
                                if (x2, y2) > (x1, y1)
                                else ((x2, y2), (x1, y1))
                            )
                            if key in split_edges:
                                x3 = 0.5 * (x1 + x2)
                                y3 = 0.5 * (y1 + y2)
                                v3 = stored[(x3, y3)]
                                mesh_line.insert(i + 1, (x3, y3, v3))
                                made_changes = True
                                i += 1
                            i += 1

                # handle missing regions
                old_meshpoints, mesh_points = mesh_points, []
                for mesh_line in old_meshpoints:
                    mesh_points.extend(
                        [
                            sorted(g)
                            for k, g in itertools.groupby(
                                mesh_line, lambda x: x[2] is None
                            )
                        ]
                    )
                mesh_points = [
                    mesh_line
                    for mesh_line in mesh_points
                    if not any(x[2] is None for x in mesh_line)
                ]
            elif mesh == "System`All":
                mesh_points = set()
                for t in triangles:
                    mesh_points.add((t[0], t[1]) if t[1] > t[0] else (t[1], t[0]))
                    mesh_points.add((t[1], t[2]) if t[2] > t[1] else (t[2], t[1]))
                    mesh_points.add((t[0], t[2]) if t[2] > t[0] else (t[2], t[0]))
                mesh_points = list(mesh_points)

            # find the max and min height
            v_min = v_max = None
            for t in triangles:
                for tx, ty, v in t:
                    if v_min is None or v < v_min:
                        v_min = v
                    if v_max is None or v > v_max:
                        v_max = v
            graphics.extend(
                self.construct_graphics(
                    triangles, mesh_points, v_min, v_max, options, evaluation
                )
            )
        return self.final_graphics(graphics, options)


class _PredefinedGradient(_GradientColorScheme):
    def __init__(self, colors):
        self._colors = colors

    def colors(self):
        return self._colors


class BarChart(_Chart):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/BarChart.html</url>
    <dl>
        <dt>'BarChart[{$b1$, $b2$ ...}]'
        <dd>makes a bar chart with lengths $b1$, $b2$, ....
    </dl>
    Drawing options include -
    Charting:
    <ul>
      <li>Mesh
      <li>PlotRange
      <li>ChartLabels
      <li>ChartLegends
      <li>ChartStyle
    </ul>

    BarChart specific:
    <ul>
      <li>Axes  (default {False, True})
      <li>AspectRatio: (default 1 / GoldenRatio)
    </ul>

    A bar chart of a list of heights:
    >> BarChart[{1, 4, 2}]
     = -Graphics-

    >> BarChart[{1, 4, 2}, ChartStyle -> {Red, Green, Blue}]
     = -Graphics-

    >> BarChart[{{1, 2, 3}, {2, 3, 4}}]
     = -Graphics-

    Chart several datasets with categorical labels:
    >> BarChart[{{1, 2, 3}, {2, 3, 4}}, ChartLabels -> {"a", "b", "c"}]
     = -Graphics-

    >> BarChart[{{1, 5}, {3, 4}}, ChartStyle -> {{EdgeForm[Thin], White}, {EdgeForm[Thick], White}}]
     = -Graphics-
    """

    options = _Chart.options.copy()
    options.update(
        {
            "Axes": "{False, True}",
            "AspectRatio": "1 / GoldenRatio",
        }
    )

    summary_text = "draw a bar chart"

    def _draw(self, data, color, evaluation, options):
        def vector2(x, y) -> ListExpression:
            return to_mathics_list(x, y)

        def boxes():
            w = 0.9
            s = 0.06
            w_half = 0.5 * w
            x = 0.1 + s + w_half

            for y_values in data:
                y_length = len(y_values)
                for i, y in enumerate(y_values):
                    x0 = x - w_half
                    x1 = x0 + w
                    yield (i + 1, y_length), x0, x1, y
                    x = x1 + s + w_half

                x += 0.2

        def rectangles():
            yield Expression(SymbolEdgeForm, Symbol("Black"))

            last_x1 = 0

            for (k, n), x0, x1, y in boxes():
                yield Expression(
                    SymbolStyle,
                    Expression(
                        SymbolRectangle,
                        to_mathics_list(x0, 0),
                        to_mathics_list(x1, y),
                    ),
                    color(k, n),
                )

                last_x1 = x1

            yield Expression(
                SymbolLine, ListExpression(vector2(0, 0), vector2(last_x1, Integer0))
            )

        def axes():
            yield Expression(SymbolFaceForm, Symbol("Black"))

            def points(x):
                return ListExpression(vector2(x, 0), vector2(x, MTwoTenths))

            for (k, n), x0, x1, y in boxes():
                if k == 1:
                    yield Expression(SymbolLine, points(x0))
                if k == n:
                    yield Expression(SymbolLine, points(x1))

        def labels(names):
            yield Expression(SymbolFaceForm, Symbol("Black"))

            for (k, n), x0, x1, y in boxes():
                if k <= len(names):
                    name = names[k - 1]
                    yield Expression(
                        SymbolText, name, vector2((x0 + x1) / 2, MTwoTenths)
                    )

        x_coords = list(itertools.chain(*[[x0, x1] for (k, n), x0, x1, y in boxes()]))
        y_coords = [0] + [y for (k, n), x0, x1, y in boxes()]

        graphics = list(rectangles()) + list(axes())

        x_range = "System`All"
        y_range = "System`All"

        x_range = list(get_plot_range(x_coords, x_coords, x_range))
        y_range = list(get_plot_range(y_coords, y_coords, y_range))

        chart_labels = self.get_option(options, "ChartLabels", evaluation)
        if chart_labels.get_head_name() == "System`List":
            graphics.extend(list(labels(chart_labels.elements)))
            y_range[0] = -0.4  # room for labels at the bottom

        # FIXME: this can't be right...
        # always specify -.1 as the minimum x plot range, as this will make the y axis apppear
        # at origin (0,0); otherwise it will be shifted right; see GraphicsBox.axis_ticks().
        x_range[0] = -0.1

        options["System`PlotRange"] = ListExpression(
            vector2(*x_range), vector2(*y_range)
        )

        return Expression(
            SymbolGraphics, ListExpression(*graphics), *options_to_rules(options)
        )


class ColorData(Builtin):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ColorData.html</url>
    <dl>
      <dt>'ColorData["$name$"]'
      <dd>returns a color function with the given $name$.
    </dl>

    Define a user-defined color function:
    >> Unprotect[ColorData]; ColorData["test"] := ColorDataFunction["test", "Gradients", {0, 1}, Blend[{Red, Green, Blue}, #1] &]; Protect[ColorData]

    Compare it to the default color function, 'LakeColors':
    >> {DensityPlot[x + y, {x, -1, 1}, {y, -1, 1}], DensityPlot[x + y, {x, -1, 1}, {y, -1, 1}, ColorFunction->"test"]}
     = {-Graphics-, -Graphics-}
    """

    # rules = {
    #    'ColorData["LakeColors"]': (
    #        """ColorDataFunction["LakeColors", "Gradients", {0, 1},
    #            Blend[{RGBColor[0.293416, 0.0574044, 0.529412],
    #                RGBColor[0.563821, 0.527565, 0.909499],
    #                RGBColor[0.762631, 0.846998, 0.914031],
    #                RGBColor[0.941176, 0.906538, 0.834043]}, #1] &]"""),
    # }
    summary_text = "named color gradients and collections"
    messages = {
        "notent": "`1` is not a known color scheme. ColorData[] gives you lists of schemes.",
    }

    palettes = {
        "LakeColors": _PredefinedGradient(
            [
                (0.293416, 0.0574044, 0.529412),
                (0.563821, 0.527565, 0.909499),
                (0.762631, 0.846998, 0.914031),
                (0.941176, 0.906538, 0.834043),
            ]
        ),
        "Pastel": _PalettableGradient(
            palettable.colorbrewer.qualitative.Pastel1_9, False
        ),
        "Rainbow": _PalettableGradient(
            palettable.colorbrewer.diverging.Spectral_9, True
        ),
        "RedBlueTones": _PalettableGradient(
            palettable.colorbrewer.diverging.RdBu_11, False
        ),
        "GreenPinkTones": _PalettableGradient(
            palettable.colorbrewer.diverging.PiYG_9, False
        ),
        "GrayTones": _PalettableGradient(
            palettable.colorbrewer.sequential.Greys_9, False
        ),
        "SolarColors": _PalettableGradient(
            palettable.colorbrewer.sequential.OrRd_9, True
        ),
        "CherryTones": _PalettableGradient(
            palettable.colorbrewer.sequential.Reds_9, True
        ),
        "FuchsiaTones": _PalettableGradient(
            palettable.colorbrewer.sequential.RdPu_9, True
        ),
        "SiennaTones": _PalettableGradient(
            palettable.colorbrewer.sequential.Oranges_9, True
        ),
        # specific to Mathics
        "Paired": _PalettableGradient(
            palettable.colorbrewer.qualitative.Paired_9, False
        ),
        "Accent": _PalettableGradient(
            palettable.colorbrewer.qualitative.Accent_8, False
        ),
        "Aquatic": _PalettableGradient(palettable.wesanderson.Aquatic1_5, False),
        "Zissou": _PalettableGradient(palettable.wesanderson.Zissou_5, False),
        "Tableau": _PalettableGradient(palettable.tableau.Tableau_20, False),
        "TrafficLight": _PalettableGradient(palettable.tableau.TrafficLight_9, False),
        "Moonrise1": _PalettableGradient(palettable.wesanderson.Moonrise1_5, False),
    }

    def eval_directory(self, evaluation: Evaluation):
        "ColorData[]"
        return ListExpression(String("Gradients"))

    def eval(self, name, evaluation: Evaluation):
        "ColorData[name_String]"
        py_name = name.get_string_value()
        if py_name == "Gradients":
            return ListExpression(*[String(name) for name in self.palettes.keys()])
        palette = ColorData.palettes.get(py_name, None)
        if palette is None:
            evaluation.message("ColorData", "notent", name)
            return
        return palette.color_data_function(py_name)

    @staticmethod
    def colors(name, evaluation):
        palette = ColorData.palettes.get(name, None)
        if palette is None:
            evaluation.message("ColorData", "notent", name)
            return None
        return palette.colors()


class ColorDataFunction(Builtin):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ColorDataFunction.html</url>
    <dl>
      <dt>'ColorDataFunction[range, ...]'
      <dd> is a function that represents a color scheme.
    </dl>
    """

    summary_text = "color scheme object"
    pass


class DensityPlot(_Plot3D):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/DensityPlot.html</url>
    <dl>
      <dt>'DensityPlot[$f$, {$x$, $xmin$, $xmax$}, {$y$, $ymin$, $ymax$}]'
      <dd>plots a density plot of $f$ with $x$ ranging from $xmin$ to $xmax$ and $y$ ranging from $ymin$ to $ymax$.
    </dl>

    >> DensityPlot[x ^ 2 + 1 / y, {x, -1, 1}, {y, 1, 4}]
     = -Graphics-

    >> DensityPlot[1 / x, {x, 0, 1}, {y, 0, 1}]
     = -Graphics-

    >> DensityPlot[Sqrt[x * y], {x, -1, 1}, {y, -1, 1}]
     = -Graphics-

    >> DensityPlot[1/(x^2 + y^2 + 1), {x, -1, 1}, {y, -2,2}, Mesh->Full]
     = -Graphics-

    >> DensityPlot[x^2 y, {x, -1, 1}, {y, -1, 1}, Mesh->All]
     = -Graphics-
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    options = Graphics.options.copy()
    options.update(
        {
            "Axes": "False",
            "AspectRatio": "1",
            "Mesh": "None",
            "Frame": "True",
            "ColorFunction": "Automatic",
            "ColorFunctionScaling": "True",
            "PlotPoints": "None",
            "MaxRecursion": "0",
            # 'MaxRecursion': '2',  # FIXME causes bugs in svg output see #303
        }
    )
    summary_text = "density plot for a function"

    def get_functions_param(self, functions):
        return [functions]

    def construct_graphics(
        self, triangles, mesh_points, v_min, v_max, options, evaluation
    ):
        color_function = self.get_option(options, "ColorFunction", evaluation, pop=True)
        color_function_scaling = self.get_option(
            options, "ColorFunctionScaling", evaluation, pop=True
        )

        color_function_min = color_function_max = None
        if color_function.get_name() == "System`Automatic":
            color_function = String("LakeColors")
        if color_function.get_string_value():
            func = Expression(
                SymbolColorData, String(color_function.get_string_value())
            ).evaluate(evaluation)
            if func.has_form("ColorDataFunction", 4):
                color_function_min = func.elements[2].elements[0].round_to_float()
                color_function_max = func.elements[2].elements[1].round_to_float()
                color_function = Expression(
                    SymbolFunction,
                    Expression(func.elements[3], Expression(SymbolSlot, Integer1)),
                )
            else:
                evaluation.message("DensityPlot", "color", func)
                return
        if color_function.has_form("ColorDataFunction", 4):
            color_function_min = color_function.elements[2].elements[0].round_to_float()
            color_function_max = color_function.elements[2].elements[1].round_to_float()

        color_function_scaling = color_function_scaling is SymbolTrue
        v_range = v_max - v_min

        if v_range == 0:
            v_range = 1

        if color_function.has_form("ColorDataFunction", 4):
            color_func = color_function.elements[3]
        else:
            color_func = color_function
        if (
            color_function_scaling
            and color_function_min is not None  # noqa
            and color_function_max is not None
        ):
            color_function_range = color_function_max - color_function_min

        colors = {}

        def eval_color(x, y, v):
            v_scaled = (v - v_min) / v_range
            if (
                color_function_scaling
                and color_function_min is not None  # noqa
                and color_function_max is not None
            ):
                v_color_scaled = color_function_min + v_scaled * color_function_range
            else:
                v_color_scaled = v

            # Calculate and store 100 different shades max.
            v_lookup = int(v_scaled * 100 + 0.5)

            value = colors.get(v_lookup)
            if value is None:
                value = Expression(color_func, Real(v_color_scaled))
                value = value.evaluate(evaluation)
                colors[v_lookup] = value
            return value

        points = []
        vertex_colors = []
        graphics = []
        for p in triangles:
            points.append(ListExpression(*(to_mathics_list(*x[:2]) for x in p)))
            vertex_colors.append(ListExpression(*(eval_color(*x) for x in p)))

        graphics.append(
            Expression(
                SymbolPolygon,
                ListExpression(*points),
                Expression(
                    SymbolRule,
                    Symbol("VertexColors"),
                    ListExpression(*vertex_colors),
                ),
            )
        )

        # add mesh
        for xi in range(len(mesh_points)):
            line = []
            for yi in range(len(mesh_points[xi])):
                line.append(
                    to_mathics_list(mesh_points[xi][yi][0], mesh_points[xi][yi][1])
                )
            graphics.append(Expression(SymbolLine, ListExpression(*line)))

        return graphics

    def final_graphics(self, graphics, options):
        return Expression(
            SymbolGraphics,
            ListExpression(*graphics),
            *options_to_rules(options, Graphics.options)
        )


class DiscretePlot(_Plot):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/DiscretePlot.html</url>
    <dl>
      <dt>'DiscretePlot[$expr$, {$x$, $n_max$}]'
      <dd>plots $expr$ with $x$ ranging from 1 to $n_max$.

      <dt>'DiscretePlot[$expr$, {$x$, $n_min$, $n_max$}]'
      <dd>plots $expr$ with $x$ ranging from $n_min$ to $n_max$.

      <dt>'DiscretePlot[$expr$, {$x$, $n_min$, $n_max$, $dn$}]'
      <dd>plots $expr$ with $x$ ranging from $n_min$ to $n_max$ usings steps $dn$.

      <dt>'DiscretePlot[{$expr1$, $expr2$, ...}, ...]'
      <dd>plots the values of all $expri$.
    </dl>

    The number of primes for a number $k$:
    >> DiscretePlot[PrimePi[k], {k, 1, 100}]
     = -Graphics-

    is about the same as 'Sqrt[k] * 2.5':
    >> DiscretePlot[2.5 Sqrt[k], {k, 100}]
     = -Graphics-

    Notice in the above that when the starting value, $n_min$,  is 1, we can \
    omit it.

    A plot can contain several functions, using the same parameter, here $x$:
    >> DiscretePlot[{Sin[Pi x/20], Cos[Pi x/20]}, {x, 0, 40}]
     = -Graphics-

    Compare with <url>:'Plot':
    /doc/reference-of-built-in-symbols/graphics-drawing-and-images/plotting-data/plot/</url>.
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    expect_list = False

    messages = {
        "prng": (
            "Value of option PlotRange -> `1` is not All, Automatic or "
            "an appropriate list of range specifications."
        ),
        "invexcl": (
            "Value of Exclusions -> `1` is not None, Automatic or an "
            "appropriate list of constraints."
        ),
    }

    options = Graphics.options.copy()
    options.update(
        {
            "Axes": "True",
            "AspectRatio": "1 / GoldenRatio",
            "PlotRange": "Automatic",
            "$OptionSyntax": "Strict",
        }
    )

    rules = {
        # One argument-form of DiscretePlot
        "DiscretePlot[expr_, {var_Symbol, nmax_Integer}]": "DiscretePlot[expr, {var, 1, nmax, 1}]",
        # Two argument-form of DiscretePlot
        "DiscretePlot[expr_, {var_Symbol, nmin_Integer, nmax_Integer}]": "DiscretePlot[expr, {var, nmin, nmax, 1}]",
    }

    summary_text = "discrete plot of a one-paremeter function"

    def eval(
        self, functions, x, start, nmax, step, evaluation: Evaluation, options: dict
    ):
        """DiscretePlot[functions_, {x_Symbol, start_Integer, nmax_Integer, step_Integer},
        OptionsPattern[DiscretePlot]]"""

        (
            functions,
            x_name,
            py_start,
            py_stop,
            x_range,
            y_range,
            expr_limits,
            expr,
        ) = self.process_function_and_options(
            functions, x, start, nmax, evaluation, options
        )

        py_start = start.value
        py_nmax = nmax.value
        py_step = step.value
        if py_start is None or py_nmax is None:
            evaluation.message(self.get_name(), "plln", nmax, expr)
            return
        if py_start >= py_nmax:
            evaluation.message(self.get_name(), "plld", expr_limits)
            return

        plotrange_option = self.get_option(options, "PlotRange", evaluation)
        plot_range = eval_N(plotrange_option, evaluation).to_python()

        x_range, y_range = self.get_plotrange(plot_range, py_start, py_nmax)
        if not check_plot_range(x_range, numbers.Real) or not check_plot_range(
            y_range, numbers.Real
        ):
            evaluation.message(self.get_name(), "prng", plotrange_option)
            x_range, y_range = [py_start, py_nmax], "Automatic"

        # x_range and y_range are now either Automatic, All, or of the form [min, max]
        assert x_range in ("System`Automatic", "System`All") or isinstance(
            x_range, list
        )
        assert y_range in ("System`Automatic", "System`All") or isinstance(
            y_range, list
        )

        base_plot_points = []  # list of points in base subdivision
        plot_points = []  # list of all plotted points

        # list of all plotted points across all functions
        plot_groups = []

        # List of graphics primitves that rendering will use to draw.
        # This includes the plot data, and overall graphics directives
        # like the Hue.

        for index, f in enumerate(functions):
            # list of all plotted points for a given function
            plot_points = []

            compiled_fn = compile_quiet_function(
                f, [x_name], evaluation, self.expect_list
            )

            @lru_cache()
            def apply_fn(fn: Callable, x_value: int) -> Optional[float]:
                value = fn(x_value)
                if value is not None:
                    value = float(value)
                return value

            for x_value in range(py_start, py_nmax, py_step):
                point = apply_fn(compiled_fn, x_value)
                plot_points.append((x_value, point))

            x_range = get_plot_range(
                [xx for xx, yy in base_plot_points],
                [xx for xx, yy in plot_points],
                x_range,
            )
            plot_groups.append(plot_points)

        y_values = [yy for xx, yy in plot_points]
        y_range = get_plot_range(y_values, y_values, option="System`All")

        # FIXME: For now we are going to specify that the min points are (-.1, -.1)
        # or pretty close to (0, 0) for positive plots, so that the tick axes are set to zero.
        # See GraphicsBox.axis_ticks().
        if x_range[0] > 0:
            x_range = (-0.1, x_range[1])
        if y_range[0] > 0:
            y_range = (-0.1, y_range[1])

        options["System`PlotRange"] = from_python([x_range, y_range])

        return eval_ListPlot(
            plot_groups,
            x_range,
            y_range,
            is_discrete_plot=True,
            is_joined_plot=False,
            filling=False,
            use_log_scale=False,
            options=options,
        )


class Histogram(Builtin):
    """
    <url>:Histogram: https://en.wikipedia.org/wiki/Histogram</url> \
    (<url>:WMA link: https://reference.wolfram.com/language/ref/ColorDataFunction.html</url>)

    <dl>
        <dt>'Histogram[{$x1$, $x2$ ...}]'
        <dd>plots a histogram using the values $x1$, $x2$, ....
    </dl>

    >> Histogram[{3, 8, 10, 100, 1000, 500, 300, 200, 10, 20, 200, 100, 200, 300, 500}]
     = -Graphics-

    >> Histogram[{{1, 2, 10, 5, 50, 20}, {90, 100, 101, 120, 80}}]
     = -Graphics-
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    options = Graphics.options.copy()
    options.update(
        {
            "Axes": "{True, True}",
            "AspectRatio": "1 / GoldenRatio",
            "Mesh": "None",
            "PlotRange": "Automatic",
        }
    )
    summary_text = "draw a histogram"

    def eval(self, points, spec, evaluation: Evaluation, options: dict):
        "%(name)s[points_, spec___, OptionsPattern[%(name)s]]"

        points = points.evaluate(evaluation)
        spec = spec.evaluate(evaluation).get_sequence()

        if spec and len(spec) not in (1, 2):
            return

        if points.get_head_name() != "System`List" or not points.elements:
            return

        if points.elements[0].get_head_name() == "System`List":
            if not all(q.get_head_name() == "System`List" for q in points.elements):
                return
            input = points.elements
        else:
            input = [points]

        def to_numbers(li):
            for x in li:
                y = x.to_mpmath()
                if y is not None:
                    yield y

        matrix = [list(to_numbers(data.elements)) for data in input]
        minima = [min(data) for data in matrix]
        maxima = [max(data) for data in matrix]
        max_bins = max(len(data) for data in matrix)

        minimum = min(minima)
        maximum = max(maxima)

        if minimum > 0:
            minimum = 0

        span = maximum - minimum

        from math import ceil

        from mpmath import ceil as mpceil, floor as mpfloor

        class Distribution:
            def __init__(self, data, n_bins):
                bin_width = span / n_bins
                bins = [0] * n_bins
                for x in data:
                    b = int(mpfloor((x - minimum) / bin_width))
                    if b < 0:
                        b = 0
                    elif b >= n_bins:
                        b = n_bins - 1
                    bins[b] += 1
                self.bins = bins
                self.bin_width = bin_width

            def n_bins(self):
                return len(self.bins)

            def cost(self):
                # see http://toyoizumilab.brain.riken.jp/hideaki/res/histogram.html
                bins = self.bins
                n_bins = len(bins)
                k = sum(bins) / n_bins
                v = sum(x * x for x in ((b - k) for b in bins)) / n_bins
                bin_width = self.bin_width
                return (2 * k - v) / (bin_width * bin_width)

            def graphics(self, color):
                bins = self.bins
                n_bins = len(bins)
                bin_width = self.bin_width

                def boxes():
                    x = minimum

                    for i, count in enumerate(bins):
                        x1 = x + bin_width
                        yield x, x1, count
                        x = minimum + ((i + 1) * span) / n_bins

                def rectangles():
                    yield Expression(
                        SymbolEdgeForm,
                        Expression(SymbolRGBColor, Integer0, Integer0, Integer0),
                    )

                    last_x1 = 0
                    style = to_expression(
                        SymbolRGBColor, *color, elements_conversion_fn=MachineReal
                    )

                    for x0, x1, y in boxes():
                        yield Expression(
                            SymbolStyle,
                            Expression(
                                SymbolRectangle,
                                to_mathics_list(x0, Integer0),
                                to_mathics_list(x1, y),
                            ),
                            style,
                        )

                        last_x1 = x1

                    yield Expression(
                        SymbolLine,
                        ListExpression(
                            ListExpression(Integer0, Integer0),
                            to_mathics_list(last_x1, Integer0),
                        ),
                    )

                return list(rectangles())

        def compute_cost(n_bins):
            distributions = [Distribution(data, n_bins) for data in matrix]
            return sum(d.cost() for d in distributions), distributions

        def best_distributions(n_bins, dir, cost0, distributions0):
            if dir > 0:
                step_size = (max_bins - n_bins) // 2
            else:
                step_size = (n_bins - 1) // 2
            if step_size < 1:
                step_size = 1

            while True:
                new_n_bins = n_bins + dir * step_size
                if new_n_bins < 1 or new_n_bins > max_bins:
                    good = False
                else:
                    cost, distributions = compute_cost(new_n_bins)
                    good = cost < cost0

                if not good:
                    if step_size == 1:
                        break
                    step_size = max(step_size // 2, 1)
                else:
                    n_bins = new_n_bins
                    cost0 = cost
                    distributions0 = distributions

            return cost0, distributions0

        def graphics(distributions):
            palette = palettable.wesanderson.FantasticFox1_5
            colors = list(reversed(palette.mpl_colors))

            from itertools import chain

            n_bins = distributions[0].n_bins()
            x_coords = [minimum + (i * span) / n_bins for i in range(n_bins + 1)]
            y_coords = [0] + list(
                chain(*[distribution.bins for distribution in distributions])
            )

            graphics = []
            for i, distribution in enumerate(distributions):
                color = colors[i % len(colors)]
                graphics.extend(list(chain(*[distribution.graphics(color)])))

            x_range = "System`All"
            y_range = "System`All"

            x_range = list(get_plot_range(x_coords, x_coords, x_range))
            y_range = list(get_plot_range(y_coords, y_coords, y_range))

            # always specify -.1 as the minimum x plot range, as this will make the y axis apppear
            # at origin (0,0); otherwise it will be shifted right; see GraphicsBox.axis_ticks().
            x_range[0] = -0.1

            options["System`PlotRange"] = from_python([x_range, y_range])

            return Expression(
                SymbolGraphics, ListExpression(*graphics), *options_to_rules(options)
            )

        def manual_bins(bspec, hspec):
            if isinstance(bspec, Integer):
                distributions = [
                    Distribution(data, bspec.get_int_value()) for data in matrix
                ]
                return graphics(distributions)
            elif bspec.get_head_name() == "System`List" and len(bspec.elements) == 1:
                bin_width = bspec[0].to_mpmath()
                distributions = [
                    Distribution(data, int(mpceil(span / bin_width))) for data in matrix
                ]
                return graphics(distributions)

        def auto_bins():
            # start with Rice's rule, see https://en.wikipedia.org/wiki/Histogram
            n_bins = int(ceil(2 * (max_bins ** (1.0 / 3.0))))

            # now optimize the bin size by going into both directions and looking
            # for local minima.

            cost0, distributions0 = compute_cost(n_bins)
            cost_r, distributions_r = best_distributions(
                n_bins, 1, cost0, distributions0
            )
            cost_l, distributions_l = best_distributions(
                n_bins, -1, cost0, distributions0
            )

            if cost_r < cost_l:
                distributions = distributions_r
            else:
                distributions = distributions_l

            return graphics(distributions)

        if not spec:
            return auto_bins()
        else:
            if len(spec) < 2:
                spec.append(None)
            return manual_bins(*spec)
        return Expression(
            SymbolGraphics,
            ListExpression(*graphics),
            *options_to_rules(options, Graphics.options)
        )


class ListPlot(_ListPlot):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ListPlot.html</url>
    <dl>
      <dt>'ListPlot[{$y_1$, $y_2$, ...}]'
      <dd>plots a list of y-values, assuming integer x-values 1, 2, 3, ...

      <dt>'ListPlot[{{$x_1$, $y_1$}, {$x_2$, $y_2$}, ...}]'
      <dd>plots a list of $x$, $y$ pairs.

      <dt>'ListPlot[{$list_1$, $list_2$, ...}]'
      <dd>plots several lists of points.
    </dl>

    The frequecy of Primes:
    >> ListPlot[Prime[Range[30]]]
     = -Graphics-

    seems very roughly to fit a table of quadradic numbers:
    >> ListPlot[Table[n ^ 2 / 8, {n, 30}]]
     = -Graphics-

    ListPlot accepts some Graphics options:

    >> ListPlot[Table[n ^ 2, {n, 30}], Joined->True]
     = -Graphics-

    Compare with <url>:'Plot':
    /doc/reference-of-built-in-symbols/graphics-drawing-and-images/plotting-data/plot/</url>.

    >> ListPlot[Table[n ^ 2, {n, 30}], Filling->Axis]
     = -Graphics-

    Compare with <url>:'Plot':
    /doc/reference-of-built-in-symbols/graphics-drawing-and-images/plotting-data/plot</url>.
    """

    options = Graphics.options.copy()
    options.update(
        {
            "Axes": "True",
            "AspectRatio": "1 / GoldenRatio",
            "Mesh": "None",
            "PlotRange": "Automatic",
            "PlotPoints": "None",
            "Filling": "None",
            "Joined": "False",
        }
    )
    summary_text = "plot lists of points"


class ListLinePlot(_ListPlot):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ListLinePlot.html</url>
    <dl>
      <dt>'ListLinePlot[{$y_1$, $y_2$, ...}]'
      <dd>plots a line through a list of $y$-values, assuming integer $x$-values 1, 2, 3, ...

      <dt>'ListLinePlot[{{$x_1$, $y_1$}, {$x_2$, $y_2$}, ...}]'
      <dd>plots a line through a list of $x$, $y$ pairs.

      <dt>'ListLinePlot[{$list_1$, $list_2$, ...}]'
      <dd>plots several lines.
    </dl>

    >> ListLinePlot[Table[{n, n ^ 0.5}, {n, 10}]]
     = -Graphics-

    ListPlot accepts a superset of the Graphics options.

    >> ListLinePlot[{{-2, -1}, {-1, -1}, {1, 3}}, Filling->Axis]
     = -Graphics-
    """

    attributes = A_HOLD_ALL | A_PROTECTED

    options = Graphics.options.copy()
    options.update(
        {
            "Axes": "True",
            "AspectRatio": "1 / GoldenRatio",
            "Mesh": "None",
            "PlotRange": "Automatic",
            "PlotPoints": "None",
            "Filling": "None",
            "Joined": "True",
        }
    )
    summary_text = "plot lines through lists of points"


class ListLogPlot(_ListPlot):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ListLogPlot.html</url>
    <dl>
      <dt>'ListLogPlot[{$y_1$, $y_2$, ...}]'
      <dd>log plots a list of y-values, assuming integer x-values 1, 2, 3, ...

      <dt>'ListLogPlot[{{$x_1$, $y_1$}, {$x_2$, $y_2$}, ...}]'
      <dd>log plots a list of $x$, $y$ pairs.

      <dt>'ListLogPlot[{$list_1$, $list_2$, ...}]'
      <dd>log plots several lists of points.
    </dl>

    Plotting table of Fibonacci numbers:
    >> ListLogPlot[Table[Fibonacci[n], {n, 10}]]
     = -Graphics-

    we see that Fibonacci numbers grow exponentially. So when \
    plotted using on a log scale the result fits \
    points of a sloped line.

    >> ListLogPlot[Table[n!, {n, 10}], Joined -> True]
     = -Graphics-
    """

    options = Graphics.options.copy()
    options.update(
        {
            "Axes": "True",
            "AspectRatio": "1 / GoldenRatio",
            "Mesh": "None",
            "PlotRange": "Automatic",
            "PlotPoints": "None",
            "Filling": "None",
            "Joined": "False",
        }
    )
    summary_text = "log plot lists of points"

    use_log_scale = True


class LogPlot(_Plot):
    """
    <url>:Semi-log plot:
    https://en.wikipedia.org/wiki/Semi-log_plot</url> \
    (<url>
    :WMA link:
    https://reference.wolfram.com/language/ref/LogPlot.html</url>)
    <dl>
      <dt>'LogPlot[$f$, {$x$, $xmin$, $xmax$}]'
      <dd>log plots $f$ with $x$ ranging from $xmin$ to $xmax$.

      <dt>'Plot[{$f1$, $f2$, ...}, {$x$, $xmin$, $xmax$}]'
      <dd>log plots several functions $f1$, $f2$, ...

    </dl>

    >> LogPlot[x^x, {x, 1, 5}]
     = -Graphics-

    >> LogPlot[{x^x, Exp[x], x!}, {x, 1, 5}]
     = -Graphics-

    """

    summary_text = "plot on a log scale curves of one or more functions"

    use_log_scale = True


class NumberLinePlot(_ListPlot):
    """
     <url>:WMA link:
     https://reference.wolfram.com/language/ref/NumberLinePlot.html</url>
     <dl>
       <dt>'NumberLinePlot[{$v_1$, $v_2$, ...}]'
       <dd>plots a list of values along a line.
     </dl>

     >> NumberLinePlot[Prime[Range[10]]]
      = -Graphics-

    Compare with:
     >> NumberLinePlot[Table[x^2, {x, 10}]]

      = -Graphics-
    """

    options = Graphics.options.copy()

    # This is ListPlot with some tweaks:
    # * remove the Y axis in display,
    # * set the Y value to a constant, and
    # * set the aspect ratio to reduce the distance above the
    #   x-axis
    options.update(
        {
            "Axes": "{True, False}",
            "AspectRatio": "1 / 10",
            "Mesh": "None",
            "PlotRange": "Automatic",
            "PlotPoints": "None",
            "Filling": "None",
            "Joined": "False",
        }
    )
    summary_text = "plot along a number line"

    use_log_scale = False

    def eval(self, values, evaluation: Evaluation, options: dict):
        "%(name)s[values_, OptionsPattern[%(name)s]]"

        # Fill in a Y value, and use the generic _ListPlot.eval().
        # Some graphics options have been adjusted above.
        points_list = [
            ListExpression(eval_N(value, evaluation), Integer1)
            for value in values.elements
        ]
        return _ListPlot.eval(self, ListExpression(*points_list), evaluation, options)


class PieChart(_Chart):
    """
    <url>:Pie Chart: https://en.wikipedia.org/wiki/Pie_chart</url> \
    (<url>:WMA link: https://reference.wolfram.com/language/ref/PieChart.html</url>)
    <dl>
      <dt>'PieChart[{$a1$, $a2$ ...}]'
      <dd>draws a pie chart with sector angles proportional to $a1$, $a2$, ....
    </dl>

    Drawing options include -
    Charting:
    <ul>
      <li>Mesh
      <li>PlotRange
      <li>ChartLabels
      <li>ChartLegends
      <li>ChartStyle
    </ul>

    PieChart specific:
    <ul>
      <li>Axes (default: False, False)
      <li>AspectRatio (default 1)
      <li>SectorOrigin: (default {Automatic, 0})
      <li>SectorSpacing" (default Automatic)
    </ul>

    A hypothetical comparison between types of pets owned:
    >> PieChart[{30, 20, 10}, ChartLabels -> {Dogs, Cats, Fish}]
     = -Graphics-

    A doughnut chart for a list of values:
    >> PieChart[{8, 16, 2}, SectorOrigin -> {Automatic, 1.5}]
     = -Graphics-

    A Pie chart with multiple datasets:
    >> PieChart[{{10, 20, 30}, {15, 22, 30}}]
     = -Graphics-

    Same as the above, but without gaps between the groups of data:
    >> PieChart[{{10, 20, 30}, {15, 22, 30}}, SectorSpacing -> None]
     = -Graphics-

    The doughnut chart above with labels on each of the 3 pieces:
    >> PieChart[{{10, 20, 30}, {15, 22, 30}}, ChartLabels -> {A, B, C}]
     = -Graphics-

    Negative values are removed, the data below is the same as {1, 3}:
    >> PieChart[{1, -1, 3}]
     = -Graphics-
    """

    never_monochrome = True
    options = _Chart.options.copy()
    options.update(
        {
            "Axes": "{False, False}",
            "AspectRatio": "1",
            "SectorOrigin": "{Automatic, 0}",
            "SectorSpacing": "Automatic",
        }
    )

    summary_text = "draw a pie chart"

    def _draw(self, data, color, evaluation, options: dict):
        data = [[max(0.0, x) for x in group] for group in data]

        sector_origin = self.get_option(options, "SectorOrigin", evaluation)
        if not sector_origin.has_form("List", 2):
            return
        sector_origin = eval_N(sector_origin, evaluation)

        orientation = sector_origin.elements[0]
        if (
            isinstance(orientation, Symbol)
            and orientation.get_name() == "System`Automatic"
        ):
            sector_phi = pi
            sector_sign = -1.0
        elif orientation.has_form("List", 2) and isinstance(
            orientation.elements[1], String
        ):
            sector_phi = orientation.elements[0].round_to_float()
            clock_name = orientation.elements[1].get_string_value()
            if clock_name == "Clockwise":
                sector_sign = -1.0
            elif clock_name == "Counterclockwise":
                sector_sign = 1.0
            else:
                return
        else:
            return

        sector_spacing = self.get_option(options, "SectorSpacing", evaluation)
        if isinstance(sector_spacing, Symbol):
            if sector_spacing.get_name() == "System`Automatic":
                sector_spacing = ListExpression(Integer0, TwoTenths)
            elif sector_spacing.get_name() == "System`None":
                sector_spacing = ListExpression(Integer0, Integer0)
            else:
                return
        if not sector_spacing.has_form("List", 2):
            return
        segment_spacing = 0.0  # not yet implemented; needs real arc graphics
        radius_spacing = max(0.0, min(1.0, sector_spacing.elements[1].round_to_float()))

        def vector2(x, y) -> ListExpression:
            return ListExpression(Real(x), Real(y))

        def radii():
            outer = 2.0
            inner = sector_origin.elements[1].round_to_float()
            n = len(data)

            d = (outer - inner) / n

            r0 = outer
            for i in range(n):
                r1 = r0 - d
                if i > 0:
                    r0 -= radius_spacing * d
                yield (r0, r1)
                r0 = r1

        def phis(values):
            s = sum(values)

            t = 0.0
            pi2 = pi * 2.0
            phi0 = pi
            spacing = sector_sign * segment_spacing / 2.0

            for k, value in enumerate(values):
                t += value
                phi1 = sector_phi + sector_sign * (t / s) * pi2

                yield (phi0 + spacing, phi1 - spacing)
                phi0 = phi1

        def segments():
            yield Expression(SymbolEdgeForm, Symbol("Black"))

            origin = vector2(0.0, 0.0)

            for values, (r0, r1) in zip(data, radii()):
                radius = vector2(r0, r0)

                n = len(values)

                for k, (phi0, phi1) in enumerate(phis(values)):
                    yield Expression(
                        SymbolStyle,
                        Expression(SymbolDisk, origin, radius, vector2(phi0, phi1)),
                        color(k + 1, n),
                    )

                if r1 > 0.0:
                    yield Expression(
                        SymbolStyle,
                        Expression(SymbolDisk, origin, vector2(r1, r1)),
                        Symbol("White"),
                    )

        def labels(names):
            yield Expression(SymbolFaceForm, Symbol("Black"))

            for values, (r0, r1) in zip(data, radii()):
                for name, (phi0, phi1) in zip(names, phis(values)):
                    r = (r0 + r1) / 2.0
                    phi = (phi0 + phi1) / 2.0
                    yield Expression(
                        SymbolText, name, vector2(r * cos(phi), r * sin(phi))
                    )

        graphics = list(segments())

        chart_labels = self.get_option(options, "ChartLabels", evaluation)
        if chart_labels.get_head_name() == "System`List":
            graphics.extend(list(labels(chart_labels.elements)))

        options["System`PlotRange"] = ListExpression(
            vector2(-2.0, 2.0), vector2(-2.0, 2.0)
        )

        return Expression(
            SymbolGraphics, ListExpression(*graphics), *options_to_rules(options)
        )


class Plot(_Plot):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/Plot.html</url>
    <dl>
      <dt>'Plot[$f$, {$x$, $xmin$, $xmax$}]'
      <dd>plots $f$ with $x$ ranging from $xmin$ to $xmax$.

      <dt>'Plot[{$f1$, $f2$, ...}, {$x$, $xmin$, $xmax$}]'
      <dd>plots several functions $f1$, $f2$, ...

    </dl>

    >> Plot[{Sin[x], Cos[x], x / 3}, {x, -Pi, Pi}]
     = -Graphics-

    >> Plot[Sin[x], {x, 0, 4 Pi}, PlotRange->{{0, 4 Pi}, {0, 1.5}}]
     = -Graphics-

    >> Plot[Tan[x], {x, -6, 6}, Mesh->Full]
     = -Graphics-

    >> Plot[x^2, {x, -1, 1}, MaxRecursion->5, Mesh->All]
     = -Graphics-

    >> Plot[Log[x], {x, 0, 5}, MaxRecursion->0]
     = -Graphics-

    >> Plot[Tan[x], {x, 0, 6}, Mesh->All, PlotRange->{{-1, 5}, {0, 15}}, MaxRecursion->10]
     = -Graphics-

    A constant function:
    >> Plot[3, {x, 0, 1}]
     = -Graphics-

    #> Plot[1 / x, {x, -1, 1}]
     = -Graphics-
    #> Plot[x, {y, 0, 2}]
     = -Graphics-

    #> Plot[{f[x],-49x/12+433/108},{x,-6,6}, PlotRange->{-10,10}, AspectRatio->{1}]
     = -Graphics-

    #> Plot[Sin[t],  {t, 0, 2 Pi}, PlotPoints -> 1]
     : Value of option PlotPoints -> 1 is not an integer >= 2.
     = Plot[Sin[t], {t, 0, 2 Pi}, PlotPoints -> 1]

    #> Plot[x*y, {x, -1, 1}]
     = -Graphics-
    """

    summary_text = "plot curves of one or more functions"

    @lru_cache()
    def _apply_fn(self, f: Callable, x_value):
        value = f(x_value)
        if value is not None:
            return (x_value, value)


class ParametricPlot(_Plot):
    """
    <url>
    :WMA link
    : https://reference.wolfram.com/language/ref/ParametricPlot.html</url>
    <dl>
      <dt>'ParametricPlot[{$f_x$, $f_y$}, {$u$, $umin$, $umax$}]'
      <dd>plots a parametric function $f$ with the parameter $u$ ranging from $umin$ to $umax$.

      <dt>'ParametricPlot[{{$f_x$, $f_y$}, {$g_x$, $g_y$}, ...}, {$u$, $umin$, $umax$}]'
      <dd>plots several parametric functions $f$, $g$, ...

      <dt>'ParametricPlot[{$f_x$, $f_y$}, {$u$, $umin$, $umax$}, {$v$, $vmin$, $vmax$}]'
      <dd>plots a parametric area.

      <dt>'ParametricPlot[{{$f_x$, $f_y$}, {$g_x$, $g_y$}, ...}, {$u$, $umin$, $umax$}, {$v$, $vmin$, $vmax$}]'
      <dd>plots several parametric areas.
    </dl>

    >> ParametricPlot[{Sin[u], Cos[3 u]}, {u, 0, 2 Pi}]
     = -Graphics-

    >> ParametricPlot[{Cos[u] / u, Sin[u] / u}, {u, 0, 50}, PlotRange->0.5]
     = -Graphics-

    >> ParametricPlot[{{Sin[u], Cos[u]},{0.6 Sin[u], 0.6 Cos[u]}, {0.2 Sin[u], 0.2 Cos[u]}}, {u, 0, 2 Pi}, PlotRange->1, AspectRatio->1]
    = -Graphics-
    """

    expect_list = True
    summary_text = "2D parametric curves or regions"

    def get_functions_param(self, functions):
        if functions.has_form("List", 2) and not (
            functions.elements[0].has_form("List", None)
            or functions.elements[1].has_form("List", None)
        ):
            # One function given
            functions = [functions]
        else:
            # Multiple Functions
            functions = list(functions.elements)
        return functions

    def get_plotrange(self, plotrange, start, stop):
        x_range = y_range = None
        if isinstance(plotrange, numbers.Real):
            plotrange = [[-plotrange, plotrange], [-plotrange, plotrange]]
        if plotrange == "System`Automatic":
            plotrange = ["System`Automatic", "System`Automatic"]
        elif plotrange == "System`All":
            plotrange = ["System`All", "System`All"]
        if isinstance(plotrange, list) and len(plotrange) == 2:
            if isinstance(plotrange[0], numbers.Real) and isinstance(  # noqa
                plotrange[1], numbers.Real
            ):
                x_range = [-plotrange[0], plotrange[1]]
                y_range = [-plotrange[1], plotrange[1]]
            else:
                x_range, y_range = plotrange
        return x_range, y_range

    @lru_cache()
    def _apply_fn(self, fn: Callable, x_value):
        value = fn(x_value)
        if value is not None and len(value) == 2:
            return value


class PolarPlot(_Plot):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/PolarPlot.html</url>
    <dl>
      <dt>'PolarPlot[$r$, {$t$, $t_min$, $t_max$}]'
      <dd>creates a polar plot of curve with radius $r$ as a function of angle $t$ \
      ranging from $t_min$ to $t_max$.
    </dl>

    In a Polar Plot, a <url>:polar coordinate system:
    https://en.wikipedia.org/wiki/Polar_coordinate_system</url> is used.

    A polar coordinate system is a two-dimensional coordinate system in which \
    each point on a plane  is determined by a distance from a reference point \
    and an angle from a reference direction.

    Here is a 5-blade propeller, or maybe a flower, using 'PolarPlot':

    >> PolarPlot[Cos[5t], {t, 0, Pi}]
     = -Graphics-

    The number of blades and be change by adjusting the $t$ multiplier.

    A slight change adding 'Abs' turns this a clump of grass:

    >> PolarPlot[Abs[Cos[5t]], {t, 0, Pi}]
     = -Graphics-


    Coils around a ring:
    >> PolarPlot[{1, 1 + Sin[20 t] / 5}, {t, 0, 2 Pi}]
     = -Graphics-

    A spring having 16 turns:
    >> PolarPlot[Sqrt[t], {t, 0, 16 Pi}]
     = -Graphics-
    """

    options = _Plot.options.copy()
    options.update(
        {
            "AspectRatio": "1",
        }
    )
    summary_text = "draw a polar plot"

    def get_functions_param(self, functions):
        if functions.has_form("List", None):
            functions = list(functions.elements)
        else:
            functions = [functions]
        return functions

    def get_plotrange(self, plotrange, start, stop):
        x_range = y_range = None
        if isinstance(plotrange, numbers.Real):
            plotrange = [[-plotrange, plotrange], [-plotrange, plotrange]]
        if plotrange == "System`Automatic":
            plotrange = ["System`Automatic", "System`Automatic"]
        elif plotrange == "System`All":
            plotrange = ["System`All", "System`All"]
        if isinstance(plotrange, list) and len(plotrange) == 2:
            if isinstance(plotrange[0], numbers.Real) and isinstance(  # noqa
                plotrange[1], numbers.Real
            ):
                x_range = [-plotrange[0], plotrange[1]]
                y_range = [-plotrange[1], plotrange[1]]
            else:
                x_range, y_range = plotrange
        return x_range, y_range

    @lru_cache()
    def _apply_fn(self, fn: Callable, x_value):
        value = fn(x_value)
        if value is not None:
            return (value * cos(x_value), value * sin(x_value))


class Plot3D(_Plot3D):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/Plot3D.html</url>
    <dl>
      <dt>'Plot3D[$f$, {$x$, $xmin$, $xmax$}, {$y$, $ymin$, $ymax$}]'
      <dd>creates a three-dimensional plot of $f$ with $x$ ranging from $xmin$ to $xmax$ and $y$ ranging from $ymin$ to $ymax$.

    </dl>

    Plot3D has the same options as Graphics3D, in particular:
    <ul>
    <li>Mesh
    <li>PlotPoints
    <li>MaxRecursion
    </ul>


    >> Plot3D[x ^ 2 + 1 / y, {x, -1, 1}, {y, 1, 4}]
     = -Graphics3D-

    >> Plot3D[Sin[y + Sin[3 x]], {x, -2, 2}, {y, -2, 2}, PlotPoints->20]
     = -Graphics3D-

    >> Plot3D[x / (x ^ 2 + y ^ 2 + 1), {x, -2, 2}, {y, -2, 2}, Mesh->None]
     = -Graphics3D-

    >> Plot3D[Sin[x y] /(x y), {x, -3, 3}, {y, -3, 3}, Mesh->All]
     = -Graphics3D-

    >> Plot3D[Log[x + y^2], {x, -1, 1}, {y, -1, 1}]
     = -Graphics3D-

    #> Plot3D[z, {x, 1, 20}, {y, 1, 10}]
     = -Graphics3D-

    ## MaxRecursion Option
    #> Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> 0]
     = -Graphics3D-
    #> Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> 15]
     = -Graphics3D-
    #> Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> 16]
     : MaxRecursion must be a non-negative integer; the recursion value is limited to 15. Using MaxRecursion -> 15.
     = -Graphics3D-
    #> Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> -1]
     : MaxRecursion must be a non-negative integer; the recursion value is limited to 15. Using MaxRecursion -> 0.
     = -Graphics3D-
    #> Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> a]
     : MaxRecursion must be a non-negative integer; the recursion value is limited to 15. Using MaxRecursion -> 0.
     = -Graphics3D-
    #> Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> Infinity]
     : MaxRecursion must be a non-negative integer; the recursion value is limited to 15. Using MaxRecursion -> 15.
     = -Graphics3D-

    #> Plot3D[x ^ 2 + 1 / y, {x, -1, 1}, {y, 1, z}]
     : Limiting value z in {y, 1, z} is not a machine-size real number.
     = Plot3D[x ^ 2 + 1 / y, {x, -1, 1}, {y, 1, z}]
    """

    # FIXME: This test passes but the result is 511 lines long !
    """
    #> Plot3D[x + 2y, {x, -2, 2}, {y, -2, 2}] // TeXForm
    """
    attributes = A_HOLD_ALL | A_PROTECTED

    options = Graphics.options.copy()
    options.update(
        {
            "Axes": "True",
            "AspectRatio": "1",
            "Mesh": "Full",
            "PlotPoints": "None",
            "BoxRatios": "{1, 1, 0.4}",
            "MaxRecursion": "2",
        }
    )
    summary_text = "plots 3D surfaces of one or more functions"

    def get_functions_param(self, functions):
        if functions.has_form("List", None):
            return functions.elements
        else:
            return [functions]

    def construct_graphics(
        self, triangles, mesh_points, v_min, v_max, options, evaluation: Evaluation
    ):
        graphics = []
        for p1, p2, p3 in triangles:
            graphics.append(
                Expression(
                    SymbolPolygon,
                    ListExpression(
                        to_mathics_list(*p1),
                        to_mathics_list(*p2),
                        to_mathics_list(*p3),
                    ),
                )
            )
        # Add the Grid
        for xi in range(len(mesh_points)):
            line = []
            for yi in range(len(mesh_points[xi])):
                line.append(
                    to_mathics_list(
                        mesh_points[xi][yi][0],
                        mesh_points[xi][yi][1],
                        mesh_points[xi][yi][2],
                    )
                )
            graphics.append(Expression(SymbolLine, ListExpression(*line)))
        return graphics

    def final_graphics(self, graphics, options: dict):
        return Expression(
            SymbolGraphics3D,
            ListExpression(*graphics),
            *options_to_rules(options, Graphics3D.options)
        )
