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
import pathlib
import subprocess

import numpy as np
import pytest
import yaml

from .svg_outline import outline_svg

# couple tests depend on this
try:
    import skimage
except:
    print("not running some tests because scikit-image is not installed")
    skimage = None

# Plot->Graphics->SVG->PNG tests depend on this for the SVG-PNG part
try:
    import cairosvg

    from .fonts import inject_font_style
except Exception:
    # not yet in service - see note below
    # print(f"WARNING: not running PNG tests because {oops}")
    cairosvg = None

# check if pyoidide so we can skip some there
try:
    import pyodide
except:
    pyodide = None


from test.helper import session

import mathics.builtin.drawing.plot as plot
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol
from mathics.core.util import print_expression_tree

# common plotting options for 2d plots to test with and without
opt2 = """
    AspectRatio -> 2,
    Axes -> False,
    Frame -> False,
    Mesh -> Full,
    PlotPoints -> 10
"""

# 3d plots add these options
opt3 = (
    opt2
    + """,
    BoxRatios -> {1, 2, 3}
"""
)

# non-vectorized available, vectorized not available,
classic = [
    ("barchart", "BarChart[{3,5,2,7}]", opt2, True),
    ("discreteplot", "DiscretePlot[n^2,{n,1,10}]", opt2, True),
    ("histogram", "Histogram[{1,1,1,5,5,7,8,8,8}]", opt2, True),
    ("listlineplot", "ListLinePlot[{1,4,2,5,3}]", opt2, True),
    ("listplot", "ListPlot[{1,4,2,5,3}]", opt2, True),
    ("liststepplot", "ListStepPlot[{1,4,2,5,3}]", opt2, True),
    # ("manipulate", "Manipulate[Plot[a x,{x,0,1}],{a,0,5}]", opt2, True),
    ("numberlineplot", "NumberLinePlot[{1,3,4}]", opt2, True),
    ("parametricplot", "ParametricPlot[{t,2 t},{t,0,2}]", opt2, True),
    ("piechart", "PieChart[{3,2,5}]", opt2, True),
    ("plot", "Plot[x, {x, 0, 1}]", opt2, True),
    ("polarplot", "PolarPlot[3 θ,{θ,0,2}]", opt2, True),
]

# vectorized available, non-vectorized not available
vectorized = [
    ("complexplot", "ComplexPlot[Exp[I z],{z,-2-2 I,2+2 I}]", opt2, True),
    ("complexplot3d", "ComplexPlot3D[Exp[I z],{z,-2-2 I,2+2 I}]", opt3, True),
    ("contourplot-1", "ContourPlot[x^2-y^2,{x,-2,2},{y,-2,2}]", opt2, skimage),
    ("contourplot-2", "ContourPlot[x^2+y^2==1,{x,-2,2},{y,-2,2}]", opt2, skimage),
]

# both vectorized and non-vectorized available
both = [
    ("densityplot", "DensityPlot[x y,{x,-2,2},{y,-2,2}]", opt2, True),
    ("plot3d", "Plot3D[x y,{x,-2,2},{y,-2,2}]", opt3, True),
]


# compute reference dir, which is this file minus .py plus _ref
path, _ = os.path.splitext(__file__)
ref_dir = path + "_ref"
print(f"ref_dir {ref_dir}")


# determines action to take if actual and reference files differ:
# either raise assertion error, or update reference file
UPDATE_MODE = False


def copy_file(dst_fn, src_fn):
    with open(dst_fn, "wb") as dst_f, open(src_fn, "rb") as src_f:
        dst_f.write(src_f.read())


# finish up: raise exception or update ref, and delete /tmp file if no assertion
def finish(differ, ref_fn, act_fn):
    # if ref and act differ, either update act_fn if in UPDATE_MODE, or raise assertion if not
    if differ:
        if UPDATE_MODE:
            if os.path.exists(ref_fn):
                print(
                    f"WARNING: updating existing {ref_fn}; check updated file against committed file"
                )
            else:
                print(f"NOTE: creating {ref_fn}")
            copy_file(ref_fn, act_fn)
        else:
            if os.path.exists(ref_fn):
                msg = f"reference {ref_fn} and actual {act_fn} differ"
            else:
                msg = (
                    f"reference {ref_fn} does not exist. Use --update mode to create it"
                )
            print(msg)
            raise AssertionError(msg)

    # remove /tmp file if test was successful
    if act_fn != ref_fn:
        os.remove(act_fn)


# compare ref_fn and act_fn and either raise exception or update act_fn,
# depending on UPDATE_MODE
def check_text(ref_fn, act_fn):
    if os.path.exists(ref_fn):
        try:
            result = subprocess.run(
                ["diff", "-U", "5", ref_fn, act_fn], capture_output=False
            )
            differ = result.returncode != 0
        except OSError:
            with open(ref_fn) as ref_f, open(act_fn) as act_f:
                ref_str, act_str = ref_f.read(), act_f.read()
            differ = ref_str != act_str
    else:
        differ = True
    finish(differ, ref_fn, act_fn)


# compare ref_png_fn and act_png_fn and either raise exception or update act_fn,
# depending on UPDATE_MODE
# for PNG files we have to read the file and compare the actual image data
# NOTE: this is not yet in service - see not below
def check_png(ref_png_fn, act_png_fn):
    if os.path.exists(ref_png_fn):
        act_img = skimage.io.imread(act_png_fn)[:, :, 0:3]
        ref_img = skimage.io.imread(ref_png_fn)[:, :, 0:3]
        differ = not np.all(act_img == ref_img)
        if differ:
            n = act_img.size
            sum_diff = np.sum(np.abs(act_img.astype(float) - ref_img.astype(float)))
            print(f"relative difference: {sum_diff/n:.8f}")
    else:
        differ = True
    finish(differ, ref_png_fn, act_png_fn)


