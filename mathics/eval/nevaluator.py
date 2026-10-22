# cython: language_level=3
# -*- coding: utf-8 -*-

"""
This module contains basic low-level functions that combine an Expression
with an Evaluation object to produce a new Expression following generic
algorithms.


"""

from math import ceil
from typing import List, Optional, Tuple

import mpmath
import sympy

from mathics.core.atoms import (
    Complex,
    Integer,
    Integer1,
    MachineReal,
    Number,
    PrecisionReal,
    Rational,
    Real,
)
from mathics.core.attributes import A_N_HOLD_ALL, A_N_HOLD_FIRST, A_N_HOLD_REST
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.number import (
    LOG2_10,
    MACHINE_PRECISION_VALUE,
    PrecisionValueError,
    get_closest_precision,
    prec as number_prec,
)
from mathics.core.symbols import Atom, SymbolList
from mathics.core.systemsymbols import (
    SymbolDirectedInfinity,
    SymbolInfinity,
    SymbolMachinePrecision,
    SymbolMaxExtraPrecision,
    SymbolN,
    SymbolRoot,
    SymbolRootSum,
    SymbolRule,
)


# FIXME: Add the two-argument form N[expr, n]
def eval_N(
    expression: BaseElement,
    evaluation: Evaluation,
    prec: BaseElement = SymbolMachinePrecision,
) -> Optional[BaseElement]:
    """
    Equivalent to Expression(SymbolN, expression).evaluate(evaluation)
    """
    evaluated_expression = (
        expression if expression.is_literal else expression.evaluate(evaluation)
    )

    try:
        p = get_closest_precision(prec, evaluation, show_messages=False)
    except PrecisionValueError:
        p = None
    if p is not None:
        # As in N, with extra digits when they are needed.
        result, _ = eval_NValues_to_precision(
            evaluated_expression,
            MachineReal(float(p)),
            p,
            get_max_extra_precision(evaluation),
            evaluation,
        )
        return expression if result is None else result

    result = eval_NValues(evaluated_expression, prec, evaluation)
    if result is None:
        return expression

    if result.is_literal:
        return result

    return result.evaluate(evaluation)


def get_max_extra_precision(evaluation: Evaluation) -> float:
    """The value of $MaxExtraPrecision, as a number of digits."""
    max_extra = SymbolMaxExtraPrecision.evaluate(evaluation)
    if isinstance(max_extra, (Integer, Rational, Real)):
        return max(0.0, float(max_extra.value))
    if is_infinity(max_extra):
        return float("inf")
    return 0.0


