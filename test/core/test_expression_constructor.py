from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolPlus
from mathics.core.atoms import Integer, Integer1


def test_expression_constructor():
    def attribute_check(e, varname: str):
        assert e._elements_fully_evaluated == True, varname
        assert e._is_flat == True, varname
        assert e._is_ordered == True, varname

    # The below will convert 1 Integer(1) multiple times
    # and discover that the arguments are flat, fully evaluated, and ordered.
    ones = [1] * 50
    e1 = Expression(SymbolPlus, *ones)
    attribute_check(e1, "e1")
    integer_ones = [Integer1] * 50
    e2 = Expression(SymbolPlus, *integer_ones)
    attribute_check(e2, "e2")
    assert e1 == e2
    assert e1.elements == e2.elements, "Elements should get converted the same"

    e3 = Expression(SymbolPlus, *ones, element_conversion_fn=Integer)
    attribute_check(e3, "e3")
    assert e1 == e3
    assert e1.elements == e3.elements, "Elements should get converted the same"

    e4 = Expression(
        SymbolPlus,
        *integer_ones,
        element_properties={
            "_elements_fully_evaluated": True,
            "_is_flat": True,
            "_is_ordered": True,
        },
    )
    attribute_check(e4, "e4")
    assert e1 == e4
    assert e1.elements == e4.elements, "Elements should get converted the same"
