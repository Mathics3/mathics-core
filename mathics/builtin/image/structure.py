"""
Structural Image Operations
"""
import numpy

from mathics.builtin.base import Builtin
from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer, MachineReal
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.eval.image import numpy_flip, pixels_as_float


class ImageTake(Builtin):
    """
    Extract Image parts <url>:WMA link:
    https://reference.wolfram.com/language/ref/ImageTake.html</url>
    <dl>
      <dt>'ImageTake[$image$, $n$]'
      <dd>gives the first $n$ rows of $image$.

      <dt>'ImageTake[$image$, -$n$]'
      <dd>gives the last $n$ rows of $image$.

      <dt>'ImageTake[$image$, {$r1$, $r2$}]'
      <dd>gives rows $r1$, ..., $r2$ of $image$.

      <dt>'ImageTake[$image$, {$r1$, $r2$}, {$c1$, $c2$}]'
      <dd>gives a cropped version of $image$.
    </dl>

    Crop to the include only the upper half (244 rows) of an image:
    >> alice = Import["ExampleData/MadTeaParty.gif"]; ImageTake[alice, 244]
     = -Image-

    Now crop to the include the lower half of that image:
    >> ImageTake[alice, -244]
     = -Image-

    Just the text around the hat:
    >> ImageTake[alice, {40, 150}, {500, 600}]
     = -Image-

    """

    summary_text = "extract image parts"

    # FIXME: this probably should be moved out since WMA docs
    # suggest this kind of thing is done across many kinds of
    # images.
    def _image_slice(self, image, i1: Integer, i2: Integer, axis):
        """
        Extracts a slice of an image and return a slice
        indicting a slice, a function flip, that will
        reverse the pixels in an image if necessary.
        """
        n = image.pixels.shape[axis]
        py_i1 = min(max(i1.value - 1, 0), n - 1)
        py_i2 = min(max(i2.value - 1, 0), n - 1)

        def flip(pixels):
            if py_i1 > py_i2:
                return numpy_flip(pixels, axis)
            else:
                return pixels

        return slice(min(py_i1, py_i2), 1 + max(py_i1, py_i2)), flip

    # The reason it is hard to make a rules that turn Image[image, n],
    # or Image[, {r1, r2} into the generic form Image[image, {r1, r2},
    # {c1, c2}] there can be negative numbers, e.g. -n. Also, that
    # missing values, in particular r2 and c2, when filled out can be
    # dependent on the size of the image.

    # FIXME: create common functions to process ranges.
    # FIXME: fix up and use _image_slice.

    def eval_n(self, image, n: Integer, evaluation: Evaluation):
        "ImageTake[image_Image, n_Integer]"
        py_n = n.value
        max_y, max_x = image.pixels.shape[:2]
        if py_n >= 0:
            adjusted_n = min(py_n, max_y)
            pixels = image.pixels[:adjusted_n]
            box_coords = (0, 0, max_x, adjusted_n)
        elif py_n < 0:
            adjusted_n = max(0, max_y + py_n)
            pixels = image.pixels[adjusted_n:]
            box_coords = (0, adjusted_n, max_x, max_y)

        if hasattr(image, "pillow"):
            pillow = image.pillow.crop(box_coords)
            pixels = numpy.asarray(pillow)
            return Image(pixels, image.color_space, pillow=pillow)

        return Image(pixels, image.color_space, pillow=pillow)

    def eval_rows(self, image, r1: Integer, r2: Integer, evaluation: Evaluation):
        "ImageTake[image_Image, {r1_Integer, r2_Integer}]"

        first_row = r1.value
        last_row = r2.value

        max_row, max_col = image.pixels.shape[:2]
        adjusted_first_row = (
            min(first_row, max_row) if first_row > 0 else max(0, max_row + first_row)
        )
        adjusted_last_row = (
            min(last_row, max_row) if last_row > 0 else max(0, max_row + first_row)
        )

        # More complicated in that it reverses the data?
        # if adjusted_first_row > adjusted_last_row:
        #     adjusted_first_row, adjusted_last_row = adjusted_last_row, adjusted_first_row

        pixels = image.pixels[adjusted_first_row:adjusted_last_row]

        if hasattr(image, "pillow"):
            box_coords = (0, adjusted_first_row, max_col, adjusted_last_row)
            pillow = image.pillow.crop(box_coords)
            pixels = numpy.asarray(pillow)
            return Image(pixels, image.color_space, pillow=pillow)

        pixels = image.pixels[adjusted_first_row:adjusted_last_row]
        return Image(pixels, image.color_space, pillow=pillow)

    def eval_rows_cols(
        self, image, r1: Integer, r2: Integer, c1: Integer, c2: Integer, evaluation
    ):
        "ImageTake[image_Image, {r1_Integer, r2_Integer}, {c1_Integer, c2_Integer}]"

        first_row = r1.value
        last_row = r2.value
        first_col = c1.value
        last_col = c2.value

        max_row, max_col = image.pixels.shape[:2]
        adjusted_first_row = (
            min(first_row, max_row) if first_row > 0 else max(0, max_row + first_row)
        )
        adjusted_last_row = (
            min(last_row, max_row) if last_row > 0 else max(0, max_row + last_row)
        )
        adjusted_first_col = (
            min(first_col, max_col) if first_col > 0 else max(0, max_col + first_col)
        )
        adjusted_last_col = (
            min(last_col, max_col) if last_col > 0 else max(0, max_col + last_col)
        )

        # if adjusted_first_row > adjusted_last_row:
        #     adjusted_first_row, adjusted_last_row = adjusted_last_row, adjusted_first_row

        # if adjusted_first_col > adjusted_last_col:
        #     adjusted_first_col, adjusted_last_col = adjusted_last_col, adjusted_first_col

        pixels = image.pixels[
            adjusted_first_col:adjusted_last_col, adjusted_last_row:adjusted_last_row
        ]

        if hasattr(image, "pillow"):
            box_coords = (
                adjusted_first_col,
                adjusted_first_row,
                adjusted_last_col,
                adjusted_last_row,
            )
            pillow = image.pillow.crop(box_coords)
            pixels = numpy.asarray(pillow)
            return Image(pixels, image.color_space, pillow=pillow)

        pixels = image.pixels[adjusted_first_row:adjusted_last_row]
        return Image(pixels, image.color_space, pillow=pillow)

    # Older code we can remove after we condence existing code that looks like this
    #
    # def eval_rows(self, image, r1: Integer, r2: Integer, evaluation: Evaluation):
    #     "ImageTake[image_Image, {r1_Integer, r2_Integer}]"
    #     s, f = self._slice(image, r1, r2, 0)
    #     return Image(f(image.pixels[s]), image.color_space)

    # def eval_rows_cols(
    #     self, image, r1: Integer, r2: Integer, c1: Integer, c2: Integer, evaluation
    # ):
    #     "ImageTake[image_Image, {r1_Integer, r2_Integer}, {c1_Integer, c2_Integer}]"
    #     sr, fr = self._slice(image, r1, r2, 0)
    #     sc, fc = self._slice(image, c1, c2, 1)
    #     return Image(fc(fr(image.pixels[sr, sc])), image.color_space)


