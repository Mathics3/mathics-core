# -*- coding: utf-8 -*-
"""
Mathics3 box rendering to plain text.
"""

from mathics.builtin.box.expression import BoxExpression
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
from mathics.core.formatter import add_conversion_fn, convert_box_to_format
from mathics.core.symbols import Atom, SymbolTrue
from mathics.format.box.graphics import prepare_elements as prepare_elements2d
from mathics.format.box.graphics3d import prepare_elements as prepare_elements3d
from mathics.format.form.util import _WrongFormattedExpression, text_cells_to_grid


def string(s: String, **options) -> str:
    value = s.value
    show_string_characters = (
        options.get("System`ShowStringCharacters", None) is SymbolTrue
    )
    if value.startswith('"') and value.endswith('"'):  # nopep8
        if not show_string_characters:
            value = value[1:-1]
    return value


add_conversion_fn(String, string)


def interpretation_box(box: InterpretationBox, **options):
    return convert_box_to_format(box.inner_box, **options)


add_conversion_fn(InterpretationBox, interpretation_box)


def pane_box(box: PaneBox, **options):
    return convert_box_to_format(box.inner_box, **options)


add_conversion_fn(PaneBox, pane_box)


def fractionbox(box: FractionBox, **options) -> str:
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**options, **box.box_options}
    num_text = convert_box_to_format(box.num, **child_options)
    den_text = convert_box_to_format(box.den, **child_options)
    if isinstance(box.num, RowBox):
        num_text = f"({num_text})"
    if isinstance(box.den, RowBox):
        den_text = f"({den_text})"

    return " / ".join([num_text, den_text])


add_conversion_fn(FractionBox, fractionbox)


def gridbox(box: GridBox, elements=None, **box_options) -> str:
    if not elements:
        elements = box.items
    evaluation = box_options.get("evaluation", None)
    items, options = box.get_array(elements, evaluation)

    box_options.update(box.options)

    if not items:
        return ""

    cells = [
        (
            [
                # TODO: check if this evaluation is necessary.
                convert_box_to_format(item, **box_options)
                for item in row
            ]
            if isinstance(row, tuple)
            else convert_box_to_format(row, **box_options)
        )
        for row in items
    ]

    try:
        return text_cells_to_grid(cells)
    except _WrongFormattedExpression:
        raise BoxConstructError


add_conversion_fn(GridBox, gridbox)


def sqrtbox(box: SqrtBox, **options) -> str:
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**options, **box.box_options}
    if box.index:
        return "Sqrt[%s,%s]" % (
            convert_box_to_format(box.radicand, **child_options),
            convert_box_to_format(box.index, **child_options),
        )
    return "Sqrt[%s]" % (convert_box_to_format(box.radicand, **child_options))


add_conversion_fn(SqrtBox, sqrtbox)


def superscriptbox(box: SuperscriptBox, **options) -> str:
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**options, **box.box_options}
    no_parenthesize = True
    index = box.superindex
    while not isinstance(index, Atom):
        if isinstance(index, StyleBox):
            index = index.inner_box
        else:
            break
    if isinstance(index, FractionBox):
        no_parenthesize = False

    fmt_str = "%s^%s" if no_parenthesize else "%s^(%s)"
    return fmt_str % (
        convert_box_to_format(box.base, **child_options),
        convert_box_to_format(box.superindex, **child_options),
    )


add_conversion_fn(SuperscriptBox, superscriptbox)


def subscriptbox(box: SubscriptBox, **options) -> str:
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**box.box_options, **options}
    return "Subscript[%s, %s]" % (
        convert_box_to_format(box.base, **child_options),
        convert_box_to_format(box.subindex, **child_options),
    )


add_conversion_fn(SubscriptBox, subscriptbox)


def subsuperscriptbox(box: SubsuperscriptBox, **options) -> str:
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**box.box_options, **options}
    return "Subsuperscript[%s, %s, %s]" % (
        convert_box_to_format(box.base, **child_options),
        convert_box_to_format(box.subindex, **child_options),
        convert_box_to_format(box.superindex, **child_options),
    )


add_conversion_fn(SubsuperscriptBox, subsuperscriptbox)


def rowbox(box: RowBox, elements=None, **options) -> str:
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**box.box_options, **options}
    parts_str = [
        convert_box_to_format(element, **child_options) for element in box.items
    ]
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


def stylebox(box: StyleBox, **options) -> str:
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**box.box_options, **options}
    return convert_box_to_format(box.inner_box, **child_options)


add_conversion_fn(StyleBox, stylebox)


def graphicsbox(box: GraphicsBox, elements=None, **options) -> str:
    assert elements is None

    prepare_elements2d(box, box.content, options)  # to test for Box errors
    return "-Graphics-"


add_conversion_fn(GraphicsBox, graphicsbox)


def graphics3dbox(box: Graphics3DBox, elements=None, **options) -> str:
    assert elements is None

    prepare_elements3d(box, box.content, options)  # to test for Box errors
    return "-Graphics3D-"


add_conversion_fn(Graphics3DBox, graphics3dbox)


def tag_and_form_box(box: BoxExpression, **options):
    return convert_box_to_format(box.inner_box, **options)


add_conversion_fn(FormBox, tag_and_form_box)
add_conversion_fn(TagBox, tag_and_form_box)
