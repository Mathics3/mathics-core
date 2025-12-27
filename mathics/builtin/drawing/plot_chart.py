"""
Charts

A Chart represents categorical or statistical data in some form.
"""

from math import cos, pi, sin

from mathics.builtin.graphics import Graphics
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Integer0, Real, String
from mathics.core.attributes import A_HOLD_ALL, A_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolBlack,
    SymbolEdgeForm,
    SymbolGraphics,
    SymbolStyle,
)
from mathics.eval.drawing.charts import draw_bar_chart, eval_chart
from mathics.eval.nevaluator import eval_N

# This tells documentation how to sort this module
sort_order = "mathics.builtin.chart"

SymbolDisk = Symbol("Disk")
SymbolFaceForm = Symbol("FaceForm")
SymbolText = Symbol("Text")

TwoTenths = Real(0.2)
MTwoTenths = -TwoTenths


class _Chart(Builtin):
    attributes = A_HOLD_ALL | A_PROTECTED
    never_monochrome = False
    options = Graphics.options.copy()
    options.update(
        {
            "Mesh": "None",
            "PlotRange": "Automatic",
            "ChartLabels": "None",
            "ChartLegends": "None",
            "ChartStyle": "Automatic",
        }
    )

    def _draw(self, data, color, evaluation: Evaluation, options: dict):
        raise NotImplementedError()

    def eval(self, points, evaluation: Evaluation, options: dict):
        "%(name)s[points_, OptionsPattern[%(name)s]]"
        return eval_chart(self, points, evaluation, options)


class BarChart(_Chart):
    """
    <url>:WMA link: https://reference.wolfram.com/language/ref/BarChart.html</url>
    <dl>
        <dt>'BarChart'[{$b_1$, $b_2$ ...}]
        <dd>makes a bar chart with lengths $b_1$, $b_2$, ....
    </dl>

    Drawing options include -
    Charting:
    <ul>
      <li>Mesh
      <li>PlotRange
      <li>ChartLabels
      <li>ChartLegends
      <li>ChartStyle
    </ul>

    BarChart specific:
    <ul>
      <li>Axes  (default {False, True})
      <li>AspectRatio: (default 1 / GoldenRatio)
    </ul>

    A bar chart of a list of heights:
    >> BarChart[{1, 4, 2}]
     = -Graphics-

    >> BarChart[{1, 4, 2}, ChartStyle -> {Red, Green, Blue}]
     = -Graphics-

    >> BarChart[{{1, 2, 3}, {2, 3, 4}}]
     = -Graphics-

    Chart several datasets with categorical labels:
    >> BarChart[{{1, 2, 3}, {2, 3, 4}}, ChartLabels -> {"a", "b", "c"}]
     = -Graphics-

    >> BarChart[{{1, 5}, {3, 4}}, ChartStyle -> {{EdgeForm[Thin], White}, {EdgeForm[Thick], White}}]
     = -Graphics-
    """

    options = _Chart.options.copy()
    options.update(
        {
            "Axes": "{False, True}",
            "AspectRatio": "1 / GoldenRatio",
        }
    )

    summary_text = "draw a bar chart"

    def _draw(self, data, color, evaluation, options):
        """Draw a bar chart"""
        return draw_bar_chart(self, data, color, evaluation, options)


class PieChart(_Chart):
    """
    <url>:Pie Chart: https://en.wikipedia.org/wiki/Pie_chart</url> \
    (<url>:WMA link: https://reference.wolfram.com/language/ref/PieChart.html</url>)
    <dl>
      <dt>'PieChart'[{$a_1$, $a_2$ ...}]
      <dd>draws a pie chart with sector angles proportional to $a_1$, $a_2$, ....
    </dl>

    Drawing options include -
    Charting:
    <ul>
      <li>Mesh
      <li>PlotRange
      <li>ChartLabels
      <li>ChartLegends
      <li>ChartStyle
    </ul>

    PieChart specific:
    <ul>
      <li>Axes (default: False, False)
      <li>AspectRatio (default 1)
      <li>SectorOrigin: (default {Automatic, 0})
      <li>SectorSpacing" (default Automatic)
    </ul>

    A hypothetical comparison between types of pets owned:
    >> PieChart[{30, 20, 10}, ChartLabels -> {Dogs, Cats, Fish}]
     = -Graphics-

    A doughnut chart for a list of values:
    >> PieChart[{8, 16, 2}, SectorOrigin -> {Automatic, 1.5}]
     = -Graphics-

    A Pie chart with multiple datasets:
    >> PieChart[{{10, 20, 30}, {15, 22, 30}}]
     = -Graphics-

    Same as the above, but without gaps between the groups of data:
    >> PieChart[{{10, 20, 30}, {15, 22, 30}}, SectorSpacing -> None]
     = -Graphics-

    The doughnut chart above with labels on each of the 3 pieces:
    >> PieChart[{{10, 20, 30}, {15, 22, 30}}, ChartLabels -> {A, B, C}]
     = -Graphics-

    Negative values are removed, the data below is the same as {1, 3}:
    >> PieChart[{1, -1, 3}]
     = -Graphics-
    """

    never_monochrome = True
    options = _Chart.options.copy()
    options.update(
        {
            "Axes": "{False, False}",
            "AspectRatio": "1",
            "SectorOrigin": "{Automatic, 0}",
            "SectorSpacing": "Automatic",
        }
    )

    summary_text = "draw a pie chart"

    def _draw(self, data, color, evaluation, options: dict):
        data = [[max(0.0, x) for x in group] for group in data]

        sector_origin = self.get_option(options, "SectorOrigin", evaluation)
        if not sector_origin.has_form("List", 2):
            return
        sector_origin = eval_N(sector_origin, evaluation)

        orientation = sector_origin.elements[0]
        if (
            isinstance(orientation, Symbol)
            and orientation.get_name() == "System`Automatic"
        ):
            sector_phi = pi
            sector_sign = -1.0
        elif orientation.has_form("List", 2) and isinstance(
            orientation.elements[1], String
        ):
            sector_phi = orientation.elements[0].round_to_float()
            clock_name = orientation.elements[1].get_string_value()
            if clock_name == "Clockwise":
                sector_sign = -1.0
            elif clock_name == "Counterclockwise":
                sector_sign = 1.0
            else:
                return
        else:
            return

        sector_spacing = self.get_option(options, "SectorSpacing", evaluation)
        if isinstance(sector_spacing, Symbol):
            if sector_spacing.get_name() == "System`Automatic":
                sector_spacing = ListExpression(Integer0, TwoTenths)
            elif sector_spacing.get_name() == "System`None":
                sector_spacing = ListExpression(Integer0, Integer0)
            else:
                return
        if not sector_spacing.has_form("List", 2):
            return
        segment_spacing = 0.0  # not yet implemented; needs real arc graphics
        radius_spacing = max(0.0, min(1.0, sector_spacing.elements[1].round_to_float()))

        def vector2(x, y) -> ListExpression:
            return ListExpression(Real(x), Real(y))

        def radii():
            outer = 2.0
            inner = sector_origin.elements[1].round_to_float()
            n = len(data)

            d = (outer - inner) / n

            r0 = outer
            for i in range(n):
                r1 = r0 - d
                if i > 0:
                    r0 -= radius_spacing * d
                yield (r0, r1)
                r0 = r1

        def phis(values):
            s = sum(values)

            t = 0.0
            pi2 = pi * 2.0
            phi0 = pi
            spacing = sector_sign * segment_spacing / 2.0

            for k, value in enumerate(values):
                t += value
                phi1 = sector_phi + sector_sign * (t / s) * pi2

                yield (phi0 + spacing, phi1 - spacing)
                phi0 = phi1

        def segments():
            yield Expression(SymbolEdgeForm, SymbolBlack)

            origin = vector2(0.0, 0.0)

            for values, (r0, r1) in zip(data, radii()):
                radius = vector2(r0, r0)

                n = len(values)

                for k, (phi0, phi1) in enumerate(phis(values)):
                    yield Expression(
                        SymbolStyle,
                        Expression(SymbolDisk, origin, radius, vector2(phi0, phi1)),
                        color(k + 1, n),
                    )

                if r1 > 0.0:
                    yield Expression(
                        SymbolStyle,
                        Expression(SymbolDisk, origin, vector2(r1, r1)),
                        Symbol("White"),
                    )

        def labels(names):
            yield Expression(SymbolFaceForm, SymbolBlack)

            for values, (r0, r1) in zip(data, radii()):
                for name, (phi0, phi1) in zip(names, phis(values)):
                    r = (r0 + r1) / 2.0
                    phi = (phi0 + phi1) / 2.0
                    yield Expression(
                        SymbolText, name, vector2(r * cos(phi), r * sin(phi))
                    )

        graphics = list(segments())

        chart_labels = self.get_option(options, "ChartLabels", evaluation)
        if chart_labels.get_head_name() == "System`List":
            graphics.extend(list(labels(chart_labels.elements)))

        options["System`PlotRange"] = ListExpression(
            vector2(-2.0, 2.0), vector2(-2.0, 2.0)
        )

        return Expression(
            SymbolGraphics, ListExpression(*graphics), *options_to_rules(options)
        )
