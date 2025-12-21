import numbers
import os
from abc import ABC
from functools import lru_cache
from math import cos, pi, sin
from typing import Callable, Optional

import palettable

import mathics.eval.drawing.plot3d
import mathics.eval.drawing.plot3d_vectorized
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
    SymbolAll,
    SymbolAutomatic,
    SymbolBlack,
    SymbolEdgeForm,
    SymbolFull,
    SymbolGraphics,
    SymbolLine,
    SymbolLog10,
    SymbolNone,
    SymbolPlotRange,
    SymbolRGBColor,
    SymbolSequence,
    SymbolStyle,
)
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
from mathics.eval.nevaluator import eval_N

from . import plot

# This tells documentation how to sort this module
from .plot import sort_order

# TODO: add more options
# TODO: generalize, use for other plots
class PlotOptions:
    """
    Extract Options common to many types of plotting.
    This aims to reduce duplication of code,
    and to make it easier to pass options to eval_* routines.
    """

    # TODO: more precise types
    ranges: list
    mesh: str
    plotpoints: list
    maxdepth: int

    def error(self, what, *args, **kwargs):
        if not isinstance(what, str):
            what = what.get_name()
        self.evaluation.message(what, *args, **kwargs)
        raise ValueError()

    def __init__(self, expr, range_exprs, options, evaluation):
        self.evaluation = evaluation

        # plot ranges of the form {x,xmin,xmax} etc.
        self.ranges = []
        for range_expr in range_exprs:
            if not range_expr.has_form("List", 3):
                self.error(expr, "invrange", range_expr)
            if not isinstance(range_expr.elements[0], Symbol):
                self.error(expr, "invrange", range_expr)
            range = [range_expr.elements[0]]
            for limit_expr in range_expr.elements[1:3]:
                limit = eval_N(limit_expr, evaluation).to_python()
                if not isinstance(limit, (int, float, complex)):
                    self.error(expr, "plln", limit_expr, range_expr)
                range.append(limit)
            if isinstance(limit, (int, float)) and range[2] <= range[1]:
                self.error(expr, "invrange", range_expr)
            if isinstance(limit, complex) and (
                range[2].real <= range[1].real or range[2].imag <= range[1].imag
            ):
                self.error(expr, "invrange", range_expr)
            self.ranges.append(range)

        # Contours option
        contours = expr.get_option(options, "Contours", evaluation)
        if contours is not None:
            c = contours.to_python()
            if not (
                c == "System`Automatic"
                or isinstance(c, int)
                or isinstance(c, tuple)
                and all(isinstance(cc, (int, float)) for cc in c)
            ):
                self.error(expr, "invcontour", contours)
            self.contours = c

        # Mesh option
        mesh = expr.get_option(options, "Mesh", evaluation)
        if mesh not in (SymbolNone, SymbolFull, SymbolAll):
            evaluation.message("Mesh", "ilevels", mesh)
            mesh = SymbolFull
        self.mesh = mesh

        # PlotPoints option
        plotpoints_option = expr.get_option(options, "PlotPoints", evaluation)
        plotpoints = plotpoints_option.to_python()

        def check_plotpoints(steps):
            if isinstance(steps, int) and steps > 0:
                return True
            return False

        default_plotpoints = (200, 200) if plot.use_vectorized_plot else (7, 7)
        if plotpoints == "System`None":
            plotpoints = default_plotpoints
        elif check_plotpoints(plotpoints):
            plotpoints = (plotpoints, plotpoints)
        if not (
            isinstance(plotpoints, (list, tuple))
            and len(plotpoints) == 2
            and check_plotpoints(plotpoints[0])
            and check_plotpoints(plotpoints[1])
        ):
            evaluation.message(expr.get_name(), "invpltpts", plotpoints)
            plotpoints = default_plotpoints
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

        # ColorFunction and ColorFunctionScaling options
        # This was pulled from construct_density_plot (now eval_DensityPlot).
        # TODO: What does pop=True do? is it right?
        # TODO: can we move some of the subsequent processing in eval_DensityPlot to here?
        # TODO: what is the type of these? that may change if we do the above...
        self.color_function = expr.get_option(
            options, "ColorFunction", evaluation, pop=True
        )
        self.color_function_scaling = expr.get_option(
            options, "ColorFunctionScaling", evaluation, pop=True
        )


