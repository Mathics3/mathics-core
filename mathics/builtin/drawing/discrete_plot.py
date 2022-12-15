# -*- coding: utf-8 -*-
"""
Discrete Plot
"""
import numbers

from functools import lru_cache
from typing import Optional

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
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolList
from mathics.eval.nevaluator import eval_N
from mathics.eval.plot import eval_ListPlot


class _DiscretePlot(Plot):

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
        # One argument-form of DiscretePlot
        "DiscretePlot[expr_, {var_Symbol, nmin_Integer, nmax_Integer}]": "DiscretePlot[expr, {var, nmin, nmax, 1}]",
    }

    def eval(self, function, x, start, nmax, step, evaluation, options):
        """DiscretePlot[function_, {x_Symbol, start_Integer, nmax_Integer, step_Integer},
        OptionsPattern[DiscretePlot]]"""
        if isinstance(function, Symbol) and function.name is not x.get_name():
            rules = evaluation.definitions.get_ownvalues(function.name)
            for rule in rules:
                functions = rule.apply(function, evaluation, fully=True)

        if function.get_head_name() == "List":
            functions_param = self.get_functions_param(functions)
            for index, f in enumerate(functions_param):
                if isinstance(f, Symbol) and f.name is not x.get_name():
                    rules = evaluation.definitions.get_ownvalues(f.name)
                    for rule in rules:
                        f = rule.apply(f, evaluation, fully=True)
                functions_param[index] = f
            functions = functions.flatten_with_respect_to_head(SymbolList)

        expr_limits = ListExpression(x, start, nmax)
        # FIXME: arrange for self to have a .symbolname property or attribute
        expr = Expression(
            Symbol(self.get_name()), function, expr_limits, *options_to_rules(options)
        )
        function = self.get_functions_param(function)
        x_name = x.get_name()

        py_start = start.value
        py_nmax = nmax.value
        py_step = step.value
        if py_start is None or py_nmax is None:
            return evaluation.message(self.get_name(), "plln", nmax, expr)
        if py_start >= py_nmax:
            return evaluation.message(self.get_name(), "plld", expr_limits)

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

        # PlotPoints Option
        # constants to generate colors

        base_plot_points = []  # list of points in base subdivision
        plot_points = []  # list of all plotted points

        compiled_fn = compile_quiet_function(
            function[0], [x_name], evaluation, self.expect_list
        )

        @lru_cache
        def apply_fn(fn, x_value: int) -> Optional[float]:
            value = fn(x_value)
            if value is not None:
                value = float(value)
            return value

        for x_value in range(py_start, py_nmax, py_step):
            point = apply_fn(compiled_fn, x_value)
            plot_points.append((x_value, point))

        x_range = get_plot_range(
            [xx for xx, yy in base_plot_points], [xx for xx, yy in plot_points], x_range
        )
        y_values = [yy for xx, yy in plot_points]
        y_range = get_plot_range(y_values, y_values, option="System`All")

        options["System`PlotRange"] = from_python([x_range, y_range])
        options["System`Discrete"] = True

        return eval_ListPlot(
            plot_points,
            x_range,
            y_range,
            is_discrete_plot=True,
            is_joined_plot=False,
            filling=False,
            options=options,
        )


class DiscretePlot(_DiscretePlot):
    """
    <dl>
      <dt>'DiscretePlot[$expr$, {$x$, $n_max$}]'
      <dd>plots $expr$ with $x$ ranging from 1 to $n_max$.

      <dt>'DiscretePlot[$expr$, {$x$, $n_min$, $n_max$}]'
      <dd>plots $expr$ with $x$ ranging from $n_min$ to $n_max$.

      <dt>'DiscretePlot[$f$, {$x$, $n_min$, $n_max$, $dn$}]'
      <dd>plots $f$ with $x$ ranging from $n_min$ to $n_max$ usings steps $dn$.

    </dl>

    >> DiscretePlot[PrimePi[k], {k, 50}]
     = -Graphics-

    >> DiscretePlot[Sin[x], {x, 0, 4 Pi}, DiscretePlotRange->{{0, 4 Pi}, {0, 1.5}}]
     = -Graphics-

    >> DiscretePlot[Tan[x], {x, -6, 6}]
     = -Graphics-
    """

    summary_text = "discrete plot of a one-paremeter function"
