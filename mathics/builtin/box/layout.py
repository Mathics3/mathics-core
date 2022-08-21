# -*- coding: utf-8 -*-

"""
Formatting constructs are represented as a hierarchy of low-level symbolic "boxes".

The routines here assist in boxing at the bottom of the hierarchy. At the other end, the top level, we have a Notebook which is just a collection of Expressions usually contained in boxes.
"""

from mathics.builtin.base import BoxExpression, Builtin
from mathics.builtin.exceptions import BoxConstructError
from mathics.builtin.options import options_to_rules

from mathics.core.atoms import Atom, String
from mathics.core.attributes import hold_all_complete, protected, read_protected
from mathics.core.element import BoxElementMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolMakeBoxes
from mathics.core.systemsymbols import SymbolRowBox, SymbolStandardForm

SymbolFractionBox = Symbol("System`FractionBox")
SymbolSubscriptBox = Symbol("System`SubscriptBox")
SymbolSubsuperscriptBox = Symbol("System`SubsuperscriptBox")
SymbolSuperscriptBox = Symbol("System`SuperscriptBox")
SymbolSqrtBox = Symbol("System`SqrtBox")


# this temporarily replace the _BoxedString class
def _boxed_string(string: str, **options):
    from mathics.core.atoms import String

    return StyleBox(String(string), **options)


def to_boxes(x, evaluation: Evaluation, options={}) -> BoxElementMixin:
    """
    This function takes the expression ``x``
    and tries to reduce it to a ``BoxElementMixin``
    expression unsing an evaluation object.
    """
    if isinstance(x, BoxElementMixin):
        return x
    if isinstance(x, Atom):
        x = x.atom_to_boxes(SymbolStandardForm, evaluation)
        return to_boxes(x, evaluation, options)
    if isinstance(x, Expression):
        if not x.has_form("MakeBoxes", None):
            x = Expression(SymbolMakeBoxes, x)
        x_boxed = x.evaluate(evaluation)
        if isinstance(x_boxed, BoxElementMixin):
            return x_boxed
        if isinstance(x_boxed, Atom):
            return to_boxes(x_boxed, evaluation, options)
    raise Exception(x, "cannot be boxed.")


class BoxData(Builtin):
    """
    <dl>
      <dt>'BoxData[...]'
      <dd>is a low-level representation of the contents of a typesetting
    cell.
    </dl>
    """

    summary_text = "low-level representation of the contents of a typesetting cell"


class TextData(Builtin):
    """
    <dl>
      <dt>'TextData[...]'
      <dd>is a low-level representation of the contents of a textual
    cell.
    </dl>
    """

    summary_text = "low-level representation of the contents of a textual cell."


class ButtonBox(BoxExpression):
    """
    <dl>
      <dt>'ButtonBox[$boxes$]'
      <dd> is a low-level box construct that represents a button in a notebook expression.
    </dl>
    """

    attributes = protected | read_protected
    summary_text = "box construct for buttons"


# Right now this seems to be used only in GridBox.
def is_constant_list(list):
    if list:
        return all(item == list[0] for item in list[1:])
    return True


class GridBox(BoxExpression):
    r"""
    <dl>
      <dt>'GridBox[{{...}, {...}}]'
      <dd>is a box construct that represents a sequence of boxes arranged in a grid.
    </dl>

    #> Grid[{{a,bc},{d,e}}, ColumnAlignments:>Symbol["Rig"<>"ht"]]
     = a   bc
     .
     . d   e

    #> TeXForm@Grid[{{a,bc},{d,e}}, ColumnAlignments->Left]
     = \begin{array}{ll} a & \text{bc}\\ d & e\end{array}

    #> TeXForm[TableForm[{{a,b},{c,d}}]]
     = \begin{array}{cc} a & b\\ c & d\end{array}

    # >> MathMLForm[TableForm[{{a,b},{c,d}}]]
    #  = ...
    """
    options = {"ColumnAlignments": "Center"}
    summary_text = "low-level representation of an arbitrary 2D layout"

    # TODO: elements in the GridBox should be stored as an array with
    # elements in its evaluated form.

    def get_array(self, elements, evaluation):
        options = self.get_option_values(elements=elements[1:], evaluation=evaluation)
        if not elements:
            raise BoxConstructError
        expr = elements[0]
        if not expr.has_form("List", None):
            if not all(element.has_form("List", None) for element in expr.elements):
                raise BoxConstructError
        items = [element.elements for element in expr.elements]
        if not is_constant_list([len(row) for row in items]):
            raise BoxConstructError
        return items, options


class InterpretationBox(BoxExpression):
    """
    <dl>
      <dt>'InterpretationBox[{...}, expr]'
      <dd> is a low-level box construct that displays as
    boxes but is interpreted on input as expr.
    </dl>

    >> A = InterpretationBox["Pepe", 4]
     = InterpretationBox["Four", 4]
    >> DisplayForm[A]
     = Four
    >> ToExpression[A] + 4
     = 8
    """

    attributes = hold_all_complete | protected | read_protected
    summary_text = "box associated to an input expression"

    def apply_to_expression(boxexpr, form, evaluation):
        """ToExpression[boxexpr_IntepretationBox, form___]"""
        return boxexpr.elements[1]

    def apply_display(boxexpr, evaluation):
        """DisplayForm[boxexpr_IntepretationBox]"""
        return boxexpr.elements[0]


