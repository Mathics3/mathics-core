"""
Custom Plots

A Density plot is kind of <url>:heat map:https://en.wikipedia.org/wiki/Heat_map</url> that represents magnitude or individual values as a color.

Similar, is a Contour Plot which is a kind of <url>:contour map:https://en.wikipedia.org/wiki/Contour_line</url>.

A <url>:Surface plot:https://en.wikipedia.org/wiki/Plot_(graphics)#Surface_plot</url> ('Plot3D') shows its 3rd or "height" dimension in a way that is projected onto a 2-dimensional surface.

'ComplexPlot' and 'ComplexPlot3D' use color and to visualize complex-valued functions in two and three dimensions respectively.
"""

import numpy as np

from mathics.builtin.drawing.graphics3d import Graphics3D
from mathics.builtin.graphics import Graphics
from mathics.builtin.options import options_to_rules
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.systemsymbols import Symbol, SymbolPlotRange, SymbolSequence

from . import plot

# This tells documentation how to sort this module
sort_order = "mathics.builtin.custom-plots"


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
        "Exclusions": "Automatic",
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
        "Exclusions": "Automatic",
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
            dim = 3 if self.graphics_class is Graphics3D else 2
            ranges = ranges.elements if ranges.head is SymbolSequence else [ranges]
            plot_options = plot.PlotOptions(self, ranges, options, dim, evaluation)
        except ValueError:
            return None

        # TODO: consult many_functions variable set by subclass and error
        # if many_functions is False but multiple are supplied
        if functions.has_form("List", None):
            plot_options.functions = functions.elements
        else:
            plot_options.functions = [functions]

        # supply default value
        if plot_options.plot_points is None:
            default_plot_points = (200, 200) if plot.use_vectorized_plot else (7, 7)
            plot_options.plot_points = default_plot_points

        # subclass must set eval_function and graphics_class
        eval_function = plot.get_plot_eval_function(self.__class__)
        with np.errstate(all="ignore"):  # suppress numpy warnings
            graphics = eval_function(plot_options, evaluation)
        if not graphics:
            return

        # now we have a list of length dim
        # handle Automatic ~ {xmin,xmax} etc.
        # TODO: dowstream consumers might be happier if we used data range where applicable
        for i, (pr, r) in enumerate(zip(plot_options.plot_range, plot_options.ranges)):
            # TODO: this treats Automatic and Full as the same, which isn't quite right
            if isinstance(pr, (str, Symbol)) and not isinstance(r[1], complex):
                # extract {xmin,xmax} from {x,xmin,xmax}
                plot_options.plot_range[i] = r[1:]

        # unpythonize and update PlotRange option
        options[str(SymbolPlotRange)] = to_mathics_list(*plot_options.plot_range)

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

    summary_text = "plots one or more complex functions as a 3D surface"
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
    <url>:heat map:https://en.wikipedia.org/wiki/Heat_map</url> (<url>:WMA link: https://reference.wolfram.com/language/ref/DensityPlot.html</url>)
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
