# -*- coding: utf-8 -*-
"""
Color Operations

Functions for manipulating colors and color images.
"""


import itertools
from math import floor

from mathics.builtin.base import Builtin
from mathics.builtin.colors.color_directives import ColorError, RGBColor, _ColorObject
from mathics.builtin.colors.color_internals import convert_color
from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer, MachineReal, Rational, Real, String
from mathics.core.convert.expression import to_expression, to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRGBColor

_image_requires = ("numpy", "PIL")

import numpy
import PIL.ImageOps


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

        if isinstance(input, Image):
            return input.color_convert(colorspace.get_string_value())
        else:
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

      <dt>'ColorNegate[$image$]'
      <dd>returns an image where each pixel has its color negated.
    </dl>

    Yellow is 'RGBColor[1.0, 1.0, 0.0]' So when inverted or subtracted \
    from 'White', we get blue:

    >> ColorNegate[Yellow] == Blue
     = True

    >> ColorNegate[Import["ExampleData/sunflowers.jpg"]]
     = -Image-
    """

    summary_text = "perform color inversion on a color or image"

    def eval_for_color(self, color, evaluation: Evaluation):
        "ColorNegate[color_RGBColor]"
        # Get components
        r, g, b = [element.to_python() for element in color.elements]
        # Invert
        r, g, b = (1.0 - r, 1.0 - g, 1.0 - b)
        # Reconstitute
        return Expression(SymbolRGBColor, Real(r), Real(g), Real(b))

    def eval_for_image(self, image, evaluation: Evaluation):
        "ColorNegate[image_Image]"
        return image.filter(lambda im: PIL.ImageOps.invert(im))


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


class DominantColors(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/DominantColors.html</url>

    <dl>
      <dt>'DominantColors[$image$]'
      <dd>gives a list of colors which are dominant in the given image.

      <dt>'DominantColors[$image$, $n$]'
      <dd>returns at most $n$ colors.

      <dt>'DominantColors[$image$, $n$, $prop$]'
      <dd>returns the given property $prop$, which may be:
        <ul>
           <li>"Color": return RGB colors,
           <li> "LABColor": return  LAB colors,
           <li> "Count": return the number of pixels a dominant color covers,
           <li> "Coverage": return the fraction of the image a dominant color \
                 covers, or
           <li> "CoverageImage": return a black and white image indicating with \
                 white the parts that are covered by a dominant color.
        </ul>
    </dl>

    The option "ColorCoverage" specifies the minimum amount of coverage needed to \
    include a dominant color in the result.

    The option "MinColorDistance" specifies the distance (in LAB color space) up \
    to which colors are merged and thus regarded as belonging to the same dominant color.

    >> img = Import["ExampleData/hedy.tif"]
     = -Image-

    >> DominantColors[img]
     = {RGBColor[0.00784314, 0.00784314, 0.0156863], RGBColor[0.996078, 0.803922, 0.721569], RGBColor[0.227451, 0.329412, 0.360784]}

    >> DominantColors[img, 3]
     = {RGBColor[0.00784314, 0.00784314, 0.0156863], RGBColor[0.996078, 0.803922, 0.721569], RGBColor[0.227451, 0.329412, 0.360784]}

    >> DominantColors[img, 3, "Coverage"]
     = {68817 / 103360, 62249 / 516800, 37953 / 516800}

    >> DominantColors[img, 3, "CoverageImage"]
     = {-Image-, -Image-, -Image-}

    >> DominantColors[img, 3, "Count"]
     = {344085, 62249, 37953}

    >> DominantColors[img, 2, "LABColor"]
     = {LABColor[0.00581591, 0.00207458, -0.00760911], LABColor[0.863667, 0.156864, 0.173956]}

    >> DominantColors[img, MinColorDistance -> 0.5]
     = {RGBColor[0.00784314, 0.00784314, 0.0156863], RGBColor[0.996078, 0.803922, 0.721569]}

    >> DominantColors[img, ColorCoverage -> 0.15]
     = {RGBColor[0.00784314, 0.00784314, 0.0156863]}
    """

    rules = {
        "DominantColors[image_Image, n_Integer, options___]": 'DominantColors[image, n, "Color", options]',
        "DominantColors[image_Image, options___]": 'DominantColors[image, 256, "Color", options]',
    }

    options = {"ColorCoverage": "Automatic", "MinColorDistance": "Automatic"}
    summary_text = "find a list of dominant colors"

    def eval(
        self,
        image: Image,
        n: Integer,
        prop: String,
        evaluation: Evaluation,
        options: dict,
    ):
        "DominantColors[image_Image, n_Integer, prop_String, OptionsPattern[%(name)s]]"

        py_prop = prop.value
        if py_prop not in ("Color", "LABColor", "Count", "Coverage", "CoverageImage"):
            return

        color_coverage = self.get_option(options, "ColorCoverage", evaluation)
        min_color_distance = self.get_option(options, "MinColorDistance", evaluation)

        if (
            isinstance(min_color_distance, Symbol)
            and min_color_distance.get_name() == "System`Automatic"
        ):
            py_min_color_distance = 0.15
        else:
            py_min_color_distance = min_color_distance.round_to_float()
            if py_min_color_distance is None:
                return

        if (
            isinstance(color_coverage, Symbol)
            and color_coverage.get_name() == "System`Automatic"
        ):
            py_min_color_coverage = 0.05
            py_max_color_coverage = 1.0
        elif color_coverage.has_form("List", 2):
            py_min_color_coverage = color_coverage.elements[0].round_to_float()
            py_max_color_coverage = color_coverage.elements[1].round_to_float()
        else:
            py_min_color_coverage = color_coverage.round_to_float()
            py_max_color_coverage = 1.0

        if py_min_color_coverage is None or py_max_color_coverage is None:
            return

        at_most = n.value

        if at_most > 256:
            return

        # reduce complexity by reducing to 256 colors. this is not uncommon; see Kiranyaz et al.,
        # "Perceptual Dominant Color Extraction by Multidimensional Particle Swarm Optimization":
        # "to reduce the computational complexity [...] a preprocessing step, which creates a
        # limited color palette in RGB color domain, is first performed."

        im = (
            image.color_convert("RGB")
            .pil()
            .convert("P", palette=PIL.Image.ADAPTIVE, colors=256)
        )
        pixels = numpy.array(list(im.getdata()))

        flat = numpy.array(list(im.getpalette())) / 255.0  # float values now
        rgb_palette = [flat[i : i + 3] for i in range(0, len(flat), 3)]  # group by 3
        lab_palette = [
            numpy.array(x) for x in convert_color(rgb_palette, "RGB", "LAB", False)
        ]

        bins = numpy.bincount(pixels, minlength=len(rgb_palette))
        num_pixels = im.size[0] * im.size[1]

        from mathics.algorithm.clusters import (
            FixedDistanceCriterion,
            PrecomputedDistances,
            agglomerate,
        )

        norm = numpy.linalg.norm

        def df(i, j):
            return norm(lab_palette[i] - lab_palette[j])

        lab_distances = [df(i, j) for i in range(len(lab_palette)) for j in range(i)]

        if py_prop == "LABColor":
            out_palette = lab_palette
            out_palette_head = "LABColor"
        else:
            out_palette = rgb_palette
            out_palette_head = "RGBColor"

        dominant = agglomerate(
            (out_palette, bins),
            (FixedDistanceCriterion, {"merge_limit": py_min_color_distance}),
            PrecomputedDistances(lab_distances),
            mode="dominant",
        )

        def result():
            min_count = max(0, int(num_pixels * py_min_color_coverage))
            max_count = min(num_pixels, int(num_pixels * py_max_color_coverage))

            for prototype, count, members in dominant:
                if max_count >= count > min_count:
                    if py_prop == "Count":
                        yield Integer(count)
                    elif py_prop == "Coverage":
                        yield Rational(int(count), num_pixels)
                    elif py_prop == "CoverageImage":
                        mask = numpy.ndarray(shape=pixels.shape, dtype=bool)
                        mask.fill(0)
                        for i in members:
                            mask = mask | (pixels == i)
                        yield Image(mask.reshape(tuple(reversed(im.size))), "Grayscale")
                    else:
                        yield to_expression(
                            Symbol(out_palette_head),
                            *prototype,
                            elements_conversion_fn=MachineReal
                        )

        return to_mathics_list(*itertools.islice(result(), 0, at_most))


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
