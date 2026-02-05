# -*- coding: utf-8 -*-
"""
Mathics3 box rendering to (AMS)LaTeX strings.

Formatting is usually initiated in Mathics via TeXForm[].

AMS LaTeX is LaTeX with addition mathematical symbols, which
we may make use of via the mathics-scanner tables.

TeXForm in WMA is slightly vague or misleading since the output is
typically LaTeX rather than Plain TeX. In Mathics3, we also assume AMS
LaTeX or more specifically that we the additional AMS Mathematical
Symbols exist.
"""

import re

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
from mathics.builtin.colors.color_directives import RGBColor
from mathics.core.atoms import String
from mathics.core.convert.op import (
    AMSTEX_OPERATORS,
    UNICODE_TO_AMSLATEX,
    UNICODE_TO_LATEX,
    get_latex_operator,
    named_characters,
)
from mathics.core.exceptions import BoxConstructError
from mathics.core.formatter import (
    add_conversion_fn,
    convert_box_to_format,
    convert_inner_box_field,
    lookup_method as lookup_conversion_method,
)
from mathics.core.symbols import SymbolTrue
from mathics.core.systemsymbols import SymbolAutomatic
from mathics.format.box.graphics import prepare_elements as prepare_elements2d
from mathics.format.box.graphics3d import (
    get_boundbox_lines as get_boundbox_lines3D,
    prepare_elements as prepare_elements3d,
)
from mathics.format.render.asy_fns import asy_color, asy_create_pens, asy_number

# mathics_scanner does not generates this table in a way that we can load it here.
# When it get fixed, we can use that table instead of this one:

BRACKET_INFO = {
    (
        String("("),
        String(")"),
    ): {
        "latex_open": "(",
        "latex_closing": ")",
        "latex_open_large": r"\left(",
        "latex_closing_large": r"\right)",
    },
    (
        String("{"),
        String("}"),
    ): {
        "latex_open": r"\{",
        "latex_closing": r"\}",
        "latex_open_large": r"\left\{",
        "latex_closing_large": r"\right\}",
    },
    (
        String("["),
        String("]"),
    ): {
        "latex_open": "[",
        "latex_closing": "]",
        "latex_open_large": r"\left[",
        "latex_closing_large": r"\right]",
    },
    (
        String(named_characters["LeftDoubleBracket"]),
        String(named_characters["RightDoubleBracket"]),
    ): {
        "latex_open": r"[[",
        "latex_closing": "]]",
        "latex_open_large": r"\left[\left[",
        "latex_closing_large": r"\right]\right]",
    },
    (
        String(named_characters["LeftAngleBracket"]),
        String(named_characters["RightAngleBracket"]),
    ): {
        "latex_open": "\\langle",
        "latex_closing": "\\rangle",
        "latex_open_large": r"\left\langle ",
        "latex_closing_large": r"\right\rangle ",
    },
    (
        String(named_characters["LeftDoubleBracketingBar"]),
        String(named_characters["RightDoubleBracketingBar"]),
    ): {
        "latex_open": r"\|",
        "latex_closing": r"\|",
        "latex_open_large": r"\left\|",
        "latex_closing_large": r"\right\| ",
    },
    (
        String("<|"),
        String("|>"),
    ): {
        "latex_open": r"\langle\vert ",
        "latex_closing": r"\vert\rangle ",
        "latex_open_large": r"\left\langle\left\vert ",
        "latex_closing_large": r"\right\vert\right\rangle ",
    },
}

TEX_REPLACE = {
    "{": r"\{",
    "}": r"\}",
    "_": r"\_",
    "$": r"\$",
    "%": r"\%",
    "#": r"\#",
    "&": r"\&",
    "\\": r"\backslash{}",
    "^": r"{}^{\wedge}",
    "~": r"\sim{}",
    "|": r"\vert{}",
    # These two are trivial replaces,
    # but are needed to define the regular expression
    "<": "<",
    ">": ">",
}
TEX_TEXT_REPLACE = {
    "$": r"\$",
    "&": r"$\&$",
    "#": r"$\#$",
    "%": r"$\%$",
    r"{": r"\{",
    r"}": r"\}",
    r"_": r"\_",
    "<": r"$<$",
    ">": r"$>$",
    "~": r"$\sim$",
    "|": r"$\vert$",
    "\\": r"$\backslash$",
    "^": r"${}^{\wedge}$",
}

TEX_REPLACE.update(UNICODE_TO_AMSLATEX)
TEX_REPLACE.update(
    {
        key: r"\text{" + val + "}"
        for key, val in UNICODE_TO_LATEX.items()
        if key not in TEX_REPLACE
    }
)

