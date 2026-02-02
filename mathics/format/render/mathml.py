# -*- coding: utf-8 -*-
"""
Lower-level formatter of Mathics3 into MathML strings.

MathML formatting is usually initiated in Mathics via MathMLForm[].

Following WMA MathML generated text, and for readability, MathML tags
containing sub-tags are split on several lines, one by
sub element, and indented according to nesting level. The
indentation step size is one space.

For example, the Box expression

>> FractionBox[RowBox[{"a", "+", SuperscriptBox["b", "c"]}], "d"]

produces
```
<mfrac>
 <mrow>
  <mi>a</mi>
  <mo>+</mo>
  <msup>
   <mi>b</mi>
   <mi>c</mi>
  </msup>
 </mrow>
 <mi>d</mi>
</mfrac>
```

"""

import base64
import html

from mathics_scanner.tokeniser import is_symbol_name

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


# "Operators" which are not in display_operators_set
extra_operators = {
    ",",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    # TODO: check why the following characters are not in `operators`:
    "\u301a",  # [[
    "\u301b",  # ]]
    "\u00d7",  # \[Times]
    "\u2032",  # \[RawComma]
    "\u2032\u2032",  # \[RawComma]\[RawComma]
    "\u2062",  # \[InvisibleTimes]
    "\u222b",  # \[Integral]
    "\u2146",  # \[DifferentialD]
}


# "s" is a String or What?
def string(s, **options) -> str:
    text = s.value

    number_as_text = options.get("number_as_text", None)
    show_string_characters = (
        options.get("System`ShowStringCharacters", None) is SymbolTrue
    )
    if isinstance(s, BoxElementMixin):
        if number_as_text is None:
            number_as_text = SymbolFalse

    if hasattr(s, "box_options"):
        indent_level = s.box_options.get("indent_level", 0)
    else:
        indent_level = options.get("_indent_level", 0)

    indent_spaces = " " * indent_level

    def render(format, s):
        encoded_text = encode_mathml(s)
        return indent_spaces + format % encoded_text

    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
        if not show_string_characters:
            return render("<mtext>%s</mtext>", text)
        return render("<ms>%s</ms>", text)
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
            if text == "\u2146":  # DifferentialD
                return render(
                    '<mo form="prefix" lspace="0.2em" rspace="0">%s</mo>', text
                )
            if text == "\u2062":  # InvisibleTimes
                return render(
                    '<mo form="prefix" lspace="0" rspace="0.2em">%s</mo>', text
                )
            return render("<mo>%s</mo>", text)
        elif is_symbol_name(text):
            return render("<mi>%s</mi>", text)
        else:
            return "".join(
                render("<mtext>%s</mtext>", line) for line in text.split("\n")
            )


add_conversion_fn(String, string)


def interpretation_box(box: InterpretationBox, **options):
    boxes = box.boxes
    origin = box.expr
    if origin.has_form("InputForm", None):
        # InputForm produce outputs of the form
        # InterpretationBox[Style[_String, ...], origin_InputForm, opts___]
        assert isinstance(boxes, StyleBox), f"boxes={boxes} are not a StyleBox"
        boxes = boxes.boxes
        options["System`ShowStringCharacters"] = SymbolTrue
        assert isinstance(boxes, String)
        # Remove the outer quotes
    elif origin.has_form("OutputForm", None):
        # OutputForm produce outputs of the form
        # InterpretationBox[PaneBox[_String, ...], origin_OutputForm, opts___]
        assert boxes.has_form("PaneBox", 1, None)
        boxes = boxes.boxes
        assert isinstance(boxes, String)
        # Remove the outer quotes
        boxes = String(boxes.value)

    return lookup_conversion_method(boxes, "mathml")(boxes, **options)


add_conversion_fn(InterpretationBox, interpretation_box)


def pane_box(box, **options):
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    options["_indent_level"] = indent_level + 1

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
        return f"{indent_spaces}<mstyle {dims}>\n{content}\n{indent_spaces}</mstyle>"
    return f"{indent_spaces}{content}"


add_conversion_fn(PaneBox, pane_box)


