# -*- coding: utf-8 -*-
"""
This module contains basic low-level functions that combine an ``Expression``
with an ``Evaluation`` objects to produce ``BoxExpressions``, following
makeboxes rules.
"""


from typing import Optional, Union

from mathics.core.atoms import Complex, Rational, String
from mathics.core.element import BaseElement, BoxElementMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolFullForm,
    SymbolList,
    SymbolMakeBoxes,
)
from mathics.core.systemsymbols import (  # SymbolRule, SymbolRuleDelayed,
    SymbolComplex,
    SymbolRational,
    SymbolStandardForm,
)
from mathics.eval.makeboxes.formatvalues import do_format
from mathics.eval.makeboxes.precedence import parenthesize


def to_boxes(x, evaluation: Evaluation, options={}) -> BoxElementMixin:
    """
    This function takes the expression ``x``
    and tries to reduce it to a ``BoxElementMixin``
    expression using an evaluation object.
    """
    if isinstance(x, BoxElementMixin):
        return x
    if isinstance(x, Atom):
        x = x.atom_to_boxes(SymbolStandardForm, evaluation)
        return to_boxes(x, evaluation, options)
    if isinstance(x, Expression):
        if x.has_form("MakeBoxes", None):
            x_boxed = x.evaluate(evaluation)
        else:
            x_boxed = eval_makeboxes(x, evaluation)
        if isinstance(x_boxed, BoxElementMixin):
            return x_boxed
        if isinstance(x_boxed, Atom):
            return to_boxes(x_boxed, evaluation, options)
    return eval_makeboxes_fullform(x, evaluation)


# this temporarily replaces the _BoxedString class
def _boxed_string(string: str, **options):
    from mathics.builtin.box.layout import StyleBox

    return StyleBox(String(string), **options)


