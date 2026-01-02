# -*- coding: utf-8 -*-
"""
Plotting Data

Plotting functions take a function as a parameter and data, often a range of \
points, as another parameter, and plot or show the function applied to the data.
"""

import os

import palettable

import mathics.eval.drawing.plot3d
import mathics.eval.drawing.plot3d_vectorized
from mathics.builtin.graphics import Graphics
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Integer, Integer0, MachineReal, String
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED
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
    SymbolEdgeForm,
    SymbolFull,
    SymbolGraphics,
    SymbolLine,
    SymbolNone,
    SymbolPlotRange,
    SymbolRGBColor,
    SymbolStyle,
)
from mathics.eval.drawing.colors import COLOR_PALETTES, get_color_palette
from mathics.eval.drawing.plot import get_plot_range
from mathics.eval.nevaluator import eval_N

# The vectorized plot function generates GraphicsComplex using NumericArray,
# which no consumer will currently understand. So lets make it opt-in for now.
# If it remains opt-in we'll probably want some combination of env variables,
# Set option such as $UseVectorizedPlot, and maybe a non-standard Plot3D option.
# For now an env variable is simplest.
# TODO: work out exactly how to deploy.


# can be set via environment variable at startup time,
# or changed dynamically by setting the use_vectorized_plot flag
use_vectorized_plot = os.getenv("MATHICS3_USE_VECTORIZED_PLOT", False)


# get the plot eval function for the given class,
# depending on whether vectorized plot functions are enabled
def get_plot_eval_function(cls):
    function_name = "eval_" + cls.__name__
    plot_module = (
        mathics.eval.drawing.plot3d_vectorized
        if use_vectorized_plot
        else mathics.eval.drawing.plot3d
    )
    fun = getattr(plot_module, function_name)
    return fun


# This tells documentation how to sort this module
# Here we are also hiding "drawing" since this erroneously appears at the top level.
sort_order = "mathics.builtin.plotting-data"

SymbolRectangle = Symbol("Rectangle")


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


