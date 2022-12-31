"""
Image testing
"""
from mathics.builtin.base import Test
from mathics.builtin.image.base import Image, _skimage_requires

# This tells documentation how to sort this module
sort_order = "mathics.builtin.image.image-filters"


class _ImageTest(Test):
    """
    Testing Image Builtins -- those function names ending with "Q" -- that require scikit-image.
    """

    requires = _skimage_requires


class BinaryImageQ(_ImageTest):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/BinaryImageQ.html</url>

    <dl>
      <dt>'BinaryImageQ[$image]'
      <dd>returns True if the pixels of $image are binary bit values, and False otherwise.
    </dl>

    S> img = Import["ExampleData/lena.tif"];
    S> BinaryImageQ[img]
     = False

    S> BinaryImageQ[Binarize[img]]
     = ...
     : ...
    """

    summary_text = "test whether pixels in an image are binary bit values"

    def test(self, expr):
        return isinstance(expr, Image) and expr.storage_type() == "Bit"


class ImageQ(_ImageTest):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/ImageQ.html</url>

    <dl>
      <dt>'ImageQ[Image[$pixels]]'
      <dd>returns True if $pixels has dimensions from which an Image can be constructed, and False otherwise.
    </dl>

    >> ImageQ[Image[{{0, 1}, {1, 0}}]]
     = True

    >> ImageQ[Image[{{{0, 0, 0}, {0, 1, 0}}, {{0, 1, 0}, {0, 1, 1}}}]]
     = True

    >> ImageQ[Image[{{{0, 0, 0}, {0, 1}}, {{0, 1, 0}, {0, 1, 1}}}]]
     = False

    >> ImageQ[Image[{1, 0, 1}]]
     = False

    >> ImageQ["abc"]
     = False
    """

    summary_text = "test whether is a valid image"

    def test(self, expr):
        return isinstance(expr, Image)
