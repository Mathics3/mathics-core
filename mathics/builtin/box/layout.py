# -*- coding: utf-8 -*-
r"""
Low-Level Notebook Structure

Formatting constructs are represented as a hierarchy of low-level \
symbolic "boxes".

The routines here assist in boxing at the bottom of the hierarchy, typically found when using in a notebook.

Boxing is recursively performed using on the <url>:Head:/doc/reference-of-built-in-symbols/atomic-elements-of-expressions/atomic-primitives/head/</url> of a \Mathics expression
"""

# The Box objects are `BoxElementMixin` objects. These objects are literal
# objects, and do `evaluate`.  Instead text render functions in
# `mathics.format` processes the `BoxElementMixin` object to produce
# output.


from typing import Tuple

from mathics.builtin.box.expression import BoxExpression
from mathics.builtin.options import filter_non_default_values, options_to_rules
from mathics.core.atoms import String
from mathics.core.attributes import A_HOLD_ALL_COMPLETE, A_PROTECTED, A_READ_PROTECTED
from mathics.core.builtin import Builtin
from mathics.core.element import BaseElement, BoxElementMixin, EvalMixin
from mathics.core.evaluation import Evaluation
from mathics.core.exceptions import BoxConstructError
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.eval.makeboxes import to_boxes

# This tells documentation how to sort this module
sort_order = "mathics.builtin.low-level-notebook-structure"


def elements_to_expressions(
    self: BoxExpression, elements: Tuple[BaseElement], options: dict
) -> Tuple[BaseElement]:
    """
    Return a tuple of Mathics3 normal atoms or expressions.
    """
    opts = sorted(options_to_rules(options, filter_non_default_values(self)))
    expr_elements = [
        elem.to_expression() if isinstance(elem, BoxExpression) else elem
        for elem in elements
    ]
    return tuple(expr_elements + opts)


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

    <url>:WMA link:https://reference.wolfram.com/language/ref/ButtonBox.html</url>
    <dl>
      <dt>'ButtonBox'[$boxes$]
      <dd> is a low-level box undocumented construct that represents a button \
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
      <dt>'FractionBox'[$x$, $y$]
      <dd> FractionBox[x, y] is a low-level formatting construct that represents $\frac{x}{y}$.
    </dl>
    """

    options = {
        "MultilineFunction": "Automatic",
        "FractionLine": "Automatic",
    }

    @property
    def elements(self):
        if self._elements is None:
            self._elements = elements_to_expressions(
                self,
                (
                    self.num,
                    self.den,
                ),
                self.box_options,
            )
        return self._elements

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


class GridBox(BoxExpression):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/GridBox.html</url>
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

    @property
    def elements(self):
        if self._elements is None:
            self._elements = elements_to_expressions(self, self.items, self.box_options)
        return self._elements

    def init(self, *elems, **kwargs):
        assert kwargs
        self.options = kwargs
        self.items = elems
        self._elements = elems

    def get_array(self, elements, evaluation):
        if not elements:
            raise BoxConstructError

        options = self.options
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
      <dt>'InterpretationBox[{...}, $expr$]'
      <dd> is a low-level box construct that displays as boxes, but is \
           interpreted on input as an $expr$.
    </dl>

    >> A = InterpretationBox["Four", 4]
     = InterpretationBox[Four, 4]
    >> DisplayForm[A]
     = Four
    >> ToExpression[A] + 4
     = 8
    """

    attributes = A_HOLD_ALL_COMPLETE | A_PROTECTED | A_READ_PROTECTED
    options = {
        "Editable": "Automatic",
        "AutoDelete": "Automatic",
    }
    summary_text = "box associated to an input expression"

    def __repr__(self):
        result = "InterpretationBox\n  " + repr(self.boxed)
        result += f"\n  {self.box_options}"
        return result

    def init(self, *expr, **options):
        self.boxed = expr[0]
        self.expr = expr[1]
        self.box_options = options

    @property
    def elements(self):
        if self._elements is None:
            self._elements = elements_to_expressions(
                self,
                (
                    self.boxed,
                    self.expr,
                ),
                self.box_options,
            )
        return self._elements

    def eval_create(self, reprs, expr, evaluation, options):
        """InterpretationBox[reprs_, expr_, OptionsPattern[]]"""
        # If the first element is not a literal, this
        # function evaluates it (because the symbol has
        # the attribute HoldAllComplete, this does not happen
        # in the evaluation loop). Then, if the result is a
        # BoxElementMixin, creates and return instance of `InterpretationBox`.
        if isinstance(reprs, EvalMixin):
            reprs = reprs.evaluate(evaluation)
        if not isinstance(reprs, BoxElementMixin):
            return
        return InterpretationBox(reprs, expr, **options)

    def eval_to_expression1(self, boxexpr, evaluation):
        """ToExpression[boxexpr_InterpretationBox]"""
        return boxexpr.expr

    def eval_to_expression2(self, boxexpr, form, evaluation):
        """ToExpression[boxexpr_InterpretationBox, form_]"""
        return boxexpr.expr

    def eval_display(self, boxexpr, evaluation):
        """DisplayForm[boxexpr_InterpretationBox]"""
        return boxexpr.boxed


