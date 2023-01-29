"""
Image Colors
"""

import numpy
import PIL

from mathics.builtin.base import Builtin, String
from mathics.builtin.colors.color_internals import colorspaces as known_colorspaces
from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolColorQuantize,
    SymbolMatrixQ,
    SymbolThreshold,
)
from mathics.eval.image import linearize_numpy_array, matrix_to_numpy, pixels_as_ubyte

# This tells documentation how to sort this module
sort_order = "mathics.builtin.image.image-colors"


class Binarize(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Binarize.html</url>

    <dl>
      <dt>'Binarize[$image$]'
      <dd>gives a binarized version of $image$, in which each pixel is either 0 or 1.

      <dt>'Binarize[$image$, $t$]'
      <dd>map values $x$ > $t$ to 1, and values $x$ <= $t$ to 0.

      <dt>'Binarize[$image$, {$t1$, $t2$}]'
      <dd>map $t1$ < $x$ < $t2$ to 1, and all other values to 0.
    </dl>

    S> hedy = Import["ExampleData/hedy.tif"];
    S> Binarize[hedy]
     = -Image-
    S> Binarize[hedy, 0.7]
     = -Image-
    S> Binarize[hedy, {0.2, 0.6}]
     = -Image-
    """

    summary_text = "create a binarized image"

    def eval(self, image: Image, evaluation: Evaluation):
        "Binarize[image_Image]"
        image = image.grayscale()
        thresh = (
            Expression(SymbolThreshold, image).evaluate(evaluation).round_to_float()
        )
        if thresh is not None:
            return Image(image.pixels > thresh, "Grayscale")

    def eval_t(self, image: Image, t, evaluation: Evaluation):
        "Binarize[image_Image, t_?RealNumberQ]"
        pixels = image.grayscale().pixels
        return Image(pixels > t.round_to_float(), "Grayscale")

    def eval_t1_t2(self, image: Image, t1, t2, evaluation: Evaluation):
        "Binarize[image_Image, {t1_?RealNumberQ, t2_?RealNumberQ}]"
        pixels = image.grayscale().pixels
        mask1 = pixels > t1.round_to_float()
        mask2 = pixels < t2.round_to_float()
        return Image(mask1 * mask2, "Grayscale")


class ColorCombine(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ColorCombine.html</url>

    <dl>
      <dt>'ColorCombine[$channels$, $colorspace$]'
      <dd>Gives an image with $colorspace$ and the respective components described by the given channels.
    </dl>

    >> ColorCombine[{{{1, 0}, {0, 0.75}}, {{0, 1}, {0, 0.25}}, {{0, 0}, {1, 0.5}}}, "RGB"]
     = -Image-
    """

    summary_text = "combine color channels"

    def eval(self, channels, colorspace, evaluation: Evaluation):
        "ColorCombine[channels_List, colorspace_String]"

        py_colorspace = colorspace.get_string_value()
        if py_colorspace not in known_colorspaces:
            return

        numpy_channels = []
        for channel in channels.elements:
            if (
                not Expression(SymbolMatrixQ, channel).evaluate(evaluation)
                is SymbolTrue
            ):
                return
            numpy_channels.append(matrix_to_numpy(channel))

        if not numpy_channels:
            return

        if not all(x.shape == numpy_channels[0].shape for x in numpy_channels[1:]):
            return

        return Image(numpy.dstack(numpy_channels), py_colorspace)


class ColorQuantize(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ColorQuantize.html</url>

    <dl>
      <dt>'ColorQuantize[$image$, $n$]'
      <dd>gives a version of $image$ using only $n$ colors.
    </dl>

    >> img = Import["ExampleData/hedy.tif"];
    >> ColorQuantize[img, 6]
     = -Image-

    #> ColorQuantize[img, 0]
     : Positive integer expected at position 2 in ColorQuantize[-Image-, 0].
     = ColorQuantize[-Image-, 0]
    #> ColorQuantize[img, -1]
     : Positive integer expected at position 2 in ColorQuantize[-Image-, -1].
     = ColorQuantize[-Image-, -1]
    """

    summary_text = "give an approximation to image that uses only n distinct colors"
    messages = {"intp": "Positive integer expected at position `2` in `1`."}

    def eval(self, image, n: Integer, evaluation: Evaluation):
        "ColorQuantize[image_Image, n_Integer]"
        py_value = n.value
        if py_value <= 0:
            evaluation.message(
                "ColorQuantize", "intp", Expression(SymbolColorQuantize, image, n), 2
            )
            return
        converted = image.color_convert("RGB")
        if converted is None:
            return
        pixels = pixels_as_ubyte(converted.pixels)
        im = PIL.Image.fromarray(pixels).quantize(py_value)
        im = im.convert("RGB")
        return Image(numpy.array(im), "RGB")


class ColorSeparate(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ColorSeparate.html</url>

    <dl>
      <dt>'ColorSeparate[$image$]'
      <dd>Gives each channel of $image$ as a separate grayscale image.
    </dl>

    >> img = Import["ExampleData/hedy.tif"];
    >> ColorSeparate[img]
     = ...

    """

    summary_text = "separate color channels"

    def eval(self, image: Image, evaluation: Evaluation):
        "ColorSeparate[image_]"
        images = []
        pixels = image.pixels
        if len(pixels.shape) < 3:
            images.append(pixels)
        else:
            for i in range(pixels.shape[2]):
                images.append(Image(pixels[:, :, i], "Grayscale"))
        return ListExpression(*images)


class Colorize(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Colorize.html</url>

    <dl>
      <dt>'Colorize[$values$]'
      <dd>returns an image where each number in the rectangular matrix \
          $values$ is a pixel and each occurrence of the same number is \
          displayed in the same unique color, which is different from the \
          colors of all non-identical numbers.

      <dt>'Colorize[$image$]'
      <dd>gives a colorized version of $image$.
    </dl>

    >> Colorize[{{1.3, 2.1, 1.5}, {1.3, 1.3, 2.1}, {1.3, 2.1, 1.5}}]
     = -Image-

    >> Colorize[{{1, 2}, {2, 2}, {2, 3}}, ColorFunction -> (Blend[{White, Blue}, #]&)]
     = -Image-
    """

    summary_text = "create pseudocolor images"
    options = {"ColorFunction": "Automatic"}

    messages = {
        "cfun": "`1` is neither a gradient ColorData nor a pure function suitable as ColorFunction."
    }

    def eval(self, values, evaluation, options):
        "Colorize[values_, OptionsPattern[%(name)s]]"

        if isinstance(values, Image):
            pixels = values.grayscale().pixels
            matrix = pixels_as_ubyte(pixels.reshape(pixels.shape[:2]))
        else:
            if not Expression(SymbolMatrixQ, values).evaluate(evaluation) is SymbolTrue:
                return
            matrix = matrix_to_numpy(values)

        a, n = linearize_numpy_array(matrix)
        # the maximum value for n is the number of pixels in a, which is acceptable and never too large.

        color_function = self.get_option(options, "ColorFunction", evaluation)
        if (
            isinstance(color_function, Symbol)
            and color_function.get_name() == "System`Automatic"
        ):
            color_function = String("LakeColors")

        from mathics.builtin.drawing.plot import gradient_palette

        cmap = gradient_palette(color_function, n, evaluation)
        if not cmap:
            evaluation.message("Colorize", "cfun", color_function)
            return

        s = (a.shape[0], a.shape[1], 1)
        p = numpy.transpose(numpy.array([cmap[i] for i in range(n)])[:, 0:3])
        return Image(
            numpy.concatenate([p[i][a].reshape(s) for i in range(3)], axis=2),
            color_space="RGB",
        )


class ImageColorSpace(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ImageColorSpace.html</url>

    <dl>
      <dt>'ImageColorSpace[$image$]'
      <dd>gives $image$'s color space, e.g. "RGB" or "CMYK".
    </dl>

    >> img = Import["ExampleData/MadTeaParty.gif"];
    >> ImageColorSpace[img]
     = Grayscale

    >> img = Import["ExampleData/sunflowers.jpg"];
    >> ImageColorSpace[img]
     = RGB
    """

    summary_text = "colorspace used in the image"

    def eval(self, image: Image, evaluation: Evaluation):
        "ImageColorSpace[image_Image]"
        return String(image.color_space)
