# -*- coding: utf-8 -*-
"""
This module contains basic low-level functions that combine an ``Expression``
with an ``Evaluation`` objects to produce ``BoxExpressions``, following
formatting rules.
"""


import typing
from typing import Any, Dict, Type

from mathics.core.atoms import Complex, Integer, Rational, Real, String, SymbolI
from mathics.core.convert.expression import to_expression_with_specialization
from mathics.core.element import BaseElement, BoxElementMixin, EvalMixin
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import (
    Atom,
    Symbol,
    SymbolDivide,
    SymbolFullForm,
    SymbolGraphics,
    SymbolGraphics3D,
    SymbolHoldForm,
    SymbolList,
    SymbolMakeBoxes,
    SymbolNumberForm,
    SymbolPlus,
    SymbolPostfix,
    SymbolRepeated,
    SymbolRepeatedNull,
    SymbolTimes,
)
from mathics.core.systemsymbols import (
    SymbolComplex,
    SymbolMinus,
    SymbolRational,
    SymbolRowBox,
    SymbolStandardForm,
)

# An operator precedence value that will ensure that whatever operator
# this is attached to does not have parenthesis surrounding it.
# Operator precedence values are integers; If if an operator
# "op" is greater than the surrounding precedence, then "op"
# will be surrounded by parenthesis, e.g. ... (...op...) ...
# In named-characters.yml of mathics-scanner we start at 0.
# However, negative values would also work.
NEVER_ADD_PARENTHESIS = 0

# These Strings are used in Boxing output
StringElipsis = String("...")
StringLParen = String("(")
StringRParen = String(")")
StringRepeated = String("..")

builtins_precedence: Dict[Symbol, int] = {}

element_formatters = {}


# this temporarily replaces the _BoxedString class
def _boxed_string(string: str, **options):
    from mathics.builtin.box.layout import StyleBox

    return StyleBox(String(string), **options)