#
# TODO: because of the history of this code, it's very inconsistent about
# strings vs symbols. Keep moving it towards Symbols.
#
# Some of this is because to_python is convenient because it turns List into list,
# but it also turns Symbols to str. Maybe needs an option not to do that, e.g.
# to_python(preserve_symbols=True)
#
class PlotOptions:
    """
    Extract Options common to many types of plotting.
    This aims to reduce duplication of code,
    and to make it easier to pass options to eval_* routines.
    """

    # TODO: more precise types
    ranges: list
    mesh: str
    plot_points: list
    maxdepth: int

    def __init__(self, builtin, functions, range_exprs, options, dim, evaluation):
        def error(*args, **kwargs):
            evaluation.message(builtin.get_name(), *args, **kwargs)
            raise ValueError()

        # convert functions to list of lists of exprs
        def to_list(expr):
            if isinstance(expr, Expression) and expr.head is SymbolList:
                return [to_list(e) for e in expr.elements]
            else:
                return expr

        functions = to_list(functions)
        self.functions = functions if isinstance(functions, list) else [functions]

        # plot ranges of the form {x,xmin,xmax} etc. (returns Symbol)
        self.ranges = []
        for i, range_expr in enumerate(range_exprs):
            if isinstance(range_expr, Symbol) and hasattr(builtin, "default_ranges"):
                self.ranges.append([range_expr, *builtin.default_ranges[i]])
                continue
            if not range_expr.has_form("List", 3):
                error("invrange", range_expr)
            if not isinstance(range_expr.elements[0], Symbol):
                error("invrange", range_expr)
            range = [range_expr.elements[0]]
            for limit_expr in range_expr.elements[1:3]:
                limit = eval_N(limit_expr, evaluation).to_python()
                if not isinstance(limit, (int, float, complex)):
                    error("plln", limit_expr, range_expr)
                range.append(limit)
            if isinstance(limit, (int, float)) and range[2] <= range[1]:
                error("invrange", range_expr)
            if isinstance(limit, complex) and (
                range[2].real <= range[1].real or range[2].imag <= range[1].imag
            ):
                error("invrange", range_expr)
            self.ranges.append(range)

        # Contours option (returns str)
        contours = builtin.get_option(options, "Contours", evaluation)
        if contours is not None:
            c = contours.to_python()
            if not (
                c == "System`Automatic"
                or isinstance(c, int)
                or isinstance(c, tuple)
                and all(isinstance(cc, (int, float)) for cc in c)
            ):
                error("invcontour", contours)
            self.contours = c

        # Supports None, Automatic, or list of numbers
        # TODO Turn expressions into points E.g. Sin[x] == 0 becomes 0, 2 Pi...
        # (returns Symbol)
        exclusions_option = builtin.get_option(options, "Exclusions", evaluation)
        exclusions = eval_N(exclusions_option, evaluation).to_python(
            preserve_symbols=True
        )
        if exclusions in (SymbolNone, SymbolAutomatic):
            pass
        elif isinstance(exclusions, (int, float)):
            exclusions = [exclusions]
        elif isinstance(exclusions, (list, tuple)):
            if not all(isinstance(e, (int, float)) for e in exclusions):
                error("invexcl", exclusions_option)
        else:
            error("invexcl", exclusions_option)
        self.exclusions = exclusions

        # Mesh option (returns Symbol)
        mesh = builtin.get_option(options, "Mesh", evaluation).to_python(
            preserve_symbols=True
        )
        if isinstance(mesh, (list, tuple)) and all(isinstance(m, int) for m in mesh):
            self.mesh = mesh
        elif mesh not in (SymbolNone, SymbolFull, SymbolAll):
            evaluation.message("Mesh", "ilevels", mesh)
            self.mesh = SymbolFull
        else:
            self.mesh = mesh

        # PlotPoints option (returns Symbol)
        plot_points_option = builtin.get_option(options, "PlotPoints", evaluation)
        pp = plot_points_option.to_python(preserve_symbols=True)
        npp = builtin.num_plot_points if hasattr(builtin, "num_plot_points") else len(self.ranges)
        if pp == SymbolNone:
            pp = None
        else:
            if not isinstance(pp, (tuple, list)):
                pp = (pp,) * npp
            if not (
                isinstance(pp, (list, tuple))
                and len(pp) == npp
                and all(isinstance(p, int) and p >= 2 for p in pp)
            ):
                error("invpltpts", plot_points_option)
                pp = None
            elif npp == 1:
                pp = pp[0]
        self.plot_points = pp

        # MaxRecursion Option
        maxrec_option = builtin.get_option(options, "MaxRecursion", evaluation)
        max_depth = maxrec_option.to_python()
        if isinstance(max_depth, int):
            if max_depth < 0:
                max_depth = 0
                evaluation.message(builtin.get_name(), "invmaxrec", max_depth, 15)
            elif max_depth > 15:
                max_depth = 15
                evaluation.message(builtin.get_name(), "invmaxrec", max_depth, 15)
            else:
                pass  # valid
        elif max_depth == float("inf"):
            max_depth = 15
            evaluation.message(builtin.get_name(), "invmaxrec", max_depth, 15)
        else:
            max_depth = 0
            evaluation.message(builtin.get_name(), "invmaxrec", max_depth, 15)
        self.max_depth = max_depth

        # PlotRange option
        # Normalize to always return a list of either numeric,
        # Symbol (for vectorized plots), or str (for classic plogs)
        # TODO: convert classic plots to use Symbol instead of str also
        if use_vectorized_plot:
            preserve_symbols = True
            symbol_type = Symbol
        else:
            # TODO: get rid of these
            preserve_symbols = False
            symbol_type = str
        plot_range = builtin.get_option(options, str(SymbolPlotRange), evaluation)
        plot_range = eval_N(plot_range, evaluation).to_python(
            preserve_symbols=preserve_symbols
        )
        if isinstance(plot_range, symbol_type):
            # PlotRange -> Automatic becomes PlotRange -> {Automatic, ...}
            plot_range = [plot_range] * dim
        if isinstance(plot_range, (int, float)):
            # PlotRange -> s becomes PlotRange -> {Automatic,...,{-s,s}}
            pr = float(plot_range)
            plot_range = [symbol_type("System`Automatic")] * dim
            plot_range[-1] = [-pr, pr]
            if builtin.get_name() == "System`ParametricPlot":
                plot_range[0] = [-pr, pr]
        elif isinstance(plot_range, (list, tuple)) and isinstance(
            plot_range[0], (int, float)
        ):
            # PlotRange -> {s0,s1} becomes  PlotRange -> {Automatic,...,{s0,s1}}
            pr = plot_range
            plot_range = [symbol_type("System`Automatic")] * dim
            plot_range[-1] = pr
        self.plot_range = plot_range

        # ColorFunction and ColorFunctionScaling options
        # This was pulled from construct_density_plot (now eval_DensityPlot).
        # TODO: What does pop=True do? is it right?
        # TODO: can we move some of the subsequent processing in eval_DensityPlot to here?
        # TODO: what is the type of these? that may change if we do the above...
        self.color_function = builtin.get_option(
            options, "ColorFunction", evaluation, pop=True
        )
        self.color_function_scaling = builtin.get_option(
            options, "ColorFunctionScaling", evaluation, pop=True
        )