class PaneBox(BoxExpression):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Pane.html</url>

    <dl>
      <dt>'PaneBox[expr]'
      <dd> is a low-level undocumented box construct, used in OutputForm.
    </dl>

    """

    attributes = A_HOLD_ALL_COMPLETE | A_PROTECTED | A_READ_PROTECTED
    summary_text = "box associated to pane"
    options = {"ImageSize": "Automatic"}

    @property
    def elements(self):
        if self._elements is None:
            self._elements = elements_to_expressions(
                self, (self.boxed,), self.box_options
            )
        return self._elements

    def init(self, expr, **options):
        self.boxed = expr
        self.box_options = options

    def eval_panebox1(self, expr, evaluation, options):
        "PaneBox[expr_String, OptionsPattern[]]"
        return PaneBox(expr, **options)

    def eval_display_form(boxexpr, form, evaluation, expression, options):
        """ToExpression[boxexpr_PaneBox, form_, OptionsPattern[]]"""
        return Expression(expression.head, boxexpr.elements[0], form).evaluate(
            evaluation
        )

    def eval_display(boxexpr, evaluation):
        """DisplayForm[boxexpr_PaneBox]"""
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
        return f"RowBox[{self.elements[0].__repr__()}]"

    @property
    def elements(self):
        if self._elements is None:
            self._elements = (
                ListExpression(
                    *(
                        item.to_expression()
                        if isinstance(item, BoxExpression)
                        else item
                        for item in self.items
                    )
                ),
            )
        return self._elements

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

    summary_text = "cell option directing whether show quotes around strings"


class SqrtBox(BoxExpression):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SqrtData.html</url>
    <dl>
      <dt>'SqrtBox'[$x$]
      <dd> is a low-level formatting construct that represents $\\sqrt{x}$.
      <dt>'SqrtBox'[$x$, $y$]
      <dd> represents $\\sqrt[y]{x}$.
    </dl>
    """

    options = {
        "MultilineFunction": "Automatic",
        "MinSize": "Automatic",
    }

    @property
    def elements(self):
        if self._elements is None:
            index = self.index
            if index is None:
                # self.box_options
                self._elements = elements_to_expressions(
                    self, (self.radicand,), self.box_options
                )
            else:
                self._elements = elements_to_expressions(
                    self, (self.radicand, index), self.box_options
                )
        return self._elements

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

    options = {
        "ShowStringCharacters": "False",
        "ShowSpecialCharacters": "False",
        "$OptionSyntax": "Ignore",
    }
    attributes = A_PROTECTED | A_READ_PROTECTED
    summary_text = "associate boxes with styles"

    def __repr__(self):
        return repr(self.to_expression())

    @property
    def elements(self):
        if self._elements is None:
            style = self.style
            boxes = self.boxes
            if style:
                self._elements = elements_to_expressions(
                    self, (boxes, style), self.box_options
                )
            else:
                self._elements = elements_to_expressions(
                    self, (boxes,), self.box_options
                )
        return self._elements

    def eval_options(self, boxes, evaluation: Evaluation, options: dict):
        """StyleBox[boxes_, OptionsPattern[]]"""
        if not isinstance(boxes, BoxElementMixin):
            return
        return StyleBox(boxes, style=None, **options)

    def eval_style(self, boxes, style, evaluation: Evaluation, options: dict):
        """StyleBox[boxes_, style_String, OptionsPattern[]]"""
        if not isinstance(boxes, BoxElementMixin):
            return
        return StyleBox(boxes, style=style, **options)

    def get_string_value(self) -> str:
        box = self.boxes
        if isinstance(box, String):
            return box.value
        return ""

    def init(self, boxes, style=None, **options):
        # This implementation supersedes Expression.process_style_box
        if isinstance(boxes, StyleBox):
            options.update(boxes.box_options)
            boxes = boxes.boxes
        self.style = style
        self.box_options = options
        assert options is not None
        self.boxes = boxes
        assert isinstance(
            self.boxes, BoxElementMixin
        ), f"{type(self.boxes)},{self.boxes}"