def eval_NValues(
    expr: BaseElement, prec: BaseElement, evaluation: Evaluation
) -> Optional[BaseElement]:
    """
    Looks for the numeric value of ```expr`` with precision ``prec`` by applying NValues rules
    stored in ``evaluation.definitions``.
    If ``prec`` can not be evaluated as a number, returns None; otherwise, returns an expression.
    """
    from mathics.core.convert.sympy import from_sympy

    if prec.has_form(SymbolList, None):
        return eval_NValues_with_accuracy(expr, prec, evaluation)

    # If expr is a List, or a Rule (or maybe expressions with heads for
    # which we are sure do not have NValues or special attributes)
    # just apply `eval_NValues` to each element and return the new list.
    if hasattr(expr, "head") and expr.head in (SymbolList, SymbolRule):
        elements = expr.elements

        # FIXME: incorporate these lines into Expression call
        result = (
            ListExpression(expr.head)
            if expr.head is SymbolList
            else Expression(expr.head)
        )
        new_elements = [
            eval_NValues(element, prec, evaluation) for element in expr.elements
        ]
        result.elements = tuple(
            new_element if new_element else element
            for element, new_element in zip(elements, new_elements)
        )
        result._build_elements_properties()
        return result

    # Get the precision goal to use in non-integer numbers
    try:
        # Here ``get_closest_precision`` is called with ``show_messages``
        # set to ``False`` to avoid showing the same warnings repeatedly.
        d = get_closest_precision(prec, evaluation, show_messages=False)
    except PrecisionValueError:
        # We can ensure that the function always returns an expression if
        # the exception was captured by the caller.
        return

    # If the expression is a number, just round it to the required
    # precision.
    if isinstance(expr, Number):
        return expr.round() if d is None else expr.round(int(d))

    # Special case for the Root builtin
    # This should be implemented as an NValue
    if expr.has_form((SymbolRoot, SymbolRootSum), 2):
        return from_sympy(sympy.N(expr.to_sympy(), d))

    # Here we look for the NValues associated to the
    # lookup_name of the expression.
    # If a rule is found and successfully applied,
    # reevaluate the result and apply `eval_NValues` again.
    # This should be implemented as a loop instead of
    # recursively.
    name = expr.get_symbol_definition_name()
    if name != "":
        nexpr = Expression(SymbolN, expr, normalize_n_precision(prec))
        try:
            result: Optional[BaseElement] = evaluation.definitions.get_value(
                name, "System`NValues", nexpr, evaluation
            )
        except ValueError:
            result = None
        if result is not None:
            if not result.sameQ(nexpr):
                result = result.evaluate(evaluation)
                result = eval_NValues(result, prec, evaluation)
                return result

    # If we are here, it is because there are no NValues that match
    # the expression. Here, if we arrive at an atomic expression,
    # just return it.
    if isinstance(expr, Atom):
        return expr
    else:
        # Otherwise, look at the attributes, determine over which elements
        # we need to apply `eval_NValues`, and rebuild the expression with
        # the results.
        attributes = expr.head.get_attributes(evaluation.definitions)
        head = expr.head
        elements = expr.get_mutable_elements()
        if A_N_HOLD_ALL & attributes:
            eval_range = ()
        elif A_N_HOLD_FIRST & attributes:
            eval_range = range(1, len(elements))
        elif A_N_HOLD_REST & attributes:
            if len(expr.elements) > 0:
                eval_range = (0,)
            else:
                eval_range = ()
        else:
            eval_range = range(len(elements))

        newhead = eval_NValues(head, prec, evaluation)
        head = head if newhead is None else newhead

        for index in eval_range:
            new_element = eval_NValues(elements[index], prec, evaluation)
            if new_element:
                elements[index] = new_element

        # FIXME: incorporate these 3 lines into Expression call
        result = Expression(head)
        result.elements = elements
        result._build_elements_properties()
        return result


LOG2_10_FLOAT = float(LOG2_10)


def is_infinity(element: BaseElement) -> bool:
    """Is ``element`` Infinity, evaluated or not?"""
    return element is SymbolInfinity or (
        element.has_form(SymbolDirectedInfinity, 1)
        and element.elements[0].sameQ(Integer1)
    )


def normalize_n_precision(prec: BaseElement) -> BaseElement:
    """
    The form in which a precision, or a {precision, accuracy} pair, is
    given to the N rules: as in WMA, a number is a machine real.
    """
    if isinstance(prec, (Integer, Rational, Real)) and not isinstance(
        prec, MachineReal
    ):
        return MachineReal(float(prec.value))
    if prec.has_form(SymbolList, 2):
        elements = tuple(normalize_n_precision(element) for element in prec.elements)
        if any(new is not old for new, old in zip(elements, prec.elements)):
            return ListExpression(*elements)
    return prec


