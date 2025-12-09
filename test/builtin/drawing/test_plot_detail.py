"""
These tests evaluate Plot* functions, write the result expression to a file in
outline tree form, and then compare the actual result with an expected reference
result using diff. For example, if the code that emits a PlotRange based on
the actual range of data plotted is disabled, the diff looks like this,
making it fairly clear what is wrong:

@@ -109,13 +109,7 @@
     System`None
   System`Rule
     System`PlotRange
-    System`List
-      System`List
-        System`Real 0.0
-        System`Real 1.0
-      System`List
-        System`Real 0.0
-        System`Real 1.0
+    System`Automatic
   System`Rule
     System`PlotRangeClipping
     System`False

The NumericArrays are emitted using NumPy's default str, which is an
abbreviated display of the array, which has enough data that it should
generally catch any gross error. For example if the function being
plotted is changed the diff shows that the the of the array is correct,
but the xyz coordinates output points are changed:

@@ -7,12 +7,12 @@
     System`GraphicsComplex
       System`NumericArray NumericArray[Real64, 40000×3]
         [[0.         0.         0.        ]
-         [0.00502513 0.         0.        ]
-         [0.01005025 0.         0.        ]
+         [0.00502513 0.         0.00502513]
+         [0.01005025 0.         0.01005025]
          ...
-         [0.98994975 1.         0.98994975]
-         [0.99497487 1.         0.99497487]
-         [1.         1.         1.        ]]
+         [0.98994975 1.         1.98994975]
+         [0.99497487 1.         1.99497487]
+         [1.         1.         2.        ]]
       System`Polygon
         System`NumericArray NumericArray[Integer64, 39601×4]
           [[    1     2   202   201]

The reference results are not huge but they are too unwieldy
to include in code, so they are stored as files in their own
*_ref directory.
"""

import os
import subprocess
from test.helper import session

import mathics.builtin.drawing.plot as plot
from mathics.core.util import print_expression_tree

# non-vectorized available, vectorized not available,
classic = [
    ("barchart", "BarChart[{3,5,2,7}]"),
    ("discreteplot", "DiscretePlot[n^2,{n,1,10}]"),
    ("histogram", "Histogram[{1,1,1,5,5,7,8,8,8}]"),
    ("listlineplot", "ListLinePlot[{1,4,2,5,3}]"),
    ("listplot", "ListPlot[{1,4,2,5,3}]"),
    ("liststepplot", "ListStepPlot[{1,4,2,5,3}]"),
    # ("manipulate", "Manipulate[Plot[a x,{x,0,1}],{a,0,5}]"),
    ("numberlineplot", "NumberLinePlot[{1,3,4}]"),
    ("parametricplot", "ParametricPlot[{t,2 t},{t,0,2}]"),
    ("piechart", "PieChart[{3,2,5}]"),
    ("plot", "Plot[x, {x, 0, 1}]"),
    ("polarplot", "PolarPlot[3 θ,{θ,0,2}]"),
]

# vectorized available, non-vectorized not available
vectorized = [
    ("complexplot", "ComplexPlot[Exp[I z],{z,-2-2 I,2+2 I}]"),
    ("complexplot3d", "ComplexPlot3D[Exp[I z],{z,-2-2 I,2+2 I}]"),
    ("contourplot-1", "ContourPlot[x^2-y^2,{x,-2,2},{y,-2,2}]"),
    ("contourplot-2", "ContourPlot[x^2+y^2==1,{x,-2,2},{y,-2,2}]"),
]

# both vectorized and non-vectorized available
both = [
    ("densityplot", "DensityPlot[x y,{x,-2,2},{y,-2,2}]"),
    ("plot3d", "Plot3D[x y,{x,-2,2},{y,-2,2}]"),
]

# common plotting options to test with and without
opts = """
    AspectRatio -> 2,
    Axes -> False,
    BoxRatios -> {1, 2, 3},
    Frame -> False,
    Mesh -> Full,
    PlotPoints -> 10
"""

# compute reference dir, which is this file minus .py plus _ref
path, _ = os.path.splitext(__file__)
ref_dir = path + "_ref"
print(f"ref_dir {ref_dir}")


def one_test(name, str_expr, vec, opt, act_dir="/tmp"):
    # update name and set use_vectorized_plot depending on
    # whether vectorized test
    if vec:
        name += "-vec"
        plot.use_vectorized_plot = vec
    else:
        name += "-cls"

    # update name and splice in options depending on
    # whether default or with-options test
    if opt:
        name += "-opt"
        str_expr = f"{str_expr[:-1]}, {opts}]"
    else:
        name += "-def"

    print(f"=== running {name} {str_expr}")

    try:
        # evaluate the expression to be tested
        expr = session.parse(str_expr)
        act_expr = expr.evaluate(session.evaluation)

        # write the results to act_fn in act_dir
        act_fn = os.path.join(act_dir, f"{name}.txt")
        with open(act_fn, "w") as act_f:
            print_expression_tree(act_expr, file=act_f)

        # use diff to compare the actual result in act_fn to reference result in ref_fn,
        # with a fallback of simple string comparison if diff is not available
        ref_fn = os.path.join(ref_dir, f"{name}.txt")
        try:
            result = subprocess.run(
                ["diff", "-U", "5", ref_fn, act_fn], capture_output=False
            )
            assert result.returncode == 0, "reference and actual result differ"
        except OSError:
            with open(ref_fn) as ref_f, open(act_fn) as act_f:
                ref_str, act_str = ref_f.read(), act_f.read()
            assert ref_str == act_str, "reference and actual result differ"

        # remove /tmp file if test was successful
        if act_fn != ref_fn:
            os.remove(act_fn)

    finally:
        plot.use_vectorized_plot = False


def test_all(act_dir="/tmp", opt=None):
    # run twice, once without and once with options
    for opt in [False, True]:
        # run classic tests
        for name, str_expr in classic + both:
            one_test(name, str_expr, False, opt, act_dir)

        # run vectorized tests
        for name, str_expr in vectorized + both:
            one_test(name, str_expr, True, opt, act_dir)


if __name__ == "__main__":
    # reference files can be generated by pointing saved actual
    # output at reference dir instead of /tmp
    def make_ref_files():
        test_all(ref_dir)

    def run_tests():
        try:
            test_all()
        except AssertionError:
            print("FAIL")

    make_ref_files()
    #run_tests()
