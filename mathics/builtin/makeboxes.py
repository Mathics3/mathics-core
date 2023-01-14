# -*- coding: utf-8 -*-
"""
Low level Format definitions
"""

from typing import Union

import mpmath

from mathics.builtin.base import Builtin, Predefined
from mathics.builtin.box.layout import RowBox, to_boxes
from mathics.core.atoms import Integer, Integer1, Real, String
from mathics.core.attributes import A_HOLD_ALL_COMPLETE, A_READ_PROTECTED
from mathics.core.convert.op import operator_to_ascii, operator_to_unicode
from mathics.core.element import BaseElement, BoxElementMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.number import dps
from mathics.core.symbols import Atom, Symbol
from mathics.core.systemsymbols import SymbolInputForm, SymbolOutputForm, SymbolRowBox
from mathics.eval.makeboxes import (
    NEVER_ADD_PARENTHESIS,
    _boxed_string,
    format_element,
    parenthesize,
)


def int_to_s_exp(expr, n):
    n = expr.get_int_value()
    if n < 0:
        nonnegative = 0
        s = str(-n)
    else:
        nonnegative = 1
        s = str(n)
    exp = len(s) - 1
    return s, exp, nonnegative


# FIXME: op should be a string, so remove the Union.
def make_boxes_infix(
    elements, op: Union[String, list], precedence: int, grouping, form: Symbol
):
    result = []
    for index, element in enumerate(elements):
        if index > 0:
            if isinstance(op, list):
                result.append(op[index - 1])
            else:
                result.append(op)
        parenthesized = False
        if grouping == "System`NonAssociative":
            parenthesized = True
        elif grouping == "System`Left" and index > 0:
            parenthesized = True
        elif grouping == "System`Right" and index == 0:
            parenthesized = True

        element_boxes = MakeBoxes(element, form)
        element = parenthesize(precedence, element, element_boxes, parenthesized)

        result.append(element)
    return Expression(SymbolRowBox, ListExpression(*result))


def real_to_s_exp(expr, n):
    if expr.is_zero:
        s = "0"
        if expr.is_machine_precision():
            exp = 0
        else:
            p = expr.get_precision()
            exp = -dps(p)
        nonnegative = 1
    else:
        if n is None:
            if expr.is_machine_precision():
                value = expr.get_float_value()
                s = repr(value)
            else:
                with mpmath.workprec(expr.get_precision()):
                    value = expr.to_mpmath()
                    s = mpmath.nstr(value, dps(expr.get_precision()) + 1)
        else:
            with mpmath.workprec(expr.get_precision()):
                value = expr.to_mpmath()
                s = mpmath.nstr(value, n)

        # sign prefix
        if s[0] == "-":
            assert value < 0
            nonnegative = 0
            s = s[1:]
        else:
            assert value >= 0
            nonnegative = 1

        # exponent (exp is actual, pexp is printed)
        if "e" in s:
            s, exp = s.split("e")
            exp = int(exp)
            if len(s) > 1 and s[1] == ".":
                # str(float) doesn't always include '.' if 'e' is present.
                s = s[0] + s[2:].rstrip("0")
        else:
            exp = s.index(".") - 1
            s = s[: exp + 1] + s[exp + 2 :].rstrip("0")

            # consume leading '0's.
            i = 0
            while s[i] == "0":
                i += 1
                exp -= 1
            s = s[i:]

        # add trailing zeros for precision reals
        if n is not None and not expr.is_machine_precision() and len(s) < n:
            s = s + "0" * (n - len(s))
    return s, exp, nonnegative