# 640 = sys.int_info.str_digits_check_threshold.
# Someday when 3.11 is the minimum version of Python supported,
# we can replace the magic value 640 below with sys.int.str_digits_check_threshold.
def int_to_string_shorter_repr(value: int, form: Symbol, max_digits=640):
    """Convert value to a String, restricted to max_digits characters.

    if value has an n-digit decimal representation,
      value = d_1 *10^{n-1} d_2 * 10^{n-2} + d_3 10^{n-3} + ..... +
              d_{n-2}*100 +d_{n-1}*10 + d_{n}
    is represented as the string

    "d_1d_2d_3...d_{k}<<n-2k>>d_{n-k-1}...d_{n-2}d_{n-1}d_{n}"

    where n-2k digits are replaced by a placeholder.
    """
    if max_digits == 0:
        return String(str(value))

    # Normalize to positive quantities
    is_negative = value < 0
    if is_negative:
        value = -value
        max_digits = max_digits - 1

    # Estimate the number of decimal digits
    num_digits = int(value.bit_length() * 0.3)

    # If the estimated number is below the threshold,
    # return it as it is.
    if num_digits <= max_digits:
        if is_negative:
            return String("-" + str(value))
        return String(str(value))

    # estimate the size of the placeholder
    size_placeholder = len(str(num_digits)) + 6
    # Estimate the number of available decimal places
    avaliable_digits = max(max_digits - size_placeholder, 0)
    # how many most significative digits include
    len_msd = (avaliable_digits + 1) // 2
    # how many least significative digits to include:
    len_lsd = avaliable_digits - len_msd
    # Compute the msd.
    msd = str(value // 10 ** (num_digits - len_msd))
    if msd == "0":
        msd = ""

    # If msd has more digits than the expected, it means that
    # num_digits was wrong.
    extra_msd_digits = len(msd) - len_msd
    if extra_msd_digits > 0:
        # Remove the extra digit and fix the real
        # number of digits.
        msd = msd[:len_msd]
        num_digits = num_digits + 1

    lsd = ""
    if len_lsd > 0:
        lsd = str(value % 10 ** (len_lsd))
        # complete decimal positions in the lsd:
        lsd = (len_lsd - len(lsd)) * "0" + lsd

    # Now, compute the true number of hiding
    # decimal places, and built the placeholder
    remaining = num_digits - len_lsd - len_msd
    placeholder = f" <<{remaining}>> "
    # Check if the shorten string is actually
    # shorter than the full string representation:
    if len(placeholder) < remaining:
        value_str = f"{msd}{placeholder}{lsd}"
    else:
        value_str = str(value)

    if is_negative:
        value_str = "-" + value_str
    return String(value_str)


def eval_makeboxes_outputform(expr, evaluation, form):
    """
    Build a 2D representation of the expression using only keyboard characters.
    """
    from mathics.builtin.box.layout import PaneBox
    from mathics.form.outputform import expression_to_outputform_text

    text_outputform = str(expression_to_outputform_text(expr, evaluation, form))
    elem1 = PaneBox(String('"' + text_outputform + '"'))
    return elem1


# TODO: evaluation is needed because `atom_to_boxes` uses it. Can we remove this
# argument?
def eval_makeboxes_fullform(
    expr: BaseElement, evaluation: Evaluation
) -> BoxElementMixin:
    """Same as MakeBoxes[FullForm[expr_], f_]"""
    from mathics.builtin.box.layout import RowBox

    if isinstance(expr, BoxElementMixin):
        expr = expr.to_expression()
    if isinstance(expr, Atom):
        if isinstance(expr, Rational):
            expr = Expression(SymbolRational, expr.numerator(), expr.denominator())
        elif isinstance(expr, Complex):
            expr = Expression(SymbolComplex, expr.real, expr.imag)
        else:
            return expr.atom_to_boxes(SymbolFullForm, evaluation)
    head, elements = expr.head, expr.elements
    boxed_elements = tuple(
        (eval_makeboxes_fullform(element, evaluation) for element in elements)
    )
    # In some places it would be less verbose to use special outputs for
    # `List`, `Rule` and `RuleDelayed`. WMA does not that, but we do it for
    # `List`.
    #
    # if head is SymbolRule and len(elements) == 2:
    #    return RowBox(boxed_elements[0], String("->"), boxed_elements[1])
    # if head is SymbolRuleDelayed and len(elements) == 2:
    #    return RowBox(boxed_elements[0], String(":>"), boxed_elements[1])
    if head is SymbolList:
        left, right, sep = (String(ch) for ch in ("{", "}", ","))
        result_elements = [left]
    else:
        left, right, sep = (String(ch) for ch in ("[", "]", ","))
        result_elements = [eval_makeboxes_fullform(head, evaluation), left]

    if len(boxed_elements) > 1:
        arguments = []
        for b_elem in boxed_elements:
            if len(arguments) > 0:
                arguments.append(sep)
            arguments.append(b_elem)
        result_elements.append(RowBox(*arguments))
    elif len(boxed_elements) == 1:
        result_elements.append(boxed_elements[0])
    result_elements.append(right)
    return RowBox(*result_elements)


def eval_generic_makeboxes(self, expr, f, evaluation):
    """MakeBoxes[expr_,
    f:TraditionalForm|StandardForm|OutputForm|InputForm]"""
    from mathics.builtin.box.layout import RowBox

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
        head_boxes = parenthesize(
            670, head, Expression(SymbolMakeBoxes, head, f), False
        )
        head_boxes = head_boxes.evaluate(evaluation)
        head_boxes = to_boxes(head_boxes, evaluation)
        result = [head_boxes, to_boxes(String(left), evaluation)]

        if len(elements) > 1:
            row = []
            if f_name in (
                "System`InputForm",
                "System`OutputForm",
            ):
                sep = ", "
            else:
                sep = ","
            for index, element in enumerate(elements):
                if index > 0:
                    row.append(to_boxes(String(sep), evaluation))
                row.append(
                    to_boxes(
                        Expression(SymbolMakeBoxes, element, f).evaluate(evaluation),
                        evaluation,
                    )
                )
            result.append(RowBox(*row))
        elif len(elements) == 1:
            result.append(
                to_boxes(
                    Expression(SymbolMakeBoxes, elements[0], f).evaluate(evaluation),
                    evaluation,
                )
            )
        result.append(to_boxes(String(right), evaluation))
        return RowBox(*result)


def eval_makeboxes(
    expr, evaluation: Evaluation, form=SymbolStandardForm
) -> Optional[BaseElement]:
    """
    This function takes the definitions provided by the evaluation
    object, and produces a boxed fullform for expr.

    Basically: MakeBoxes[expr // form]
    """
    # This is going to be reimplemented.
    if form is SymbolFullForm:
        return eval_makeboxes_fullform(expr, evaluation)
    return Expression(SymbolMakeBoxes, expr, form).evaluate(evaluation)


def format_element(
    element: BaseElement, evaluation: Evaluation, form: Symbol, **kwargs
) -> Optional[Union[BoxElementMixin, BaseElement]]:
    """
    Applies formats associated to the expression, and then calls Makeboxes
    """
    # Halt any potential evaluation tracing while performing boxing.
    evaluation.is_boxing = True
    while element.get_head() is form:
        element = element.elements[0]

    if element.has_form("FullForm", 1):
        return eval_makeboxes_fullform(element.elements[0], evaluation)

    # In order to work like in WMA, `format_element`
    # should evaluate `MakeBoxes[element//form, StandardForm]`
    # Then, MakeBoxes[expr_, StandardForm], for any expr,
    # should apply Format[...] rules, and then
    # MakeBoxes[...] rules. These rules should be stored
    # as FormatValues[...]
    # As a first step in that direction, let's mimic this behaviour
    # just for the case of OutputForm:
    if element.has_form("OutputForm", 1):
        return eval_makeboxes_outputform(element.elements[0], evaluation, form)

    formatted_expr = do_format(element, evaluation, form)
    if formatted_expr is None:
        return None

    result_box = eval_makeboxes(formatted_expr, evaluation, form)
    if isinstance(result_box, String):
        return result_box
    if isinstance(result_box, BoxElementMixin):
        return result_box
    else:
        return eval_makeboxes_fullform(element, evaluation)
