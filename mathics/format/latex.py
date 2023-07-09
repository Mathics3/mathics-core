# -*- coding: utf-8 -*-
"""Lower-level formatter of Mathics objects as (AMS)LaTeX strings.

AMS LaTeX is LaTeX with addition mathematical symbols, which
we may make use of via the mathics-scanner tables.

LaTeX formatting is usually initiated in Mathics via TeXForm[].

TeXForm in WMA is slightly vague or misleading since the output is
typically LaTeX rather than Plain TeX. In Mathics, we also assume AMS
LaTeX or more specifically that we the additional AMS Mathematical
Symbols exist.
"""

import re

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
from mathics.builtin.colors.color_directives import RGBColor
from mathics.core.atoms import String
from mathics.core.exceptions import BoxConstructError
from mathics.core.formatter import (
    add_conversion_fn,
    lookup_method as lookup_conversion_method,
)
from mathics.core.symbols import SymbolTrue
from mathics.format.asy_fns import asy_color, asy_create_pens, asy_number

# mathics_scanner does not generates this table in a way that we can load it here.
# When it get fixed, we can use that table instead of this one:

amstex_operators = {
    "\u2032": "'",
    "\u2032\u2032": "''",
    "\u2062": " ",
    "\u221e": r"\infty ",
    "\u00d7": r"\times ",
    "(": r"\left(",
    "[": r"\left[",
    "{": r"\left\{",
    ")": r"\right)",
    "]": r"\right]",
    "}": r"\right\}",
    "\u301a": r"\left[\left[",
    "\u301b": r"\right]\right]",
    ",": ",",
    ", ": ", ",
    "\u222b": r"\int",
    "\u2146": r"\, d",
    "\uF74C": r"\, d",
    "\U0001D451": r"\, d",
    "\u2211": r"\sum",
    "\u220f": r"\prod",
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
    "\u222b": r"\int ",
    "\u2146": r"\, d",
    "\uF74C": r"\, d",
    "\U0001D451": r"\, d",
}
TEX_TEXT_REPLACE = TEX_REPLACE.copy()
TEX_TEXT_REPLACE.update(
    {
        "<": r"$<$",
        ">": r"$>$",
        "~": r"$\sim$",
        "|": r"$\vert$",
        "\\": r"$\backslash$",
        "^": r"${}^{\wedge}$",
        "\u222b": r"$\int$ ",
        "\uF74C": r"\, d",
    }
)
TEX_REPLACE_RE = re.compile("([" + "".join([re.escape(c) for c in TEX_REPLACE]) + "])")


def encode_tex(text: str, in_text=False) -> str:
    def replace(match):
        c = match.group(1)
        repl = TEX_TEXT_REPLACE if in_text else TEX_REPLACE
        # return TEX_REPLACE[c]
        return repl.get(c, c)

    text = TEX_REPLACE_RE.sub(replace, text)
    text = text.replace("\n", "\\newline\n")
    return text


def string(self, **options) -> str:
    text = self.value

    def render(format, string, in_text=False):
        return format % encode_tex(string, in_text)

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
        else:
            return render(r"\text{%s}", text[1:-1], in_text=True)
    elif text and text[0] in "0123456789-.":
        return render("%s", text)
    else:
        op_string = amstex_operators.get(text, None)
        if op_string:
            return op_string
        elif len(text) > 1:
            return render(r"\text{%s}", text, in_text=True)
        else:
            return render("%s", text)


add_conversion_fn(String, string)


