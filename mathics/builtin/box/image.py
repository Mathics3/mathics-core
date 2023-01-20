# -*- coding: utf-8 -*-
"""
Boxing Symbol for Raster Images
"""
# Docs are not yet ready for prime time. Maybe after release 6.0.0.
no_doc = True

import base64
import tempfile
import warnings
from copy import deepcopy
from io import BytesIO
from typing import Tuple

import PIL.Image

from mathics.builtin.box.expression import BoxExpression
from mathics.core.element import BaseElement
from mathics.eval.image import pixels_as_ubyte


class ImageBox(BoxExpression):
    """
    <dl>
      <dt>'ImageBox'
      <dd>is the symbol used in boxing 'Image' expressions.
    </dl>

    """

    summary_text = "symbol used boxing Image expresssions"

    def boxes_to_b64text(
        self, elements: Tuple[BaseElement] = None, **options
    ) -> Tuple[bytes, Tuple[int, int]]:
        """
        Produces a base64 png representation and a tuple with the size of the pillow image
        associated to the object.
        """
        contents, size = self.boxes_to_png(elements, **options)
        encoded = base64.b64encode(contents)
        encoded = b"data:image/png;base64," + encoded
        return (encoded, size)

    def boxes_to_png(self, elements=None, **options) -> Tuple[bytes, Tuple[int, int]]:
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

    def boxes_to_text(self, elements=None, **options) -> str:
        return "-Image-"

    def boxes_to_mathml(self, elements=None, **options) -> str:
        encoded, size = self.boxes_to_b64text(elements, **options)
        decoded = encoded.decode("utf8")
        # see https://tools.ietf.org/html/rfc2397
        return f'<mglyph src="{decoded}" width="{size[0]}px" height="{size[1]}px" />'

    def boxes_to_tex(self, elements=None, **options) -> str:
        """
        Store the associated image as a png file and return
        a LaTeX command for including it.
        """

        data, size = self.boxes_to_png(elements, **options)
        res = 100  # pixels/cm
        width_str, height_str = (str(n / res).strip() for n in size)
        head = rf"\includegraphics[width={width_str}cm,height={height_str}cm]"

        # This produces a random name, where the png file is going to be stored.
        # LaTeX does not have a native way to store an figure embeded in
        # the source.
        fp = tempfile.NamedTemporaryFile(delete=True, suffix=".png")
        path = fp.name
        fp.close()

        with open(path, "wb") as imgfile:
            imgfile.write(data)

        return head + "{" + format(path) + "}"
