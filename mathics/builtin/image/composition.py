"""
Image Compositions
"""
import numpy

from mathics.builtin.base import Builtin
from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer, Rational, Real
from mathics.core.evaluation import Evaluation
from mathics.eval.image import pixels_as_float


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
            return evaluation.message(self.get_name(), "bddarg", arg)
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

    >> lena = Import["ExampleData/lena.tif"];
    >> noise = RandomImage[{-0.2, 0.2}, ImageDimensions[lena], ColorSpace -> "RGB"];
    >> ImageAdd[noise, lena]
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


# TODO: ImageAssemble, ImageCollage, ImageCompose
