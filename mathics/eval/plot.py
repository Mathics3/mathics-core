"""
Evaluation routines for 2D plotting.

These routines build Mathics M-Expressions that describe plots.
Note that this is distinct from boxing, formatting and rendering e.g. to SVG.
That is done as another pass after M-expression evaluation finishes.
"""

from math import cos, isinf, isnan, pi, sqrt
from typing import Callable, Iterable, List, Optional, Type, Union

from mathics.builtin.numeric import chop
from mathics.builtin.options import options_to_rules
from mathics.builtin.scoping import dynamic_scoping
from mathics.core.atoms import Integer, Integer0, Real, String
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolN, SymbolPower, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolGraphics,
    SymbolHue,
    SymbolLine,
    SymbolLog10,
    SymbolLogPlot,
    SymbolMessageName,
    SymbolPoint,
    SymbolPolygon,
    SymbolQuiet,
)

RealPoint6 = Real(0.6)
RealPoint2 = Real(0.2)


try:
    from mathics.compile import CompileArg, CompileError, _compile, real_type

    has_compile = True
except ImportError:
    has_compile = False


def automatic_plot_range(values):
    """Calculates mean and standard deviation, throwing away all points
    which are more than 'thresh' number of standard deviations away from
    the mean. These are then used to find good vmin and vmax values. These
    values can then be used to find Automatic Plotrange."""

    if not values:
        return 0, 1

    thresh = 2.0
    values = sorted(values)
    valavg = sum(values) / len(values)
    valdev = sqrt(
        sum([(x - valavg) ** 2 for x in values]) / zero_to_one(len(values) - 1)
    )

    n1, n2 = 0, len(values) - 1
    if valdev != 0:
        for v in values:
            if abs(v - valavg) / valdev < thresh:
                break
            n1 += 1
        for v in values[::-1]:
            if abs(v - valavg) / valdev < thresh:
                break
            n2 -= 1

    vrange = values[n2] - values[n1]
    vmin = values[n1] - 0.05 * vrange  # 5% extra looks nice
    vmax = values[n2] + 0.05 * vrange
    return vmin, vmax


def compile_quiet_function(expr, arg_names, evaluation, list_is_expected: bool):
    """
    Given an expression return a quiet callable version.
    Compiles the expression where possible.
    """
    if has_compile and not list_is_expected:
        try:
            cfunc = _compile(
                expr, [CompileArg(arg_name, real_type) for arg_name in arg_names]
            )
        except CompileError:
            pass
        else:

            def quiet_f(*args):
                try:
                    result = cfunc(*args)
                    if not (isnan(result) or isinf(result)):
                        return result
                except Exception:
                    pass
                return None

            return quiet_f
    expr: Optional[Type[BaseElement]] = Expression(SymbolN, expr).evaluate(evaluation)
    quiet_expr = Expression(
        SymbolQuiet,
        expr,
        ListExpression(Expression(SymbolMessageName, SymbolPower, String("infy"))),
    )

    def quiet_f(*args):
        vars = {arg_name: Real(arg) for arg_name, arg in zip(arg_names, args)}
        value = dynamic_scoping(quiet_expr.evaluate, vars, evaluation)
        if list_is_expected:
            if value.has_form("List", None):
                value = [extract_pyreal(item) for item in value.elements]
                if any(item is None for item in value):
                    return None
                return value
            else:
                return None
        else:
            value = extract_pyreal(value)
            if value is None or isinf(value) or isnan(value):
                return None
            return value

    return quiet_f


