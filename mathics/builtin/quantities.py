# -*- coding: utf-8 -*-
"""
Units and Quantities
"""

from pint import UnitRegistry

from mathics.builtin.base import Builtin, Test
from mathics.core.atoms import Integer, Integer1, Number, Real, String
from mathics.core.attributes import (
    A_HOLD_REST,
    A_N_HOLD_REST,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolQuantity, SymbolRowBox

# This tells documentation how to sort this module
sort_order = "mathics.builtin.units-and-quantites"

ureg = UnitRegistry()
Q_ = ureg.Quantity


def get_converted_magnitude(magnitude_expr, evaluation: Evaluation) -> float:
    """
    The Python "pint" library mixes in a Python numeric value as a multiplier inside
    a Mathics Expression. here we pick out that multiplier and
    convert it from a Python numeric to a Mathics numeric.
    """
    magnitude_elements = list(magnitude_expr.elements)
    magnitude_elements[1] = from_python(magnitude_elements[1])
    magnitude_expr._elements = tuple(magnitude_elements)
    # FIXME: consider returning an int when that is possible
    return magnitude_expr.evaluate(evaluation).get_float_value()


class KnownUnitQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/KnownUnitQ.html</url>

    <dl>
      <dt>'KnownUnitQ[$unit$]'
      <dd>returns True if $unit$ is a canonical unit, and False otherwise.
    </dl>

    >> KnownUnitQ["Feet"]
     = True

    >> KnownUnitQ["Foo"]
     = False
    """

    summary_text = "tests whether its argument is a canonical unit."

    def test(self, expr):
        def validate(unit):
            try:
                Q_(1, unit)
            except Exception:
                return False
            else:
                return True

        return validate(expr.get_string_value().lower())


class Quantity(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Quantity.html</url>

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

    attributes = A_HOLD_REST | A_N_HOLD_REST | A_PROTECTED | A_READ_PROTECTED

    messages = {
        "unkunit": "Unable to interpret unit specification `1`.",
    }
    summary_text = "represents a quantity with units"

    def validate(self, unit, evaluation: Evaluation):
        if KnownUnitQ(unit).evaluate(evaluation) is Symbol("False"):
            return False
        return True

    def eval_makeboxes(self, mag, unit, f, evaluation: Evaluation):
        "MakeBoxes[Quantity[mag_, unit_String], f:StandardForm|TraditionalForm|OutputForm|InputForm]"

        q_unit = unit.value.lower()
        if self.validate(unit, evaluation):
            return Expression(
                SymbolRowBox, ListExpression(mag, String(" "), String(q_unit))
            )
        else:
            return Expression(
                SymbolRowBox,
                to_mathics_list(SymbolQuantity, "[", mag, ",", q_unit, "]"),
            )

    def eval_n(self, mag, unit, evaluation: Evaluation):
        "Quantity[mag_, unit_String]"

        if self.validate(unit, evaluation):
            if mag.has_form("List", None):
                results = []
                for i in range(len(mag.elements)):
                    quantity = Q_(mag.elements[i], unit.value.lower())
                    results.append(
                        Expression(
                            SymbolQuantity, quantity.magnitude, String(quantity.units)
                        )
                    )
                return ListExpression(*results)
            else:
                quantity = Q_(mag, unit.value.lower())
                return Expression(
                    SymbolQuantity, quantity.magnitude, String(quantity.units)
                )
        else:
            evaluation.message("Quantity", "unkunit", unit)

    def eval(self, unit, evaluation: Evaluation):
        "Quantity[unit_]"
        if not isinstance(unit, String):
            evaluation.message("Quantity", "unkunit", unit)
        else:
            return self.eval_n(Integer1, unit, evaluation)


class QuantityMagnitude(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/QuantityMagnitude.html</url>

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

    summary_text = "get magnitude associated with a quantity."

    def eval(self, expr, evaluation: Evaluation):
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

    def eval_unit(self, expr, unit, evaluation: Evaluation):
        "QuantityMagnitude[expr_, unit_]"

        def get_magnitude(elements, targetUnit, evaluation: Evaluation):
            quantity = Q_(elements[0], elements[1].get_string_value())
            converted_quantity = quantity.to(targetUnit)
            q_mag = get_converted_magnitude(converted_quantity.magnitude, evaluation)

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


class QuantityQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/QuantityQ.html</url>
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

    summary_text = "tests whether its the argument is a quantity"

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

        return expr.get_head() == SymbolQuantity and validate(expr.elements)


class QuantityUnit(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/QuantityUnit.html</url>

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

    def eval(self, expr, evaluation: Evaluation):
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


class UnitConvert(Builtin):

    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/UnitConvert.html</url>

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
    summary_text = "convert between units."

    def eval(self, expr, toUnit, evaluation: Evaluation):
        "UnitConvert[expr_, toUnit_]"

        def convert_unit(elements, target):

            mag = elements[0]
            unit = elements[1].get_string_value()
            quantity = Q_(mag, unit)
            converted_quantity = quantity.to(target)

            q_mag = get_converted_magnitude(converted_quantity.magnitude, evaluation)

            # Displaying the magnitude in Integer form if the convert rate is an Integer
            if q_mag - int(q_mag) > 0:
                return Expression(SymbolQuantity, Real(q_mag), String(target))
            else:
                return Expression(SymbolQuantity, Integer(q_mag), String(target))

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

    def eval_base_unit(self, expr, evaluation: Evaluation):
        "UnitConvert[expr_]"

        def convert_unit(elements):

            mag = elements[0]
            unit = elements[1].get_string_value()

            quantity = Q_(mag, unit)
            converted_quantity = quantity.to_base_units()

            mag = get_converted_magnitude(converted_quantity.magnitude, evaluation)

            return Expression(
                SymbolQuantity,
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
