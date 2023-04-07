"""
Pixel Operations
"""
import numpy

from mathics.builtin.base import Builtin
from mathics.builtin.image.base import Image
from mathics.core.atoms import Integer, MachineReal
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.list import ListExpression
from mathics.eval.image import pixels_as_float


class PixelValue(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/PixelValue.html</url>

    <dl>
      <dt>'PixelValue[$image$, {$x$, $y$}]'
      <dd>gives the value of the pixel at position {$x$, $y$} in $image$.
    </dl>

    >> hedy = Import["ExampleData/hedy.tif"];
    >> PixelValue[hedy, {1, 1}]
     = {0.439216, 0.356863, 0.337255}
    #> {82 / 255, 22 / 255, 57 / 255} // N  (* pixel byte values from bottom left corner *)
     = {0.321569, 0.0862745, 0.223529}

    #> PixelValue[hedy, {0, 1}];
     : Padding not implemented for PixelValue.
    #> PixelValue[hedy, {512, 1}]
     = {0.0509804, 0.0509804, 0.0588235}
    #> PixelValue[hedy, {647, 1}];
     : Padding not implemented for PixelValue.
    #> PixelValue[hedy, {1, 0}];
     : Padding not implemented for PixelValue.
    #> PixelValue[hedy, {1, 512}]
     = {0.286275, 0.4, 0.423529}
    #> PixelValue[hedy, {1, 801}];
     : Padding not implemented for PixelValue.
    """

    messages = {"nopad": "Padding not implemented for PixelValue."}

    summary_text = "get pixel value of image at a given position"

    def eval(self, image: Image, x, y, evaluation: Evaluation):
        "PixelValue[image_Image, {x_?RealNumberQ, y_?RealNumberQ}]"
        x = int(x.round_to_float())
        y = int(y.round_to_float())
        height = image.pixels.shape[0]
        width = image.pixels.shape[1]
        if not (1 <= x <= width and 1 <= y <= height):
            evaluation.message("PixelValue", "nopad")
            return
        pixel = pixels_as_float(image.pixels)[height - y, x - 1]
        if isinstance(pixel, (numpy.ndarray, numpy.generic, list)):
            return ListExpression(*[MachineReal(float(x)) for x in list(pixel)])
        else:
            return MachineReal(float(pixel))


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

    >> hedy = Import["ExampleData/hedy.tif"];
    >> PixelValuePositions[hedy, 1, 0][[1]]
     = {101, 491, 1}
    >> PixelValue[hedy, {180, 192}]
     = {0.00784314, 0.00784314, 0.0156863}
    """

    rules = {
        "PixelValuePositions[image_Image, val_?RealNumberQ]": "PixelValuePositions[image, val, 0]"
    }

    summary_text = "list the position of pixels with a given value"

    def eval(self, image: Image, val, d, evaluation: Evaluation):
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


# TODO:
#  ImageApply
#  ImageApplyIndexed
#  ImageScan
#  ImageValue,
#  ImageValuePositions
#  ReplaceImageValue,
#  ReplacePixelValue,
