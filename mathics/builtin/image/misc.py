# -*- coding: utf-8 -*-
# FIXME - split out rest:
# Color Manipulation, etc.
"""
Miscellaneous image-related functions
"""

import numpy
import PIL

from mathics.builtin.base import Builtin, String
from mathics.builtin.image.base import Image, skimage_requires
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolNull
from mathics.core.systemsymbols import SymbolFailed, SymbolRule
from mathics.eval.image import extract_exif

# The following classes are used to allow inclusion of
# Builtin Functions only when certain Python packages
# are available. They do this by setting the `requires` class variable.


# Code related to Mathics Functions that import and export.


class ImageExport(Builtin):
    """
    <dl>
      <dt> 'ImageExport["path", $image$]'
      <dd> export $image$ as file in "path".
    </dl>
    """

    no_doc = True

    messages = {"noimage": "only an Image[] can be exported into an image file"}

    def eval(self, path: String, expr, opts, evaluation: Evaluation):
        """ImageExport[path_String, expr_, opts___]"""
        if isinstance(expr, Image):
            expr.pil().save(path.value)
            return SymbolNull
        else:
            evaluation.message("ImageExport", "noimage")
            return


class ImageImport(Builtin):
    """
    <dl>
      <dt> 'ImageImport["path"]'
      <dd> import an image from the file "path".
    </dl>

    ## Image
    >> Import["ExampleData/Einstein.jpg"]
     = -Image-
    >> Import["ExampleData/sunflowers.jpg"]
     = -Image-
    >> Import["ExampleData/MadTeaParty.gif"]
     = -Image-
    >> Import["ExampleData/moon.tif"]
     = -Image-
    >> Import["ExampleData/hedy.tif"]
     = -Image-
    """

    messages = {
        "infer": "Cannot infer format of file `1`.",
        "imgmisc": "PIL error: `1`.",
    }

    no_doc = True

    def eval(self, path: String, evaluation: Evaluation):
        """ImageImport[path_String]"""
        try:
            pillow = PIL.Image.open(path.value)
        except PIL.UnidentifiedImageError:
            evaluation.message("ImageImport", "infer", path)
            return SymbolFailed
        except Exception as e:
            evaluation.message("ImageImport", "imgmisc", str(e))
            return SymbolFailed

        pixels = numpy.asarray(pillow)
        is_rgb = len(pixels.shape) >= 3 and pixels.shape[2] >= 3
        options_from_exif = extract_exif(pillow, evaluation)

        image = Image(pixels, "RGB" if is_rgb else "Grayscale", pillow=pillow)
        image_list_expression = [
            Expression(SymbolRule, String("Image"), image),
            Expression(SymbolRule, String("ColorSpace"), String(image.color_space)),
        ]

        if options_from_exif is not None:
            image_list_expression.append(options_from_exif)

        return ListExpression(*image_list_expression)


