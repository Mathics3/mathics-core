# -*- coding: utf-8 -*-
# FIXME - move the rest into builtin.image
"""
Image[] and image-related functions

Note that you (currently) need scikit-image installed in order for this \
module to work.
"""

# This tells documentation how to sort this module
# Here, we are also hiding "drawing" since this erroneously appears at
# the top level.
sort_order = "mathics.builtin.image-and-image-related-functions"

import functools
import math
import os.path as osp
from collections import defaultdict

import numpy
import PIL

from mathics.builtin.base import Builtin, String
from mathics.builtin.colors.color_internals import colorspaces as known_colorspaces
from mathics.builtin.image.base import Image, _SkimageBuiltin
from mathics.core.atoms import Integer, Integer0, Integer1, MachineReal
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolDivide, SymbolNull, SymbolTrue
from mathics.core.systemsymbols import SymbolRule
from mathics.eval.image import (
    convolve,
    extract_exif,
    matrix_to_numpy,
    numpy_to_matrix,
    pixels_as_float,
    pixels_as_ubyte,
    pixels_as_uint,
)

SymbolColorQuantize = Symbol("ColorQuantize")
SymbolMatrixQ = Symbol("MatrixQ")
SymbolThreshold = Symbol("Threshold")

_skimage_requires = ("skimage", "scipy", "matplotlib", "networkx")

try:
    import skimage.filters
except ImportError:
    have_skimage_filters = False
else:
    have_skimage_filters = True

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


