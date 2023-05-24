"""
Image Properties
"""

from mathics.builtin.base import Builtin, String
from mathics.core.atoms import Integer
from mathics.core.convert.expression import from_python, to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import SymbolDivide
from mathics.eval.image import (
    numpy_to_matrix,
    pixels_as_float,
    pixels_as_ubyte,
    pixels_as_uint,
)

# This tells documentation how to sort this module
sort_order = "mathics.builtin.image.image-properties"


class ImageAspectRatio(Builtin):
    """
    <url>:WMA link:
    https://reference.wolfram.com/language/ref/ImageAspectRatio.html</url>

    <dl>
      <dt>'ImageAspectRatio[$image$]'
      <dd>gives the aspect ratio of $image$.
    </dl>

    >> img = Import["ExampleData/hedy.tif"];
    >> ImageAspectRatio[img]
     = 400 / 323

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

    >> img = Import["ExampleData/hedy.tif"];
    >> ImageChannels[img]
     = 3
    """

    summary_text = "get number of channels present in the data for an image"

    def eval(self, image, evaluation: Evaluation):
        "ImageChannels[image_Image]"
        return Integer(image.channels())


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
            evaluation.message("ImageData", "pixelfmt", stype)
            return
        return from_python(numpy_to_matrix(pixels))


class ImageDimensions(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ImageDimensions.html</url>

    <dl>
      <dt>'ImageDimensions[$image$]'
      <dd>Returns the dimensions {$width$, $height$} of $image$ in pixels.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> ImageDimensions[hedy]
     = {646, 800}

    >> ImageDimensions[RandomImage[1, {50, 70}]]
     = {50, 70}
    """

    summary_text = "get the pixel dimensions of an image"

    def eval(self, image, evaluation: Evaluation):
        "ImageDimensions[image_Image]"
        return to_mathics_list(*image.dimensions(), elements_conversion_fn=Integer)


class ImageType(Builtin):
    """
    <url>
    :WMA link:https://reference.wolfram.com/language/ref/ImageType.html</url>

    <dl>
      <dt>'ImageType[$image$]'
      <dd>gives the interval storage type of $image$, e.g. "Real", "Bit32", or "Bit".
    </dl>

    >> img = Import["ExampleData/hedy.tif"];
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
