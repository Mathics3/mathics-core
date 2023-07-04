# FIXME: split these forms up further.
# MathML and TeXForm feel more closely related since they go with
# specific kinds of interpreters: LaTeX and MathML

# SympyForm and PythonForm feel related since are our own hacky thing
# (and mostly broken for now)

# NumberForm, TableForm, and MatrixForm seem closely related since
# they seem to be relevant for particular kinds of structures rather
# than applicable to all kinds of expressions.

"""
Forms which appear in '$OutputForms'.
"""
import re
from math import ceil
from typing import Optional

from mathics.builtin.base import Builtin
from mathics.builtin.box.layout import GridBox, RowBox, to_boxes
from mathics.builtin.forms.base import FormBaseClass
from mathics.builtin.makeboxes import MakeBoxes, number_form
from mathics.builtin.tensors import get_dimensions
from mathics.core.atoms import (
    Integer,
    MachineReal,
    PrecisionReal,
    Real,
    String,
    StringFromPython,
)
from mathics.core.evaluation import Evaluation
from mathics.core.expression import BoxError, Expression
from mathics.core.list import ListExpression
from mathics.core.number import (
    LOG2_10,
    RECONSTRUCT_MACHINE_PRECISION_DIGITS,
    convert_base,
    dps,
)
from mathics.core.symbols import (
    Symbol,
    SymbolFalse,
    SymbolFullForm,
    SymbolList,
    SymbolNull,
    SymbolTrue,
)
from mathics.core.systemsymbols import (
    SymbolAutomatic,
    SymbolInfinity,
    SymbolMakeBoxes,
    SymbolNumberForm,
    SymbolOutputForm,
    SymbolRowBox,
    SymbolRuleDelayed,
    SymbolSubscriptBox,
    SymbolSuperscriptBox,
)
from mathics.eval.makeboxes import StringLParen, StringRParen, format_element
from mathics.eval.testing_expressions import expr_min

MULTI_NEWLINE_RE = re.compile(r"\n{2,}")


class BaseForm(Builtin):
    """
    <dl>
      <dt>'BaseForm[$expr$, $n$]'
      <dd>prints numbers in $expr$ in base $n$.
    </dl>

    >> BaseForm[33, 2]
     = 100001_2

    >> BaseForm[234, 16]
     = ea_16

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

    #> BaseForm[0, 2]
     = 0_2
    #> BaseForm[0.0, 2]
     = 0.0_2

    #> BaseForm[N[Pi, 30], 16]
     = 3.243f6a8885a308d313198a2e_16
    """

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

        base = n.get_int_value()
        if base <= 0:
            evaluation.message("BaseForm", "intpm", expr, n)
            return None

        if isinstance(expr, PrecisionReal):
            x = expr.to_sympy()
            p = int(ceil(expr.get_precision() / LOG2_10) + 1)
        elif isinstance(expr, MachineReal):
            x = expr.value
            p = RECONSTRUCT_MACHINE_PRECISION_DIGITS
        elif isinstance(expr, Integer):
            x = expr.value
            p = 0
        else:
            return to_boxes(Expression(SymbolMakeBoxes, expr, f), evaluation)

        try:
            val = convert_base(x, base, p)
        except ValueError:
            evaluation.message("BaseForm", "basf", n)
            return

        if f is SymbolOutputForm:
            return to_boxes(String("%s_%d" % (val, base)), evaluation)
        else:
            return to_boxes(
                Expression(SymbolSubscriptBox, String(val), String(base)), evaluation
            )


class FullForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/FullForm.html</url>

    <dl>
      <dt>'FullForm[$expr$]'
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


class MathMLForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/MathMLForm.html</url>

    <dl>
      <dt>'MathMLForm[$expr$]'
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

        boxes = MakeBoxes(expr).evaluate(evaluation)
        try:
            mathml = boxes.boxes_to_mathml(evaluation=evaluation)
        except BoxError:
            evaluation.message(
                "General",
                "notboxes",
                Expression(SymbolFullForm, boxes).evaluate(evaluation),
            )
            mathml = ""
        is_a_picture = mathml[:6] == "<mtext"

        # mathml = '<math><mstyle displaystyle="true">%s</mstyle></math>' % mathml
        # #convert_box(boxes)
        query = evaluation.parse("Settings`$UseSansSerif")
        usesansserif = query.evaluate(evaluation).to_python()
        if not is_a_picture:
            if isinstance(usesansserif, bool) and usesansserif:
                mathml = '<mstyle mathvariant="sans-serif">%s</mstyle>' % mathml

        mathml = '<math display="block">%s</math>' % mathml  # convert_box(boxes)
        return Expression(SymbolRowBox, ListExpression(String(mathml)))


class InputForm(FormBaseClass):
    r"""
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/InputForm.html</url>

    <dl>
      <dt>'InputForm[$expr$]'
      <dd>displays $expr$ in an unambiguous form suitable for input.
    </dl>

    >> InputForm[a + b * c]
     = a + b*c
    >> InputForm["A string"]
     = "A string"
    >> InputForm[f'[x]]
     = Derivative[1][f][x]
    >> InputForm[Derivative[1, 0][f][x]]
     = Derivative[1, 0][f][x]
    #> InputForm[2 x ^ 2 + 4z!]
     = 2*x^2 + 4*z!
    #> InputForm["\$"]
     = "\\$"
    """

    in_outputforms = True
    in_printforms = True
    summary_text = "plain-text input format"


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
        elif py_value is not None and py_value > 0:
            return [py_value, py_value]
        elif value.has_form("List", 2):
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
    <dl>
      <dt>'NumberForm[$expr$, $n$]'
      <dd>prints a real number $expr$ with $n$-digits of precision.

      <dt>'NumberForm[$expr$, {$n$, $f$}]'
      <dd>prints with $n$-digits and $f$ digits to the right of the decimal point.
    </dl>

    >> NumberForm[N[Pi], 10]
     = 3.141592654

    >> NumberForm[N[Pi], {10, 5}]
     = 3.14159


    ## Undocumented edge cases
    #> NumberForm[Pi, 20]
     = Pi
    #> NumberForm[2/3, 10]
     = 2 / 3

    ## No n or f
    #> NumberForm[N[Pi]]
     = 3.14159
    #> NumberForm[N[Pi, 20]]
     = 3.1415926535897932385
    #> NumberForm[14310983091809]
     = 14310983091809

    ## Zero case
    #> z0 = 0.0;
    #> z1 = 0.0000000000000000000000000000;
    #> NumberForm[{z0, z1}, 10]
     = {0., 0.×10^-28}
    #> NumberForm[{z0, z1}, {10, 4}]
     = {0.0000, 0.0000×10^-28}

    ## Trailing zeros
    #> NumberForm[1.0, 10]
     = 1.
    #> NumberForm[1.000000000000000000000000, 10]
     = 1.000000000
    #> NumberForm[1.0, {10, 8}]
     = 1.00000000
    #> NumberForm[N[Pi, 33], 33]
     = 3.14159265358979323846264338327950

    ## Correct rounding - see sympy/issues/11472
    #> NumberForm[0.645658509, 6]
     = 0.645659
    #> NumberForm[N[1/7], 30]
     = 0.1428571428571428

    ## Integer case
    #> NumberForm[{0, 2, -415, 83515161451}, 5]
     = {0, 2, -415, 83515161451}
    #> NumberForm[{2^123, 2^123.}, 4, ExponentFunction -> ((#1) &)]
     = {10633823966279326983230456482242756608, 1.063×10^37}
    #> NumberForm[{0, 10, -512}, {10, 3}]
     = {0.000, 10.000, -512.000}

    ## Check arguments
    #> NumberForm[1.5, -4]
     : Formatting specification -4 should be a positive integer or a pair of positive integers.
     = 1.5
    #> NumberForm[1.5, {1.5, 2}]
     : Formatting specification {1.5, 2} should be a positive integer or a pair of positive integers.
     = 1.5
    #> NumberForm[1.5, {1, 2.5}]
     : Formatting specification {1, 2.5} should be a positive integer or a pair of positive integers.
     = 1.5

    ## Right padding
    #> NumberForm[153., 2]
     : In addition to the number of digits requested, one or more zeros will appear as placeholders.
     = 150.
    #> NumberForm[0.00125, 1]
     = 0.001
    #> NumberForm[10^5 N[Pi], {5, 3}]
     : In addition to the number of digits requested, one or more zeros will appear as placeholders.
     = 314160.000
    #> NumberForm[10^5 N[Pi], {6, 3}]
     = 314159.000
    #> NumberForm[10^5 N[Pi], {6, 10}]
     = 314159.0000000000
    #> NumberForm[1.0000000000000000000, 10, NumberPadding -> {"X", "Y"}]
     = X1.000000000

    ## Check options

    ## DigitBlock
    #> NumberForm[12345.123456789, 14, DigitBlock -> 3]
     = 12,345.123 456 789
    #> NumberForm[12345.12345678, 14, DigitBlock -> 3]
     = 12,345.123 456 78
    #> NumberForm[N[10^ 5 Pi], 15, DigitBlock -> {4, 2}]
     = 31,4159.26 53 58 97 9
    #> NumberForm[1.2345, 3, DigitBlock -> -4]
     : Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.
     = 1.2345
    #> NumberForm[1.2345, 3, DigitBlock -> x]
     : Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.
     = 1.2345
    #> NumberForm[1.2345, 3, DigitBlock -> {x, 3}]
     : Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.
     = 1.2345
    #> NumberForm[1.2345, 3, DigitBlock -> {5, -3}]
     : Value for option DigitBlock should be a positive integer, Infinity, or a pair of positive integers.
     = 1.2345

    ## ExponentFunction
    #> NumberForm[12345.123456789, 14, ExponentFunction -> ((#) &)]
     = 1.2345123456789×10^4
    #> NumberForm[12345.123456789, 14, ExponentFunction -> (Null&)]
     = 12345.123456789
    #> y = N[Pi^Range[-20, 40, 15]];
    #> NumberForm[y, 10, ExponentFunction -> (3 Quotient[#, 3] &)]
     =  {114.0256472×10^-12, 3.267763643×10^-3, 93.64804748×10^3, 2.683779414×10^12, 76.91214221×10^18}
    #> NumberForm[y, 10, ExponentFunction -> (Null &)]
     : In addition to the number of digits requested, one or more zeros will appear as placeholders.
     : In addition to the number of digits requested, one or more zeros will appear as placeholders.
     = {0.0000000001140256472, 0.003267763643, 93648.04748, 2683779414000., 76912142210000000000.}

    ## ExponentStep
    #> NumberForm[10^8 N[Pi], 10, ExponentStep -> 3]
     = 314.1592654×10^6
    #> NumberForm[1.2345, 3, ExponentStep -> x]
     : Value of option ExponentStep -> x is not a positive integer.
     = 1.2345
    #> NumberForm[1.2345, 3, ExponentStep -> 0]
     : Value of option ExponentStep -> 0 is not a positive integer.
     = 1.2345
    #> NumberForm[y, 10, ExponentStep -> 6]
     = {114.0256472×10^-12, 3267.763643×10^-6, 93648.04748, 2.683779414×10^12, 76.91214221×10^18}

    ## NumberFormat
    #> NumberForm[y, 10, NumberFormat -> (#1 &)]
     = {1.140256472, 0.003267763643, 93648.04748, 2.683779414, 7.691214221}

    ## NumberMultiplier
    #> NumberForm[1.2345, 3, NumberMultiplier -> 0]
     : Value for option NumberMultiplier -> 0 is expected to be a string.
     = 1.2345
    #> NumberForm[N[10^ 7 Pi], 15, NumberMultiplier -> "*"]
     = 3.14159265358979*10^7

    ## NumberPoint
    #> NumberForm[1.2345, 5, NumberPoint -> ","]
     = 1,2345
    #> NumberForm[1.2345, 3, NumberPoint -> 0]
     : Value for option NumberPoint -> 0 is expected to be a string.
     = 1.2345

    ## NumberPadding
    #> NumberForm[1.41, {10, 5}]
     = 1.41000
    #> NumberForm[1.41, {10, 5}, NumberPadding -> {"", "X"}]
     = 1.41XXX
    #> NumberForm[1.41, {10, 5}, NumberPadding -> {"X", "Y"}]
     = XXXXX1.41YYY
    #> NumberForm[1.41, 10, NumberPadding -> {"X", "Y"}]
     = XXXXXXXX1.41
    #> NumberForm[1.2345, 3, NumberPadding -> 0]
     :  Value for option NumberPadding -> 0 should be a string or a pair of strings.
     = 1.2345
    #> NumberForm[1.41, 10, NumberPadding -> {"X", "Y"}, NumberSigns -> {"-------------", ""}]
     = XXXXXXXXXXXXXXXXXXXX1.41
    #> NumberForm[{1., -1., 2.5, -2.5}, {4, 6}, NumberPadding->{"X", "Y"}]
     = {X1.YYYYYY, -1.YYYYYY, X2.5YYYYY, -2.5YYYYY}

    ## NumberSeparator
    #> NumberForm[N[10^ 5 Pi], 15, DigitBlock -> 3, NumberSeparator -> " "]
     = 314 159.265 358 979
    #> NumberForm[N[10^ 5 Pi], 15, DigitBlock -> 3, NumberSeparator -> {" ", ","}]
     = 314 159.265,358,979
    #> NumberForm[N[10^ 5 Pi], 15, DigitBlock -> 3, NumberSeparator -> {",", " "}]
     = 314,159.265 358 979
    #> NumberForm[N[10^ 7 Pi], 15, DigitBlock -> 3, NumberSeparator -> {",", " "}]
     = 3.141 592 653 589 79×10^7
    #> NumberForm[1.2345, 3, NumberSeparator -> 0]
     :  Value for option NumberSeparator -> 0 should be a string or a pair of strings.
     = 1.2345

    ## NumberSigns
    #> NumberForm[1.2345, 5, NumberSigns -> {"-", "+"}]
     = +1.2345
    #> NumberForm[-1.2345, 5, NumberSigns -> {"- ", ""}]
     = - 1.2345
    #> NumberForm[1.2345, 3, NumberSigns -> 0]
     : Value for option NumberSigns -> 0 should be a pair of strings or two pairs of strings.
     = 1.2345

    ## SignPadding
    #> NumberForm[1.234, 6, SignPadding -> True, NumberPadding -> {"X", "Y"}]
     = XXX1.234
    #> NumberForm[-1.234, 6, SignPadding -> True, NumberPadding -> {"X", "Y"}]
     = -XX1.234
    #> NumberForm[-1.234, 6, SignPadding -> False, NumberPadding -> {"X", "Y"}]
     = XX-1.234
    #> NumberForm[-1.234, {6, 4}, SignPadding -> False, NumberPadding -> {"X", "Y"}]
     = X-1.234Y

    ## 1-arg, Option case
    #> NumberForm[34, ExponentFunction->(Null&)]
     = 34

    ## zero padding integer x0.0 case
    #> NumberForm[50.0, {5, 1}]
     = 50.0
    #> NumberForm[50, {5, 1}]
     = 50.0

    ## Rounding correctly
    #> NumberForm[43.157, {10, 1}]
     = 43.2
    #> NumberForm[43.15752525, {10, 5}, NumberSeparator -> ",", DigitBlock -> 1]
     = 4,3.1,5,7,5,3
    #> NumberForm[80.96, {16, 1}]
     = 81.0
    #> NumberForm[142.25, {10, 1}]
     = 142.3
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
            return number_form(expr, py_n, None, evaluation, py_options)
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
            return number_form(expr, py_n, None, evaluation, py_options)
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
            return number_form(expr, py_n, py_f, evaluation, py_options)
        return Expression(SymbolMakeBoxes, expr, form)


class OutputForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/OutputForm.html</url>

    <dl>
      <dt>'OutputForm[$expr$]'
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
      <dt>'PythonForm[$expr$]'
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
    = [1, 2, 3]
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
      <dt>'SympyForm[$expr$]'
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
      <dt>'StandardForm[$expr$]'
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
      <dt>'TraditionalForm[$expr$]'
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
      <dt>'TeXForm[$expr$]'
      <dd>displays $expr$ using TeX math mode commands.
    </dl>

    >> TeXForm[HoldForm[Sqrt[a^3]]]
     = \sqrt{a^3}

    #> {"hi","you"} //InputForm //TeXForm
     = \left\{\text{``hi''}, \text{``you''}\right\}

    #> TeXForm[a+b*c]
     = a+b c
    #> TeXForm[InputForm[a+b*c]]
     = a\text{ + }b*c
    """

    in_outputforms = True
    in_printforms = True
    summary_text = "formatted expression as TeX commands"

    def eval_tex(self, expr, evaluation) -> Expression:
        "MakeBoxes[expr_, TeXForm]"
        boxes = MakeBoxes(expr).evaluate(evaluation)
        try:
            # Here we set ``show_string_characters`` to False, to reproduce
            # the standard behaviour in WMA. Remove this parameter to recover the
            # quotes in InputForm and FullForm
            tex = boxes.boxes_to_tex(
                show_string_characters=False, evaluation=evaluation
            )

            # Replace multiple newlines by a single one e.g. between asy-blocks
            tex = MULTI_NEWLINE_RE.sub("\n", tex)

            tex = tex.replace(" \uF74c", " \\, d")  # tmp hack for Integrate
        except BoxError:
            evaluation.message(
                "General",
                "notboxes",
                Expression(SymbolFullForm, boxes).evaluate(evaluation),
            )
            tex = ""
        return Expression(SymbolRowBox, ListExpression(String(tex)))


class TableForm(FormBaseClass):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/TableForm.html</url>

    <dl>
      <dt>'TableForm[$expr$]'
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

    #> TableForm[{}]
     = #<--#
    """

    in_outputforms = True
    in_printforms = False
    options = {"TableDepth": "Infinity"}
    summary_text = "format as a table"

    def eval_makeboxes(self, table, f, evaluation, options):
        """MakeBoxes[%(name)s[table_, OptionsPattern[%(name)s]],
        f:StandardForm|TraditionalForm|OutputForm]"""
        dims = len(get_dimensions(table, head=SymbolList))
        depth = self.get_option(options, "TableDepth", evaluation, pop=True)
        options["System`TableDepth"] = depth
        depth = expr_min((Integer(dims), depth))
        depth = depth.value
        if depth is None:
            evaluation.message(self.get_name(), "int")
            return

        if depth <= 0:
            return format_element(table, evaluation, f)
        elif depth == 1:
            return GridBox(
                ListExpression(
                    *(
                        ListExpression(format_element(item, evaluation, f))
                        for item in table.elements
                    ),
                )
            )
            # return Expression(
            #    'GridBox', Expression('List', *(
            #        Expression('List', Expression('MakeBoxes', item, f))
            #        for item in table.elements)))
        else:
            options["System`TableDepth"] = Integer(depth - 2)

            def transform_item(item):
                if depth > 2:
                    return self.eval_makeboxes(item, f, evaluation, options)
                else:
                    return format_element(item, evaluation, f)

            result = GridBox(
                ListExpression(
                    *(
                        ListExpression(
                            *(transform_item(item) for item in row.elements),
                        )
                        for row in table.elements
                    ),
                )
            )
            options["System`TableDepth"] = Integer(depth)
            return result


class MatrixForm(TableForm):
    """
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/MatrixForm.html</url>

    <dl>
      <dt>'MatrixForm[$m$]'
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

    ## Issue #182
    #> {{2*a, 0},{0,0}}//MatrixForm
     = 2 ⁢ a   0
     .
     . 0       0
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
