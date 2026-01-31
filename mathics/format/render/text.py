# -*- coding: utf-8 -*-
"""
Lower-level formatter Mathics objects as plain text.
"""


from mathics.builtin.box.graphics import GraphicsBox
from mathics.builtin.box.graphics3d import Graphics3DBox
from mathics.builtin.box.layout import (
    FormBox,
    FractionBox,
    GridBox,
    InterpretationBox,
    PaneBox,
    RowBox,
    SqrtBox,
    StyleBox,
    SubscriptBox,
    SubsuperscriptBox,
    SuperscriptBox,
    TagBox,
)
from mathics.core.atoms import String
from mathics.core.exceptions import BoxConstructError
from mathics.core.formatter import add_conversion_fn, lookup_method
from mathics.core.symbols import Atom, SymbolTrue
from mathics.format.form.util import _WrongFormattedExpression, text_cells_to_grid


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


def interpretation_box(self, **options):
    return boxes_to_text(self.boxes, **options)


add_conversion_fn(InterpretationBox, interpretation_box)


def pane_box(self, **options):
    result = boxes_to_text(self.boxes, **options)
    return result


add_conversion_fn(PaneBox, pane_box)


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
        elements = self.items
    evaluation = box_options.get("evaluation", None)
    items, options = self.get_array(elements, evaluation)

    box_options.update(self.options)

    if not items:
        return ""

    cells = [
        (
            [
                # TODO: check if this evaluation is necessary.
                boxes_to_text(item, **box_options)
                for item in row
            ]
            if isinstance(row, tuple)
            else boxes_to_text(row, **box_options)
        )
        for row in items
    ]

    try:
        return text_cells_to_grid(cells)
    except _WrongFormattedExpression:
        raise BoxConstructError


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
    no_parenthesize = True
    index = self.superindex
    while not isinstance(index, Atom):
        if isinstance(index, StyleBox):
            index = index.boxes
        else:
            break
    if isinstance(index, FractionBox):
        no_parenthesize = False

    fmt_str = "%s^%s" if no_parenthesize else "%s^(%s)"
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
    parts_str = [boxes_to_text(element, **options) for element in self.items]
    if len(parts_str) == 0:
        return ""
    if len(parts_str) == 1:
        return parts_str[0]
    # This loop integrate all the row adding spaces after a ",", followed
    # by something which is not a comma. For example,
    # >> ToString[RowBox[{",",",","p"}]//DisplayForm]
    #  = ",, p"
    result = parts_str[0]
    comma = result == ","
    for elem in parts_str[1:]:
        if elem == ",":
            result += elem
            comma = True
            continue
        if comma:
            result += " "
            comma = False

        result += elem
    return result


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


def tag_and_form_box(self, **options):
    return boxes_to_text(self.boxes, **options)


add_conversion_fn(FormBox, tag_and_form_box)
add_conversion_fn(TagBox, tag_and_form_box)
