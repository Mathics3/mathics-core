from typing import Callable, Optional, Tuple

import mpmath
import sympy

from mathics.core.atoms import Integer0, Integer1, Integer2, IntegerM1, Number
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement
from mathics.core.expression import Expression
from mathics.core.number import FP_MANTISA_BINARY_DIGITS, SpecialValueError, min_prec
from mathics.core.symbols import Symbol, SymbolPlus, SymbolPower, SymbolTimes
from mathics.core.systemsymbols import (
    SymbolComplexInfinity,
    SymbolDirectedInfinity,
    SymbolIndeterminate,
    SymbolInfinity,
)


# @lru_cache(maxsize=4096)
def call_mpmath(
    mpmath_function: Callable, mpmath_args: tuple, prec: Optional[int] = None
):
    """
    calls the mpmath_function with mpmath_args parms
    if prec=None, use floating point arithmetic.
    Otherwise, work with prec bits of precision.
    """
    if prec is None:
        prec = FP_MANTISA_BINARY_DIGITS
    with mpmath.workprec(prec):
        try:
            result_mp = mpmath_function(*mpmath_args)
            if prec != FP_MANTISA_BINARY_DIGITS:
                return from_mpmath(result_mp, prec)
            return from_mpmath(result_mp)
        except ValueError as exc:
            text = str(exc)
            if text == "gamma function pole":
                return SymbolComplexInfinity
            else:
                raise
        except ZeroDivisionError:
            return
        except SpecialValueError as exc:
            return Symbol(exc.name)


def eval_mpmath_function(
    mpmath_function: Callable, *args: Tuple[Number], prec: Optional[int] = None
) -> Optional[Number]:
    """
    Call the mpmath function `mpmath_function` with the arguments `args`
    working with precision `prec`. If `prec` is `None`, work with machine
    precision.

    Return a Mathics Number or None if the evaluation failed.
    """
    if prec is None:
        # if any argument has machine precision then the entire calculation
        # is done with machine precision.
        float_args = [arg.round().get_float_value(permit_complex=True) for arg in args]
        if None in float_args:
            return

        return call_mpmath(mpmath_function, tuple(float_args))
    else:
        with mpmath.workprec(prec):
            # to_mpmath seems to require that the precision is set from outside
            mpmath_args = [x.to_mpmath() for x in args]
            if None in mpmath_args:
                return
            return call_mpmath(mpmath_function, tuple(mpmath_args), prec)


def eval_Plus(*items: Tuple[BaseElement]) -> BaseElement:
    "evaluate Plus for general elements"
    elements = []
    last_item = last_count = None

    prec = min_prec(*items)
    is_machine_precision = any(item.is_machine_precision() for item in items)
    numbers = []

    def append_last():
        if last_item is not None:
            if last_count == 1:
                elements.append(last_item)
            else:
                if last_item.has_form("Times", None):
                    elements.append(
                        Expression(
                            SymbolTimes, from_sympy(last_count), *last_item.elements
                        )
                    )
                else:
                    elements.append(
                        Expression(SymbolTimes, from_sympy(last_count), last_item)
                    )

    for item in items:
        if isinstance(item, Number):
            numbers.append(item)
        else:
            count = rest = None
            if item.has_form("Times", None):
                for element in item.elements:
                    if isinstance(element, Number):
                        count = element.to_sympy()
                        rest = item.get_mutable_elements()
                        rest.remove(element)
                        if len(rest) == 1:
                            rest = rest[0]
                        else:
                            rest.sort()
                            rest = Expression(SymbolTimes, *rest)
                        break
            if count is None:
                count = sympy.Integer(1)
                rest = item
            if last_item is not None and last_item == rest:
                last_count = last_count + count
            else:
                append_last()
                last_item = rest
                last_count = count
    append_last()
    if numbers:
        # TODO: reorganize de conditions to avoid compute unnecesary
        # quantities. In particular, is we check mathine_precision,
        # we do not need to evaluate prec.
        if prec is not None:
            if is_machine_precision:
                numbers = [item.to_mpmath() for item in numbers]
                number = mpmath.fsum(numbers)
                number = from_mpmath(number)
            else:
                # TODO: If there are Complex numbers in `numbers`,
                # and we are not working in machine precision, compute the sum of the real and imaginary
                # parts separately, to preserve precision. For example,
                # 1.`2 + 1.`3 I should produce
                # Complex[1.`2, 1.`3]
                # but with this implementation returns
                # Complex[1.`2, 1.`2]
                #
                # TODO: if the precision are not equal for each number,
                # we should estimate the result precision by computing the sum of individual errors
                # prec =  sum(abs(n.value) * 2**(-n.value._prec)    for n in number if n.value._prec is not None)/sum(abs(n))
                with mpmath.workprec(prec):
                    numbers = [item.to_mpmath() for item in numbers]
                    number = mpmath.fsum(numbers)
                    number = from_mpmath(number, precision=prec)
        else:
            number = from_sympy(sum(item.to_sympy() for item in numbers))
    else:
        number = Integer0

    if not number.sameQ(Integer0):
        elements.insert(0, number)

    if not elements:
        return Integer0
    elif len(elements) == 1:
        return elements[0]
    else:
        elements.sort()
        return Expression(SymbolPlus, *elements)