TEX_TEXT_REPLACE.update(UNICODE_TO_LATEX)
TEX_TEXT_REPLACE.update(
    {
        key: f"${val}$"
        for key, val in UNICODE_TO_AMSLATEX.items()
        if key not in TEX_TEXT_REPLACE
    }
)


TEX_REPLACE_RE = re.compile("([" + "".join([re.escape(c) for c in TEX_REPLACE]) + "])")


def convert_inner_box(box, **options):
    return convert_inner_box_field(box, "inner_box", **options)


def encode_tex(text: str, in_text=False) -> str:
    def replace(match):
        c = match.group(1)
        repl = TEX_TEXT_REPLACE if in_text else TEX_REPLACE
        # return TEX_REPLACE[c]
        return repl.get(c, c)

    text = TEX_REPLACE_RE.sub(replace, text)
    text = text.replace("\n", "\\newline\n")
    return text


add_conversion_fn(FormBox, convert_inner_box)


def fractionbox(box: FractionBox, **options) -> str:
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**options, **box.box_options}
    num_text = convert_box_to_format(box.num, **child_options)
    den_text = convert_box_to_format(box.den, **child_options)
    return "\\frac{%s}{%s}" % (num_text, den_text)


add_conversion_fn(FractionBox, fractionbox)


def graphics3dbox(box: Graphics3DBox, elements=None, **options) -> str:
    assert elements is None
    elements = box.content

    (
        elements,
        axes,
        ticks,
        ticks_style,
        calc_dimensions,
        boxscale,
    ) = prepare_elements3d(box, elements, options, max_width=450)

    elements._apply_boxscaling(boxscale)

    format_fn = lookup_conversion_method(elements, "asy")
    if format_fn is not None:
        asy = format_fn(elements)
    else:
        asy = elements.to_asy()

    xmin, xmax, ymin, ymax, zmin, zmax, boxscale, w, h = calc_dimensions()

    # TODO: Intelligently place the axes on the longest non-middle edge.
    # See algorithm used by web graphics in mathics/web/media/graphics.js
    # for details of this. (Projection to screen etc).

    # Choose axes placement (boundbox edge vertices)
    axes_indices = []
    if axes[0]:
        axes_indices.append(0)
    if axes[1]:
        axes_indices.append(6)
    if axes[2]:
        axes_indices.append(8)

    # Draw boundbox and axes
    boundbox_asy = ""
    boundbox_lines = get_boundbox_lines3D(box, xmin, xmax, ymin, ymax, zmin, zmax)

    for i, line in enumerate(boundbox_lines):
        if i in axes_indices:
            pen = asy_create_pens(
                edge_color=RGBColor(components=(0, 0, 0, 1)), stroke_width=1.5
            )
        else:
            pen = asy_create_pens(
                edge_color=RGBColor(components=(0.4, 0.4, 0.4, 1)), stroke_width=1
            )

        path = "--".join(["(%.5g,%.5g,%.5g)" % coords for coords in line])
        boundbox_asy += "draw((%s), %s);\n" % (path, pen)

    # TODO: Intelligently draw the axis ticks such that they are always
    # directed inward and choose the coordinate direction which makes the
    # ticks the longest. Again, details in mathics/web/media/graphics.js

    # Draw axes ticks
    ticklength = 0.05 * max([xmax - xmin, ymax - ymin, zmax - zmin])
    pen = asy_create_pens(
        edge_color=RGBColor(components=(0, 0, 0, 1)), stroke_width=1.2
    )
    for xi in axes_indices:
        if xi < 4:  # x axis
            for i, tick in enumerate(ticks[0][0]):
                line = [
                    (tick, boundbox_lines[xi][0][1], boundbox_lines[xi][0][2]),
                    (
                        tick,
                        boundbox_lines[xi][0][1],
                        boundbox_lines[xi][0][2] + ticklength,
                    ),
                ]

                path = "--".join(["({0},{1},{2})".format(*coords) for coords in line])

                boundbox_asy += "draw(({0}), {1});\n".format(path, pen)
                boundbox_asy += 'label("{0}",{1},{2});\n'.format(
                    ticks[0][2][i],
                    (tick, boundbox_lines[xi][0][1], boundbox_lines[xi][0][2]),
                    "S",
                )

            for small_tick in ticks[0][1]:
                line = [
                    (
                        small_tick,
                        boundbox_lines[xi][0][1],
                        boundbox_lines[xi][0][2],
                    ),
                    (
                        small_tick,
                        boundbox_lines[xi][0][1],
                        boundbox_lines[xi][0][2] + 0.5 * ticklength,
                    ),
                ]

                path = "--".join(["({0},{1},{2})".format(*coords) for coords in line])

                boundbox_asy += "draw(({0}), {1});\n".format(path, pen)

        if 4 <= xi < 8:  # y axis
            for i, tick in enumerate(ticks[1][0]):
                line = [
                    (boundbox_lines[xi][0][0], tick, boundbox_lines[xi][0][2]),
                    (
                        boundbox_lines[xi][0][0],
                        tick,
                        boundbox_lines[xi][0][2] - ticklength,
                    ),
                ]
                path = "--".join(["({0},{1},{2})".format(*coords) for coords in line])

                boundbox_asy += "draw(({0}), {1});\n".format(path, pen)

                boundbox_asy += 'label("{0}",{1},{2});\n'.format(
                    ticks[1][2][i],
                    (boundbox_lines[xi][0][0], tick, boundbox_lines[xi][0][2]),
                    "NW",
                )

            for small_tick in ticks[1][1]:
                line = [
                    (
                        boundbox_lines[xi][0][0],
                        small_tick,
                        boundbox_lines[xi][0][2],
                    ),
                    (
                        boundbox_lines[xi][0][0],
                        small_tick,
                        boundbox_lines[xi][0][2] - 0.5 * ticklength,
                    ),
                ]
                path = "--".join(["({0},{1},{2})".format(*coords) for coords in line])
                boundbox_asy += "draw(({0}), {1});\n".format(path, pen)
        if 8 <= xi:  # z axis
            for i, tick in enumerate(ticks[2][0]):
                line = [
                    (boundbox_lines[xi][0][0], boundbox_lines[xi][0][1], tick),
                    (
                        boundbox_lines[xi][0][0],
                        boundbox_lines[xi][0][1] + ticklength,
                        tick,
                    ),
                ]
                path = "--".join(["({0},{1},{2})".format(*coords) for coords in line])
                boundbox_asy += "draw(({0}), {1});\n".format(path, pen)
                boundbox_asy += 'label("{0}",{1},{2});\n'.format(
                    ticks[2][2][i],
                    (boundbox_lines[xi][0][0], boundbox_lines[xi][0][1], tick),
                    "W",
                )
            for small_tick in ticks[2][1]:
                line = [
                    (
                        boundbox_lines[xi][0][0],
                        boundbox_lines[xi][0][1],
                        small_tick,
                    ),
                    (
                        boundbox_lines[xi][0][0],
                        boundbox_lines[xi][0][1] + 0.5 * ticklength,
                        small_tick,
                    ),
                ]
                path = "--".join(["({0},{1},{2})".format(*coords) for coords in line])
                boundbox_asy += "draw(({0}), {1});\n".format(path, pen)

    height, width = (400, 400)  # TODO: Proper size

    # Background color
    if box.background_color:
        bg_color, opacity = asy_color(box.background_color)
        background_directive = "background=" + bg_color + ", "
    else:
        background_directive = ""

    tex = r"""
\begin{{asy}}
import three;
import solids;
import tube;
size({0}cm, {1}cm);
currentprojection=perspective({2[0]},{2[1]},{2[2]});
currentlight=light(rgb(0.5,0.5,0.5), {5}specular=red, (2,0,2), (2,2,2), (0,2,2));
{3}
{4}
\end{{asy}}
""".format(
        asy_number(width / 60),
        asy_number(height / 60),
        # Rescale viewpoint
        [vp * max([xmax - xmin, ymax - ymin, zmax - zmin]) for vp in box.viewpoint],
        asy,
        boundbox_asy,
        background_directive,
    )
    return tex


