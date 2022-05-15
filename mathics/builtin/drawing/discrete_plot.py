# -*- coding: utf-8 -*-
import numbers


from mathics.builtin.drawing.plot import (
    Plot,
    check_plot_range,
    compile_quiet_function,
    get_plot_range,
)
from mathics.builtin.graphics import Graphics
from mathics.builtin.options import options_to_rules

from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED
from mathics.core.convert.python import from_python
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol, SymbolList
from mathics.core.systemsymbols import SymbolPlot


class _DiscretePlot(Plot):

    attributes = A_HOLD_ALL | A_PROTECTED

    options = Graphics.options.copy()
    options.update(
        {
            "Axes": "True",
            "AspectRatio": "1 / GoldenRatio",
            "PlotRange": "Automatic",
            "$OptionSyntax": "Strict",
        }
    )

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

    expect_list = False

    def eval(self, function, x, start, stop, evaluation, options):
        """%(name)s[function_, {x_Symbol, start_Integer, stop_Integer},
        OptionsPattern[%(name)s]]"""
        if isinstance(function, Symbol) and function.name is not x.get_name():
            rules = evaluation.definitions.get_ownvalues(function.name)
            for rule in rules:
                function = rule.apply(function, evaluation, fully=True)

        expr_limits = Expression(SymbolList, x, start, stop)
        expr = Expression(
            self.get_name(), function, expr_limits, *options_to_rules(options)
        )
        x_name = x.get_name()

        py_start = start.value
        py_stop = stop.value
        if py_start is None or py_stop is None:
            return evaluation.message(self.get_name(), "plln", stop, expr)
        if py_start >= py_stop:
            return evaluation.message(self.get_name(), "plld", expr_limits)

        plotrange_option = self.get_option(options, "PlotRange", evaluation)

        plotrange = plotrange_option.to_python(n_evaluation=evaluation)
        x_range, y_range = self.get_plotrange(plotrange, py_start, py_stop)
        if not check_plot_range(x_range, numbers.Real) or not check_plot_range(
            y_range, numbers.Real
        ):
            evaluation.message(self.get_name(), "prng", plotrange_option)
            x_range, y_range = [py_start, py_stop], "Automatic"

        # x_range and y_range are now either Automatic, All, or of the form [min, max]
        assert x_range in ("System`Automatic", "System`All") or isinstance(
            x_range, list
        )
        assert y_range in ("System`Automatic", "System`All") or isinstance(
            y_range, list
        )

        # PlotPoints Option
        # constants to generate colors

        def get_points_minmax(points):
            xmin = xmax = ymin = ymax = None
            for line in points:
                for x, y in line:
                    if xmin is None or x < xmin:
                        xmin = x
                    if xmax is None or x > xmax:
                        xmax = x
                    if ymin is None or y < ymin:
                        ymin = y
                    if ymax is None or y > ymax:
                        ymax = y
            return xmin, xmax, ymin, ymax

        base_plot_points = []  # list of points in base subdivision
        plot_points = []  # list of all plotted points
        graphics = []  # list of resulting graphics primitives

        points = []
        xvalues = []  # x value for each point in points
        cf = compile_quiet_function(function, [x_name], evaluation, self.expect_list)
        for x_value in range(py_start, py_stop):
            point = self.eval_f(cf, x_value)
            points.append(point)
            xvalues.append(x_value)

        x_range = get_plot_range(
            [xx for xx, yy in base_plot_points], [xx for xx, yy in plot_points], x_range
        )
        y_range = get_plot_range(
            [yy for xx, yy in base_plot_points], [yy for xx, yy in plot_points], y_range
        )

        graphics = from_python(points)

        options["System`PlotRange"] = from_python([x_range, y_range])
        options["System`Discrete"] = True

        return Expression(
            SymbolPlot,
            Expression(SymbolList, *graphics),
            # *options_to_rules(options)
        )


class DiscretePlot(_DiscretePlot):
    """
    <dl>
      <dt>'DiscretePlot[$f$, {$x$, $xmin$, $xmax$}]'
      <dd>plots $f$ with $x$ ranging from $xmin$ to $xmax$.

      <dt>'DiscretePlot[{$f1$, $f2$, ...}, {$x$, $xmin$, $xmax$}]'
      <dd>plots several functions $f1$, $f2$, ...

    </dl>

    >> DiscretePlot[PrimePi[k], {k, 1, 50}]
     = -Graphics-

    >> DiscretePlot[Sin[x], {x, 0, 4 Pi}, DiscretePlotRange->{{0, 4 Pi}, {0, 1.5}}]
     = -Graphics-

    >> DiscretePlot[Tan[x], {x, -6, 6}, Mesh->Full]
     = -Graphics-
    """
