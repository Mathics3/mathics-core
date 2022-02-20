# -*- coding: utf-8 -*-

from mathics.builtin.base import BoxConstruct


class CompiledCodeBox(BoxConstruct):
    """Routines which get called when Boxing (adding formatting and bounding-box information)
    to CompiledCode.
    """

    def boxes_to_text(self, elements=None, **options):
        if elements is None:
            elements = self._elements
        return elements[0].value

    def boxes_to_mathml(self, elements=None, **options):
        if elements is None:
            elements = self._elements
        return elements[0].value

    def boxes_to_tex(self, elements=None, **options):
        if elements is None:
            elements = self._elements
        return elements[0].value
