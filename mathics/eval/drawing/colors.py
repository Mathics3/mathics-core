"""
Color functions

"""

from typing import Optional

import palettable

from mathics.core.atoms import Integer0, Integer1, MachineReal, String
from mathics.core.convert.expression import to_expression
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolBlend,
    SymbolColorData,
    SymbolFunction,
    SymbolMap,
    SymbolRGBColor,
    SymbolSlot,
)

SymbolColorDataFunction = Symbol("ColorDataFunction")


class _GradientColorScheme:
    def colors(self) -> list:
        """return the list of colors"""
        raise NotImplementedError

    def color_data_function(self, name: str) -> Expression:
        """Return a function that compute the colors"""
        colors = ListExpression(
            *[
                to_expression(
                    SymbolRGBColor, *color, elements_conversion_fn=MachineReal
                )
                for color in self.colors()
            ]
        )
        blend = Expression(
            SymbolFunction,
            Expression(SymbolBlend, colors, Expression(SymbolSlot, Integer1)),
        )
        arguments = [
            String(name),
            String("Gradients"),
            ListExpression(Integer0, Integer1),
            blend,
        ]
        return Expression(SymbolColorDataFunction, *arguments)


class _PalettableGradient(_GradientColorScheme):
    def __init__(self, palette, is_reversed: bool):
        self.palette = palette
        self.reversed = is_reversed

    def colors(self) -> list:
        colors = self.palette.mpl_colors
        if self.reversed:
            colors = list(reversed(colors))
        return colors


class _PredefinedGradient(_GradientColorScheme):
    _colors: list

    def __init__(self, colors: list):
        self._colors = colors

    def colors(self) -> list:
        return self._colors


COLOR_PALETTES = {
    "LakeColors": _PredefinedGradient(
        [
            (0.293416, 0.0574044, 0.529412),
            (0.563821, 0.527565, 0.909499),
            (0.762631, 0.846998, 0.914031),
            (0.941176, 0.906538, 0.834043),
        ]
    ),
    "Pastel": _PalettableGradient(palettable.colorbrewer.qualitative.Pastel1_9, False),
    "Rainbow": _PalettableGradient(palettable.colorbrewer.diverging.Spectral_9, True),
    "RedBlueTones": _PalettableGradient(
        palettable.colorbrewer.diverging.RdBu_11, False
    ),
    "GreenPinkTones": _PalettableGradient(
        palettable.colorbrewer.diverging.PiYG_9, False
    ),
    "GrayTones": _PalettableGradient(palettable.colorbrewer.sequential.Greys_9, False),
    "SolarColors": _PalettableGradient(palettable.colorbrewer.sequential.OrRd_9, True),
    "CherryTones": _PalettableGradient(palettable.colorbrewer.sequential.Reds_9, True),
    "FuchsiaTones": _PalettableGradient(palettable.colorbrewer.sequential.RdPu_9, True),
    "SiennaTones": _PalettableGradient(
        palettable.colorbrewer.sequential.Oranges_9, True
    ),
    # specific to Mathics
    "Paired": _PalettableGradient(palettable.colorbrewer.qualitative.Paired_9, False),
    "Accent": _PalettableGradient(palettable.colorbrewer.qualitative.Accent_8, False),
    "Aquatic": _PalettableGradient(palettable.wesanderson.Aquatic1_5, False),
    "Zissou": _PalettableGradient(palettable.wesanderson.Zissou_5, False),
    "Tableau": _PalettableGradient(palettable.tableau.Tableau_20, False),
    "TrafficLight": _PalettableGradient(palettable.tableau.TrafficLight_9, False),
    "Moonrise1": _PalettableGradient(palettable.wesanderson.Moonrise1_5, False),
}


def get_color_palette(name, evaluation):
    palette = COLOR_PALETTES.get(name, None)
    if palette is None:
        evaluation.message("ColorData", "notent", name)
        return None
    return palette.colors()


def gradient_palette(
    color_function: BaseElement, n: int, evaluation: Evaluation
) -> Optional[list]:  # always returns RGB values
    """Return a list of rgb color components"""
    if isinstance(color_function, String):
        color_data = Expression(SymbolColorData, color_function).evaluate(evaluation)
        if not color_data.has_form("ColorDataFunction", 4):
            return None
        _, kind, interval, blend = color_data.elements
        if not isinstance(kind, String) or kind.get_string_value() != "Gradients":
            return None
        if not interval.has_form("List", 2):
            return None
        x0, x1 = (x.round_to_float() for x in interval.elements)
    else:
        blend = color_function
        x0 = 0.0
        x1 = 1.0

    xd = x1 - x0
    offsets = [MachineReal(x0 + float(xd * i) / float(n - 1)) for i in range(n)]
    colors = Expression(SymbolMap, blend, ListExpression(*offsets)).evaluate(evaluation)
    if len(colors.elements) != n:
        return None

    from mathics.builtin.colors.color_directives import ColorError, expression_to_color

    try:
        objects = [expression_to_color(x) for x in colors.elements]
        if any(x is None for x in objects):
            return None
        return [x.to_rgba()[:3] for x in objects]
    except ColorError:
        return None
