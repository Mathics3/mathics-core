"""
Format functions for arithmetic expressions.

"""

from mathics.builtin.arithmetic import create_infix
from mathics.core.atoms import (
    Complex,
    Integer,
    Integer1,
    IntegerM1,
    Number,
    Rational,
    Real,
    String,
)
from mathics.core.convert.expression import to_expression
from mathics.core.convert.sympy import from_sympy
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import SymbolDivide, SymbolHoldForm, SymbolPower, SymbolTimes
from mathics.core.systemsymbols import SymbolInfix, SymbolLeft, SymbolMinus
from mathics.format.form.util import PRECEDENCE_PLUS, PRECEDENCE_TIMES


def format_plus(items, evaluation: Evaluation):
    """format Times[___] using `op` as operator"""

    def negate(item):  # -> Expression (see FIXME below)
        if item.has_form("Times", 2, None):
            if isinstance(item.elements[0], Number):
                first, *rest = item.elements
                first = -first
                if first.sameQ(Integer1):
                    if len(rest) == 1:
                        return rest[0]
                    return Expression(SymbolTimes, *rest)

                return Expression(SymbolTimes, first, *rest)
            else:
                return Expression(SymbolTimes, IntegerM1, *item.elements)
        elif isinstance(item, Number):
            return from_sympy(-item.to_sympy())
        else:
            return Expression(SymbolTimes, IntegerM1, item)

    def is_negative(value) -> bool:
        if isinstance(value, Complex):
            real, imag = value.to_sympy().as_real_imag()
            if real <= 0 and imag <= 0:
                return True
        elif isinstance(value, Number) and value.to_sympy() < 0:
            return True
        return False

    elements = items.get_sequence()
    values = [to_expression(SymbolHoldForm, element) for element in elements[:1]]
    ops = []
    for element in elements[1:]:
        if (
            element.has_form("Times", 1, None) and is_negative(element.elements[0])
        ) or is_negative(element):
            element = negate(element)
            op = "-"
        else:
            op = "+"
        values.append(Expression(SymbolHoldForm, element))
        ops.append(String(op))
    return Expression(
        SymbolInfix,
        ListExpression(*values),
        ListExpression(*ops),
        Integer(PRECEDENCE_PLUS),
        SymbolLeft,
    )


def format_times(items, evaluation, op="\u2062"):
    """format Times[___] using `op` as operator"""

    def inverse(item):
        if item.has_form("Power", 2) and isinstance(  # noqa
            item.elements[1], (Integer, Rational, Real)
        ):
            neg = -item.elements[1]
            if neg.sameQ(Integer1):
                return item.elements[0]
            else:
                return Expression(SymbolPower, item.elements[0], neg)
        else:
            return item

    items = items.get_sequence()
    if len(items) < 2:
        return
    positive = []
    negative = []
    for item in items:
        if (
            item.has_form("Power", 2)
            and isinstance(item.elements[1], (Integer, Rational, Real))
            and item.elements[1].to_sympy() < 0
        ):  # nopep8
            negative.append(inverse(item))
        elif isinstance(item, Rational):
            numerator = item.numerator()
            if not numerator.sameQ(Integer1):
                positive.append(numerator)
            negative.append(item.denominator())
        else:
            positive.append(item)

    if positive and hasattr(positive[0], "value") and positive[0].value == -1:
        del positive[0]
        minus = True
    else:
        minus = False
    positive = [Expression(SymbolHoldForm, item) for item in positive]
    negative = [Expression(SymbolHoldForm, item) for item in negative]
    if positive:
        positive = create_infix(positive, op, PRECEDENCE_TIMES, "Left")
    else:
        positive = Integer1
    if negative:
        negative = create_infix(negative, op, PRECEDENCE_TIMES, "Left")
        result = Expression(
            SymbolDivide,
            Expression(SymbolHoldForm, positive),
            Expression(SymbolHoldForm, negative),
        )
    else:
        result = positive
    if minus:
        result = Expression(
            SymbolMinus, result
        )  # Expression('PrecedenceForm', result, 481))
    result = Expression(SymbolHoldForm, result)
    return result
