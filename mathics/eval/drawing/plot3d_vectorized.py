"""
Vectorized evaluation routines for Plot3D, DensityPlot, ComplexPlot, and ComplexPlot3D,
which share a good bit of code.
"""

import math

import numpy as np

from mathics.builtin.colors.color_internals import convert_color
from mathics.core.convert.lambdify import lambdify_compile as plot_compile
from mathics.core.evaluation import Evaluation
from mathics.core.symbols import strip_context
from mathics.core.systemsymbols import SymbolNone, SymbolRGBColor
from mathics.timing import Timer

from .util import GraphicsGenerator


def make_plot(plot_options, evaluation: Evaluation, dim: int, is_complex: bool, emit):
    graphics = GraphicsGenerator(dim)

    # pull out plot options
    if not is_complex:
        _, xmin, xmax = plot_options.ranges[0]
        _, ymin, ymax = plot_options.ranges[1]
    else:
        # will generate xs and ys as for real, then combine to form complex cs
        _, cmin, cmax = plot_options.ranges[0]
        xmin, xmax = cmin.real, cmax.real
        ymin, ymax = cmin.imag, cmax.imag
    names = [strip_context(str(range[0])) for range in plot_options.ranges]

    # Mesh option
    nmesh = 20
    if plot_options.mesh is SymbolNone:
        nmesh = 0

    # compile the functions
    with Timer("compile"):
        compiled_functions = [
            plot_compile(evaluation, function, names)
            for function in plot_options.functions
        ]

    def compute_over_grid(nx, ny):
        """
        For each function, computes an (nx*ny, 3) array of coordinates (xyzs),
        and an (nx, ny) array of indices (inxs) into xyzs representing
        the index in xyzs of the corresponding position in the grid.
        Returns an iterator over (xyzs,inxs) pairs, one for each function.

        This is used for computing the full grid of quads representing the
        surface defined by each function, and also for computing a sparse
        grid used to display a mesh of lines on the surface.
        """

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
                if not is_complex:
                    zs = function(**{str(names[0]): xs, str(names[1]): ys})
                else:
                    cs = xs + ys * 1j  # TODO: fast enough?
                    zs = function(**{str(names[0]): cs})

            # sometimes expr gets compiled into something that returns a complex
            # even though the imaginary part is 0
            # TODO: check that imag is all 0?
            # TODO: needed this for Hypergeometric - look into that
            # assert np.all(np.isreal(zs)), "array contains complex values"
            if not is_complex:
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
        quads = np.stack([inxs[:-1, :-1], inxs[:-1, 1:], inxs[1:, 1:], inxs[1:, :-1]])

        # transpose and flatten to ((nx-1)*(ny-1), 4) array, suitable for use in GraphicsComplex
        quads = quads.T.reshape(-1, 4)

        # pass the xyzs and quads back to the caller to add colors and emit quads as appropriate
        emit(graphics, i, xyzs, quads)

    # If requested by the Mesh attribute create a mesh of lines covering the surfaces
    # For now only for Plot3D
    # TODO: mesh for DensityPlot?
    if nmesh and dim == 3:
        # meshes are black for now
        graphics.add_directives([SymbolRGBColor, 0, 0, 0])

        with Timer("Mesh"):
            nx, ny = plot_options.plotpoints
            # Do nmesh lines in each direction, each line formed
            # from one row or one column of the inxs array.
            # Each mesh line has high res (nx or ny) so it follows
            # the contours of the surface.
            for xyzs, inxs in compute_over_grid(nx, nmesh):
                graphics.add_complex(xyzs.astype(float), lines=inxs, polys=None)
            for xyzs, inxs in compute_over_grid(nmesh, ny):
                graphics.add_complex(xyzs.astype(float), lines=inxs.T, polys=None)

    return graphics


@Timer("eval_Plot3D")
def eval_Plot3D(
    plot_options,
    evaluation: Evaluation,
):
    def emit(graphics, i, xyzs, quads):
        # color-blind friendly palette from https://davidmathlogic.com/colorblind
        palette = [
            (255, 176, 0),  # orange
            (100, 143, 255),  # blue
            (220, 38, 127),  # red
            (50, 150, 140),  # green
            (120, 94, 240),  # purple
            (254, 97, 0),  # dark orange
            (0, 114, 178),  # dark blue
        ]

        # choose a color
        rgb = palette[i % len(palette)]
        rgb = [c / 255.0 for c in rgb]
        # graphics.add_color(SymbolRGBColor, rgb)
        graphics.add_directives([SymbolRGBColor, *rgb])

        # add a GraphicsComplex displaying a surface for this function
        graphics.add_complex(xyzs, lines=None, polys=quads)

    return make_plot(plot_options, evaluation, dim=3, is_complex=False, emit=emit)


@Timer("eval_DensityPlot")
def eval_DensityPlot(
    plot_options,
    evaluation: Evaluation,
):
    def emit(graphics, i, xyzs, quads):
        # Fixed palette for now
        # TODO: accept color options
        with Timer("compute colors"):
            zs = xyzs[:, 2]
            z_min, z_max = min(zs), max(zs)
            zs = zs[:, np.newaxis]  # allow broadcasting
            c_min, c_max = [0.5, 0, 0.1], [1.0, 0.9, 0.5]
            c_min, c_max = (
                np.full((len(zs), 3), c_min),
                np.full((len(zs), 3), c_max),
            )
            colors = ((zs - z_min) * c_max + (z_max - zs) * c_min) / (z_max - z_min)

        # flatten the points and add the quads
        graphics.add_complex(xyzs[:, 0:2], lines=None, polys=quads, colors=colors)

    return make_plot(plot_options, evaluation, dim=2, is_complex=False, emit=emit)


@Timer("complex colors")
def complex_colors(zs, s=None):
    # hue depends on phase
    h = np.angle(zs, deg=True) / 360

    # saturation depends on magnitude
    if s is None:
        zabs = abs(zs)
        zabs = -np.log(zabs)
        zmin, zmax = min(zabs), max(zabs)
        s = (zabs - zmin) / (zmax - zmin)
    else:
        s = np.full(zs.shape, s)

    # brightness is constant
    b = np.full(zs.shape, 1.0)

    # convert to rgb
    hsb = np.array([h, s, b]).T
    rgb = convert_color(hsb, "HSB", "RGB", False)

    return rgb


@Timer("eval_ComplexPlot3D")
def eval_ComplexPlot3D(
    plot_options,
    evaluation: Evaluation,
):
    def emit(graphics, i, xyzs, quads):
        zs = xyzs[:, 2]
        rgb = complex_colors(zs, s=0.8)
        xyzs[:, 2] = abs(zs)
        graphics.add_complex(xyzs.astype(float), lines=None, polys=quads, colors=rgb)

    return make_plot(plot_options, evaluation, dim=3, is_complex=True, emit=emit)


@Timer("eval_ComplexPlot")
def eval_ComplexPlot(
    plot_options,
    evaluation: Evaluation,
):
    def emit(graphics, i, xyzs, quads):
        # flatten the points and add the quads
        rgb = complex_colors(xyzs[:, 2])
        graphics.add_complex(
            xyzs[:, 0:2].astype(float), lines=None, polys=quads, colors=rgb
        )

    return make_plot(plot_options, evaluation, dim=2, is_complex=True, emit=emit)
