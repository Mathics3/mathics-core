# -*- coding: utf-8 -*-

from mathics.core.expression import Expression
from mathics.core.symbols import Symbol


def test_flatten_with_respect_to_head():
    """
    Tests expr.flatten_with_respect_to_head(head_element)
    """

    Plus = Symbol("Plus")
    plus_expr = Expression(Plus, 1, Expression(Plus, 2, Expression(Plus, 3, 4)), 5)
    assert (
        len(plus_expr.elements) == 3
    ), "Unflattened Plus elements should be 1, Plus(...), 5"

    flattened_plus_expr = plus_expr.flatten_with_respect_to_head(Plus)
    assert (
        len(flattened_plus_expr.elements) == 5
    ), "Flattened Plus elements should be 1, 2, 3, 4, 5"

    # Now test setting the level parameter
    flattened_plus_expr = plus_expr.flatten_with_respect_to_head(Plus, level=1)
    assert (
        len(flattened_plus_expr.elements) == 4
    ), "Flattened Plus elements with level should be 1, 2, Plus(...), 5"

    flattened_plus_expr = plus_expr.flatten_with_respect_to_head(Plus, level=0)
    assert flattened_plus_expr == plus_expr, "No flattening with level=0"

    for level in (-1, 10, 100):
        flattened_plus_expr = plus_expr.flatten_with_respect_to_head(Plus, level=level)
        assert (
            len(flattened_plus_expr.elements) == 5
        ), f"Flattened Plus elements limit {level} should be 1, 2, 3, 4, 5"

    f = Symbol("f")
    a = Symbol("a")
    b = Symbol("b")
    expr = Expression(f, a, Expression(f, b, Expression(f, a, b)))
    assert len(expr.elements) == 2
    flattened_expr = expr.flatten_with_respect_to_head(f)
    assert len(flattened_expr.elements) == 4, "should have flattened to: a, b, a, b"

    flattened_expr = expr.flatten_with_respect_to_head(a)
    assert (
        flattened_expr == expr
    ), "Non-matching head - nothing should have been flattened"


if __name__ == "__main__":
    test_flatten_with_respect_to_head()
