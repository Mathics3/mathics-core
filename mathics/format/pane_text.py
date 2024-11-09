"""
This module produces a "pretty-print" inspired 2d text representation.

This code is completely independent from Mathics objects, so it could live
alone in a different package.
"""

from typing import List, Optional, Union


class TextBlock:
    lines: List[str]
    width: int
    height: int
    base: int

    @staticmethod
    def _build_attributes(lines, width=0, height=0, base=0):
        width = max(width, max(len(line) for line in lines)) if lines else 0

        # complete lines:
        lines = [
            line if len(line) == width else (line + (width - len(line)) * " ")
            for line in lines
        ]

        if base < 0:
            height = height - base
            empty_line = width * " "
            lines = (-base) * [empty_line] + lines
            base = -base
        if height > len(lines):
            empty_line = width * " "
            lines = lines + (height - len(lines)) * [empty_line]
        else:
            height = len(lines)

        return (lines, width, height, base)

    def __init__(self, text, padding=0, base=0, height=1, width=0):
        if isinstance(text, str):
            if text == "":
                lines = []
            else:
                lines = text.split("\n")
        else:
            lines = sum((line.split("\n") for line in text), [])
        if padding:
            padding_spaces = padding * " "
            lines = [padding_spaces + line.replace("\t", "    ") for line in lines]
        else:
            lines = [line.replace("\t", "    ") for line in lines]

        self.lines, self.width, self.height, self.base = self._build_attributes(
            lines, width, height, base
        )

    @property
    def text(self):
        return "\n".join(self.lines)

    @text.setter
    def text(self, value):
        raise TypeError("TextBlock is inmutable")

    def __repr__(self):
        return self.text

    def __add__(self, tb):
        result = TextBlock("")
        result += self
        result += tb
        return result

    def __iadd__(self, tb):
        """In-place addition"""
        if isinstance(tb, str):
            tb = TextBlock(tb)
        base = self.base
        other_base = tb.base
        left_lines = self.lines
        right_lines = tb.lines
        offset = other_base - base
        if offset > 0:
            left_lines = left_lines + offset * [self.width * " "]
            base = other_base
        elif offset < 0:
            offset = -offset
            right_lines = right_lines + offset * [tb.width * " "]

        offset = len(right_lines) - len(left_lines)
        if offset > 0:
            left_lines = offset * [self.width * " "] + left_lines
        elif offset < 0:
            right_lines = (-offset) * [tb.width * " "] + right_lines

        return TextBlock(
            list(left + right for left, right in zip(left_lines, right_lines)),
            base=base,
        )

    def ajust_base(self, base: int):
        """
        if base is larger than self.base,
        adds lines at the bottom of the text
        and update self.base
        """
        if base > self.base:
            diff = base - self.base
            result = TextBlock(
                self.lines + diff * [" "], self.width, self.height, self.base
            )

        return result

    def ajust_width(self, width: int, align: str = "c"):
        def padding(lines, diff):
            if diff > 0:
                if align == "c":
                    left_pad = int(diff / 2)
                    right_pad = diff - left_pad
                    lines = [
                        (left_pad * " " + line + right_pad * " ") for line in lines
                    ]
                elif align == "r":
                    lines = [(diff * " " + line) for line in lines]
                else:
                    lines = [(line + diff * " ") for line in lines]
            return lines

        diff_width = width - self.width
        if diff_width <= 0:
            return self

        new_lines = padding(self.lines, diff_width)
        return TextBlock(new_lines, base=self.base)

    def box(self):
        top = "+" + self.width * "-" + "+"
        out = "\n".join("|" + line + "|" for line in self.lines)
        out = top + "\n" + out + "\n" + top
        return TextBlock(out, self.base + 1)

    def join(self, iterable):
        result = TextBlock("")
        for i, item in enumerate(iterable):
            if i == 0:
                result = item
            else:
                result = result + self + item
        return result

    def stack(self, top, align: str = "c"):
        if isinstance(top, str):
            top = TextBlock(top)

        bottom = self
        bottom_width, top_width = bottom.width, top.width

        if bottom_width > top_width:
            top = top.ajust_width(bottom_width, align=align)
        elif bottom_width < top_width:
            bottom = bottom.ajust_width(top_width, align=align)

        return TextBlock(top.lines + bottom.lines, base=self.base)  # type: ignore[union-attr]


def _draw_integral_symbol(height: int) -> TextBlock:
    return TextBlock(
        (" /+ \n" + "\n".join(height * [" |  "]) + "\n+/ "), base=int((height + 1) / 2)
    )


