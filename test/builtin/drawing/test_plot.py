# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.drawing.plot
"""

import sys
import time
from test.helper import check_evaluation, evaluate

import pytest


@pytest.mark.parametrize(
    ("str_expr", "msgs", "str_expected", "fail_msg"),
    [
        ("Plot[1 / x, {x, -1, 1}]", None, "-Graphics-", None),
        ("Plot[x, {y, 0, 2}]", None, "-Graphics-", None),
        (
            "Plot[{f[x],-49x/12+433/108},{x,-6,6}, PlotRange->{-10,10}, AspectRatio->{1}]",
            None,
            "-Graphics-",
            None,
        ),
        (
            "Plot[Sin[t],  {t, 0, 2 Pi}, PlotPoints -> 1]",
            ("Value of option PlotPoints -> 1 is not an integer >= 2.",),
            "Plot[Sin[t], {t, 0, 2 Pi}, PlotPoints -> 1]",
            None,
        ),
        ("Plot[x*y, {x, -1, 1}]", None, "-Graphics-", None),
        ("Plot3D[z, {x, 1, 20}, {y, 1, 10}]", None, "-Graphics3D-", None),
        ## MaxRecursion Option
        (
            "Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> 0]",
            None,
            "-Graphics3D-",
            None,
        ),
        (
            "Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> 15]",
            None,
            "-Graphics3D-",
            None,
        ),
        (
            "Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> 16]",
            (
                "MaxRecursion must be a non-negative integer; the recursion value is limited to 15. Using MaxRecursion -> 15.",
            ),
            "-Graphics3D-",
            None,
        ),
        (
            "Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> -1]",
            (
                "MaxRecursion must be a non-negative integer; the recursion value is limited to 15. Using MaxRecursion -> 0.",
            ),
            "-Graphics3D-",
            None,
        ),
        (
            "Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> a]",
            (
                "MaxRecursion must be a non-negative integer; the recursion value is limited to 15. Using MaxRecursion -> 0.",
            ),
            "-Graphics3D-",
            None,
        ),
        (
            "Plot3D[0, {x, -2, 2}, {y, -2, 2}, MaxRecursion -> Infinity]",
            (
                "MaxRecursion must be a non-negative integer; the recursion value is limited to 15. Using MaxRecursion -> 15.",
            ),
            "-Graphics3D-",
            None,
        ),
        (
            "Plot3D[x ^ 2 + 1 / y, {x, -1, 1}, {y, 1, z}]",
            ("Limiting value z in {y, 1, z} is not a machine-size real number.",),
            "Plot3D[x ^ 2 + 1 / y, {x, -1, 1}, {y, 1, z}]",
            None,
        ),
        (
            "StringTake[Plot3D[x + 2y, {x, -2, 2}, {y, -2, 2}] // TeXForm//ToString,67]",
            None,
            "\n\\begin{asy}\nimport three;\nimport solids;\nsize(6.6667cm, 6.6667cm);",
            None,
        ),
        (
            "Graphics3D[Point[Table[{Sin[t], Cos[t], 0}, {t, 0, 2. Pi, Pi / 15.}]]] // TeXForm//ToString",
            None,
            (
                "\n\\begin{asy}\nimport three;\nimport solids;\nsize(6.6667cm, 6.6667cm);\n"
                "currentprojection=perspective(2.6,-4.8,4.0);\n"
                "currentlight=light(rgb(0.5,0.5,1), specular=red, (2,0,2), (2,2,2), (0,2,2));\n"
                "// Point3DBox\npath3 g=(0,1,0)--(0.20791,0.97815,0)--(0.40674,0.91355,0)--"
                "(0.58779,0.80902,0)--(0.74314,0.66913,0)--(0.86603,0.5,0)--(0.95106,0.30902,0)--"
                "(0.99452,0.10453,0)--(0.99452,-0.10453,0)--(0.95106,-0.30902,0)--(0.86603,-0.5,0)"
                "--(0.74314,-0.66913,0)--(0.58779,-0.80902,0)--(0.40674,-0.91355,0)--"
                "(0.20791,-0.97815,0)--(5.6655e-16,-1,0)--(-0.20791,-0.97815,0)--"
                "(-0.40674,-0.91355,0)--(-0.58779,-0.80902,0)--(-0.74314,-0.66913,0)--"
                "(-0.86603,-0.5,0)--(-0.95106,-0.30902,0)--(-0.99452,-0.10453,0)--"
                "(-0.99452,0.10453,0)--(-0.95106,0.30902,0)--(-0.86603,0.5,0)--"
                "(-0.74314,0.66913,0)--(-0.58779,0.80902,0)--(-0.40674,0.91355,0)--"
                "(-0.20791,0.97815,0)--(1.5314e-15,1,0)--cycle;dot(g, rgb(0, 0, 0));\n"
                "draw(((-0.99452,-1,-1)--(0.99452,-1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-0.99452,1,-1)--(0.99452,1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-0.99452,-1,1)--(0.99452,-1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-0.99452,1,1)--(0.99452,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-0.99452,-1,-1)--(-0.99452,1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((0.99452,-1,-1)--(0.99452,1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-0.99452,-1,1)--(-0.99452,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((0.99452,-1,1)--(0.99452,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-0.99452,-1,-1)--(-0.99452,-1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((0.99452,-1,-1)--(0.99452,-1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-0.99452,1,-1)--(-0.99452,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((0.99452,1,-1)--(0.99452,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n\\end{asy}\n"
            ),
            None,
        ),
    ],
)
def test_private_doctests_plot(str_expr, msgs, str_expected, fail_msg):
    """builtin.drawing.plot"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )
