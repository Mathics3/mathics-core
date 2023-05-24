# -*- coding: utf-8 -*-
"""
Formatting constructs are represented as a hierarchy of low-level \
symbolic "boxes".

The routines here assist in boxing at the bottom of the hierarchy. \
At the other end, the top level, we have a Notebook which is just a \
collection of Expressions usually contained in boxes.
"""
# Docs are not yet ready for prime time. Maybe after release 6.0.0.
no_doc = True

from mathics.builtin.base import Builtin
from mathics.builtin.box.expression import BoxExpression
from mathics.builtin.options import options_to_rules
from mathics.core.atoms import Atom, String
from mathics.core.attributes import A_HOLD_ALL_COMPLETE, A_PROTECTED, A_READ_PROTECTED
from mathics.core.element import BoxElementMixin
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import BoxConstructError
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolFullForm
from mathics.core.systemsymbols import (
    SymbolFractionBox,
    SymbolRowBox,
    SymbolSqrtBox,
    SymbolStandardForm,
    SymbolSubscriptBox,
    SymbolSubsuperscriptBox,
    SymbolSuperscriptBox,
)
from mathics.eval.makeboxes import eval_makeboxes


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
        if x.has_form("MakeBoxes", None):
            x_boxed = x.evaluate(evaluation)
        else:
            x_boxed = eval_makeboxes(x, evaluation)
        if isinstance(x_boxed, BoxElementMixin):
            return x_boxed
        if isinstance(x_boxed, Atom):
            return to_boxes(x_boxed, evaluation, options)
    raise eval_makeboxes(Expression(SymbolFullForm, x), evaluation)