# FIXME: move to not-yet created Pixel Operations
class PixelValue(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/PixelValue.html</url>

    <dl>
      <dt>'PixelValue[$image$, {$x$, $y$}]'
      <dd>gives the value of the pixel at position {$x$, $y$} in $image$.
    </dl>

    >> lena = Import["ExampleData/lena.tif"];
    >> PixelValue[lena, {1, 1}]
     = {0.321569, 0.0862745, 0.223529}
    #> {82 / 255, 22 / 255, 57 / 255} // N  (* pixel byte values from bottom left corner *)
     = {0.321569, 0.0862745, 0.223529}

    #> PixelValue[lena, {0, 1}];
     : Padding not implemented for PixelValue.
    #> PixelValue[lena, {512, 1}]
     = {0.72549, 0.290196, 0.317647}
    #> PixelValue[lena, {513, 1}];
     : Padding not implemented for PixelValue.
    #> PixelValue[lena, {1, 0}];
     : Padding not implemented for PixelValue.
    #> PixelValue[lena, {1, 512}]
     = {0.886275, 0.537255, 0.490196}
    #> PixelValue[lena, {1, 513}];
     : Padding not implemented for PixelValue.
    """

    messages = {"nopad": "Padding not implemented for PixelValue."}

    summary_text = "get pixel value of image at a given position"

    def eval(self, image, x, y, evaluation: Evaluation):
        "PixelValue[image_Image, {x_?RealNumberQ, y_?RealNumberQ}]"
        x = int(x.round_to_float())
        y = int(y.round_to_float())
        height = image.pixels.shape[0]
        width = image.pixels.shape[1]
        if not (1 <= x <= width and 1 <= y <= height):
            return evaluation.message("PixelValue", "nopad")
        pixel = pixels_as_float(image.pixels)[height - y, x - 1]
        if isinstance(pixel, (numpy.ndarray, numpy.generic, list)):
            return ListExpression(*[MachineReal(float(x)) for x in list(pixel)])
        else:
            return MachineReal(float(pixel))


# TODO; ImageCrop, ImageTrip, ImagePad, BorderDimensions
