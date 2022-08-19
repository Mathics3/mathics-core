# -*- coding: utf-8 -*-

from mathics.builtin.base import BoxExpression


class CompiledCodeBox(BoxExpression):
    """
    <dl>
      <dt>'CompiledCodeBox[...]'
      <dd> holds the compiled code generated by 'Compile'.
    </dl>

    Routines which get called when Boxing (adding formatting and bounding-box information)
    to CompiledCode.

    """

    # summary_text = "box representation of a compiled code"

    def boxes_to_text(self, elements=None, **options):
        if elements is None:
            elements = self.elements
        return elements[0].value

    def boxes_to_mathml(self, elements=None, **options):
        if elements is None:
            elements = self.elements
        return elements[0].value

    def boxes_to_tex(self, elements=None, **options):
        if elements is None:
            elements = self.elements
        return elements[0].value