class SubscriptBox(BoxExpression):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/SubscriptBox.html</url>
    <dl>
      <dt>'SubscriptBox'[$a$, $b$]
      <dd>is a box construct that represents $a_b$.
    </dl>

    ## >> MakeBoxes[x_{3}]
    ##  = Subscript[x, 3]
    ## >> ToBoxes[%]
    ## = SubscriptBox[x, 3]
    """

    #    attributes =  A_PROTECTED | A_READ_PROTECTED

    options = {
        "MultilineFunction": "Automatic",
    }

    @property
    def elements(self):
        if self._elements is None:
            self._elements = elements_to_expressions(
                self, (self.base, self.subindex), self.box_options
            )
        return self._elements

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


class SubsuperscriptBox(BoxExpression):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SubsuperscriptBox.html</url>

    <dl>
      <dt>'SubsuperscriptBox'[$a$, $b$, $c$]
      <dd>is a box construct that represents $a_b^c$.
    </dl>
    """

    options = {
        "MultilineFunction": "Automatic",
    }

    @property
    def elements(self):
        if self._elements is None:
            # self.box_options
            self._elements = elements_to_expressions(
                (
                    self,
                    self.base,
                    self.subindex,
                    self.superindex,
                ),
                self.box_options,
            )
        return self._elements

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


class SuperscriptBox(BoxExpression):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/SuperscriptBox.html</url>
    <dl>
      <dt>'SuperscriptBox'[$a$, $b$]
      <dd>is a box construct that represents $a^b$.
    </dl>

    """

    options = {
        "MultilineFunction": "Automatic",
    }

    @property
    def elements(self):
        if self._elements is None:
            self._elements = elements_to_expressions(
                self,
                (
                    self.base,
                    self.superindex,
                ),
                self.box_options,
            )
        return self._elements

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

    attributes = A_PROTECTED | A_READ_PROTECTED
    summary_text = "box tag with a head"

    def init(self, *elems, **kwargs):
        self.box_options = kwargs
        self.form = elems[1]
        self.boxed = elems[0]
        assert isinstance(self.boxed, BoxElementMixin), f"{type(self.boxes)}"

    @property
    def elements(self):
        if self._elements is None:
            self._elements = elements_to_expressions(
                self,
                (
                    self.boxed,
                    self.form,
                ),
                self.box_options,
            )
        return self._elements

    def eval_tagbox(self, expr, form: Symbol, evaluation: Evaluation):
        """TagBox[expr_, form_Symbol]"""
        options = {}
        expr = to_boxes(expr, evaluation, options)
        assert isinstance(expr, BoxElementMixin), f"{expr}"
        return TagBox(expr, form, **options)


class TemplateBox(BoxExpression):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/TemplateBox.html</url>
    <dl>
      <dt>'TemplateBox'[{$box_1$, $box_2$,...}, tag]
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
