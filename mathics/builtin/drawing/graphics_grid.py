# -*- coding: utf-8 -*-
"""
Arrays of Graphics

'GraphicsGrid', 'GraphicsRow' and 'GraphicsColumn' lay graphics out in a \
grid. As in WMA, the result is a single 'Graphics', made of one 'Inset' \
per graphic.
"""

from typing import List, Optional, Tuple

from mathics.core.atoms import Integer, Real
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolList
from mathics.core.systemsymbols import (
    SymbolGraphics,
    SymbolImageScaled,
    SymbolInset,
    SymbolLine,
    SymbolRule,
    SymbolRuleDelayed,
)

# This tells documentation how to sort this module
sort_order = "mathics.builtin.plotting-graphing-and-drawing.graphics-grid"

# The width of a cell for a graphic without a numeric ImageSize, as in WMA.
DEFAULT_CELL_WIDTH = 360.0
# The space between cells, in printer's points, when no Spacings are given.
DEFAULT_SPACING = 15.0

SymbolAspectRatio = Symbol("System`AspectRatio")
SymbolFrame = Symbol("System`Frame")
SymbolGraphicsSpacing = Symbol("System`GraphicsSpacing")
SymbolImageSize = Symbol("System`ImageSize")
SymbolPlotRange = Symbol("System`PlotRange")
SymbolSpacings = Symbol("System`Spacings")
SymbolAll = Symbol("System`All")
SymbolTrue = Symbol("System`True")


def _number(expr) -> Optional[float]:
    if isinstance(expr, (Integer, Real)):
        return float(expr.value)
    return None


def _graphics_option(graphics, name: str):
    """The value of option `name` given in a Graphics expression, or None."""
    if not graphics.has_form(SymbolGraphics, None):
        return None
    for element in graphics.elements[1:]:
        if element.has_form((SymbolRule, SymbolRuleDelayed), 2):
            if element.elements[0].get_name() == name:
                return element.elements[1]
    return None


def _cell_size(item) -> Tuple[float, float]:
    """The natural size, in printer's points, of one item of the grid."""
    width = DEFAULT_CELL_WIDTH
    size = _graphics_option(item, "System`ImageSize")
    if size is not None:
        if _number(size) is not None:
            width = _number(size)
        elif size.has_form(SymbolList, 2) and _number(size.elements[0]) is not None:
            width = _number(size.elements[0])
            if _number(size.elements[1]) is not None:
                return width, _number(size.elements[1])
    ratio = _number(_graphics_option(item, "System`AspectRatio") or Integer(0))
    return width, width * (ratio if ratio else 1.0)


def _spacing(options: dict, cell: float) -> float:
    """The space between cells: Spacings below 1 are a fraction of the cell."""
    value = options.get("System`Spacings")
    if value is None or value.get_name() == "System`Automatic":
        value = options.get("System`GraphicsSpacing")
    if value is not None and value.has_form(SymbolList, 2):
        value = value.elements[0]
    number = _number(value) if value is not None else None
    if number is None:
        return DEFAULT_SPACING
    return number * cell if number < 1 else number


def graphics_grid(
    rows: List[List], options: dict, evaluation: Evaluation
) -> Optional[Expression]:
    """
    A Graphics with the items of `rows` (a list of lists) laid out in a grid,
    each one in an Inset centered in its cell. Row 1 is at the top.
    """
    if not rows or not any(rows):
        return None
    ncols = max(len(row) for row in rows)
    sizes = [[_cell_size(item) for item in row] for row in rows]
    col_widths = [
        max((sizes[i][j][0] for i in range(len(rows)) if j < len(rows[i])), default=0)
        for j in range(ncols)
    ]
    row_heights = [max((s[1] for s in row), default=0) for row in sizes]
    gap = _spacing(options, max(col_widths + row_heights))

    # Cell boundaries: gap/2 around each cell, so a gap between two cells.
    xs = [0.0]
    for w in col_widths:
        xs.append(xs[-1] + w + gap)
    ys = [0.0]
    for h in row_heights:
        ys.append(ys[-1] + h + gap)
    width, height = xs[-1], ys[-1]

    insets = []
    for i, row in enumerate(rows):
        for j, item in enumerate(row):
            if item.has_form(SymbolList, 0) or item.get_name() == "System`Null":
                continue
            center = ListExpression(
                Real((xs[j] + xs[j + 1]) / 2), Real(-(ys[i] + ys[i + 1]) / 2)
            )
            insets.append(
                Expression(
                    SymbolInset,
                    item,
                    center,
                    Expression(SymbolImageScaled, ListExpression(Real(0.5), Real(0.5))),
                    ListExpression(Real(sizes[i][j][0]), Real(sizes[i][j][1])),
                )
            )

    primitives = [ListExpression(*insets)]
    frame = options.get("System`Frame")
    if frame is not None and frame in (SymbolAll, SymbolTrue):
        lines = [
            ListExpression(
                ListExpression(Real(x), Real(0.0)),
                ListExpression(Real(x), Real(-height)),
            )
            for x in xs
        ] + [
            ListExpression(
                ListExpression(Real(0.0), Real(-y)),
                ListExpression(Real(width), Real(-y)),
            )
            for y in ys
        ]
        primitives.append(Expression(SymbolLine, ListExpression(*lines)))

    graphics_options = [
        Expression(
            SymbolRule,
            SymbolPlotRange,
            ListExpression(
                ListExpression(Real(0.0), Real(width)),
                ListExpression(Real(-height), Real(0.0)),
            ),
        ),
    ]
    image_size = options.get("System`ImageSize")
    if image_size is None or image_size.get_name() == "System`Automatic":
        image_size = Integer(round(width))
    graphics_options.append(Expression(SymbolRule, SymbolImageSize, image_size))
    for name, value in options.items():
        if name in (
            "System`Spacings",
            "System`GraphicsSpacing",
            "System`Frame",
            "System`ImageSize",
        ):
            continue
        graphics_options.append(Expression(SymbolRule, Symbol(name), value))
    return Expression(SymbolGraphics, ListExpression(*primitives), *graphics_options)


