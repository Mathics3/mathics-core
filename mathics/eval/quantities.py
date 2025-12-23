# -*- coding: utf-8 -*-
"""
Implementation of mathics.builtin.quantities
"""
from typing import Optional

from pint import UnitRegistry
from pint.errors import DimensionalityError, UndefinedUnitError

from mathics.core.atoms import (
    Integer,
    Integer0,
    Integer1,
    IntegerM1,
    Number,
    Rational,
    Real,
    String,
)
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolPower, SymbolQuantity, SymbolTimes
from mathics.core.util import strip_string_quotes

ureg = UnitRegistry()
Q_ = ureg.Quantity


def add_quantities(
    mag_1: float, u_1: BaseElement, mag_2: float, u_2: BaseElement, evaluation=None
) -> Optional[Expression]:
    """Try to add two quantities"""
    cmp = compare_units(u_1, u_2)
    if cmp is None:
        return None
    if cmp == 1:
        conv = convert_units(Integer1, u_1, u_2, evaluation).elements[0]
        if conv is not Integer1:
            mag_1 = conv * mag_1
        u_1 = u_2
    elif cmp == -1:
        conv = convert_units(Integer1, u_2, u_1, evaluation).elements[0]
        if conv is not Integer1:
            mag_2 = conv * mag_2
    mag = mag_1 + mag_2
    if evaluation:
        mag = mag.evaluate(evaluation)
    return Expression(SymbolQuantity, mag, u_1)


def compare_units(u_1: BaseElement, u_2: BaseElement) -> Optional[int]:
    """
    Compare two units.
    if both units are equal, return 0.
    If u1>u2 returns 1
    If u1<u2 returns -1
    if the units can not be compared return None
    """
    u_1_str = expression_to_pint_string(u_1)
    u_2_str = expression_to_pint_string(u_2)

    if u_1_str == u_2_str:
        return 0

    # Can not compare two non-multiplicative quantities
    if not (is_multiplicative(u_1_str) and is_multiplicative(u_2_str)):
        return None

    try:
        conversion_factor = Q_(1, u_1_str).to(u_2_str).magnitude
    except DimensionalityError:
        return None

    if conversion_factor == 1:
        return 0

    return 1 if conversion_factor > 1 else -1


def convert_units(
    magnitude: BaseElement,
    src: BaseElement,
    tgt: Optional[BaseElement] = None,
    evaluation: Optional[Evaluation] = None,
) -> Expression:
    """
    Implement the unit conversion

    The Python "pint" library mixes in a Python numeric value as a multiplier inside
    a Mathics Expression. Here we pick out that multiplier and
    convert it from a Python numeric to a Mathics numeric.
    """
    assert isinstance(magnitude, Number)
    assert isinstance(src, BaseElement)
    assert tgt is None or isinstance(tgt, BaseElement)
    src_unit: str = expression_to_pint_string(src)

    if tgt is not None:
        tgt_unit: Optional[str] = expression_to_pint_string(tgt)
        try:
            converted_quantity = Q_(1, src_unit).to(tgt_unit)
        except (UndefinedUnitError, DimensionalityError) as exc:
            raise ValueError("incompatible or undefined units") from exc
    else:
        converted_quantity = Q_(1, src_unit).to_base_units()

    tgt_unit = str(converted_quantity.units)
    scale = round_if_possible(converted_quantity.magnitude)

    if is_multiplicative(src_unit) and is_multiplicative(tgt_unit):
        if scale is not Integer1:
            magnitude = scale * magnitude
    else:
        offset = round_if_possible(Q_(0, src_unit).to(tgt_unit).magnitude)
        if offset is not Integer0:
            scale = round_if_possible(scale.value - offset.value)
            if scale.value != 1:
                magnitude = magnitude * scale
            magnitude = magnitude + offset
        else:
            magnitude = scale * magnitude

    # If evaluation is provided, try to simplify
    if evaluation is not None:
        magnitude = magnitude.evaluate(evaluation)
    return Expression(SymbolQuantity, magnitude, pint_str_to_expression(tgt_unit))


def expression_to_pint_string(expr: BaseElement) -> str:
    """
    Convert a unit expression to a string
    compatible with pint
    """
    if isinstance(expr, String):
        result = expr.value
    elif expr.has_form("Times", None):
        result = "*".join(expression_to_pint_string(factor) for factor in expr.elements)
    elif expr.has_form("Power", 2):
        base, power = expr.elements
        if not isinstance(power, Integer):
            raise ValueError("invalid unit expression")
        result = f" (({expression_to_pint_string(base)})**{power.value}) "
    else:
        raise ValueError("invalid unit expression")
    return normalize_unit_name(result)


