# cython: language_level=3
# -*- coding: utf-8 -*-

import typing
from typing import Any, Optional

from mathics.core.element import ensure_context

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
    head: "Element"
    leaves: typing.List[Any]
    _sequences: Any

    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            return
        head = args[0]
        if isinstance(head, str):
            head = Symbol(head)
        self._head = head
        self._elements = args[1:]

    def __repr__(self) -> str:
        return "<BoxExpression: %s>" % self

    def __str__(self) -> str:
        if not hasattr(self, "_head"):
            return "<BoxExpression uninitialized>"
        return "%s[%s]" % (
            self._head,
            ", ".join([element.__str__() for element in self._elements]),
        )

    @property
    def elements(self):
        return self._elements

    def evaluate(self, evaluation):
        print("Deprecated!")
        return self

    def flatten_pattern_sequence(self, evaluation):
        """
        called from mathics.core.pattern
        """
        print("Deprecated!")
        return self

    def get_attributes(self, definitions):
        return nothing

    def get_elements(self):
        return self._elements

    # Compatibily with old code. Deprecated, but remove after a little bit
    get_leaves = get_elements

    def get_head(self):
        return self._head

    def get_head_name(self):
        return self._head.name if isinstance(self._head, Symbol) else ""

    def get_mutable_elements(self) -> list:
        """
        Return a shallow mutable copy of the elements
        """
        return list(self._elements)

    def has_form(self, heads, *element_counts):
        """
        element_counts:
            (,):        no elements allowed
            (None,):    no constraint on number of elements
            (n, None):  leaf count >= n
            (n1, n2, ...):    leaf count in {n1, n2, ...}
        """

        head_name = self._head.get_name()
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

    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, value):
        raise ValueError("Expression.head is write protected.")

    # Deprecated - remove eventually
    @property
    def leaves(self):
        return self._elements

    # Deprecated - remove eventually
    @leaves.setter
    def leaves(self, value):
        raise ValueError("Expression.leaves is write protected.")

    def set_element(self, index: int, value):
        """
        Update element[i] with value
        """
        elements = list(self._elements)
        elements[index] = value
        self._elements = tuple(elements)
        self._cache = None

    def process_style_box(self, options):
        if self.has_form("StyleBox", 1, None):
            rules = self._elements[1:]
            for rule in rules:
                if rule.has_form("Rule", 2):
                    name = rule._elements[0].get_name()
                    value = rule._elements[1]
                    if name == "System`ShowStringCharacters":
                        value = value.is_true()
                        options = options.copy()
                        options["show_string_characters"] = value
                    elif name == "System`ImageSizeMultipliers":
                        if value.has_form("List", 2):
                            m1 = value._elements[0].round_to_float()
                            m2 = value._elements[1].round_to_float()
                            if m1 is not None and m2 is not None:
                                options = options.copy()
                                options["image_size_multipliers"] = (m1, m2)
            return True, options
        else:
            return False, options

    def boxes_to_text(self, **options) -> str:
        """
        From a Boxed expression, produces a text representation.
        """
        # Idea @mmatera: All the Boxes expressions should be implemented as a different class
        # which implements these ``boxes_to_*`` methods.

        is_style, options = self.process_style_box(options)
        if is_style:
            return self._elements[0].boxes_to_text(**options)
        if self.has_form("RowBox", 1) and self._elements[0].has_form(  # nopep8
            "List", None
        ):
            return "".join(
                [
                    element.boxes_to_text(**options)
                    for element in self._elements[0]._elements
                ]
            )
        elif self.has_form("SuperscriptBox", 2):
            return "^".join(
                [element.boxes_to_text(**options) for element in self._elements]
            )
        elif self.has_form("FractionBox", 2):
            return "/".join(
                [
                    " ( " + element.boxes_to_text(**options) + " ) "
                    for element in self._elements
                ]
            )
        else:
            raise BoxError(self, "text")

    def boxes_to_mathml(self, **options) -> str:
        is_style, options = self.process_style_box(options)
        if is_style:
            return self._elements[0].boxes_to_mathml(**options)
        name = self._head.get_name()
        if (
            name == "System`RowBox"
            and len(self._elements) == 1
            and self._elements[0].get_head() is SymbolList  # nopep8
        ):
            result = []
            inside_row = options.get("inside_row")
            # inside_list = options.get('inside_list')
            options = options.copy()

            def is_list_interior(content):
                if content.has_form("List", None) and all(
                    element.get_string_value() == ","
                    for element in content._elements[1::2]
                ):
                    return True
                return False

            is_list_row = False
            if (
                len(self._elements[0]._elements) == 3
                and self._elements[0]._elements[0].get_string_value() == "{"  # nopep8
                and self._elements[0]._elements[2].get_string_value() == "}"
                and self._elements[0]._elements[1].has_form("RowBox", 1)
            ):
                content = self._elements[0]._elements[1]._elements[0]
                if is_list_interior(content):
                    is_list_row = True

            if not inside_row and is_list_interior(self._elements[0]):
                is_list_row = True

            if is_list_row:
                options["inside_list"] = True
            else:
                options["inside_row"] = True

            for element in self._elements[0].get_elements():
                result.append(element.boxes_to_mathml(**options))
            return "<mrow>%s</mrow>" % " ".join(result)
        else:
            options = options.copy()
            options["inside_row"] = True
            if name == "System`SuperscriptBox" and len(self._elements) == 2:
                return "<msup>%s %s</msup>" % (
                    self._elements[0].boxes_to_mathml(**options),
                    self._elements[1].boxes_to_mathml(**options),
                )
            if name == "System`SubscriptBox" and len(self._elements) == 2:
                return "<msub>%s %s</msub>" % (
                    self._elements[0].boxes_to_mathml(**options),
                    self._elements[1].boxes_to_mathml(**options),
                )
            if name == "System`SubsuperscriptBox" and len(self._elements) == 3:
                return "<msubsup>%s %s %s</msubsup>" % (
                    self._elements[0].boxes_to_mathml(**options),
                    self._elements[1].boxes_to_mathml(**options),
                    self._elements[2].boxes_to_mathml(**options),
                )
            elif name == "System`FractionBox" and len(self._elements) == 2:
                return "<mfrac>%s %s</mfrac>" % (
                    self._elements[0].boxes_to_mathml(**options),
                    self._elements[1].boxes_to_mathml(**options),
                )
            elif name == "System`SqrtBox" and len(self._elements) == 1:
                return "<msqrt>%s</msqrt>" % (
                    self._elements[0].boxes_to_mathml(**options)
                )
            elif name == "System`GraphBox":
                return "<mi>%s</mi>" % (self._elements[0].boxes_to_mathml(**options))
            else:
                raise BoxError(self, "xml")

    def boxes_to_tex(self, **options) -> str:
        def block(tex, only_subsup=False):
            if len(tex) == 1:
                return tex
            else:
                if not only_subsup or "_" in tex or "^" in tex:
                    return "{%s}" % tex
                else:
                    return tex

        is_style, options = self.process_style_box(options)
        if is_style:
            return self._elements[0].boxes_to_tex(**options)
        name = self._head.get_name()
        if (
            name == "System`RowBox"
            and len(self._elements) == 1
            and self._elements[0].get_head_name() == "System`List"  # nopep8
        ):
            return "".join(
                [
                    element.boxes_to_tex(**options)
                    for element in self._elements[0].get_elements()
                ]
            )
        elif name == "System`SuperscriptBox" and len(self._elements) == 2:
            tex1 = self._elements[0].boxes_to_tex(**options)
            sup_string = self._elements[1].get_string_value()
            if sup_string == "\u2032":
                return "%s'" % tex1
            elif sup_string == "\u2032\u2032":
                return "%s''" % tex1
            else:
                return "%s^%s" % (
                    block(tex1, True),
                    block(self._elements[1].boxes_to_tex(**options)),
                )
        elif name == "System`SubscriptBox" and len(self._elements) == 2:
            return "%s_%s" % (
                block(self._elements[0].boxes_to_tex(**options), True),
                block(self._elements[1].boxes_to_tex(**options)),
            )
        elif name == "System`SubsuperscriptBox" and len(self._elements) == 3:
            return "%s_%s^%s" % (
                block(self._elements[0].boxes_to_tex(**options), True),
                block(self._elements[1].boxes_to_tex(**options)),
                block(self._elements[2].boxes_to_tex(**options)),
            )
        elif name == "System`FractionBox" and len(self._elements) == 2:
            return "\\frac{%s}{%s}" % (
                self._elements[0].boxes_to_tex(**options),
                self._elements[1].boxes_to_tex(**options),
            )
        elif name == "System`SqrtBox" and len(self._elements) == 1:
            return "\\sqrt{%s}" % self._elements[0].boxes_to_tex(**options)
        else:
            raise BoxError(self, "tex")