def eval_ListPlot(
    plot_groups: list,
    x_range: list,
    y_range: list,
    is_discrete_plot: bool,
    is_joined_plot: bool,
    filling,
    use_log_scale: bool,
    options: dict,
):
    """
    Evaluation part of LisPlot[] and DiscretePlot[]

    plot_groups: the plot point data, It can be in a number of different list formats
    x_range: the x range that of the area to show in the plot
    y_range: the y range that of the area to show in the plot
    is_discrete_plot: True if called from DiscretePlot, False if called from ListPlot
    is_joined_plot: True if points are to be joined. This never happens in a discrete plot
    options: miscellaneous graphics options from underlying M-Expression
    """

    if not isinstance(plot_groups, list) or len(plot_groups) == 0:
        return

    # Classify the kind of data that "point" is, and
    # canonicalize this into a list of lines.
    if all(not isinstance(point, (list, tuple)) for point in plot_groups):
        # We have only y values given.

        # Remove entries that are not float or int.
        plot_groups = tuple(y for y in plot_groups if isinstance(y, (float, int)))

        if len(plot_groups) == 0:
            # Plot groups is empty
            y_min = 0
            y_max = 0
        else:
            y_min = min(plot_groups)
            y_max = max(plot_groups)

        x_min = 0
        x_max = len(plot_groups)
        plot_groups = [
            [[float(i + 1), plot_groups[i]] for i in range(len(plot_groups))]
        ]
    elif all(
        isinstance(plot_group, (list, tuple)) and len(plot_group) == 2
        for plot_group in plot_groups
    ):
        # He have a single list of (x,y) pairs.

        # FIXME: is this right?
        x_range = get_plot_range(
            [xx for xx, yy in plot_groups], [xx for xx, yy in plot_groups], x_range
        )
        y_range = get_plot_range(
            [yy for xx, yy in plot_groups], [yy for xx, yy in plot_groups], y_range
        )

        get_plot_range(
            [xx for xx, yy in plot_groups], [xx for xx, yy in plot_groups], x_range
        )
        plot_groups = [plot_groups]
    elif all(isinstance(line, list) for line in plot_groups):
        if not all(isinstance(line, list) for line in plot_groups):
            return

        # He have a list of plot groups
        if all(
            isinstance(point, list) and len(point) == 2
            for plot_group in plot_groups
            for point in plot_groups
        ):
            pass
        elif not is_discrete_plot and all(
            not isinstance(point, list) for line in plot_groups for point in line
        ):
            # FIXME: is this right?
            y_min = min(plot_groups)[0]
            y_max = max(plot_groups)[0]
            x_min = 0
            x_max = len(plot_groups)

            plot_groups = [
                [[float(i + 1), l] for i, l in enumerate(plot_group)]
                for plot_group in plot_groups
            ]

    # Split into plot segments
    plot_groups = [[plot_group] for plot_group in plot_groups]
    if isinstance(x_range, (list, tuple)):
        x_min, m_max = x_range
        y_min, y_max = y_range

    for lidx, plot_group in enumerate(plot_groups):
        i = 0
        while i < len(plot_groups[lidx]):
            seg = plot_group[i]
            for j, point in enumerate(seg):
                x_min = min(x_min, point[0])
                x_max = max(x_min, point[0])
                y_min = min(y_min, point[1])
                y_max = max(y_max, point[1])
                if not (
                    isinstance(point[0], (int, float))
                    and isinstance(point[1], (int, float))
                ):
                    plot_groups[lidx].insert(i, seg[:j])
                    plot_groups[lidx][i + 1] = seg[j + 1 :]
                    i -= 1
                    break

            i += 1

    # FIXME: For now we are going to specify that the min points are (-.1, -.1)
    # or pretty close to (0, 0) for positive plots, so that the tick axes are set to zero.
    # See GraphicsBox.axis_ticks().
    if x_min > 0:
        x_min = -0.1
    if y_min > 0:
        y_min = -0.1

    x_range = x_min, x_max
    y_range = y_min, y_max

    is_axis_filling = is_discrete_plot
    if filling == "System`Axis":
        # TODO: Handle arbitary axis intercepts
        filling = 0.0
        is_axis_filling = True
    elif filling == "System`Bottom":
        filling = y_range[0]
    elif filling == "System`Top":
        filling = y_range[1]

    # constants to generate colors for a plot group
    hue = 0.67
    hue_pos = 0.236068
    hue_neg = -0.763932

    # List of graphics primitives that rendering will use to draw.
    # This includes the plot data, and overall graphics directives
    # like the Hue.
    graphics = []

    for index, plot_group in enumerate(plot_groups):
        graphics.append(Expression(SymbolHue, Real(hue), RealPoint6, RealPoint6))
        for segment in plot_group:
            mathics_segment = from_python(segment)
            if is_joined_plot:
                graphics.append(Expression(SymbolLine, mathics_segment))
                if filling is not None:
                    graphics.append(
                        Expression(
                            SymbolHue, Real(hue), RealPoint6, RealPoint6, RealPoint2
                        )
                    )
                    fill_area = list(segment)
                    fill_area.append([segment[-1][0], filling])
                    fill_area.append([segment[0][0], filling])
                    graphics.append(Expression(SymbolPolygon, from_python(fill_area)))
            elif is_axis_filling:
                graphics.append(Expression(SymbolPoint, mathics_segment))
                for mathics_point in mathics_segment:
                    graphics.append(
                        Expression(
                            SymbolLine,
                            ListExpression(
                                ListExpression(mathics_point[0], Integer0),
                                mathics_point,
                            ),
                        )
                    )
            else:
                graphics.append(Expression(SymbolPoint, mathics_segment))
                if filling is not None:
                    for point in segment:
                        graphics.append(
                            Expression(
                                SymbolLine,
                                from_python(
                                    [[point[0], filling], [point[0], point[1]]]
                                ),
                            )
                        )

        if index % 4 == 0:
            hue += hue_pos
        else:
            hue += hue_neg
        if hue > 1:
            hue -= 1
        if hue < 0:
            hue += 1

    options["System`PlotRange"] = from_python([x_range, y_range])

    if use_log_scale:
        options[SymbolLogPlot.name] = SymbolTrue

    return Expression(
        SymbolGraphics, ListExpression(*graphics), *options_to_rules(options)
    )