def fractionbox(self, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    return "\\frac{%s}{%s}" % (
        lookup_conversion_method(self.num, "latex")(self.num, **options),
        lookup_conversion_method(self.den, "latex")(self.den, **options),
    )


add_conversion_fn(FractionBox, fractionbox)


def gridbox(self, elements=None, **box_options) -> str:
    def boxes_to_tex(box, **options):
        return lookup_conversion_method(box, "latex")(box, **options)

    if not elements:
        elements = self._elements
    evaluation = box_options.get("evaluation")
    items, options = self.get_array(elements, evaluation)

    new_box_options = box_options.copy()
    new_box_options["inside_list"] = True
    column_alignments = options["System`ColumnAlignments"].get_name()
    try:
        column_alignments = {
            "System`Center": "c",
            "System`Left": "l",
            "System`Right": "r",
        }[column_alignments]
    except KeyError:
        # invalid column alignment
        raise BoxConstructError
    column_count = 1
    for row in items:
        if isinstance(row, tuple):
            column_count = max(column_count, len(row))

    result = r"\begin{array}{%s} " % (column_alignments * column_count)
    for index, row in enumerate(items):
        if isinstance(row, tuple):
            result += " & ".join(boxes_to_tex(item, **new_box_options) for item in row)
        else:
            result += r"\multicolumn{%s}{%s}{%s}" % (
                str(column_count),
                column_alignments,
                boxes_to_tex(row, **new_box_options),
            )
        if index != len(items) - 1:
            result += "\\\\ "
    result += r"\end{array}"
    return result


add_conversion_fn(GridBox, gridbox)


def sqrtbox(self, **options):
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    if self.index:
        return "\\sqrt[%s]{%s}" % (
            lookup_conversion_method(self.radicand, "latex")(self.radicand, **options),
            lookup_conversion_method(self.index, "latex")(self.index, **options),
        )
    return "\\sqrt{%s}" % lookup_conversion_method(self.radicand, "latex")(
        self.radicand, **options
    )


add_conversion_fn(SqrtBox, sqrtbox)


def superscriptbox(self, **options):
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    base_to_tex = lookup_conversion_method(self.base, "latex")
    tex1 = base_to_tex(self.base, **options)

    sup_string = self.superindex.get_string_value()
    # Handle derivatives
    if sup_string == "\u2032":
        return "%s'" % tex1
    elif sup_string == "\u2032\u2032":
        return "%s''" % tex1
    else:
        base = self.tex_block(tex1, True)
        superidx_to_tex = lookup_conversion_method(self.superindex, "latex")
        superindx = self.tex_block(superidx_to_tex(self.superindex, **options), True)
        if isinstance(self.superindex, (String, StyleBox)):
            return "%s^%s" % (
                base,
                superindx,
            )
        else:
            return "%s^{%s}" % (
                base,
                superindx,
            )


add_conversion_fn(SuperscriptBox, superscriptbox)


def subscriptbox(self, **options):
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    base_to_tex = lookup_conversion_method(self.base, "latex")
    subidx_to_tex = lookup_conversion_method(self.subindex, "latex")
    return "%s_%s" % (
        self.tex_block(base_to_tex(self.base, **options), True),
        self.tex_block(subidx_to_tex(self.subindex, **options)),
    )


add_conversion_fn(SubscriptBox, subscriptbox)


def subsuperscriptbox(self, **options):
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    base_to_tex = lookup_conversion_method(self.base, "latex")
    subidx_to_tex = lookup_conversion_method(self.subindex, "latex")
    superidx_to_tex = lookup_conversion_method(self.superindex, "latex")

    return "%s_%s^%s" % (
        self.tex_block(base_to_tex(self.base, **options), True),
        self.tex_block(subidx_to_tex(self.subindex, **options)),
        self.tex_block(superidx_to_tex(self.superindex, **options)),
    )


add_conversion_fn(SubsuperscriptBox, subsuperscriptbox)


def rowbox(self, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    return "".join(
        [
            lookup_conversion_method(element, "latex")(element, **options)
            for element in self.items
        ]
    )


add_conversion_fn(RowBox, rowbox)


def stylebox(self, **options) -> str:
    _options = self.box_options.copy()
    _options.update(options)
    options = _options
    return lookup_conversion_method(self.boxes, "latex")(self.boxes, **options)


add_conversion_fn(StyleBox, stylebox)


def graphicsbox(self, elements=None, **options) -> str:
    """This is the top-level function that converts a Mathics Expression
    in to something suitable for AMSLaTeX.

    However right now the only LaTeX support for graphics is via Asymptote and
    that seems to be the package of choice in general for LaTeX.
    """

    if not elements:
        elements = self._elements
        fields = self._prepare_elements(elements, options, max_width=450)
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

    if self.background_color is not None:
        color, opacity = asy_color(self.background_color)
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


def graphics3dbox(self, elements=None, **options) -> str:
    if not elements:
        elements = self._elements

    (
        elements,
        axes,
        ticks,
        ticks_style,
        calc_dimensions,
        boxscale,
    ) = self._prepare_elements(elements, options, max_width=450)

    elements._apply_boxscaling(boxscale)

    format_fn = lookup_conversion_method(elements, "asy")
    if format_fn is not None:
        asy = format_fn(elements)
    else:
        asy = elements.to_asy()

    xmin, xmax, ymin, ymax, zmin, zmax, boxscale, w, h = calc_dimensions()

    # TODO: Intelligently place the axes on the longest non-middle edge.
    # See algorithm used by web graphics in mathics/web/media/graphics.js
    # for details of this. (Projection to sceen etc).

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
    boundbox_lines = self.get_boundbox_lines(xmin, xmax, ymin, ymax, zmin, zmax)

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

    (height, width) = (400, 400)  # TODO: Proper size
    tex = r"""
\begin{{asy}}
import three;
import solids;
size({0}cm, {1}cm);
currentprojection=perspective({2[0]},{2[1]},{2[2]});
currentlight=light(rgb(0.5,0.5,1), specular=red, (2,0,2), (2,2,2), (0,2,2));
{3}
{4}
\end{{asy}}
""".format(
        asy_number(width / 60),
        asy_number(height / 60),
        # Rescale viewpoint
        [vp * max([xmax - xmin, ymax - ymin, zmax - zmin]) for vp in self.viewpoint],
        asy,
        boundbox_asy,
    )
    return tex


add_conversion_fn(Graphics3DBox, graphics3dbox)
