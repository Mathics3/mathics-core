# -*- coding: utf-8 -*-
"""
Lower-level formatter Mathics objects as plain text.
"""


from mathics.builtin.box.graphics import GraphicsBox
from mathics.builtin.box.graphics3d import Graphics3DBox
from mathics.builtin.box.layout import (
    FractionBox,
    GridBox,
    RowBox,
    SqrtBox,
    StyleBox,
    SubscriptBox,
    SubsuperscriptBox,
    SuperscriptBox,
)
from mathics.core.atoms import String
from mathics.core.exceptions import BoxConstructError
from mathics.core.formatter import add_conversion_fn, lookup_method
from mathics.core.symbols import Atom, SymbolTrue


def boxes_to_text(boxes, **options) -> str:
    return lookup_method(boxes, "text")(boxes, **options)


def string(self, **options) -> str:
    value = self.value
    show_string_characters = (
        options.get("System`ShowStringCharacters", None) is SymbolTrue
    )
    if value.startswith('"') and value.endswith('"'):  # nopep8
        if not show_string_characters:
            value = value[1:-1]
    return value


add_conversion_fn(String, string)


def fractionbox(self, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    num_text = boxes_to_text(self.num, **options)
    den_text = boxes_to_text(self.den, **options)
    if isinstance(self.num, RowBox):
        num_text = f"({num_text})"
    if isinstance(self.den, RowBox):
        den_text = f"({den_text})"

    return " / ".join([num_text, den_text])


add_conversion_fn(FractionBox, fractionbox)


def gridbox(self, elements=None, **box_options) -> str:
    if not elements:
        elements = self._elements
    evaluation = box_options.get("evaluation", None)
    items, options = self.get_array(elements, evaluation)

    result = ""
    if not items:
        return ""
    try:
        widths = [0] * max(1, max(len(row) for row in items if isinstance(row, tuple)))
    except ValueError:
        widths = [0]

    cells = [
        [
            # TODO: check if this evaluation is necesary.
            boxes_to_text(item, **box_options).splitlines()
            for item in row
        ]
        if isinstance(row, tuple)
        else [boxes_to_text(row, **box_options).splitlines()]
        for row in items
    ]

    # compute widths
    full_width = 0
    for i, row in enumerate(cells):
        for index, cell in enumerate(row):
            if index >= len(widths):
                raise BoxConstructError
            if not isinstance(items[i], tuple):
                for line in cell:
                    full_width = max(full_width, len(line))
            else:
                for line in cell:
                    widths[index] = max(widths[index], len(line))

    full_width = max(sum(widths), full_width)

    for row_index, row in enumerate(cells):
        if row_index > 0:
            result += "\n"
        k = 0
        while True:
            line_exists = False
            line = ""
            for cell_index, cell in enumerate(row):
                if len(cell) > k:
                    line_exists = True
                    text = cell[k]
                else:
                    text = ""
                line += text
                if isinstance(items[row_index], tuple):
                    if cell_index < len(row) - 1:
                        line += " " * (widths[cell_index] - len(text))
                        # if cell_index < len(row) - 1:
                        line += "   "

            if line_exists:
                result += line + "\n"
            else:
                break
            k += 1
    return result


add_conversion_fn(GridBox, gridbox)


def sqrtbox(self, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    if self.index:
        return "Sqrt[%s,%s]" % (
            boxes_to_text(self.radicand, **options),
            boxes_to_text(self.index, **options),
        )
    return "Sqrt[%s]" % (boxes_to_text(self.radicand, **options))


add_conversion_fn(SqrtBox, sqrtbox)


def superscriptbox(self, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    fmt_str = "%s^%s" if isinstance(self.superindex, Atom) else "%s^(%s)"
    return fmt_str % (
        boxes_to_text(self.base, **options),
        boxes_to_text(self.superindex, **options),
    )


add_conversion_fn(SuperscriptBox, superscriptbox)


def subscriptbox(self, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    return "Subscript[%s, %s]" % (
        boxes_to_text(self.base, **options),
        boxes_to_text(self.subindex, **options),
    )


add_conversion_fn(SubscriptBox, subscriptbox)


def subsuperscriptbox(self, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    return "Subsuperscript[%s, %s, %s]" % (
        boxes_to_text(self.base, **options),
        boxes_to_text(self.subindex, **options),
        boxes_to_text(self.superindex, **options),
    )


add_conversion_fn(SubsuperscriptBox, subsuperscriptbox)


def rowbox(self, elements=None, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    return "".join([boxes_to_text(element, **options) for element in self.items])


add_conversion_fn(RowBox, rowbox)


def stylebox(self, **options) -> str:
    options.pop("evaluation", None)
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    return boxes_to_text(self.boxes, **options)


add_conversion_fn(StyleBox, stylebox)


def graphicsbox(self, elements=None, **options) -> str:
    if not elements:
        elements = self._elements

    self._prepare_elements(elements, options)  # to test for Box errors
    return "-Graphics-"


add_conversion_fn(GraphicsBox, graphicsbox)


def graphics3dbox(self, elements=None, **options) -> str:
    if not elements:
        elements = self._elements
    return "-Graphics3D-"


add_conversion_fn(Graphics3DBox, graphics3dbox)