def bracket(inner: Union[str, TextBlock]) -> TextBlock:
    if isinstance(inner, str):
        inner = TextBlock(inner)
    height = inner.height
    if height == 1:
        left_br, right_br = TextBlock("["), TextBlock("]")
    else:
        left_br = TextBlock(
            "+-\n" + "\n".join((height) * ["| "]) + "\n+-", base=inner.base + 1
        )
        right_br = TextBlock(
            "-+ \n" + "\n".join((height) * [" |"]) + "\n-+", base=inner.base + 1
        )
    return left_br + inner + right_br


def curly_braces(inner: Union[str, TextBlock]) -> TextBlock:
    if isinstance(inner, str):
        inner = TextBlock(inner)
    height = inner.height
    if height == 1:
        left_br, right_br = TextBlock("{"), TextBlock("}")
    else:
        half_height = max(1, int((height - 3) / 2))
        half_line = "\n".join(half_height * [" |"])
        left_br = TextBlock(
            "\n".join([" /", half_line, "< ", half_line, " \\"]), base=half_height + 1
        )
        half_line = "\n".join(half_height * ["| "])
        right_br = TextBlock(
            "\n".join(["\\ ", half_line, " >", half_line, "/ "]), base=half_height + 1
        )

    return left_br + inner + right_br


def draw_vertical(
    pen: str, height, base=0, left_padding=0, right_padding=0
) -> TextBlock:
    """
    build a TextBlock with a vertical line of height `height`
    using the string `pen`. If paddings are given,
    spaces are added to the sides.
    For example, `draw_vertical("=", 3)` produces
    TextBlock(("=\n"
               "=\n"
               "=", base=base
             )
    """
    pen = (left_padding * " ") + str(pen) + (right_padding * " ")
    return TextBlock("\n".join(height * [pen]), base=base)


def fraction(a: Union[TextBlock, str], b: Union[TextBlock, str]) -> TextBlock:
    """
    A TextBlock representation of
    a Fraction
    """
    if isinstance(a, str):
        a = TextBlock(a)
    if isinstance(b, str):
        b = TextBlock(b)
    width = max(b.width, a.width) + 2
    frac_bar = TextBlock(width * "-")
    result = frac_bar.stack(a)
    result = b.stack(result)
    result.base = b.height
    return result


def grid(items: list, **options) -> TextBlock:
    """
    Process items and build a TextBlock
    """
    result: TextBlock = TextBlock("")

    if not items:
        return result

    # Ensure that items is a list
    items = list(items)
    # Ensure that all are TextBlock or list
    items = [TextBlock(item) if isinstance(item, str) else item for item in items]

    # options
    col_border = options.get("col_border", False)
    row_border = options.get("row_border", False)

    # normalize widths:
    widths: list = [1]
    try:
        widths = [1] * max(
            len(item) for item in items if isinstance(item, (tuple, list))
        )
    except ValueError:
        pass

    full_width: int = 0
    for row in items:
        if isinstance(row, TextBlock):
            full_width = max(full_width, row.width)
        else:
            for index, item in enumerate(row):
                widths[index] = max(widths[index], item.width)

    total_width: int = sum(widths) + max(0, len(widths) - 1) * 3

    if full_width > total_width:
        widths[-1] = widths[-1] + full_width - total_width
        total_width = full_width

    # Set the borders

    if row_border:
        if col_border:
            interline = TextBlock("+" + "+".join((w + 2) * "-" for w in widths) + "+")
        else:
            interline = TextBlock((sum(w + 3 for w in widths) - 2) * "-")
        full_width = interline.width - 4
    else:
        if col_border:
            interline = (
                TextBlock("|")
                + TextBlock("|".join((w + 2) * " " for w in widths))
                + TextBlock("|")
            )
            full_width = max(0, interline.width - 4)
        else:
            interline = TextBlock((sum(w + 3 for w in widths) - 3) * " ")
            full_width = max(0, interline.width - 4)

    def normalize_widths(row):
        if isinstance(row, TextBlock):
            return [row.ajust_width(max(0, full_width), align="l")]
        return [item.ajust_width(widths[i]) for i, item in enumerate(row)]

    items = [normalize_widths(row) for row in items]

    if col_border:
        for i, row in enumerate(items):
            row_height: int = max(item.height for item in row)
            row_base: int = max(item.base for item in row)
            col_sep = draw_vertical(
                "|", height=row_height, base=row_base, left_padding=1, right_padding=1
            )

            new_row_txt = col_sep.join(row)
            new_row_txt = (
                draw_vertical("|", row_height, base=row_base, right_padding=1)
                + new_row_txt
                + draw_vertical("|", row_height, base=row_base, left_padding=1)
            )
            if i == 0:
                if row_border:
                    new_row_txt = new_row_txt.stack(interline, align="l")
                result = new_row_txt
            else:
                new_row_txt = new_row_txt.stack(interline, align="l")
                result = new_row_txt.stack(result, align="l")
    else:
        for i, row in enumerate(items):
            new_row_txt = TextBlock("   ").join(row)
            if i == 0:
                if row_border:
                    new_row_txt = new_row_txt.stack(interline, align="l")
                result = new_row_txt
            else:
                new_row_txt = new_row_txt.stack(interline, align="l")
                result = new_row_txt.stack(result, align="l")

    if row_border:
        result = interline.stack(result, align="l")

    result.base = int(result.height / 2)
    return result