def eval_Plot(
    functions: List[Expression],
    apply_fn: Callable,
    x_name: str,
    start: int,
    stop: int,
    x_range: list,
    y_range,
    num_plot_points: int,
    mesh,
    list_is_expected: bool,
    exclusions: list,
    max_recursion: int,
    use_log_scale: bool,
    options: dict,
    evaluation: Evaluation,
) -> Expression:
    """
    Evaluation part of Plot[]

    Note: (?) indicates somewhat vague guesses.

    functions: is a list of Mathics M-Expressions to be evaluated
    start: minimum x-axis value
    stop:  maximum t x-axis value
    x_name; the name of the function parameter name used by ``functions``
    x_range: x-axis range of the form Automatic, All, or [min, max]
    y_range: y-axis range of the form Automatic, All, or [min, max]
    y_range: either Automatic, All, or of the form [min, max]
    num_plot_points: number of points to plot
    list_is_expected: list is expected in evaluation (?)
    max_recursion: maximum number of levels of recursion in evaluation (?)
    options: Plot options
    evaluation: Expression evaluation object typically needed in evaluation
    """
    # constants to generate colors
    hue = 0.67
    hue_pos = 0.236068
    hue_neg = -0.763932

    def get_points_range(points):
        xmin, xmax, ymin, ymax = get_points_minmax(points)
        if xmin is None or xmax is None:
            xmin, xmax = 0, 1
        if ymin is None or ymax is None:
            ymin, ymax = 0, 1
        return zero_to_one(xmax - xmin), zero_to_one(ymax - ymin)

    function_hues = []
    base_plot_points = []  # list of points in base subdivision
    plot_points = []  # list of all plotted points
    mesh_points = []

    # List of graphics primitives that rendering will use to draw.
    # This includes the plot data, and overall graphics directives
    # like the Hue.
    graphics = []

    for index, f in enumerate(functions):
        points = []
        xvalues = []  # x value for each point in points
        tmp_mesh_points = []  # For this function only
        continuous = False
        d = (stop - start) / (num_plot_points - 1)
        if use_log_scale:
            # Scale point values down by Log 10.
            # Tick mark values will be adjusted to be 10^n in GraphicsBox.
            f = Expression(SymbolLog10, f)
        compiled_fn = compile_quiet_function(f, [x_name], evaluation, list_is_expected)
        for i in range(num_plot_points):
            x_value = start + i * d
            point = apply_fn(compiled_fn, x_value)
            if point is not None:
                if continuous:
                    points[-1].append(point)
                    xvalues[-1].append(x_value)
                else:
                    points.append([point])
                    xvalues.append([x_value])
                continuous = True
            else:
                continuous = False

        base_points = []
        for line in points:
            base_points.extend(line)
        base_plot_points.extend(base_points)

        xmin, xmax = automatic_plot_range([xx for xx, yy in base_points])
        xscale = 1.0 / zero_to_one(xmax - xmin)
        ymin, ymax = automatic_plot_range([yy for xx, yy in base_points])
        yscale = 1.0 / zero_to_one(ymax - ymin)

        if mesh == "System`Full":
            for line in points:
                tmp_mesh_points.extend(line)

        def find_excl(excl):
            # Find which line the exclusion is in
            for line in range(len(xvalues)):  # TODO: Binary Search faster?
                if xvalues[line][0] <= excl and xvalues[line][-1] >= excl:
                    break
                if (
                    xvalues[line][-1] <= excl
                    and xvalues[min(line + 1, len(xvalues) - 1)][0] >= excl
                ):
                    return min(line + 1, len(xvalues) - 1), 0, False
            xi = 0
            for xi in range(len(xvalues[line]) - 1):
                if xvalues[line][xi] <= excl and xvalues[line][xi + 1] >= excl:
                    return line, xi + 1, True
            return line, xi + 1, False

        if exclusions != "System`None":
            for excl in exclusions:
                if excl != "System`Automatic":
                    l, xi, split_required = find_excl(excl)
                    if split_required:
                        xvalues.insert(l + 1, xvalues[l][xi:])
                        xvalues[l] = xvalues[l][:xi]
                        points.insert(l + 1, points[l][xi:])
                        points[l] = points[l][:xi]
                # assert(xvalues[l][-1] <= excl  <= xvalues[l+1][0])

        # Adaptive Sampling - loop again and interpolate highly angled
        # sections

        # Cos of the maximum angle between successive line segments
        ang_thresh = cos(pi / 180)

        for line, line_xvalues in zip(points, xvalues):
            recursion_count = 0
            smooth = False
            while not smooth and recursion_count < max_recursion:
                recursion_count += 1
                smooth = True
                i = 2
                while i < len(line):
                    vec1 = (
                        xscale * (line[i - 1][0] - line[i - 2][0]),
                        yscale * (line[i - 1][1] - line[i - 2][1]),
                    )
                    vec2 = (
                        xscale * (line[i][0] - line[i - 1][0]),
                        yscale * (line[i][1] - line[i - 1][1]),
                    )
                    try:
                        angle = (vec1[0] * vec2[0] + vec1[1] * vec2[1]) / sqrt(
                            (vec1[0] ** 2 + vec1[1] ** 2)
                            * (vec2[0] ** 2 + vec2[1] ** 2)
                        )
                    except ZeroDivisionError:
                        angle = 0.0
                    if abs(angle) < ang_thresh:
                        smooth = False
                        incr = 0

                        x_value = 0.5 * (line_xvalues[i - 1] + line_xvalues[i])

                        point = apply_fn(compiled_fn, x_value)
                        if point is not None:
                            line.insert(i, point)
                            line_xvalues.insert(i, x_value)
                            incr += 1

                        x_value = 0.5 * (line_xvalues[i - 2] + line_xvalues[i - 1])
                        point = apply_fn(compiled_fn, x_value)
                        if point is not None:
                            line.insert(i - 1, point)
                            line_xvalues.insert(i - 1, x_value)
                            incr += 1

                        i += incr
                    i += 1

        if exclusions == "System`None":  # Join all the Lines
            points = [[(xx, yy) for line in points for xx, yy in line]]

        graphics.append(Expression(SymbolHue, Real(hue), RealPoint6, RealPoint6))
        graphics.append(Expression(SymbolLine, from_python(points)))

        for line in points:
            plot_points.extend(line)

        if mesh == "System`All":
            for line in points:
                tmp_mesh_points.extend(line)

        if mesh != "System`None":
            mesh_points.append(tmp_mesh_points)

        function_hues.append(hue)

        if index % 4 == 0:
            hue += hue_pos
        else:
            hue += hue_neg
        if hue > 1:
            hue -= 1
        if hue < 0:
            hue += 1

    x_range = get_plot_range(
        [xx for xx, yy in base_plot_points], [xx for xx, yy in plot_points], x_range
    )
    y_range = get_plot_range(
        [yy for xx, yy in base_plot_points], [yy for xx, yy in plot_points], y_range
    )

    # FIXME: For now we are going to specify that the min points are (-.1, -.1)
    # or pretty close to (0, 0) for positive plots, so that the tick axes are set to zero.
    # See GraphicsBox.axis_ticks().
    if x_range[0] > 0:
        x_range = (-0.1, x_range[1])
    if y_range[0] > 0:
        y_range = (-0.1, y_range[1])

    options["System`PlotRange"] = from_python([x_range, y_range])

    if use_log_scale:
        options[SymbolLogPlot.name] = SymbolTrue

    if mesh != "None":
        for hue, points in zip(function_hues, mesh_points):
            graphics.append(Expression(SymbolHue, Real(hue), RealPoint6, RealPoint6))
            mesh_points = [to_mathics_list(xx, yy) for xx, yy in points]
            graphics.append(Expression(SymbolPoint, ListExpression(*mesh_points)))

    return Expression(
        SymbolGraphics, ListExpression(*graphics), *options_to_rules(options)
    )


