# -*- coding: utf-8 -*-

from mathics.builtin.base import BoxConstruct
from mathics.builtin.options import options_to_rules

from mathics.core.symbols import SymbolFalse, SymbolList, SymbolTrue, Symbol
from mathics.core.atoms import Atom, String
from mathics.core.attributes import hold_all_complete, protected, read_protected
from mathics.core.expression import Expression
from mathics.core.evaluation import Evaluation
from mathics.core.formatter import encode_mathml, encode_tex, extra_operators
from mathics.core.parser import is_symbol_name


def to_boxes(x, evaluation: Evaluation, options={}) -> BoxConstruct:
    """
    This function takes the expression ``x``
    and tries to reduce it to a ``BoxConstruct``
    expression unsing an evaluation object.
    """
    if isinstance(x, BoxConstruct):
        return x
    if isinstance(x, String):
        x = _BoxedString(x, options)
        return x
    if isinstance(x, Atom):
        x = x.atom_to_boxes(Symbol("StandardForm"), evaluation)
        if isinstance(x, String):
            return _BoxedString(x, options)
    if isinstance(x, Expression):
        if not x.has_form("MakeBoxes", None):
            x = Expression("MakeBoxes", x)
        x_boxed = x.evaluate(evaluation)
    if isinstance(x_boxed, BoxConstruct):
        return x_boxed
    if isinstance(x_boxed, Atom):
        return to_boxes(x_boxed, evaluation, options)
    raise Exception(x, "cannot be boxed.")


