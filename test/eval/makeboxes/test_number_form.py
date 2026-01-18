from test.helper import evaluate

import pytest
import sympy

from mathics.core.atoms import Integer, Integer0, Integer1, IntegerM1, Real
from mathics.format.makeboxes.numberform import (
    int_to_string_shorter_repr,
    int_to_tuple_info,
    real_to_tuple_info,
)

# from packaging.version import Version


@pytest.mark.parametrize(
    ("integer", "expected", "exponent", "is_nonnegative", "digits"),
    [
        (Integer0, "0", 0, True, 1),
        (Integer1, "1", 0, True, 1),
        (IntegerM1, "1", 0, False, 1),
        (Integer(999), "999", 2, True, 3),
        (Integer(1000), "1000", 3, True, 4),
        (Integer(-9999), "9999", 3, False, 4),
        (Integer(-10000), "10000", 4, False, 5),
    ],
)
def test_int_to_tuple_info(
    integer: Integer, expected: str, exponent: int, is_nonnegative: bool, digits: int
):
    assert int_to_tuple_info(integer) == (expected, exponent, is_nonnegative, digits)
    assert int_to_tuple_info(integer, 3) == (
        expected,
        exponent,
        is_nonnegative,
        min(3, digits),
    )


@pytest.mark.parametrize(
    (
        "real",
        "digits",
        "expected",
        "exponent",
        "is_nonnegative",
        "red_digits",
        "precision",
    ),
    [
        # Using older uncorrected version of Real()
        # (
        #     (Real(sympy.Float(0.0, 10)), 10, "0", -10, True)
        #     if Version(sympy.__version__) < Version("1.13.0")
        #     else (Real(sympy.Float(0.0, 10)), 10, "0000000000", -1, True)
        # ),
        (Real(sympy.Float(0.0, 10)), 10, "0", -10, True, 10, 10),
        (Real(0), 1, "0", 0, True, 1, 15),
        (Real(0), 2, "0", 0, True, 2, 15),
        (Real(0.1), 2, "1", -1, True, 2, 15),
        (Real(0.12), 2, "12", -1, True, 2, 15),
        (Real(-0.12), 2, "12", -1, False, 2, 15),
        (Real(3.141593), 10, "3141593", 0, True, 10, 15),
    ],
)
def test_real_to_tuple_info(
    real: Real,
    digits: int,
    expected: str,
    exponent: int,
    is_nonnegative: bool,
    red_digits: int,
    precision: int,
):
    assert real_to_tuple_info(real, digits) == (
        expected,
        exponent,
        is_nonnegative,
        red_digits,
        precision,
    )


@pytest.mark.parametrize(
    ("int_expr", "digits", "str_repr"),
    [
        ("1234567890", 0, "1234567890"),
        ("1234567890", 2, " <<10>> "),
        ("1234567890", 9, "1234567890"),
        ("1234567890", 10, "1234567890"),
        ("9934567890", 10, "9934567890"),
        ("1234567890", 11, "1234567890"),
        ("1234567890", 20, "1234567890"),
        ("-1234567890", 0, "-1234567890"),
        ("-1234567890", 2, "- <<10>> "),
        ("-1234567890", 9, "-1 <<9>> "),
        ("-1234567890", 10, "-1234567890"),
        ("-1234567890", 11, "-1234567890"),
        ("-9934567890", 11, "-9934567890"),
        ("12345678900987654321", 15, "1234 <<13>> 321"),
        ("-1234567890", 20, "-1234567890"),
        ("12345678900987654321", 0, "12345678900987654321"),
        ("12345678900987654321", 2, " <<20>> "),
        ("92345678900987654329", 2, " <<20>> "),
        ("12345678900987654321", 9, "1 <<19>> "),
        ("12345678900987654321", 10, "1 <<18>> 1"),
        ("12345678900987654321", 11, "12 <<17>> 1"),
        ("12345678900987654321", 20, "12345678900987654321"),
        ("-12345678900987654321", 0, "-12345678900987654321"),
        ("-12345678900987654321", 2, "- <<20>> "),
        ("-12345678900987654321", 9, "- <<20>> "),
        ("-12345678900987654321", 10, "-1 <<19>> "),
        ("-12345678900987654321", 11, "-1 <<18>> 1"),
        ("-12345678900987654321", 15, "-123 <<14>> 321"),
        ("-99345678900987654321", 15, "-993 <<14>> 321"),
        ("-12345678900987654321", 16, "-1234 <<13>> 321"),
        ("-99345678900987654321", 16, "-9934 <<13>> 321"),
        ("-12345678900987654321", 20, "-12345678900987654321"),
    ],
)
def test_string_conversion_limited_size(int_expr, digits, str_repr):
    value = evaluate(int_expr).value
    result = int_to_string_shorter_repr(value, digits)
    assert result == str_repr, f"{value} -> {digits}-> {result.value}!={str_repr}"