class _GraphicsGridBase(Builtin):
    options = {
        "Spacings": "Automatic",
        "GraphicsSpacing": "Automatic",
        "Frame": "None",
        "ImageSize": "Automatic",
        "Background": "None",
    }

    def _options(self, options) -> dict:
        return {
            name: value
            for name, value in options.items()
            if not (
                value.get_name() == "System`Automatic"
                or (
                    name in ("System`Frame", "System`Background")
                    and value.get_name() == "System`None"
                )
            )
        }


class GraphicsGrid(_GraphicsGridBase):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/GraphicsGrid.html</url>

    <dl>
      <dt>'GraphicsGrid'[{{$g_{11}$, $g_{12}$, ...}, ...}]
      <dd>a graphic in which the $g_{ij}$ are laid out in a grid.
    </dl>

    The result is a 'Graphics' with one 'Inset' for each graphic:
    >> GraphicsGrid[{{Graphics[Disk[]], Graphics[Circle[]]}, {Graphics[Rectangle[]]}}]
     = -Graphics-

    'Spacings' sets the space between the cells, 'Frame -> All' draws lines around them:
    >> GraphicsGrid[{{Graphics[Disk[]], Graphics[Circle[]]}}, Spacings -> 0, Frame -> All]
     = -Graphics-
    """

    summary_text = "lay out graphics in a grid"

    def eval(self, rows, evaluation: Evaluation, options):
        "GraphicsGrid[rows_List, OptionsPattern[GraphicsGrid]]"
        if not all(row.has_form(SymbolList, None) for row in rows.elements):
            return None
        return graphics_grid(
            [list(row.elements) for row in rows.elements],
            self._options(options),
            evaluation,
        )


class GraphicsRow(_GraphicsGridBase):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/GraphicsRow.html</url>

    <dl>
      <dt>'GraphicsRow'[{$g_1$, $g_2$, ...}]
      <dd>a graphic in which the $g_i$ are laid out in a row.
    </dl>

    >> GraphicsRow[{Graphics[Disk[]], Graphics[Circle[]]}]
     = -Graphics-
    """

    summary_text = "lay out graphics in a row"

    def eval(self, items, evaluation: Evaluation, options):
        "GraphicsRow[items_List, OptionsPattern[GraphicsRow]]"
        return graphics_grid([list(items.elements)], self._options(options), evaluation)


class GraphicsColumn(_GraphicsGridBase):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/GraphicsColumn.html</url>

    <dl>
      <dt>'GraphicsColumn'[{$g_1$, $g_2$, ...}]
      <dd>a graphic in which the $g_i$ are laid out in a column.
    </dl>

    >> GraphicsColumn[{Graphics[Disk[]], Graphics[Circle[]]}]
     = -Graphics-
    """

    summary_text = "lay out graphics in a column"

    def eval(self, items, evaluation: Evaluation, options):
        "GraphicsColumn[items_List, OptionsPattern[GraphicsColumn]]"
        return graphics_grid(
            [[item] for item in items.elements], self._options(options), evaluation
        )


class GraphicsArray(_GraphicsGridBase):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/GraphicsArray.html</url>

    <dl>
      <dt>'GraphicsArray'[{$g_1$, $g_2$, ...}]
      <dd>is an obsolete form of 'GraphicsRow'.

      <dt>'GraphicsArray'[{{$g_{11}$, $g_{12}$, ...}, ...}]
      <dd>is an obsolete form of 'GraphicsGrid'.
    </dl>

    >> GraphicsArray[{Graphics[Disk[]], Graphics[Circle[]]}]
     : GraphicsArray is obsolete. Switching to GraphicsGrid.
     = -Graphics-
    """

    messages = {"obs": "GraphicsArray is obsolete. Switching to GraphicsGrid."}
    summary_text = "obsolete form of GraphicsGrid and GraphicsRow"

    def eval(self, items, evaluation: Evaluation, options):
        "GraphicsArray[items_List, OptionsPattern[GraphicsArray]]"
        evaluation.message("GraphicsArray", "obs")
        if items.elements and all(
            item.has_form(SymbolList, None) for item in items.elements
        ):
            rows = [list(row.elements) for row in items.elements]
        else:
            rows = [list(items.elements)]
        return graphics_grid(rows, self._options(options), evaluation)
