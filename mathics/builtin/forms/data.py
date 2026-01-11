"""
Data-Specific Forms

Some forms are specific to formatting certain kinds of data, like numbers, strings, or matrices.

These are in contrast to the Forms like 'OutputForm' or 'StandardForm', which are intended to work over all kinds of data.

"""
import re

from mathics.builtin.box.layout import RowBox, to_boxes
from mathics.builtin.forms.base import FormBaseClass
from mathics.builtin.makeboxes import MakeBoxes
from mathics.core.atoms import Integer, Real, String
from mathics.core.builtin import Builtin
from mathics.core.element import EvalMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.number import dps
from mathics.core.symbols import Symbol, SymbolFalse, SymbolNull, SymbolTrue
from mathics.core.systemsymbols import (
    SymbolAutomatic,
    SymbolInfinity,
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
    eval_tableform,
)
from mathics.eval.strings import eval_StringForm_MakeBoxes, eval_ToString


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


class _NumberForm(Builtin):
    """
    Base class for NumberForm, AccountingForm, EngineeringForm, and ScientificForm.
    """

    default_ExponentFunction = None
    default_NumberFormat = None
    in_outputforms = True
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


class SequenceForm(FormBaseClass):
    r"""
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/SequenceForm.html</url>

    <dl>
      <dt>'SequenceForm'[$expr_1$, $expr_2$, ..]
      <dd>format the textual concatenation of the printed forms of $expi$.
    </dl>
    'SequenceForm' has been superseded by <url>:Row:
    /doc/reference-of-built-in-symbols/layout/row
    </url> and 'Text' (which is not implemented yet).

    >> SequenceForm["[", "x = ", 56, "]"]
     = [x = 56]
    """

    in_outputforms = False
    in_printforms = False

    options = {
        "CharacterEncoding": '"Unicode"',
    }

    summary_text = "format a string from a template and a list of parameters"

    def eval_makeboxes(self, args, form, evaluation, options: dict):
        """MakeBoxes[SequenceForm[args___, OptionsPattern[SequenceForm]],
        form:StandardForm|TraditionalForm|OutputForm]"""
        encoding = options["System`CharacterEncoding"]
        return RowBox(
            *[
                (
                    arg
                    if isinstance(arg, String)
                    else eval_ToString(arg, form, encoding.value, evaluation)
                )
                for arg in args.get_sequence()
            ]
        )


class StringForm(FormBaseClass):
    r"""
    <url>
      :WMA link:
      https://reference.wolfram.com/language/ref/StringForm.html</url>

    <dl>
      <dt>'StringForm'[$str$, $expr_1$, $expr_2$, ...]
      <dd>displays the string $str$, replacing placeholders in $str$
        with the corresponding expressions.
    </dl>

    >> StringForm["`1` bla `2` blub `` bla `2`", a, b, c]
     = a bla b blub c bla b
    """

    in_outputforms = False
    in_printforms = False
    messages = {
        "sfr": 'Item `1` requested in "`3`" out of range; `2` items available.',
        "sfq": "Unmatched backquote in `1`.",
    }
    summary_text = "format a string from a template and a list of parameters"

    def eval_makeboxes(self, s, args, form, evaluation):
        """MakeBoxes[StringForm[s_String, args___],
        form:StandardForm|TraditionalForm]"""
        return eval_StringForm_MakeBoxes(s, args.get_sequence(), form, evaluation)


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
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     . -Graphics-   -Graphics-   -Graphics-
     .
     .
    """

    in_outputforms = True
    in_printforms = False
    options = {"TableDepth": "Infinity"}
    summary_text = "format as a table"

    def eval_makeboxes(self, table, f, evaluation, options):
        """MakeBoxes[%(name)s[table_, OptionsPattern[%(name)s]],
        f:StandardForm|TraditionalForm]"""
        return eval_tableform(self, table, f, evaluation, options)


# This has to come after TableForm
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
