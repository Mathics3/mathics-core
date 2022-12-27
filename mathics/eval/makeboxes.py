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
from mathics.core.definitions import OutputForms
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
    SymbolOutputForm,
    SymbolRational,
    SymbolRowBox,
    SymbolStandardForm,
)

builtins_precedence: Dict[Symbol, int] = {}

element_formatters = {}


# this temporarily replaces the _BoxedString class
def _boxed_string(string: str, **options):
    from mathics.builtin.box.layout import StyleBox

    return StyleBox(String(string), **options)


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


def eval_makeboxes(
    self, expr, evaluation: Evaluation, form=SymbolStandardForm
) -> Expression:
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
            if not (form is SymbolOutputForm and head is SymbolStandardForm):
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
                        String(".."),
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
                        String("..."),
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
    # For negative values, ensure that the element_precedence is at least the precedence. (Fixes #332)
    elif isinstance(element, (Integer, Real)) and element.value < 0:
        element_prec = precedence
    else:
        element_prec = builtins_precedence.get(element.get_head())
    if precedence is not None and element_prec is not None:
        if precedence > element_prec or (precedence == element_prec and when_equal):
            return Expression(
                SymbolRowBox,
                ListExpression(String("("), element_boxes, String(")")),
            )
    return element_boxes


element_formatters[Rational] = do_format_rational
element_formatters[Complex] = do_format_complex
element_formatters[Expression] = do_format_expression
