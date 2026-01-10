"test latex formatter"
from test.helper import reset_session, session

import pytest

from mathics.core.systemsymbols import SymbolStandardForm
from mathics.eval.makeboxes import format_element

reset_session()
evaluation = session.evaluation


def get_latex(wl_expression):
    wl_expression = session.evaluate(wl_expression)
    print(wl_expression)
    boxes = format_element(wl_expression, evaluation, SymbolStandardForm)
    return boxes.boxes_to_tex(
        show_string_characters=False, evaluation=evaluation
    ).strip()


@pytest.mark.parametrize(
    ("testcase", "expected"),
    [
        ('"["', r"\text{[}"),
        ('"]"', r"\text{]}"),
        ("HoldForm[A[[1,2]]]", r"A\left[\left[1, 2\right]\right]"),
        ('"wrong ]"', r"\text{wrong ]}"),
        ("Integrate[F[x],x]", r"\int F\left[x\right] \, dx"),
        ("Cap[c,b]", r"c \cap b"),
        ("CupCap[c,b]", r"c \stackrel{\smile}{\frown} b"),
        ("Congruent[c,b]", r"c \equiv b"),
        ("Pi", r"\pi"),
    ],
)
def test_expressions(testcase, expected):
    result = get_latex(testcase)
    assert result == expected
