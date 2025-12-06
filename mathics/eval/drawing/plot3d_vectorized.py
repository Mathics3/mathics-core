"""
Vectorized evaluation routines for Plot3D, DensityPlot, ComplexPlot, and ComplexPlot3D,
which share a good bit of code.
"""

import math

import numpy as np

from mathics.builtin.colors.color_internals import convert_color
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import strip_context
from mathics.core.systemsymbols import (
    SymbolEqual,
    SymbolNone,
    SymbolRGBColor,
    SymbolSubtract,
)
from mathics.timing import Timer

from .plot_compile import plot_compile
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


# color-blind friendly palette from https://davidmathlogic.com/colorblind
# palette3 is for 3d plots, i.e. surfaces
palette3 = [
    (255, 176, 0),  # orange
    (100, 143, 255),  # blue
    (220, 38, 127),  # red
    (50, 150, 140),  # green
    (120, 94, 240),  # purple
    (254, 97, 0),  # dark orange
    (0, 114, 178),  # dark blue
]


# palette 2 is for 2d plots, i.e. lines
# same colors as palette3 but in a little different order
palette2 = [
    (100, 143, 255),  # blue
    (255, 176, 0),  # orange
    (50, 150, 140),  # green
    (220, 38, 127),  # red
    (120, 94, 240),  # purple
    (254, 97, 0),  # dark orange
    (0, 114, 178),  # dark blue
]


def palette_color_directive(palette, i):
    """returns a directive in a form suitable for graphics.add_directives"""
    """ for setting the color of an entire entity such as a line or surface """
    rgb = palette[i % len(palette)]
    rgb = [c / 255.0 for c in rgb]
    return [SymbolRGBColor, *rgb]


@Timer("density_colors")
def density_colors(zs):
    """default color palette for DensityPlot and ContourPlot (f(x) form)"""
    z_min, z_max = min(zs), max(zs)
    zs = zs[:, np.newaxis]  # allow broadcasting
    # c_min, c_max = [0.3, 0.00, 0.3], [1.0, 0.95, 0.8]
    c_min, c_max = [0.5, 0, 0.1], [1.0, 0.9, 0.5]
    c_min, c_max = (
        np.full((len(zs), 3), c_min),
        np.full((len(zs), 3), c_max),
    )
    colors = ((zs - z_min) * c_max + (z_max - zs) * c_min) / (z_max - z_min)
    return colors


@Timer("eval_Plot3D")
def eval_Plot3D(
    plot_options,
    evaluation: Evaluation,
):
    def emit(graphics, i, xyzs, quads):
        # choose a color
        color_directive = palette_color_directive(palette3, i)
        graphics.add_directives(color_directive)

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
        colors = density_colors(xyzs[:, 2])

        # flatten the points and add the quads
        graphics.add_complex(xyzs[:, 0:2], lines=None, polys=quads, colors=colors)

    return make_plot(plot_options, evaluation, dim=2, is_complex=False, emit=emit)


@Timer("eval_ContourPlot")
def eval_ContourPlot(
    plot_options,
    evaluation: Evaluation,
):
    import skimage.measure

    # whether to show a background similar to density plot, except quantized
    background = len(plot_options.functions) == 1
    contour_levels = plot_options.contours

    # convert fs of the form a==b to a-b, inplicit contour level 0
    plot_options.functions = list(plot_options.functions)  # so we can modify it
    for i, f in enumerate(plot_options.functions):
        if f.head == SymbolEqual:
            f = Expression(SymbolSubtract, *f.elements[0:2])
            plot_options.functions[i] = f
            contour_levels = [0]
            background = False

    def emit(graphics, i, xyzs, quads):
        # set line color
        if background:
            # showing a background, so just black lines
            color_directive = [SymbolRGBColor, 0, 0, 0]
        else:
            # no background - each curve gets its own color
            color_directive = palette_color_directive(palette2, i)
        graphics.add_directives(color_directive)

        # get data
        nx, ny = plot_options.plotpoints
        _, xmin, xmax = plot_options.ranges[0]
        _, ymin, ymax = plot_options.ranges[1]
        zs = xyzs[:, 2]  # this is a linear list matching with quads

        # process contour_levels
        levels = contour_levels
        zmin, zmax = np.min(zs), np.max(zs)
        if isinstance(levels, str):
            # TODO: need to pick "nice" number so levels have few digits
            # an odd number ensures there is a contour at 0 if range is balanced
            levels = 9
        if isinstance(levels, int):
            # computed contour levels have equal distance between them,
            # and half that between first/last contours and zmin/zmax
            dz = (zmax - zmin) / levels
            levels = zmin + np.arange(levels) * dz + dz/2

        # one contour line per contour level
        for level in levels:
            # find contours and add lines
            with Timer("contours"):
                zgrid = zs.reshape((nx, ny))  # find_contours needs it as an array
                contours = skimage.measure.find_contours(zgrid, level)

            # add lines
            for segment in contours:
                segment[:, 0] = segment[:, 0] * ((xmax - xmin) / nx) + xmin
                segment[:, 1] = segment[:, 1] * ((ymax - ymin) / ny) + ymin
                graphics.add_linexyzs(segment)

        # background is solid colors between contour lines
        if background:
            with Timer("contour background"):
                # add extra levels below zmin and above zmax to define end ranges
                levels = [zmin-(levels[0]-zmin)] + list(levels) + [zmax+(zmax-levels[-1])]
                for lo, hi in zip(levels[:-1], levels[1:]):
                    # use masks and fancy indexing to assign (lo+hi)/2 to all zs between lo and hi
                    zs[(lo < zs) & (zs <= hi)] = (lo + hi) / 2
                colors = density_colors(zs) # same colors as density plot
                graphics.add_complex(xyzs[:, 0:2], lines=None, polys=quads, colors=colors)

    # plot_options.plotpoints = [n * 10 for n in plot_options.plotpoints]
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
