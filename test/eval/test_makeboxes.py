# -*- coding: utf-8 -*-

from test.helper import evaluate

import pytest

import mathics.core.systemsymbols as SymbolOutputForm
from mathics.eval.makeboxes import int_to_string_shorter_repr


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
    result = int_to_string_shorter_repr(value, SymbolOutputForm, digits)
    assert result.value == str_repr, f"{value} -> {digits}-> {result.value}!={str_repr}"
