"""
Basic Image Processing
"""

import numpy
import PIL

from mathics.builtin.base import Builtin, String
from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer, MachineReal
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.eval.image import pixels_as_float

try:
    import skimage.filters
except ImportError:
    have_skimage_filters = False
else:
    have_skimage_filters = True


class Blur(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/Blur.html</url>

    <dl>
      <dt>'Blur[$image$]'
      <dd>gives a blurred version of $image$.

      <dt>'Blur[$image$, $r$]'
      <dd>blurs $image$ with a kernel of size $r$.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> Blur[hedy]
     = -Image-
    >> Blur[hedy, 5]
     = -Image-
    """

    summary_text = "blur an image"
    rules = {
        "Blur[image_Image]": "Blur[image, 2]",
        "Blur[image_Image, r_?RealNumberQ]": "ImageConvolve[image, BoxMatrix[r] / Total[Flatten[BoxMatrix[r]]]]",
    }


class ImageAdjust(Builtin):
    """

    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ImageAdjust.html</url>

    <dl>
      <dt>'ImageAdjust[$image$]'
      <dd>adjusts the levels in $image$.

      <dt>'ImageAdjust[$image$, $c$]'
      <dd>adjusts the contrast in $image$ by $c$.

      <dt>'ImageAdjust[$image$, {$c$, $b$}]'
      <dd>adjusts the contrast $c$, and brightness $b$ in $image$.

      <dt>'ImageAdjust[$image$, {$c$, $b$, $g$}]'
      <dd>adjusts the contrast $c$, brightness $b$, and gamma $g$ in $image$.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> ImageAdjust[hedy]
     = -Image-
    """

    summary_text = "adjust levels, brightness, contrast, gamma, etc"
    rules = {
        "ImageAdjust[image_Image, c_?RealNumberQ]": "ImageAdjust[image, {c, 0, 1}]",
        "ImageAdjust[image_Image, {c_?RealNumberQ, b_?RealNumberQ}]": "ImageAdjust[image, {c, b, 1}]",
    }

    def eval_auto(self, image, evaluation: Evaluation):
        "ImageAdjust[image_Image]"
        pixels = pixels_as_float(image.pixels)

        # channel limits
        axis = (0, 1)
        cmaxs, cmins = pixels.max(axis=axis), pixels.min(axis=axis)

        # normalise channels
        scales = cmaxs - cmins
        if not scales.shape:
            scales = numpy.array([scales])
        scales[scales == 0.0] = 1
        pixels -= cmins
        pixels /= scales
        return Image(pixels, image.color_space)

    def eval_contrast_brightness_gamma(self, image, c, b, g, evaluation: Evaluation):
        "ImageAdjust[image_Image, {c_?RealNumberQ, b_?RealNumberQ, g_?RealNumberQ}]"

        im = image.pil()

        # gamma
        g = g.round_to_float()
        if g != 1:
            im = PIL.ImageEnhance.Color(im).enhance(g)

        # brightness
        b = b.round_to_float()
        if b != 0:
            im = PIL.ImageEnhance.Brightness(im).enhance(b + 1)

        # contrast
        c = c.round_to_float()
        if c != 0:
            im = PIL.ImageEnhance.Contrast(im).enhance(c + 1)

        return Image(numpy.array(im), image.color_space)


class ImagePartition(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ImagePartition.html</url>

    <dl>
      <dt>'ImagePartition[$image$, $s$]'
      <dd>Partitions an image into an array of $s$ x $s$ pixel subimages.

      <dt>'ImagePartition[$image$, {$w$, $h$}]'
      <dd>Partitions an image into an array of $w$ x $h$ pixel subimages.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> ImageDimensions[hedy]
     = {646, 800}
    >> ImagePartition[hedy, 256]
     = {{-Image-, -Image-}, {-Image-, -Image-}, {-Image-, -Image-}}

    >> ImagePartition[hedy, {512, 128}]
     = {{-Image-}, {-Image-}, {-Image-}, {-Image-}, {-Image-}, {-Image-}}

    #> ImagePartition[hedy, 257]
     = {{-Image-, -Image-}, {-Image-, -Image-}, {-Image-, -Image-}}
    #> ImagePartition[hedy, 646]
     = {{-Image-}}
    #> ImagePartition[hedy, 647]
     = {}
    #> ImagePartition[hedy, {256, 300}]
     = {{-Image-, -Image-}, {-Image-, -Image-}}

    #> ImagePartition[hedy, {0, 300}]
     : {0, 300} is not a valid size specification for image partitions.
     = ImagePartition[-Image-, {0, 300}]
    """

    summary_text = "divide an image in an array of sub-images"
    rules = {"ImagePartition[i_Image, s_Integer]": "ImagePartition[i, {s, s}]"}

    messages = {"arg2": "`1` is not a valid size specification for image partitions."}

    def eval(self, image, w: Integer, h: Integer, evaluation: Evaluation):
        "ImagePartition[image_Image, {w_Integer, h_Integer}]"
        py_w = w.value
        py_h = h.value
        if py_w <= 0 or py_h <= 0:
            evaluation.message("ImagePartition", "arg2", ListExpression(w, h))
            return
        pixels = image.pixels
        shape = pixels.shape

        # drop blocks less than w x h
        parts = []
        for yi in range(shape[0] // py_h):
            row = []
            for xi in range(shape[1] // py_w):
                p = pixels[yi * py_h : (yi + 1) * py_h, xi * py_w : (xi + 1) * py_w]
                row.append(Image(p, image.color_space))
            if row:
                parts.append(row)
        return from_python(parts)


class Sharpen(Builtin):
    """

    <url>:WMA link:https://reference.wolfram.com/language/ref/Sharpen.html</url>

    <dl>
      <dt>'Sharpen[$image$]'
      <dd>gives a sharpened version of $image$.

      <dt>'Sharpen[$image$, $r$]'
      <dd>sharpens $image$ with a kernel of size $r$.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> Sharpen[hedy]
     = -Image-
    >> Sharpen[hedy, 5]
     = -Image-
    """

    summary_text = "sharpen version of an image"
    rules = {"Sharpen[i_Image]": "Sharpen[i, 2]"}

    def eval(self, image, r, evaluation: Evaluation):
        "Sharpen[image_Image, r_?RealNumberQ]"
        f = PIL.ImageFilter.UnsharpMask(r.round_to_float())
        return image.filter(lambda im: im.filter(f))


class Threshold(Builtin):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Threshold.html</url>

    <dl>
      <dt>'Threshold[$image$]'
      <dd>gives a value suitable for binarizing $image$.
    </dl>

    The option "Method" may be "Cluster" (use Otsu's threshold), "Median", or "Mean".

    >> img = Import["ExampleData/hedy.tif"];
    >> Threshold[img]
     = 0.408203
    X> Binarize[img, %]
     = -Image-
    X> Threshold[img, Method -> "Mean"]
     = 0.22086
    X> Threshold[img, Method -> "Median"]
     = 0.0593961
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

    def eval(self, image, evaluation: Evaluation, options: dict):
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
            evaluation.message("Threshold", "illegalmethod", method)
            return

        return MachineReal(float(threshold))


# Todo  Darker, ImageClip, ImageEffect, ImageRestyle, Lighter
