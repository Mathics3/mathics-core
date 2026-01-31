# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.quantities

In particular, Rationalize and RealValuNumberQ
"""

from test.helper import check_evaluation, check_wrong_number_of_arguments

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("Quantity[10, Meters]", None, "Quantity[10, Meters]", None),
        (
            "Quantity[Meters]",
            ("Unable to interpret unit specification Meters.",),
            "Quantity[Meters]",
            None,
        ),
        ('Quantity[1, "foot"]', None, 'Quantity[1, "foot"]', None),
        (
            'Quantity[1, "aaa"]',
            ("Unable to interpret unit specification aaa.",),
            'Quantity[1, "aaa"]',
            None,
        ),
        ('QuantityMagnitude[Quantity[1, "meter"], "centimeter"]', None, "100", None),
        (
            'QuantityMagnitude[Quantity[{3, 1}, "meter"], "centimeter"]',
            None,
            "{300, 100}",
            None,
        ),
        (
            'QuantityMagnitude[Quantity[{300,100}, "centimeter"], "meter"]',
            None,
            "{3, 1}",
            None,
        ),
        (
            'QuantityMagnitude[Quantity[{3, 1}, "meter"], "inch"]',
            None,
            "{118.11, 39.3701}",
            None,
        ),
        (
            'QuantityMagnitude[Quantity[{3, 1}, "meter"], Quantity[3, "centimeter"]]',
            None,
            "{300, 100}",
            None,
        ),
        (
            'QuantityMagnitude[Quantity[3, "mater"]]',
            ("Unable to interpret unit specification mater.",),
            'QuantityMagnitude[Quantity[3, "mater"]]',
            None,
        ),
        ("QuantityQ[3]", None, "False", None),
        (
            'QuantityUnit[Quantity[10, "aaa"]]',
            ("Unable to interpret unit specification aaa.",),
            'QuantityUnit[Quantity[10, "aaa"]]',
            None,
        ),
        (
            'UnitConvert[Quantity[{3, 10}, "centimeter"]]',
            None,
            '{Quantity[3/100, "meter"], Quantity[1/10, "meter"]}',
            None,
        ),
        (
            'UnitConvert[Quantity[3, "aaa"]]',
            ("Unable to interpret unit specification aaa.",),
            'UnitConvert[Quantity[3, "aaa"]]',
            None,
        ),
        (
            'UnitConvert[Quantity[{300, 152}, "centimeter"], Quantity[10, "meter"]]',
            None,
            '{Quantity[3, "meter"], Quantity[38/25, "meter"]}',
            None,
        ),
        (
            'UnitConvert[Quantity[{300, 152}, "km"], Quantity[10, "cm"]]',
            None,
            '{Quantity[30000000, "centimeter"], Quantity[15200000, "centimeter"]}',
            None,
        ),
        (
            'UnitConvert[Quantity[{3, 1}, "meter"], "inch"]',
            None,
            '{Quantity[118.11, "inch"], Quantity[39.3701, "inch"]}',
            None,
        ),
        (
            'UnitConvert[Quantity[20, "celsius"]]',
            None,
            '"293.15 kelvin"',
            None,
        ),
        (
            'UnitConvert[Quantity[300, "fahrenheit"]]',
            None,
            '"422.039 kelvin"',
            None,
        ),
        (
            'UnitConvert[Quantity[451, "fahrenheit"], "celsius"]',
            None,
            '"232.778 degree Celsius"',
            None,
        ),
        (
            'UnitConvert[Quantity[20, "celsius"], "kelvin"]',
            None,
            '"293.15 kelvin"',
            None,
        ),
        (
            'UnitConvert[Quantity[273, "kelvin"], "celsius"]',
            None,
            '"-0.15 degree Celsius"',
            None,
        ),
    ],
)
def test_private_doctests_numeric(str_expr, msgs, str_expected, fail_msg):
    """ """
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=False,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


@pytest.mark.parametrize(
    ("str_expr", "str_expected"),
    [
        ('a=.; 3*Quantity[a, "meter"^2]', "3 a meter ^ 2"),
        ('a Quantity[1/a, "Meter"^2]', "1 meter ^ 2"),
        ('Quantity[3, "Meter"^2]', "3 meter ^ 2"),
        (
            'Quantity[2, "Meter"]^2',
            "4 meter ^ 2",
        ),
        ('Quantity[5, "Meter"]^2-Quantity[3, "Meter"]^2', "16 meter ^ 2"),
        (
            'Quantity[2, "kg"] * Quantity[9.8, "Meter/Second^2"]',
            "19.6 kilogram meter / second ^ 2",
        ),
        (
            'UnitConvert[Quantity[2, "Ampere*Second"], "microcoulomb"]',
            "2000000 microcoulomb",
        ),
        (
            'UnitConvert[Quantity[2., "Ampere*microSecond"], "microcoulomb"]',
            "2. microcoulomb",
        ),
        # TODO Non integer powers:
        #        ('Quantity[4., "watt"]^(1/2)','2 square root watts'),
        #        ('Quantity[4., "watt"]^(1/3)','2^(2/3) cube root watts'),
        #        ('Quantity[4., "watt"]^(.24)','1.39474 watts to the 0.24'),
    ],
)
def test_quantity_operations(str_expr, str_expected):
    """test operations involving quantities"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
    )


def test_wrong_number_of_arguments():
    tests = [
        (
            "QuantityQ[a, b]",
            ["QuantityQ called with 2 arguments; 1 argument is expected."],
            "QuantityQ with wrong number of arguments",
        ),
        (
            "Quantity[]",
            ["Quantity called with 0 arguments; 1 argument is expected."],
            "Quantity called with wrong number of arguments",
        ),
    ]
    check_wrong_number_of_arguments(tests)
