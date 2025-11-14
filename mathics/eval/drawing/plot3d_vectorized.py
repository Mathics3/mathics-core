"""
Vectorized dvaluation routines for Plot3D and DensityPlot, which share a good bit of code.
"""

import itertools
import math
from typing import Callable
import os
import numpy as np

from mathics.core.atoms import Integer1, Real, String
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import SymbolTrue, strip_context
from mathics.core.systemsymbols import (
    SymbolAll,
    SymbolColorData,
    SymbolFull,
    SymbolFunction,
    SymbolSlot,
)
from mathics.eval.drawing.plot import compile_quiet_function

from .util import GraphicsGenerator
from .plot_compile import compile


def eval_Plot3D(
    plot_options,
    evaluation: Evaluation,
):

    graphics = GraphicsGenerator(dim=3)

    for function in plot_options.functions:

        _, xmin, xmax = plot_options.ranges[0]
        _, ymin, ymax = plot_options.ranges[1]
        nx, ny = plot_options.plotpoints
        names = [strip_context(str(range[0])) for range in plot_options.ranges]

        #with util.Timer("compile"):
        function = compile(evaluation, function, names)

        # compute (nx, ny) grids of xs and ys for corresponding vertexes
        xs = np.linspace(xmin, xmax, nx)
        ys = np.linspace(ymin, ymax, ny)
        xs, ys = np.meshgrid(xs, ys)

        # compute zs from xs and ys using compiled function
        #with util.Timer("compute zs"):
        zs = function(**{str(names[0]): xs, str(names[1]): ys})

        # sometimes expr gets compiled into something that returns a complex
        # even though the imaginary part is 0
        # TODO: check that imag is all 0?
        # TODO: needed this for Hypergeometric - look into that
        #assert np.all(np.isreal(zs)), "array contains complex values"
        zs = np.real(zs)

        # (nx*ny, 3) array of points, to be indexed by quads
        xyzs = np.stack([xs, ys, zs]).transpose(1,2,0).reshape(-1,3)

        # (nx,ny) array of numbers from 0 to n-1 that are
        # indexes into xyzs array for corresponding vertex
        inxs = np.arange(math.prod(xs.shape)).reshape(xs.shape)

        # (4, nx-1, ny-1) array of quads represented as indexes into xyzs array
        quads = np.stack([inxs[:-1,:-1], inxs[:-1,1:], inxs[1:,1:], inxs[1:,:-1]])

        # transpose and flatten to ((nx-1)*(ny-1), 4) array, suitable for use in GraphicsComplex
        quads = quads.T.reshape(-1, 4)

        # ugh - indexes in Polygon are 1-based
        quads += 1

        # add a GraphicsComplex for this function
        graphics.add_complex(xyzs, lines=None, polys=quads)

    return graphics


#
#
#


def eval_DensityPlot(
    plot_options,
    evaluation: Evaluation,
):
    triangles, mesh_points, v_min, v_max = compute_triangles(plot_options, evaluation)

    color_function = plot_options.color_function
    color_function_scaling = plot_options.color_function_scaling

    # TODO: can some of this be pulled out into PlotOptions for more general use?
    color_function_min = color_function_max = None
    if color_function.get_name() == "System`Automatic":
        color_function = String("LakeColors")
    if color_function.get_string_value():
        func = Expression(
            SymbolColorData, String(color_function.get_string_value())
        ).evaluate(evaluation)
        if func.has_form("ColorDataFunction", 4):
            color_function_min = func.elements[2].elements[0].round_to_float()
            color_function_max = func.elements[2].elements[1].round_to_float()
            color_function = Expression(
                SymbolFunction,
                Expression(func.elements[3], Expression(SymbolSlot, Integer1)),
            )
        else:
            evaluation.message("DensityPlot", "color", func)
            return
    if color_function.has_form("ColorDataFunction", 4):
        color_function_min = color_function.elements[2].elements[0].round_to_float()
        color_function_max = color_function.elements[2].elements[1].round_to_float()

    color_function_scaling = color_function_scaling is SymbolTrue
    v_range = v_max - v_min

    if v_range == 0:
        v_range = 1

    if color_function.has_form("ColorDataFunction", 4):
        color_func = color_function.elements[3]
    else:
        color_func = color_function
    if (
        color_function_scaling
        and color_function_min is not None  # noqa
        and color_function_max is not None
    ):
        color_function_range = color_function_max - color_function_min

    colors = {}

    def eval_color(x, y, v):
        v_scaled = (v - v_min) / v_range
        if (
            color_function_scaling
            and color_function_min is not None  # noqa
            and color_function_max is not None
        ):
            v_color_scaled = color_function_min + v_scaled * color_function_range
        else:
            v_color_scaled = v

        # Calculate and store 100 different shades max.
        v_lookup = int(v_scaled * 100 + 0.5)

        value = colors.get(v_lookup)
        if value is None:
            value = Expression(color_func, Real(v_color_scaled))
            value = value.evaluate(evaluation)
            colors[v_lookup] = value
        return value

    graphics = GraphicsGenerator(dim=2)

    # add the triangles with their colors
    polys = tuple(tuple(p[:2] for p in tri) for tri in triangles)
    colors = tuple(tuple(eval_color(*p) for p in tri) for tri in triangles)
    graphics.add_polyxyzs(polys, colors)

    # add the mesh lines
    for xi in range(len(mesh_points)):
        graphics.add_linexyzs([mesh_points[xi]])

    return graphics
