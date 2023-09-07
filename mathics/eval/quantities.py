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
    Number,
    Rational,
    Real,
    String,
)
from mathics.core.element import BaseElement
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolQuantity

ureg = UnitRegistry()
Q_ = ureg.Quantity


def add_quantities(
    mag_1: float, u_1: str, mag_2: float, u_2: str, evaluation=None
) -> Expression:
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
    return Expression(SymbolQuantity, mag, String(u_1))


def compare_units(u_1, u_2) -> Optional[int]:
    """
    Compare two units.
    if both units are equal, return 0.
    If u1>u2 returns 1
    If u1<u2 returns -1
    if the units can not be compared return None
    """
    u_1 = normalize_unit_name(u_1)
    u_2 = normalize_unit_name(u_2)

    if u_1 == u_2:
        return 0

    # Can not compare two non-multiplicative quantities
    if not (is_multiplicative(u_1) and is_multiplicative(u_2)):
        return None

    try:
        conversion_factor = Q_(1, u_1).to(u_2).magnitude
    except DimensionalityError:
        return None

    if conversion_factor == 1:
        return 0

    return 1 if conversion_factor > 1 else -1


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
    except UndefinedUnitError:
        unit = ureg.get_name(unit)

    try:
        return ureg._units[unit].converter.is_multiplicative
    except UndefinedUnitError as exc:
        raise ValueError("Unit is not a registered unit") from exc


def convert_units(
    magnitude: BaseElement,
    src_unit: str,
    tgt_unit: Optional[str] = None,
    evaluation: Optional[Evaluation] = None,
) -> Expression:
    """
    Implement the unit conversion

    The Python "pint" library mixes in a Python numeric value as a multiplier inside
    a Mathics Expression. Here we pick out that multiplier and
    convert it from a Python numeric to a Mathics numeric.
    """
    assert isinstance(magnitude, Number)
    src_unit = normalize_unit_name(src_unit)
    if tgt_unit:
        tgt_unit = normalize_unit_name(tgt_unit)
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
    return Expression(SymbolQuantity, magnitude, String(tgt_unit))


def normalize_unit_name(unit: str) -> str:
    """The normalized name of a unit"""
    try:
        return ureg.get_name(unit)
    except UndefinedUnitError:
        unit = unit.replace(" ", "_")

    try:
        return ureg.get_name(unit)
    except UndefinedUnitError:
        unit = unit.lower()

    try:
        return ureg.get_name(unit)
    except (UndefinedUnitError) as exc:
        raise ValueError("undefined units") from exc


def normalize_unit_name_with_magnitude(unit: str, magnitude) -> str:
    """The normalized name of a unit"""
    try:
        return Q_(magnitude, unit).units
    except UndefinedUnitError:
        unit = unit.replace(" ", "_")

    try:
        return Q_(magnitude, unit).units
    except UndefinedUnitError:
        unit = unit.lower()

    try:
        return Q_(magnitude, unit).units
    except (UndefinedUnitError) as exc:
        raise ValueError("undefined units") from exc


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


def validate_unit(unit: str) -> bool:
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
        print(unit, " is not a valid unit")
        return False
    return True


def validate_unit_expression(unit: Expression) -> bool:
    """Test if `unit` is a valid unit"""
    if isinstance(unit, String):
        return validate_unit(unit.value)
    if unit.has_form("Power", 2):
        base, exp = unit.elements
        if not isinstance(exp, Integer):
            return False
        return validate_unit_expression(base)
    if unit.has_form("Times", None):
        return all(validate_unit_expression(factor) for factor in unit.elements)
    return False