def fractionbox(box: FractionBox, **options) -> str:
    indent_level = box.box_options.get("_indent_level", options.get("_indent_level", 0))
    indent_spaces = " " * indent_level
    indent_level += 1
    has_nonbox_children = False

    for child_box in (box.num, box.den):
        if hasattr(child_box, "box_options"):
            child_box.box_options["_indent_level"] = indent_level
        else:
            has_nonbox_children = True

    if has_nonbox_children:
        # non_boxed children have to get indent_level information passed down
        # via a parameter. Here it is the "options" variable. (Which is a bad name).
        child_options = {**options, "_indent_level": indent_level}

    return f"{indent_spaces}<mfrac>\n%s\n%s\n{indent_spaces}</mfrac>" % (
        lookup_conversion_method(box.num, "mathml")(box.num, **child_options),
        lookup_conversion_method(box.den, "mathml")(box.den, **child_options),
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
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    result = f"{indent_spaces}<mtable {joined_attrs}>\n"
    new_box_options = box_options.copy()
    new_box_options["inside_list"] = True
    new_box_options["_indent_level"] = indent_level + 3

    for row in items:
        result += f"{indent_spaces} <mtr>"
        if isinstance(row, tuple):
            for item in row:
                new_box_options["_indent_level"] = indent_level + 4
                result += f"\n{indent_spaces}  <mtd {joined_attrs}>\n{boxes_to_mathml(item, **new_box_options)}\n{indent_spaces}  </mtd>"
        else:
            result += f"\n{indent_spaces}  <mtd {joined_attrs} columnspan={num_fields}>\n{boxes_to_mathml(row, **new_box_options)}\n{indent_spaces}  </mtd>"
        result += f"\n{indent_spaces} </mtr>\n"
    result += f"{indent_spaces}</mtable>"
    # print(f"gridbox: {result}")
    return result


add_conversion_fn(GridBox, gridbox)


def sqrtbox(box: SqrtBox, **options):
    _options = box.box_options.copy()
    _options.update(options)
    options = _options
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    options["_indent_level"] = indent_level + 1

    if box.index:
        return f"{indent_spaces}<mroot>\n%s\n%s\n{indent_spaces}</mroot>" % (
            lookup_conversion_method(box.radicand, "mathml")(box.radicand, **options),
            lookup_conversion_method(box.index, "mathml")(box.index, **options),
        )

    return (
        f"{indent_spaces}<msqrt>\n%s\n{indent_spaces}</msqrt>"
        % lookup_conversion_method(box.radicand, "mathml")(box.radicand, **options)
    )


add_conversion_fn(SqrtBox, sqrtbox)


def subscriptbox(box: SqrtBox, **options):
    _options = box.box_options.copy()
    _options.update(options)
    options = _options
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    options["_indent_level"] = indent_level + 1
    return f"{indent_spaces}<msub>\n%s\n%s\n{indent_spaces}</msub>" % (
        lookup_conversion_method(box.base, "mathml")(box.base, **options),
        lookup_conversion_method(box.subindex, "mathml")(box.subindex, **options),
    )


add_conversion_fn(SubscriptBox, subscriptbox)


def superscriptbox(box: SuperscriptBox, **options):
    _options = box.box_options.copy()
    _options.update(options)
    options = _options
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    options["_indent_level"] = indent_level + 1

    return f"{indent_spaces}<msup>\n%s\n%s\n{indent_spaces}</msup>" % (
        lookup_conversion_method(box.base, "mathml")(box.base, **options),
        lookup_conversion_method(box.superindex, "mathml")(box.superindex, **options),
    )


add_conversion_fn(SuperscriptBox, superscriptbox)


def subsuperscriptbox(box: SubscriptBox, **options):
    _options = box.box_options.copy()
    _options.update(options)
    options = _options
    options["inside_row"] = True

    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    options["_indent_level"] = indent_level + 1

    return f"{indent_spaces}<msubsup>\n%s\n%s\n%s\n{indent_spaces}</msubsup>" % (
        lookup_conversion_method(box.base, "mathml")(box.base, **options),
        lookup_conversion_method(box.subindex, "mathml")(box.subindex, **options),
        lookup_conversion_method(box.superindex, "mathml")(box.superindex, **options),
    )


add_conversion_fn(SubsuperscriptBox, subsuperscriptbox)


def rowbox(box: RowBox, **options) -> str:
    _options = box.box_options.copy()
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

    if is_list_row:
        options["inside_list"] = True
    else:
        options["inside_row"] = True

    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    options["_indent_level"] = indent_level + 1

    for element in box.items:
        # Propagate properties down to box children.
        # The below test could also be done via isinstance of of Box.
        result.append(lookup_conversion_method(element, "mathml")(element, **options))

    # print(f"mrow: {result}")
    return f"{indent_spaces}<mrow>\n%s\n{indent_spaces}</mrow>" % ("\n".join(result),)


add_conversion_fn(RowBox, rowbox)


def stylebox(box: StyleBox, **options) -> str:
    _options = box.box_options.copy()
    _options.update(options)
    options = _options
    return lookup_conversion_method(box.boxes, "mathml")(box.boxes, **options)


add_conversion_fn(StyleBox, stylebox)


def graphicsbox(box: GraphicsBox, elements=None, **options) -> str:
    # FIXME: SVG is the only thing we can convert MathML into.
    # Handle other graphics formats.
    svg_body = box.boxes_to_svg(elements, **options)

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
        int(box.width),
        int(box.height),
        base64.b64encode(svg_body.encode("utf8")).decode("utf8"),
    )
    indent_level = options.get("_indent_level", 0)
    if indent_level:
        mathml = " " * indent_level + mathml

    # print("boxes_to_mathml", mathml)
    return mathml


add_conversion_fn(GraphicsBox, graphicsbox)


def graphics3dbox(box: Graphics3DBox, elements=None, **options) -> str:
    """Turn the Graphics3DBox into a MathML string"""
    json_repr = box.boxes_to_json(elements, **options)
    mathml = f'<graphics3d data="{html.escape(json_repr)}" />'
    mathml = f"<mtable>\n<mtr>\n<mtd>\n{mathml}\n</mtd>\n</mtr>\n</mtable>"
    indent_level = options.get("_indent_level", 0)
    if indent_level:
        mathml = " " * indent_level + mathml
    return mathml


add_conversion_fn(Graphics3DBox, graphics3dbox)


def tag_and_form_box(box, **options):
    return lookup_conversion_method(box.boxes, "mathml")(box.boxes, **options)


add_conversion_fn(FormBox, tag_and_form_box)
add_conversion_fn(TagBox, tag_and_form_box)
