# -*- coding: utf-8 -*-
"""
Plotting Data

Plotting functions take a function as a parameter and data, often a range of \
points, as another parameter, and plot or show the function applied to the data.
"""

import numbers
from abc import ABC
from functools import lru_cache
import itertools
from math import cos, pi, sin
from typing import Callable, Optional

import palettable

from mathics.builtin.drawing.graphics3d import Graphics3D
from mathics.builtin.graphics import Graphics
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Integer, Integer0, Integer1, MachineReal, Real, String
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolList
from mathics.core.systemsymbols import (
    SymbolBlack,
    SymbolEdgeForm,
    SymbolGraphics,
    SymbolGraphics3D,
    SymbolLine,
    SymbolLog10,
    SymbolPolygon,
    SymbolRGBColor,
    SymbolRule,
    SymbolStyle,
    SymbolVertexColors,
)
from mathics.core.util import print_expression_tree
from mathics.eval.drawing.charts import draw_bar_chart, eval_chart
from mathics.eval.drawing.colors import COLOR_PALETTES, get_color_palette
from mathics.eval.drawing.plot import (
    ListPlotPairOfNumbersError,
    ListPlotType,
    check_plot_range,
    compile_quiet_function,
    eval_ListPlot,
    eval_Plot,
    get_filling_option,
    get_plot_range,
    get_plot_range_option,
)
from mathics.eval.drawing.plot3d import eval_Plot3D, eval_DensityPlot
from mathics.eval.nevaluator import eval_N

# This tells documentation how to sort this module
# Here we are also hiding "drawing" since this erroneously appears at the top level.
sort_order = "mathics.builtin.plotting-data"

SymbolDisk = Symbol("Disk")
SymbolFaceForm = Symbol("FaceForm")
SymbolRectangle = Symbol("Rectangle")
SymbolText = Symbol("Text")

TwoTenths = Real(0.2)
MTwoTenths = -TwoTenths


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
        return eval_chart(self, points, evaluation, options)


class _ListPlot(Builtin, ABC):
    """
    Base class for ListPlot, and ListLinePlot
    2-Dimensional plot a list of points in some fashion.
    """

    attributes = A_PROTECTED | A_READ_PROTECTED

    messages = {
        "joind": "Value of option Joined -> `1` is not True or False.",
        "lpn": "`1` is not a list of numbers or pairs of numbers.",
        "prng": (
            "Value of option PlotRange -> `1` is not All, Automatic or "
            "an appropriate list of range specifications."
        ),
    }

    use_log_scale = False

    def eval(self, points, evaluation: Evaluation, options: dict):
        "%(name)s[points_, OptionsPattern[%(name)s]]"

        class_name = self.__class__.__name__

        # Scale point values down by Log 10. Tick mark values will be adjusted to be 10^n in GraphicsBox.
        if self.use_log_scale:
            points = ListExpression(
                *(
                    Expression(SymbolLog10, point).evaluate(evaluation)
                    for point in points
                )
            )

        points = points.evaluate(evaluation)
        if not isinstance(points, ListExpression):
            evaluation.message(class_name, "lpn", points)
            return

        if not all(
            element.is_numeric(evaluation)
            or isinstance(element, ListExpression)
            or (1 <= len(element.elements) <= 2)
            or (len(element.elements) == 1 and isinstance(element[0], ListExpression))
            for element in points.elements
        ):
            evaluation.message(class_name, "lpn", points)
            return

        # If "points" is a literal value with a Python representation,
        # it has a ".value" attribute with a non-None value. So here,
        # we don't have to eval_N().to_python().

        all_points = (
            points.value
            if hasattr(points, "value") and points.value is not None
            else eval_N(points, evaluation).to_python()  # TODO: force tuple-ness?
        )

        # FIXME: arrange for self to have a .symbolname property or attribute
        expr = Expression(Symbol(self.get_name()), points, *options_to_rules(options))

        if class_name == "ListPlot":
            plot_type = ListPlotType.ListPlot
        elif class_name == "ListLinePlot":
            plot_type = ListPlotType.ListLinePlot
        elif class_name == "ListStepPlot":
            plot_type = ListPlotType.ListStepPlot
        else:
            plot_type = None

        x_range, y_range = get_plot_range_option(options, evaluation, self.get_name())
        filling = get_filling_option(options, evaluation)

        # Joined Option
        joined_option = self.get_option(options, "Joined", evaluation)
        is_joined_plot = joined_option.to_python()
        if is_joined_plot not in [True, False]:
            evaluation.message(class_name, "joind", joined_option, expr)
            is_joined_plot = False

        try:
            return eval_ListPlot(
                all_points,
                x_range,
                y_range,
                is_discrete_plot=False,
                is_joined_plot=is_joined_plot,
                filling=filling,
                use_log_scale=self.use_log_scale,
                list_plot_type=plot_type,
                options=options,
            )
        except ListPlotPairOfNumbersError:
            evaluation.message(class_name, "lpn", points)
            return


