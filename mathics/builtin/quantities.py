# -*- coding: utf-8 -*-


from mathics.builtin.base import Builtin, Test
from mathics.core.atoms import (
    String,
    Integer,
    Integer1,
    Real,
    Number,
)
from mathics.core.convert.expression import to_mathics_list
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolRowBox

from mathics.core.attributes import hold_rest, n_hold_rest, protected, read_protected

from pint import UnitRegistry

SymbolQuantity = Symbol("Quantity")

ureg = UnitRegistry()
Q_ = ureg.Quantity


class KnownUnitQ(Test):

    """
    <dl>
    <dt>'KnownUnitQ[$unit$]'
        <dd>returns True if $unit$ is a canonical unit, and False otherwise.
    </dl>

    >> KnownUnitQ["Feet"]
     = True

    >> KnownUnitQ["Foo"]
     = False
    """

    summary_text = "check if its argument is a canonical unit."

    def test(self, expr):
        def validate(unit):
            try:
                Q_(1, unit)
            except Exception:
                return False
            else:
                return True

        return validate(expr.get_string_value().lower())


class UnitConvert(Builtin):

    """
    <dl>
    <dt>'UnitConvert[$quantity$, $targetunit$] '
        <dd> converts the specified $quantity$ to the specified $targetunit$.
    <dt>'UnitConvert[quantity]'
        <dd> converts the specified $quantity$ to its "SIBase" units.
    </dl>

    Convert from miles to kilometers:
    >> UnitConvert[Quantity[5.2, "miles"], "kilometers"]
     = 8.36859 kilometer

    Convert a Quantity object to the appropriate SI base units:
    >> UnitConvert[Quantity[3.8, "Pounds"]]
     = 1.72365 kilogram

    #> UnitConvert[Quantity[{3, 10}, "centimeter"]]
     = {0.03 meter, 0.1 meter}

    #> UnitConvert[Quantity[3, "aaa"]]
     : Unable to interpret unit specification aaa.
     = UnitConvert[Quantity[3,aaa]]

    #> UnitConvert[Quantity[{300, 152}, "centimeter"], Quantity[10, "meter"]]
     = {3 meter, 1.52 meter}

    #> UnitConvert[Quantity[{3, 1}, "meter"], "inch"]
     = {118.11 inch, 39.3701 inch}
    """

    messages = {
        "argrx": "UnitConvert called with `1` arguments; 2 arguments are expected"
    }
    summary_text = "Conversion between units."

    def apply(self, expr, toUnit, evaluation):
        "UnitConvert[expr_, toUnit_]"

        def convert_unit(leaves, target):

            mag = leaves[0]
            unit = leaves[1].get_string_value()
            quantity = Q_(mag, unit)
            converted_quantity = quantity.to(target)

            q_mag = converted_quantity.magnitude.evaluate(evaluation).get_float_value()

            # Displaying the magnitude in Integer form if the convert rate is an Integer
            if q_mag - int(q_mag) > 0:
                return Expression(SymbolQuantity, Real(q_mag), target)
            else:
                return Expression(SymbolQuantity, Integer(q_mag), target)

        if len(evaluation.out) > 0:
            return

        if toUnit.has_form("Quantity", None):
            targetUnit = toUnit.elements[1].get_string_value().lower()
        elif toUnit.has_form("List", None):
            if not toUnit.elements[0].has_form("Quantity", None):
                return
            else:
                targetUnit = toUnit.elements[0].elements[1].get_string_value().lower()
        elif isinstance(toUnit, String):
            targetUnit = toUnit.get_string_value().lower()
        else:
            return
        if expr.has_form("List", None):
            abc = []
            for i in range(len(expr.elements)):
                abc.append(convert_unit(expr.elements[i].elements, targetUnit))
            return ListExpression(*abc)
        else:
            return convert_unit(expr.elements, targetUnit)

    def apply_base_unit(self, expr, evaluation):
        "UnitConvert[expr_]"

        def convert_unit(elements):

            mag = elements[0]
            unit = elements[1].get_string_value()

            quantity = Q_(mag, unit)
            converted_quantity = quantity.to_base_units()

            return Expression(
                "Quantity",
                converted_quantity.magnitude,
                String(converted_quantity.units),
            )

        if len(evaluation.out) > 0:
            return
        if expr.has_form("List", None):
            abc = []
            for i in range(len(expr.elements)):
                abc.append(convert_unit(expr.elements[i].elements))
            return ListExpression(*abc)
        else:
            return convert_unit(expr.elements)


