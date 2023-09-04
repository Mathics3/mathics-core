# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.quantities

In particular, Rationalize and RealValuNumberQ
"""

from test.helper import check_evaluation

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
            '{Quantity[0.03, "meter"], Quantity[0.1, "meter"]}',
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
            '{Quantity[3, "meter"], Quantity[1.52, "meter"]}',
            None,
        ),
        (
            'UnitConvert[Quantity[{3, 1}, "meter"], "inch"]',
            None,
            '{Quantity[118.11, "inch"], Quantity[39.3701, "inch"]}',
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