class _Plot(Builtin, ABC):
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
        """Get the numbers of parameters in a function"""
        if functions.has_form("List", None):
            functions = list(functions.elements)
        else:
            functions = [functions]
        return functions

    def get_plotrange(self, plotrange, start, stop):
        """Determine the plot range for each variable"""
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
        """Process the arguments of a plot expression."""
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

        x_range, y_range = get_plot_range_option(options, evaluation, self.get_name())
        return functions, x_name, py_start, py_stop, x_range, y_range, expr_limits, expr

# TODO: add more options
# TODO: generalize, use for other plots
class PlotOptions:

    # TODO: more precise types
    ranges: list
    mesh: str
    plotpoints: list
    maxdepth: int

    def __init__(self, expr, range_exprs, options, evaluation):
        
        # plot ranges
        # TODO: check length of range_expr
        # TODO: check type of name (should be Symbol)
        # TODO: check that upper limit > lower limit
        self.ranges = []
        for range_expr in range_exprs:
            name = range_expr.elements[0]
            range = [name]
            for limit_expr in range_expr.elements[1:3]:
                limit = limit_expr.to_python()
                if not isinstance(limit, (int,float)):
                    evaluation.message(expr.get_name(), "plln", limit_expr, range_expr)
                    raise ValueError()
                range.append(limit)
            self.ranges.append(range)

        # Mesh option
        mesh_option = expr.get_option(options, "Mesh", evaluation)
        mesh = mesh_option.to_python()
        if mesh not in ["System`None", "System`Full", "System`All"]:
            evaluation.message("Mesh", "ilevels", mesh_option)
            mesh = "System`Full"
        self.mesh = mesh

        # PlotPoints option
        plotpoints_option = expr.get_option(options, "PlotPoints", evaluation)
        plotpoints = plotpoints_option.to_python()
        def check_plotpoints(steps):
            if isinstance(steps, int) and steps > 0:
                return True
            return False
        if plotpoints == "System`None":
            plotpoints = (7, 7)
        elif check_plotpoints(plotpoints):
            plotpoints = (plotpoints, plotpoints)
        if not (
            isinstance(plotpoints, (list, tuple))
            and len(plotpoints) == 2
            and check_plotpoints(plotpoints[0])
            and check_plotpoints(plotpoints[1])
        ):
            evaluation.message(expr.get_name(), "invpltpts", plotpoints)
            plotpoints = (7, 7)
        self.plotpoints = plotpoints

        # MaxRecursion Option
        maxrec_option = expr.get_option(options, "MaxRecursion", evaluation)
        max_depth = maxrec_option.to_python()
        if isinstance(max_depth, int):
            if max_depth < 0:
                max_depth = 0
                evaluation.message(expr.get_name(), "invmaxrec", max_depth, 15)
            elif max_depth > 15:
                max_depth = 15
                evaluation.message(expr.get_name(), "invmaxrec", max_depth, 15)
            else:
                pass  # valid
        elif max_depth == float("inf"):
            max_depth = 15
            evaluation.message(expr.get_name(), "invmaxrec", max_depth, 15)
        else:
            max_depth = 0
            evaluation.message(expr.get_name(), "invmaxrec", max_depth, 15)
        self.max_depth = max_depth


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
        args,
        evaluation: Evaluation,
        options: dict,
    ):
        """%(name)s[args___, OptionsPattern[%(name)s]]"""

        # TODO: test error for too many, too few, no args

        # parse options, bailing out if anything is wrong
        try:
            plot_options = PlotOptions(self, args.elements[1:3], options, evaluation)
        except ValueError as oops:
            return None

        # ask the subclass to get one or more functions as appropriate
        plot_options.functions = self.get_functions_param(args.elements[0])

        # delegate to subclass
        return self.do_eval(plot_options, evaluation, options)