def eval_NValues_with_accuracy(
    expr: BaseElement, prec_acc: BaseElement, evaluation: Evaluation
) -> Optional[BaseElement]:
    """
    Evaluates ``N[expr, {prec, acc}]``: each inexact number in the result
    has at most ``prec`` digits of precision and ``acc`` digits of accuracy,
    so its precision is ``min(prec, acc + Log10[Abs[x]])``. Either of them
    can be ``Infinity``. Returns None if ``{prec, acc}`` is not valid.

    As in WMA, the precision of such a number can be fractional.
    """
    prec_acc_elements = prec_acc.get_elements()
    if len(prec_acc_elements) != 2:
        return None
    prec, acc = prec_acc_elements
    if prec is SymbolMachinePrecision:
        return eval_NValues(expr, prec, evaluation)

    if is_infinity(prec):
        p = None
    else:
        try:
            p = get_closest_precision(prec, evaluation, show_messages=False)
        except PrecisionValueError:
            return None
        if p is None:
            return None

    if is_infinity(acc):
        a = None
    elif acc is SymbolMachinePrecision:
        a = MACHINE_PRECISION_VALUE
    else:
        a = acc.round_to_float(evaluation) if hasattr(acc, "round_to_float") else None
        if a is None:
            return None

    # A rule given for this very pair, as in N[x, {10, 5}] = v.
    name = expr.get_symbol_definition_name()
    if name != "":
        nexpr = Expression(SymbolN, expr, normalize_n_precision(prec_acc))
        try:
            result = evaluation.definitions.get_value(
                name, "System`NValues", nexpr, evaluation
            )
        except ValueError:
            result = None
        if result is not None and not result.sameQ(nexpr):
            expr = result.evaluate(evaluation)

    if a is None:
        return expr if p is None else eval_NValues(expr, prec, evaluation)

    # Without a bound on the precision, the working precision has to be
    # enough for the largest number in the result.
    working_prec = p if p is not None else max(a, 0) + 20
    result = _eval_NValues_evaluated(expr, working_prec, evaluation)
    if p is None and result is not None:
        needed = _max_precision_for_accuracy(result, a)
        if needed > working_prec:
            result = _eval_NValues_evaluated(expr, needed + 1, evaluation)
    if result is None:
        return None
    return _bound_accuracy(result, a)


def _eval_NValues_evaluated(
    expr: BaseElement, prec: float, evaluation: Evaluation
) -> Optional[BaseElement]:
    result = eval_NValues(expr, Integer(ceil(prec)), evaluation)
    return None if result is None else result.evaluate(evaluation)


def eval_NValues_to_precision(
    expr: BaseElement,
    prec: BaseElement,
    p: float,
    max_extra: float,
    evaluation: Evaluation,
) -> Tuple[Optional[BaseElement], bool]:
    """
    Evaluates ``N[expr, p]``, where ``prec`` is ``p`` as given to the N
    rules. As in WMA, each arbitrary-precision number in the result has
    precision ``p``, unless an input number had less.

    When the computation loses digits, as in a cancellation or a product
    of ``p``-digit numbers, it is done again with more digits, up to
    ``max_extra`` more than ``p``, for as long as a number short of ``p``
    digits gains some. A new result is used only if it has the same form
    as the first one: N rules are given the working precision, and one for
    ``p`` itself may not match it.

    Returns a pair: the result, and whether the extra digits were not
    enough.
    """
    result = eval_NValues(expr, prec, evaluation)
    if result is None:
        return None, False
    result = result.evaluate(evaluation)
    precisions = _precisions(result)
    short = [i for i, digits in enumerate(precisions) if digits < p]
    working = p
    exhausted = False
    while short:
        if working >= p + max_extra:
            # As in WMA, there is no message when no extra digit was allowed.
            exhausted = working > p
            break
        # The most digits lost at the last working precision, and one more.
        lost = max(working - precisions[i] for i in short)
        working = min(p + lost + 1, p + max_extra)
        retry = _eval_NValues_evaluated(expr, working, evaluation)
        if retry is None or not _same_form(result, retry):
            break
        retry_precisions = _precisions(retry)
        if len(retry_precisions) != len(precisions):
            break
        # A number that gains nothing has an input with fewer than p digits.
        gained = [i for i in short if retry_precisions[i] > precisions[i]]
        if not gained:
            break
        result, precisions = retry, retry_precisions
        short = [i for i in gained if precisions[i] < p]
    return _bound_precision(result, p), exhausted


