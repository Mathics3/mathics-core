"""
Vectorized evaluation routines for Plot3D and DensityPlot, which share a good bit of code.

TODO: fill out eval_DensityPlot
"""

import math

import numpy as np

from mathics.core.evaluation import Evaluation
from mathics.core.symbols import strip_context
from mathics.core.systemsymbols import SymbolRGBColor, SymbolNone, SymbolEdgeForm
from mathics.timing import Timer

from .plot_compile import plot_compile
from .util import GraphicsGenerator


@Timer("eval_Plot3D")
def eval_Plot3D(
    plot_options,
    evaluation: Evaluation,
):
    graphics = GraphicsGenerator(dim=3)

    # pull out plot options
    _, xmin, xmax = plot_options.ranges[0]
    _, ymin, ymax = plot_options.ranges[1]
    names = [strip_context(str(range[0])) for range in plot_options.ranges]

    # Mesh option
    nmesh = None
    if isinstance(plot_options.mesh, int):
        nmesh = plot_options.mesh
    elif plot_options.mesh is not SymbolNone:
        nmesh = 20

    # https://davidmathlogic.com/colorblind
    palette = [
        (255, 176, 0), # orange
        (100, 143, 255), # blue
        (220, 38, 127), # red
        (50, 150, 140), # green
        (120, 94, 240), # purple
        #(240, 228, 66), # yellow
        (254, 97, 0), # dark orange
        (0, 114, 178), # dark blue
        #(0, 0, 0), # black
    ]

    # compile the functions
    with Timer("compile"):
        compiled_functions = [plot_compile(evaluation, function, names) for function in plot_options.functions]

    def compute_over_grid(nx, ny):

        # compute (nx, ny) grids of xs and ys for corresponding vertexes
        xs = np.linspace(xmin, xmax, nx)
        ys = np.linspace(ymin, ymax, ny)
        xs, ys = np.meshgrid(xs, ys)

        # (nx,ny) array of numbers from 0 to n-1 that are
        # indexes into xyzs array for corresponding vertex
        # +1 because these will be used as WL indexes, which are 1-based
        inxs = np.arange(math.prod(xs.shape)).reshape(xs.shape) + 1

        for function in compiled_functions:

            # compute zs from xs and ys using compiled function
            with Timer("compute zs"):
                zs = function(**{str(names[0]): xs, str(names[1]): ys})

            # sometimes expr gets compiled into something that returns a complex
            # even though the imaginary part is 0
            # TODO: check that imag is all 0?
            # TODO: needed this for Hypergeometric - look into that
            # assert np.all(np.isreal(zs)), "array contains complex values"
            zs = np.real(zs)

            # if it's a constant, make it a full array
            if isinstance(zs, (float, int, complex)):
                zs = np.full(xs.shape, zs)

            # (nx*ny, 3) array of points, to be indexed by quads
            xyzs = np.stack([xs, ys, zs]).transpose(1, 2, 0).reshape(-1, 3)

            yield xyzs, inxs

    # generate the quads and emit a GraphicsComplex containing them
    for i, (xyzs, inxs) in enumerate(compute_over_grid(*plot_options.plotpoints)):

        # shift inxs array four different ways and stack to form
        # (4, nx-1, ny-1) array of quads represented as indexes into xyzs array
        quads = np.stack(
            [inxs[:-1, :-1], inxs[:-1, 1:], inxs[1:, 1:], inxs[1:, :-1]]
        )

        # transpose and flatten to ((nx-1)*(ny-1), 4) array, suitable for use in GraphicsComplex
        quads = quads.T.reshape(-1, 4)

        # choose a color
        rgb = palette[i%len(palette)]
        rgb = [c/255.0 for c in rgb]
        #graphics.add_color(SymbolRGBColor, rgb)
        graphics.add_directives([SymbolRGBColor, *rgb])

        # add a GraphicsComplex for this function
        graphics.add_complex(xyzs, lines=None, polys=quads)

    # if requested by the Mesh attribute create a mesh of lines covering the surfaces
    if nmesh:

        # meshes are black for now
        graphics.add_directives([SymbolRGBColor, 0,0,0])

        with Timer("Mesh"):
            nmesh = 20 # TODO: use supplied option
            nx, ny = plot_options.plotpoints
            # Do nmesh lines in each direction.
            # Each mesh line has high res (nx or ny) so it follows
            # the contours of the surface.
            for xyzs, inxs in compute_over_grid(nx, nmesh):
                graphics.add_complex(xyzs, lines=inxs, polys=None)
            for xyzs, inxs in compute_over_grid(nmesh, ny):
                graphics.add_complex(xyzs, lines=inxs.T, polys=None)

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