def int_to_string_shorter_repr(value: Integer, form: Symbol, max_digits=640):
    """Convert value to a String, restricted to max_digits characters.

    if value has a n digits decimal representation,
      value = d_1 *10^{n-1} d_2 * 10^{n-2} + d_3 10^{n-3} + ..... +   d_{n-2}*100 +d_{n-1}*10 + d_{n}
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

    # If the estimated number is bellow the threshold,
    # return it as it is.
    if num_digits <= max_digits:
        if is_negative:
            return String("-" + str(value))
        return String(str(value))

    # estimate the size of the placeholder
    size_placeholder = len(str(num_digits)) + 6
    # Estimate the number of avaliable decimal places
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


def eval_fullform_makeboxes(
    self, expr, evaluation: Evaluation, form=SymbolStandardForm
) -> Expression:
    """
    This function takes the definitions provided by the evaluation
    object, and produces a boxed form for expr.

    Basically: MakeBoxes[expr // FullForm]
    """
    # This is going to be reimplemented.
    expr = Expression(SymbolFullForm, expr)
    return Expression(SymbolMakeBoxes, expr, form).evaluate(evaluation)


def eval_makeboxes(expr, evaluation: Evaluation, form=SymbolStandardForm) -> Expression:
    """
    This function takes the definitions provided by the evaluation
    object, and produces a boxed fullform for expr.

    Basically: MakeBoxes[expr // form]
    """
    # This is going to be reimplemented.
    return Expression(SymbolMakeBoxes, expr, form).evaluate(evaluation)


def format_element(
    element: BaseElement, evaluation: Evaluation, form: Symbol, **kwargs
) -> Type[BaseElement]:
    """
    Applies formats associated to the expression, and then calls Makeboxes
    """
    expr = do_format(element, evaluation, form)
    result = Expression(SymbolMakeBoxes, expr, form)
    result_box = result.evaluate(evaluation)
    if isinstance(result_box, String):
        return result_box
    if isinstance(result_box, BoxElementMixin):
        return result_box
    else:
        return format_element(element, evaluation, SymbolFullForm, **kwargs)


# do_format_*


def do_format(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Type[BaseElement]:
    do_format_method = element_formatters.get(type(element), do_format_element)
    return do_format_method(element, evaluation, form)


def do_format_element(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Type[BaseElement]:
    """
    Applies formats associated to the expression and removes
    superfluous enclosing formats.
    """

    from mathics.core.definitions import OutputForms

    evaluation.inc_recursion_depth()
    try:
        expr = element
        head = element.get_head()  # use element.head
        elements = element.get_elements()
        include_form = False
        # If the expression is enclosed by a Format
        # takes the form from the expression and
        # removes the format from the expression.
        if head in OutputForms and len(expr.elements) == 1:
            expr = elements[0]
            if not form.sameQ(head):
                form = head
                include_form = True

        # If form is Fullform, return it without changes
        if form is SymbolFullForm:
            if include_form:
                expr = Expression(form, expr)
            return expr
        # Repeated and RepeatedNull confuse the formatter,
        # so we need to hardlink their format rules:
        if head is SymbolRepeated:
            if len(elements) == 1:
                return Expression(
                    SymbolHoldForm,
                    Expression(
                        SymbolPostfix,
                        ListExpression(elements[0]),
                        StringRepeated,
                        Integer(170),
                    ),
                )
            else:
                return Expression(SymbolHoldForm, expr)
        elif head is SymbolRepeatedNull:
            if len(elements) == 1:
                return Expression(
                    SymbolHoldForm,
                    Expression(
                        SymbolPostfix,
                        Expression(SymbolList, elements[0]),
                        StringElipsis,
                        Integer(170),
                    ),
                )
            else:
                return Expression(SymbolHoldForm, expr)

        # If expr is not an atom, looks for formats in its definition
        # and apply them.
        def format_expr(expr):
            if not (isinstance(expr, Atom)) and not (isinstance(expr.head, Atom)):
                # expr is of the form f[...][...]
                return None
            name = expr.get_lookup_name()
            format_rules = evaluation.definitions.get_formats(name, form.get_name())
            for rule in format_rules:
                result = rule.apply(expr, evaluation)
                if result is not None and result != expr:
                    return result.evaluate(evaluation)
            return None

        formatted = format_expr(expr) if isinstance(expr, EvalMixin) else None
        if formatted is not None:
            do_format = element_formatters.get(type(formatted), do_format_element)
            result = do_format(formatted, evaluation, form)
            if include_form:
                result = Expression(form, result)
            return result

        # If the expression is still enclosed by a Format,
        # iterate.
        # If the expression is not atomic or of certain
        # specific cases, iterate over the elements.
        head = expr.get_head()
        if head in OutputForms:
            # If the expression was of the form
            # Form[expr, opts]
            # then the format was not stripped. Then,
            # just return it as it is.
            if len(expr.elements) != 1:
                return expr
            do_format = element_formatters.get(type(element), do_format_element)
            expr = do_format(expr, evaluation, form)

        elif (
            head is not SymbolNumberForm
            and not isinstance(expr, (Atom, BoxElementMixin))
            and head not in (SymbolGraphics, SymbolGraphics3D)
        ):
            # print("Not inside graphics or numberform, and not is atom")
            new_elements = [
                element_formatters.get(type(element), do_format_element)(
                    element, evaluation, form
                )
                for element in expr.elements
            ]
            expr_head = expr.head
            do_format = element_formatters.get(type(expr_head), do_format_element)
            head = do_format(expr_head, evaluation, form)
            expr = to_expression_with_specialization(head, *new_elements)

        if include_form:
            expr = Expression(form, expr)
        return expr
    finally:
        evaluation.dec_recursion_depth()


def do_format_rational(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Type[BaseElement]:
    if form is SymbolFullForm:
        return do_format_expression(
            Expression(
                Expression(SymbolHoldForm, SymbolRational),
                element.numerator(),
                element.denominator(),
            ),
            evaluation,
            form,
        )
    else:
        numerator = element.numerator()
        minus = numerator.value < 0
        if minus:
            numerator = Integer(-numerator.value)
        result = Expression(SymbolDivide, numerator, element.denominator())
        if minus:
            result = Expression(SymbolMinus, result)
        result = Expression(SymbolHoldForm, result)
        return do_format_expression(result, evaluation, form)


def do_format_complex(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Type[BaseElement]:
    if form is SymbolFullForm:
        return do_format_expression(
            Expression(
                Expression(SymbolHoldForm, SymbolComplex), element.real, element.imag
            ),
            evaluation,
            form,
        )

    parts: typing.List[Any] = []
    if element.is_machine_precision() or not element.real.is_zero:
        parts.append(element.real)
    if element.imag.sameQ(Integer(1)):
        parts.append(SymbolI)
    else:
        parts.append(Expression(SymbolTimes, element.imag, SymbolI))

    if len(parts) == 1:
        result = parts[0]
    else:
        result = Expression(SymbolPlus, *parts)

    return do_format_expression(Expression(SymbolHoldForm, result), evaluation, form)


def do_format_expression(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Type[BaseElement]:
    # # not sure how much useful is this format_cache
    # if element._format_cache is None:
    #    element._format_cache = {}

    # last_evaluated_time, expr = element._format_cache.get(form, (None, None))
    # if last_evaluated_time is not None and expr is not None:
    # if True
    #    symbolname = expr.get_name()
    #    if symbolname != "":
    #        if not evaluation.definitions.is_uncertain_final_value(
    #            last_evaluated_time, set((symbolname,))
    #        ):
    #            return expr
    expr = do_format_element(element, evaluation, form)
    # element._format_cache[form] = (evaluation.definitions.now, expr)
    return expr


def parenthesize(
    precedence: int, element: Type[BaseElement], element_boxes, when_equal: bool
) -> Type[Expression]:
    """
    "Determines if ``element_boxes`` needs to be surrounded with parenthesis.
    This is done based on ``precedence`` and the computed preceence of
    ``element``.  The adjusted ListExpression is returned.

    If when_equal is True, parentheses will be added if the two
    precedence values are equal.
    """
    while element.has_form("HoldForm", 1):
        element = element.elements[0]

    if element.has_form(("Infix", "Prefix", "Postfix"), 3, None):
        element_prec = element.elements[2].value
    elif element.has_form("PrecedenceForm", 2):
        element_prec = element.elements[1].value
    # If "element" is a negative number, we need to parenthesize the number. (Fixes #332)
    elif isinstance(element, (Integer, Real)) and element.value < 0:
        # Force parenthesis by adjusting the surrounding context's precedence value,
        # We can't change the precedence for the number since it, doesn't
        # have a precedence value.
        element_prec = precedence
    else:
        element_prec = builtins_precedence.get(element.get_head())
    if precedence is not None and element_prec is not None:
        if precedence > element_prec or (precedence == element_prec and when_equal):
            return Expression(
                SymbolRowBox,
                ListExpression(StringLParen, element_boxes, StringRParen),
            )
    return element_boxes


element_formatters[Rational] = do_format_rational
element_formatters[Complex] = do_format_complex
element_formatters[Expression] = do_format_expression
