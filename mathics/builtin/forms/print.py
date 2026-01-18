r"""
General-purpose Forms

A number of forms are suitable for formatting any kind of \Mathics expression.

The variable <url>:$PrintForms:
/doc/reference-of-built-in-symbols/forms-of-input-and-output/form-variables/$printforms/</url> \
contains a list of Forms \
that are in this category. After formatting the \Mathics expression, these removing mention of the form.

While Forms that appear in '$PrintForms' can be altered at run time, \
below are the functions that appear in '$PrintForms' at startup.
"""

from mathics.builtin.box.layout import InterpretationBox, StyleBox, TagBox
from mathics.builtin.forms.base import FormBaseClass
from mathics.core.atoms import String
from mathics.core.expression import Expression
from mathics.core.symbols import SymbolFalse, SymbolFullForm, SymbolTrue
from mathics.core.systemsymbols import SymbolInputForm
from mathics.form import render_input_form
from mathics.format.makeboxes import (
    eval_makeboxes_fullform,
    eval_mathmlform,
    eval_texform,
)

sort_order = "mathics.builtin.forms.general-purpose-forms"


class FullForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/FullForm.html</url>

    <dl>
      <dt>'FullForm'[$expr$]
      <dd>displays the underlying form of $expr$.
    </dl>

    >> FullForm[a + b * c]
     = Plus[a, Times[b, c]]
    >> FullForm[2/3]
     = Rational[2, 3]
    >> FullForm["A string"]
     = "A string"
    """

    in_outputforms = True
    in_printforms = False
    summary_text = "format expression in underlying M-Expression representation"

    def eval_makeboxes(self, expr, fmt, evaluation):
        """MakeBoxes[FullForm[expr_], fmt_]"""
        fullform_box = eval_makeboxes_fullform(expr, evaluation)
        style_box = StyleBox(
            fullform_box,
            **{
                "System`ShowSpecialCharacters": SymbolFalse,
                "System`ShowStringCharacters": SymbolTrue,
                "System`NumberMarks": SymbolTrue,
            },
        )
        return TagBox(style_box, SymbolFullForm)


class InputForm(FormBaseClass):
    r"""
     <url>
       :WMA link:
       https://reference.wolfram.com/language/ref/InputForm.html</url>

     <dl>
       <dt>'InputForm'[$expr$]
       <dd>displays $expr$ in an unambiguous form suitable for input to \Mathics.
     </dl>

     'InputForm' produces one-dimensional output that is suitable for input to \Mathics:

     >> InputForm["A string"]
      = "A string"

     >> InputForm[f'[x]]
      = Derivative[1][f][x]

     >> InputForm[Derivative[1, 0][f][x]]
      = Derivative[1, 0][f][x]

     'InputForm' shows arithmetic expressions in traditional mathematical notation:

     >> 2+F[x] // InputForm
      = 2 + F[x]

     Compare this to 'FullForm':

     >> 2+F[x] // FullForm
      = Plus[2, F[x]]

    'InputForm' output can be altered via 'Format' assignment :

     >> Format[Foo[x], InputForm] := Bar

     >> Foo[x] // InputForm
      = Bar

    In contrast, 'FullForm' output is not altered via 'Format' assignment :
     >> Format[Foo[x], InputForm] := Baz

     >> Foo[x] // FullForm
      = Foo[x]
    """

    in_outputforms = True
    in_printforms = True
    summary_text = "format expression suitable for Mathics3 input"

    # TODO: eventually, remove OutputForm in the second argument.
    def eval_makeboxes(self, expr, evaluation):
        """MakeBoxes[InputForm[expr_], Alternatives[StandardForm,TraditionalForm,OutputForm]]"""

        inputform = String(render_input_form(expr, evaluation))
        inputform = StyleBox(
            inputform,
            **{
                "System`ShowSpecialCharacters": SymbolFalse,
                "System`ShowStringCharacters": SymbolTrue,
                "System`NumberMarks": SymbolTrue,
            },
        )
        expr = Expression(SymbolInputForm, expr)
        return InterpretationBox(
            inputform,
            expr,
            **{"System`Editable": SymbolTrue, "System`AutoDelete": SymbolTrue},
        )


class MathMLForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/MathMLForm.html</url>

    <dl>
      <dt>'MathMLForm'[$expr$]
      <dd>displays $expr$ as a MathML expression.
    </dl>

    >> MathMLForm[HoldForm[Sqrt[a^3]]]
     = ...

    ## Test cases for Unicode - redo please as a real test
    >> MathMLForm[\\[Mu]]
    = ...

    ## This can causes the TeX to fail
    ## >> MathMLForm[Graphics[Text["\u03bc"]]]
    ##  = ...

    ## The <mo> should contain U+2062 INVISIBLE TIMES
    ## MathMLForm[MatrixForm[{{2*a, 0},{0,0}}]]
    = ...
    """

    in_outputforms = True
    in_printforms = True

    summary_text = "format expression as MathML commands"

    def eval_mathml(self, expr, evaluation) -> Expression:
        "MakeBoxes[MathMLForm[expr_], (OutputForm|StandardForm|TraditionalForm)]"
        return eval_mathmlform(expr, evaluation)


class OutputForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/OutputForm.html</url>

    <dl>
      <dt>'OutputForm'[$expr$]
      <dd>displays $expr$ in a plain-text form.
    </dl>

    >> OutputForm[f'[x]]
     = f'[x]
    >> OutputForm[Derivative[1, 0][f][x]]
     = Derivative[1, 0][f][x]

    'OutputForm' is used by default:
    >> OutputForm[{"A string", a + b}]
     = {A string, a + b}
    >> {"A string", a + b}
     = {A string, a + b}
    >> OutputForm[Graphics[Rectangle[]]]
     = -Graphics-
    """

    summary_text = "format expression in plain text"
    # Remove me at the end of the refactor
    rules = {"MakeBoxes[OutputForm[expr_], form_]": "MakeBoxes[expr, OutputForm]"}


class StandardForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/StandardForm.html</url>

    <dl>
      <dt>'StandardForm'[$expr$]
      <dd>displays $expr$ in the default form.
    </dl>

    >> StandardForm[a + b * c]
     = a+b c
    >> StandardForm["A string"]
     = A string
    >> f'[x]
     = f'[x]
    """

    in_outputforms = True
    in_printforms = True
    summary_text = "format expression the default way"


class TraditionalForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/TraditionalForm.html</url>

    <dl>
      <dt>'TraditionalForm'[$expr$]
      <dd>displays $expr$ in a format similar to the traditional mathematical notation, where \
           function evaluations are represented by brackets instead of square brackets.
    </dl>

    ## To pass this test, we need to improve the implementation of Element.format
    ## >> TraditionalForm[g[x]]
    ## = g(x)
    """

    in_outputforms = True
    in_printforms = True

    summary_text = "format expression using traditional mathematical notation"


class TeXForm(FormBaseClass):
    r"""
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/TeXForm.html</url>

    <dl>
      <dt>'TeXForm'[$expr$]
      <dd>displays $expr$ using TeX math mode commands.
    </dl>

    >> TeXForm[HoldForm[Sqrt[a^3]]]
     = \sqrt{a^3}
    """

    in_outputforms = True
    in_printforms = True
    summary_text = "format expression as LaTeX commands"

    def eval_tex(self, expr, evaluation) -> Expression:
        "MakeBoxes[TeXForm[expr_], (OutputForm|StandardForm|TraditionalForm)]"
        return eval_texform(expr, evaluation)
