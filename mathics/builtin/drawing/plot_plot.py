"""
General Graphical Plots

A graphical plot displays information about functions or points.
"""

from abc import ABC
from functools import lru_cache
from typing import Callable, Optional

import numpy as np

from mathics.builtin.graphics import Graphics
from mathics.builtin.options import options_to_rules
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolList
from mathics.core.systemsymbols import SymbolPlotRange, SymbolSequence
from mathics.eval.drawing.plot import ListPlotType, eval_Plot
from mathics.eval.drawing.plot_vectorized import eval_Plot_vectorized
from mathics.eval.nevaluator import eval_N

from . import plot

# This tells documentation how to sort this module
sort_order = "mathics.builtin.graphical-plot"


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
        "invpltpts": "Value of option PlotPoints -> `1` is not an integer >= 2.",
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
            "MaxRecursion": "3",
            "Mesh": "None",
            "PlotRange": "Automatic",
            "PlotPoints": "None",
            "Exclusions": "Automatic",
            "$OptionSyntax": "Strict",
        }
    )

    def apply_function(self, f: Callable, x_value):
        value = f(x_value)
        if value is not None:
            return (x_value, value)

    def eval(self, functions, ranges, evaluation: Evaluation, options: dict):
        """%(name)s[functions_, ranges__,  OptionsPattern[%(name)s]]"""

        # parse options, bailing out if anything is wrong
        try:
            ranges = ranges.elements if ranges.head is SymbolSequence else [ranges]
            plot_options = plot.PlotOptions(self, ranges, options, 2, evaluation)
        except ValueError:
            return None

        # for classic plot we cache results, but for vectorized we can't
        # because ndarray is unhashable, and in any case probably isn't useful
        # TODO: does caching results in the classic case have demonstrable performance benefit?
        apply_function = self.apply_function
        if not plot.use_vectorized_plot:
            apply_function = lru_cache(apply_function)

        # additional options specific to this class
        plot_options.functions = self.get_functions_param(functions)
        plot_options.apply_function = apply_function
        plot_options.use_log_scale = self.use_log_scale
        plot_options.expect_list = self.expect_list
        if plot_options.plot_points is None:
            default_plot_points = 1000 if plot.use_vectorized_plot else 57
            plot_options.plot_points = default_plot_points

        # pass through the expanded plot_range options
        options[str(SymbolPlotRange)] = to_mathics_list(*plot_options.plot_range)

        # this will be either the vectorized or the classic eval function
        eval_function = eval_Plot_vectorized if plot.use_vectorized_plot else eval_Plot
        graphics = eval_function(plot_options, options, evaluation)
        return graphics

    def get_functions_param(self, functions):
        """Get the numbers of parameters in a function"""
        if functions.has_form("List", None):
            functions = list(functions.elements)
        else:
            functions = [functions]
        return functions


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

    def apply_function(self, f: Callable, x_value):
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

    def apply_function(self, fn: Callable, x_value):
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

    def apply_function(self, fn: Callable, x_value):
        value = fn(x_value)
        if value is not None:
            # use np.sin and np.cos to support vectorized plot
            return (value * np.cos(x_value), value * np.sin(x_value))