class BoxData(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/BoxData.html</url>

    <dl>
      <dt>'BoxData[...]'
      <dd>is a low-level representation of the contents of a typesetting
    cell.
    </dl>
    """

    summary_text = "low-level representation of the contents of a typesetting cell"


class ButtonBox(BoxExpression):
    """
    <dl>
      <dt>'ButtonBox[$boxes$]'
      <dd> is a low-level box construct that represents a button \
           in a notebook expression.
    </dl>
    """

    attributes = A_PROTECTED | A_READ_PROTECTED
    summary_text = "box construct for buttons"


# Right now this seems to be used only in GridBox.
def is_constant_list(list):
    if list:
        return all(item == list[0] for item in list[1:])
    return True


class FractionBox(BoxExpression):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/FractionBox.html</url>

    <dl>
      <dt>'FractionBox[$x$, $y$]'
      <dd> FractionBox[x, y] is a low-level formatting construct that represents $\frac{x}{y}$.
    </dl>
    """

    options = {
        "MultilineFunction": "Automatic",
        "FractionLine": "Automatic",
    }

    def eval(self, num, den, evaluation: Evaluation, options: dict):
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
        if not elements:
            raise BoxConstructError

        options = self.get_option_values(elements=elements[1:], evaluation=evaluation)
        expr = elements[0]
        if not expr.has_form("List", None):
            if not all(element.has_form("List", None) for element in expr.elements):
                raise BoxConstructError
        items = [
            element.elements if element.has_form("List", None) else element
            for element in expr.elements
        ]
        if not is_constant_list([len(row) for row in items if isinstance(row, tuple)]):
            max_len = max(len(items) for item in items)
            empty_string = String("")

            def complete_rows(row):
                if isinstance(row, tuple):
                    return row + (max_len - len(row)) * (empty_string,)
                return row

            items = [complete_rows(row) for row in items]

        return items, options


class InterpretationBox(BoxExpression):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/InterpretationBox.html</url>

    <dl>
      <dt>'InterpretationBox[{...}, expr]'
      <dd> is a low-level box construct that displays as boxes, but is \
           interpreted on input as expr.
    </dl>

    >> A = InterpretationBox["Pepe", 4]
     = InterpretationBox["Four", 4]
    >> DisplayForm[A]
     = Four
    >> ToExpression[A] + 4
     = 8
    """

    attributes = A_HOLD_ALL_COMPLETE | A_PROTECTED | A_READ_PROTECTED
    summary_text = "box associated to an input expression"

    def eval_to_expression(boxexpr, form, evaluation):
        """ToExpression[boxexpr_IntepretationBox, form___]"""
        return boxexpr.elements[1]

    def eval_display(boxexpr, evaluation):
        """DisplayForm[boxexpr_IntepretationBox]"""
        return boxexpr.elements[0]


class RowBox(BoxExpression):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/RowBox.html</url>
    <dl>
      <dt>'RowBox[{...}]'
      <dd>is a box construct that represents a sequence of boxes arranged in \
          a horizontal row.
    </dl>
    """

    summary_text = "horizontal arrange of boxes"

    def __repr__(self):
        return "RowBox[List[" + self.items.__repr__() + "]]"

    def eval_list(self, boxes, evaluation):
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
        self._elements = self.items

    def to_expression(self) -> Expression:
        """
        returns an expression that can be evaluated. This is needed
        to implement the interface of normal Expressions, for example, when a boxed expression
        is manipulated to produce a new boxed expression.

        For instance, consider the following definition:
        ```
        MakeBoxes[{items___}, StandardForm] := RowBox[{"[", Sequence @@ Riffle[MakeBoxes /@ {items}, " "], "]"}]
        ```
        Here, MakeBoxes is applied over the items, then ``Riffle`` the elements of the result, convert them into
        a sequence and finally, a ``RowBox`` is built. Then, riffle needs an expression as an argument. To get it,
        in the apply method, this function must be called.
        """
        if self._elements is None:
            self._elements = tuple(
                item.to_expression() if isinstance(item, BoxElementMixin) else item
                for item in self.items
            )

        return Expression(SymbolRowBox, ListExpression(*self._elements))


class ShowStringCharacters(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ShowStringCharacters.html</url>
    <dl>
      <dt>'ShowStringCharacters'
      <dd>is an option for Cell that directs whether to display '"' in strings.
    </dl>

    <ul>
    <li>'ShowStringCharacters' is usually 'False' for output cells and 'True' for input cells.
    <li>'ShowStringCharacters' is often set in styles rather than in individual cells.
    </ul>

    <i>This option can sometimes be output, but currently it is not interpreted.</i>
    """

    summary_text = "cell option directing wither show show quotes around strings"


class SqrtBox(BoxExpression):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SqrtData.html</url>
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

    def eval_index(self, radicand, index, evaluation: Evaluation, options: dict):
        """SqrtBox[radicand_, index_, OptionsPattern[]]"""
        radicand_box, index_box = (
            to_boxes(radicand, evaluation, options),
            to_boxes(index, evaluation, options),
        )
        return SqrtBox(radicand_box, index_box, **options)

    def eval(self, radicand, evaluation: Evaluation, options: dict):
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


class StyleBox(BoxExpression):
    """

    <url>:WMA link: https://reference.wolfram.com/language/ref/StyleBox.html</url>
    <dl>
      <dt>'StyleBox[boxes, options]'
      <dd> is a low-level representation of boxes  to be shown with the specified option settings.

      <dt>'StyleBox[boxes, style]'
      <dd> uses the option setting for the specified style in the current notebook.
    </dl>
    """

    options = {"ShowStringCharacters": "True", "$OptionSyntax": "Ignore"}
    attributes = A_PROTECTED | A_READ_PROTECTED
    summary_text = "associate boxes with styles"

    def eval_options(self, boxes, evaluation: Evaluation, options: dict):
        """StyleBox[boxes_, OptionsPattern[]]"""
        return StyleBox(boxes, style="", **options)

    def eval_style(self, boxes, style, evaluation: Evaluation, options: dict):
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

    #    attributes =  A_PROTECTED | A_READ_PROTECTED

    options = {
        "MultilineFunction": "Automatic",
    }

    def eval(self, a, b, evaluation: Evaluation, options: dict):
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
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SubsuperscriptBox.html</url>

    <dl>
      <dt>'SubsuperscriptBox[$a$, $b$, $c$]'
      <dd>is a box construct that represents $a_b^c$.
    </dl>
    """

    options = {
        "MultilineFunction": "Automatic",
    }

    def eval(self, a, b, c, evaluation: Evaluation, options: dict):
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
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SuperscriptBox.html</url>
    <dl>
      <dt>'SuperscriptBox[$a$, $b$]'
      <dd>is a box construct that represents $a^b$.
    </dl>

    """

    options = {
        "MultilineFunction": "Automatic",
    }

    def eval(self, a, b, evaluation: Evaluation, options: dict):
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


class TagBox(BoxExpression):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/TagBox.html</url>

    <dl>
      <dt>'TagBox[boxes, tag]'
      <dd> is a low-level box construct that displays as
    boxes but is interpreted on input as expr
    </dl>
    """

    attributes = A_HOLD_ALL_COMPLETE | A_PROTECTED | A_READ_PROTECTED
    summary_text = "box tag with a head"


class TemplateBox(BoxExpression):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/TemplateBox.html</url>
    <dl>
      <dt>'TemplateBox[{$box_1$, $box_2$,...}, tag]'
      <dd>is a low-level box structure that parameterizes the display and evaluation of the boxes $box_i$ .
    </dl>
    """

    attributes = A_HOLD_ALL_COMPLETE | A_PROTECTED | A_READ_PROTECTED
    summary_text = "parametrized box"


class TextData(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/TextData.html</url>

    <dl>
      <dt>'TextData[...]'
      <dd>is a low-level representation of the contents of a textual
    cell.
    </dl>
    """

    summary_text = "low-level representation of the contents of a textual cell."


class TooltipBox(BoxExpression):
    """
    ## <url>
    ## :WMA link:
    ## https://reference.wolfram.com/language/ref/TooltipBox.html</url>

    <dl>
      <dt>'TooltipBox[{...}]'
      <dd>undocumented...
    </dl>
    """

    summary_text = "box for showing tooltips"