def extract_pyreal(value) -> Optional[float]:
    if isinstance(value, (Real, Integer)):
        return chop(value).round_to_float()
    return None


def get_plot_range(values: Iterable, all_values: Iterable, option: str) -> tuple:
    """
    Returns a tuple of the min and max values in values.
    """
    if option == "System`Automatic":
        result = automatic_plot_range(values)
    elif option == "System`All":
        if not all_values:
            result = (0, 1)
        else:
            result = min(all_values), max(all_values)
    else:
        result = option
    if result[0] == result[1]:
        value = result[0]
        if value > 0:
            return 0, value * 2
        if value < 0:
            return value * 2, 0
        return -1, 1
    return result


def get_points_minmax(points: Iterable) -> tuple:
    """
    Return the minimum and maximum x and y values
    in a list of points.
    """
    xmin = xmax = ymin = ymax = None
    for line in points:
        for x, y in line:
            if xmin is None or x < xmin:
                xmin = x
            if xmax is None or x > xmax:
                xmax = x
            if ymin is None or y < ymin:
                ymin = y
            if ymax is None or y > ymax:
                ymax = y
    return xmin, xmax, ymin, ymax


def zero_to_one(value: Union[float, int]) -> Union[float, int]:
    """
    Return 1 only if ``value`` is zero, otherwise keep the value as is.

    This is useful in scaling when the value can be used as
    a divisor or when determining the number of points to plot, and we want to
    assure there is at least one point plotted.
    """
    return 1 if value == 0 else value
