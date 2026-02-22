"""
Vectorized evaluation routines for Plot and related subclasses of _Plot
"""

import numpy as np

from mathics.builtin.graphics import Graphics
from mathics.builtin.options import filter_from_iterable, options_to_rules
from mathics.core.convert.lambdify import lambdify_compile
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import SymbolList, strip_context
from mathics.timing import Timer

from .colors import palette2, palette_color_directive
from .util import GraphicsGenerator


@Timer("eval_Plot_vectorized")
def eval_Plot_vectorized(plot_options, options, evaluation: Evaluation):
    # Note on naming: we use t to refer to the independent variable initially.
    # For Plot etc. it will be x, but for ParametricPlot it is better called t,
    # and for PolarPlot theta. After we call the apply_function supplied by
    # the plotting class we will then have actual plot coordinate xs and ys.
    tname, tmin, tmax = plot_options.ranges[0]
    nt = plot_options.plot_points

    # ParametricPlot passes a List of two functions, but lambdify_compile doesn't handle that
    # TODO: we should be receiving this as a Python list not an expression List?
    # TODO: can lambidfy_compile handle list with an appropriate to_sympy?
    def compile_maybe_list(evaluation, function, names):
        if isinstance(function, Expression) and function.head == SymbolList:
            fs = [lambdify_compile(evaluation, f, names) for f in function.elements]

            def compiled(vs):
                return [f(vs) for f in fs]

        else:
            compiled = lambdify_compile(evaluation, function, names)
        return compiled

    # compile the functions
    with Timer("compile"):
        names = [strip_context(str(tname))]
        compiled_functions = [
            compile_maybe_list(evaluation, function, names)
            for function in plot_options.functions
        ]

    # compute requested regularly spaced points over the requested range
    ts = np.linspace(tmin, tmax, nt)

    # 1-based indexes into point array to form a line
    line = np.arange(nt) + 1

    # compute the curves and accumulate in a GraphicsGenerator
    graphics = GraphicsGenerator(dim=2)
    for i, function in enumerate(compiled_functions):
        # compute xs and ys from ts using the compiled function
        # and the apply_function supplied by the plot class
        with Timer("compute xs and ys"):
            xs, ys = plot_options.apply_function(function, ts)

        # sometimes expr gets compiled into something that returns a complex
        # even though the imaginary part is 0
        # TODO: check that imag is all 0?
        # assert np.all(np.isreal(zs)), "array contains complex values"
        xs = np.real(xs)
        ys = np.real(ys)

        # take log if requested; downstream axes will adjust accordingly
        if plot_options.use_log_scale:
            ys = np.log10(ys)

        # if it's a constant, make it a full array
        if isinstance(xs, (float, int, complex)):
            xs = np.full(ts.shape, xs)
        if isinstance(ys, (float, int, complex)):
            ys = np.full(ts.shape, ys)

        # (nx, 2) array of points, to be indexed by lines
        xys = np.stack([xs, ys]).T

        # give it a color from the 2d graph default color palette
        color = palette_color_directive(palette2, i)
        graphics.add_directives(color)

        # emit this line
        graphics.add_complex(xys, lines=line, polys=None)

    # copy options to output and generate the Graphics expr
    options = options_to_rules(options, filter_from_iterable(Graphics.options))
    graphics_expr = graphics.generate(options)
    return graphics_expr
