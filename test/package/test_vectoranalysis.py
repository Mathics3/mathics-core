# -*- coding: utf-8 -*-
"""
Unit tests from packages/VectorAnalysis
"""
from test.helper import check_evaluation

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        (None, None, None, None),
        ('Needs["VectorAnalysis`"];', None, "Null", None),
        ("DotProduct[{1,2,3}, {4,5,6}]", None, "32", None),
        ("DotProduct[{-1.4, 0.6, 0.2}, {0.1, 0.6, 1.7}]", None, "0.56", None),
        ("CrossProduct[{1,2,3}, {4,5,6}]", None, "{-3, 6, -3}", None),
        (
            "CrossProduct[{-1.4, 0.6, 0.2}, {0.1, 0.6, 1.7}]",
            None,
            "{0.9, 2.4, -0.9}",
            None,
        ),
        ("ScalarTripleProduct[{-2,3,1},{0,4,0},{-1,3,3}]", None, "-20", None),
        (
            "ScalarTripleProduct[{-1.4,0.6,0.2}, {0.1,0.6,1.7}, {0.7,-1.5,-0.2}]",
            None,
            "-2.79",
            None,
        ),
        (
            "last=CoordinatesToCartesian[{2, Pi, 3}, Spherical]",
            None,
            "{0, 0, -2}",
            None,
        ),
        ("CoordinatesFromCartesian[last, Spherical]", None, "{2, Pi, 0}", None),
        (
            "last=CoordinatesToCartesian[{2, Pi, 3}, Cylindrical]",
            None,
            "{-2, 0, 3}",
            None,
        ),
        ("CoordinatesFromCartesian[last, Cylindrical]", None, "{2, Pi, 3}", None),
        ## Needs Sin/Cos exact value (PR #100) for these tests to pass
        # ('last=CoordinatesToCartesian[{2, Pi / 4, Pi / 3}, Spherical]', None,
        #  '{Sqrt[2] / 2, Sqrt[2] Sqrt[3] / 2, Sqrt[2]}', None),
        # ('CoordinatesFromCartesian[last, Spherical]', None,
        # '{2, Pi / 4, Pi / 3}', None,),
        # ('last=CoordinatesToCartesian[{2, Pi / 4, -1}, Cylindrical]', None,
        # '{Sqrt[2], Sqrt[2], -1}', None),
        # ('last=CoordinatesFromCartesian[last, Cylindrical]', None,
        # '{2, Pi / 4, -1}', None),
        ## Continue...
        (
            "CoordinatesToCartesian[{0.27, 0.51, 0.92}, Cylindrical]",
            None,
            "{0.235641, 0.131808, 0.92}",
            None,
        ),
        (
            "CoordinatesToCartesian[{0.27, 0.51, 0.92}, Spherical]",
            None,
            "{0.0798519, 0.104867, 0.235641}",
            None,
        ),
        ("Coordinates[]", None, "{Xx, Yy, Zz}", None),
        ("Coordinates[Spherical]", None, "{Rr, Ttheta, Pphi}", None),
        ("SetCoordinates[Cylindrical]", None, "Cylindrical[Rr, Ttheta, Zz]", None),
        ("Coordinates[]", None, "{Rr, Ttheta, Zz}", None),
        ("CoordinateSystem", None, "Cylindrical", None),
        ("Parameters[]", None, "{}", None),
        (
            "CoordinateRanges[]",
            None,
            ## And[a<b, b<c] must be evaluated as a<b<c
            ## '{0 <= Rr < Infinity, -Pi < Ttheta <= Pi, -Infinity < Zz < Infinity}', None),
            "{0 <= Rr && Rr < Infinity, -Pi < Ttheta && Ttheta <= Pi, -Infinity < Zz < Infinity}",
            None,
        ),
        (
            "CoordinateRanges[Cartesian]",
            None,
            "{-Infinity < Xx < Infinity, -Infinity < Yy < Infinity, -Infinity < Zz < Infinity}",
            None,
        ),
        ("ScaleFactors[Cartesian]", None, "{1, 1, 1}", None),
        ("ScaleFactors[Spherical]", None, "{1, Rr, Rr Sin[Ttheta]}", None),
        ("ScaleFactors[Cylindrical]", None, "{1, Rr, 1}", None),
        ("ScaleFactors[{2, 1, 3}, Cylindrical]", None, "{1, 2, 1}", None),
        ("JacobianDeterminant[Cartesian]", None, "1", None),
        ("JacobianDeterminant[Spherical]", None, "Rr ^ 2 Sin[Ttheta]", None),
        ("JacobianDeterminant[Cylindrical]", None, "Rr", None),
        ("JacobianDeterminant[{2, 1, 3}, Cylindrical]", None, "2", None),
        ("JacobianMatrix[Cartesian]", None, "{{1, 0, 0}, {0, 1, 0}, {0, 0, 1}}", None),
        (
            "JacobianMatrix[Spherical]",
            None,
            "{{Cos[Pphi] Sin[Ttheta], Rr Cos[Pphi] Cos[Ttheta], -Rr Sin[Pphi] Sin[Ttheta]}, {Sin[Pphi] Sin[Ttheta], Rr Cos[Ttheta] Sin[Pphi], Rr Cos[Pphi] Sin[Ttheta]}, {Cos[Ttheta], -Rr Sin[Ttheta], 0}}",
            None,
        ),
        (
            "JacobianMatrix[Cylindrical]",
            None,
            "{{Cos[Ttheta], -Rr Sin[Ttheta], 0}, {Sin[Ttheta], Rr Cos[Ttheta], 0}, {0, 0, 1}}",
            None,
        ),
    ],
)
def test_private_doctests_vectoranalysis(str_expr, msgs, str_expected, fail_msg):
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
