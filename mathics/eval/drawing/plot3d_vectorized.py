"""
Vectorized evaluation routines for Plot3D and DensityPlot, which share a good bit of code.

TODO: fill out eval_DensityPlot
"""

import math

import numpy as np

from mathics.core.evaluation import Evaluation
from mathics.core.symbols import strip_context

from .plot_compile import compile
from .util import GraphicsGenerator


def eval_Plot3D(
    plot_options,
    evaluation: Evaluation,
):
    graphics = GraphicsGenerator(dim=3)

    for function in plot_options.functions:
        # pull out plot options
        _, xmin, xmax = plot_options.ranges[0]
        _, ymin, ymax = plot_options.ranges[1]
        nx, ny = plot_options.plotpoints
        names = [strip_context(str(range[0])) for range in plot_options.ranges]

        # with util.Timer("compile"):
        function = compile(evaluation, function, names)

        # compute (nx, ny) grids of xs and ys for corresponding vertexes
        xs = np.linspace(xmin, xmax, nx)
        ys = np.linspace(ymin, ymax, ny)
        xs, ys = np.meshgrid(xs, ys)

        # compute zs from xs and ys using compiled function
        # with util.Timer("compute zs"):
        zs = function(**{str(names[0]): xs, str(names[1]): ys})

        # sometimes expr gets compiled into something that returns a complex
        # even though the imaginary part is 0
        # TODO: check that imag is all 0?
        # TODO: needed this for Hypergeometric - look into that
        # assert np.all(np.isreal(zs)), "array contains complex values"
        zs = np.real(zs)

        # (nx*ny, 3) array of points, to be indexed by quads
        xyzs = np.stack([xs, ys, zs]).transpose(1, 2, 0).reshape(-1, 3)

        # (nx,ny) array of numbers from 0 to n-1 that are
        # indexes into xyzs array for corresponding vertex
        inxs = np.arange(math.prod(xs.shape)).reshape(xs.shape)

        # shift inxs array four different ways and stack to form
        # (4, nx-1, ny-1) array of quads represented as indexes into xyzs array
        quads = np.stack([inxs[:-1, :-1], inxs[:-1, 1:], inxs[1:, 1:], inxs[1:, :-1]])

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
    # TODO
    # see plot3d.eval_DensityPlot for possible info on handling colors
    pass
