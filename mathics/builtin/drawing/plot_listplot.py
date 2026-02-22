"""
List Plots


List plots graph discrete points on a coordinate system.
"""

import numbers
from abc import ABC
from functools import lru_cache
from typing import Callable, Optional

from mathics.builtin.graphics import Graphics
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Integer1
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolList
from mathics.core.systemsymbols import SymbolLog10
from mathics.eval.drawing.plot import (
    ListPlotPairOfNumbersError,
    ListPlotType,
    check_plot_range,
    compile_quiet_function,
    eval_ListPlot,
    get_filling_option,
    get_plot_range,
    get_plot_range_option,
)
from mathics.eval.nevaluator import eval_N

# This tells documentation how to sort this module
sort_order = "mathics.builtin.plotting-data"


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
    /doc/reference-of-built-in-symbols/plotting-graphing-and-drawing/general-graphical-plots/plot/</url>.

    >> ListPlot[Table[n ^ 2, {n, 30}], Filling->Axis]
     = -Graphics-

    Compare with <url>:'Plot':
    /doc/reference-of-built-in-symbols/plotting-graphing-and-drawing/general-graphical-plots/plot</url>.
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


class DiscretePlot(_ListPlot):
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
    /doc/reference-of-built-in-symbols/plotting-graphing-and-drawing/general-graphical-plots/plot/</url>.
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

    def get_functions_param(self, functions):
        """Get the numbers of parameters in a function"""
        if functions.has_form("List", None):
            functions = list(functions.elements)
        else:
            functions = [functions]
        return functions
