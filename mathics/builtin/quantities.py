# -*- coding: utf-8 -*-
"""
Units and Quantities
"""

from pint import UnitRegistry

from mathics.core.atoms import Integer, Integer1, Number, Real, String
from mathics.core.attributes import (
    A_HOLD_REST,
    A_N_HOLD_REST,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, Test
from mathics.core.convert.expression import to_mathics_list
from mathics.core.convert.python import from_python
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol, SymbolFalse
from mathics.core.systemsymbols import SymbolQuantity, SymbolRowBox

# from pint.errors import UndefinedUnit


# This tells documentation how to sort this module
sort_order = "mathics.builtin.units-and-quantites"

ureg = UnitRegistry()
Q_ = ureg.Quantity


def get_converted_magnitude(magnitude_expr, evaluation: Evaluation) -> float:
    """
    The Python "pint" library mixes in a Python numeric value as a multiplier inside
    a Mathics Expression. Here we pick out that multiplier and
    convert it from a Python numeric to a Mathics numeric.
    """

    if isinstance(magnitude_expr, Number):
        return magnitude_expr
    # TODO: This looks very hacky. Reformulate in a clearer
    # way.
    magnitude_elements = list(magnitude_expr.elements)
    magnitude_elements[1] = from_python(magnitude_elements[1])
    magnitude_expr._elements = tuple(magnitude_elements)
    # FIXME: consider returning an int when that is possible
    return magnitude_expr.evaluate(evaluation).get_float_value()


def validate_unit(unit):
    try:
        Q_(1, unit)
    except Exception:
        return False
    else:
        return True


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
        return validate_unit(expr.get_string_value().lower())


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
    """

    attributes = A_HOLD_REST | A_N_HOLD_REST | A_PROTECTED | A_READ_PROTECTED

    messages = {
        "unkunit": "Unable to interpret unit specification `1`.",
    }
    summary_text = "represents a quantity with units"

    def eval_makeboxes(self, mag, unit, f, evaluation: Evaluation):
        "MakeBoxes[Quantity[mag_, unit_String], f:StandardForm|TraditionalForm|OutputForm|InputForm]"

        q_unit = unit.value.lower()
        if validate_unit(unit.get_string_value().lower()):
            return Expression(
                SymbolRowBox, ListExpression(mag, String(" "), String(q_unit))
            )
        else:
            return Expression(
                SymbolRowBox,
                to_mathics_list(SymbolQuantity, "[", mag, ", ", q_unit, "]"),
            )

    def eval_list(self, mag, unit, evaluation: Evaluation):
        "Quantity[mag_List, unit_]"
        head = Symbol(self.get_name())
        return ListExpression(
            *(Expression(head, m, unit).evaluate(evaluation) for m in mag.elements)
        )

    def eval_n(self, mag, unit, evaluation: Evaluation):
        "Quantity[mag_, unit_String]"

        if validate_unit(unit.get_string_value().lower()):
            quantity = Q_(mag, unit.value.lower())
            return Expression(
                SymbolQuantity, quantity.magnitude, String(quantity.units)
            )

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
    """

    summary_text = "get magnitude associated with a quantity."

    def eval_List1(self, expr, evaluation: Evaluation):
        "QuantityMagnitude[expr_List]"
        return ListExpression(
            *(
                Expression(Symbol(self.get_name()), e).evaluate(evaluation)
                for e in expr.elements
            )
        )

    def eval_List2(self, expr, unit, evaluation: Evaluation):
        "QuantityMagnitude[expr_List, unit_]"
        return ListExpression(
            *(
                Expression(Symbol(self.get_name()), e, unit).evaluate(evaluation)
                for e in expr.elements
            )
        )

    def eval_quantity(self, mag, unit, evaluation: Evaluation):
        "QuantityMagnitude[Quantity[mag_, unit_]]"
        return mag if validate_unit(unit.get_string_value().lower()) else None

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
            quantity = Q_(magnitude, unit.get_string_value().lower())
        except Exception:
            return None

        target = targetUnit.get_string_value().lower()
        converted_quantity = quantity.to(target)
        q_mag = get_converted_magnitude(converted_quantity.magnitude, evaluation)
        if q_mag - int(q_mag) > 0:
            return Real(q_mag)
        else:
            return Integer(q_mag)


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
        if not validate_unit(unit.get_string_value().lower()):
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
        return unit if validate_unit(unit.get_string_value().lower()) else None

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

    def eval_2List(self, expr, toUnit, evaluation: Evaluation):
        "UnitConvert[expr_, toUnit_List]"
        return ListExpression(
            *(
                Expression(Symbol(self.get_name()), expr, u).evaluate(evaluation)
                for u in toUnit.elements
            )
        )

    def eval_2Quantity(self, expr, toUnit, evaluation: Evaluation):
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

        try:
            mag, unit = expr.elements
        except ValueError:
            return None
        try:
            quantity = Q_(mag, unit.get_string_value().lower())
        except Exception:
            return None

        target = toUnit.get_string_value().lower()
        converted_quantity = quantity.to(target)
        q_mag = get_converted_magnitude(converted_quantity.magnitude, evaluation)

        # Displaying the magnitude in Integer form if the convert rate is an Integer
        if q_mag - int(q_mag) > 0:
            return Expression(SymbolQuantity, Real(q_mag), String(target))
        else:
            return Expression(SymbolQuantity, Integer(q_mag), String(target))

    def eval_base_unit(self, expr, evaluation: Evaluation):
        "UnitConvert[expr_]"

        def convert_unit(q, top=False):
            if q.has_form("List", None):
                return ListExpression(*(convert_unit(elem) for elem in q.elements))

            if not q.has_form("Quantity", 2):
                return None if top else Expression(Symbol(self.get_name()), q)

            mag = q.elements[0]
            unit = q.elements[1].get_string_value().lower()

            try:
                quantity = Q_(mag, unit)
            except Exception as e:
                return None if top else Expression(Symbol(self.get_name()), q)

            converted_quantity = quantity.to_base_units()
            mag = get_converted_magnitude(converted_quantity.magnitude, evaluation)

            return Expression(
                SymbolQuantity,
                converted_quantity.magnitude,
                String(converted_quantity.units),
            )

        if expr.has_form("List", None):
            return ListExpression(*(convert_unit(q, False) for q in expr.elements))

        if not expr.has_form("Quantity", 2):
            return None

        return convert_unit(expr, True)
