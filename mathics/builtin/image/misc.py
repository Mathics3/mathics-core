# -*- coding: utf-8 -*-
# FIXME - plit out rest:
# Color Manipulation, etc.
"""
Miscellaneous image-related functions
"""

# This tells documentation how to sort this module
# Here, we are also hiding "drawing" since this erroneously appears at
# the top level.
sort_order = "mathics.builtin.image-and-image-related-functions"

import os.path as osp
from collections import defaultdict

import numpy
import PIL

from mathics.builtin.base import Builtin, String
from mathics.builtin.image.base import Image, _SkimageBuiltin
from mathics.core.atoms import Integer
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolDivide, SymbolNull
from mathics.core.systemsymbols import SymbolRule
from mathics.eval.image import extract_exif

_skimage_requires = ("skimage", "scipy", "matplotlib", "networkx")

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
            return evaluation.message("ImageExport", "noimage")


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
    >> Import["ExampleData/lena.tif"]
     = -Image-
    """

    no_doc = True

    def eval(self, path: String, evaluation: Evaluation):
        """ImageImport[path_String]"""
        pillow = PIL.Image.open(path.value)
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
            return evaluation.message("RandomImage", "bddim", from_python(size))
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
            return evaluation.message("RandomImage", "imgcstype", color_space)
        return Image(data, cs)


class EdgeDetect(_SkimageBuiltin):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/EdgeDetect.html</url>

    <dl>
      <dt>'EdgeDetect[$image$]'
      <dd>returns an image showing the edges in $image$.
    </dl>

    >> lena = Import["ExampleData/lena.tif"];
    >> EdgeDetect[lena]
     = -Image-
    >> EdgeDetect[lena, 5]
     = -Image-
    >> EdgeDetect[lena, 4, 0.5]
     = -Image-
    """

    summary_text = "detect edges in an image using Canny and other methods"
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


# image attribute queries


