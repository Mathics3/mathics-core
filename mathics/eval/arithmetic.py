# -*- coding: utf-8 -*-

"""
helper functions for arithmetic evaluation
"""

from typing import List, Optional

import mpmath
import sympy

from mathics.core.atoms import Integer0, Integer1, Number
from mathics.core.convert.mpmath import from_mpmath
from mathics.core.convert.sympy import from_sympy
from mathics.core.element import BaseElement
from mathics.core.number import dps, min_prec
from mathics.eval.numbers import eval_accuracy


def associate_powers(expr: BaseElement) -> BaseElement:
    """
    base^a^b^c^... -> base^(a*b*c*...)
    """
    powers = []
    base = expr
    while base.has_form("Power", 2):
        base, power = base.elements
        powers.append(power)

    if len(powers) < 2:
        return base

    return Expression(SymbolPower, base, Expression(SymbolTimes, *powers))


def eval_add_numbers(
    numbers: List[Number],
) -> Number:
    """
    Add the numbers.
    """
    if len(numbers) == 0:
        return Integer0

    prec = min_prec(*numbers)
    if prec is not None:
        is_machine_precision = any(number.is_machine_precision() for number in numbers)
        if is_machine_precision:
            numbers = [item.to_mpmath() for item in numbers]
            number = mpmath.fsum(numbers)
            return from_mpmath(number)
        else:
            # For a sum, what is relevant is the minimum accuracy of the terms
            item_accuracies = (eval_accuracy(item) for item in numbers)
            acc = min(
                (item_acc for item_acc in item_accuracies if item_acc is not None),
                default=None,
            )
            with mpmath.workprec(prec):
                numbers = [item.to_mpmath() for item in numbers]
                number = mpmath.fsum(numbers)
                return from_mpmath(number, acc=acc)
    else:
        return from_sympy(sum(item.to_sympy() for item in numbers))


def eval_multiply_numbers(
    numbers: List[Number],
    prec: Optional[int] = None,
    is_machine_precision: bool = False,
) -> Number:
    """
    Multiplies the numbers.
    """
    if len(numbers) == 0:
        return Integer1
    prec = min_prec(*numbers)
    if prec is not None:
        is_machine_precision = any(number.is_machine_precision() for number in numbers)
        if is_machine_precision:
            numbers = [item.to_mpmath() for item in numbers]
            number = mpmath.fprod(numbers)
            return from_mpmath(number)
        else:
            with mpmath.workprec(prec):
                numbers = [item.to_mpmath() for item in numbers]
                number = mpmath.fprod(numbers)
                return from_mpmath(number, dps(prec))
    else:
        number = sympy.Mul(*[item.to_sympy() for item in numbers])
        return from_sympy(number)
