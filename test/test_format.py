from .helper import evaluate, session

from mathics.builtin.base import BoxConstruct, Predefined
from mathics.builtin.graphics import GRAPHICS_OPTIONS
from mathics.core.attributes import hold_all, protected, read_protected


import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4"', "4", None),
        ("4", "4", None),
        ('"Hola!"', "Hola!", None),
        ("a", "a", None),
        ("Pi", "Pi", None),
        ("a^4", "a ^ 4", None),
        ("Subscript[a, 4]", "Subscript[a, 4]", None),
        ("Subsuperscript[a, p, q]", "Subsuperscript[a, p, q]", None),
        ("Integrate[F[x],{x,a,g[b]}]", "Integrate[F[x], {x, a, g[b]}]", None),
    ],
)
def test_makeboxes_outputform_text(
    str_expr: str, str_expected: str, msg: str, message=""
):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`OutputForm")
    print(result, type(result))
    print(format_result, type(format_result))
    print(str_expected, type(format_result))
    # Atoms are not still correctly processed as BoxConstruct
    #    assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert format_result.boxes_to_text() == expected, msg
    else:
        assert format_result.boxes_to_text() == str_expected


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ('"4"', "\\text{4}", None),
        ("4", "4", None),
        ('"Hola!"', "\\text{Hola!}", None),
        ("Pi", "\\text{Pi}", None),
        ("a", "a", None),
        ("a^4", "a^4", None),
        ("Subscript[a, 4]", "a_4", None),
        ("Subsuperscript[a, p, q]", "a_p^q", None),
        (
            "Integrate[F[x],{x,a,g[b]}]",
            "\\int_a^{g\\left[b\\right]} F\\left[x\\right] \uf74cx",
            None,
        ),
    ],
)
def test_makeboxes_outputform_tex(
    str_expr: str, str_expected: str, msg: str, message=""
):
    result = session.evaluate(str_expr)
    format_result = result.format(session.evaluation, "System`StandardForm")
    print(result, type(result))
    print(format_result, type(format_result))
    # Atoms are not still correctly processed as BoxConstruct
    # assert isinstance(format_result,  BoxConstruct)
    if msg:
        assert format_result.boxes_to_tex() == expected, msg
    else:
        assert format_result.boxes_to_tex() == str_expected