class _BoxedString(BoxConstruct):

    options = {
        "System`ShowStringCharacters": "False",
    }

    def init(self, string, options={}):
        self.value = string.value
        self.box_options = {
            "System`ShowStringCharacters": SymbolFalse,
        }
        self.box_options.update(options)

    def __repr__(self):
        return self.value

    def to_expression(self):
        return String(self.value)

    def boxes_to_text(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        value = self.value
        show_string_characters = options["System`ShowStringCharacters"]
        show_string_characters = show_string_characters is SymbolTrue
        if (
            not show_string_characters
            and value.startswith('"')  # nopep8
            and value.endswith('"')
        ):
            value = value[1:-1]

        return value

    def boxes_to_mathml(self, **options) -> str:
        from mathics.builtin import display_operators_set as operators

        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        show_string_characters = options["System`ShowStringCharacters"] is SymbolTrue
        text = self.value

        def render(format, string):
            encoded_text = encode_mathml(string)
            return format % encoded_text

        if text.startswith('"') and text.endswith('"'):
            if show_string_characters:
                return render("<ms>%s</ms>", text[1:-1])
            else:
                outtext = ""
                for line in text[1:-1].split("\n"):
                    outtext += render("<mtext>%s</mtext>", line)
                return outtext
        elif text and ("0" <= text[0] <= "9" or text[0] == "."):
            return render("<mn>%s</mn>", text)
        else:
            if text in operators or text in extra_operators:
                if text == "\u2146":
                    return render(
                        '<mo form="prefix" lspace="0.2em" rspace="0">%s</mo>', text
                    )
                if text == "\u2062":
                    return render(
                        '<mo form="prefix" lspace="0" rspace="0.2em">%s</mo>', text
                    )
                return render("<mo>%s</mo>", text)
            elif is_symbol_name(text):
                return render("<mi>%s</mi>", text)
            else:
                outtext = ""
                for line in text.split("\n"):
                    outtext += render("<mtext>%s</mtext>", line)
                return outtext

    def boxes_to_tex(self, **options) -> str:
        # from mathics.builtin import display_operators_set as operators

        _options = self.box_options.copy()
        _options.update(options)
        options = _options

        # operators = display_operators_set
        show_string_characters = options["System`ShowStringCharacters"] is SymbolTrue
        text = self.value

        def render(format, string, in_text=False):
            return format % encode_tex(string, in_text)

        if text.startswith('"') and text.endswith('"'):
            if show_string_characters:
                return render(r'\text{"%s"}', text[1:-1], in_text=True)
            else:
                return render(r"\text{%s}", text[1:-1], in_text=True)
        elif text and text[0] in "0123456789-.":
            return render("%s", text)
        else:
            # FIXME: this should be done in a better way.
            if text == "\u2032":
                return "'"
            elif text == "\u2032\u2032":
                return "''"
            elif text == "\u2062":
                return " "
            elif text == "\u221e":
                return r"\infty "
            elif text == "\u00d7":
                return r"\times "
            elif text in ("(", "[", "{"):
                return render(r"\left%s", text)
            elif text in (")", "]", "}"):
                return render(r"\right%s", text)
            elif text == "\u301a":
                return r"\left[\left["
            elif text == "\u301b":
                return r"\right]\right]"
            elif text == "," or text == ", ":
                return text
            elif text == "\u222b":
                return r"\int"
            # Tolerate WL or Unicode DifferentialD
            elif text in ("\u2146", "\U0001D451"):
                return r"\, d"
            elif text == "\u2211":
                return r"\sum"
            elif text == "\u220f":
                return r"\prod"
            elif len(text) > 1:
                return render(r"\text{%s}", text, in_text=True)
            else:
                return render("%s", text)


class ButtonBox(BoxConstruct):
    """
    <dl>
    <dt>'ButtonBox[$boxes$]'
        <dd> is a low-level box construct that represents a button in a
    notebook expression.
    </dl>
    """

    attributes = protected | read_protected
    summary_text = "box construct for buttons"


class InterpretationBox(BoxConstruct):
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


class SubscriptBox(BoxConstruct):
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
        """SubscriptBox[a_, b_, OptionsPattern[]]"""
        a_box, b_box = (
            to_boxes(a, evaluation, options),
            to_boxes(b, evaluation, options),
        )
        return SubscriptBox(a_box, b_box, options)

    def init(self, a, b, options):
        self.box_options = options.copy()
        if not (
            isinstance(a, (String, BoxConstruct))
            and isinstance(b, (String, BoxConstruct))
        ):
            raise Exception((a, b), "are not boxes")
        self.base = a
        self.subindex = b

    def to_expression(self):
        """
        returns an evaluable expression.
        """
        return Expression("SubscriptBox", self.base, self.subindex)

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


class SubsuperscriptBox(BoxConstruct):
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
        """SubsuperscriptBox[a_, b_, c_, OptionsPattern[]]"""
        a_box, b_box, c_box = (
            to_boxes(a, evaluation, options),
            to_boxes(b, evaluation, options),
            to_boxes(c, evaluation, options),
        )
        return SubsuperscriptBox(a_box, b_box, c_box, options)

    def init(self, a, b, c, options):
        self.box_options = options.copy()
        if not (
            isinstance(a, BoxConstruct)
            and isinstance(b, BoxConstruct)
            and isinstance(c, BoxConstruct)
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
            "SubsuperscriptBox", self.base, self.subindex, self.superindex
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


class SuperscriptBox(BoxConstruct):
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
        """SuperscriptBox[a_, b_, OptionsPattern[]]"""
        a_box, b_box = (
            to_boxes(a, evaluation, options),
            to_boxes(b, evaluation, options),
        )
        return SuperscriptBox(a_box, b_box, options)

    def init(self, a, b, options):
        self.box_options = options.copy()
        if not (isinstance(a, BoxConstruct) and isinstance(b, BoxConstruct)):
            raise Exception((a, b), "are not boxes")
        self.base = a
        self.superindex = b

    def to_expression(self):
        """
        returns an evaluable expression.
        """
        return Expression("SuperscriptBox", self.base, self.superindex)

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


class RowBox(BoxConstruct):
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
        # TODO: check that each element is an string or a BoxConstruct
        self.box_options = {}
        if isinstance(items[0], Expression):
            if len(items) != 1:
                raise Exception(
                    items, "is not a List[] or a list of Strings or BoxConstruct"
                )
            if items[0].has_form("List", None):
                items = items[0]._elements
            else:
                raise Exception(
                    items, "is not a List[] or a list of Strings or BoxConstruct"
                )
        for item in items:
            if not isinstance(item, BoxConstruct):
                raise Exception(
                    item, "is not a List[] or a list of Strings or BoxConstruct"
                )
        self.items = tuple(items)

        elements = []
        for item in items:
            if isinstance(item, BoxConstruct):
                elements.append(item.to_expression())
            else:
                elements.append(item)
        elements = Expression(SymbolList, *elements)
        self._elements = tuple((elements,))

    def to_expression(self):
        """
        returns an evaluable expression.
        """
        items = (item.to_expression() for item in self.items)
        result = Expression("RowBox", Expression("List", *items))
        return result

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


class StyleBox(BoxConstruct):
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
        options.pop("evaluation")
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
        return StyleBox(boxes, style="", options=options)

    def apply_style(self, boxes, style, evaluation, options):
        """StyleBox[boxes_, style_String, OptionsPattern[]]"""
        return StyleBox(boxes, style=style, options=options)

    def init(self, boxes, style=None, options={}):
        # This implementation superseeds Expresion.process_style_box
        self.style = style
        self.box_options = options
        # Here I need to check that is exactly
        # String and not a BoxedString
        if type(boxes) is String:
            self.boxes = _BoxedString(boxes)
        else:
            self.boxes = boxes

    def to_expression(self):
        if self.style:
            return Expression(
                self.get_name(),
                self.boxes,
                self.style,
                *options_to_rules(self.box_options)
            )
        return Expression(
            self.get_name(), self.boxes, *options_to_rules(self.box_options)
        )


class TagBox(BoxConstruct):
    """
    <dl>
    <dt>'TagBox[boxes, tag]'
        <dd> is a low-level box construct that displays as
    boxes but is interpreted on input as expr
    </dl>
    """

    attributes = hold_all_complete | protected | read_protected
    summary_text = "box tag with a head"


class TemplateBox(BoxConstruct):
    """
    <dl>
    <dt>'TemplateBox[{$box_1$, $box_2$,...}, tag]'
        <dd>is a low-level box structure that parameterizes the display and evaluation of the boxes $box_i$ .
    </dl>
    """

    attributes = hold_all_complete | protected | read_protected
    summary_text = "parametrized box"


class TooltipBox(BoxConstruct):
    """
    <dl>
    <dt>'TooltipBox[{...}]'
        <dd>undocumented...
    </dl>
    """

    summary_text = "box for showing tooltips"


class FractionBox(BoxConstruct):
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
        return FractionBox(num_box, den_box, options)

    def init(self, num, den, options={}):
        self.num = num
        self.den = den
        self.box_options = options

    def to_expression(self):
        return Expression("FractionBox", self.num, self.den)

    def boxes_to_text(self, **options):
        _options = self.box_options.copy()
        _options.update(options)
        options = _options
        return "/".join(
            [
                " ( " + element.boxes_to_text(**options) + " ) "
                for element in (self.num, self.den)
            ]
        )

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


class SqrtBox(BoxConstruct):
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
        return SqrtBox(radicand_box, index_box, options)

    def apply(self, radicand, evaluation, options):
        """SqrtBox[radicand_, OptionsPattern[]]"""
        radicand_box = to_boxes(radicand, evaluation, options)
        return SqrtBox(radicand_box, None, options)

    def init(self, radicand, index=None, options={}):
        self.radicand = radicand
        self.index = index
        self.box_options = options

    def to_expression(self):
        if self.index:
            return Expression("SqrtBox", self.radicand, self.index)
        return Expression("SqrtBox", self.radicand)

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
