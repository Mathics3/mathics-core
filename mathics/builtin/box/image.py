# -*- coding: utf-8 -*-

import base64
import tempfile
from copy import deepcopy
from io import BytesIO
from typing import Tuple

from mathics.builtin.box.expression import BoxExpression
from mathics.eval.image import pixels_as_ubyte

try:
    import warnings

    import PIL
    import PIL.Image
    import PIL.ImageEnhance
    import PIL.ImageFilter
    import PIL.ImageOps

except ImportError:
    pass


class ImageBox(BoxExpression):
    """
    <dl>
      <dt>'ImageBox[...]'
      <dd>is a box structure for an image element.
    </dl>
    Routines which get called when Boxing (adding formatting and bounding-box information)
    an Image object.
    """

    def boxes_to_b64text(self, elements=None, **options):
        contents, size = self.boxes_to_png(elements, **options)
        encoded = base64.b64encode(contents)
        encoded = b"data:image/png;base64," + encoded
        return encoded, size

    def boxes_to_png(self, elements=None, **options) -> Tuple:
        """
        returns a tuple with the set of bytes with a png representation of the image
        and the scaled size.
        """
        image = self.elements[0] if elements is None else elements[0]

        pixels = pixels_as_ubyte(image.color_convert("RGB", True).pixels)
        shape = pixels.shape

        width = shape[1]
        height = shape[0]
        scaled_width = width
        scaled_height = height

        # If the image was created from PIL, use that rather than
        # reconstruct it from pixels which we can get wrong.
        # In particular getting color-mapping info right can be
        # tricky.
        if hasattr(image, "pillow"):
            pillow = deepcopy(image.pillow)
        else:
            pixels_format = "RGBA" if len(shape) >= 3 and shape[2] == 4 else "RGB"
            pillow = PIL.Image.fromarray(pixels, pixels_format)

        # if the image is very small, scale it up using nearest neighbour.
        min_size = 128
        if width < min_size and height < min_size:
            scale = min_size / max(width, height)
            scaled_width = int(scale * width)
            scaled_height = int(scale * height)
            pillow = pillow.resize(
                (scaled_height, scaled_width), resample=PIL.Image.NEAREST
            )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            stream = BytesIO()
            pillow.save(stream, format="png")
            stream.seek(0)
            contents = stream.read()
            stream.close()

        return (contents, (scaled_width, scaled_height))

    def boxes_to_text(self, elements=None, **options):
        return "-Image-"

    def boxes_to_mathml(self, elements=None, **options):
        encoded, size = self.boxes_to_b64text(elements, **options)
        # see https://tools.ietf.org/html/rfc2397
        return '<mglyph src="%s" width="%dpx" height="%dpx" />' % (encoded, *size)

    def boxes_to_tex(self, elements=None, **options):
        data, size = self.boxes_to_png(elements, **options)
        res = 100  # pixels/cm
        head = rf"\includegraphics[width={size[0]/res}, height={size[1]/res}]"

        # This produces a random name, where the png file is going to be stored.
        # LaTeX does not have a native way to store an figure embeded in
        # the source.
        fp = tempfile.NamedTemporaryFile(delete=True, suffix=".png")
        path = fp.name
        fp.close()

        with open(path, "wb") as imgfile:
            imgfile.write(data)

        return head + "{" + format(path) + "}"
