import numbers
from abc import ABC
from functools import lru_cache
from math import cos, sin
from typing import Callable, Optional

from mathics.builtin.graphics import Graphics
from mathics.builtin.options import options_to_rules
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolList
from mathics.core.systemsymbols import (
    SymbolAll,
    SymbolAutomatic,
    SymbolFull,
    SymbolNone,
)
from mathics.eval.drawing.plot import (
    ListPlotType,
    check_plot_range,
    compile_quiet_function,
    eval_ListPlot,
    eval_Plot,
    get_plot_range,
    get_plot_range_option,
)
from mathics.eval.nevaluator import eval_N

# This tells documentation how to sort this module
from .plot import sort_order # noqa


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
        if mesh_option not in (SymbolNone, SymbolFull, SymbolAll):
            evaluation.message("Mesh", "ilevels", mesh_option)
            mesh = "System`None"
        else:
            mesh = mesh_option.to_python()

        # PlotPoints Option
        plotpoints_option = self.get_option(options, "PlotPoints", evaluation)
        if plotpoints_option is SymbolNone:
            plotpoints = 57
        else:
            plotpoints = plotpoints_option.to_python()
        if not (isinstance(plotpoints, int) and plotpoints >= 2):
            evaluation.message(self.get_name(), "ppts", plotpoints)
            return

        # MaxRecursion Option
        max_recursion_limit = 15
        maxrecursion_option = self.get_option(options, "MaxRecursion", evaluation)

        # Investigate whether the maxrecursion value is optimal. Bruce
        # Lucas observes that in some cases, using more points and
        # decreasing recursion is faster and gives better results.
        # Note that the tradeoff may be different for Plot versus
        # Plot3D. Recursive subdivision in Plot3D is probably a lot
        # harder.
        maxrecursion = 3

        try:
            if maxrecursion_option is not SymbolAutomatic:
                maxrecursion = maxrecursion_option.to_python()
                if maxrecursion == float("inf"):
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
                self.get_name(), "invmaxrec", maxrecursion_option, max_recursion_limit
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
        # TODO Turn expressions into points E.g. Sin[x] == 0 becomes 0, 2 Pi...

        if exclusions_option in (SymbolNone, (SymbolNone,)):
            exclusions = "System`None"
        else:
            exclusions = eval_N(exclusions_option, evaluation).to_python()
            if not isinstance(exclusions, list):
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
