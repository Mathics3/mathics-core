# -*- coding: utf-8 -*-
"""
Low-level Format definitions
"""


from mathics.core.atoms import Integer
from mathics.core.attributes import A_HOLD_ALL_COMPLETE, A_READ_PROTECTED
from mathics.core.builtin import Builtin, Predefined
from mathics.core.symbols import Symbol
from mathics.format.box import (
    eval_generic_makeboxes,
    eval_makeboxes_fullform,
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
        "MakeBoxes[expr_]": "MakeBoxes[expr, StandardForm]",
        # The following rule is temporal.
        "MakeBoxes[expr_, form:(TeXForm|MathMLForm)]": "MakeBoxes[form[expr], StandardForm]",
        (
            "MakeBoxes[(form:StandardForm|TraditionalForm)"
            "[expr_], StandardForm|TraditionalForm]"
        ): ("MakeBoxes[expr, form]"),
    }
    summary_text = "settable low-level translator from expression to display boxes"

    def eval_general(self, expr, f, evaluation):
        """MakeBoxes[expr_, f:TraditionalForm|StandardForm]"""
        return eval_generic_makeboxes(expr, f, evaluation)


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