def one_test(name, str_expr, vec, svg, opt, act_dir="/tmp"):
    # update name and set use_vectorized_plot depending on
    # whether vectorized test
    if vec:
        name += "-vec"
        plot.use_vectorized_plot = vec
    else:
        name += "-cls"

    # update name and splice in options depending on
    # whether default or with-options test
    if opt is None:
        name += "-def"
    elif opt is ...:
        pass
    else:
        name += "-opt"
        str_expr = f"{str_expr[:-1]}, {opt}]"

    print(f"=== running {name} {str_expr}")

    try:
        # evaluate the expression to be tested
        act_expr = session.evaluate(str_expr)
        if len(session.evaluation.out):
            print("=== messages:")
            for message in session.evaluation.out:
                print(message.text)
        assert not session.evaluation.out, "no output messages expected"

        # write the results to act_fn in act_dir
        act_fn = os.path.join(act_dir, f"{name}.txt")
        with open(act_fn, "w") as act_f:
            print_expression_tree(act_expr, file=act_f, approximate=True)

        # use diff to compare the actual result in act_fn to reference result in ref_fn,
        # with a fallback of simple string comparison if diff is not available
        ref_fn = os.path.join(ref_dir, f"{name}.txt")
        check_text(ref_fn, act_fn)

        if svg:
            act_svg_fn = os.path.join(act_dir, f"{name}.svg.txt")
            ref_svg_fn = os.path.join(ref_dir, f"{name}.svg.txt")
            boxed_expr = Expression(Symbol("System`ToBoxes"), act_expr).evaluate(
                session.evaluation
            )
            act_svg = boxed_expr.boxes_to_svg()
            act_svg = outline_svg(
                act_svg, precision=2, include_text=True, include_tail=True
            )
            with open(act_svg_fn, "w") as f:
                f.write(act_svg)
            check_text(ref_svg_fn, act_svg_fn)

        # generate png and compare if requested
        # NOTE: this experiment was only partially successful, so is not in service.
        # The inject_font_style call improves things by using a predictable font,
        # but was only partially successful. Leaving here in case we find a way to use it.
        if False:
            act_png_fn = os.path.join(act_dir, f"{name}.png")
            ref_png_fn = os.path.join(ref_dir, f"{name}.png")
            boxed_expr = Expression(Symbol("System`ToBoxes"), act_expr).evaluate(
                session.evaluation
            )
            act_svg = boxed_expr.boxes_to_svg()
            act_svg = inject_font_style(act_svg)
            cairosvg.svg2png(
                bytestring=act_svg.encode("utf-8"),
                write_to=act_png_fn,
                background_color="white",
            )
            check_png(ref_png_fn, act_png_fn)

    finally:
        plot.use_vectorized_plot = False


def yaml_tests(fn, act_dir, vec):
    """run a set of tests from yaml file fn"""

    # read the yaml file
    fn = pathlib.Path(__file__).resolve().parent / fn
    with open(fn) as r:
        tests = yaml.safe_load(r)

    # switch to appropriate mode
    plot.use_vectorized_plot = vec

    for name, info in tests.items():
        skip = info.get("skip", False)
        if isinstance(skip, str):
            skip = {
                "pyodide": pyodide,  # skip if on pyodide
                "skimage": not skimage,  # skip if no skimage
            }[skip]
        if not skip:
            svg = not vec and info.get(
                "svg", True
            )  # no png for vectorized functions yet
            # not yet in service - see note above
            # if not cairosvg or not skimage:
            #    png = False
            one_test(name, info["expr"], vec, svg, ..., act_dir)
        else:
            print(f"skipping {name}")


@pytest.mark.skipif(
    not os.environ.get("MATHICS_PLOT_DETAILED_TESTS", False),
    reason="Run just if required",
)
def test_all(act_dir="/tmp", opt=None):
    # run twice, once without and once with options
    for use_opt in [False, True]:
        # run classic tests
        for name, str_expr, opt, cond in classic + both:
            if cond:
                opt = opt if use_opt else None
                one_test(name, str_expr, False, False, opt, act_dir)

        # run vectorized tests
        for name, str_expr, opt, cond in vectorized + both:
            if cond:
                opt = opt if use_opt else None
                one_test(name, str_expr, True, False, opt, act_dir)

    # several of these tests failed on pyodide due to apparent differences
    # in numpy (and/or the blas library backing it) between pyodide and other platforms
    # including numerical instability, different data types (integer vs real)
    # the tests above seem so far to be ok on pyodide, but generally they are
    # simpler than these doc_tests
    if not pyodide:
        yaml_tests("doc_tests.yaml", act_dir, vec=False)
        yaml_tests("vec_tests.yaml", act_dir, vec=True)


# reference files can be generated by pointing saved actual
# output at reference dir instead of /tmp
# TODO: this is redundant with --update mode; consider removing this
def make_ref_files():
    test_all(ref_dir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="manage plot tests")
    parser.add_argument("--update", action="store_true", help="update reference files")
    args = parser.parse_args()
    UPDATE_MODE = args.update

    try:
        test_all()
    except AssertionError:
        print("FAIL")
