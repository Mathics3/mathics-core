"""
Evaluation routines for 2D plotting.

These routines build Mathics M-Expressions that describe plots.
Note that this is distinct from boxing, formatting and rendering e.g. to SVG.
That is done as another pass after M-expression evaluation finishes.
"""

import itertools

import palettable

from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Integer, Integer0, MachineReal, String
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolBlack,
    SymbolEdgeForm,
    SymbolFaceForm,
    SymbolGraphics,
    SymbolGrid,
    SymbolLine,
    SymbolRGBColor,
    SymbolRow,
    SymbolRule,
    SymbolStyle,
)
from mathics.eval.drawing.colors import get_color_palette
from mathics.eval.drawing.plot import get_plot_range

SymbolText = Symbol("Text")
SymbolRectangle = Symbol("System`Rectangle")
TwoTenths = MachineReal(0.2)
MTwoTenths = -TwoTenths


def eval_chart(self, points, evaluation: Evaluation, options: dict):
    """Evaluate a chart from a list of points"""
    points = points.evaluate(evaluation)

    if points.get_head_name() != "System`List" or not points.elements:
        return

    if points.elements[0].get_head_name() == "System`List":
        if not all(group.get_head_name() == "System`List" for group in points.elements):
            return
        multiple_colors = True
        groups = points.elements
    else:
        multiple_colors = False
        groups = [points]

    chart_legends = self.get_option(options, "ChartLegends", evaluation)
    has_chart_legends = chart_legends.get_head_name() == "System`List"
    if has_chart_legends:
        multiple_colors = True

    def to_number(x):
        if isinstance(x, Integer):
            return float(x.get_int_value())
        return x.round_to_float(evaluation=evaluation)

    data = [[to_number(x) for x in group.elements] for group in groups]

    chart_style = self.get_option(options, "ChartStyle", evaluation)
    if isinstance(chart_style, Symbol) and chart_style.get_name() == "System`Automatic":
        chart_style = String("Automatic")

    if chart_style.get_head_name() == "System`List":
        colors = chart_style.elements
        spread_colors = False
    elif isinstance(chart_style, String):
        if chart_style.get_string_value() == "Automatic":
            mpl_colors = palettable.wesanderson.Moonrise1_5.mpl_colors
        else:
            mpl_colors = get_color_palette(chart_style.get_string_value(), None)
            if mpl_colors is None:
                return
            multiple_colors = True

        if not multiple_colors and not self.never_monochrome:
            colors = [to_expression(SymbolRGBColor, *mpl_colors[0])]
        else:
            colors = [to_expression(SymbolRGBColor, *c) for c in mpl_colors]
        spread_colors = True
    else:
        return

    def legends(names):
        if not data:
            return

        n = len(data[0])
        for d in data[1:]:
            if len(d) != n:
                return  # data groups should have same size

        def box(color):
            return Expression(
                SymbolGraphics,
                ListExpression(
                    Expression(SymbolFaceForm, color), Expression(SymbolRectangle)
                ),
                Expression(
                    SymbolRule,
                    Symbol("ImageSize"),
                    ListExpression(Integer(50), Integer(50)),
                ),
            )

        rows_per_col = 5

        n_cols = 1 + len(names) // rows_per_col
        if len(names) % rows_per_col == 0:
            n_cols -= 1

        if n_cols == 1:
            n_rows = len(names)
        else:
            n_rows = rows_per_col

        for i in range(n_rows):
            items = []
            for j in range(n_cols):
                k = 1 + i + j * rows_per_col
                if k - 1 < len(names):
                    items.extend([box(color(k, n)), names[k - 1]])
                else:
                    items.extend([String(""), String("")])
            yield ListExpression(*items)

    def color(k, n):
        if spread_colors and n < len(colors):
            index = int(k * (len(colors) - 1)) // n
            return colors[index]
        return colors[(k - 1) % len(colors)]

    chart = self._draw(data, color, evaluation, options)

    if has_chart_legends:
        grid = Expression(
            SymbolGrid, ListExpression(*list(legends(chart_legends.elements)))
        )
        chart = Expression(SymbolRow, ListExpression(chart, grid))

    return chart


def draw_bar_chart(self, data, color, evaluation, options):
    def vector2(x, y) -> ListExpression:
        return to_mathics_list(x, y)

    def boxes():
        w = 0.9
        s = 0.06
        w_half = 0.5 * w
        x = 0.1 + s + w_half

        for y_values in data:
            y_length = len(y_values)
            for i, y in enumerate(y_values):
                x0 = x - w_half
                x1 = x0 + w
                yield (i + 1, y_length), x0, x1, y
                x = x1 + s + w_half

            x += 0.2

    def rectangles():
        yield Expression(SymbolEdgeForm, SymbolBlack)

        last_x1 = 0

        for (k, n), x0, x1, y in boxes():
            yield Expression(
                SymbolStyle,
                Expression(
                    SymbolRectangle,
                    to_mathics_list(x0, 0),
                    to_mathics_list(x1, y),
                ),
                color(k, n),
            )

            last_x1 = x1

        yield Expression(
            SymbolLine, ListExpression(vector2(0, 0), vector2(last_x1, Integer0))
        )

    def axes():
        yield Expression(SymbolFaceForm, SymbolBlack)

        def points(x):
            return ListExpression(vector2(x, 0), vector2(x, MTwoTenths))

        for (k, n), x0, x1, y in boxes():
            if k == 1:
                yield Expression(SymbolLine, points(x0))
            if k == n:
                yield Expression(SymbolLine, points(x1))

    def labels(names):
        yield Expression(SymbolFaceForm, SymbolBlack)

        for (k, n), x0, x1, y in boxes():
            if k <= len(names):
                name = names[k - 1]
                yield Expression(SymbolText, name, vector2((x0 + x1) / 2, MTwoTenths))

    x_coords = list(itertools.chain(*[[x0, x1] for (k, n), x0, x1, y in boxes()]))
    y_coords = [0] + [y for (k, n), x0, x1, y in boxes()]

    graphics = list(rectangles()) + list(axes())

    x_range = "System`All"
    y_range = "System`All"

    x_range = list(get_plot_range(x_coords, x_coords, x_range))
    y_range = list(get_plot_range(y_coords, y_coords, y_range))

    chart_labels = self.get_option(options, "ChartLabels", evaluation)
    if chart_labels.get_head_name() == "System`List":
        graphics.extend(list(labels(chart_labels.elements)))
        y_range[0] = -0.4  # room for labels at the bottom

    # FIXME: this can't be right...
    # always specify -.1 as the minimum x plot range, as this will make the y axis appear
    # at origin (0,0); otherwise it will be shifted right; see GraphicsBox.axis_ticks().
    x_range[0] = -0.1

    options["System`PlotRange"] = ListExpression(vector2(*x_range), vector2(*y_range))

    return Expression(
        SymbolGraphics, ListExpression(*graphics), *options_to_rules(options)
    )
