"""
Operations on Image Structure
"""
import numpy

from mathics.builtin.base import Builtin
from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer
from mathics.core.evaluation import Evaluation
from mathics.eval.image import numpy_flip

# This tells documentation how to sort this module
sort_order = "mathics.builtin.image.operations"


def clip_to(i: int, upper) -> int:
    return min(i, upper) if i > 0 else max(0, upper + i)


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

        def _clip_to(i: int, lower, upper) -> int:
            return min(max(i, 0), upper)

        n = image.pixels.shape[axis]
        py_i1 = -clip_to(i1.value - 1, 0, n - 1)
        py_i2 = _clip_to(i2.value - 1, 0, n - 1)

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
        adjusted_first_row = clip_to(first_row, last_row)
        adjusted_last_row = clip_to(last_row, max_row)

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
        adjusted_first_row = clip_to(first_row, max_row)
        adjusted_last_row = clip_to(last_row, max_row)
        adjusted_first_col = clip_to(first_col, max_col)
        adjusted_last_col = clip_to(last_col, max_col)

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


# TODO; ImageCrop, ImageTrip, ImagePad, BorderDimensions
