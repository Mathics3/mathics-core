# -*- coding: utf-8 -*-
"""
Units and Quantities
"""
from typing import Optional

from mathics.core.atoms import Integer1, Number, String
from mathics.core.attributes import (
    A_HOLD_REST,
    A_N_HOLD_REST,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, Test
from mathics.core.convert.expression import to_mathics_list
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import SymbolQuantity, SymbolRowBox, SymbolTimes
from mathics.eval.quantities import (
    convert_units,
    normalize_unit_name_with_magnitude,
    validate_unit,
)

# This tells documentation how to sort this module
sort_order = "mathics.builtin.units-and-quantites"


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

    def test(self, expr) -> bool:
        return validate_unit(expr.get_string_value())


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

    If the first argument is an array, then the unit is distributed on each element
    >> Quantity[{10, 20}, "Meters"]
     = {10 meter, 20 meter}

    If the second argument is a number, then the expression is evaluated to
    the product of the magnitude and that number
    >> Quantity[2, 3/2]
     = 3

    Notice that units are specified as Strings. If the unit is not a Symbol or a Number,
    the expression is not interpreted as a Quantity object:

    >> QuantityQ[Quantity[2, Second]]
     = False
    """

    attributes = A_HOLD_REST | A_N_HOLD_REST | A_PROTECTED | A_READ_PROTECTED

    messages = {
        "unkunit": "Unable to interpret unit specification `1`.",
    }
    summary_text = "represents a quantity with units"

    def eval_makeboxes(self, mag, unit, f, evaluation: Evaluation):
        """MakeBoxes[Quantity[mag_, unit_String],
        f:StandardForm|TraditionalForm|OutputForm|InputForm]"""
        if not isinstance(unit, String):
            return None

        q_unit = unit.value
        if q_unit and validate_unit(q_unit):
            return Expression(
                SymbolRowBox,
                ListExpression(mag, String(" "), String(q_unit.replace("_", " "))),
            )

        return Expression(
            SymbolRowBox,
            to_mathics_list(SymbolQuantity, "[", mag, ", ", String(q_unit), "]"),
        )

    def eval_list(self, mag, unit, evaluation: Evaluation):
        "Quantity[mag_List, unit_]"
        head = Symbol(self.get_name())
        return ListExpression(
            *(Expression(head, m, unit).evaluate(evaluation) for m in mag.elements)
        )

    def eval_n(self, mag, unit, evaluation: Evaluation) -> Optional[Expression]:
        "Quantity[mag_, unit_]"
        if isinstance(unit, String):
            unit_str = unit.value
            if not validate_unit(unit_str):
                evaluation.message("Quantity", "unkunit", unit)
                return None

            normalized_units = normalize_unit_name_with_magnitude(unit_str, mag)
            # If the units are already normalized, return None
            if normalized_units == unit.value:
                return None
            return Expression(SymbolQuantity, mag, String(normalized_units))
        unit = unit.evaluate(evaluation)
        if isinstance(unit, Number):
            return Expression(SymbolTimes, mag, unit).evaluate(evaluation)
        return None

    def eval(self, unit, evaluation: Evaluation):
        "Quantity[unit_]"
        if not isinstance(unit, String):
            evaluation.message("Quantity", "unkunit", unit)
            return None
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
    """

    summary_text = "get magnitude associated with a quantity."

    def eval_list_1(self, expr, evaluation: Evaluation):
        "QuantityMagnitude[expr_List]"
        return ListExpression(
            *(
                Expression(Symbol(self.get_name()), e).evaluate(evaluation)
                for e in expr.elements
            )
        )

    def eval_list_2(self, expr, unit, evaluation: Evaluation):
        "QuantityMagnitude[expr_List, unit_]"
        return ListExpression(
            *(
                Expression(Symbol(self.get_name()), e, unit).evaluate(evaluation)
                for e in expr.elements
            )
        )

    def eval_quantity(self, mag, unit, evaluation: Evaluation):
        "QuantityMagnitude[Quantity[mag_, unit_]]"
        return mag if validate_unit(unit.get_string_value()) else None

    def eval_quantity_unit(self, quantity, targetUnit, evaluation: Evaluation):
        "QuantityMagnitude[quantity_Quantity, targetUnit_]"

        if targetUnit.has_form("System`List", None):
            return ListExpression(
                *(
                    Expression(Symbol(self.get_name()), quantity, u)
                    for u in targetUnit.elements
                )
            )
        if targetUnit.has_form("Quantity", 2):
            targetUnit = targetUnit.elements[1]
        if not isinstance(targetUnit, String):
            return None

        try:
            magnitude, unit = quantity.elements
        except ValueError:
            return None
        try:
            converted_quantity = convert_units(
                magnitude,
                unit.get_string_value(),
                targetUnit.get_string_value(),
                evaluation,
            )
            return converted_quantity.elements[0]
        except ValueError:
            return None


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
    """

    summary_text = "tests whether its the argument is a quantity"

    def test(self, expr) -> bool:
        if not expr.has_form("Quantity", 2):
            return False
        try:
            magnitude, unit = expr.elements
        except ValueError:
            return False

        if not isinstance(magnitude, Number):
            return False

        unit_str = unit.get_string_value()
        if unit_str is None or not validate_unit(unit_str):
            return False
        return True


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
    """

    summary_text = "the unit associated to a quantity"

    def eval_quantity(self, mag, unit, evaluation: Evaluation):
        "QuantityUnit[Quantity[mag_, unit_]]"
        return unit if validate_unit(unit.get_string_value()) else None

    def eval_list(self, expr, evaluation: Evaluation):
        "QuantityUnit[expr_List]"
        return ListExpression(
            *(
                Expression(Symbol(self.get_name()), e).evaluate(evaluation)
                for e in expr.elements
            )
        )


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
    """

    messages = {
        "argrx": "UnitConvert called with `1` arguments; 2 arguments are expected"
    }
    summary_text = "convert between units."

    def eval_2_list(self, expr, toUnit, evaluation: Evaluation):
        "UnitConvert[expr_, toUnit_List]"
        return ListExpression(
            *(
                Expression(Symbol(self.get_name()), expr, u).evaluate(evaluation)
                for u in toUnit.elements
            )
        )

    def eval_2_quantity(self, expr, toUnit, evaluation: Evaluation):
        "UnitConvert[expr_, toUnit_Quantity]"
        if not toUnit.has_form("Quantity", 2):
            return None
        toUnit = toUnit.elements[1]
        return Expression(Symbol(self.get_name()), expr, toUnit).evaluate(evaluation)

    def eval_2(self, expr, toUnit, evaluation: Evaluation):
        "UnitConvert[expr_, toUnit_]"
        if expr.has_form("List", None):
            return ListExpression(
                *(
                    Expression(Symbol(self.get_name()), elem, toUnit).evaluate(
                        evaluation
                    )
                    for elem in expr.elements
                )
            )
        if not expr.has_form("Quantity", 2):
            return None

        mag, unit = expr.elements
        if not isinstance(unit, String):
            return None

        try:
            return convert_units(
                mag,
                unit.get_string_value(),
                toUnit.get_string_value(),
                evaluation,
            )
        except ValueError:
            return None

    def eval_base_unit_list(self, expr, evaluation: Evaluation):
        "UnitConvert[expr_List]"
        head = Symbol(self.get_name())
        return ListExpression(
            *(Expression(head, item).evaluate(evaluation) for item in expr.elements)
        )

    def eval_base_unit(self, mag, unit, evaluation: Evaluation):
        "UnitConvert[Quantity[mag_, unit_String]]"

        if not isinstance(unit, String):
            return None
        try:
            return convert_units(mag, unit.get_string_value(), evaluation=evaluation)
        except ValueError:
            return None
