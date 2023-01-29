# -*- coding: utf-8 -*-

"""
helper functions for images
"""

import functools
from operator import itemgetter
from typing import List, Optional, Tuple

import numpy
import PIL
import PIL.Image

from mathics.builtin.base import String
from mathics.core.atoms import Rational
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRule, SymbolSimplify

try:
    from PIL.ExifTags import TAGS as ExifTags
except ImportError:
    ExifTags = {}

# Exif: Exchangeable image file format for digital still cameras.
# See http://www.exiv2.org/tags.html

# names overriding the ones given by Pillow
Exif_names = {
    37385: "FlashInfo",
    40960: "FlashpixVersion",
    40962: "PixelXDimension",
    40963: "PixelYDimension",
}

# After Python 3.6 support is dropped, this can be simplified
# to for Pillow 9+ and use PIL.Image.Resampling only.
if hasattr(PIL.Image, "Resampling"):
    pil_resize = PIL.Image.Resampling
else:
    pil_resize = PIL.Image

# See:
# https://pillow.readthedocs.io/en/stable/handbook/concepts.html#filters
# For a list and comparison of the filters.

resampling_names2PIL = {
    "Automatic": getattr(pil_resize, "BICUBIC"),
    "Bicubic": getattr(pil_resize, "BICUBIC"),
    "Bilinear": getattr(pil_resize, "BILINEAR"),
    "Box": getattr(pil_resize, "BOX"),
    "Hamming": getattr(pil_resize, "HAMMING"),
    "Lanczos": getattr(pil_resize, "LANCZOS"),
    "Nearest": getattr(pil_resize, "NEAREST"),
}


def convolve(in1, in2, fixed=True):
    """
    A very much boiled down version scipy.signal.signaltools.fftconvolve with added padding, see
    https://github.com/scipy/scipy/blob/master/scipy/signal/signaltools.py; please see the Scipy
    LICENSE in the accompanying files.
    """

    in1 = numpy.asarray(in1)
    in2 = numpy.asarray(in2)

    padding = numpy.array(in2.shape) // 2
    if fixed:  # add "Fixed" padding?
        in1 = numpy.pad(in1, padding, "edge")

    s1 = numpy.array(in1.shape)
    s2 = numpy.array(in2.shape)
    shape = s1 + s2 - 1

    sp1 = numpy.fft.rfftn(in1, shape)
    sp2 = numpy.fft.rfftn(in2, shape)
    ret = numpy.fft.irfftn(sp1 * sp2, shape)

    excess = (numpy.array(ret.shape) - s1) // 2 + padding
    return ret[tuple(slice(p, -p) for p in excess)]


def extract_exif(image, evaluation: Evaluation) -> Optional[Expression]:
    """
    Convert Exif information from image into options
    that can be passed to Image[].
    Return None if there is no Exif information.
    """
    if hasattr(image, "getexif"):

        # PIL seems to have a bug in getting v2_tags,
        # specifically tag offsets because
        # it expects image.fp to exist and for us it
        # doesn't.
        try:
            exif = image.getexif()
        except Exception:
            return None

        # If exif is None or an empty list, we have no information.
        if not exif:
            return None

        exif_options: List[Expression] = []

        for k, v in sorted(exif.items(), key=itemgetter(0)):
            name = ExifTags.get(k)
            if not name:
                continue

            # EXIF has the following types: Short, Long, Rational, Ascii, Byte
            # (see http://www.exiv2.org/tags.html). we detect the type from the
            # Python type Pillow gives us and do the appropiate MMA handling.

            if isinstance(v, tuple) and len(v) == 2:  # Rational
                value = Rational(v[0], v[1])
                if name == "FocalLength":
                    value = from_python(value.round(2))
                else:
                    value = Expression(SymbolSimplify, value).evaluate(evaluation)
            elif isinstance(v, bytes):  # Byte
                value = String(" ".join([str(x) for x in v]))
            elif isinstance(v, (int, str)):  # Short, Long, ASCII
                value = from_python(v)
            else:
                continue

            exif_options.append(
                Expression(SymbolRule, String(Exif_names.get(k, name)), value)
            )

        return Expression(SymbolRule, String("RawExif"), ListExpression(*exif_options))


def get_image_size_spec(old_size, new_size) -> Optional[float]:
    predefined_sizes = {
        "System`Tiny": 75,
        "System`Small": 150,
        "System`Medium": 300,
        "System`Large": 450,
        "System`Automatic": 0,  # placeholder
    }
    result = new_size.round_to_float()
    if result is not None:
        result = int(result)
        if result <= 0:
            return None
        return result

    if isinstance(new_size, Symbol):
        name = new_size.get_name()
        if name == "System`All":
            return old_size
        return predefined_sizes.get(name, None)
    if new_size.has_form("Scaled", 1):
        s = new_size.elements[0].round_to_float()
        if s is None:
            return None
        return max(1, old_size * s)  # handle negative s values silently
    return None


def image_pixels(matrix):
    try:
        pixels = numpy.array(matrix, dtype="float64")
    except ValueError:  # irregular array, e.g. {{0, 1}, {0, 1, 1}}
        return None
    shape = pixels.shape
    if len(shape) == 2 or (len(shape) == 3 and shape[2] in (1, 3, 4)):
        return pixels
    else:
        return None