add_conversion_fn(Graphics3DBox, graphics3dbox)


def graphicsbox(box: GraphicsBox, elements=None, **options) -> str:
    """This is the top-level function that converts a Mathics Expression
    in to something suitable for AMSLaTeX.

    However right now the only LaTeX support for graphics is via Asymptote and
    that seems to be the package of choice in general for LaTeX.
    """
    assert elements is None

    if not elements:
        content = box.content
        fields = prepare_elements2d(box, content, options, max_width=450)
        if len(fields) == 2:
            elements, calc_dimensions = fields
        else:
            elements, calc_dimensions = fields[0], fields[-2]

    fields = calc_dimensions()
    if len(fields) == 8:
        xmin, xmax, ymin, ymax, w, h, width, height = fields
        elements.view_width = w

    else:
        assert len(fields) == 9
        xmin, xmax, ymin, ymax, _, _, _, width, height = fields
        elements.view_width = width

    asy_completely_visible = "\n".join(
        lookup_conversion_method(element, "asy")(element)
        for element in elements.elements
        if element.is_completely_visible
    )

    asy_regular = "\n".join(
        lookup_conversion_method(element, "asy")(element)
        for element in elements.elements
        if not element.is_completely_visible
    )

    asy_box = "box((%s,%s), (%s,%s))" % (
        asy_number(xmin),
        asy_number(ymin),
        asy_number(xmax),
        asy_number(ymax),
    )

    if box.background_color is not None:
        color, opacity = asy_color(box.background_color)
        if opacity is not None:
            color = color + f"+opacity({opacity})"
        asy_background = "filldraw(%s, %s);" % (asy_box, color)
    else:
        asy_background = ""

    tex = r"""
\begin{asy}
usepackage("amsmath");
size(%scm, %scm);
%s
%s
clip(%s);
%s
\end{asy}
""" % (
        asy_number(width / 60),
        asy_number(height / 60),
        asy_background,
        asy_regular,
        asy_box,
        asy_completely_visible,
    )
    return tex


