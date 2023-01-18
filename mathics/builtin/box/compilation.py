# -*- coding: utf-8 -*-
"""
Boxing Symbols for compiled code
"""

from mathics.builtin.box.expression import BoxExpression


class CompiledCodeBox(BoxExpression):
    """
    <dl>
      <dt>'CompiledCodeBox'
      <dd> is the symbol used in boxing 'CompiledCode' expression.
    </dl>
    """

    summary_text = "symbol used in boxing 'CompiledCode' expressions"

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
