# -*- coding: utf-8 -*-
"""
Units and Quantities
"""
from typing import Optional

from mathics.core.atoms import Integer, Integer1, Number, String
from mathics.core.attributes import (
    A_HOLD_REST,
    A_N_HOLD_REST,
    A_PROTECTED,
    A_READ_PROTECTED,
)
from mathics.core.builtin import Builtin, Test
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.list import ListExpression
from mathics.core.symbols import Symbol
from mathics.core.systemsymbols import (
    SymbolPower,
    SymbolQuantity,
    SymbolRow,
    SymbolTimes,
)
from mathics.eval.quantities import (
    add_quantities,
    convert_units,
    normalize_unit_expression,
    normalize_unit_expression_with_magnitude,
    validate_pint_unit,
    validate_unit_expression,
)

# This tells documentation how to sort this module
sort_order = "mathics.builtin.units-and-quantites"


class KnownUnitQ(Test):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/KnownUnitQ.html</url>

    <dl>
      <dt>'KnownUnitQ'[$unit$]
      <dd>returns True if $unit$ is a canonical unit, and False otherwise.
    </dl>

    >> KnownUnitQ["Feet"]
     = True

    >> KnownUnitQ["Foo"]
     = False

    >> KnownUnitQ["meter"^2/"second"]
     = True
    """

    summary_text = "tests whether its argument is a canonical unit."

    def test(self, expr) -> bool:
        return validate_unit_expression(expr)


class Quantity(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/Quantity.html</url>

    <dl>
      <dt>'Quantity'[$magnitude$, $unit$]
      <dd>represents a quantity with size $magnitude$ and unit specified by $unit$.

      <dt>'Quantity'[$unit$]
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
     : Unable to interpret unit specification Second.
     = False

    Quantities can be multiplied and raised to integer powers:
    >> Quantity[3, "centimeter"] / Quantity[2, "second"]^2
     = 3 / 4 centimeter / second ^ 2

    ## TODO: Allow to simplify producs:
    ## >> Quantity[3, "centimeter"] Quantity[2, "meter"]
    ##  = 600 centimeter ^ 2

    Quantities of the same kind can be added:
    >> Quantity[6, "meter"] + Quantity[3, "centimeter"]
     = 603 centimeter


    Quantities of different kind can not:
    >> Quantity[6, "meter"] + Quantity[3, "second"]
     : second and meter are incompatible units.
     = 3 second + 6 meter

    ## TODO: Implement quantities with composed units:
    ## >> UnitConvert[Quantity[2, "Ampere" * "Second"], "Coulomb"]
    ## = Quantity[2, Coulomb]
    """

    attributes = A_HOLD_REST | A_N_HOLD_REST | A_PROTECTED | A_READ_PROTECTED

    messages = {
        "unkunit": "Unable to interpret unit specification `1`.",
        "compat": "`1` and `2` are incompatible units.",
    }
    # TODO: Support fractional powers of units
    rules = {
        "Quantity[m1_, u1_]*Quantity[m2_, u2_]": "Quantity[m1*m2, u1*u2]",
        "Quantity[m_, u_]*a_": "Quantity[a*m, u]",
        "Power[Quantity[m_, u_], p_]": "Quantity[m^p, u^p]",
    }
    summary_text = "represents a quantity with units"

    def eval_plus(self, q1, u1, q2, u2, evaluation):
        """Plus[Quantity[q1_, u1_], Quantity[q2_,u2_]]"""
        result = add_quantities(q1, u1, q2, u2, evaluation)
        if result is None:
            evaluation.message("Quantity", "compat", u1, u2)
        return result

    def format_quantity(self, mag, unit, evaluation: Evaluation):
        "Quantity[mag_, unit_]"

        def format_units(units):
            if isinstance(units, String):
                q_unit = units.value
                if validate_pint_unit(q_unit):
                    result = String(q_unit.replace("_", " "))
                    return result
                return None
            if units.has_form("Power", 2):
                base, exp = units.elements
                if not isinstance(exp, Integer):
                    return None
                result = Expression(SymbolPower, format_units(base), exp)
                return result
            if units.has_form("Times", None):
                result = Expression(
                    SymbolTimes, *(format_units(factor) for factor in units.elements)
                )
                return result
            return None

        unit = format_units(unit)
        if unit is None:
            return None

        return Expression(SymbolRow, ListExpression(mag, String(" "), unit))

    def eval_list_of_magnitudes_unit(self, mag, unit, evaluation: Evaluation):
        "Quantity[mag_List, unit_]"
        head = Symbol(self.get_name())
        return ListExpression(
            *(Expression(head, m, unit).evaluate(evaluation) for m in mag.elements)
        )

    def eval_magnitude_and_unit(
        self, mag, unit, evaluation: Evaluation
    ) -> Optional[Expression]:
        "Quantity[mag_, unit_]"

        unit = unit.evaluate(evaluation)

        if isinstance(unit, Number):
            return Expression(SymbolTimes, mag, unit).evaluate(evaluation)

        if unit.has_form("Quantity", 2):
            if not validate_unit_expression(unit):
                return None
            unit = unit.elements[1]

        try:
            normalized_unit = normalize_unit_expression_with_magnitude(unit, mag)
        except ValueError:
            evaluation.message("Quantity", "unkunit", unit)
            return None

        if unit.sameQ(normalized_unit):
            return None

        return Expression(SymbolQuantity, mag, normalized_unit)

    def eval_unit(self, unit, evaluation: Evaluation):
        "Quantity[unit_]"
        unit = unit.evaluate(evaluation)
        if isinstance(unit, Number):
            return unit
        if unit.has_form("Quantity", 2):
            return unit
        try:
            unit = normalize_unit_expression(unit)
        except ValueError:
            evaluation.message("Quantity", "unkunit", unit)
            return None
        # TODO: add element property "fully_evaluated
        return Expression(SymbolQuantity, Integer1, unit)


