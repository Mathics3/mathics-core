# cython: language_level=3
# -*- coding: utf-8 -*-


from mathics.builtin.exceptions import BoxConstructError

from mathics.core.element import ensure_context
from mathics.core.expression import Expression
from mathics.core.symbols import (
    BaseElement,
    Symbol,
)

# from mathics.core.systemsymbols import (
#    SymbolSymbol,
# )


class BoxError(Exception):
    def __init__(self, box, form) -> None:
        super().__init__("Box %s cannot be formatted as %s" % (box, form))
        self.box = box
        self.form = form


class BoxExpression(BaseElement):
    """
    This class is supposed to be the(second) base class for BoxConstruct.
    This would allow to split the interface between a part that handles
    the role of ``Expression`` inside the evaluation process,
    and a part that handles the formatting.
    """

    def __init__(self, *args, **kwargs):
        pass

    def to_expression(self):
        expr = Expression(self.get_name(), *self._elements)
        return expr

    def replace_vars(self, vars, options=None, in_scoping=True, in_function=True):
        expr = self.to_expression()
        result = expr.replace_vars(vars, options, in_scoping, in_function)
        return result

    def evaluate(self, evaluation):
        # THINK about: Should we evaluate the elements here?
        return self

    def get_elements(self):
        expr = self.to_expression()
        elements = expr.get_elements()
        return elements

    def get_head_name(self):
        return self.get_name()

    def get_lookup_name(self):
        return self.get_name()

    def get_string_value(self):
        return "-@" + self.get_head_name() + "@-"

    def sameQ(self, expr) -> bool:
        """Mathics SameQ"""
        return expr.sameQ(self.to_expression())

    def do_format(self, evaluation, format):
        return self

    def format(self, evaluation, fmt):
        expr = Expression("HoldForm", self.to_expression())
        fexpr = expr.format(evaluation, fmt)
        return fexpr

    def get_head(self):
        return Symbol(self.get_name())

    @property
    def head(self):
        return self.get_head()

    @head.setter
    def head(self, value):
        raise ValueError("BoxConstruct.head is write protected.")

    @property
    def leaves(self):
        return self.get_elements()

    @leaves.setter
    def leaves(self, value):
        raise ValueError("BoxConstruct.leaves is write protected.")

    # I need to repeat this, because this is not
    # an expression...
    def has_form(self, heads, *element_counts):
        """
        element_counts:
            (,):        no leaves allowed
            (None,):    no constraint on number of leaves
            (n, None):  leaf count >= n
            (n1, n2, ...):    leaf count in {n1, n2, ...}
        """

        head_name = self.get_name()
        if isinstance(heads, (tuple, list, set)):
            if head_name not in [ensure_context(h) for h in heads]:
                return False
        else:
            if head_name != ensure_context(heads):
                return False
        if not element_counts:
            return False
        if element_counts and element_counts[0] is not None:
            count = len(self._elements)
            if count not in element_counts:
                if (
                    len(element_counts) == 2
                    and element_counts[1] is None  # noqa
                    and count >= element_counts[0]
                ):
                    return True
                else:
                    return False
        return True

    def flatten_pattern_sequence(self, evaluation) -> "BaseElement":
        return self.to_expression()

    def boxes_to_text(self, leaves, **options) -> str:
        raise BoxConstructError

    def boxes_to_mathml(self, leaves, **options) -> str:
        raise BoxConstructError

    def boxes_to_tex(self, leaves, **options) -> str:
        raise BoxConstructError