class SubscriptBox(BoxExpression):
    """
    <dl>
      <dt>'SubscriptBox[$a$, $b$]'
      <dd>is a box construct that represents $a_b$.
    </dl>

    >> MakeBoxes[x_{3}]
     = Subscript[x, 3]
    >> ToBoxes[%]
     = SubscriptBox[x, 3]
    """

    #    attributes =  Protected | ReadProtected

    options = {
        "MultilineFunction": "Automatic",
    }

    def apply(self, a, b, evaluation, options):
        """SubscriptBox[a_, b__, OptionsPattern[]]"""
        a_box, b_box = (
            to_boxes(a, evaluation, options),
            to_boxes(b, evaluation, options),
        )
        return SubscriptBox(a_box, b_box, **options)

    def init(self, a, b, **options):
        self.box_options = options.copy()
        if not (isinstance(a, BoxElementMixin) and isinstance(b, BoxElementMixin)):
            raise Exception((a, b), "are not boxes")
        self.base = a
        self.subindex = b

    def to_expression(self):
        """
        returns an evaluable expression.
        """
        return Expression(SymbolSubscriptBox, self.base, self.subindex)


class SubsuperscriptBox(BoxExpression):
    """
    <dl>
      <dt>'SubsuperscriptBox[$a$, $b$, $c$]'
      <dd>is a box construct that represents $a_b^c$.
    </dl>
    """

    options = {
        "MultilineFunction": "Automatic",
    }

    def apply(self, a, b, c, evaluation, options):
        """SubsuperscriptBox[a_, b__, c__, OptionsPattern[]]"""
        a_box, b_box, c_box = (
            to_boxes(a, evaluation, options),
            to_boxes(b, evaluation, options),
            to_boxes(c, evaluation, options),
        )
        return SubsuperscriptBox(a_box, b_box, c_box, **options)

    def init(self, a, b, c, **options):
        self.box_options = options.copy()
        if not all(isinstance(x, BoxElementMixin) for x in (a, b, c)):
            raise Exception((a, b, c), "are not boxes")
        self.base = a
        self.subindex = b
        self.superindex = c

    def to_expression(self):
        """
        returns an evaluable expression.
        """
        return Expression(
            SymbolSubsuperscriptBox, self.base, self.subindex, self.superindex
        )


class SuperscriptBox(BoxExpression):
    """
    <dl>
      <dt>'SuperscriptBox[$a$, $b$]'
      <dd>is a box construct that represents $a^b$.
    </dl>

    """

    options = {
        "MultilineFunction": "Automatic",
    }

    def apply(self, a, b, evaluation, options):
        """SuperscriptBox[a_, b__, OptionsPattern[]]"""
        a_box, b_box = (
            to_boxes(a, evaluation, options),
            to_boxes(b, evaluation, options),
        )
        return SuperscriptBox(a_box, b_box, **options)

    def init(self, a, b, **options):
        self.box_options = options.copy()
        if not all(isinstance(x, BoxElementMixin) for x in (a, b)):
            raise Exception((a, b), "are not boxes")
        self.base = a
        self.superindex = b

    def to_expression(self):
        """
        returns an evaluable expression.
        """
        return Expression(SymbolSuperscriptBox, self.base, self.superindex)


class RowBox(BoxExpression):
    """
    <dl>
      <dt>'RowBox[{...}]'
      <dd>is a box construct that represents a sequence of boxes arranged in a horizontal row.
    </dl>
    """

    summary_text = "horizontal arrange of boxes"

    def __repr__(self):
        return "RowBox[List[" + self.items.__repr__() + "]]"

    def apply_list(self, boxes, evaluation):
        """RowBox[boxes_List]"""
        boxes = boxes.evaluate(evaluation)
        items = tuple(to_boxes(b, evaluation) for b in boxes.elements)
        result = RowBox(*items)
        return result

    def init(self, *items, **kwargs):
        # TODO: check that each element is an string or a BoxElementMixin
        self.box_options = {}
        if isinstance(items[0], Expression):
            if len(items) != 1:
                raise Exception(
                    items, "is not a List[] or a list of Strings or BoxElementMixin"
                )
            if items[0].has_form("List", None):
                items = items[0]._elements
            else:
                raise Exception(
                    items, "is not a List[] or a list of Strings or BoxElementMixin"
                )

        def check_item(item):
            if isinstance(item, String):
                return item
            if not isinstance(item, BoxElementMixin):
                raise Exception(
                    item, "is not a List[] or a list of Strings or BoxElementMixin"
                )
            return item

        self.items = tuple((check_item(item) for item in items))
        self._elements = None

    def to_expression(self) -> Expression:
        """
        returns an expression that can be evaluated. This is needed
        to implement the interface of normal Expressions, for example, when a boxed expression
        is manipulated to produce a new boxed expression.

        For instance, consider the folling definition:
        ```
        MakeBoxes[{items___}, StandardForm] := RowBox[{"[", Sequence @@ Riffle[MakeBoxes /@ {items}, " "], "]"}]
        ```
        Here, MakeBoxes is applied over the items, then ``Riffle`` the elements of the result, convert them into
        a sequence and finally, a ``RowBox`` is built. Then, riffle needs an expression as an argument. To get it,
        in the apply method, this function must be called.
        """
        if self._elements is None:
            items = tuple(
                item.to_expression() if isinstance(item, BoxElementMixin) else item
                for item in self.items
            )

            self._elements = Expression(SymbolRowBox, ListExpression(*items))
        return self._elements