class Quantity(Builtin):
    """
    <dl>
    <dt>'Quantity[$magnitude$, $unit$]'
        <dd>represents a quantity with size $magnitude$ and unit specified by $unit$.
    <dt>'Quantity[$unit$]'
        <dd>assumes the magnitude of the specified $unit$ to be 1.
    </dl>

    >> Quantity["Kilogram"]
     = 1 kilogram

    >> Quantity[10, "Meters"]
     = 10 meter

    >> Quantity[{10,20}, "Meters"]
     = {10 meter, 20 meter}

    #> Quantity[10, Meters]
     = Quantity[10, Meters]

    #> Quantity[Meters]
     : Unable to interpret unit specification Meters.
     = Quantity[Meters]

    #> Quantity[1, "foot"]
     = 1 foot
    """

    attributes = hold_rest | n_hold_rest | protected | read_protected

    messages = {
        "unkunit": "Unable to interpret unit specification `1`.",
    }
    summary_text = "quantity with units"

    def validate(self, unit, evaluation):
        if KnownUnitQ(unit).evaluate(evaluation) is Symbol("False"):
            return False
        return True

    def apply_makeboxes(self, mag, unit, f, evaluation):
        "MakeBoxes[Quantity[mag_, unit_String], f:StandardForm|TraditionalForm|OutputForm|InputForm]"

        q_unit = unit.get_string_value().lower()
        if self.validate(unit, evaluation):
            return Expression(SymbolRowBox, ListExpression(mag, " ", q_unit))
        else:
            return Expression(
                SymbolRowBox,
                to_mathics_list(SymbolQuantity, "[", mag, ",", q_unit, "]"),
            )

    def apply_n(self, mag, unit, evaluation):
        "Quantity[mag_, unit_String]"

        if self.validate(unit, evaluation):
            if mag.has_form("List", None):
                results = []
                for i in range(len(mag.elements)):
                    quantity = Q_(mag.elements[i], unit.get_string_value().lower())
                    results.append(
                        Expression(
                            SymbolQuantity, quantity.magnitude, String(quantity.units)
                        )
                    )
                return ListExpression(*results)
            else:
                quantity = Q_(mag, unit.get_string_value().lower())
                return Expression(
                    "Quantity", quantity.magnitude, String(quantity.units)
                )
        else:
            return evaluation.message("Quantity", "unkunit", unit)

    def apply_1(self, unit, evaluation):
        "Quantity[unit_]"
        if not isinstance(unit, String):
            return evaluation.message("Quantity", "unkunit", unit)
        else:
            return self.apply_n(Integer1, unit, evaluation)


class QuantityQ(Test):
    """
    <dl>
    <dt>'QuantityQ[$expr$]'
        <dd>return True if $expr$ is a valid Association object, and False otherwise.
    </dl>

    >> QuantityQ[Quantity[3, "Meters"]]
     = True

    >> QuantityQ[Quantity[3, "Maters"]]
     : Unable to interpret unit specification Maters.
     = False

    #> QuantityQ[3]
     = False
    """

    summary_text = "checks if the argument is a quantity"

    def test(self, expr):
        def validate_unit(unit):
            try:
                Q_(1, unit)
            except Exception:
                return False
            else:
                return True

        def validate(elements):
            if len(elements) < 1 or len(elements) > 2:
                return False
            elif len(elements) == 1:
                if validate_unit(elements[0].get_string_value().lower()):
                    return True
                else:
                    return False
            else:
                if isinstance(elements[0], Number):
                    if validate_unit(elements[1].get_string_value().lower()):
                        return True
                    else:
                        return False
                else:
                    return False

        return expr.get_head_name() == "System`Quantity" and validate(expr.elements)


