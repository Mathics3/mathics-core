"""
Test 2d Output form
"""

from test.helper import session

import pytest


@pytest.mark.parametrize(
    ("str_expr", "str_expected", "msg"),
    [
        ("$Use2DOutputForm=True;", "Null", "Set the 2D form"),
        (
            '"Hola\nCómo estás?"',
            ("\n" "Hola       \n" "Cómo estás?"),
            "String",
        ),
        ("a^b", ("\n" " b\n" "a "), "power"),
        ("(-a)^b", ("\n" "    b\n" "(-a) "), "power of negative"),
        ("(a+b)^c", ("\n" "       c\n" "(a + b) "), "power with composite basis"),
        ("Derivative[1][f][x]", "f'[x]", "first derivative"),
        ("Derivative[2][f][x]", "f''[x]", "second derivative"),
        ("Derivative[3][f][x]", ("\n" " (3)   \n" "f   [x]"), "Third derivative"),
        (
            "Derivative[0,2][f][x]",
            ("\n" " (0,2)   \n" "f     [x]"),
            "partial derivative",
        ),
        (
            "Integrate[f[x]^2,x]",
            ("\n" "⌠    2   \n" "⎮f[x]  dx\n" "⌡        "),
            "Indefinite integral",
        ),
        ("$Use2DOutputForm=False;", "Null", "Go back to the standard behavior."),
    ],
)
def test_Output2D(str_expr: str, str_expected: str, msg: str):
    test_expr = f"OutputForm[{str_expr}]"
    result = session.evaluate_as_in_cli(test_expr).result
    if msg:
        assert result == str_expected, msg
    else:
        assert result == str_expected