class StyleBox(BoxExpression):
    """
    <dl>
      <dt>'StyleBox[boxes, options]'
      <dd> is a low-level representation of boxes
     to be shown with the specified option settings.
      <dt>'StyleBox[boxes, style]'
      <dd> uses the option setting for the specified style in
    the current notebook.
    </dl>
    """

    options = {"ShowStringCharacters": "True", "$OptionSyntax": "Ignore"}
    attributes = protected | read_protected
    summary_text = "associate boxes with styles"

    def apply_options(self, boxes, evaluation, options):
        """StyleBox[boxes_, OptionsPattern[]]"""
        return StyleBox(boxes, style="", **options)

    def apply_style(self, boxes, style, evaluation, options):
        """StyleBox[boxes_, style_String, OptionsPattern[]]"""
        return StyleBox(boxes, style=style, **options)

    def get_string_value(self):
        box = self.boxes
        if isinstance(box, String):
            return box.value
        return None

    def init(self, boxes, style=None, **options):
        # This implementation superseeds Expresion.process_style_box
        if isinstance(boxes, StyleBox):
            options.update(boxes.box_options)
            boxes = boxes.boxes
        self.style = style
        self.box_options = options
        self.boxes = boxes

    def to_expression(self):
        if self.style:
            return Expression(
                Symbol(self.get_name()),
                self.boxes,
                self.style,
                *options_to_rules(self.box_options),
            )
        return Expression(
            Symbol(self.get_name()), self.boxes, *options_to_rules(self.box_options)
        )


class TagBox(BoxExpression):
    """
    <dl>
      <dt>'TagBox[boxes, tag]'
      <dd> is a low-level box construct that displays as
    boxes but is interpreted on input as expr
    </dl>
    """

    attributes = hold_all_complete | protected | read_protected
    summary_text = "box tag with a head"


class TemplateBox(BoxExpression):
    """
    <dl>
      <dt>'TemplateBox[{$box_1$, $box_2$,...}, tag]'
      <dd>is a low-level box structure that parameterizes the display and evaluation of the boxes $box_i$ .
    </dl>
    """

    attributes = hold_all_complete | protected | read_protected
    summary_text = "parametrized box"


class TooltipBox(BoxExpression):
    """
    <dl>
      <dt>'TooltipBox[{...}]'
      <dd>undocumented...
    </dl>
    """

    summary_text = "box for showing tooltips"


class FractionBox(BoxExpression):
    """
    <dl>
      <dt>'FractionBox[$x$, $y$]'
      <dd> FractionBox[x, y] is a low-level formatting construct that represents $\frac{x}{y}$.
    </dl>
    """

    options = {
        "MultilineFunction": "Automatic",
        "FractionLine": "Automatic",
    }

    def apply(self, num, den, evaluation, options):
        """FractionBox[num_, den_, OptionsPattern[]]"""
        num_box, den_box = (
            to_boxes(num, evaluation, options),
            to_boxes(den, evaluation, options),
        )
        return FractionBox(num_box, den_box, **options)

    def init(self, num, den, **options):
        self.num = num
        self.den = den
        self.box_options = options

    def to_expression(self):
        return Expression(SymbolFractionBox, self.num, self.den)


class SqrtBox(BoxExpression):
    """
    <dl>
      <dt>'SqrtBox[$x$]'
      <dd> is a low-level formatting construct that represents $\\sqrt{x}$.
      <dt>'SqrtBox[$x$, $y$]'
      <dd> represents $\\sqrt[y]{x}$.
    </dl>
    """

    options = {
        "MultilineFunction": "Automatic",
        "MinSize": "Automatic",
    }

    def apply_index(self, radicand, index, evaluation, options):
        """SqrtBox[radicand_, index_, OptionsPattern[]]"""
        radicand_box, index_box = (
            to_boxes(radicand, evaluation, options),
            to_boxes(index, evaluation, options),
        )
        return SqrtBox(radicand_box, index_box, **options)

    def apply(self, radicand, evaluation, options):
        """SqrtBox[radicand_, OptionsPattern[]]"""
        radicand_box = to_boxes(radicand, evaluation, options)
        return SqrtBox(radicand_box, None, **options)

    def init(self, radicand, index=None, **options):
        self.radicand = radicand
        self.index = index
        self.box_options = options

    def to_expression(self):
        if self.index:
            return Expression(SymbolSqrtBox, self.radicand, self.index)
        return Expression(SymbolSqrtBox, self.radicand)
