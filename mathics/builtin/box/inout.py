# -*- coding: utf-8 -*-

from mathics.builtin.base import BoxExpression
from mathics.builtin.exceptions import BoxConstructError
from mathics.builtin.options import options_to_rules

from mathics.core.atoms import Atom, String, SymbolString
from mathics.core.attributes import hold_all_complete, protected, read_protected
from mathics.core.element import BoxElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.formatter import (
    _BoxedString,
)
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
    from mathics.builtin.box.inout import StyleBox
    from mathics.core.atoms import String

    return StyleBox(String(string), **options)


def to_boxes(x, evaluation: Evaluation, options={}) -> BoxElement:
    """
    This function takes the expression ``x``
    and tries to reduce it to a ``BoxElement``
    expression unsing an evaluation object.
    """
    if isinstance(x, BoxElement):
        return x
    if isinstance(x, String):
        x = _BoxedString(x.value, **options)
        return x
    if isinstance(x, Atom):
        x = x.atom_to_boxes(SymbolStandardForm, evaluation)
        return to_boxes(x, evaluation, options)
    if isinstance(x, Expression):
        if not x.has_form("MakeBoxes", None):
            x = Expression(SymbolMakeBoxes, x)
        x_boxed = x.evaluate(evaluation)
        if isinstance(x_boxed, BoxElement):
            return x_boxed
        if isinstance(x_boxed, Atom):
            return to_boxes(x_boxed, evaluation, options)
    raise Exception(x, "cannot be boxed.")