add_conversion_fn(GraphicsBox, graphicsbox)


def gridbox(box: GridBox, elements=None, **box_options) -> str:
    if not elements:
        elements = box._elements
    evaluation = box_options.get("evaluation")
    items, options = box.get_array(elements, evaluation)
    box_options.update(options)
    box_options["inside_list"] = True
    column_alignments = box_options["System`ColumnAlignments"].get_name()
    try:
        column_alignments = {
            "System`Center": "c",
            "System`Left": "l",
            "System`Right": "r",
        }[column_alignments]
    except KeyError as exc:
        # invalid column alignment
        raise BoxConstructError from exc
    column_count = 1
    for row in items:
        if isinstance(row, tuple):
            column_count = max(column_count, len(row))

    result = r"\begin{array}{%s} " % (column_alignments * column_count)
    for index, row in enumerate(items):
        if isinstance(row, tuple):
            result += " & ".join(
                convert_box_to_format(item, **box_options) for item in row
            )
        else:
            result += r"\multicolumn{%s}{%s}{%s}" % (
                str(column_count),
                column_alignments,
                convert_box_to_format(row, **box_options),
            )
        if index != len(items) - 1:
            result += "\\\\ "
    result += r"\end{array}"
    return result


add_conversion_fn(GridBox, gridbox)
add_conversion_fn(InterpretationBox, convert_inner_box)


def pane_box(box: PaneBox, **options):
    content = convert_inner_box_field(box, **options)
    options = box.box_options
    size = options.get("System`ImageSize", SymbolAutomatic).to_python()

    if size == "System`Automatic":
        return content
    if isinstance(size, int):
        width = f"{size}pt"
        height = ""
    elif isinstance(size, tuple) and len(size) == 2:
        width_val, height_val = size[0], size[1]
        if isinstance(width_val, int):
            width = f"{width_val}pt"
        else:
            width = "\\textwidth"
        if isinstance(height_val, int):
            height = f"[{height_val}pt]"
        else:
            height = ""
    else:
        width = "\\textwidth"
        height = ""

    return (
        "\\begin{minipage}{"
        + width
        + "}"
        + height
        + "\n"
        + content
        + "\n\\end{minipage}"
    )


add_conversion_fn(PaneBox, pane_box)


def rowbox_sequence(items, **options):
    parts_str = [
        lookup_conversion_method(element, "latex")(element, **options)
        for element in items
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


def rowbox_parenthesized(items, **options):
    if len(items) < 2:
        return None
    key = (
        items[0],
        items[-1],
    )
    items = items[1:-1]
    try:
        bracket_data = BRACKET_INFO[key]
    except KeyError:
        return None

    contain = rowbox_sequence(items, **options) if len(items) > 0 else ""

    if any(item.is_multiline for item in items):
        return f'{bracket_data["latex_open_large"]}{contain}{bracket_data["latex_closing_large"]}'
    return f'{bracket_data["latex_open"]}{contain}{bracket_data["latex_closing"]}'


def rowbox(box: RowBox, **options) -> str:
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**box.box_options, **options}
    items = box.items
    # Handle special cases
    if len(items) >= 3:
        head, *rest = items
        rest_latex = rowbox_parenthesized(rest, **options)
        if rest_latex is not None:
            # Must be a function-like expression f[]
            head_latex = lookup_conversion_method(head, "latex")(head, **child_options)
            return head_latex + rest_latex
    if len(items) >= 2:
        parenthesized_latex = rowbox_parenthesized(items, **child_options)
        if parenthesized_latex is not None:
            return parenthesized_latex
    return rowbox_sequence(items, **child_options)