class BarChart(_Chart):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/BarChart.html</url>
    <dl>
        <dt>'BarChart'[{$b_1$, $b_2$ ...}]
        <dd>makes a bar chart with lengths $b_1$, $b_2$, ....
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
        """Draw a bar chart"""
        return draw_bar_chart(self, data, color, evaluation, options)


class ColorData(Builtin):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ColorData.html</url>
    <dl>
      <dt>'ColorData'["$name$"]
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

    palettes = COLOR_PALETTES

    def eval_directory(self, evaluation: Evaluation):
        "ColorData[]"
        return ListExpression(String("Gradients"))

    def eval(self, name, evaluation: Evaluation):
        "ColorData[name_String]"
        py_name = name.get_string_value()
        if py_name == "Gradients":
            return ListExpression(*[String(name) for name in self.palettes])
        palette = ColorData.palettes.get(py_name, None)
        if palette is None:
            evaluation.message("ColorData", "notent", name)
            return
        return palette.color_data_function(py_name)

    @staticmethod
    def colors(name, evaluation):
        """Get a color palette by its name"""
        return get_color_palette(name, evaluation)


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
      <dt>'DensityPlot'[$f$, {$x$, $x_{min}$, $x_{max}$}, {$y$, $y_{min}$, $y_{max}$}]
      <dd>plots a density plot of $f$ with $x$ ranging from $x_{min}$ to $x_{max}$ and $y$ ranging from $y_{min}$ to $y_{max}$.
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

    # TODO: error if more than one function here
    def get_functions_param(self, functions):
        """can only have one function"""
        return [functions]

    # called by superclass
    def do_eval(self, plot_options, evaluation, options):
        """called by superclass to call appropriate eval_* function"""
        # TODO: self and options needed b/c some options processing still done in DensityPlot
        graphics = eval_DensityPlot(self, plot_options, evaluation, options)
        graphics_expr = graphics.generate(options_to_rules(options, Graphics.options))
        return graphics_expr


class DiscretePlot(_Plot):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/DiscretePlot.html</url>
    <dl>
      <dt>'DiscretePlot'[$expr$, {$x$, $n_{max}$}]
      <dd>plots $expr$ with $x$ ranging from 1 to $n_{max}$.

      <dt>'DiscretePlot'[$expr$, {$x$, $n_{min}$, $n_{max}$}]
      <dd>plots $expr$ with $x$ ranging from $n_{min}$ to $n_{max}$.

      <dt>'DiscretePlot'[$expr$, {$x$, $n_{min}$, $n_{max}$, $dn$}]
      <dd>plots $expr$ with $x$ ranging from $n_{min}$ to $n_{max}$ usings steps $dn$.

      <dt>'DiscretePlot'[{$expr_1$, $expr_2$, ...}, ...]
      <dd>plots the values of all $expri$.
    </dl>

    The number of primes for a number $k$:
    >> DiscretePlot[PrimePi[k], {k, 1, 100}]
     = -Graphics-

    is about the same as 'Sqrt[k] * 2.5':
    >> DiscretePlot[2.5 Sqrt[k], {k, 100}]
     = -Graphics-

    Notice in the above that when the starting value, $n_{min}$,  is 1, we can \
    omit it.

    A plot can contain several functions, using the same parameter, here $x$:
    >> DiscretePlot[{Sin[Pi x/20], Cos[Pi x/20]}, {x, 0, 40}]
     = -Graphics-

    Compare with <url>:'Plot':
    /doc/reference-of-built-in-symbols/graphics-and-drawing/plotting-data/plot/</url>.
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
        # One-argument plot range form of DiscretePlot
        "DiscretePlot[expr_, {var_Symbol, nmax_Integer}, options___]": "DiscretePlot[expr, {var, 1, nmax, 1}, options]",
        # Two-argument plot range form of DiscretePlot
        "DiscretePlot[expr_, {var_Symbol, nmin_Integer, nmax_Integer}, options___]": "DiscretePlot[expr, {var, nmin, nmax, 1, options}]",
    }

    summary_text = "discrete plot of a one-parameter function"

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

        # List of graphics primitives that rendering will use to draw.
        # This includes the plot data, and overall graphics directives
        # like the Hue.

        for f in functions:
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
                [xx for xx, _ in base_plot_points],
                [xx for xx, _ in plot_points],
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
            list_plot_type=ListPlotType.DiscretePlot,
            options=options,
        )


