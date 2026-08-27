# -*- coding: utf-8 -*-
"""
Unit tests for mathics.builtins.specialfns.elliptic
"""
from test.helper import check_wrong_number_of_arguments


def test_wrong_number_of_arguments():
    tests = [
        (
            "EllipticE[]",
            ["EllipticE called with 0 arguments; 1 or 2 arguments are expected."],
            "EllipticE error call with too few arguments; 'argt' tag",
        ),
        (
            "EllipticE[a, b, c]",
            ["EllipticE called with 3 arguments; 1 or 2 arguments are expected."],
            "EllipticE error call with too many arguments; 'argt' tag",
        ),
        (
            "EllipticF[]",
            ["EllipticF called with 0 arguments; 2 arguments are expected."],
            "EllipticF error call with wrong number of arguments; 'argrx' tag",
        ),
        (
            "EllipticF[a]",
            ["EllipticF called with 1 argument; 2 arguments are expected."],
            "EllipticF error call with one arguments; 'argr' tag",
        ),
        (
            "EllipticK[a, b, c, d]",
            ["EllipticK called with 4 arguments; 1 argument is expected."],
            "EllipticK error call with wrong number of arguments; 'argx' tag",
        ),
        (
            "EllipticPi[a]",
            ["EllipticPi called with 1 argument; 2 or 3 arguments are expected."],
            "EllipticE error call with too few arguments; 'argtu' tag",
        ),
        (
            "EllipticPi[]",
            ["EllipticPi called with 0 arguments; 2 or 3 arguments are expected."],
            "EllipticPi error call with too many arguments; 'argt' tag",
        ),
    ]
    check_wrong_number_of_arguments(tests)
