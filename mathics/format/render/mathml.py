# -*- coding: utf-8 -*-
"""
Mathics3 Graphics3D box rendering to MathML strings.

MathML rendering is usually initiated via MathMLForm[].
"""

import base64

from mathics_scanner.tokeniser import is_symbol_name

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
from mathics.core.element import BoxElementMixin
from mathics.core.exceptions import BoxConstructError
from mathics.core.formatter import (
    add_conversion_fn,
    lookup_method as lookup_conversion_method,
)
from mathics.core.load_builtin import display_operators_set as operators
from mathics.core.symbols import SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolAutomatic


def encode_mathml(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace('"', "&quot;").replace(" ", "&nbsp;")
    text = text.replace("\n", '<mspace linebreak="newline" />')
    return text


extra_operators = {
    ",",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    "\u301a",
    "\u301b",
    "\u00d7",
    "\u2032",
    "\u2032\u2032",
    " ",
    "\u2062",
    "\u222b",
    "\u2146",
}


def string(s: String, **options) -> str:
    text = s.value

    number_as_text = options.get("number_as_text", None)
    show_string_characters = (
        options.get("System`ShowStringCharacters", None) is SymbolTrue
    )
    if isinstance(s, BoxElementMixin):
        if number_as_text is None:
            number_as_text = SymbolFalse

    def render(format, string):
        encoded_text = encode_mathml(string)
        return format % encoded_text

    if text.startswith('"') and text.endswith('"'):
        if show_string_characters:
            return render("<ms>%s</ms>", text[1:-1])
        else:
            outtext = ""
            for line in text[1:-1].split("\n"):
                outtext += render("<mtext>%s</mtext>", line)
            return outtext
    elif (
        text
        and (number_as_text is SymbolFalse)
        and ("0" <= text[0] <= "9" or text[0] in (".", "-"))
    ):
        text = text.split("`")[0]
        return render("<mn>%s</mn>", text)
    else:
        if text in operators or text in extra_operators:
            # Empty strings are taken as an operator character,
            # but this confuses the MathML interpreter in
            # Mathics-Django:
            if text == "":
                return ""
            if text == "\u2146":
                return render(
                    '<mo form="prefix" lspace="0.2em" rspace="0">%s</mo>', text
                )
            if text == "\u2062":
                return render(
                    '<mo form="prefix" lspace="0" rspace="0.2em">%s</mo>', text
                )
            return render("<mo>%s</mo>", text)
        elif is_symbol_name(text):
            return render("<mi>%s</mi>", text)
        else:
            outtext = ""
            for line in text.split("\n"):
                outtext += render("<mtext>%s</mtext>", line)
            return outtext


add_conversion_fn(String, string)


def interpretation_box(box: InterpretationBox, **options):
    return lookup_conversion_method(box.boxes, "mathml")(box.boxes, **options)


add_conversion_fn(InterpretationBox, interpretation_box)


def pane_box(box: PaneBox, **options):
    content = lookup_conversion_method(box.boxes, "mathml")(box.boxes, **options)
    options = box.box_options
    size = options.get("System`ImageSize", SymbolAutomatic).to_python()
    if size is SymbolAutomatic:
        width = ""
        height = ""
    elif isinstance(size, int):
        width = f"{size}px"
        height = ""
    elif isinstance(size, tuple) and len(size) == 2:
        width_val, height_val = size[0], size[1]
        if isinstance(width_val, int):
            width = f"{width_val}px"
        else:
            width = ""
        if isinstance(height_val, int):
            height = f"{height_val}px"
        else:
            height = ""
    else:
        width = ""
        height = ""

    dims = f"width:{width};" if width else ""
    if height:
        dims += f"height:{height};"
    if dims:
        dims += "overflow:hidden;"
        dims = f' style="{dims}" '
    if dims:
        return f"<mstyle {dims}>\n{content}\n</mstyle>"
    return content


add_conversion_fn(PaneBox, pane_box)


def fractionbox(box: FractionBox, **options) -> str:
    return "<mfrac>%s %s</mfrac>" % (
        lookup_conversion_method(box.num, "mathml")(box.num, **options),
        lookup_conversion_method(box.den, "mathml")(box.den, **options),
    )


add_conversion_fn(FractionBox, fractionbox)


def gridbox(box: GridBox, elements=None, **box_options) -> str:
    def boxes_to_mathml(box, **options):
        return lookup_conversion_method(box, "mathml")(box, **options)

    if not elements:
        elements = box._elements
    evaluation = box_options.get("evaluation")
    items, options = box.get_array(elements, evaluation)
    num_fields = max(len(item) if isinstance(item, tuple) else 1 for item in items)

    attrs = {}
    column_alignments = options["System`ColumnAlignments"].get_name()
    try:
        attrs["columnalign"] = {
            "System`Center": "center",
            "System`Left": "left",
            "System`Right": "right",
        }[column_alignments]
    except KeyError:
        # invalid column alignment
        raise BoxConstructError
    joined_attrs = " ".join(f'{name}="{value}"' for name, value in attrs.items())
    result = f"<mtable {joined_attrs}>\n"
    for row in items:
        result += "<mtr>"
        if isinstance(row, tuple):
            for item in row:
                item.inside_list = True
                result += (
                    f"<mtd {joined_attrs}>{boxes_to_mathml(item, **options)}</mtd>"
                )
        else:
            row.inside_list = True
            result += f"<mtd {joined_attrs} columnspan={num_fields}>{boxes_to_mathml(row, **options)}</mtd>"
        result += "</mtr>\n"
    result += "</mtable>"
    # print(f"gridbox: {result}")
    return result


add_conversion_fn(GridBox, gridbox)


def sqrtbox(box: SqrtBox, **options):
    if box.index:
        return "<mroot> %s %s </mroot>" % (
            lookup_conversion_method(box.radicand, "mathml")(box.radicand, **options),
            lookup_conversion_method(box.index, "mathml")(box.index, **options),
        )

    return "<msqrt> %s </msqrt>" % lookup_conversion_method(box.radicand, "mathml")(
        box.radicand, **options
    )


add_conversion_fn(SqrtBox, sqrtbox)


def subscriptbox(box: SubscriptBox, **options):
    return "<msub>%s %s</msub>" % (
        lookup_conversion_method(box.base, "mathml")(box.base, **options),
        lookup_conversion_method(box.subindex, "mathml")(box.subindex, **options),
    )


add_conversion_fn(SubscriptBox, subscriptbox)


def superscriptbox(box: SuperscriptBox, **options):
    return "<msup>%s %s</msup>" % (
        lookup_conversion_method(box.base, "mathml")(box.base, **options),
        lookup_conversion_method(box.superindex, "mathml")(box.superindex, **options),
    )


add_conversion_fn(SuperscriptBox, superscriptbox)


def subsuperscriptbox(box: SubsuperscriptBox, **options):
    box.base.inside_row = box.subindex.inside_row = box.superindex.inside_row = True
    return "<msubsup>%s %s %s</msubsup>" % (
        lookup_conversion_method(box.base, "mathml")(box.base, **options),
        lookup_conversion_method(box.subindex, "mathml")(box.subindex, **options),
        lookup_conversion_method(box.superindex, "mathml")(box.superindex, **options),
    )


add_conversion_fn(SubsuperscriptBox, subsuperscriptbox)


def rowbox(box: RowBox, **options) -> str:
    result = []
    inside_row = box.inside_row

    def is_list_interior(content):
        if all(element.get_string_value() == "," for element in content[1::2]):
            return True
        return False

    is_list_row = False
    if (
        len(box.items) >= 3
        and box.items[0].get_string_value() == "{"
        and box.items[2].get_string_value() == "}"
        and box.items[1].has_form("RowBox", 1, None)
    ):
        content = box.items[1].items
        if is_list_interior(content):
            is_list_row = True

    if not inside_row and is_list_interior(box.items):
        is_list_row = True

    nest_field = "inside_list" if is_list_row else "inside_row"

    for element in box.items:
        if hasattr(element, nest_field):
            setattr(element, nest_field, True)
        result.append(lookup_conversion_method(element, "mathml")(element, **options))

    # print(f"mrow: {result}")

    return "<mrow>%s</mrow>" % " ".join(result)


add_conversion_fn(RowBox, rowbox)


def stylebox(box: StyleBox, **options) -> str:
    return lookup_conversion_method(box.boxes, "mathml")(box.boxes, **options)


add_conversion_fn(StyleBox, stylebox)


def graphicsbox(box: GraphicsBox, elements=None, **options) -> str:
    # FIXME: SVG is the only thing we can convert MathML into.
    # Handle other graphics formats.
    svg_body = box.boxes_to_format("svg", **options)

    # mglyph, which is what we have been using, is bad because MathML standard changed.
    # metext does not work because the way in which we produce the svg images is also based on this outdated mglyph
    # behaviour.
    # template = '<mtext width="%dpx" height="%dpx"><img width="%dpx" height="%dpx" src="data:image/svg+xml;base64,%s"/></mtext>'
    template = (
        '<mglyph width="%dpx" height="%dpx" src="data:image/svg+xml;base64,%s"/>'
        # '<mglyph  src="data:image/svg+xml;base64,%s"/>'
    )
    # print(svg_body)
    mathml = template % (
        int(box.boxwidth),
        int(box.boxheight),
        base64.b64encode(svg_body.encode("utf8")).decode("utf8"),
    )
    # print("boxes_to_mathml", mathml)
    return mathml


add_conversion_fn(GraphicsBox, graphicsbox)


def graphics3dbox(box, elements=None, **options) -> str:
    """Turn the Graphics3DBox into a MathML string"""
    result = box.boxes_to_js(**options)
    result = f"<mtable><mtr><mtd>{result}</mtd></mtr></mtable>"
    return result


add_conversion_fn(Graphics3DBox, graphics3dbox)


def tag_and_form_box(box: BoxExpression, **options):
    return lookup_conversion_method(box.boxes, "mathml")(box.boxes, **options)


add_conversion_fn(FormBox, tag_and_form_box)
add_conversion_fn(TagBox, tag_and_form_box)
