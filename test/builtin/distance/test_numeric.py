# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.distance.numeric
"""

from test.helper import check_evaluation


def test_cosine_distance():
    for str_expr, str_expected, message, fail_msg in (
        ("CosineDistance[5, 6]", "0", "CosineDistance of a pair Integers is 0", None),
        (
            "CosineDistance[5, 6.0]",
            "0.0",
            "CosineDistance of an Integers and a Real is 0.0",
            None,
        ),
        ("CosineDistance[Complex[1, 0], Complex[0, 2]]", "1. + 1 I", None, None),
        (
            "CosineDistance[Complex[5.0, 0], Complex[10, 3]]",
            "0.0421737 + 0.287348 I",
            "CosineDistance of an two Complex numbers is defined",
            None,
        ),
        (
            "CosineDistance[{1, 2, 3}, {1, 2, 3, 4}]",
            "CosineDistance[{1, 2, 3}, {1, 2, 3, 4}]",
            "Mismatched vector sizes",
            [
                "The arguments {1, 2, 3} and {1, 2, 3, 4} do not have compatible dimensions."
            ],
        ),
    ):
        check_evaluation(str_expr, str_expected, message, expected_messages=fail_msg)
