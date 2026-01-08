# FIXME: split these forms up further.
# MathML and TeXForm feel more closely related since they go with
# specific kinds of interpreters: LaTeX and MathML

# SympyForm and PythonForm feel related since are our own hacky thing
# (and mostly broken for now)

# NumberForm, TableForm, and MatrixForm seem closely related since
# they seem to be relevant for particular kinds of structures rather
# than applicable to all kinds of expressions.

"""
Form Functions
"""
from typing import Optional

from mathics.builtin.box.layout import InterpretationBox, RowBox, StyleBox, TagBox
from mathics.builtin.forms.base import FormBaseClass
from mathics.core.atoms import Integer, Real, String, StringFromPython
from mathics.core.builtin import Builtin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.number import dps
from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolFullForm,
    SymbolNull,
    SymbolTrue,
)
from mathics.core.systemsymbols import (
    SymbolAutomatic,
    SymbolInfinity,
    SymbolInputForm,
    SymbolMakeBoxes,
    SymbolNumberForm,
    SymbolRowBox,
    SymbolRuleDelayed,
    SymbolSuperscriptBox,
)
from mathics.eval.makeboxes import (
    NumberForm_to_String,
    StringLParen,
    StringRParen,
    eval_baseform,
    eval_makeboxes_fullform,
    eval_mathmlform,
    eval_tableform,
    eval_texform,
)
from mathics.form import render_input_form


class BaseForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/BaseForm.html</url>

    <dl>
      <dt>'BaseForm'[$expr$, $n$]
      <dd>prints numbers in $expr$ in base $n$.
    </dl>

    A binary integer:
    >> BaseForm[33, 2]
     = 100001_2

    A hexadecimal number:
    >> BaseForm[234, 16]
     = ea_16

    A binary real number:
    >> BaseForm[12.3, 2]
     = 1100.01001100110011001_2

    >> BaseForm[-42, 16]
     = -2a_16

    >> BaseForm[x, 2]
     = x

    >> BaseForm[12, 3] // FullForm
     = BaseForm[12, 3]

    Bases must be between 2 and 36:
    >> BaseForm[12, -3]
     : Positive machine-sized integer expected at position 2 in BaseForm[12, -3].
     = BaseForm[12, -3]
    >> BaseForm[12, 100]
     : Requested base 100 must be between 2 and 36.
     = BaseForm[12, 100]
    """

    in_outputforms = True
    in_printforms = False
    summary_text = "print with all numbers given in a base"
    messages = {
        "intpm": (
            "Positive machine-sized integer expected at position 2 in "
            "BaseForm[`1`, `2`]."
        ),
        "basf": "Requested base `1` must be between 2 and 36.",
    }

    def eval_makeboxes(self, expr, n, f, evaluation: Evaluation):
        """MakeBoxes[BaseForm[expr_, n_],
        f:StandardForm|TraditionalForm|OutputForm]"""
        return eval_baseform(self, expr, n, f, evaluation)


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
    in_printforms = True
    summary_text = "underlying M-Expression representation"

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

    # This can causes the TeX to fail
    # >> MathMLForm[Graphics[Text["\u03bc"]]]
    #  = ...

    ## The <mo> should contain U+2062 INVISIBLE TIMES
    ## MathMLForm[MatrixForm[{{2*a, 0},{0,0}}]]
    = ...
    """

    in_outputforms = True
    in_printforms = True

    summary_text = "formatted expression as MathML commands"

    def eval_mathml(self, expr, evaluation) -> Expression:
        "MakeBoxes[expr_, MathMLForm]"
        return eval_mathmlform(expr, evaluation)


