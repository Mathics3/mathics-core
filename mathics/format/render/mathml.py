# -*- coding: utf-8 -*-
"""
Mathics3 Box rendering to MathML strings.

MathML formatting is usually initiated in Mathics via MathMLForm[].

For readability, and following WMA MathML generated code,  tags \
containing sub-tags are split on several lines, one by
sub element, and indented according to the level of the part. \
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
from mathics.core.convert.op import named_characters, operator_to_unicode
from mathics.core.element import BoxElementMixin
from mathics.core.exceptions import BoxConstructError
from mathics.core.formatter import (
    add_conversion_fn,
    convert_box_to_format,
    convert_inner_box_field,
)
from mathics.core.load_builtin import display_operators_set as operators
from mathics.core.symbols import SymbolFalse, SymbolTrue
from mathics.core.systemsymbols import SymbolAutomatic


def convert_inner_box(box, **options):
    return convert_inner_box_field(box, "inner_box", **options)


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
    named_characters["LeftDoubleBracket"],
    named_characters["RightDoubleBracket"],
    operator_to_unicode["Times"],
    named_characters["Prime"],
    named_characters["Prime"] * 2,
    " ",
    named_characters["InvisibleTimes"],
    named_characters["Integral"],
    named_characters["DifferentialD"],
}


add_conversion_fn(FormBox, convert_inner_box)


def fractionbox(box: FractionBox, **options) -> str:
    # Note: values set in `options` take precedence over `box_options`
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    child_options = {**options, **box.box_options}
    child_options["_indent_level"] = indent_level + 1
    num_text = convert_box_to_format(box.num, **child_options)
    den_text = convert_box_to_format(box.den, **child_options)
    return f"{indent_spaces}<mfrac>\n%s\n%s\n{indent_spaces}</mfrac>" % (
        num_text,
        den_text,
    )


add_conversion_fn(FractionBox, fractionbox)


def graphics3dbox(box: Graphics3DBox, elements=None, **options) -> str:
    """Turn the Graphics3DBox into a MathML string"""
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    result = box.box_to_js(**options)
    result = (
        f"{indent_spaces}<mtable>\n"
        f"<mtr>\n"
        f"{indent_spaces} <mtd>\n"
        f"{indent_spaces}  {result}\n"
        f"{indent_spaces} </mtd>\n</mtr>\n"
        f"{indent_spaces}</mtable>"
    )
    return result


add_conversion_fn(Graphics3DBox, graphics3dbox)


def graphicsbox(box: GraphicsBox, elements=None, **options) -> str:
    # FIXME: SVG is the only thing we can convert MathML into.
    # Handle other graphics formats.
    svg_body = box.box_to_format("svg", **options)

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
    indent_level = options.get("_indent_level", 0)
    if indent_level:
        mathml = " " * indent_level + mathml
    # print("box_to_mathml", mathml)
    return mathml


add_conversion_fn(GraphicsBox, graphicsbox)


def gridbox(box: GridBox, elements=None, **super_options) -> str:
    if not elements:
        elements = box._elements
    evaluation = super_options.get("evaluation")
    items, box_options = box.get_array(elements, evaluation)
    num_fields = max(len(item) if isinstance(item, tuple) else 1 for item in items)

    attrs = {}
    column_alignments = box_options["System`ColumnAlignments"].get_name()
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
    indent_level = super_options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    child_options = {**super_options, **box_options}
    child_options["_indent_level"] = indent_level + 3
    result = f"{indent_spaces}<mtable {joined_attrs}>\n"

    for row in items:
        result += f"{indent_spaces} <mtr>"
        if isinstance(row, tuple):
            for item in row:
                item.inside_list = True
                result += (
                    f"\n{indent_spaces}  <mtd {joined_attrs}>\n%s\n{indent_spaces}  </mtd>"
                    % convert_box_to_format(item, **child_options)
                )
        else:
            row.inside_list = True
            result += (
                f"\n{indent_spaces}  <mtd {joined_attrs} columnspan={num_fields}>\n%s\n{indent_spaces}  </mtd>"
                % convert_box_to_format(row, **child_options)
            )
        result += f"\n{indent_spaces} </mtr>\n"
    result += f"{indent_spaces}</mtable>"
    # print(f"gridbox: {result}")
    return result


add_conversion_fn(GridBox, gridbox)


def interpretation_box(box: InterpretationBox, **options):
    origin = box.expr
    child_options = {**options, **box.box_options}
    box = box.inner_box
    if origin.has_form("InputForm", None):
        # InputForm produce outputs of the form
        # InterpretationBox[Style[_String, ...], origin_InputForm, opts___]
        assert isinstance(box, StyleBox), f"box={box} are not a StyleBox"
        box = box.inner_box
        child_options["System`ShowStringCharacters"] = SymbolTrue
        assert isinstance(box, String)
    elif origin.has_form("OutputForm", None):
        # OutputForm produce outputs of the form
        # InterpretationBox[PaneBox[_String, ...], origin_OutputForm, opts___]
        assert box.has_form("PaneBox", 1, None)
        box = box.inner_box
        assert isinstance(box, String)
        # Remove the outer quotes
        box = String(box.value)

    return convert_box_to_format(box, **child_options)


add_conversion_fn(InterpretationBox, interpretation_box)


def pane_box(box: PaneBox, **options):
    """render a PaneBox into mathml code"""
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    child_options = {**options, **box.box_options}
    child_options["_indent_level"] = indent_level + 1

    content = convert_inner_box_field(box, **child_options)
    size = child_options.get("System`ImageSize", SymbolAutomatic).to_python()
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


def rowbox(box: RowBox, **options) -> str:
    # Note: values set in `options` take precedence over `box_options`
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level

    child_options = {**box.box_options, **options}
    child_options["_indent_level"] = indent_level + 1
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
        result.append(convert_box_to_format(element, **child_options))

    # print(f"mrow: {result}")
    return f"{indent_spaces}<mrow>\n%s\n{indent_spaces}</mrow>" % ("\n".join(result),)


add_conversion_fn(RowBox, rowbox)


def sqrtbox(box: SqrtBox, **options):
    # Note: values set in `options` take precedence over `box_options`
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    child_options = {**options, **box.box_options}
    child_options["_indent_level"] = indent_level + 1
    if box.index:
        return f"{indent_spaces}<mroot>\n%s\n%s\n{indent_spaces}</mroot>" % (
            convert_inner_box_field(box, "radicand", **child_options),
            convert_inner_box_field(box, "index", **child_options),
        )
    return (
        f"{indent_spaces}<msqrt>\n%s\n{indent_spaces}</msqrt>"
        % convert_inner_box_field(box, "radicand", **child_options)
    )


add_conversion_fn(SqrtBox, sqrtbox)


def string(s: String, **options) -> str:
    text = s.value

    number_as_text = options.get("number_as_text", None)
    show_string_characters = (
        options.get("System`ShowStringCharacters", None) is SymbolTrue
    )
    if isinstance(s, BoxElementMixin):
        if number_as_text is None:
            number_as_text = SymbolFalse

    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level

    def render(format, string):
        encoded_text = encode_mathml(string)
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


def subscriptbox(box: SubscriptBox, **options):
    # Note: values set in `options` take precedence over `box_options`
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    child_options = {**options, **box.box_options}
    child_options["_indent_level"] = indent_level + 1
    return f"{indent_spaces}<msub>\n%s\n%s\n{indent_spaces}</msub>" % (
        convert_inner_box_field(box, "base", **child_options),
        convert_inner_box_field(box, "subindex", **child_options),
    )


add_conversion_fn(SubscriptBox, subscriptbox)


def subsuperscriptbox(box: SubsuperscriptBox, **options):
    # Note: values set in `options` take precedence over `box_options`
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    child_options = {**options, **box.box_options}
    child_options["_indent_level"] = indent_level + 1
    box.base.inside_row = box.subindex.inside_row = box.superindex.inside_row = True
    return f"{indent_spaces}<msubsup>\n%s\n%s\n%s\n{indent_spaces}</msubsup>" % (
        convert_inner_box_field(box, "base", **child_options),
        convert_inner_box_field(box, "subindex", **child_options),
        convert_inner_box_field(box, "superindex", **child_options),
    )


add_conversion_fn(SubsuperscriptBox, subsuperscriptbox)


def superscriptbox(box: SuperscriptBox, **options):
    # Note: values set in `options` take precedence over `box_options`
    indent_level = options.get("_indent_level", 0)
    indent_spaces = " " * indent_level
    child_options = {**options, **box.box_options}
    child_options["_indent_level"] = indent_level + 1
    return f"{indent_spaces}<msup>\n%s\n%s\n{indent_spaces}</msup>" % (
        convert_inner_box_field(box, "base", **child_options),
        convert_inner_box_field(box, "superindex", **child_options),
    )


add_conversion_fn(SuperscriptBox, superscriptbox)
add_conversion_fn(StyleBox, convert_inner_box)
add_conversion_fn(TagBox, convert_inner_box)
