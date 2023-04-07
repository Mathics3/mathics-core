"""
Morphological Image Processing
"""

from mathics.builtin.base import Builtin
from mathics.builtin.image.base import Image, skimage_requires
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.eval.image import matrix_to_numpy, pixels_as_float, pixels_as_ubyte


class _MorphologyFilter(Builtin):
    """
    Base class for many Morphological Image Processing filters.
    This requires scikit-mage to be installed.
    """

    messages = {
        "grayscale": "Your image has been converted to grayscale as color images are not supported yet."
    }

    requires = skimage_requires
    rules = {"%(name)s[i_Image, r_?RealNumberQ]": "%(name)s[i, BoxMatrix[r]]"}

    def eval(self, image, k, evaluation: Evaluation):
        "%(name)s[image_Image, k_?MatrixQ]"
        if image.color_space != "Grayscale":
            image = image.grayscale()
            evaluation.message(self.get_name(), "grayscale")
        import skimage.morphology

        f = getattr(skimage.morphology, self.get_name(True).lower())
        shape = image.pixels.shape[:2]
        img = f(image.pixels.reshape(shape), matrix_to_numpy(k))
        return Image(img, "Grayscale")


class Closing(_MorphologyFilter):
    """
    <url>
    :WMA link
    :https://reference.wolfram.com/language/ref/Closing.html</url>

    <dl>
      <dt>'Closing[$image$, $ker$]'
      <dd>Gives the morphological closing of $image$ with respect to structuring element $ker$.
    </dl>

    >> ein = Import["ExampleData/Einstein.jpg"];
    >> Closing[ein, 2.5]
     = -Image-
    """

    summary_text = "morphological closing regarding a kernel"


class Dilation(_MorphologyFilter):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Dilation.html</url>

    <dl>
      <dt>'Dilation[$image$, $ker$]'
      <dd>Gives the morphological dilation of $image$ with respect to structuring element $ker$.
    </dl>

    >> ein = Import["ExampleData/Einstein.jpg"];
    >> Dilation[ein, 2.5]
     = -Image-
    """

    summary_text = "give the dilation with respect to a range-r square"


class Erosion(_MorphologyFilter):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Erosion.html</url>

    <dl>
      <dt>'Erosion[$image$, $ker$]'
      <dd>Gives the morphological erosion of $image$ with respect to structuring element $ker$.
    </dl>

    >> ein = Import["ExampleData/Einstein.jpg"];
    >> Erosion[ein, 2.5]
     = -Image-
    """

    summary_text = "give erosion with respect to a range-r square"


class MorphologicalComponents(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/MorphologicalComponents.html</url>

    <dl>
      <dt>'MorphologicalComponents[$image$]'
      <dd> Builds a 2-D array in which each pixel of $image$ is replaced \
           by an integer index representing the connected foreground image \
           component in which the pixel lies.

      <dt>'MorphologicalComponents[$image$, $threshold$]'
      <dd> consider any pixel with a value above $threshold$ as the foreground.
    </dl>
    """

    summary_text = "tag connected regions of similar colors"

    rules = {"MorphologicalComponents[i_Image]": "MorphologicalComponents[i, 0]"}

    def eval(self, image, t, evaluation: Evaluation):
        "MorphologicalComponents[image_Image, t_?RealNumberQ]"
        pixels = pixels_as_ubyte(
            pixels_as_float(image.grayscale().pixels) > t.round_to_float()
        )
        import skimage.measure

        return from_python(
            skimage.measure.label(pixels, background=0, connectivity=2).tolist()
        )


class Opening(_MorphologyFilter):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Opening.html</url>

    <dl>
      <dt>'Opening[$image$, $ker$]'
      <dd>Gives the morphological opening of $image$ with respect to structuring element $ker$.
    </dl>

    >> ein = Import["ExampleData/Einstein.jpg"];
    >> Opening[ein, 2.5]
     = -Image-
    """

    summary_text = "get morphological opening regarding a kernel"


# TODO DistanceTransform, Thinning, Pruning,
# and lots of others under "Morophological Transforms
