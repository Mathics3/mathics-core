"""
Image Compositions
"""
import os.path as osp
from collections import defaultdict

import numpy

from mathics.builtin.base import Builtin, String
from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer, Rational, Real
from mathics.core.evaluation import Evaluation
from mathics.core.symbols import Symbol
from mathics.eval.image import pixels_as_float

# This tells documentation how to sort this module
sort_order = "mathics.builtin.image.image-compositions"


class _ImageArithmetic(Builtin):
    messages = {"bddarg": "Expecting a number, image, or graphics instead of `1`."}

    @staticmethod
    def convert_Image(image):
        assert isinstance(image, Image)
        return pixels_as_float(image.pixels)

    @staticmethod
    def convert_args(*args):
        images = []
        for arg in args:
            if isinstance(arg, Image):
                images.append(_ImageArithmetic.convert_Image(arg))
            elif isinstance(arg, (Integer, Rational, Real)):
                images.append(float(arg.to_python()))
            else:
                return None, arg
        return images, None

    @staticmethod
    def _reduce(iterable, ufunc):
        result = None
        for i in iterable:
            if result is None:
                # ufunc is destructive so copy first
                result = numpy.copy(i)
            else:
                # e.g. result *= i
                ufunc(result, i, result)
        return result

    def eval(self, image, args, evaluation: Evaluation):
        "%(name)s[image_Image, args__]"
        images, arg = self.convert_args(image, *args.get_sequence())
        if images is None:
            evaluation.message(self.get_name(), "bddarg", arg)
            return
        ufunc = getattr(numpy, self.get_name(True)[5:].lower())
        result = self._reduce(images, ufunc).clip(0, 1)
        return Image(result, image.color_space)


class ImageAdd(_ImageArithmetic):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ImageAdd.html</url>

    <dl>
      <dt>'ImageAdd[$image$, $expr_1$, $expr_2$, ...]'
      <dd>adds all $expr_i$ to $image$ where each $expr_i$ must be an image \
          or a real number.
    </dl>

    >> i = Image[{{0, 0.5, 0.2, 0.1, 0.9}, {1.0, 0.1, 0.3, 0.8, 0.6}}];

    >> ImageAdd[i, 0.5]
     = -Image-

    >> ImageAdd[i, i]
     = -Image-

    #> ImageAdd[i, 0.2, i, 0.1]
     = -Image-

    #> ImageAdd[i, x]
     : Expecting a number, image, or graphics instead of x.
     = ImageAdd[-Image-, x]

    >> ein = Import["ExampleData/Einstein.jpg"];
    >> noise = RandomImage[{-0.1, 0.1}, ImageDimensions[ein]];
    >> ImageAdd[noise, ein]
     = -Image-

    >> hedy = Import["ExampleData/hedy.tif"];
    >> noise = RandomImage[{-0.2, 0.2}, ImageDimensions[hedy], ColorSpace -> "RGB"];
    >> ImageAdd[noise, hedy]
     = -Image-
    """

    summary_text = "build an image adding pixel values of another image "


class ImageMultiply(_ImageArithmetic):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ImageMultiply.html</url>

    <dl>
      <dt>'ImageMultiply[$image$, $expr_1$, $expr_2$, ...]'
      <dd>multiplies all $expr_i$ with $image$ where each $expr_i$ must be an image or a real number.
    </dl>

    >> i = Image[{{0, 0.5, 0.2, 0.1, 0.9}, {1.0, 0.1, 0.3, 0.8, 0.6}}];

    >> ImageMultiply[i, 0.2]
     = -Image-

    >> ImageMultiply[i, i]
     = -Image-

    #> ImageMultiply[i, 0.2, i, 0.1]
     = -Image-

    #> ImageMultiply[i, x]
     : Expecting a number, image, or graphics instead of x.
     = ImageMultiply[-Image-, x]

    S> ein = Import["ExampleData/Einstein.jpg"];
    S> noise = RandomImage[{0.7, 1.3}, ImageDimensions[ein]];
    S> ImageMultiply[noise, ein]
     = -Image-
    """

    summary_text = "build an image multiplying the pixel values of another image "


class ImageSubtract(_ImageArithmetic):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ImageSubtract.html</url>

    <dl>
      <dt>'ImageSubtract[$image$, $expr_1$, $expr_2$, ...]'
      <dd>subtracts all $expr_i$ from $image$ where each $expr_i$ must be an \
          image or a real number.
    </dl>

    >> i = Image[{{0, 0.5, 0.2, 0.1, 0.9}, {1.0, 0.1, 0.3, 0.8, 0.6}}];

    >> ImageSubtract[i, 0.2]
     = -Image-

    >> ImageSubtract[i, i]
     = -Image-

    #> ImageSubtract[i, 0.2, i, 0.1]
     = -Image-

    #> ImageSubtract[i, x]
     : Expecting a number, image, or graphics instead of x.
     = ImageSubtract[-Image-, x]
    """

    summary_text = "build an image substracting pixel values of another image "


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


# TODO:
# ImageAssemble,
# Collage Creation other than WordCloud
# ImageCompose
