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
        return False
    return True
