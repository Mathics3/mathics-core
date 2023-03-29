# -*- coding: utf-8 -*-
"""
Color Operations

Functions for manipulating colors.
"""


import itertools
from math import floor

import numpy

from mathics.builtin.base import Builtin
from mathics.builtin.colors.color_directives import ColorError, RGBColor, _ColorObject
from mathics.builtin.colors.color_internals import convert_color
from mathics.core.atoms import Integer, MachineReal, Rational, Real, String
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRGBColor


class Blend(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/Blend.html</url>

    <dl>
      <dt>'Blend[{$c1$, $c2$}]'
      <dd>represents the color between $c1$ and $c2$.

      <dt>'Blend[{$c1$, $c2$}, $x$]'
      <dd>represents the color formed by blending $c1$ and $c2$ with
          factors 1 - $x$ and $x$ respectively.

      <dt>'Blend[{$c1$, $c2$, ..., $cn$}, $x$]'
      <dd>blends between the colors $c1$ to $cn$ according to the
          factor $x$.
    </dl>

    >> Blend[{Red, Blue}]
     = RGBColor[0.5, 0., 0.5]
    >> Blend[{Red, Blue}, 0.3]
     = RGBColor[0.7, 0., 0.3]
    >> Blend[{Red, Blue, Green}, 0.75]
     = RGBColor[0., 0.5, 0.5]

    >> Graphics[Table[{Blend[{Red, Green, Blue}, x], Rectangle[{10 x, 0}]}, {x, 0, 1, 1/10}]]
     = -Graphics-

    >> Graphics[Table[{Blend[{RGBColor[1, 0.5, 0, 0.5], RGBColor[0, 0, 1, 0.5]}, x], Disk[{5x, 0}]}, {x, 0, 1, 1/10}]]
     = -Graphics-

    #> Blend[{Red, Green, Blue}, {1, 0.5}]
     : {1, 0.5} should be a real number or a list of non-negative numbers, which has the same length as {RGBColor[1, 0, 0], RGBColor[0, 1, 0], RGBColor[0, 0, 1]}.
     = Blend[{RGBColor[1, 0, 0], RGBColor[0, 1, 0], RGBColor[0, 0, 1]}, {1, 0.5}]
    """

    messages = {
        "arg": (
            "`1` is not a valid list of color or gray-level directives, "
            "or pairs of a real number and a directive."
        ),
        "argl": (
            "`1` should be a real number or a list of non-negative "
            "numbers, which has the same length as `2`."
        ),
    }

    rules = {"Blend[colors_]": "Blend[colors, ConstantArray[1, Length[colors]]]"}
    summary_text = "blend of colors"

    def do_blend(self, colors, values):
        type = None
        homogenous = True
        for color in colors:
            if type is None:
                type = color.__class__
            else:
                if color.__class__ != type:
                    homogenous = False
                    break
        if not homogenous:
            colors = [RGBColor(components=color.to_rgba()) for color in colors]
            type = RGBColor
        total = sum(values)
        result = None
        for color, value in zip(colors, values):
            frac = value / total
            part = [component * frac for component in color.components]
            if result is None:
                result = part
            else:
                result = [r + p for r, p in zip(result, part)]
        return type(components=result)

    def eval(self, colors, u, evaluation: Evaluation):
        "Blend[{colors___}, u_]"

        colors_orig = colors
        try:
            colors = [_ColorObject.create(color) for color in colors.get_sequence()]
            if not colors:
                raise ColorError
        except ColorError:
            evaluation.message("Blend", "arg", ListExpression(colors_orig))
            return

        if u.has_form("List", None):
            values = [value.round_to_float(evaluation) for value in u.elements]
            if None in values:
                values = None
            if len(u.elements) != len(colors):
                values = None
            use_list = True
        else:
            values = u.round_to_float(evaluation)
            if values is None:
                pass
            elif values > 1:
                values = 1.0
            elif values < 0:
                values = 0.0
            use_list = False
        if values is None:
            evaluation.message("Blend", "argl", u, ListExpression(colors_orig))
            return

        if use_list:
            return self.do_blend(colors, values).to_expr()
        else:
            x = values
            pos = int(floor(x * (len(colors) - 1)))
            x = (x - pos * 1.0 / (len(colors) - 1)) * (len(colors) - 1)
            if pos == len(colors) - 1:
                return colors[-1].to_expr()
            else:
                return self.do_blend(colors[pos : (pos + 2)], [1 - x, x]).to_expr()


class ColorConvert(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ColorConvert.html</url>

    <dl>
      <dt>'ColorConvert[$c$, $colspace$]'
      <dd>returns the representation of $c$ in the color space $colspace$. $c$ \
          may be a color or an image.
    </dl>

    Valid values for $colspace$ are:

    CMYK: convert to CMYKColor
    Grayscale: convert to GrayLevel
    HSB: convert to Hue
    LAB: concert to LABColor
    LCH: convert to LCHColor
    LUV: convert to LUVColor
    RGB: convert to RGBColor
    XYZ: convert to XYZColor
    """

    messages = {
        "ccvinput": "`` should be a color.",
        "imgcstype": "`` is not a valid color space.",
    }
    summary_text = "convert between color models"

    def eval(self, input, colorspace, evaluation: Evaluation):
        "ColorConvert[input_, colorspace_String]"

        from mathics.builtin.colors.color_directives import (
            color_to_expression,
            expression_to_color,
        )

        py_color = expression_to_color(input)
        if py_color is None:
            evaluation.message("ColorConvert", "ccvinput", input)
            return

        py_colorspace = colorspace.get_string_value()
        converted_components = convert_color(
            py_color.components, py_color.color_space, py_colorspace
        )

        if converted_components is None:
            evaluation.message("ColorConvert", "imgcstype", colorspace)
            return

        return color_to_expression(converted_components, py_colorspace)


class ColorNegate(Builtin):
    """
    Color Inversion (<url>
    :WMA:
    https://reference.wolfram.com/language/ref/ColorNegate.html</url>)

    <dl>
      <dt>'ColorNegate[$color$]'
      <dd>returns the negative of a color, that is, the RGB color \
          subtracted from white.
    </dl>

    Yellow is 'RGBColor[1.0, 1.0, 0.0]' So when inverted or subtracted \
    from 'White', we get blue:

    >> ColorNegate[Yellow] == Blue
     = True

    """

    summary_text = "perform color inversion on a color"

    def eval_for_color(self, color, evaluation: Evaluation):
        "ColorNegate[color_RGBColor]"
        # Get components
        r, g, b = [element.to_python() for element in color.elements]
        # Invert
        r, g, b = (1.0 - r, 1.0 - g, 1.0 - b)
        # Reconstitute
        return Expression(SymbolRGBColor, Real(r), Real(g), Real(b))


class Darker(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Darker.html</url>

    <dl>
    <dt>'Darker[$c$, $f$]'
        <dd>is equivalent to 'Blend[{$c$, Black}, $f$]'.
    <dt>'Darker[$c$]'
        <dd>is equivalent to 'Darker[$c$, 1/3]'.
    </dl>

    >> Graphics[{Darker[Red], Disk[]}]
     = -Graphics-

    >> Graphics3D[{Darker[Green], Sphere[]}]
     = -Graphics3D-

    >> Graphics[Table[{Darker[Yellow, x], Disk[{12x, 0}]}, {x, 0, 1, 1/6}]]
     = -Graphics-
    """

    rules = {"Darker[c_, f_]": "Blend[{c, Black}, f]", "Darker[c_]": "Darker[c, 1/3]"}
    summary_text = "make a color darker"


class Lighter(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Lighter.html</url>

    <dl>
      <dt>'Lighter[$c$, $f$]'
      <dd>is equivalent to 'Blend[{$c$, White}, $f$]'.

      <dt>'Lighter[$c$]'
      <dd>is equivalent to 'Lighter[$c$, 1/3]'.
    </dl>

    >> Lighter[Orange, 1/4]
     = RGBColor[1., 0.625, 0.25]
    >> Graphics[{Lighter[Orange, 1/4], Disk[]}]
     = -Graphics-
    >> Graphics[Table[{Lighter[Orange, x], Disk[{12x, 0}]}, {x, 0, 1, 1/6}]]
     = -Graphics-
    """

    rules = {
        "Lighter[c_, f_]": "Blend[{c, White}, f]",
        "Lighter[c_]": "Lighter[c, 1/3]",
    }
    summary_text = "make a color lighter"
