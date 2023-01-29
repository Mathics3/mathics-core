"""
Image Filters
"""

import numpy
import PIL

from mathics.builtin.base import Builtin
from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer
from mathics.core.evaluation import Evaluation
from mathics.eval.image import convolve, matrix_to_numpy, pixels_as_float

# This tells documentation how to sort this module
sort_order = "mathics.builtin.image.image-filters"


class _PillowImageFilter(Builtin):
    """
    Base class for various Image filters.
    """

    def compute(self, image, f):
        return image.filter(lambda im: im.filter(f))


class GaussianFilter(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/GaussianFilter.html</url>

    <dl>
      <dt>'GaussianFilter[$image$, $r$]'
      <dd>blurs $image$ using a Gaussian blur filter of radius $r$.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> GaussianFilter[hedy, 2.5]
     = -Image-
    """

    summary_text = "apply a gaussian filter to an image"
    messages = {"only3": "GaussianFilter only supports up to three channels."}

    def eval_radius(self, image, radius, evaluation: Evaluation):
        "GaussianFilter[image_Image, radius_?RealNumberQ]"
        if len(image.pixels.shape) > 2 and image.pixels.shape[2] > 3:
            evaluation.message("GaussianFilter", "only3")
            return
        else:
            f = PIL.ImageFilter.GaussianBlur(radius.round_to_float())
            return image.filter(lambda im: im.filter(f))


class ImageConvolve(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ImageConvolve.html</url>

    <dl>
      <dt>'ImageConvolve[$image$, $kernel$]'
      <dd>Computes the convolution of $image$ using $kernel$.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> ImageConvolve[hedy, DiamondMatrix[5] / 61]
     = -Image-
    >> ImageConvolve[hedy, DiskMatrix[5] / 97]
     = -Image-
    >> ImageConvolve[hedy, BoxMatrix[5] / 121]
     = -Image-
    """

    summary_text = "give the convolution of image with kernel"

    def eval(self, image, kernel, evaluation: Evaluation):
        "ImageConvolve[image_Image, kernel_?MatrixQ]"
        numpy_kernel = matrix_to_numpy(kernel)
        pixels = pixels_as_float(image.pixels)
        shape = pixels.shape[:2]
        channels = []
        for c in (pixels[:, :, i] for i in range(pixels.shape[2])):
            channels.append(convolve(c.reshape(shape), numpy_kernel, fixed=True))
        return Image(numpy.dstack(channels), image.color_space)


class MaxFilter(_PillowImageFilter):
    """

    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MaxFilter.html</url>

    <dl>
      <dt>'MaxFilter[$image$, $r$]'
      <dd>gives $image$ with a maximum filter of radius $r$ applied on it. This always \
          picks the largest value in the filter's area.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> MaxFilter[hedy, 5]
     = -Image-
    """

    summary_text = "replace every pixel value by the maximum in a neighborhood"

    def eval(self, image, r: Integer, evaluation: Evaluation):
        "MaxFilter[image_Image, r_Integer]"
        return self.compute(image, PIL.ImageFilter.MaxFilter(1 + 2 * r.value))


class MedianFilter(_PillowImageFilter):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MedianFilter.html</url>

    <dl>
      <dt>'MedianFilter[$image$, $r$]'
      <dd>gives $image$ with a median filter of radius $r$ applied on it. This always \
          picks the median value in the filter's area.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> MedianFilter[hedy, 5]
     = -Image-
    """

    summary_text = "replace every pixel value by the median in a neighborhood"

    def eval(self, image, r: Integer, evaluation: Evaluation):
        "MedianFilter[image_Image, r_Integer]"
        return self.compute(image, PIL.ImageFilter.MedianFilter(1 + 2 * r.value))


class MinFilter(_PillowImageFilter):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MinFilter.html</url>

    <dl>
    <dt>'MinFilter[$image$, $r$]'
      <dd>gives $image$ with a minimum filter of radius $r$ applied on it. This always \
          picks the smallest value in the filter's area.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> MinFilter[hedy, 5]
     = -Image-
    """

    summary_text = "replace every pixel value by the minimum in a neighborhood"

    def eval(self, image, r: Integer, evaluation: Evaluation):
        "MinFilter[image_Image, r_Integer]"
        return self.compute(image, PIL.ImageFilter.MinFilter(1 + 2 * r.value))


# TODO:

# BilateralFilter
# CommonestFilter
# CurvatureFlowFilter
# DerivativeFilter
# EntropyFilter
# GaborFilter,
# GeometricMeanFilter
# GradientFilter,
# GradientOrintationFilter,
# HarmonicMeanFilter
# ImageCorrelate,
# KuwaharaFilter
# LaplacianFilter,
# LaplacianGaussianFilter
# MeanFilter,
# MeanShiftFilter
# PeronMalikFilter
# RangeFilter
# RidgeFilter,
# StandardDevisationFilter
# WienerFilter,

# ... and verything in:

# Nonlocal Filters, Frequence-BasedFilters, Region-of-Interest Processing, General Neighborhood Processing