class InputForm(FormBaseClass):
    r"""
     <url>
       :WMA link:
       https://reference.wolfram.com/language/ref/InputForm.html</url>

     <dl>
       <dt>'InputForm'[$expr$]
       <dd>displays $expr$ in an unambiguous form suitable for input to Mathics3.
     </dl>

     'InputForm' produces one-dimensional output that is suitable for input to Mathics3:

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
    summary_text = "plain-text input format"

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


class _NumberForm(Builtin):
    """
    Base class for NumberForm, AccountingForm, EngineeringForm, and ScientificForm.
    """

    default_ExponentFunction = None
    default_NumberFormat = None

    messages = {
        "npad": "Value for option NumberPadding -> `1` should be a string or a pair of strings.",
        "dblk": "Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.",
        "npt": "Value for option `1` -> `2` is expected to be a string.",
        "nsgn": "Value for option NumberSigns -> `1` should be a pair of strings or two pairs of strings.",
        "nspr": "Value for option NumberSeparator -> `1` should be a string or a pair of strings.",
        "opttf": "Value of option `1` -> `2` should be True or False.",
        "estep": "Value of option `1` -> `2` is not a positive integer.",
        "iprf": "Formatting specification `1` should be a positive integer or a pair of positive integers.",  # NumberFormat only
        "sigz": "In addition to the number of digits requested, one or more zeros will appear as placeholders.",
    }

    def check_options(self, options: dict, evaluation: Evaluation):
        """
        Checks options are valid and converts them to python.
        """
        result = {}
        for option_name in self.options:
            method = getattr(self, "check_" + option_name)
            arg = options["System`" + option_name]
            value = method(arg, evaluation)
            if value is None:
                return None
            result[option_name] = value
        return result

    def check_DigitBlock(self, value, evaluation: Evaluation):
        py_value = value.get_int_value()
        if value.sameQ(SymbolInfinity):
            return [0, 0]
        if py_value is not None and py_value > 0:
            return [py_value, py_value]
        if value.has_form("List", 2):
            nleft, nright = value.elements
            py_left, py_right = nleft.get_int_value(), nright.get_int_value()
            if nleft.sameQ(SymbolInfinity):
                nleft = 0
            elif py_left is not None and py_left > 0:
                nleft = py_left
            else:
                nleft = None
            if nright.sameQ(SymbolInfinity):
                nright = 0
            elif py_right is not None and py_right > 0:
                nright = py_right
            else:
                nright = None
            result = [nleft, nright]
            if None not in result:
                return result
        evaluation.message(self.get_name(), "dblk", value)

    def check_ExponentFunction(self, value, evaluation: Evaluation):
        if value.sameQ(SymbolAutomatic):
            return self.default_ExponentFunction

        def exp_function(x):
            return Expression(value, x).evaluate(evaluation)

        return exp_function

    def check_NumberFormat(self, value, evaluation: Evaluation):
        if value.sameQ(SymbolAutomatic):
            return self.default_NumberFormat

        def num_function(man, base, exp, options):
            return Expression(value, man, base, exp).evaluate(evaluation)

        return num_function

    def check_NumberMultiplier(self, value, evaluation: Evaluation):
        result = value.get_string_value()
        if result is None:
            evaluation.message(self.get_name(), "npt", "NumberMultiplier", value)
        return result

    def check_NumberPoint(self, value, evaluation: Evaluation):
        result = value.get_string_value()
        if result is None:
            evaluation.message(self.get_name(), "npt", "NumberPoint", value)
        return result

    def check_ExponentStep(self, value, evaluation: Evaluation):
        result = value.get_int_value()
        if result is None or result <= 0:
            evaluation.message(self.get_name(), "estep", "ExponentStep", value)
            return
        return result

    def check_SignPadding(self, value, evaluation: Evaluation):
        if value.sameQ(SymbolTrue):
            return True
        elif value.sameQ(SymbolFalse):
            return False
        evaluation.message(self.get_name(), "opttf", value)

    def _check_List2str(self, value, msg, evaluation: Evaluation):
        if value.has_form("List", 2):
            result = [element.get_string_value() for element in value.elements]
            if None not in result:
                return result
        evaluation.message(self.get_name(), msg, value)

    def check_NumberSigns(self, value, evaluation: Evaluation):
        return self._check_List2str(value, "nsgn", evaluation)

    def check_NumberPadding(self, value, evaluation: Evaluation):
        return self._check_List2str(value, "npad", evaluation)

    def check_NumberSeparator(self, value, evaluation: Evaluation):
        py_str = value.get_string_value()
        if py_str is not None:
            return [py_str, py_str]
        return self._check_List2str(value, "nspr", evaluation)


class NumberForm(_NumberForm):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/NumberForm.html</url>

    <dl>
      <dt>'NumberForm'[$expr$, $n$]
      <dd>prints a real number $expr$ with $n$-digits of precision.

      <dt>'NumberForm'[$expr$, {$n$, $f$}]
      <dd>prints with $n$-digits and $f$ digits to the right of the decimal point.
    </dl>

    >> NumberForm[N[Pi], 10]
     = 3.141592654

    >> NumberForm[N[Pi], {10, 6}]
     = 3.141593

    >> NumberForm[N[Pi]]
     = 3.14159

    """

    options = {
        "DigitBlock": "Infinity",
        "ExponentFunction": "Automatic",
        "ExponentStep": "1",
        "NumberFormat": "Automatic",
        "NumberMultiplier": '"×"',
        "NumberPadding": '{"", "0"}',
        "NumberPoint": '"."',
        "NumberSeparator": '{",", " "}',
        "NumberSigns": '{"-", ""}',
        "SignPadding": "False",
    }
    summary_text = "print at most a number of digits of all approximate real numbers in the expression"

    @staticmethod
    def default_ExponentFunction(value):
        n = value.get_int_value()
        if -5 <= n <= 5:
            return SymbolNull
        else:
            return value

    @staticmethod
    def default_NumberFormat(man, base, exp, options):
        py_exp = exp.get_string_value()
        if py_exp:
            mul = String(options["NumberMultiplier"])
            return Expression(
                SymbolRowBox,
                ListExpression(man, mul, Expression(SymbolSuperscriptBox, base, exp)),
            )
        else:
            return man

    def eval_list_n(self, expr, n, evaluation, options) -> Expression:
        "NumberForm[expr_List, n_, OptionsPattern[NumberForm]]"
        options = [
            Expression(SymbolRuleDelayed, Symbol(key), value)
            for key, value in options.items()
        ]
        return ListExpression(
            *[
                Expression(SymbolNumberForm, element, n, *options)
                for element in expr.elements
            ]
        )

    def eval_list_nf(self, expr, n, f, evaluation, options) -> Expression:
        "NumberForm[expr_List, {n_, f_}, OptionsPattern[NumberForm]]"
        options = [
            Expression(SymbolRuleDelayed, Symbol(key), value)
            for key, value in options.items()
        ]
        return ListExpression(
            *[
                Expression(SymbolNumberForm, element, ListExpression(n, f), *options)
                for element in expr.elements
            ],
        )

    def eval_makeboxes(self, expr, form, evaluation, options={}):
        """MakeBoxes[NumberForm[expr_, OptionsPattern[NumberForm]],
        form:StandardForm|TraditionalForm|OutputForm]"""

        fallback = Expression(SymbolMakeBoxes, expr, form)

        py_options = self.check_options(options, evaluation)
        if py_options is None:
            return fallback

        if isinstance(expr, Integer):
            py_n = len(str(abs(expr.get_int_value())))
        elif isinstance(expr, Real):
            if expr.is_machine_precision():
                py_n = 6
            else:
                py_n = dps(expr.get_precision())
        else:
            py_n = None

        if py_n is not None:
            py_options["_Form"] = form.get_name()
            return NumberForm_to_String(expr, py_n, None, evaluation, py_options)
        return Expression(SymbolMakeBoxes, expr, form)

    def eval_makeboxes_n(self, expr, n, form, evaluation, options={}):
        """MakeBoxes[NumberForm[expr_, n_?NotOptionQ, OptionsPattern[NumberForm]],
        form:StandardForm|TraditionalForm|OutputForm]"""

        fallback = Expression(SymbolMakeBoxes, expr, form)

        py_n = n.get_int_value()
        if py_n is None or py_n <= 0:
            evaluation.message("NumberForm", "iprf", n)
            return fallback

        py_options = self.check_options(options, evaluation)
        if py_options is None:
            return fallback

        if isinstance(expr, (Integer, Real)):
            py_options["_Form"] = form.get_name()
            return NumberForm_to_String(expr, py_n, None, evaluation, py_options)
        return Expression(SymbolMakeBoxes, expr, form)

    def eval_makeboxes_nf(self, expr, n, f, form, evaluation, options={}):
        """MakeBoxes[NumberForm[expr_, {n_, f_}, OptionsPattern[NumberForm]],
        form:StandardForm|TraditionalForm|OutputForm]"""

        fallback = Expression(SymbolMakeBoxes, expr, form)

        nf = ListExpression(n, f)
        py_n = n.get_int_value()
        py_f = f.get_int_value()
        if py_n is None or py_n <= 0 or py_f is None or py_f < 0:
            evaluation.message("NumberForm", "iprf", nf)
            return fallback

        py_options = self.check_options(options, evaluation)
        if py_options is None:
            return fallback

        if isinstance(expr, (Integer, Real)):
            py_options["_Form"] = form.get_name()
            return NumberForm_to_String(expr, py_n, py_f, evaluation, py_options)
        return Expression(SymbolMakeBoxes, expr, form)


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

    summary_text = "plain-text output format"


