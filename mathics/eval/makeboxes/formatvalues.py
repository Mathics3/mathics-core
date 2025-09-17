# -*- coding: utf-8 -*-
"""
This module contains basic low-level functions that combine an ``Expression``
with an ``Evaluation`` objects to produce ``BoxExpressions``, following
formatting rules.
"""


from typing import Any, Callable, Dict, List, Optional, Type

from mathics.core.atoms import Complex, Integer, Rational, String, SymbolI
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
    SymbolNumberForm,
    SymbolPlus,
    SymbolPostfix,
    SymbolRepeated,
    SymbolRepeatedNull,
    SymbolTimes,
)
from mathics.core.systemsymbols import SymbolComplex, SymbolMinus, SymbolRational

# These Strings are used in Boxing output
StringElipsis = String("...")
StringLParen = String("(")
StringRParen = String(")")
StringRepeated = String("..")


# do_format_*

_element_formatters: Dict[
    Type[BaseElement],
    Callable[[BaseElement, Evaluation, Symbol], Optional[BaseElement]],
] = {}


def do_format(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Optional[BaseElement]:
    do_format_method = _element_formatters.get(type(element), do_format_element)
    return do_format_method(element, evaluation, form)


def do_format_element(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Optional[BaseElement]:
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
        if head in OutputForms and len(elements) == 1:
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
            do_format_fn = _element_formatters.get(type(formatted), do_format_element)
            result = do_format_fn(formatted, evaluation, form)
            if include_form and result is not None:
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
            if len(expr.get_elements()) != 1:
                return expr
            do_format_fn = _element_formatters.get(type(element), do_format_element)
            result = do_format_fn(expr, evaluation, form)
            if isinstance(result, Expression):
                expr = result

        elif (
            head is not SymbolNumberForm
            and not isinstance(expr, (Atom, BoxElementMixin))
            and head not in (SymbolGraphics, SymbolGraphics3D)
        ):
            new_elements = tuple(
                (
                    _element_formatters.get(type(element), do_format_element)(
                        element, evaluation, form
                    )
                    for element in expr.elements
                )
            )
            expr_head = expr.head
            do_format = _element_formatters.get(type(expr_head), do_format_element)
            head = do_format(expr_head, evaluation, form)
            expr = to_expression_with_specialization(head, *new_elements)

        if include_form:
            expr = Expression(form, expr)
        return expr
    finally:
        evaluation.dec_recursion_depth()


def do_format_rational(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Optional[BaseElement]:
    if not isinstance(element, Rational):
        return None
    if form is SymbolFullForm:
        return Expression(
            SymbolRational,
            element.numerator(),
            element.denominator(),
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
        result = do_format_expression(result, evaluation, form)
        return result


def do_format_complex(
    element: BaseElement, evaluation: Evaluation, form: Symbol
) -> Optional[BaseElement]:
    if not isinstance(element, Complex):
        return None
    if form is SymbolFullForm:
        return Expression(
            SymbolComplex,
            element.real,
            element.imag,
        )

    parts: List[Any] = []
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
) -> Optional[BaseElement]:
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


_element_formatters[Rational] = do_format_rational
_element_formatters[Complex] = do_format_complex
_element_formatters[Expression] = do_format_expression
