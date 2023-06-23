"""
Geometric Operations
"""

import math

import numpy
import PIL
import PIL.ImageEnhance
import PIL.ImageFilter
import PIL.ImageOps

from mathics.builtin.base import Builtin
from mathics.builtin.image.base import Image
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRule
from mathics.eval.image import get_image_size_spec, resize_width_height


class ImageResize(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ImageResize.html</url>

    <dl>
      <dt>'ImageResize[$image$, $width$]'
      <dd>

      <dt>'ImageResize[$image$, {$width$, $height$}]'
      <dd>
    </dl>

    The Resampling option can be used to specify how to resample the image. Options are:
    <ul>
      <li>Automatic
      <li>Bicubic
      <li>Bilinear
      <li>Box
      <li>Hamming
      <li>Lanczos
      <li>Nearest
    </ul>

    See <url>
    :Pillow Filters:
    https://pillow.readthedocs.io/en/stable/handbook/concepts.html#filters</url>\
    for a description of these.

    S> alice = Import["ExampleData/MadTeaParty.gif"]
     = -Image-

    S> shape = ImageDimensions[alice]
     = {640, 487}

    S> ImageResize[alice, shape / 2]
     = -Image-

    The default sampling method is "Bicubic" which has pretty good upscaling \
    and downscaling quality. However "Box" is the fastest:


    S> ImageResize[alice, shape / 2, Resampling -> "Box"]
     = -Image-
    """

    messages = {
        "imgrssz": "The size `1` is not a valid image size specification.",
        "imgrsm": "Invalid resampling method `1`.",
        "gaussaspect": "Gaussian resampling needs to maintain aspect ratio.",
        "skimage": "Please install scikit-image to use Resampling -> Gaussian.",
    }

    options = {"Resampling": "Automatic"}
    summary_text = "resize an image"

    def eval_resize_width(self, image, s, evaluation, options):
        "ImageResize[image_Image, s_, OptionsPattern[ImageResize]]"
        old_w = image.pixels.shape[1]
        if s.has_form("List", 1):
            width = s.elements[0]
        else:
            width = s
        w = get_image_size_spec(old_w, width)
        if w is None:
            evaluation.message("ImageResize", "imgrssz", s)
            return
        if s.has_form("List", 1):
            height = width
        else:
            height = Symbol("Automatic")
        return self.eval_resize_width_height(image, width, height, evaluation, options)

    def eval_resize_width_height(self, image, width, height, evaluation, options):
        "ImageResize[image_Image, {width_, height_}, OptionsPattern[ImageResize]]"
        # resampling method
        resampling = self.get_option(options, "Resampling", evaluation)
        if (
            isinstance(resampling, Symbol)
            and resampling.get_name() == "System`Automatic"
        ):
            resampling_name = "Bicubic"
        else:
            resampling_name = resampling.value

        # find new size
        old_w, old_h = image.pixels.shape[1], image.pixels.shape[0]
        w = get_image_size_spec(old_w, width)
        h = get_image_size_spec(old_h, height)
        if h is None or w is None:
            evaluation.message("ImageResize", "imgrssz", to_mathics_list(width, height))
            return

        # handle Automatic
        old_aspect_ratio = old_w / old_h
        if w == 0 and h == 0:
            # if both width and height are Automatic then use old values
            w, h = old_w, old_h
        elif w == 0:
            w = max(1, h * old_aspect_ratio)
        elif h == 0:
            h = max(1, w / old_aspect_ratio)

        if resampling_name != "Gaussian":
            # Gaussian need to unrounded values to compute scaling ratios.
            # round to closest pixel for other methods.
            h, w = int(round(h)), int(round(w))

        # perform the resize
        return resize_width_height(image, w, h, resampling_name, evaluation)


class ImageReflect(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ImageReflect.html</url>
    <dl>
      <dt>'ImageReflect[$image$]'
      <dd>Flips $image$ top to bottom.

      <dt>'ImageReflect[$image$, $side$]'
      <dd>Flips $image$ so that $side$ is interchanged with its opposite.

      <dt>'ImageReflect[$image$, $side_1$ -> $side_2$]'
      <dd>Flips $image$ so that $side_1$ is interchanged with $side_2$.
    </dl>

    >> ein = Import["ExampleData/Einstein.jpg"];
    >> ImageReflect[ein]
     = -Image-
    >> ImageReflect[ein, Left]
     = -Image-
    >> ImageReflect[ein, Left -> Top]
     = -Image-

    #> ein == ImageReflect[ein, Left -> Left] == ImageReflect[ein, Right -> Right] == ImageReflect[ein, Top -> Top] == ImageReflect[ein, Bottom -> Bottom]
     = True
    #> ImageReflect[ein, Left -> Right] == ImageReflect[ein, Right -> Left] == ImageReflect[ein, Left] == ImageReflect[ein, Right]
     = True
    #> ImageReflect[ein, Bottom -> Top] == ImageReflect[ein, Top -> Bottom] == ImageReflect[ein, Top] == ImageReflect[ein, Bottom]
     = True
    #> ImageReflect[ein, Left -> Top] == ImageReflect[ein, Right -> Bottom]     (* Transpose *)
     = True
    #> ImageReflect[ein, Left -> Bottom] == ImageReflect[ein, Right -> Top]     (* Anti-Transpose *)
     = True

    #> ImageReflect[ein, x -> Top]
     : x -> Top is not a valid 2D reflection specification.
     = ImageReflect[-Image-, x -> Top]
    """

    summary_text = "reflect an image"
    rules = {
        "ImageReflect[image_Image]": "ImageReflect[image, Top -> Bottom]",
        "ImageReflect[image_Image, Top|Bottom]": "ImageReflect[image, Top -> Bottom]",
        "ImageReflect[image_Image, Left|Right]": "ImageReflect[image, Left -> Right]",
    }

    messages = {"bdrfl2": "`1` is not a valid 2D reflection specification."}

    def eval(self, image, orig, dest, evaluation: Evaluation):
        "ImageReflect[image_Image, Rule[orig_, dest_]]"
        if isinstance(orig, Symbol) and isinstance(dest, Symbol):
            specs = [orig.get_name(), dest.get_name()]
            specs.sort()  # `Top -> Bottom` is the same as `Bottom -> Top`

        def anti_transpose(i):
            return numpy.flipud(numpy.transpose(numpy.flipud(i)))

        def no_op(i):
            return i

        method = {
            ("System`Bottom", "System`Top"): numpy.flipud,
            ("System`Left", "System`Right"): numpy.fliplr,
            ("System`Left", "System`Top"): numpy.transpose,
            ("System`Right", "System`Top"): anti_transpose,
            ("System`Bottom", "System`Left"): anti_transpose,
            ("System`Bottom", "System`Right"): numpy.transpose,
            ("System`Bottom", "System`Bottom"): no_op,
            ("System`Top", "System`Top"): no_op,
            ("System`Left", "System`Left"): no_op,
            ("System`Right", "System`Right"): no_op,
        }.get(tuple(specs), None)

        if method is None:
            evaluation.message(
                "ImageReflect", "bdrfl2", Expression(SymbolRule, orig, dest)
            )
            return

        return Image(method(image.pixels), image.color_space)


class ImageRotate(Builtin):
    """

    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ImageRotate.html</url>

    <dl>
    <dt>'ImageRotate[$image$]'
      <dd>Rotates $image$ 90 degrees counterclockwise.
    <dt>'ImageRotate[$image$, $theta$]'
      <dd>Rotates $image$ by a given angle $theta$
    </dl>

    >> ein = Import["ExampleData/Einstein.jpg"];

    >> ImageRotate[ein]
     = -Image-

    >> ImageRotate[ein, 45 Degree]
     = -Image-

    >> ImageRotate[ein, Pi / 4]
     = -Image-

    #> ImageRotate[ein, ein]
     : Angle -Image- should be a real number, one of Top, Bottom, Left, Right, or a rule from one to another.
     = ImageRotate[-Image-, -Image-]
    """

    messages = {
        "imgang": "Angle `1` should be a real number, one of Top, Bottom, Left, Right, or a rule from one to another."
    }

    rules = {"ImageRotate[i_Image]": "ImageRotate[i, 90 Degree]"}

    summary_text = "rotate an image"

    def eval(self, image, angle, evaluation: Evaluation):
        "ImageRotate[image_Image, angle_]"

        # FIXME: this test I suppose is okay in that it checks more or less what is needed.
        # However there might be a better test like for Real-valued-ness which could be used
        # instead.
        py_angle = (
            angle.round_to_float(evaluation)
            if hasattr(angle, "round_to_float")
            else None
        )

        if py_angle is None:
            evaluation.message("ImageRotate", "imgang", angle)
            return

        def rotate(im):
            return im.rotate(
                180 * py_angle / math.pi, resample=PIL.Image.BICUBIC, expand=True
            )

        return image.filter(rotate)


# TODO Thumbnail
