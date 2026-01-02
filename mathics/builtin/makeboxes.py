# -*- coding: utf-8 -*-
"""
Low-level Format definitions
"""


from mathics.core.atoms import Integer
from mathics.core.attributes import A_HOLD_ALL_COMPLETE, A_READ_PROTECTED
from mathics.core.builtin import Builtin, Predefined
from mathics.core.symbols import Symbol
from mathics.eval.makeboxes import (
    eval_generic_makeboxes,
    eval_infix,
    eval_makeboxes_fullform,
    eval_postprefix,
    format_element,
    parenthesize,
)

# TODO: Differently from the current implementation, MakeBoxes should only
# accept as its format field the symbols in `$BoxForms`. This is something to
# fix in a following step, changing the way in which Format and MakeBoxes work.


class BoxForms_(Predefined):
    r"""
    <url>:WMA link:https://reference.wolfram.com/language/ref/\$BoxForms.html</url>

    <dl>
      <dt>'\$BoxForms'
      <dd>contains the list of box formats.
    </dl>

    >> $BoxForms
     = ...
    """

    attributes = A_READ_PROTECTED
    name = "$BoxForms"
    rules = {"$BoxForms": "{StandardForm, TraditionalForm}"}
    summary_text = "the list of box formats"


class MakeBoxes(Builtin):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/MakeBoxes.html</url>

    <dl>
      <dt>'MakeBoxes'[$expr$]
      <dd>is a low-level formatting primitive that converts $expr$
        to box form, without evaluating it.
      <dt>'\\( ... \\)'
      <dd>directly inputs box objects.
    </dl>

    String representation of boxes
    >> \\(x \\^ 2\\)
     = SuperscriptBox[x, 2]

    >> \\(x \\_ 2\\)
     = SubscriptBox[x, 2]

    >> \\( a \\+ b \\% c\\)
     = UnderoverscriptBox[a, b, c]

    >> \\( a \\& b \\% c\\)
     = UnderoverscriptBox[a, c, b]

    #> \\( \\@ 5 \\)
     = SqrtBox[5]

    >> \\(x \\& y \\)
     = OverscriptBox[x, y]

    >> \\(x \\+ y \\)
     = UnderscriptBox[x, y]

    #> \\( x \\^ 2 \\_ 4 \\)
     = SuperscriptBox[x, SubscriptBox[2, 4]]

    ## Tests for issue 151 (infix operators in heads)
    #> (a + b)[x]
     = (a + b)[x]
    #> (a b)[x]
     = (a b)[x]
    #> (a <> b)[x]
     : String expected.
     = (a <> b)[x]
    """

    attributes = A_HOLD_ALL_COMPLETE

    rules = {
        "MakeBoxes[Infix[head_[elements___]], "
        "    f:StandardForm|TraditionalForm|OutputForm|InputForm]": (
            'MakeBoxes[Infix[head[elements], StringForm["~`1`~", head]], f]'
        ),
        "MakeBoxes[expr_]": "MakeBoxes[expr, StandardForm]",
        "MakeBoxes[(form:StandardForm|TraditionalForm|OutputForm|TeXForm|"
        "MathMLForm)[expr_], StandardForm|TraditionalForm]": ("MakeBoxes[expr, form]"),
        "MakeBoxes[(form:StandardForm|OutputForm|MathMLForm|TeXForm)[expr_], OutputForm]": "MakeBoxes[expr, form]",
        "MakeBoxes[(form:InputForm)[expr_], StandardForm|TraditionalForm|OutputForm]": "StyleBox[MakeBoxes[expr, form], ShowStringCharacters->True]",
        "MakeBoxes[PrecedenceForm[expr_, prec_], f_]": "MakeBoxes[expr, f]",
        "MakeBoxes[Style[expr_, OptionsPattern[Style]], f_]": (
            "StyleBox[MakeBoxes[expr, f], "
            "ImageSizeMultipliers -> OptionValue[ImageSizeMultipliers]]"
        ),
    }
    summary_text = "settable low-level translator from expression to display boxes"

    def eval_fullform(self, expr, evaluation):
        """MakeBoxes[expr_, FullForm]"""
        return eval_makeboxes_fullform(expr, evaluation)

    def eval_general(self, expr, f, evaluation):
        """MakeBoxes[expr_,
        f:TraditionalForm|StandardForm|OutputForm|InputForm]"""
        return eval_generic_makeboxes(self, expr, f, evaluation)

    def eval_outerprecedenceform(self, expr, precedence, form, evaluation):
        """MakeBoxes[PrecedenceForm[expr_, precedence_],
        form:StandardForm|TraditionalForm|OutputForm|InputForm]"""

        py_precedence = precedence.get_int_value()
        boxes = MakeBoxes(expr, form)
        return parenthesize(py_precedence, expr, boxes, True)

    def eval_postprefix(self, p, expr, h, precedence, form, evaluation):
        """MakeBoxes[(p:Prefix|Postfix)[expr_, h_, precedence_:None],
        form:StandardForm|TraditionalForm|OutputForm|InputForm]"""
        return eval_postprefix(self, p, expr, h, precedence, form, evaluation)

    def eval_infix(
        self, expr, operator, precedence: Integer, grouping, form: Symbol, evaluation
    ):
        """MakeBoxes[Infix[expr_, operator_, precedence_:None, grouping_:None], form:StandardForm|TraditionalForm|OutputForm|InputForm]"""
        return eval_infix(self, expr, operator, precedence, grouping, form, evaluation)


class ToBoxes(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ToBoxes.html</url>

    <dl>
      <dt>'ToBoxes'[$expr$]
      <dd>evaluates $expr$ and converts the result to box form.
    </dl>

    Unlike 'MakeBoxes', 'ToBoxes' evaluates its argument:
    >> ToBoxes[a + a]
     = RowBox[{2,  , a}]

    >> ToBoxes[a + b]
     = RowBox[{a, +, b}]
    >> ToBoxes[a ^ b] // FullForm
     = SuperscriptBox["a", "b"]
    """

    summary_text = "produce the display boxes of an evaluated expression"

    def eval(self, expr, form, evaluation):
        "ToBoxes[expr_, form_:StandardForm]"

        form_name = form.get_name()
        if form_name is None:
            evaluation.message("ToBoxes", "boxfmt", form)
        boxes = format_element(expr, evaluation, form)
        return boxes