class Histogram(Builtin):
    """
    <url>:Histogram: https://en.wikipedia.org/wiki/Histogram</url> \
    (<url>:WMA link: https://reference.wolfram.com/language/ref/ColorDataFunction.html</url>)

    <dl>
        <dt>'Histogram'[{$x_1$, $x_2$ ...}]
        <dd>plots a histogram using the values $x_1$, $x_2$, ....
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

        minimum = min(minimum, 0)

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
            step_size = max(step_size, 1)

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

            # always specify -.1 as the minimum x plot range, as this will make the y axis appear
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
            *options_to_rules(options, Graphics.options),
        )


class ListPlot(_ListPlot):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ListPlot.html</url>
    <dl>
      <dt>'ListPlot'[{$y_1$, $y_2$, ...}]
      <dd>plots a list of y-values, assuming integer x-values 1, 2, 3, ...

      <dt>'ListPlot'[{{$x_1$, $y_1$}, {$x_2$, $y_2$}, ...}]
      <dd>plots a list of $x$, $y$ pairs.

      <dt>'ListPlot'[{$list_1$, $list_2$, ...}]
      <dd>plots several lists of points.
    </dl>

    The frequency of Primes:
    >> ListPlot[Prime[Range[30]]]
     = -Graphics-

    seems very roughly to fit a table of quadratic numbers:
    >> ListPlot[Table[n ^ 2 / 8, {n, 30}]]
     = -Graphics-

    ListPlot accepts some Graphics options:

    >> ListPlot[Table[n ^ 2, {n, 30}], Joined->True]
     = -Graphics-

    Compare with <url>:'Plot':
    /doc/reference-of-built-in-symbols/graphics-and-drawing/plotting-data/plot/</url>.

    >> ListPlot[Table[n ^ 2, {n, 30}], Filling->Axis]
     = -Graphics-

    Compare with <url>:'Plot':
    /doc/reference-of-built-in-symbols/graphics-and-drawing/plotting-data/plot</url>.
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
      <dt>'ListLinePlot'[{$y_1$, $y_2$, ...}]
      <dd>plots a line through a list of $y$-values, assuming integer $x$-values 1, 2, 3, ...

      <dt>'ListLinePlot'[{{$x_1$, $y_1$}, {$x_2$, $y_2$}, ...}]
      <dd>plots a line through a list of $x$, $y$ pairs.

      <dt>'ListLinePlot'[{$list_1$, $list_2$, ...}]
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


class ListStepPlot(_ListPlot):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ListStepPlot.html</url>
    <dl>
      <dt>'ListStepPlot'[{$y_1$, $y_2$, ...}]
      <dd>plots a line through a list of $y$-values, assuming integer $x$-values 1, 2, 3, ...

      <dt>'ListStepPlot'[{{$x_1$, $y_1$}, {$x_2$, $y_2$}, ...}]
      <dd>plots a line through a list of $x$, $y$ pairs.

      <dt>'ListStepPlot'[{$list_1$, $list_2$, ...}]
      <dd>plots several lines.
    </dl>

    >> ListStepPlot[{1, 1, 2, 3, 5, 8, 13, 21}]
     = -Graphics-

    'ListStepPlot' accepts a superset of the Graphics options. \
    By default, 'ListStepPlot's are joined, but that can be disabled.

    >> ListStepPlot[{1, 1, 2, 3, 5, 8, 13, 21}, Joined->False]
     = -Graphics-

    The same as the first example but using a list of point as data, \
    and filling the plot to the x axis.

    >> ListStepPlot[{{1, 1}, {3, 2}, {4, 5}, {5, 8}, {6, 13}, {7, 21}}, Filling->Axis]
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
    summary_text = "plot values in steps"


class ListLogPlot(_ListPlot):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ListLogPlot.html</url>
    <dl>
      <dt>'ListLogPlot'[{$y_1$, $y_2$, ...}]
      <dd>log plots a list of y-values, assuming integer x-values 1, 2, 3, ...

      <dt>'ListLogPlot'[{{$x_1$, $y_1$}, {$x_2$, $y_2$}, ...}]
      <dd>log plots a list of $x$, $y$ pairs.

      <dt>'ListLogPlot'[{$list_1$, $list_2$, ...}]
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
      <dt>'LogPlot'[$f$, {$x$, $x_{min}$, $x_{max}$}]
      <dd>log plots $f$ with $x$ ranging from $x_{min}$ to $x_{max}$.

      <dt>'Plot'[{$f_1$, $f_2$, ...}, {$x$, $x_{min}$, $x_{max}$}]
      <dd>log plots several functions $f_1$, $f_2$, ...

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
       <dt>'NumberLinePlot'[{$v_1$, $v_2$, ...}]
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
      <dt>'PieChart'[{$a_1$, $a_2$ ...}]
      <dd>draws a pie chart with sector angles proportional to $a_1$, $a_2$, ....
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
            yield Expression(SymbolEdgeForm, SymbolBlack)

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
            yield Expression(SymbolFaceForm, SymbolBlack)

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
      <dt>'Plot'[$f$, {$x$, $x_{min}$, $x_{max}$}]
      <dd>plots $f$ with $x$ ranging from $x_{min}$ to $x_{max}$.

      <dt>'Plot'[{$f_1$, $f_2$, ...}, {$x$, $x_{min}$, $x_{max}$}]
      <dd>plots several functions $f_1$, $f_2$, ...

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
    :WMA link:\
    https://reference.wolfram.com/language/ref/ParametricPlot.html</url>
    <dl>
      <dt>'ParametricPlot'[{$f_x$, $f_y$}, {$u$, $u_{min}$, $u_{max}$}]
      <dd>plots a parametric function $f$ with the parameter $u$ ranging from $u_{min}$ to $u_{max}$.

      <dt>'ParametricPlot'[{{$f_x$, $f_y$}, {$g_x$, $g_y$}, ...}, {$u$, $u_{min}$, $u_{max}$}]
      <dd>plots several parametric functions $f$, $g$, ...

      <dt>'ParametricPlot'[{$f_x$, $f_y$}, {$u$, $u_{min}$, $u_{max}$}, {$v$, $v_{min}$, $v_{max}$}]
      <dd>plots a parametric area.

      <dt>'ParametricPlot'[{{$f_x$, $f_y$}, {$g_x$, $g_y$}, ...}, {$u$, $u_{min}$, $u_{max}$}, {$v$, $v_{min}$, $v_{max}$}]
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
      <dt>'PolarPlot'[$r$, {$t$, $t_{min}$, $t_{max}$}]
      <dd>creates a polar plot of curve with radius $r$ as a function of angle $t$ \
      ranging from $t_{min}$ to $t_{max}$.
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
      <dt>'Plot3D'[$f$, {$x$, $x_{min}$, $x_{max}$}, {$y$, $y_{min}$, $y_{max}$}]
      <dd>creates a three-dimensional plot of $f$ with $x$ ranging from $x_{min}$ to \
          $x_{max}$ and $y$ ranging from $y_{min}$ to $y_{max}$.

          See <url>:Drawing Option and Option Values:
    /doc/reference-of-built-in-symbols/graphics-and-drawing/drawing-options-and-option-values
    </url> for a list of Plot options.
    </dl>

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
        """May have a function or a list of functions"""
        if functions.has_form("List", None):
            return functions.elements
        else:
            return [functions]

    def do_eval(self, plot_options, evaluation, options):
        """called by superclass to call appropriate eval_* function"""
        graphics = eval_Plot3D(plot_options, evaluation)
        graphics_expr = graphics.generate(options_to_rules(options, Graphics3D.options))
        return graphics_expr