class QuantityUnit(Builtin):
    """
    <dl>
    <dt>'QuantityUnit[$quantity$]'
        <dd>returns the unit associated with the specified $quantity$.
    </dl>

    >> QuantityUnit[Quantity["Kilogram"]]
     = kilogram

    >> QuantityUnit[Quantity[10, "Meters"]]
     = meter

    >> QuantityUnit[Quantity[{10,20}, "Meters"]]
     = {meter, meter}

    #> QuantityUnit[Quantity[10, "aaa"]]
     : Unable to interpret unit specification aaa.
     = QuantityUnit[Quantity[10,aaa]]
    """

    summary_text = "the unit associated to a quantity"

    def apply(self, expr, evaluation):
        "QuantityUnit[expr_]"

        def get_unit(elements):
            if len(elements) == 1:
                return elements[0]
            else:
                return elements[1]

        if len(evaluation.out) > 0:
            return
        if expr.has_form("List", None):
            results = []
            for i in range(len(expr.elements)):
                results.append(get_unit(expr.elements[i].elements))
            return ListExpression(*results)
        else:
            return get_unit(expr.elements)


class QuantityMagnitude(Builtin):
    """
    <dl>
    <dt>'QuantityMagnitude[$quantity$]'
        <dd>gives the amount of the specified $quantity$.
    <dt>'QuantityMagnitude[$quantity$, $unit$]'
        <dd>gives the value corresponding to $quantity$ when converted to $unit$.
    </dl>

    >> QuantityMagnitude[Quantity["Kilogram"]]
     = 1

    >> QuantityMagnitude[Quantity[10, "Meters"]]
     = 10

    >> QuantityMagnitude[Quantity[{10,20}, "Meters"]]
     = {10, 20}

    #> QuantityMagnitude[Quantity[1, "meter"], "centimeter"]
     = 100

    #> QuantityMagnitude[Quantity[{3,1}, "meter"], "centimeter"]
     = {300, 100}

    #> QuantityMagnitude[Quantity[{300,100}, "centimeter"], "meter"]
     = {3, 1}

    #> QuantityMagnitude[Quantity[{3, 1}, "meter"], "inch"]
     = {118.11, 39.3701}

    #> QuantityMagnitude[Quantity[{3, 1}, "meter"], Quantity[3, "centimeter"]]
     = {300, 100}

    #> QuantityMagnitude[Quantity[3,"mater"]]
     : Unable to interpret unit specification mater.
     = QuantityMagnitude[Quantity[3,mater]]
    """

    summary_text = "The magnitude associated to a quantity."

    def apply(self, expr, evaluation):
        "QuantityMagnitude[expr_]"

        def get_magnitude(elements):
            if len(elements) == 1:
                return 1
            else:
                return elements[0]

        if len(evaluation.out) > 0:
            return
        if expr.has_form("List", None):
            results = []
            for i in range(len(expr.elements)):
                results.append(get_magnitude(expr.elements[i].elements))
            return ListExpression(*results)
        else:
            return get_magnitude(expr.elements)

    def apply_unit(self, expr, unit, evaluation):
        "QuantityMagnitude[expr_, unit_]"

        def get_magnitude(elements, targetUnit, evaluation):
            quanity = Q_(elements[0], elements[1].get_string_value())
            converted_quantity = quanity.to(targetUnit)
            q_mag = converted_quantity.magnitude.evaluate(evaluation).get_float_value()

            # Displaying the magnitude in Integer form if the convert rate is an Integer
            if q_mag - int(q_mag) > 0:
                return Real(q_mag)
            else:
                return Integer(q_mag)

        if len(evaluation.out) > 0:
            return

        # Getting the target unit
        if unit.has_form("Quantity", None):
            targetUnit = unit.elements[1].get_string_value().lower()
        elif unit.has_form("List", None):
            if not unit.elements[0].has_form("Quantity", None):
                return
            else:
                targetUnit = unit.elements[0].elements[1].get_string_value().lower()
        elif isinstance(unit, String):
            targetUnit = unit.get_string_value().lower()
        else:
            return

        # convert the quantity to the target unit and return the magnitude
        if expr.has_form("List", None):
            results = []
            for i in range(len(expr.elements)):
                results.append(
                    get_magnitude(expr.elements[i].elements, targetUnit, evaluation)
                )
            return ListExpression(*results)
        else:
            return get_magnitude(expr.elements, targetUnit, evaluation)
