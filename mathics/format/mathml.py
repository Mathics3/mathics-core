# -*- coding: utf-8 -*-
"""
Lower-level formatter of Mathics objects as MathML strings.

MathML formatting is usually initiated in Mathics via MathMLForm[].
"""

import base64
import html

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
from mathics.core.element import BoxElementMixin
from mathics.core.exceptions import BoxConstructError
from mathics.core.formatter import (
    add_conversion_fn,
    lookup_method as lookup_conversion_method,
)
from mathics.core.parser import is_symbol_name
from mathics.core.symbols import SymbolTrue


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


def string(self, **options) -> str:
    from mathics.builtin import display_operators_set as operators

    text = self.value

    number_as_text = options.get("number_as_text", None)
    show_string_characters = (
        options.get("System`ShowStringCharacters", None) is SymbolTrue
    )
    if isinstance(self, BoxElementMixin):
        if number_as_text is None:
            number_as_text = options.get("number_as_text", False)

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
        text and not number_as_text and ("0" <= text[0] <= "9" or text[0] in (".", "-"))
    ):
        return render("<mn>%s</mn>", text)
    else:
        if text in operators or text in extra_operators:
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


def fractionbox(self, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    return "<mfrac>%s %s</mfrac>" % (
        lookup_conversion_method(self.num, "mathml")(self.num, **options),
        lookup_conversion_method(self.den, "mathml")(self.den, **options),
    )


add_conversion_fn(FractionBox, fractionbox)


def gridbox(self, elements=None, **box_options) -> str:
    def boxes_to_mathml(box, **options):
        return lookup_conversion_method(box, "mathml")(box, **options)

    if not elements:
        elements = self._elements
    evaluation = box_options.get("evaluation")
    items, options = self.get_array(elements, evaluation)
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
    new_box_options = box_options.copy()
    new_box_options["inside_list"] = True
    for row in items:
        result += "<mtr>"
        if isinstance(row, tuple):
            for item in row:
                result += f"<mtd {joined_attrs}>{boxes_to_mathml(item, **new_box_options)}</mtd>"
        else:
            result += f"<mtd {joined_attrs} columnspan={num_fields}>{boxes_to_mathml(row, **new_box_options)}</mtd>"
        result += "</mtr>\n"
    result += "</mtable>"
    # print(f"gridbox: {result}")
    return result


add_conversion_fn(GridBox, gridbox)


def sqrtbox(self, **options):
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    if self.index:
        return "<mroot> %s %s </mroot>" % (
            lookup_conversion_method(self.radicand, "mathml")(self.radicand, **options),
            lookup_conversion_method(self.index, "mathml")(self.index, **options),
        )

    return "<msqrt> %s </msqrt>" % lookup_conversion_method(self.radicand, "mathml")(
        self.radicand, **options
    )


add_conversion_fn(SqrtBox, sqrtbox)


def subscriptbox(self, **options):
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    return "<msub>%s %s</msub>" % (
        lookup_conversion_method(self.base, "mathml")(self.base, **options),
        lookup_conversion_method(self.subindex, "mathml")(self.subindex, **options),
    )


add_conversion_fn(SubscriptBox, subscriptbox)


def superscriptbox(self, **options):
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    return "<msup>%s %s</msup>" % (
        lookup_conversion_method(self.base, "mathml")(self.base, **options),
        lookup_conversion_method(self.superindex, "mathml")(self.superindex, **options),
    )


add_conversion_fn(SuperscriptBox, superscriptbox)


def subsuperscriptbox(self, **options):
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    options["inside_row"] = True
    return "<msubsup>%s %s %s</msubsup>" % (
        lookup_conversion_method(self.base, "mathml")(self.base, **options),
        lookup_conversion_method(self.subindex, "mathml")(self.subindex, **options),
        lookup_conversion_method(self.superindex, "mathml")(self.superindex, **options),
    )


add_conversion_fn(SubsuperscriptBox, subsuperscriptbox)


def rowbox(self, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    result = []
    inside_row = options.get("inside_row")
    # inside_list = options.get('inside_list')
    options = options.copy()

    def is_list_interior(content):
        if all(element.get_string_value() == "," for element in content[1::2]):
            return True
        return False

    is_list_row = False
    if (
        len(self.items) >= 3
        and self.items[0].get_string_value() == "{"
        and self.items[2].get_string_value() == "}"
        and self.items[1].has_form("RowBox", 1, None)
    ):
        content = self.items[1].items
        if is_list_interior(content):
            is_list_row = True

    if not inside_row and is_list_interior(self.items):
        is_list_row = True

    if is_list_row:
        options["inside_list"] = True
    else:
        options["inside_row"] = True

    for element in self.items:
        result.append(lookup_conversion_method(element, "mathml")(element, **options))

    # print(f"mrow: {result}")

    return "<mrow>%s</mrow>" % " ".join(result)


add_conversion_fn(RowBox, rowbox)


def stylebox(self, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    return lookup_conversion_method(self.boxes, "mathml")(self.boxes, **options)


add_conversion_fn(StyleBox, stylebox)


def graphicsbox(self, elements=None, **options) -> str:
    # FIXME: SVG is the only thing we can convert MathML into.
    # Handle other graphics formats.
    svg_body = self.boxes_to_svg(elements, **options)

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
        int(self.width),
        int(self.height),
        base64.b64encode(svg_body.encode("utf8")).decode("utf8"),
    )
    # print("boxes_to_mathml", mathml)
    return mathml


add_conversion_fn(GraphicsBox, graphicsbox)


def sqrtbox(self, **options):
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    if self.index:
        return "<mroot> %s %s </mroot>" % (
            lookup_conversion_method(self.radicand, "mathml")(self.radicand, **options),
            lookup_conversion_method(self.index, "mathml")(self.index, **options),
        )

    return "<msqrt> %s </msqrt>" % lookup_conversion_method(self.radicand, "mathml")(
        self.radicand, **options
    )


add_conversion_fn(SqrtBox, sqrtbox)


def graphics3dbox(self, elements=None, **options) -> str:
    """Turn the Graphics3DBox into a MathML string"""
    json_repr = self.boxes_to_json(elements, **options)
    mathml = f'<graphics3d data="{html.escape(json_repr)}" />'
    mathml = f"<mtable><mtr><mtd>{mathml}</mtd></mtr></mtable>"
    return mathml


add_conversion_fn(Graphics3DBox, graphics3dbox)