def number_form(expr, n, f, evaluation: Evaluation, options: dict):
    """
    Converts a Real or Integer instance to Boxes.

    n digits of precision with f (can be None) digits after the decimal point.
    evaluation (can be None) is used for messages.

    The allowed options are python versions of the options permitted to
    NumberForm and must be supplied. See NumberForm or Real.make_boxes
    for correct option examples.
    """

    assert isinstance(n, int) and n > 0 or n is None
    assert f is None or (isinstance(f, int) and f >= 0)

    is_int = False
    if isinstance(expr, Integer):
        assert n is not None
        s, exp, nonnegative = int_to_s_exp(expr, n)
        if f is None:
            is_int = True
    elif isinstance(expr, Real):
        if n is not None:
            n = min(n, dps(expr.get_precision()) + 1)
        s, exp, nonnegative = real_to_s_exp(expr, n)
        if n is None:
            n = len(s)
    else:
        raise ValueError("Expected Real or Integer.")

    assert isinstance(n, int) and n > 0

    sign_prefix = options["NumberSigns"][nonnegative]

    # round exponent to ExponentStep
    rexp = (exp // options["ExponentStep"]) * options["ExponentStep"]

    if is_int:
        # integer never uses scientific notation
        pexp = ""
    else:
        method = options["ExponentFunction"]
        pexp = method(Integer(rexp)).get_int_value()
        if pexp is not None:
            exp -= pexp
            pexp = str(pexp)
        else:
            pexp = ""

    # pad right with '0'.
    if len(s) < exp + 1:
        if evaluation is not None:
            evaluation.message("NumberForm", "sigz")
        # TODO NumberPadding?
        s = s + "0" * (1 + exp - len(s))
    # pad left with '0'.
    if exp < 0:
        s = "0" * (-exp) + s
        exp = 0

    # left and right of NumberPoint
    left, right = s[: exp + 1], s[exp + 1 :]

    def _round(number, ndigits):
        """
        python round() for integers but with correct rounding.
        e.g. `_round(14225, -1)` is `14230` not `14220`.
        """
        assert isinstance(ndigits, int)
        assert ndigits < 0
        assert isinstance(number, int)
        assert number >= 0
        number += 5 * int(10 ** -(1 + ndigits))
        number //= int(10**-ndigits)
        return number

    # pad with NumberPadding
    if f is not None:
        if len(right) < f:
            # pad right
            right = right + (f - len(right)) * options["NumberPadding"][1]
        elif len(right) > f:
            # round right
            tmp = int(left + right)
            tmp = _round(tmp, f - len(right))
            tmp = str(tmp)
            left, right = tmp[: exp + 1], tmp[exp + 1 :]

    def split_string(s, start, step):
        if start > 0:
            yield s[:start]
        for i in range(start, len(s), step):
            yield s[i : i + step]

    # insert NumberSeparator
    digit_block = options["DigitBlock"]
    if digit_block[0] != 0:
        left = split_string(left, len(left) % digit_block[0], digit_block[0])
        left = options["NumberSeparator"][0].join(left)
    if digit_block[1] != 0:
        right = split_string(right, 0, digit_block[1])
        right = options["NumberSeparator"][1].join(right)

    left_padding = 0
    max_sign_len = max(len(options["NumberSigns"][0]), len(options["NumberSigns"][1]))
    i = len(sign_prefix) + len(left) + len(right) - max_sign_len
    if i < n:
        left_padding = n - i
    elif len(sign_prefix) < max_sign_len:
        left_padding = max_sign_len - len(sign_prefix)
    left_padding = left_padding * options["NumberPadding"][0]

    # insert NumberPoint
    if options["SignPadding"]:
        prefix = sign_prefix + left_padding
    else:
        prefix = left_padding + sign_prefix

    if is_int:
        s = prefix + left
    else:
        s = prefix + left + options["NumberPoint"] + right

    # base
    base = "10"

    # build number
    method = options["NumberFormat"]
    if options["_Form"] in ("System`InputForm", "System`FullForm"):
        return method(
            _boxed_string(s, number_as_text=True),
            _boxed_string(base, number_as_text=True),
            _boxed_string(pexp, number_as_text=True),
            options,
        )
    else:
        return method(String(s), String(base), String(pexp), options)


# TODO: Differently from the current implementation, MakeBoxes should only
# accept as its format field the symbols in `$BoxForms`. This is something to
# fix in a following step, changing the way in which Format and MakeBoxes work.


class BoxForms_(Predefined):
    """
    <url>:WMA link:https://reference.wolfram.com/language/ref/$BoxForms.html</url>

    <dl>
      <dt>
      <dd>$BoxForms is the list of box formats.
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
      <dt>'MakeBoxes[$expr$]'
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
        "MakeBoxes[(form:FullForm|InputForm)[expr_], StandardForm|TraditionalForm|OutputForm]": "StyleBox[MakeBoxes[expr, form], ShowStringCharacters->True]",
        "MakeBoxes[PrecedenceForm[expr_, prec_], f_]": "MakeBoxes[expr, f]",
        "MakeBoxes[Style[expr_, OptionsPattern[Style]], f_]": (
            "StyleBox[MakeBoxes[expr, f], "
            "ImageSizeMultipliers -> OptionValue[ImageSizeMultipliers]]"
        ),
    }
    summary_text = "settable low-level translator from expression to display boxes"

    def eval_general(self, expr, f, evaluation):
        """MakeBoxes[expr_,
        f:TraditionalForm|StandardForm|OutputForm|InputForm|FullForm]"""
        if isinstance(expr, BoxElementMixin):
            expr = expr.to_expression()
        if isinstance(expr, Atom):
            return expr.atom_to_boxes(f, evaluation)
        else:
            head = expr.head
            elements = expr.elements

            f_name = f.get_name()
            if f_name == "System`TraditionalForm":
                left, right = "(", ")"
            else:
                left, right = "[", "]"

            # Parenthesize infix operators at the head of expressions,
            # like (a + b)[x], but not f[a] in f[a][b].
            #
            head_boxes = parenthesize(670, head, MakeBoxes(head, f), False)
            head_boxes = head_boxes.evaluate(evaluation)
            head_boxes = to_boxes(head_boxes, evaluation)
            result = [head_boxes, to_boxes(String(left), evaluation)]

            if len(elements) > 1:
                row = []
                if f_name in (
                    "System`InputForm",
                    "System`OutputForm",
                    "System`FullForm",
                ):
                    sep = ", "
                else:
                    sep = ","
                for index, element in enumerate(elements):
                    if index > 0:
                        row.append(to_boxes(String(sep), evaluation))
                    row.append(
                        to_boxes(MakeBoxes(element, f).evaluate(evaluation), evaluation)
                    )
                result.append(RowBox(*row))
            elif len(elements) == 1:
                result.append(
                    to_boxes(MakeBoxes(elements[0], f).evaluate(evaluation), evaluation)
                )
            result.append(to_boxes(String(right), evaluation))
            return RowBox(*result)

    def eval_outerprecedenceform(self, expr, precedence, evaluation):
        """MakeBoxes[PrecedenceForm[expr_, precedence_],
        StandardForm|TraditionalForm|OutputForm|InputForm]"""

        py_precedence = precedence.get_int_value()
        boxes = MakeBoxes(expr)
        return parenthesize(py_precedence, expr, boxes, True)

    def eval_postprefix(self, p, expr, h, precedence, form, evaluation):
        """MakeBoxes[(p:Prefix|Postfix)[expr_, h_, precedence_:None],
        form:StandardForm|TraditionalForm|OutputForm|InputForm]"""

        if not isinstance(h, String):
            h = MakeBoxes(h, form)

        py_precedence = precedence.get_int_value()

        elements = expr.elements
        if len(elements) == 1:
            element = elements[0]
            element_boxes = MakeBoxes(element, form)
            element = parenthesize(py_precedence, element, element_boxes, True)
            if p.get_name() == "System`Postfix":
                args = (element, h)
            else:
                args = (h, element)

            return Expression(SymbolRowBox, ListExpression(*args).evaluate(evaluation))
        else:
            return MakeBoxes(expr, form).evaluate(evaluation)

    def eval_infix(
        self, expr, operator, precedence: Integer, grouping, form: Symbol, evaluation
    ):
        """MakeBoxes[Infix[expr_, operator_, precedence_:None, grouping_:None],
        form:StandardForm|TraditionalForm|OutputForm|InputForm]"""

        ## FIXME: this should go into a some formatter.
        def format_operator(operator) -> Union[String, BaseElement]:
            """
            Format infix operator `operator`. To do this outside parameter form is used.
            Sometimes no changes are made and operator is returned unchanged.

            This function probably should be rewritten be more scalable across other forms
            and moved to a module that contiaing similar formatting routines.
            """
            if not isinstance(operator, String):
                return MakeBoxes(operator, form)

            op_str = operator.value

            # FIXME: performing a check using the operator symbol representation feels a bit
            # fragile. The operator name seems more straightforward and more robust.
            if form == SymbolInputForm and op_str in ["*", "^", " "]:
                return operator
            elif (
                form in (SymbolInputForm, SymbolOutputForm)
                and not op_str.startswith(" ")
                and not op_str.endswith(" ")
            ):
                # FIXME: Again, testing on specific forms is fragile and not scalable.
                op = String(" " + op_str + " ")
                return op
            return operator

        py_precedence = (
            precedence.value if hasattr(precedence, "value") else NEVER_ADD_PARENTHESIS
        )
        grouping = grouping.get_name()

        if isinstance(expr, Atom):
            evaluation.message("Infix", "normal", Integer1)
            return None

        elements = expr.elements
        if len(elements) > 1:
            if operator.has_form("List", len(elements) - 1):
                operator = [format_operator(op) for op in operator.elements]
                return make_boxes_infix(
                    elements, operator, py_precedence, grouping, form
                )
            else:
                encoding_rule = evaluation.definitions.get_ownvalue(
                    "$CharacterEncoding"
                )
                encoding = (
                    "UTF8" if encoding_rule is None else encoding_rule.replace.value
                )
                op_str = (
                    operator.value
                    if isinstance(operator, String)
                    else operator.short_name
                )
                if encoding == "ASCII":
                    operator = format_operator(
                        String(operator_to_ascii.get(op_str, op_str))
                    )
                else:
                    operator = format_operator(
                        String(operator_to_unicode.get(op_str, op_str))
                    )

            return make_boxes_infix(elements, operator, py_precedence, grouping, form)

        elif len(elements) == 1:
            return MakeBoxes(elements[0], form)
        else:
            return MakeBoxes(expr, form)


class ToBoxes(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/ToBoxes.html</url>

    <dl>
      <dt>'ToBoxes[$expr$]'
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
