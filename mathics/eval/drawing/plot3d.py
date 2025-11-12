"""
Evaluation routines for 2D plotting.

These routines build Mathics M-Expressions that describe plots.
Note that this is distinct from boxing, formatting and rendering e.g. to SVG.
That is done as another pass after M-expression evaluation finishes.
"""

import itertools
from math import cos, pi, sqrt
from typing import Callable

from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Integer1, Real, String
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolColorData,
    SymbolFunction,
    SymbolLine,
    SymbolPolygon,
    SymbolRule,
    SymbolSlot,
)
from mathics.eval.drawing.plot import compile_quiet_function

ListPlotNames = (
    "DiscretePlot",
    "ListPlot",
    "ListLinePlot",
    "ListStepPlot",
)


def eval_plot3d(
    self,
    plot_options,
    evaluation: Evaluation,
    options: dict,
):
    """%(name)s[functions_, {x_Symbol, xstart_, xstop_},
    {y_Symbol, ystart_, ystop_}, OptionsPattern[%(name)s]]"""

    plotpoints = plot_options.plotpoints
    _, xstart, xstop = plot_options.ranges[0]
    _, ystart, ystop = plot_options.ranges[1]
    max_depth = plot_options.max_depth
    mesh = plot_options.mesh

    # Plot the functions
    graphics = []
    for _, f in enumerate(plot_options.functions):
        stored = {}

        compiled_fn = compile_quiet_function(
            f, [range[0].get_name() for range in plot_options.ranges], evaluation, False
        )

        def apply_fn(compiled_fn: Callable, x_value, y_value):
            try:
                # Try to used cached value first
                return stored[(x_value, y_value)]
            except KeyError:
                value = compiled_fn(x_value, y_value)
                if value is not None:
                    value = float(value)
                stored[(x_value, y_value)] = value
                return value

        triangles = []

        split_edges = set()  # subdivided edges

        def triangle(x1, y1, x2, y2, x3, y3, depth=0):
            v1, v2, v3 = (
                apply_fn(compiled_fn, x1, y1),
                apply_fn(compiled_fn, x2, y2),
                apply_fn(compiled_fn, x3, y3),
            )

            if (v1 is v2 is v3 is None) and (depth > max_depth // 2):
                # fast finish because the entire region is undefined but
                # recurse 'a little' to avoid missing well defined regions
                return
            elif v1 is None or v2 is None or v3 is None:
                # 'triforce' pattern recursion to find the edge of defined region
                #         1
                #         /\
                #      4 /__\ 6
                #       /\  /\
                #      /__\/__\
                #     2   5    3
                if depth < max_depth:
                    x4, y4 = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
                    x5, y5 = 0.5 * (x2 + x3), 0.5 * (y2 + y3)
                    x6, y6 = 0.5 * (x1 + x3), 0.5 * (y1 + y3)
                    split_edges.add(
                        ((x1, y1), (x2, y2))
                        if (x2, y2) > (x1, y1)
                        else ((x2, y2), (x1, y1))
                    )
                    split_edges.add(
                        ((x2, y2), (x3, y3))
                        if (x3, y3) > (x2, y2)
                        else ((x3, y3), (x2, y2))
                    )
                    split_edges.add(
                        ((x1, y1), (x3, y3))
                        if (x3, y3) > (x1, y1)
                        else ((x3, y3), (x1, y1))
                    )
                    triangle(x1, y1, x4, y4, x6, y6, depth + 1)
                    triangle(x4, y4, x2, y2, x5, y5, depth + 1)
                    triangle(x6, y6, x5, y5, x3, y3, depth + 1)
                    triangle(x4, y4, x5, y5, x6, y6, depth + 1)
                return
            triangles.append(sorted(((x1, y1, v1), (x2, y2, v2), (x3, y3, v3))))

        # linear (grid) sampling
        numx = plotpoints[0] * 1.0
        numy = plotpoints[1] * 1.0
        for xi in range(plotpoints[0]):
            for yi in range(plotpoints[1]):
                # Decide which way to break the square grid into triangles
                # by looking at diagonal lengths.
                #
                # 3___4        3___4
                # |\  |        |  /|
                # | \ | versus | / |
                # |__\|        |/__|
                # 1   2        1   2
                #
                # Approaching the boundary of the well defined region is
                # important too. Use first strategy if 1 or 4 are undefined
                # and strategy 2 if either 2 or 3 are undefined.
                #
                x1, x2, x3, x4 = (
                    xstart + value * (xstop - xstart)
                    for value in (
                        xi / numx,
                        (xi + 1) / numx,
                        xi / numx,
                        (xi + 1) / numx,
                    )
                )
                y1, y2, y3, y4 = (
                    ystart + value * (ystop - ystart)
                    for value in (
                        yi / numy,
                        yi / numy,
                        (yi + 1) / numy,
                        (yi + 1) / numy,
                    )
                )

                v1 = apply_fn(compiled_fn, x1, y1)
                v2 = apply_fn(compiled_fn, x2, y2)
                v3 = apply_fn(compiled_fn, x3, y3)
                v4 = apply_fn(compiled_fn, x4, y4)

                if v1 is None or v4 is None:
                    triangle(x1, y1, x2, y2, x3, y3)
                    triangle(x4, y4, x3, y3, x2, y2)
                elif v2 is None or v3 is None:
                    triangle(x2, y2, x1, y1, x4, y4)
                    triangle(x3, y3, x4, y4, x1, y1)
                else:
                    if abs(v3 - v2) > abs(v4 - v1):
                        triangle(x2, y2, x1, y1, x4, y4)
                        triangle(x3, y3, x4, y4, x1, y1)
                    else:
                        triangle(x1, y1, x2, y2, x3, y3)
                        triangle(x4, y4, x3, y3, x2, y2)

        # adaptive resampling
        # TODO: optimise this
        # Cos of the maximum angle between successive line segments
        ang_thresh = cos(20 * pi / 180)
        for depth in range(1, max_depth):
            needs_removal = set()
            lent = len(triangles)  # number of initial triangles
            for i1 in range(lent):
                for i2 in range(lent):
                    # find all edge pairings
                    if i1 == i2:
                        continue
                    t1 = triangles[i1]
                    t2 = triangles[i2]

                    edge_pairing = (
                        (t1[0], t1[1]) == (t2[0], t2[1])
                        or (t1[0], t1[1]) == (t2[1], t2[2])
                        or (t1[0], t1[1]) == (t2[0], t2[2])
                        or (t1[1], t1[2]) == (t2[0], t2[1])
                        or (t1[1], t1[2]) == (t2[1], t2[2])
                        or (t1[1], t1[2]) == (t2[0], t2[2])
                        or (t1[0], t1[2]) == (t2[0], t2[1])
                        or (t1[0], t1[2]) == (t2[1], t2[2])
                        or (t1[0], t1[2]) == (t2[0], t2[2])
                    )
                    if not edge_pairing:
                        continue
                    v1 = [t1[1][i] - t1[0][i] for i in range(3)]
                    w1 = [t1[2][i] - t1[0][i] for i in range(3)]
                    v2 = [t2[1][i] - t2[0][i] for i in range(3)]
                    w2 = [t2[2][i] - t2[0][i] for i in range(3)]
                    n1 = (  # surface normal for t1
                        (v1[1] * w1[2]) - (v1[2] * w1[1]),
                        (v1[2] * w1[0]) - (v1[0] * w1[2]),
                        (v1[0] * w1[1]) - (v1[1] * w1[0]),
                    )
                    n2 = (  # surface normal for t2
                        (v2[1] * w2[2]) - (v2[2] * w2[1]),
                        (v2[2] * w2[0]) - (v2[0] * w2[2]),
                        (v2[0] * w2[1]) - (v2[1] * w2[0]),
                    )
                    try:
                        angle = (n1[0] * n2[0] + n1[1] * n2[1] + n1[2] * n2[2]) / sqrt(
                            (n1[0] ** 2 + n1[1] ** 2 + n1[2] ** 2)
                            * (n2[0] ** 2 + n2[1] ** 2 + n2[2] ** 2)
                        )
                    except ZeroDivisionError:
                        angle = 0.0
                    if abs(angle) < ang_thresh:
                        for i, t in ((i1, t1), (i2, t2)):
                            # subdivide
                            x1, y1 = t[0][0], t[0][1]
                            x2, y2 = t[1][0], t[1][1]
                            x3, y3 = t[2][0], t[2][1]
                            x4, y4 = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
                            x5, y5 = 0.5 * (x2 + x3), 0.5 * (y2 + y3)
                            x6, y6 = 0.5 * (x1 + x3), 0.5 * (y1 + y3)
                            needs_removal.add(i)
                            split_edges.add(
                                ((x1, y1), (x2, y2))
                                if (x2, y2) > (x1, y1)
                                else ((x2, y2), (x1, y1))
                            )
                            split_edges.add(
                                ((x2, y2), (x3, y3))
                                if (x3, y3) > (x2, y2)
                                else ((x3, y3), (x2, y2))
                            )
                            split_edges.add(
                                ((x1, y1), (x3, y3))
                                if (x3, y3) > (x1, y1)
                                else ((x3, y3), (x1, y1))
                            )
                            triangle(x1, y1, x4, y4, x6, y6, depth=depth)
                            triangle(x2, y2, x4, y4, x5, y5, depth=depth)
                            triangle(x3, y3, x5, y5, x6, y6, depth=depth)
                            triangle(x4, y4, x5, y5, x6, y6, depth=depth)
            # remove subdivided triangles which have been divided
            triangles = [t for i, t in enumerate(triangles) if i not in needs_removal]

        # fix up subdivided edges
        #
        # look at every triangle and see if its edges need updating.
        # depending on how many edges require subdivision we proceede with
        # one of two subdivision strategies
        #
        # TODO possible optimisation: don't look at every triangle again
        made_changes = True
        while made_changes:
            made_changes = False
            new_triangles = []
            for i, t in enumerate(triangles):
                new_points = []
                if ((t[0][0], t[0][1]), (t[1][0], t[1][1])) in split_edges:
                    new_points.append([0, 1])
                if ((t[1][0], t[1][1]), (t[2][0], t[2][1])) in split_edges:
                    new_points.append([1, 2])
                if ((t[0][0], t[0][1]), (t[2][0], t[2][1])) in split_edges:
                    new_points.append([0, 2])

                if len(new_points) == 0:
                    continue
                made_changes = True
                # 'triforce' subdivision
                #         1
                #         /\
                #      4 /__\ 6
                #       /\  /\
                #      /__\/__\
                #     2   5    3
                # if less than three edges require subdivision bisect them
                # anyway but fake their values by averaging
                x4 = 0.5 * (t[0][0] + t[1][0])
                y4 = 0.5 * (t[0][1] + t[1][1])
                v4 = stored.get((x4, y4), 0.5 * (t[0][2] + t[1][2]))

                x5 = 0.5 * (t[1][0] + t[2][0])
                y5 = 0.5 * (t[1][1] + t[2][1])
                v5 = stored.get((x5, y5), 0.5 * (t[1][2] + t[2][2]))

                x6 = 0.5 * (t[0][0] + t[2][0])
                y6 = 0.5 * (t[0][1] + t[2][1])
                v6 = stored.get((x6, y6), 0.5 * (t[0][2] + t[2][2]))

                if not (v4 is None or v6 is None):
                    new_triangles.append(sorted((t[0], (x4, y4, v4), (x6, y6, v6))))
                if not (v4 is None or v5 is None):
                    new_triangles.append(sorted((t[1], (x4, y4, v4), (x5, y5, v5))))
                if not (v5 is None or v6 is None):
                    new_triangles.append(sorted((t[2], (x5, y5, v5), (x6, y6, v6))))
                if not (v4 is None or v5 is None or v6 is None):
                    new_triangles.append(
                        sorted(((x4, y4, v4), (x5, y5, v5), (x6, y6, v6)))
                    )
                triangles[i] = None

            triangles.extend(new_triangles)
            triangles = [t for t in triangles if t is not None]

        # add the mesh
        mesh_points = []
        if mesh == "System`Full":
            for xi in range(plotpoints[0] + 1):
                xval = xstart + xi / numx * (xstop - xstart)
                mesh_row = []
                for yi in range(plotpoints[1] + 1):
                    yval = ystart + yi / numy * (ystop - ystart)
                    z = stored[(xval, yval)]
                    mesh_row.append((xval, yval, z))
                mesh_points.append(mesh_row)

            for yi in range(plotpoints[1] + 1):
                yval = ystart + yi / numy * (ystop - ystart)
                mesh_col = []
                for xi in range(plotpoints[0] + 1):
                    xval = xstart + xi / numx * (xstop - xstart)
                    z = stored[(xval, yval)]
                    mesh_col.append((xval, yval, z))
                mesh_points.append(mesh_col)

            # handle edge subdivisions
            made_changes = True
            while made_changes:
                made_changes = False
                for mesh_line in mesh_points:
                    i = 0
                    while i < len(mesh_line) - 1:
                        x1, y1, v1 = mesh_line[i]
                        x2, y2, v2 = mesh_line[i + 1]
                        key = (
                            ((x1, y1), (x2, y2))
                            if (x2, y2) > (x1, y1)
                            else ((x2, y2), (x1, y1))
                        )
                        if key in split_edges:
                            x3 = 0.5 * (x1 + x2)
                            y3 = 0.5 * (y1 + y2)
                            v3 = stored[(x3, y3)]
                            mesh_line.insert(i + 1, (x3, y3, v3))
                            made_changes = True
                            i += 1
                        i += 1

            # handle missing regions
            old_meshpoints, mesh_points = mesh_points, []
            for mesh_line in old_meshpoints:
                mesh_points.extend(
                    [
                        sorted(g)
                        for k, g in itertools.groupby(mesh_line, lambda x: x[2] is None)
                    ]
                )
            mesh_points = [
                mesh_line
                for mesh_line in mesh_points
                if not any(x[2] is None for x in mesh_line)
            ]
        elif mesh == "System`All":
            mesh_points = set()
            for t in triangles:
                mesh_points.add((t[0], t[1]) if t[1] > t[0] else (t[1], t[0]))
                mesh_points.add((t[1], t[2]) if t[2] > t[1] else (t[2], t[1]))
                mesh_points.add((t[0], t[2]) if t[2] > t[0] else (t[2], t[0]))
            mesh_points = list(mesh_points)

        # find the max and min height
        v_min = v_max = None
        for t in triangles:
            for tx, ty, v in t:
                if v_min is None or v < v_min:
                    v_min = v
                if v_max is None or v > v_max:
                    v_max = v
        graphics.extend(
            self.construct_graphics(
                triangles, mesh_points, v_min, v_max, options, evaluation
            )
        )
    return self.final_graphics(graphics, options)


def construct_density_plot(
    self, triangles, mesh_points, v_min, v_max, options, evaluation
):
    """
    Construct a density plot
    """
    color_function = self.get_option(options, "ColorFunction", evaluation, pop=True)
    color_function_scaling = self.get_option(
        options, "ColorFunctionScaling", evaluation, pop=True
    )

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

    points = []
    vertex_colors = []
    graphics = []
    for p in triangles:
        points.append(ListExpression(*(to_mathics_list(*x[:2]) for x in p)))
        vertex_colors.append(ListExpression(*(eval_color(*x) for x in p)))

    graphics.append(
        Expression(
            SymbolPolygon,
            ListExpression(*points),
            Expression(
                SymbolRule,
                Symbol("VertexColors"),
                ListExpression(*vertex_colors),
            ),
        )
    )

    # add mesh
    for xi in range(len(mesh_points)):
        line = []
        for yi in range(len(mesh_points[xi])):
            line.append(to_mathics_list(mesh_points[xi][yi][0], mesh_points[xi][yi][1]))
        graphics.append(Expression(SymbolLine, ListExpression(*line)))

    return graphics