def _precisions(expr: BaseElement) -> List[float]:
    """
    The precisions of the arbitrary-precision numbers in ``expr``, in
    order. A zero, which has no precision, counts as infinitely precise.
    """
    if isinstance(expr, PrecisionReal):
        return [float("inf") if expr.is_zero else expr.precision10]
    if isinstance(expr, Complex):
        return _precisions(expr.real) + _precisions(expr.imag)
    if isinstance(expr, Atom):
        return []
    return [
        digits
        for element in (expr.head,) + tuple(expr.elements)
        for digits in _precisions(element)
    ]


def _same_form(expr: BaseElement, other: BaseElement) -> bool:
    """Are ``expr`` and ``other`` the same, up to the values of their numbers?"""
    if isinstance(expr, Number) and isinstance(other, Number):
        return True
    if isinstance(expr, Atom) or isinstance(other, Atom):
        return expr.sameQ(other)
    return (
        len(expr.elements) == len(other.elements)
        and _same_form(expr.head, other.head)
        and all(map(_same_form, expr.elements, other.elements))
    )


def _bound_precision(expr: BaseElement, p: float) -> BaseElement:
    """
    Lowers the precision of each nonzero arbitrary-precision number in
    ``expr`` to at most ``p`` digits.
    """
    if isinstance(expr, PrecisionReal):
        if expr.is_zero or expr.precision10 <= p:
            return expr
        return PrecisionReal.from_value(expr.extended_value, p)
    if isinstance(expr, Complex):
        return Complex(_bound_precision(expr.real, p), _bound_precision(expr.imag, p))
    if isinstance(expr, Atom):
        return expr
    head = _bound_precision(expr.head, p)
    elements = tuple(_bound_precision(element, p) for element in expr.elements)
    if head is expr.head and all(
        new is old for new, old in zip(elements, expr.elements)
    ):
        return expr
    if head is SymbolList:
        return ListExpression(*elements)
    return Expression(head, *elements)


def _max_precision_for_accuracy(expr: BaseElement, acc: float) -> float:
    """The largest precision that ``acc`` digits of accuracy need in ``expr``."""
    if isinstance(expr, PrecisionReal):
        return 0 if expr.is_zero else acc + float(mpmath.log10(abs(expr.to_mpmath())))
    if isinstance(expr, Complex):
        return max(
            _max_precision_for_accuracy(expr.real, acc),
            _max_precision_for_accuracy(expr.imag, acc),
        )
    if isinstance(expr, Atom):
        return 0
    return max(
        (_max_precision_for_accuracy(element, acc) for element in expr.elements),
        default=0,
    )


def _bound_accuracy(expr: BaseElement, acc: float) -> BaseElement:
    """
    Lowers the accuracy of each arbitrary-precision number in ``expr``
    to at most ``acc`` digits. A number smaller than that accuracy
    becomes a zero of that accuracy.
    """
    if isinstance(expr, PrecisionReal):
        value = expr.value
        if expr.is_zero:
            digits = 0.0
        else:
            digits = acc + float(mpmath.log10(abs(expr.to_mpmath())))
        if digits <= 0:
            return PrecisionReal(
                sympy.Float(0, precision=max(1, round((acc + 1) * LOG2_10_FLOAT))),
                acc,
            )
        if digits >= expr.precision10:
            return expr
        return PrecisionReal.from_value(expr.extended_value, digits)
    if isinstance(expr, Complex):
        return Complex(_bound_accuracy(expr.real, acc), _bound_accuracy(expr.imag, acc))
    if isinstance(expr, Atom):
        return expr
    elements = tuple(_bound_accuracy(element, acc) for element in expr.get_elements())
    if all(new is old for new, old in zip(elements, expr.get_elements())):
        return expr
    if expr.get_head() is SymbolList:
        return ListExpression(*elements)
    return Expression(expr.get_head(), *elements)


# TODO:  Revisit - can this be simplified? Is there some broader framework this fits into?


# comment mmatera: Other methods that I would like to have here, as non-member methods are