def is_multiplicative(unit: str) -> bool:
    """
    Check if a quantity is multiplicative. For example,
    centimeters are "multiplicative" because is a multiple
    of its basis unit "meter"
    On the other hand, "celsius" is not: the magnitude in Celsius
    is the magnitude in Kelvin plus an offset.
    """
    # unit = normalize_unit_name(unit)
    try:
        return ureg._units[unit].converter.is_multiplicative
    except (UndefinedUnitError, KeyError):
        try:
            unit = ureg.get_name(unit)
        except UndefinedUnitError:
            # if not found, assume it is
            return True
    try:
        return ureg._units[unit].converter.is_multiplicative
    except (UndefinedUnitError, KeyError):
        # if not found, assume it is
        return True


def normalize_unit_expression(unit: BaseElement) -> str:
    """Normalize the expression representing a unit"""
    unit_str = expression_to_pint_string(unit)
    return pint_str_to_expression(unit_str)


def normalize_unit_expression_with_magnitude(
    unit: BaseElement, magnitude: BaseElement
) -> str:
    """
    Normalize the expression representing a unit,
    taking into account the numeric value
    """
    unit_str = expression_to_pint_string(unit)

    m = magnitude.value if isinstance(magnitude, Number) else 2.0
    unit_str = normalize_unit_name_with_magnitude(unit_str, m)
    return pint_str_to_expression(unit_str)


def normalize_unit_name(unit: str) -> str:
    """The normalized name of a unit"""
    return normalize_unit_name_with_magnitude(unit, 1)


def normalize_unit_name_with_magnitude(unit: str, magnitude) -> str:
    """The normalized name of a unit"""
    unit = unit.strip()
    try:
        return str(Q_(magnitude, unit).units)
    except UndefinedUnitError:
        unit = unit.replace(" ", "_")
        unit.replace("_*", " *")
        unit.replace("*_", "* ")
        unit.replace("/_", "/ ")
        unit.replace("_/", " /")
        unit.replace("_(", " (")
        unit.replace(")_", ") ")

    try:
        return str(Q_(magnitude, unit).units)
    except UndefinedUnitError:
        unit = unit.lower()

    try:
        return str(Q_(magnitude, unit).units)
    except UndefinedUnitError as exc:
        raise ValueError("undefined units") from exc


def pint_str_to_expression(unit: str) -> BaseElement:
    """
    Produce a Mathics Expression from a pint unit expression
    """
    assert isinstance(unit, str)
    unit = normalize_unit_name(unit)

    factors = unit.split(" / ")
    factor = factors[0]
    divisors = factors[1:]
    factors = factor.split(" * ")

    def process_factor(factor):
        base_and_power = factor.split(" ** ")
        if len(base_and_power) == 1:
            return String(normalize_unit_name(factor))
        base, power = base_and_power
        power_mathics = Integer(int(power))
        base_mathics = String(normalize_unit_name(base))
        return Expression(SymbolPower, base_mathics, power_mathics)

    factors_mathics = [process_factor(factor) for factor in factors] + [
        Expression(SymbolPower, process_factor(factor), IntegerM1)
        for factor in divisors
    ]
    if len(factors_mathics) == 1:
        return factors_mathics[0]
    return Expression(SymbolTimes, *factors_mathics)


def round_if_possible(x_float: float) -> Number:
    """
    Produce an exact Mathics number from x
    when it is possible.
    If x is integer, return Integer(x)
    If 1/x is integer, return Rational(1,1/x)
    Otherwise, return Real(x)
    """
    if x_float - int(x_float) == 0:
        return Integer(x_float)

    inv_x = 1 / x_float
    if inv_x == int(inv_x):
        return Rational(1, int(inv_x))
    return Real(x_float)


def validate_pint_unit(unit: str) -> bool:
    """Test if `unit` is a valid unit"""
    try:
        ureg.get_name(unit)
    except UndefinedUnitError:
        unit = unit.lower().replace(" ", "_")
    else:
        return True

    try:
        ureg.get_name(unit)
    except UndefinedUnitError:
        return False
    return True


def validate_unit_expression(unit: BaseElement) -> bool:
    """Test if `unit` is a valid unit"""
    if isinstance(unit, String):
        unit_value = strip_string_quotes(unit.value)
        return validate_pint_unit(unit_value)
    if unit.has_form("Power", 2):
        base, exp = unit.elements
        if not isinstance(exp, Integer):
            return False
        return validate_unit_expression(base)
    if unit.has_form("Times", None):
        return all(validate_unit_expression(factor) for factor in unit.elements)
    return False
