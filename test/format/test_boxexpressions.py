# -*- coding: utf-8 -*-

from test.helper import session

import pytest

from mathics.core.element import BoxElementMixin
from mathics.core.expression import Expression


@pytest.mark.parametrize(
    ("expr_str",),
    [
        # Notice that in the evaluation, Box Expression objects
        # removes options with the corresponding default values, and
        # options are sorted in lexicographical order.
        # In the examples, also use only expressions in their fully evaluated
        # forms. For example, do not use `Color->Red` but
        # `Color->RGBColor[1, 0, 0]`.
        (
            'StyleBox[FractionBox[StyleBox["3", Color->RGBColor[1, 0, 0], ShowStringCharacters->True], "2"], Alignment->Left]',
        ),
        ('StyleBox["Hola", Color->RGBColor[1, 0, 0], ShowStringCharacters->True]',),
        (
            'InterpretationBox[StyleBox["Hola", Color->RGBColor[1, 0, 0], ShowStringCharacters->True], AutoDelete->True, Editable->True]',
        ),
        (
            'RowBox[{"Say hi!:", StyleBox["Hola", Color->RGBColor[1, 0, 0], ShowStringCharacters->True]}]',
        ),
    ],
)
def test_boxexpressions(expr_str):
    expr = session.parse(expr_str)
    boxes = expr.evaluate(session.evaluation)
    assert isinstance(
        boxes, BoxElementMixin
    ), f"boxes of type {type(boxes)} should be a Box expression or string."

    expr_from_boxes = boxes.to_expression()
    assert isinstance(
        expr_from_boxes, Expression
    ), f"{type(boxes)}.to_expression() should be Expression."
    assert expr_from_boxes.sameQ(
        expr
    ), f"The initial and the reconstructed expressions must be the same:\n{expr}\n{expr_from_boxes}\n"
    assert boxes.sameQ(
        expr_from_boxes
    ), "Boxes should be equivalent to the reconstructed expression.\n{expr_from_boxes}\n{boxes}\n"
    # This seems to be an issue with the sameQ method of `Expression`.
    assert expr_from_boxes.sameQ(
        boxes
    ), f"Boxes should be equivalent to the reconstructed expression.\n{expr_from_boxes}\n{boxes}\n"
