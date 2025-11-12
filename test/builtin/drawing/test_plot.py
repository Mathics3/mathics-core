# -*- coding: utf-8 -*-
"""
Unit tests from mathics.builtin.drawing.plot
"""

from test.helper import check_evaluation, session

import pytest

from mathics.core.util import print_expression_tree


def test__listplot():
    """tests for module builtin.drawing.plot._ListPlot"""
    for str_expr, msgs, str_expected, fail_msg in (
        (
            "ListPlot[5]",
            ("5 is not a list of numbers or pairs of numbers.",),
            "ListPlot[5]",
            "ListPlot with invalid list of point",
        ),
        (
            "ListLinePlot[{{}, {{1., 1.}}, {{1., 2.}}, {}}]",
            (
                "{{}, {{1., 1.}}, {{1., 2.}}, {}} is not a list of numbers or pairs of numbers.",
            ),
            "ListLinePlot[{{}, {{1., 1.}}, {{1., 2.}}, {}}]",
            "ListLinePlot with invalid list of point",
        ),
    ):
        check_evaluation(
            str_expr,
            str_expected,
            to_string_expr=True,
            to_string_expected=True,
            hold_expected=True,
            failure_message=fail_msg,
            expected_messages=msgs,
        )


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
        (
            "Graphics[{Disk[]}, Background->RGBColor[1,.1,.1]]//TeXForm//ToString",
            None,
            (
                '\n\\begin{asy}\nusepackage("amsmath");\nsize(5.8333cm, 5.8333cm);\n'
                "filldraw(box((0,0), (350,350)), rgb(1, 0.1, 0.1));\n"
                "filldraw(ellipse((175,175),175,175), rgb(0, 0, 0), nullpen);\n"
                "clip(box((0,0), (350,350)));\n\\end{asy}\n"
            ),
            "Background 2D",
        ),
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
            "StringTake[Plot3D[x + 2y, {x, -2, 2}, {y, -2, 2}] // TeXForm//ToString,80]",
            None,
            "\n\\begin{asy}\nimport three;\nimport solids;\nimport tube;\nsize(6.6667cm, 6.6667cm);",
            None,
        ),
        (
            "Graphics3D[{Sphere[]}, Background->RGBColor[1,.1,.1]]//TeXForm//ToString",
            None,
            (
                "\n\\begin{asy}\n"
                "import three;\n"
                "import solids;\n"
                "import tube;\n"
                "size(6.6667cm, 6.6667cm);\n"
                "currentprojection=perspective(2.6,-4.8,4.0);\n"
                "currentlight=light(rgb(0.5,0.5,0.5), background=rgb(1, 0.1, 0.1), specular=red, (2,0,2), (2,2,2), (0,2,2));\n"
                "// Sphere3DBox\n"
                "draw(surface(sphere((0, 0, 0), 1)), rgb(1,1,1)+opacity(1));\n"
                "draw(((-1,-1,-1)--(1,-1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-1,1,-1)--(1,1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-1,-1,1)--(1,-1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-1,1,1)--(1,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-1,-1,-1)--(-1,1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((1,-1,-1)--(1,1,-1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-1,-1,1)--(-1,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((1,-1,1)--(1,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-1,-1,-1)--(-1,-1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((1,-1,-1)--(1,-1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((-1,1,-1)--(-1,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "draw(((1,1,-1)--(1,1,1)), rgb(0.4, 0.4, 0.4)+linewidth(1));\n"
                "\\end{asy}\n"
            ),
            "Background 3D",
        ),
        (
            "Graphics3D[Point[Table[{Sin[t], Cos[t], 0}, {t, 0, 2. Pi, Pi / 15.}]]] //Chop//TeXForm//ToString",
            None,
            (
                "\n\\begin{asy}\nimport three;\n"
                "import solids;\n"
                "import tube;\n"
                "size(6.6667cm, 6.6667cm);\n"
                "currentprojection=perspective(2.6,-4.8,4.0);\n"
                "currentlight=light(rgb(0.5,0.5,0.5), specular=red, (2,0,2), (2,2,2), (0,2,2));\n"
                "// Point3DBox\npath3 g=(0,1,0)--(0.20791,0.97815,0)--(0.40674,0.91355,0)--"
                "(0.58779,0.80902,0)--(0.74314,0.66913,0)--(0.86603,0.5,0)--(0.95106,0.30902,0)--"
                "(0.99452,0.10453,0)--(0.99452,-0.10453,0)--(0.95106,-0.30902,0)--(0.86603,-0.5,0)"
                "--(0.74314,-0.66913,0)--(0.58779,-0.80902,0)--(0.40674,-0.91355,0)--"
                "(0.20791,-0.97815,0)--(0,-1,0)--(-0.20791,-0.97815,0)--"
                "(-0.40674,-0.91355,0)--(-0.58779,-0.80902,0)--(-0.74314,-0.66913,0)--"
                "(-0.86603,-0.5,0)--(-0.95106,-0.30902,0)--(-0.99452,-0.10453,0)--"
                "(-0.99452,0.10453,0)--(-0.95106,0.30902,0)--(-0.86603,0.5,0)--"
                "(-0.74314,0.66913,0)--(-0.58779,0.80902,0)--(-0.40674,0.91355,0)--"
                "(-0.20791,0.97815,0)--(0,1,0)--cycle;dot(g, rgb(0, 0, 0));\n"
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
def test_plot(str_expr, msgs, str_expected, fail_msg):
    """tests for module builtin.drawing.plot"""
    check_evaluation(
        str_expr,
        str_expected,
        to_string_expr=True,
        to_string_expected=True,
        hold_expected=True,
        failure_message=fail_msg,
        expected_messages=msgs,
    )


#
# Call plotting functions and examine the structure of the output
# In case of error trees are printed with an embedded >>> marker showing location of error
#


def print_expression_tree_with_marker(expr):
    print_expression_tree(expr, marker=lambda expr: getattr(expr, "_marker", ""))


def check_structure(result, expected):
    """Check that expected is a prefix of result at every node"""

    def error(msg):
        result._marker = "RESULT >>> "
        expected._marker = "EXPECTED >>> "
        raise AssertionError(msg)

    # do the heads match?
    if result.get_head() != expected.get_head():
        error("heads don't match")

    # does the structure match?
    if hasattr(expected, "elements"):
        if not hasattr(result, "elements"):
            error("expected elements but result has none")
        for i, e in enumerate(expected.elements):
            if len(result.elements) <= i:
                error("result has too few elements")
            check_structure(result.elements[i], e)
    else:
        if str(result) != str(expected):
            error("leaves don't match")


def eval_and_check_structure(str_expr, str_expected):
    expr = session.parse(str_expr)
    result = expr.evaluate(session.evaluation)
    expected = session.parse(str_expected)
    try:
        check_structure(result, expected)
    except AssertionError as oops:
        print(f"\nERROR: {oops} (error is marked with >>> below)")
        print("=== result:")
        print_expression_tree_with_marker(result)
        print("=== expected:")
        print_expression_tree_with_marker(expected)
        raise


def test_plot3d_default():
    eval_and_check_structure(
        """
        Plot3D[
            x+y,
            {x,0,1}, {y,0,1},
            PlotPoints->{2,2},
            MaxRecursion->0
        ]
        """,
        """
        Graphics3D[
            {
                Polygon[{{0.0,0.0,0.0}, {0.0,0.5,0.5}, {0.5,0.0,0.5}}],
                Polygon[{{}}], Polygon[{{}}], Polygon[{{}}],  Polygon[{{}}], Polygon[{{}}], Polygon[{{}}], Polygon[{{}}],
                (* mesh lines for default Mesh->Full *)
                Line[{{0.0,0.0,0.0},{0.0,0.5,0.5},{0.0,1.0,1.0}}],
                Line[{{}}], Line[{{}}], Line[{{}}], Line[{{}}], Line[{{}}]
            },
            AspectRatio -> 1,
            Axes -> True,
            AxesStyle -> {},
            Background -> Automatic,
            BoxRatios -> {1, 1, 0.4},
            ImageSize -> Automatic,
            LabelStyle -> {},
            PlotRange -> Automatic,
            PlotRangePadding -> Automatic,
            TicksStyle -> {}
        ]
        """,
    )


def test_plot3d_nondefault():
    eval_and_check_structure(
        """
        Plot3D[
            x+y,
            {x,0,1}, {y,0,1},
            PlotPoints->{2,2},
            MaxRecursion->0
            AspectRatio -> 0.5,
            Axes -> False,
            AxesStyle -> {Red,Blue},
            Background -> Green,
            BoxRatios -> {10, 10, 1},
            ImageSize -> {200,200},
            LabelStyle -> Red,
            PlotRange -> {0,1},
            PlotRangePadding -> {1,2},
            TicksStyle -> {Purple,White}
        ]
        """,
        """
        Graphics3D[
            {
                Polygon[{{0.0,0.0,0.0}, {0.0,0.5,0.5}, {0.5,0.0,0.5}}],
                Polygon[{{}}]
            },
            AspectRatio -> 1, (* TODO: is not passed through apparently - or is my misunderstanding? *)
            Axes -> False,
            AxesStyle -> {RGBColor[1,0,0],RGBColor[0,0,1]},
            Background -> RGBColor[0,1,0],
            BoxRatios -> {10, 10, 1},
            ImageSize -> {200,200},
            LabelStyle -> RGBColor[1,0,0],
            PlotRange -> {0,1},
            PlotRangePadding -> {1,2},
            TicksStyle -> {RGBColor[0.5,0,0.5],GrayLevel[1]}
        ]
        """,
    )


def test_densityplot_default():
    eval_and_check_structure(
        """
        DensityPlot[
            x+y, {x,0,1}, {y,0,1},
            PlotPoints-> {2,2},
            MaxRecursion->0
        ]
        """,
        """
        Graphics[
            {
                Polygon[
                    {
                        {{0.0,0.0},{0.0,0.5},{0.5,0.0}},
                        {{0.0,0.5},{0.5,0.0},{0.5,0.5}}
                    },
                    VertexColors -> {
                        {
                            RGBColor[0.293416, 0.0574044, 0.529412],
                            RGBColor[0.49621975000000007, 0.41002484999999994, 0.8144772499999999],
                            RGBColor[0.49621975000000007, 0.41002484999999994, 0.8144772499999999]
                        },
                        {
                            RGBColor[0.49621975000000007, 0.41002484999999994, 0.8144772499999999],
                            RGBColor[0.49621975000000007, 0.41002484999999994, 0.8144772499999999],
                            RGBColor[0.663226, 0.6872815, 0.9117649999999999]
                        }
                    }
                ]
            },
            AspectRatio -> 1,
            Axes -> False,
            AxesStyle -> {},
            Background -> Automatic,
            ImageSize -> Automatic,
            LabelStyle -> {},
            PlotRange -> Automatic,
            PlotRangePadding -> Automatic,
            TicksStyle -> {}
        ]
        """,
    )


def test_densityplot_nondefault():
    eval_and_check_structure(
        """
        DensityPlot[
            x+y, {x,0,1}, {y,0,1},
            PlotPoints-> {2,2},
            MaxRecursion->0
            AspectRatio -> 0.5,
            Axes -> True,
            AxesStyle -> {Red,Blue},
            Background -> Green,
            ImageSize -> {200,200},
            LabelStyle -> Red,
            PlotRange -> {0,1},
            PlotRangePadding -> {1,2},
            TicksStyle -> {Purple,White}
        ]
        """,
        """
        Graphics[
            {
                Polygon[
                    {
                        {{0.0,0.0},{0.0,0.5},{0.5,0.0}},
                        {{0.0,0.5},{0.5,0.0},{0.5,0.5}}
                    },
                    VertexColors -> {
                        {
                            RGBColor[0.293416, 0.0574044, 0.529412],
                            RGBColor[0.49621975000000007, 0.41002484999999994, 0.8144772499999999],
                            RGBColor[0.49621975000000007, 0.41002484999999994, 0.8144772499999999]
                        },
                        {
                            RGBColor[0.49621975000000007, 0.41002484999999994, 0.8144772499999999],
                            RGBColor[0.49621975000000007, 0.41002484999999994, 0.8144772499999999],
                            RGBColor[0.663226, 0.6872815, 0.9117649999999999]
                        }
                    }
                ]
            },
            AspectRatio -> 1, (* TODO: is not passed through apparently - or is my misunderstanding? *)
            Axes -> True,
            AxesStyle -> {RGBColor[1,0,0],RGBColor[0,0,1]},
            Background -> RGBColor[0,1,0],
            ImageSize -> {200,200},
            LabelStyle -> RGBColor[1,0,0],
            PlotRange -> {0,1},
            PlotRangePadding -> {1,2},
            TicksStyle -> {RGBColor[0.5,0,0.5],GrayLevel[1]}
        ]
        """,
    )