class QuantityMagnitude(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/QuantityMagnitude.html</url>

    <dl>
      <dt>'QuantityMagnitude'[$quantity$]
      <dd>gives the amount of the specified $quantity$.

      <dt>'QuantityMagnitude'[$quantity$, $unit$]
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

    def eval_list(self, expr, evaluation: Evaluation):
        "QuantityMagnitude[expr_List]"
        return ListExpression(
            *(
                Expression(Symbol(self.get_name()), e).evaluate(evaluation)
                for e in expr.elements
            )
        )

    def eval_list_with_unit(self, expr, unit, evaluation: Evaluation):
        "QuantityMagnitude[expr_List, unit_]"
        return ListExpression(
            *(
                Expression(Symbol(self.get_name()), e, unit).evaluate(evaluation)
                for e in expr.elements
            )
        )

    def eval_quantity(self, mag, unit, evaluation: Evaluation):
        "QuantityMagnitude[Quantity[mag_, unit_]]"
        return mag if validate_unit_expression(unit) else None

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

        try:
            magnitude, unit = quantity.elements
        except ValueError:
            return None
        try:
            converted_quantity = convert_units(
                magnitude,
                unit,
                targetUnit,
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
      <dt>'QuantityQ'[$expr$]
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

        return validate_unit_expression(unit)


class QuantityUnit(Builtin):
    """
    <url>
    :WMA link:
    https://reference.wolfram.com/language/ref/QuantityUnit.html</url>

    <dl>
      <dt>'QuantityUnit'[$quantity$]
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
        return unit if validate_unit_expression(unit) else None

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

    def eval_expr_several_units(self, expr, toUnit, evaluation: Evaluation):
        "UnitConvert[expr_, toUnit_List]"
        return ListExpression(
            *(
                Expression(Symbol(self.get_name()), expr, u).evaluate(evaluation)
                for u in toUnit.elements
            )
        )

    def eval_quantity_to_unit_from_quantity(self, expr, toUnit, evaluation: Evaluation):
        "UnitConvert[expr_, toUnit_Quantity]"
        if not toUnit.has_form("Quantity", 2):
            return None
        toUnit = toUnit.elements[1]
        return Expression(Symbol(self.get_name()), expr, toUnit).evaluate(evaluation)

    def eval_quantity_to_unit(self, expr, toUnit, evaluation: Evaluation):
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

        try:
            return convert_units(
                mag,
                unit,
                toUnit,
                evaluation,
            )
        except ValueError:
            return None

    def eval_list_to_base_unit(self, expr, evaluation: Evaluation):
        "UnitConvert[expr_List]"
        head = Symbol(self.get_name())
        return ListExpression(
            *(Expression(head, item).evaluate(evaluation) for item in expr.elements)
        )

    def eval_quantity_to_base_unit(self, mag, unit, evaluation: Evaluation):
        "UnitConvert[Quantity[mag_, unit_]]"
        try:
            return convert_units(mag, unit, evaluation=evaluation)
        except ValueError:
            return None