def eval_Times(*items):
    elements = []
    numbers = []
    infinity_factor = False
    # These quantities only have sense if there are numeric terms.
    # Also, prec is only needed if is_machine_precision is not True.
    prec = min_prec(*items)
    is_machine_precision = any(item.is_machine_precision() for item in items)

    # find numbers and simplify Times -> Power
    for item in items:
        if isinstance(item, Number):
            numbers.append(item)
        elif elements and item == elements[-1]:
            elements[-1] = Expression(SymbolPower, elements[-1], Integer2)
        elif (
            elements
            and item.has_form("Power", 2)
            and elements[-1].has_form("Power", 2)
            and item.elements[0].sameQ(elements[-1].elements[0])
        ):
            elements[-1] = Expression(
                SymbolPower,
                elements[-1].elements[0],
                Expression(SymbolPlus, item.elements[1], elements[-1].elements[1]),
            )
        elif (
            elements
            and item.has_form("Power", 2)
            and item.elements[0].sameQ(elements[-1])
        ):
            elements[-1] = Expression(
                SymbolPower,
                elements[-1],
                Expression(SymbolPlus, item.elements[1], Integer1),
            )
        elif (
            elements
            and elements[-1].has_form("Power", 2)
            and elements[-1].elements[0].sameQ(item)
        ):
            elements[-1] = Expression(
                SymbolPower,
                item,
                Expression(SymbolPlus, Integer1, elements[-1].elements[1]),
            )
        elif item.get_head().sameQ(SymbolDirectedInfinity):
            infinity_factor = True
            if len(item.elements) > 0:
                direction = item.elements[0]
                if isinstance(direction, Number):
                    numbers.append(direction)
                else:
                    elements.append(direction)
        elif item.sameQ(SymbolInfinity) or item.sameQ(SymbolComplexInfinity):
            infinity_factor = True
        else:
            elements.append(item)

    if numbers:
        if prec is not None:
            if is_machine_precision:
                numbers = [item.to_mpmath() for item in numbers]
                number = mpmath.fprod(numbers)
                number = from_mpmath(number)
            else:
                with mpmath.workprec(prec):
                    numbers = [item.to_mpmath() for item in numbers]
                    number = mpmath.fprod(numbers)
                    number = from_mpmath(number, precision=prec)
        else:
            number = sympy.Mul(*[item.to_sympy() for item in numbers])
            number = from_sympy(number)
    else:
        number = Integer1

    if number.sameQ(Integer1):
        number = None
    elif number.is_zero:
        if infinity_factor:
            return SymbolIndeterminate
        return number
    elif number.sameQ(IntegerM1) and elements and elements[0].has_form("Plus", None):
        elements[0] = Expression(
            elements[0].get_head(),
            *[
                Expression(SymbolTimes, IntegerM1, element)
                for element in elements[0].elements
            ],
        )
        number = None

    if number is not None:
        elements.insert(0, number)

    if not elements:
        if infinity_factor:
            return SymbolComplexInfinity
        return Integer1

    if len(elements) == 1:
        ret = elements[0]
    else:
        ret = Expression(SymbolTimes, *elements)
    if infinity_factor:
        return Expression(SymbolDirectedInfinity, ret)
    else:
        return ret