class _Plot3D(Builtin):
    """Common base class for Plot3D, DensityPlot, ComplexPlot, ComplexPlot3D"""

    attributes = A_HOLD_ALL | A_PROTECTED

    # Check for correct number of args
    eval_error = Builtin.generic_argument_error
    expected_args = 3

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
        "invrange": (
            "Plot range `1` must be of the form {variable, min, max}, "
            "where max > min."
        ),
        "invcontour": (
            "Contours option must be Automatic, an integer, or a list of numbers."
        ),
    }

    # Plot3D, ComplexPlot3D
    options3d = Graphics3D.options | {
        "Axes": "True",
        "AspectRatio": "1",
        "Mesh": "Full",
        "PlotPoints": "None",
        "BoxRatios": "{1, 1, 0.4}",
        "MaxRecursion": "2",
    }

    # DensityPlot, ComplexPlot
    options2d = Graphics.options | {
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

    def eval(
        self,
        functions,
        ranges,
        evaluation: Evaluation,
        options: dict,
    ):
        """%(name)s[functions_, ranges__, OptionsPattern[%(name)s]]"""

        # TODO: test error for too many, too few, no args

        # parse options, bailing out if anything is wrong
        try:
            ranges = ranges.elements if ranges.head is SymbolSequence else [ranges]
            plot_options = PlotOptions(self, ranges, options, evaluation)
        except ValueError:
            return None

        # TODO: consult many_functions variable set by subclass and error
        # if many_functions is False but multiple are supplied
        if functions.has_form("List", None):
            plot_options.functions = functions.elements
        else:
            plot_options.functions = [functions]

        # subclass must set eval_function and graphics_class
        eval_function = plot.get_plot_eval_function(self.__class__)
        graphics = eval_function(plot_options, evaluation)
        if not graphics:
            return

        # Expand PlotRange option using the {x,xmin,xmax} etc. range specifications
        # Pythonize it, so Symbol becomes str, numeric becomes int or float
        plot_range = self.get_option(options, str(SymbolPlotRange), evaluation)
        plot_range = plot_range.to_python()
        dim = 3 if self.graphics_class is Graphics3D else 2
        if isinstance(plot_range, str):
            # PlotRange -> Automatic becomes PlotRange -> {Automatic, ...}
            plot_range = [str(SymbolAutomatic)] * dim
        if isinstance(plot_range, (int, float)):
            # PlotRange -> s becomes PlotRange -> {Automatic,...,{-s,s}}
            pr = plot_range
            plot_range = [str(SymbolAutomatic)] * dim
            plot_range[-1] = [-pr, pr]
        elif isinstance(plot_range, (list, tuple)) and isinstance(
            plot_range[0], (int, float)
        ):
            # PlotRange -> {s0,s1} becomes  PlotRange -> {Automatic,...,{s0,s1}}
            pr = plot_range
            plot_range = [str(SymbolAutomatic)] * dim
            plot_range[-1] = pr

        # now we have a list of length dim
        # handle Automatic ~ {xmin,xmax} etc.
        for i, (pr, r) in enumerate(zip(plot_range, plot_options.ranges)):
            # TODO: this treats Automatic and Full as the same, which isn't quite right
            if isinstance(pr, str) and not isinstance(r[1], complex):
                plot_range[i] = r[1:]  # extract {xmin,xmax} from {x,xmin,xmax}

        # unpythonize and update PlotRange option
        options[str(SymbolPlotRange)] = to_mathics_list(*plot_range)

        # generate the Graphics[3D] result
        graphics_expr = graphics.generate(
            options_to_rules(options, self.graphics_class.options)
        )
        return graphics_expr


class ComplexPlot3D(_Plot3D):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ComplexPlot3D.html</url>
    <dl>
      <dt>'Plot3D'[$f$, {$z$, $z_{min}$, $z_{max}$}]
      <dd>creates a three-dimensional plot of the magnitude of $f$ with $z$ ranging from $z_{min}$ to \
          $z_{max}$ with surface colored according to phase

          See <url>:Drawing Option and Option Values:
    /doc/reference-of-built-in-symbols/graphics-and-drawing/drawing-options-and-option-values
    </url> for a list of Plot options.
    </dl>

    """

    summary_text = "plots one or more complex functions as a surface"
    expected_args = 2
    options = _Plot3D.options3d | {"Mesh": "None"}

    many_functions = True
    graphics_class = Graphics3D


class ComplexPlot(_Plot3D):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ComplexPlot.html</url>
    <dl>
      <dt>'Plot3D'[$f$, {$z$, $z_{min}$, $z_{max}$}]
      <dd>creates two-dimensional plot of $f$ with $z$ ranging from $z_{min}$ to \
          $z_{max}$ colored according to phase

          See <url>:Drawing Option and Option Values:
    /doc/reference-of-built-in-symbols/graphics-and-drawing/drawing-options-and-option-values
    </url> for a list of Plot options.
    </dl>

    """

    summary_text = "plots a complex function showing phase using colors"
    expected_args = 2
    options = _Plot3D.options2d

    many_functions = False
    graphics_class = Graphics


class ContourPlot(_Plot3D):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/ContourPlot.html</url>
    <dl>
      <dt>'Contour'[$f$, {$x$, $x_{min}$, $x_{max}$}, {$y$, $y_{min}$, $y_{max}$}]
      <dd>creates a two-dimensional contour plot ofh $f$ over the region
          $x$ ranging from $x_{min}$ to $x_{max}$ and $y$ ranging from $y_{min}$ to $y_{max}$.

          See <url>:Drawing Option and Option Values:
    /doc/reference-of-built-in-symbols/graphics-and-drawing/drawing-options-and-option-values
    </url> for a list of Plot options.
    </dl>

    """

    requires = ["skimage"]
    summary_text = "creates a contour plot"
    expected_args = 3
    options = _Plot3D.options2d | {"Contours": "Automatic"}
    # TODO: other options?

    many_functions = True
    graphics_class = Graphics


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

    summary_text = "density plot for a function"
    expected_args = 3
    options = _Plot3D.options2d

    many_functions = False
    graphics_class = Graphics




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

    summary_text = "plots 3D surfaces of one or more functions"
    expected_args = 3
    options = _Plot3D.options3d

    many_functions = True
    graphics_class = Graphics3D