add_conversion_fn(RowBox, rowbox)


def sqrtbox(box: SqrtBox, **options):
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**options, **box.box_options}
    if box.index:
        return "\\sqrt[%s]{%s}" % (
            lookup_conversion_method(box.radicand, "latex")(box.radicand, **options),
            lookup_conversion_method(box.index, "latex")(box.index, **options),
        )
    return "\\sqrt{%s}" % lookup_conversion_method(box.radicand, "latex")(
        box.radicand, **child_options
    )


add_conversion_fn(SqrtBox, sqrtbox)


def string(s: String, **options) -> str:
    """String to LaTeX form"""
    text = s.value

    def render(format, string_, in_text=False):
        return format % encode_tex(string_, in_text)

    if text.startswith('"') and text.endswith('"'):
        show_string_characters = (
            options.get("System`ShowStringCharacters", None) is SymbolTrue
        )
        # In WMA, ``TeXForm`` never adds quotes to
        # strings, even if ``InputForm`` or ``FullForm``
        # is required, to so get the standard WMA behaviour,
        # this option is set to False:
        # show_string_characters = False
        if show_string_characters:
            return render(r"\text{``%s''}", text[1:-1], in_text=True)
        return render(r"\text{%s}", text[1:-1], in_text=True)
    if text and text[0] in "0123456789-.":
        text = text.split("`")[0]
        return render("%s", text)

    # First consider the special cases
    op_string = AMSTEX_OPERATORS.get(text, None)
    if op_string:
        return op_string

    # Regular text:
    if len(text) > 1:
        return render(r"\text{%s}", text, in_text=True)

    # Unicode operator or variable?
    op_string = get_latex_operator(text)
    if len(op_string) > 7 and op_string[:7] == r"\symbol":
        op_string = r"\text{" + op_string + "}"

    if op_string != text:
        return f" {op_string} "

    # must be a variable...
    return render("%s", text)


add_conversion_fn(String, string)


def subscriptbox(box: SubscriptBox, **options):
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**options, **box.box_options}
    base_to_tex = lookup_conversion_method(box.base, "latex")
    subidx_to_tex = lookup_conversion_method(box.subindex, "latex")
    return "%s_%s" % (
        box.tex_block(base_to_tex(box.base, **child_options), True),
        box.tex_block(subidx_to_tex(box.subindex, **child_options)),
    )


add_conversion_fn(SubscriptBox, subscriptbox)


def subsuperscriptbox(box: SubsuperscriptBox, **options):
    # Note: values set in `options` take precedence over `box_options`
    child_options = {**box.box_options, **options}
    base_to_tex = lookup_conversion_method(box.base, "latex")
    subidx_to_tex = lookup_conversion_method(box.subindex, "latex")
    superidx_to_tex = lookup_conversion_method(box.superindex, "latex")

    return "%s_%s^%s" % (
        box.tex_block(base_to_tex(box.base, **child_options), True),
        box.tex_block(subidx_to_tex(box.subindex, **child_options)),
        box.tex_block(superidx_to_tex(box.superindex, **child_options)),
    )


add_conversion_fn(SubsuperscriptBox, subsuperscriptbox)


def superscriptbox(box: SuperscriptBox, **options):
    child_options = {**options, **box.box_options}
    base_to_tex = lookup_conversion_method(box.base, "latex")
    tex1 = base_to_tex(box.base, **options)

    sup_string = box.superindex.get_string_value()
    # Handle derivatives
    if sup_string == named_characters["Prime"]:
        return "%s'" % tex1
    if sup_string == named_characters["Prime"] * 2:
        return "%s''" % tex1
    base = box.tex_block(tex1, True)
    superidx_to_tex = lookup_conversion_method(box.superindex, "latex")
    superindx = box.tex_block(superidx_to_tex(box.superindex, **child_options), True)
    if len(superindx) == 1 and isinstance(box.superindex, (String, StyleBox)):
        return "%s^%s" % (
            base,
            superindx,
        )
    return "%s^{%s}" % (
        base,
        superindx,
    )


add_conversion_fn(SuperscriptBox, superscriptbox)
add_conversion_fn(StyleBox, convert_inner_box)
add_conversion_fn(TagBox, convert_inner_box)