class PythonForm(FormBaseClass):
    """
    <dl>
      <dt>'PythonForm'[$expr$]
      <dd>returns an approximate equivalent of $expr$ in Python, when that is possible. We assume
      that Python has SymPy imported. No explicit import will be include in the result.
    </dl>

    >> PythonForm[Infinity]
    = math.inf
    >> PythonForm[Pi]
    = sympy.pi
    >> E // PythonForm
    = sympy.E
    >> {1, 2, 3} // PythonForm
    = (1, 2, 3)
    """

    in_outputforms = True
    in_printforms = True
    summary_text = "translate expressions as Python source code"
    # >> PythonForm[HoldForm[Sqrt[a^3]]]
    #  = sympy.sqrt{a**3} # or something like this

    def eval_python(self, expr, evaluation) -> Expression:
        "MakeBoxes[expr_, PythonForm]"

        def build_python_form(expr):
            if isinstance(expr, Symbol):
                return expr.to_sympy()
            return expr.to_python()

        try:
            python_equivalent = build_python_form(expr)
        except Exception:
            return
        return StringFromPython(python_equivalent)

    def eval(self, expr, evaluation) -> Expression:
        "PythonForm[expr_]"
        return self.eval_python(expr, evaluation)


class SympyForm(FormBaseClass):
    """
    <dl>
      <dt>'SympyForm'[$expr$]
      <dd>returns an Sympy $expr$ in Python. Sympy is used internally
      to implement a number of Mathics functions, like Simplify.
    </dl>

    >> SympyForm[Pi^2]
    = pi**2
    >> E^2 + 3E // SympyForm
    = exp(2) + 3*E
    """

    in_outputforms = True
    in_printforms = True
    summary_text = "translate expressions to SymPy"

    def eval_sympy(self, expr, evaluation) -> Optional[Expression]:
        "MakeBoxes[expr_, SympyForm]"

        try:
            sympy_equivalent = expr.to_sympy()
        except Exception:
            return
        return StringFromPython(sympy_equivalent)

    def eval(self, expr, evaluation) -> Expression:
        "SympyForm[expr_]"
        return self.eval_sympy(expr, evaluation)


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
    summary_text = "default output format"


class TraditionalForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/TraditionalForm.html</url>

    <dl>
      <dt>'TraditionalForm'[$expr$]
      <dd>displays $expr$ in a format similar to the traditional mathematical notation, where
           function evaluations are represented by brackets instead of square brackets.
    </dl>

    ## To pass this test, we need to improve the implementation of Element.format
    ## >> TraditionalForm[g[x]]
    ## = g(x)
    """

    in_outputforms = True
    in_printforms = True

    summary_text = "traditional output format"


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
    summary_text = "formatted expression as TeX commands"

    def eval_tex(self, expr, evaluation) -> Expression:
        "MakeBoxes[expr_, TeXForm]"
        return eval_texform(expr, evaluation)


class TableForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/TableForm.html</url>

    <dl>
      <dt>'TableForm'[$expr$]
      <dd>displays $expr$ as a table.
    </dl>

    >> TableForm[Array[a, {3,2}],TableDepth->1]
     = {a[1, 1], a[1, 2]}
     .
     . {a[2, 1], a[2, 2]}
     .
     . {a[3, 1], a[3, 2]}

    A table of Graphics:
    >> Table[Style[Graphics[{EdgeForm[{Black}], RGBColor[r,g,b], Rectangle[]}], ImageSizeMultipliers->{0.2, 1}], {r,0,1,1/2}, {g,0,1,1/2}, {b,0,1,1/2}] // TableForm
     = -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
    """

    in_outputforms = True
    in_printforms = False
    options = {"TableDepth": "Infinity"}
    summary_text = "format as a table"

    def eval_makeboxes(self, table, f, evaluation, options):
        """MakeBoxes[%(name)s[table_, OptionsPattern[%(name)s]],
        f:StandardForm|TraditionalForm|OutputForm]"""
        return eval_tableform(self, table, f, evaluation, options)


class MatrixForm(TableForm):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/MatrixForm.html</url>

    <dl>
      <dt>'MatrixForm'[$m$]
      <dd>displays a matrix $m$, hiding the underlying list structure.
    </dl>

    >> Array[a,{4,3}]//MatrixForm
     = a[1, 1]   a[1, 2]   a[1, 3]
     .
     . a[2, 1]   a[2, 2]   a[2, 3]
     .
     . a[3, 1]   a[3, 2]   a[3, 3]
     .
     . a[4, 1]   a[4, 2]   a[4, 3]
    """

    in_outputforms = True
    in_printforms = False
    summary_text = "format as a matrix"

    def eval_makeboxes_matrix(self, table, form, evaluation, options):
        """MakeBoxes[%(name)s[table_, OptionsPattern[%(name)s]],
        form:StandardForm|TraditionalForm]"""

        result = super(MatrixForm, self).eval_makeboxes(
            table, form, evaluation, options
        )
        if result.get_head_name() == "System`GridBox":
            return RowBox(StringLParen, result, StringRParen)
