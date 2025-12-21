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

# This tells documentation how to sort this module
from .plot import sort_order

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