class ImageDimensions(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ImageDimensions.html</url>

    <dl>
      <dt>'ImageDimensions[$image$]'
      <dd>Returns the dimensions {$width$, $height$} of $image$ in pixels.
    </dl>

    >> lena = Import["ExampleData/lena.tif"];
    >> ImageDimensions[lena]
     = {512, 512}

    >> ImageDimensions[RandomImage[1, {50, 70}]]
     = {50, 70}
    """

    summary_text = "get the pixel dimensions of an image"

    def eval(self, image, evaluation: Evaluation):
        "ImageDimensions[image_Image]"
        return to_mathics_list(*image.dimensions(), elements_conversion_fn=Integer)


class ImageAspectRatio(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ImageAspectRatio.html</url>

    <dl>
      <dt>'ImageAspectRatio[$image$]'
      <dd>gives the aspect ratio of $image$.
    </dl>

    >> img = Import["ExampleData/lena.tif"];
    >> ImageAspectRatio[img]
     = 1

    >> ImageAspectRatio[Image[{{0, 1}, {1, 0}, {1, 1}}]]
     = 3 / 2
    """

    summary_text = "give the ratio of height to width of an image"

    def eval(self, image, evaluation: Evaluation):
        "ImageAspectRatio[image_Image]"
        dim = image.dimensions()
        return Expression(SymbolDivide, Integer(dim[1]), Integer(dim[0]))


class ImageChannels(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ImageChannels.html</url>

    <dl>
    <dt>'ImageChannels[$image$]'
      <dd>gives the number of channels in $image$.
    </dl>

    >> ImageChannels[Image[{{0, 1}, {1, 0}}]]
     = 1

    >> img = Import["ExampleData/lena.tif"];
    >> ImageChannels[img]
     = 3
    """

    summary_text = "get number of channels present in the data for an image"

    def eval(self, image, evaluation: Evaluation):
        "ImageChannels[image_Image]"
        return Integer(image.channels())


class ImageType(Builtin):
    """
    <url>
    :WMA link:https://reference.wolfram.com/language/ref/ImageType.html</url>

    <dl>
      <dt>'ImageType[$image$]'
      <dd>gives the interval storage type of $image$, e.g. "Real", "Bit32", or "Bit".
    </dl>

    >> img = Import["ExampleData/lena.tif"];
    >> ImageType[img]
     = Byte

    >> ImageType[Image[{{0, 1}, {1, 0}}]]
     = Real

    X> ImageType[Binarize[img]]
     = Bit

    """

    summary_text = "type of values used for each pixel element in an image"

    def eval(self, image, evaluation: Evaluation):
        "ImageType[image_Image]"
        return String(image.storage_type())


# complex operations


class TextRecognize(Builtin):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/TextRecognize.html</url>

    <dl>
      <dt>'TextRecognize[{$image$}]'
      <dd>Recognizes text in $image$ and returns it as string.
    </dl>
    """

    messages = {
        "tool": "No text recognition tools were found in the paths available to the Mathics kernel.",
        "langinv": "No language data for `1` is available.",
        "lang": "Language `1` is not supported in your installation of `2`. Please install it.",
    }

    options = {"Language": '"English"'}

    requires = "pyocr"

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


class WordCloud(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/WordCloud.html</url>

    <dl>
      <dt>'WordCloud[{$word1$, $word2$, ...}]'
      <dd>Gives a word cloud with the given list of words.

      <dt>'WordCloud[{$weight1$ -> $word1$, $weight2$ -> $word2$, ...}]'
      <dd>Gives a word cloud with the words weighted using the given weights.

      <dt>'WordCloud[{$weight1$, $weight2$, ...} -> {$word1$, $word2$, ...}]'
      <dd>Also gives a word cloud with the words weighted using the given weights.

      <dt>'WordCloud[{{$word1$, $weight1$}, {$word2$, $weight2$}, ...}]'
      <dd>Gives a word cloud with the words weighted using the given weights.
    </dl>

    >> WordCloud[StringSplit[Import["ExampleData/EinsteinSzilLetter.txt", CharacterEncoding->"UTF8"]]]
     = -Image-

    >> WordCloud[Range[50] -> ToString /@ Range[50]]
     = -Image-
    """

    # this is the palettable.colorbrewer.qualitative.Dark2_8 palette
    default_colors = (
        (27, 158, 119),
        (217, 95, 2),
        (117, 112, 179),
        (231, 41, 138),
        (102, 166, 30),
        (230, 171, 2),
        (166, 118, 29),
        (102, 102, 102),
    )

    options = {
        "IgnoreCase": "True",
        "ImageSize": "Automatic",
        "MaxItems": "Automatic",
    }

    requires = ("wordcloud",)

    summary_text = "show a word cloud from a list of words"

    def eval_words_weights(self, weights, words, evaluation, options):
        "WordCloud[weights_List -> words_List, OptionsPattern[%(name)s]]"
        if len(weights.elements) != len(words.elements):
            return

        def weights_and_words():
            for weight, word in zip(weights.elements, words.elements):
                yield weight.round_to_float(), word.get_string_value()

        return self._word_cloud(weights_and_words(), evaluation, options)

    def eval_words(self, words, evaluation, options):
        "WordCloud[words_List, OptionsPattern[%(name)s]]"

        if not words:
            return
        elif isinstance(words.elements[0], String):

            def weights_and_words():
                for word in words.elements:
                    yield 1, word.get_string_value()

        else:

            def weights_and_words():
                for word in words.elements:
                    if len(word.elements) != 2:
                        raise ValueError

                    head_name = word.get_head_name()
                    if head_name == "System`Rule":
                        weight, s = word.elements
                    elif head_name == "System`List":
                        s, weight = word.elements
                    else:
                        raise ValueError

                    yield weight.round_to_float(), s.get_string_value()

        try:
            return self._word_cloud(weights_and_words(), evaluation, options)
        except ValueError:
            return

    def _word_cloud(self, words, evaluation, options):
        ignore_case = self.get_option(options, "IgnoreCase", evaluation) is Symbol(
            "True"
        )

        freq = defaultdict(int)
        for py_weight, py_word in words:
            if py_word is None or py_weight is None:
                return
            key = py_word.lower() if ignore_case else py_word
            freq[key] += py_weight

        max_items = self.get_option(options, "MaxItems", evaluation)
        if isinstance(max_items, Integer):
            py_max_items = max_items.get_int_value()
        else:
            py_max_items = 200

        image_size = self.get_option(options, "ImageSize", evaluation)
        if image_size is Symbol("Automatic"):
            py_image_size = (800, 600)
        elif (
            image_size.get_head_name() == "System`List"
            and len(image_size.elements) == 2
        ):
            py_image_size = []
            for element in image_size.elements:
                if not isinstance(element, Integer):
                    return
                py_image_size.append(element.get_int_value())
        elif isinstance(image_size, Integer):
            size = image_size.get_int_value()
            py_image_size = (size, size)
        else:
            return

        # inspired by http://minimaxir.com/2016/05/wordclouds/
        import random

        def color_func(
            word, font_size, position, orientation, random_state=None, **kwargs
        ):
            return self.default_colors[random.randint(0, 7)]

        font_base_path = osp.join(osp.dirname(osp.abspath(__file__)), "..", "fonts")

        font_path = osp.realpath(font_base_path + "AmaticSC-Bold.ttf")
        if not osp.exists(font_path):
            font_path = None

        from wordcloud import WordCloud

        wc = WordCloud(
            width=py_image_size[0],
            height=py_image_size[1],
            font_path=font_path,
            max_font_size=300,
            mode="RGB",
            background_color="white",
            max_words=py_max_items,
            color_func=color_func,
            random_state=42,
            stopwords=set(),
        )
        wc.generate_from_frequencies(freq)

        image = wc.to_image()
        return Image(numpy.array(image), "RGB")
