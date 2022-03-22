# -*- coding: utf-8 -*-

from mathics.builtin.base import BoxConstruct


class ImageBox(BoxConstruct):
    # """Routines which get called when Boxing (adding formatting and bounding-box information)
    # an Image object.
    # """
    summary_text = " is the graphic representation of an image"

    def boxes_to_text(self, elements=None, **options):
        return "-Image-"

    def boxes_to_mathml(self, elements=None, **options):
        if elements is None:
            elements = self._elements
        # see https://tools.ietf.org/html/rfc2397
        return '<mglyph src="%s" width="%dpx" height="%dpx" />' % (
            elements[0].get_string_value(),
            elements[1].get_int_value(),
            elements[2].get_int_value(),
        )

    def boxes_to_tex(self, elements=None, **options):
        return "-Image-"