class ButtonBox(BoxExpression):
    """
    <dl>
      <dt>'ButtonBox[$boxes$]'
      <dd> is a low-level box construct that represents a button in a
    notebook expression.
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
      <dd>is a box construct that represents a sequence of boxes
        arranged in a grid.
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

    def boxes_to_tex(self, elements=None, **box_options) -> str:
        if not elements:
            elements = self._elements
        evaluation = box_options.get("evaluation")
        items, options = self.get_array(elements, evaluation)
        new_box_options = box_options.copy()
        new_box_options["inside_list"] = True
        column_alignments = options["System`ColumnAlignments"].get_name()
        try:
            column_alignments = {
                "System`Center": "c",
                "System`Left": "l",
                "System`Right": "r",
            }[column_alignments]
        except KeyError:
            # invalid column alignment
            raise BoxConstructError
        column_count = 0
        for row in items:
            column_count = max(column_count, len(row))
        result = r"\begin{array}{%s} " % (column_alignments * column_count)
        for index, row in enumerate(items):
            result += " & ".join(
                item.evaluate(evaluation).boxes_to_tex(**new_box_options)
                for item in row
            )
            if index != len(items) - 1:
                result += "\\\\ "
        result += r"\end{array}"
        return result

    def boxes_to_mathml(self, elements=None, **box_options) -> str:
        if not elements:
            elements = self._elements
        evaluation = box_options.get("evaluation")
        items, options = self.get_array(elements, evaluation)
        attrs = {}
        column_alignments = options["System`ColumnAlignments"].get_name()
        try:
            attrs["columnalign"] = {
                "System`Center": "center",
                "System`Left": "left",
                "System`Right": "right",
            }[column_alignments]
        except KeyError:
            # invalid column alignment
            raise BoxConstructError
        joined_attrs = " ".join(f'{name}="{value}"' for name, value in attrs.items())
        result = f"<mtable {joined_attrs}>\n"
        new_box_options = box_options.copy()
        new_box_options["inside_list"] = True
        for row in items:
            result += "<mtr>"
            for item in row:
                result += f"<mtd {joined_attrs}>{item.evaluate(evaluation).boxes_to_mathml(**new_box_options)}</mtd>"
            result += "</mtr>\n"
        result += "</mtable>"
        return result

    def boxes_to_text(self, elements=None, **box_options) -> str:
        if not elements:
            elements = self._elements
        evaluation = box_options.get("evaluation")
        items, options = self.get_array(elements, evaluation)
        result = ""
        if not items:
            return ""
        widths = [0] * len(items[0])
        cells = [
            [
                item.evaluate(evaluation).boxes_to_text(**box_options).splitlines()
                for item in row
            ]
            for row in items
        ]
        for row in cells:
            for index, cell in enumerate(row):
                if index >= len(widths):
                    raise BoxConstructError
                for line in cell:
                    widths[index] = max(widths[index], len(line))
        for row_index, row in enumerate(cells):
            if row_index > 0:
                result += "\n"
            k = 0
            while True:
                line_exists = False
                line = ""
                for cell_index, cell in enumerate(row):
                    if len(cell) > k:
                        line_exists = True
                        text = cell[k]
                    else:
                        text = ""
                    line += text
                    if cell_index < len(row) - 1:
                        line += " " * (widths[cell_index] - len(text))
                        # if cell_index < len(row) - 1:
                        line += "   "
                if line_exists:
                    result += line + "\n"
                else:
                    break
                k += 1
        return result


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
        if not (
            isinstance(a, (String, BoxElement)) and isinstance(b, (String, BoxElement))
        ):
            raise Exception((a, b), "are not boxes")
        self.base = a
        self.subindex = b

    def to_expression(self):
        """
        returns an evaluable expression.
        """
        return Expression(SymbolSubscriptBox, self.base, self.subindex)

    def boxes_to_text(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return "Subscript[%s, %s]" % (
            self.base.boxes_to_text(**options),
            self.subindex.boxes_to_text(**options),
        )

    def boxes_to_mathml(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return "<msub>%s %s</msub>" % (
            self.base.boxes_to_mathml(**options),
            self.subindex.boxes_to_mathml(**options),
        )

    def boxes_to_tex(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return "%s_%s" % (
            self.tex_block(self.base.boxes_to_tex(**options), True),
            self.tex_block(self.subindex.boxes_to_tex(**options)),
        )


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
        if not (
            isinstance(a, BoxElement)
            and isinstance(b, BoxElement)
            and isinstance(c, BoxElement)
        ):
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

    def boxes_to_text(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return "Subsuperscript[%s, %s, %s]" % (
            self.base.boxes_to_text(**options),
            self.subindex.boxes_to_text(**options),
            self.superindex.boxes_to_text(**options),
        )

    def boxes_to_mathml(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        options["inside_row"] = True
        return "<msubsup>%s %s %s</msubsup>" % (
            self.base.boxes_to_mathml(**options),
            self.subindex.boxes_to_mathml(**options),
            self.superindex.boxes_to_mathml(**options),
        )

    def boxes_to_tex(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return "%s_%s^%s" % (
            self.tex_block(self.base.boxes_to_tex(**options), True),
            self.tex_block(self.subindex.boxes_to_tex(**options)),
            self.tex_block(self.superindex.boxes_to_tex(**options)),
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
        if not (
            isinstance(a, (BoxElement, String)) and isinstance(b, (BoxElement, String))
        ):
            raise Exception((a, b), "are not boxes")
        self.base = a
        self.superindex = b

    def to_expression(self):
        """
        returns an evaluable expression.
        """
        return Expression(SymbolSuperscriptBox, self.base, self.superindex)

    def boxes_to_text(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        if isinstance(self.superindex, (Atom, _BoxedString)):
            return "%s^%s" % (
                self.base.boxes_to_text(**options),
                self.superindex.boxes_to_text(**options),
            )

        return "%s^(%s)" % (
            self.base.boxes_to_text(**options),
            self.superindex.boxes_to_text(**options),
        )

    def boxes_to_mathml(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return "<msup>%s %s</msup>" % (
            self.base.boxes_to_mathml(**options),
            self.superindex.boxes_to_mathml(**options),
        )

    def boxes_to_tex(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        tex1 = self.base.boxes_to_tex(**options)

        sup_string = self.superindex.get_string_value()
        # Handle derivatives
        if sup_string == "\u2032":
            return "%s'" % tex1
        elif sup_string == "\u2032\u2032":
            return "%s''" % tex1
        else:
            base = self.tex_block(tex1, True)
            superindx = self.tex_block(self.superindex.boxes_to_tex(**options), True)
            if isinstance(self.superindex, _BoxedString):
                return "%s^%s" % (
                    base,
                    superindx,
                )
            else:
                return "%s^{%s}" % (
                    base,
                    superindx,
                )


class RowBox(BoxExpression):
    """
    <dl>
      <dt>'RowBox[{...}]'
      <dd>is a box construct that represents a sequence of boxes
        arranged in a horizontal row.
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
        # TODO: check that each element is an string or a BoxElement
        self.box_options = {}
        if isinstance(items[0], Expression):
            if len(items) != 1:
                raise Exception(
                    items, "is not a List[] or a list of Strings or BoxElement"
                )
            if items[0].has_form("List", None):
                items = items[0]._elements
            else:
                raise Exception(
                    items, "is not a List[] or a list of Strings or BoxElement"
                )

        def check_item(item):
            if isinstance(item, String):
                return _BoxedString(item.value)
            if not isinstance(item, BoxElement):
                raise Exception(
                    item, "is not a List[] or a list of Strings or BoxElement"
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
                item.to_expression() if isinstance(item, BoxElement) else item
                for item in self.items
            )

            self._elements = Expression(SymbolRowBox, ListExpression(*items))
        return self._elements

    def boxes_to_text(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return "".join([element.boxes_to_text(**options) for element in self.items])

    def boxes_to_tex(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return "".join([element.boxes_to_tex(**options) for element in self.items])

    def boxes_to_mathml(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        result = []
        inside_row = options.get("inside_row")
        # inside_list = options.get('inside_list')
        options = options.copy()

        def is_list_interior(content):
            if all(element.get_string_value() == "," for element in content[1::2]):
                return True
            return False

        is_list_row = False
        if (
            len(self.items) == 3
            and self.items[0].get_string_value() == "{"  # nopep8
            and self.items[2].get_string_value() == "}"
            and self.items[1].has_form("RowBox", 1)
        ):
            content = self.items[1].items
            if is_list_interior(content):
                is_list_row = True

        if not inside_row and is_list_interior(self.items):
            is_list_row = True

        if is_list_row:
            options["inside_list"] = True
        else:
            options["inside_row"] = True

        for element in self.items:
            result.append(element.boxes_to_mathml(**options))
        return "<mrow>%s</mrow>" % " ".join(result)


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

    def boxes_to_text(self, **options):
        options.pop("evaluation", None)
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return self.boxes.boxes_to_text(**options)

    def boxes_to_tex(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return self.boxes.boxes_to_tex(**options)

    def boxes_to_mathml(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return self.boxes.boxes_to_mathml(**options)

    def apply_options(self, boxes, evaluation, options):
        """StyleBox[boxes_, OptionsPattern[]]"""
        return StyleBox(boxes, style="", **options)

    def apply_style(self, boxes, style, evaluation, options):
        """StyleBox[boxes_, style_String, OptionsPattern[]]"""
        return StyleBox(boxes, style=style, **options)

    def get_string_value(self):
        box = self.boxes
        if isinstance(box, (String, _BoxedString)):
            return box.value
        return None

    def init(self, boxes, style=None, **options):
        # This implementation superseeds Expresion.process_style_box
        self.style = style
        self.box_options = options
        # Here I need to check that is exactly
        # String and not a BoxedString
        if type(boxes) is String:
            self.boxes = _BoxedString(boxes.value)
        else:
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

    def boxes_to_text(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        num_text = self.num.boxes_to_text(**options)
        den_text = self.den.boxes_to_text(**options)
        if isinstance(self.num, RowBox):
            num_text = f"({num_text})"
        if isinstance(self.den, RowBox):
            den_text = f"({den_text})"

        return " / ".join([num_text, den_text])

    def boxes_to_mathml(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return "<mfrac>%s %s</mfrac>" % (
            self.num.boxes_to_mathml(**options),
            self.den.boxes_to_mathml(**options),
        )

    def boxes_to_tex(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return "\\frac{%s}{%s}" % (
            self.num.boxes_to_tex(**options),
            self.den.boxes_to_tex(**options),
        )


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

    def boxes_to_text(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        if self.index:
            return "Sqrt[%s,%s]" % (
                self.radicand.boxes_to_text(**options),
                self.index.boxes_to_text(**options),
            )
        return "Sqrt[%s]" % (self.radicand.boxes_to_text(**options))

    def boxes_to_mathml(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        if self.index:
            return "<mroot> %s %s </mroot>" % (
                self.radicand.boxes_to_mathml(**options),
                self.index.boxes_to_mathml(**options),
            )

        return "<msqrt> %s </msqrt>" % self.radicand.boxes_to_mathml(**options)

    def boxes_to_tex(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        if self.index:
            return "\\sqrt[%s]{%s}" % (
                self.index.boxes_to_tex(**options),
                self.radicand.boxes_to_tex(**options),
            )
        return "\\sqrt{%s}" % (self.radicand.boxes_to_tex(**options))