class GaussianFilter(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/GaussianFilter.html</url>

    <dl>
      <dt>'GaussianFilter[$image$, $r$]'
      <dd>blurs $image$ using a Gaussian blur filter of radius $r$.
    </dl>

    >> lena = Import["ExampleData/lena.tif"];
    >> GaussianFilter[lena, 2.5]
     = -Image-
    """

    summary_text = "apply a gaussian filter to an image"
    messages = {"only3": "GaussianFilter only supports up to three channels."}

    def eval_radius(self, image, radius, evaluation: Evaluation):
        "GaussianFilter[image_Image, radius_?RealNumberQ]"
        if len(image.pixels.shape) > 2 and image.pixels.shape[2] > 3:
            return evaluation.message("GaussianFilter", "only3")
        else:
            f = PIL.ImageFilter.GaussianBlur(radius.round_to_float())
            return image.filter(lambda im: im.filter(f))


# morphological image filters


class PillowImageFilter(Builtin):
    """

    ## <url>:PillowImageFilter:</url>

    <dl>
      <dt>'PillowImageFilter[$image$, "filtername"]'
      <dd> applies an image filter "filtername" from the pillow library.
    </dl>
    TODO: test cases?
    """

    summary_text = "apply a pillow filter to an image"

    def compute(self, image, f):
        return image.filter(lambda im: im.filter(f))


class MinFilter(PillowImageFilter):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/MinFilter.html</url>

    <dl>
    <dt>'MinFilter[$image$, $r$]'
      <dd>gives $image$ with a minimum filter of radius $r$ applied on it. This always
      picks the smallest value in the filter's area.
    </dl>

    >> lena = Import["ExampleData/lena.tif"];
    >> MinFilter[lena, 5]
     = -Image-
    """

    summary_text = "replace every pixel value by the minimum in a neighbourhood"

    def eval(self, image, r: Integer, evaluation: Evaluation):
        "MinFilter[image_Image, r_Integer]"
        return self.compute(image, PIL.ImageFilter.MinFilter(1 + 2 * r.value))


class MaxFilter(PillowImageFilter):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MaxFilter.html</url>

    <dl>
      <dt>'MaxFilter[$image$, $r$]'
      <dd>gives $image$ with a maximum filter of radius $r$ applied on it. This always \
          picks the largest value in the filter's area.
    </dl>

    >> lena = Import["ExampleData/lena.tif"];
    >> MaxFilter[lena, 5]
     = -Image-
    """

    summary_text = "replace every pixel value by the maximum in a neighbourhood"

    def eval(self, image, r: Integer, evaluation: Evaluation):
        "MaxFilter[image_Image, r_Integer]"
        return self.compute(image, PIL.ImageFilter.MaxFilter(1 + 2 * r.value))


class MedianFilter(PillowImageFilter):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MedianFilter.html</url>

    <dl>
      <dt>'MedianFilter[$image$, $r$]'
      <dd>gives $image$ with a median filter of radius $r$ applied on it. This always \
          picks the median value in the filter's area.
    </dl>

    >> lena = Import["ExampleData/lena.tif"];
    >> MedianFilter[lena, 5]
     = -Image-
    """

    summary_text = "replace every pixel value by the median in a neighbourhood"

    def eval(self, image, r: Integer, evaluation: Evaluation):
        "MedianFilter[image_Image, r_Integer]"
        return self.compute(image, PIL.ImageFilter.MedianFilter(1 + 2 * r.value))


class EdgeDetect(_SkimageBuiltin):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/EdgeDetect.html</url>

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


def _matrix(rows):
    return ListExpression(*[ListExpression(*r) for r in rows])


class BoxMatrix(Builtin):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/BoxMatrix.html</url>

    <dl>
    <dt>'BoxMatrix[$s]'
      <dd>Gives a box shaped kernel of size 2 $s$ + 1.
    </dl>

    >> BoxMatrix[3]
     = {{1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}}
    """

    summary_text = "create a matrix with all its entries set to 1"

    def eval(self, r, evaluation: Evaluation):
        "BoxMatrix[r_?RealNumberQ]"
        py_r = abs(r.round_to_float())
        s = int(math.floor(1 + 2 * py_r))
        return _matrix([[Integer1] * s] * s)


class DiskMatrix(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/DiskMatrix.html</url>

    <dl>
      <dt>'DiskMatrix[$s]'
      <dd>Gives a disk shaped kernel of size 2 $s$ + 1.
    </dl>

    >> DiskMatrix[3]
     = {{0, 0, 1, 1, 1, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {1, 1, 1, 1, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 1, 1, 1, 0, 0}}
    """

    summary_text = "create a matrix with 1 in a disk-shaped region, and 0 outside"

    def eval(self, r, evaluation: Evaluation):
        "DiskMatrix[r_?RealNumberQ]"
        py_r = abs(r.round_to_float())
        s = int(math.floor(0.5 + py_r))

        m = (Integer0, Integer1)
        r_sqr = (py_r + 0.5) * (py_r + 0.5)

        def rows():
            for y in range(-s, s + 1):
                yield [m[int((x) * (x) + (y) * (y) <= r_sqr)] for x in range(-s, s + 1)]

        return _matrix(rows())


class DiamondMatrix(Builtin):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/DiamondMatrix.html</url>

    <dl>
    <dt>'DiamondMatrix[$s]'
      <dd>Gives a diamond shaped kernel of size 2 $s$ + 1.
    </dl>

    >> DiamondMatrix[3]
     = {{0, 0, 0, 1, 0, 0, 0}, {0, 0, 1, 1, 1, 0, 0}, {0, 1, 1, 1, 1, 1, 0}, {1, 1, 1, 1, 1, 1, 1}, {0, 1, 1, 1, 1, 1, 0}, {0, 0, 1, 1, 1, 0, 0}, {0, 0, 0, 1, 0, 0, 0}}
    """

    summary_text = "create a matrix with 1 in a diamond-shaped region, and 0 outside"

    def eval(self, r, evaluation: Evaluation):
        "DiamondMatrix[r_?RealNumberQ]"
        py_r = abs(r.round_to_float())
        t = int(math.floor(0.5 + py_r))

        zero = Integer0
        one = Integer1

        def rows():
            for d in range(0, t):
                p = [zero] * (t - d)
                yield p + ([one] * (1 + d * 2)) + p

            yield [one] * (2 * t + 1)

            for d in reversed(range(0, t)):
                p = [zero] * (t - d)
                yield p + ([one] * (1 + d * 2)) + p

        return _matrix(rows())


class ImageConvolve(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ImageConvolve.html</url>

    <dl>
      <dt>'ImageConvolve[$image$, $kernel$]'
      <dd>Computes the convolution of $image$ using $kernel$.
    </dl>

    >> img = Import["ExampleData/lena.tif"];
    >> ImageConvolve[img, DiamondMatrix[5] / 61]
     = -Image-
    >> ImageConvolve[img, DiskMatrix[5] / 97]
     = -Image-
    >> ImageConvolve[img, BoxMatrix[5] / 121]
     = -Image-
    """

    summary_text = "give the convolution of image with kernel"

    def eval(self, image, kernel, evaluation: Evaluation):
        "%(name)s[image_Image, kernel_?MatrixQ]"
        numpy_kernel = matrix_to_numpy(kernel)
        pixels = pixels_as_float(image.pixels)
        shape = pixels.shape[:2]
        channels = []
        for c in (pixels[:, :, i] for i in range(pixels.shape[2])):
            channels.append(convolve(c.reshape(shape), numpy_kernel, fixed=True))
        return Image(numpy.dstack(channels), image.color_space)


class _MorphologyFilter(_SkimageBuiltin):

    messages = {
        "grayscale": "Your image has been converted to grayscale as color images are not supported yet."
    }

    rules = {"%(name)s[i_Image, r_?RealNumberQ]": "%(name)s[i, BoxMatrix[r]]"}

    def eval(self, image, k, evaluation: Evaluation):
        "%(name)s[image_Image, k_?MatrixQ]"
        if image.color_space != "Grayscale":
            image = image.grayscale()
            evaluation.message(self.get_name(), "grayscale")
        import skimage.morphology

        f = getattr(skimage.morphology, self.get_name(True).lower())
        shape = image.pixels.shape[:2]
        img = f(image.pixels.reshape(shape), matrix_to_numpy(k))
        return Image(img, "Grayscale")


class Dilation(_MorphologyFilter):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Dilation.html</url>

    <dl>
      <dt>'Dilation[$image$, $ker$]'
      <dd>Gives the morphological dilation of $image$ with respect to structuring element $ker$.
    </dl>

    >> ein = Import["ExampleData/Einstein.jpg"];
    >> Dilation[ein, 2.5]
     = -Image-
    """

    summary_text = "give the dilation with respect to a range-r square"


class Erosion(_MorphologyFilter):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Erosion.html</url>

    <dl>
      <dt>'Erosion[$image$, $ker$]'
      <dd>Gives the morphological erosion of $image$ with respect to structuring element $ker$.
    </dl>

    >> ein = Import["ExampleData/Einstein.jpg"];
    >> Erosion[ein, 2.5]
     = -Image-
    """

    summary_text = "give the erotion with respect to a range-r square"


class Opening(_MorphologyFilter):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Opening.html</url>

    <dl>
      <dt>'Opening[$image$, $ker$]'
      <dd>Gives the morphological opening of $image$ with respect to structuring element $ker$.
    </dl>

    >> ein = Import["ExampleData/Einstein.jpg"];
    >> Opening[ein, 2.5]
     = -Image-
    """

    summary_text = "get morphological opening regarding a kernel"


class Closing(_MorphologyFilter):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Closing.html</url>

    <dl>
      <dt>'Closing[$image$, $ker$]'
      <dd>Gives the morphological closing of $image$ with respect to structuring element $ker$.
    </dl>

    >> ein = Import["ExampleData/Einstein.jpg"];
    >> Closing[ein, 2.5]
     = -Image-
    """

    summary_text = "morphological closing regarding a kernel"


class MorphologicalComponents(_SkimageBuiltin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/MorphologicalComponents.html</url>

    <dl>
      <dt>'MorphologicalComponents[$image$]'
      <dd> Builds a 2-D array in which each pixel of $image$ is replaced \
           by an integer index representing the connected foreground image \
           component in which the pixel lies.

      <dt>'MorphologicalComponents[$image$, $threshold$]'
      <dd> consider any pixel with a value above $threshold$ as the foreground.
    </dl>
    """

    summary_text = "tag connected regions of similar colors"

    rules = {"MorphologicalComponents[i_Image]": "MorphologicalComponents[i, 0]"}

    def eval(self, image, t, evaluation: Evaluation):
        "MorphologicalComponents[image_Image, t_?RealNumberQ]"
        pixels = pixels_as_ubyte(
            pixels_as_float(image.grayscale().pixels) > t.round_to_float()
        )
        import skimage.measure

        return from_python(
            skimage.measure.label(pixels, background=0, connectivity=2).tolist()
        )


# color space


class ImageColorSpace(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ImageColorSpace.html</url>

    <dl>
      <dt>'ImageColorSpace[$image$]'
      <dd>gives $image$'s color space, e.g. "RGB" or "CMYK".
    </dl>

    >> img = Import["ExampleData/lena.tif"];
    >> ImageColorSpace[img]
     = RGB
    """

    summary_text = "colorspace used in the image"

    def eval(self, image, evaluation: Evaluation):
        "ImageColorSpace[image_Image]"
        return String(image.color_space)


class ColorQuantize(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ColorQuantize.html</url>

    <dl>
      <dt>'ColorQuantize[$image$, $n$]'
      <dd>gives a version of $image$ using only $n$ colors.
    </dl>

    >> img = Import["ExampleData/lena.tif"];
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
            return evaluation.message(
                "ColorQuantize", "intp", Expression(SymbolColorQuantize, image, n), 2
            )
        converted = image.color_convert("RGB")
        if converted is None:
            return
        pixels = pixels_as_ubyte(converted.pixels)
        im = PIL.Image.fromarray(pixels).quantize(py_value)
        im = im.convert("RGB")
        return Image(numpy.array(im), "RGB")


class Threshold(Builtin):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/Threshold.html</url>

    <dl>
      <dt>'Threshold[$image$]'
      <dd>gives a value suitable for binarizing $image$.
    </dl>

    The option "Method" may be "Cluster" (use Otsu's threshold), "Median", or "Mean".

    >> img = Import["ExampleData/lena.tif"];
    >> Threshold[img]
     = 0.456739
    X> Binarize[img, %]
     = -Image-
    X> Threshold[img, Method -> "Mean"]
     = 0.486458
    X> Threshold[img, Method -> "Median"]
     = 0.504726
    """

    summary_text = "estimate a threshold value for binarize an image"
    if have_skimage_filters:
        options = {"Method": '"Cluster"'}
    else:
        options = {"Method": '"Median"'}

    messages = {
        "illegalmethod": "Method `` is not supported.",
        "skimage": "Please install scikit-image to use Method -> Cluster.",
    }

    def eval(self, image, evaluation: Evaluation, options):
        "Threshold[image_Image, OptionsPattern[Threshold]]"
        pixels = image.grayscale().pixels

        method = self.get_option(options, "Method", evaluation)
        method_name = (
            method.get_string_value()
            if isinstance(method, String)
            else method.to_python()
        )
        if method_name == "Cluster":
            if not have_skimage_filters:
                evaluation.message("ImageResize", "skimage")
                return
            threshold = skimage.filters.threshold_otsu(pixels)
        elif method_name == "Median":
            threshold = numpy.median(pixels)
        elif method_name == "Mean":
            threshold = numpy.mean(pixels)
        else:
            return evaluation.message("Threshold", "illegalmethod", method)

        return MachineReal(float(threshold))


class Binarize(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Binarize.html</url>

    <dl>
      <dt>'Binarize[$image$]'
      <dd>gives a binarized version of $image$, in which each pixel is either 0 or 1.

      <dt>'Binarize[$image$, $t$]'
      <dd>map values $x$ > $t$ to 1, and values $x$ <= $t$ to 0.

      <dt>'Binarize[$image$, {$t1$, $t2$}]'
      <dd>map $t1$ < $x$ < $t2$ to 1, and all other values to 0.
    </dl>

    S> img = Import["ExampleData/lena.tif"];
    S> Binarize[img]
     = -Image-
    S> Binarize[img, 0.7]
     = -Image-
    S> Binarize[img, {0.2, 0.6}]
     = -Image-
    """

    summary_text = "create a binarized image"

    def eval(self, image, evaluation: Evaluation):
        "Binarize[image_Image]"
        image = image.grayscale()
        thresh = (
            Expression(SymbolThreshold, image).evaluate(evaluation).round_to_float()
        )
        if thresh is not None:
            return Image(image.pixels > thresh, "Grayscale")

    def eval_t(self, image, t, evaluation: Evaluation):
        "Binarize[image_Image, t_?RealNumberQ]"
        pixels = image.grayscale().pixels
        return Image(pixels > t.round_to_float(), "Grayscale")

    def eval_t1_t2(self, image, t1, t2, evaluation: Evaluation):
        "Binarize[image_Image, {t1_?RealNumberQ, t2_?RealNumberQ}]"
        pixels = image.grayscale().pixels
        mask1 = pixels > t1.round_to_float()
        mask2 = pixels < t2.round_to_float()
        return Image(mask1 * mask2, "Grayscale")


class ColorSeparate(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ColorSeparate.html</url>

    <dl>
      <dt>'ColorSeparate[$image$]'
      <dd>Gives each channel of $image$ as a separate grayscale image.
    </dl>
    """

    summary_text = "separate color channels"

    def eval(self, image, evaluation: Evaluation):
        "ColorSeparate[image_Image]"
        images = []
        pixels = image.pixels
        if len(pixels.shape) < 3:
            images.append(pixels)
        else:
            for i in range(pixels.shape[2]):
                images.append(Image(pixels[:, :, i], "Grayscale"))
        return ListExpression(*images)


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


def _linearize(a):
    # this uses a vectorized binary search to compute
    # strictly sequential indices for all values in a.

    orig_shape = a.shape
    a = a.reshape((functools.reduce(lambda x, y: x * y, a.shape),))  # 1 dimension

    u = numpy.unique(a)
    n = len(u)

    lower = numpy.ndarray(a.shape, dtype=int)
    lower.fill(0)
    upper = numpy.ndarray(a.shape, dtype=int)
    upper.fill(n - 1)

    h = numpy.sort(u)
    q = n  # worst case partition size

    while q > 2:
        m = numpy.right_shift(lower + upper, 1)
        f = a <= h[m]
        # (lower, m) vs (m + 1, upper)
        lower = numpy.where(f, lower, m + 1)
        upper = numpy.where(f, m, upper)
        q = (q + 1) // 2

    return numpy.where(a == h[lower], lower, upper).reshape(orig_shape), n


class Colorize(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Colorize.html</url>

    <dl>
      <dt>'Colorize[$values$]'
      <dd>returns an image where each number in the rectangular matrix \
          $values$ is a pixel and each occurence of the same number is \
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

        a, n = _linearize(matrix)
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


# pixel access


class ImageData(Builtin):
    """

    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ImageData.html</url>

    <dl>
      <dt>'ImageData[$image$]'
      <dd>gives a list of all color values of $image$ as a matrix.

      <dt>'ImageData[$image$, $stype$]'
      <dd>gives a list of color values in type $stype$.
    </dl>

    >> img = Image[{{0.2, 0.4}, {0.9, 0.6}, {0.5, 0.8}}];
    >> ImageData[img]
     = {{0.2, 0.4}, {0.9, 0.6}, {0.5, 0.8}}

    >> ImageData[img, "Byte"]
     = {{51, 102}, {229, 153}, {127, 204}}

    >> ImageData[Image[{{0, 1}, {1, 0}, {1, 1}}], "Bit"]
     = {{0, 1}, {1, 0}, {1, 1}}

    #> ImageData[img, "Bytf"]
     : Unsupported pixel format "Bytf".
     = ImageData[-Image-, Bytf]
    """

    messages = {"pixelfmt": 'Unsupported pixel format "``".'}

    rules = {"ImageData[image_Image]": 'ImageData[image, "Real"]'}
    summary_text = "the array of pixel values from an image"

    def eval(self, image, stype: String, evaluation: Evaluation):
        "ImageData[image_Image, stype_String]"
        pixels = image.pixels
        stype = stype.value
        if stype == "Real":
            pixels = pixels_as_float(pixels)
        elif stype == "Byte":
            pixels = pixels_as_ubyte(pixels)
        elif stype == "Bit16":
            pixels = pixels_as_uint(pixels)
        elif stype == "Bit":
            pixels = pixels.astype(int)
        else:
            return evaluation.message("ImageData", "pixelfmt", stype)
        return from_python(numpy_to_matrix(pixels))


class PixelValuePositions(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/PixelValuePositions.html</url>

    <dl>
      <dt>'PixelValuePositions[$image$, $val$]'
      <dd>gives the positions of all pixels in $image$ that have value $val$.
    </dl>

    >> PixelValuePositions[Image[{{0, 1}, {1, 0}, {1, 1}}], 1]
     = {{1, 1}, {1, 2}, {2, 1}, {2, 3}}

    >> PixelValuePositions[Image[{{0.2, 0.4}, {0.9, 0.6}, {0.3, 0.8}}], 0.5, 0.15]
     = {{2, 2}, {2, 3}}

    >> img = Import["ExampleData/lena.tif"];
    >> PixelValuePositions[img, 3 / 255, 0.5 / 255]
     = {{180, 192, 2}, {181, 192, 2}, {181, 193, 2}, {188, 204, 2}, {265, 314, 2}, {364, 77, 2}, {365, 72, 2}, {365, 73, 2}, {365, 77, 2}, {366, 70, 2}, {367, 65, 2}}
    >> PixelValue[img, {180, 192}]
     = {0.25098, 0.0117647, 0.215686}
    """

    rules = {
        "PixelValuePositions[image_Image, val_?RealNumberQ]": "PixelValuePositions[image, val, 0]"
    }

    summary_text = "list the position of pixels with a given value"

    def eval(self, image, val, d, evaluation: Evaluation):
        "PixelValuePositions[image_Image, val_?RealNumberQ, d_?RealNumberQ]"
        val = val.round_to_float()
        d = d.round_to_float()

        positions = numpy.argwhere(
            numpy.isclose(pixels_as_float(image.pixels), val, atol=d, rtol=0)
        )

        # python indexes from 0 at top left -> indices from 1 starting at bottom left
        # if single channel then ommit channel indices
        height = image.pixels.shape[0]
        if image.pixels.shape[2] == 1:
            result = sorted((j + 1, height - i) for i, j, k in positions.tolist())
        else:
            result = sorted(
                (j + 1, height - i, k + 1) for i, j, k in positions.tolist()
            )
        return ListExpression(
            *(to_mathics_list(*arg, elements_conversion_fn=Integer) for arg in result)
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
