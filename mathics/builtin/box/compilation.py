# -*- coding: utf-8 -*-
"""
Boxing Symbols for compiled code
"""

from mathics.builtin.box.expression import BoxExpression

# No user docs here: Box primitives aren't documented.
no_doc = True


class CompiledCodeBox(BoxExpression):
    """
    <dl>
      <dt>'CompiledCodeBox'
      <dd> is the symbol used in boxing 'CompiledCode' expression.
    </dl>
    """

    summary_text = "symbol used in boxing 'CompiledCode' expressions"

    def init(self, *args, **kwargs):
        self._elements = args
        self.box_options = kwargs

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