def integral_indefinite(
    integrand: Union[TextBlock, str], var: Union[TextBlock, str]
) -> TextBlock:
    # TODO: handle list of vars
    # TODO: use utf as an option
    if isinstance(var, str):
        var = TextBlock(var)

    if isinstance(integrand, str):
        integrand = TextBlock(integrand)

    int_symb: TextBlock = _draw_integral_symbol(integrand.height)
    return int_symb + integrand + " d" + var


def integral_definite(
    integrand: Union[TextBlock, str],
    var: Union[TextBlock, str],
    a: Union[TextBlock, str],
    b: Union[TextBlock, str],
) -> TextBlock:
    # TODO: handle list of vars
    # TODO: use utf as an option
    if isinstance(var, str):
        var = TextBlock(var)
    if isinstance(integrand, str):
        integrand = TextBlock(integrand)
    if isinstance(a, str):
        a = TextBlock(a)
    if isinstance(b, str):
        b = TextBlock(b)

    int_symb = _draw_integral_symbol(integrand.height)
    return subsuperscript(int_symb, a, b) + " " + integrand + " d" + var


def parenthesize(inner: Union[str, TextBlock]) -> TextBlock:
    if isinstance(inner, str):
        inner = TextBlock(inner)
    height = inner.height
    if height == 1:
        left_br, right_br = TextBlock("("), TextBlock(")")
    else:
        left_br = TextBlock(
            "/ \n" + "\n".join((height - 2) * ["| "]) + "\n\\ ", base=inner.base
        )
        right_br = TextBlock(
            " \\ \n" + "\n".join((height - 2) * [" |"]) + "\n /", base=inner.base
        )
    return left_br + inner + right_br


def sqrt_block(
    a: Union[TextBlock, str], index: Optional[Union[TextBlock, str]] = None
) -> TextBlock:
    """
    Sqrt Text Block
    """
    if isinstance(a, str):
        a = TextBlock(a)
    if isinstance(index, str):
        index = TextBlock(index)

    a_height = a.height
    result_2 = TextBlock(
        "\n".join("|" + line for line in a.text.split("\n")), base=a.base
    )
    result_2 = result_2.stack((a.width + 1) * "_", align="l")
    half_height = int(a_height / 2)

    result_1 = TextBlock(
        "\n".join(
            [
                (int(i) * " " + "\\" + int((half_height - i - 1)) * " ")
                for i in range(half_height)
            ]
        ),
        base=a.base,
    )
    if index is not None:
        result_1 = result_1.stack(index, align="c")
    return result_1 + result_2


def subscript(base: Union[TextBlock, str], a: Union[TextBlock, str]) -> TextBlock:
    if isinstance(a, str):
        a = TextBlock(a)
    if isinstance(base, str):
        base = TextBlock(base)

    text2 = a.stack(TextBlock(base.height * [""], base=base.base), align="l")
    text2.base = base.base + a.height
    return base + text2


def subsuperscript(
    base: Union[TextBlock, str], a: Union[TextBlock, str], b: Union[TextBlock, str]
) -> TextBlock:
    if isinstance(base, str):
        base = TextBlock(base)
    if isinstance(a, str):
        a = TextBlock(a)
    if isinstance(b, str):
        b = TextBlock(b)

    text2 = a.stack((base.height - 1) * "\n", align="l").stack(b, align="l")
    text2.base = base.base + a.height
    return base + text2


def superscript(base: Union[TextBlock, str], a: Union[TextBlock, str]) -> TextBlock:
    if isinstance(base, str):
        base = TextBlock(base)
    text2 = TextBlock((base.height - 1) * "\n", base=base.base).stack(a, align="l")
    return base + text2
