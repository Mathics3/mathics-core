from mathics.core.convert.expression import to_expression
from mathics.core.expression import Expression, ElementsProperties
from mathics.core.symbols import SymbolPlus
from mathics.core.atoms import Integer, Integer1


def test_expression_constructor():
    def attribute_check(e, varname: str):
        assert e.elements_properties.elements_fully_evaluated == True, varname
        assert e.elements_properties.is_flat == True, varname
        assert e.elements_properties.is_ordered == True, varname

    # The below will convert 1 Integer(1) multiple times
    # and discover that the arguments are flat, fully evaluated, and ordered.
    ones = [1] * 50
    e1 = to_expression(SymbolPlus, *ones)
    attribute_check(e1, "e1")

    e1a = to_expression("Plus", *ones)
    attribute_check(e1a, "e1a")

    integer_ones = [Integer1] * 50
    e2 = Expression(SymbolPlus, *integer_ones)
    e2._build_elements_properties()
    attribute_check(e2, "e2")
    assert e1 == e2
    assert e1.elements == e2.elements, "Elements should get converted the same"

    e3 = to_expression(SymbolPlus, *ones, elements_conversion_fn=Integer)
    e3._build_elements_properties()
    attribute_check(e3, "e3")
    assert e1 == e3
    assert e1.elements == e3.elements, "Elements should get converted the same"

    e4 = Expression(
        SymbolPlus,
        *integer_ones,
        elements_properties=ElementsProperties(True, True, True)
    )
    attribute_check(e4, "e4")
    assert e1 == e4
    assert e1.elements == e4.elements, "Elements should get converted the same"
