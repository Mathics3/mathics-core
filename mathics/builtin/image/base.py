"""
Base classes for Image Manipulation
"""
from typing import Tuple

import numpy
import PIL.Image

from mathics.builtin.base import AtomBuiltin, String
from mathics.builtin.box.image import ImageBox
from mathics.builtin.colors.color_internals import convert_color
from mathics.core.atoms import Atom
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.systemsymbols import SymbolImage, SymbolRule
from mathics.eval.image import image_pixels, pixels_as_float, pixels_as_ubyte

skimage_requires = ("skimage",)

# No user docs here.
no_doc = True


class Image(Atom):
    class_head_name = "System`Image"

    # FIXME: pixels should be optional if pillow is provided.
    def __init__(self, pixels, color_space, pillow=None, metadata={}, **kwargs):
        super(Image, self).__init__(**kwargs)

        if pillow is not None:
            self.pillow = pillow

        self.pixels = pixels

        if len(pixels.shape) == 2:
            pixels = pixels.reshape(list(pixels.shape) + [1])

        # FIXME: assigning pixels should be done lazily on demand.
        # Turn pixels into a property? Include a setter?

        self.pixels = pixels

        self.color_space = color_space
        self.metadata = metadata

        # Set a value for self.__hash__() once so that every time
        # it is used this is fast. Note that in contrast to the
        # cached object key, the hash key needs to be unique across all
        # Python objects, so we include the class in the
        # event that different objects have the same Python value
        self.hash = hash(
            (
                SymbolImage,
                self.pixels.tobytes(),
                self.color_space,
                frozenset(self.metadata.items()),
            )
        )

    def atom_to_boxes(self, form, evaluation: Evaluation) -> ImageBox:
        """
        Converts our internal Image object into a PNG base64-encoded.
        """
        return ImageBox(self)

    # __hash__ is defined so that we can store Number-derived objects
    # in a set or dictionary.
    def __hash__(self):
        return self.hash

    def __str__(self):
        return "-Image-"

    def color_convert(self, to_color_space, preserve_alpha=True):
        if to_color_space == self.color_space and preserve_alpha:
            return self
        else:
            pixels = pixels_as_float(self.pixels)
            converted = convert_color(
                pixels, self.color_space, to_color_space, preserve_alpha
            )
            if converted is None:
                return None
            return Image(converted, to_color_space)

    def channels(self):
        return self.pixels.shape[2]

    def default_format(self, evaluation, form):
        return "-Image-"

    def dimensions(self) -> Tuple[int, int]:
        shape = self.pixels.shape
        return shape[1], shape[0]

    def do_copy(self):
        return Image(self.pixels, self.color_space, self.metadata)

    def filter(self, f):  # apply PIL filters component-wise
        pixels = self.pixels
        n = pixels.shape[2]
        channels = [
            f(PIL.Image.fromarray(c, "L")) for c in (pixels[:, :, i] for i in range(n))
        ]
        return Image(numpy.dstack(channels), self.color_space)

    def get_sort_key(self, pattern_sort=False) -> tuple:
        if pattern_sort:
            # If pattern_sort=True, returns the sort key that matches to an Atom.
            return super(Image, self).get_sort_key(True)
        else:
            # If pattern is False, return a sort_key for the expression `Image[]`,
            # but with a `2` instead of `1` in the 5th position,
            # and adding two extra fields: the length in the 5th position,
            # and a hash in the 6th place.
            return (1, 3, SymbolImage, len(self.pixels), tuple(), 2, hash(self))

    def grayscale(self):
        return self.color_convert("Grayscale")

    def pil(self):

        if hasattr(self, "pillow") and self.pillow is not None:
            return self.pillow

        # see https://pillow.readthedocs.io/en/stable/handbook/concepts.html

        n = self.channels()

        if n == 1:
            dtype = self.pixels.dtype

            if dtype in (numpy.float32, numpy.float64):
                pixels = self.pixels.astype(numpy.float32)
                mode = "F"
            elif dtype == numpy.uint32:
                pixels = self.pixels
                mode = "I"
            else:
                pixels = pixels_as_ubyte(self.pixels)
                mode = "L"

            pixels = pixels.reshape(pixels.shape[:2])
        elif n == 3:
            if self.color_space == "LAB":
                mode = "LAB"
                pixels = self.pixels
            elif self.color_space == "HSB":
                mode = "HSV"
                pixels = self.pixels
            elif self.color_space == "RGB":
                mode = "RGB"
                pixels = self.pixels
            else:
                mode = "RGB"
                pixels = self.color_convert("RGB").pixels

            pixels = pixels_as_ubyte(pixels)
        elif n == 4:
            if self.color_space == "CMYK":
                mode = "CMYK"
                pixels = self.pixels
            elif self.color_space == "RGB":
                mode = "RGBA"
                pixels = self.pixels
            else:
                mode = "RGBA"
                pixels = self.color_convert("RGB").pixels

            pixels = pixels_as_ubyte(pixels)
        else:
            raise NotImplementedError

        return PIL.Image.fromarray(pixels, mode)

    def options(self):
        return ListExpression(
            Expression(SymbolRule, String("ColorSpace"), String(self.color_space)),
            Expression(SymbolRule, String("MetaInformation"), self.metadata),
        )

    def sameQ(self, other) -> bool:
        """Mathics SameQ"""
        if not isinstance(other, Image):
            return False
        if self.color_space != other.color_space or self.metadata != other.metadata:
            return False
        return numpy.array_equal(self.pixels, other.pixels)

    def storage_type(self):
        dtype = self.pixels.dtype
        if dtype in (numpy.float32, numpy.float64):
            return "Real"
        elif dtype == numpy.uint32:
            return "Bit32"
        elif dtype == numpy.uint16:
            return "Bit16"
        elif dtype == numpy.uint8:
            return "Byte"
        elif dtype == bool:
            return "Bit"
        else:
            return str(dtype)

    def to_python(self, *args, **kwargs):
        return self.pixels


class ImageAtom(AtomBuiltin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ImageAtom.html</url>

    <dl>
      <dt>'Image[...]'
      <dd> produces the internal representation of an image from an array \
          of values for the pixels.
    </dl>

    #> Image[{{{1,1,0},{0,1,1}}, {{1,0,1},{1,1,0}}}]
     = -Image-

    #> Image[{{{0,0,0,0.25},{0,0,0,0.5}}, {{0,0,0,0.5},{0,0,0,0.75}}}]
     = -Image-
    """

    summary_text = "get internal representation of an image"

    def eval_create(self, array, evaluation: Evaluation):
        "Image[array_]"
        pixels = image_pixels(array.to_python())
        if pixels is not None:
            shape = pixels.shape
            is_rgb = len(shape) == 3 and shape[2] in (3, 4)
            return Image(pixels.clip(0, 1), "RGB" if is_rgb else "Grayscale")
        else:
            return Expression(SymbolImage, array)
