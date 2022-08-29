# -*- coding: utf-8 -*-
"""
Lower-level formatter of Mathics objects as js code.

Right now this happens just for Graphics3DBox.
"""


from mathics.builtin.box.graphics3d import Graphics3DBox

from mathics.core.element import BoxElementMixin
from mathics.core.formatter import add_conversion_fn, boxes_to_format


def generic(self, **options):
    return boxes_to_format(self, "text", **options)


add_conversion_fn(BoxElementMixin, generic)


def graphics3d_box(self, elements=None, **options):
    """Turn the Graphics3DBox to into a something javascript-ish
    We include enclosing script tagging.
    """
    if elements:
        options["elements"] = elements

    json_repr = boxes_to_format(self, "json", **options)
    js = f"<graphics3d data='{json_repr}'/>"
    return js


add_conversion_fn(Graphics3DBox, graphics3d_box)