def linearize_numpy_array(a: numpy.array) -> Tuple[numpy.array, int]:
    """
    Transforms a numpy array numpy array and return the array and the number
    of dimensions in the array

    A binary search is used.
    """

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


def matrix_to_numpy(a):
    def matrix():
        for y in a.elements:
            yield [x.round_to_float() for x in y.elements]

    return numpy.array(list(matrix()))


def numpy_flip(pixels, axis):
    f = (numpy.flipud, numpy.fliplr)[axis]
    return f(pixels)


def numpy_to_matrix(pixels):
    channels = pixels.shape[2]
    if channels == 1:
        return pixels[:, :, 0].tolist()
    else:
        return pixels.tolist()


def pixels_as_float(pixels):
    dtype = pixels.dtype
    if dtype in (numpy.float32, numpy.float64):
        return pixels
    elif dtype == numpy.uint8:
        return pixels.astype(numpy.float32) / 255.0
    elif dtype == numpy.uint16:
        return pixels.astype(numpy.float32) / 65535.0
    elif dtype is numpy.dtype(bool):
        return pixels.astype(numpy.float32)
    else:
        raise NotImplementedError


def pixels_as_ubyte(pixels):
    dtype = pixels.dtype
    if dtype in (numpy.float32, numpy.float64):
        pixels = numpy.maximum(numpy.minimum(pixels, 1.0), 0.0)
        return (pixels * 255.0).astype(numpy.uint8)
    elif dtype == numpy.uint8:
        return pixels
    elif dtype == numpy.uint16:
        return (pixels / 256).astype(numpy.uint8)
    elif dtype is numpy.dtype(bool):
        return pixels.astype(numpy.uint8) * 255
    else:
        raise NotImplementedError


def pixels_as_uint(pixels):
    dtype = pixels.dtype
    if dtype in (numpy.float32, numpy.float64):
        pixels = numpy.maximum(numpy.minimum(pixels, 1.0), 0.0)
        return (pixels * 65535.0).astype(numpy.uint16)
    elif dtype == numpy.uint8:
        return pixels.astype(numpy.uint16) * 256
    elif dtype == numpy.uint16:
        return pixels
    elif dtype is numpy.dtype(bool):
        return pixels.astype(numpy.uint8) * 65535
    else:
        raise NotImplementedError


def resize_width_height(
    image, width, height, resampling_name: str, evaluation: Evaluation
):
    """
    workhorse part of ImageResize[] after mathic options have been processed.
    """
    from mathics.builtin.image.base import Image

    if resampling_name not in resampling_names2PIL.keys():
        evaluation.message("ImageResize", "imgrsm", resampling_name)
        return
    resample = resampling_names2PIL[resampling_name]

    # perform the resize
    if hasattr(image, "pillow"):
        if resampling_name not in resampling_names2PIL.keys():
            evaluation.message("ImageResize", "imgrsm", resampling_name)
            return
        pillow = image.pillow.resize(size=(width, height), resample=resample)
        pixels = numpy.asarray(pillow)
        return Image(pixels, image.color_space, pillow=pillow)

    return image.filter(lambda im: im.resize((width, height), resample=resample))

    # The Below code is hand-crapted Guassian resampling code, which is what
    # WMA does. For now, are going to punt on this, and we use PIL methods only.

    # Gaussian need sto unrounded values to compute scaling ratios.
    # round to closest pixel for other methods.

    # h, w = int(round(height)), int(round(width))
    # try:
    #     from skimage import __version__ as skimage_version, transform

    #     multichannel = image.pixels.ndim == 3

    #     sy = height / old_h
    #     sx = width / old_w
    #     if sy > sx:
    #         err = abs((sy * old_w) - (sx * old_w))
    #         s = sy
    #     else:
    #         err = abs((sy * old_h) - (sx * old_h))
    #         s = sx
    #     if err > 1.5:
    #         # TODO overcome this limitation
    #         evaluation.message("ImageResize", "gaussaspect")
    #         return
    #     elif s > 1:
    #         pixels = transform.pyramid_expand(
    #             image.pixels, upscale=s, multichannel=multichannel
    #         ).clip(0, 1)
    #     else:
    #         kwargs = {"downscale": (1.0 / s)}
    #         # scikit_image in version 0.19 changes the resize parameter deprecating
    #         # "multichannel". scikit_image also doesn't support older Pythons like 3.6.15.
    #         # If we drop suport for 3.6 we can probably remove
    #         if skimage_version >= "0.19":
    #             # Not totally sure that we want channel_axis=1, but it makes the
    #             # test work. multichannel is deprecated in scikit-image-19.2
    #             # Previously we used multichannel (=3)
    #             # as in the above s > 1 case.
    #             kwargs["channel_axis"] = 2
    #         else:
    #             kwargs["multichannel"] = multichannel

    #         pixels = transform.pyramid_reduce(image.pixels, **kwargs).clip(0, 1)

    #     return Image(pixels, image.color_space)
    # except ImportError:
    #     evaluation.message("ImageResize", "skimage")