class RandomImage(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/RandomImage.html</url>

    <dl>
      <dt>'RandomImage[$max$]'
      <dd>creates an image of random pixels with values 0 to $max$.

      <dt>'RandomImage[{$min$, $max$}]'
      <dd>creates an image of random pixels with values $min$ to $max$.

      <dt>'RandomImage[..., $size$]'
      <dd>creates an image of the given $size$.
    </dl>

    >> RandomImage[1, {100, 100}]
     = -Image-

    #> RandomImage[0.5]
     = -Image-
    #> RandomImage[{0.1, 0.9}]
     = -Image-
    #> RandomImage[0.9, {400, 600}]
     = -Image-
    #> RandomImage[{0.1, 0.5}, {400, 600}]
     = -Image-

    #> RandomImage[{0.1, 0.5}, {400, 600}, ColorSpace -> "RGB"]
     = -Image-
    """

    options = {"ColorSpace": "Automatic"}

    messages = {
        "bddim": "The specified dimension `1` should be a pair of positive integers.",
        "imgcstype": "`1` is an invalid color space specification.",
    }
    rules = {
        "RandomImage[]": "RandomImage[{0, 1}, {150, 150}]",
        "RandomImage[max_?RealNumberQ]": "RandomImage[{0, max}, {150, 150}]",
        "RandomImage[{minval_?RealNumberQ, maxval_?RealNumberQ}]": "RandomImage[{minval, maxval}, {150, 150}]",
        "RandomImage[max_?RealNumberQ, {w_Integer, h_Integer}]": "RandomImage[{0, max}, {w, h}]",
    }
    summary_text = "build an image with random pixels"

    def eval(self, minval, maxval, w, h, evaluation, options):
        "RandomImage[{minval_?RealNumberQ, maxval_?RealNumberQ}, {w_Integer, h_Integer}, OptionsPattern[RandomImage]]"
        color_space = self.get_option(options, "ColorSpace", evaluation)
        if (
            isinstance(color_space, Symbol)
            and color_space.get_name() == "System`Automatic"
        ):
            cs = "Grayscale"
        else:
            cs = color_space.get_string_value()
        size = [w.value, h.value]
        if size[0] <= 0 or size[1] <= 0:
            evaluation.message("RandomImage", "bddim", from_python(size))
            return
        minrange, maxrange = minval.round_to_float(), maxval.round_to_float()

        if cs == "Grayscale":
            data = (
                numpy.random.rand(size[1], size[0]) * (maxrange - minrange) + minrange
            )
        elif cs == "RGB":
            data = (
                numpy.random.rand(size[1], size[0], 3) * (maxrange - minrange)
                + minrange
            )
        else:
            evaluation.message("RandomImage", "imgcstype", color_space)
            return
        return Image(data, cs)


class EdgeDetect(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/EdgeDetect.html</url>

    <dl>
      <dt>'EdgeDetect[$image$]'
      <dd>returns an image showing the edges in $image$.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> EdgeDetect[hedy]
     = -Image-
    >> EdgeDetect[hedy, 5]
     = -Image-
    >> EdgeDetect[hedy, 4, 0.5]
     = -Image-
    """

    summary_text = "detect edges in an image using Canny and other methods"
    requires = skimage_requires

    rules = {
        "EdgeDetect[i_Image]": "EdgeDetect[i, 2, 0.2]",
        "EdgeDetect[i_Image, r_?RealNumberQ]": "EdgeDetect[i, r, 0.2]",
    }

    def eval(self, image, r, t, evaluation: Evaluation):
        "EdgeDetect[image_Image, r_?RealNumberQ, t_?RealNumberQ]"
        import skimage.feature

        pixels = image.grayscale().pixels
        return Image(
            skimage.feature.canny(
                pixels.reshape(pixels.shape[:2]),
                sigma=r.round_to_float() / 2,
                low_threshold=0.5 * t.round_to_float(),
                high_threshold=t.round_to_float(),
            ),
            "Grayscale",
        )


class TextRecognize(Builtin):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/TextRecognize.html</url>

    <dl>
      <dt>'TextRecognize[$image$]'
      <dd>Recognizes text in $image$ and returns it as a 'String'.
    </dl>

    >> textimage = Import["ExampleData/TextRecognize.png"]
     = -Image-

    >> TextRecognize[textimage]
     = TextRecognize[ image]
     .
     . Recognizes text in image and returns it as a String.
    """

    messages = {
        "tool": "No text recognition tools were found in the paths available to the Mathics kernel.",
        "langinv": "No language data for `1` is available.",
        "lang": "Language `1` is not supported in your installation of `2`. Please install it.",
    }

    options = {"Language": '"English"'}

    requires = ("pyocr",)

    summary_text = "recognize text in an image"

    def eval(self, image, evaluation, options):
        "TextRecognize[image_Image, OptionsPattern[%(name)s]]"
        import pyocr

        from mathics.builtin.codetables import iso639_3

        language = self.get_option(options, "Language", evaluation)
        if not isinstance(language, String):
            return
        py_language = language.get_string_value()
        py_language_code = iso639_3.get(py_language)

        if py_language_code is None:
            evaluation.message("TextRecognize", "langcode", py_language)
            return

        tools = pyocr.get_available_tools()
        if not tools:
            evaluation.message("TextRecognize", "tool")
            return
        best_tool = tools[0]

        langs = best_tool.get_available_languages()
        if py_language_code not in langs:
            # if we use Tesseract, then this means copying the necessary language files from
            # https://github.com/tesseract-ocr/tessdatainstalling to tessdata, which is
            # usually located at /usr/share/tessdata or similar, but there's no API to query
            # the exact location, so we cannot, for now, give a better message.

            evaluation.message(
                "TextRecognize", "lang", py_language, best_tool.get_name()
            )
            return

        import pyocr.builders

        text = best_tool.image_to_string(
            image.pil(), lang=py_language_code, builder=pyocr.builders.TextBuilder()
        )

        if isinstance(text, (list, tuple)):
            text = "\n".join(text)

        return String(text)


# TODO:
#  Computer Vision outside TextRecognize
#  Feature Detection routines other than EdgeDetect
