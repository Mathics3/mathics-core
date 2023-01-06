"""
This module produces a "pretty-print" inspired 2d text representation. 
"""


class TextBlock:
    def __init__(self, text, padding=0, base=0, height=1, width=0):
        self.height = height
        self.padding = padding
        text = text.replace("\t", "    ")
        lines = text.split("\n")
        for line in lines:
            width = max(len(line), width)

        lines = [
            line if len(line) == width else (line + (width - len(line)) * " ")
            for line in lines
        ]
        self.width = width + padding
        lines = [padding * " " + line for line in lines]
        if base < 0:
            height = height - base
            lines = (-base) * [width * " "] + lines
            base = -base
        if height > len(lines):
            lines = lines + (height - len(lines)) * [width * " "]
        else:
            height = len(lines)
        self.height = height
        self.text = "\n".join(lines)
        self.base = base

    def box(self):
        top = "+" + self.width * "-" + "+"
        out = "\n".join("|" + line + "|" for line in self.text.split("\n"))
        out = top + "\n" + out + "\n" + top
        return TextBlock(out, self.base + 1)

    def __repr__(self):
        return self.text

    def __add__(self, tb):
        if isinstance(tb, str):
            tb = TextBlock(tb)
        base = self.base
        other_base = tb.base
        left_lines = self.text.split("\n")
        right_lines = tb.text.split("\n")
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

        new_str = "\n".join(l + r for l, r in zip(left_lines, right_lines))
        return TextBlock(new_str, base=base)

    def join(self, iter):
        result = TextBlock("")
        for i, item in enumerate(iter):
            if i == 0:
                result = item
            else:
                result = result + self + item
        return result

    def stack(self, other, align="c"):
        if isinstance(other, str):
            other = TextBlock(other)

        self_lines = self.text.split("\n")
        other_lines = other.text.split("\n")
        self_width, other_width = self.width, other.width
        diff_width = self_width - other_width

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

        if diff_width > 0:
            other_lines = padding(other_lines, diff_width)
        elif diff_width < 0:
            self_lines = padding(self_lines, -diff_width)

        lines = other_lines + self_lines
        return TextBlock("\n".join(lines), base=self.base)


def subsuperscript(base, a, b):
    if isinstance(base, str):
        base = TextBlock(base)
    if isinstance(b, str):
        b = TextBlock(b)

    text2 = b.stack((base.height - 1) * "\n", align="l").stack(a, align="l")
    text2.base = base.base + b.height
    return base + text2


def superscript(base, a):
    if isinstance(base, str):
        base = TextBlock(base)
    text2 = TextBlock((base.height - 1) * "\n", base=base.base).stack(a, align="l")
    return base + text2


def subscript(base, a):
    if isinstance(a, str):
        a = TextBlock(a)
    text2 = a.stack(TextBlock((base.height - 1) * "\n", base=base.base), align="l")
    text2.base = base.base + a.height
    return base + text2


def sqrt_block(a, index=None):
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


def fraction(a, b):
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


def integral_indefinite(integrand, var):
    if isinstance(var, str):
        var = TextBlock(var)
    if isinstance(integrand, str):
        integrand = TextBlock(integrand)

    height = integrand.height
    int_symb = TextBlock(
        "  /+ \n" + "\n".join(height * ["  |  "]) + "\n +/ ", base=int((height + 1) / 2)
    )
    return int_symb + integrand + " d" + var


def integral_definite(integrand, var, a, b):
    if isinstance(var, str):
        var = TextBlock(var)
    if isinstance(integrand, str):
        integrand = TextBlock(integrand)
    if isinstance(a, str):
        a = TextBlock(a)
    if isinstance(b, str):
        b = TextBlock(b)

    height = integrand.height
    int_symb = TextBlock(
        "  /+ \n" + "\n".join(height * ["  |  "]) + "\n +/ ", base=int((height + 1) / 2)
    )
    return subsuperscript(int_symb, a, b) + " " + integrand + " d" + var


def bracket(inner):
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


def parenthesize(inner):
    if isinstance(inner, str):
        inner = TextBlock(inner)
    height = inner.height
    if height == 1:
        left_br, right_br = TextBlock("("), TextBlock(")")
    else:
        left_br = TextBlock(
            "/ \n" + "\n".join((height) * ["| "]) + "\n\\ ", base=inner.base + 1
        )
        right_br = TextBlock(
            " \\ \n" + "\n".join((height) * [" |"]) + "\n /", base=inner.base + 1
        )
    return left_br + inner + right_br
