# -*- coding: utf-8 -*-
"""
Low-level Format definitions
"""

from mathics.core.attributes import A_HOLD_ALL_COMPLETE
from mathics.core.builtin import Builtin
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolHoldForm
from mathics.format.box import format_element

# TODO: Differently from the current implementation, MakeBoxes should only
# accept as its format field the symbols in `$BoxForms`. This is something to
# fix in a following step, changing the way in which Format and MakeBoxes work.


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
    messages = {
        "boxfmt": (
            "`1` in `2` is not a box formatting type. "
            "A box formatting type is any member of $BoxForms."
        )
    }
    rules = {
        "MakeBoxes[expr_]": "MakeBoxes[expr, StandardForm]",
        # The following rule is temporal.
        "MakeBoxes[expr_, form:(TeXForm|MathMLForm)]": "MakeBoxes[form[expr], StandardForm]",
    }
    summary_text = "settable low-level translator from expression to display boxes"

    def eval_general(self, expr, f, evaluation):
        """MakeBoxes[expr_, f:StandardForm|TraditionalForm]"""
        return format_element(expr, evaluation, f)

    def eval_general_custom(self, expr, mbexpr, f, evaluation):
        """mbexpr:MakeBoxes[expr_, f_]"""
        if f not in evaluation.definitions.boxforms:
            expr = Expression(SymbolHoldForm, mbexpr)
            evaluation.message("MakeBoxes", "boxfmt", f, expr)
            return None

        return format_element(expr, evaluation, f)


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

    messages = {
        "boxfmt": (
            "`1` in `2` is not a box formatting type. "
            "A box formatting type is any member of $BoxForms."
        )
    }
    summary_text = "produce the display boxes of an evaluated expression"

    def eval(self, expr, tbexpr, form, evaluation):
        "tbexpr:ToBoxes[expr_, form_:StandardForm]"
        if form not in evaluation.definitions.boxforms:
            expr = Expression(SymbolHoldForm, tbexpr)
            evaluation.message("ToBoxes", "boxfmt", form, expr)
            return None

        boxes = format_element(expr, evaluation, form)
        return boxes
