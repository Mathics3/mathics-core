"""
See https://mathics-development-guide.readthedocs.io/en/latest/extending/developing-code/testing.html#plot-output-tests
for more information, including some helpful hints on how to effectively run the tests and analyze the results.

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

# couple tests depend on this
try:
    import skimage
except ImportError:
    print("not running some tests because scikit-image is not installed")
    skimage = None  # noqa

# Plot->Graphics->SVG->PNG tests depend on this for the SVG-PNG part
try:
    import cairosvg

    from .fonts import inject_font_style
except ImportError:
    # not yet in service - see note below
    # print(f"WARNING: not running PNG tests because {oops}")
    cairosvg = None  # noqa

# check if pyoidide so we can skip some there
try:
    import pyodide
except ImportError:
    pyodide = None  # noqa


from test.helper import session

from mathics.builtin.drawing import plot
from mathics.core.expression import Expression
from mathics.core.symbols import Symbol
from mathics.core.util import print_expression_tree

from .svg_outline import outline_svg

# compute reference dir, which is this file minus .py plus _ref
# and actual dir that stores actual output, this file minus .py plus _act
PATH, _ = os.path.splitext(__file__)
REF_DIR = PATH + "_ref"
ACT_DIR = PATH + "_act"
if not os.path.exists(ACT_DIR):
    os.mkdir(ACT_DIR)
print(f"REF_DIR {REF_DIR}, ACT_DIR {ACT_DIR}")


# determines action to take if actual and reference files differ:
# either raise assertion error, or update reference file
UPDATE_MODE = False


def copy_file(dst_fn, src_fn):
    with open(dst_fn, "wb") as dst_f, open(src_fn, "rb") as src_f:
        dst_f.write(src_f.read())


def finish(differ: bool, ref_fn: str, act_fn: str):
    """
    finish up: raise exception or update ref, and delete ACT_DIR  file
    if no assertion
    """
    # if ref and act differ, either update act_fn if in UPDATE_MODE, or raise assertion if not
    if differ:
        if UPDATE_MODE:
            if os.path.exists(ref_fn):
                print(
                    (
                        f"WARNING: updating existing {ref_fn}; "
                        "check updated file against committed file"
                    )
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

    # remove ACT_DIR file if test was successful
    if act_fn != ref_fn:
        os.remove(act_fn)


def check_text(ref_fn: str, act_fn: str):
    """
    compare ref_fn and act_fn and either raise exception or update act_fn,
    depending on UPDATE_MODE
    """
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


# NOTE: this is not yet in service - see not below
def check_png(ref_png_fn: str, act_png_fn: str):
    """
    compare ref_png_fn and act_png_fn and either raise exception
    or update act_fn, depending on UPDATE_MODE
    for PNG files we have to read the file and compare the actual image data.
    """
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


def one_test(name: str, str_expr: str, vec: bool, svg: bool, opts: str):
    """
    Individual test

    Parameters
    ----------
    name : str
        Name of the test.
    str_expr : str
        expression to be tested.
    vec : bool
        if True, do a vectorized test, else do a classic test.
    svg: bool
        if True, do an svg test in addition to the vectorized or classic test,
        using the Graphics output of the vectorized or classic test
    opts :
        Options to splice in

    Returns
    -------
    None.

    """
    # update name and set use_vectorized_plot depending on
    # whether vectorized test
    if vec:
        name += "-vec"
        plot.use_vectorized_plot = vec
    else:
        name += "-cls"

    # update name and splice in options depending on
    # whether default or with-options test
    if opts is not None:
        name += "-opt"
        str_expr = f"{str_expr[:-1]}, {opts}]"

    print(f"=== running {name} {str_expr}")

    try:
        # evaluate the expression to be tested
        act_expr = session.evaluate(str_expr)
        if session.evaluation.out:
            print("=== messages:")
            for message in session.evaluation.out:
                print(message.text)
        assert not session.evaluation.out, "no output messages expected"

        # write the results to act_fn in ACT_DIR
        act_fn = os.path.join(ACT_DIR, f"{name}.txt")

        with open(act_fn, "w") as act_f:
            print_expression_tree(act_expr, file=act_f, approximate=True)

        # use diff to compare the actual result in act_fn to reference result in ref_fn,
        # with a fallback of simple string comparison if diff is not available
        ref_fn = os.path.join(REF_DIR, f"{name}.txt")
        check_text(ref_fn, act_fn)

        if svg:
            act_svg_fn = os.path.join(ACT_DIR, f"{name}.svg.txt")
            ref_svg_fn = os.path.join(REF_DIR, f"{name}.svg.txt")
            boxed_expr = Expression(Symbol("System`ToBoxes"), act_expr).evaluate(
                session.evaluation
            )
            act_svg = boxed_expr.boxes_to_format("svg")
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
            act_png_fn = os.path.join(ACT_DIR, f"{name}.png")
            ref_png_fn = os.path.join(REF_DIR, f"{name}.png")
            boxed_expr = Expression(Symbol("System`ToBoxes"), act_expr).evaluate(
                session.evaluation
            )
            act_svg = boxed_expr.boxes_to_format("svg")
            act_svg = inject_font_style(act_svg)
            cairosvg.svg2png(
                bytestring=act_svg.encode("utf-8"),
                write_to=act_png_fn,
                background_color="white",
            )
            check_png(ref_png_fn, act_png_fn)

    finally:
        plot.use_vectorized_plot = False


def yaml_tests_generator(fn: str):
    """
    Yields a sequence of dictionaries containing parameters for one_test
    driven by entries in yaml file fn
    """
    fn = pathlib.Path(__file__).resolve().parent / fn
    with open(fn) as r:
        tests = yaml.safe_load(r)

    defaults = {}
    for name, info in tests.items():
        # apply defaults if found
        if name == "__DEFAULTS__":
            defaults = info
            continue
        else:
            info = defaults | info

        # skip test if marked to skip
        skip = info.get("skip", False)
        if isinstance(skip, str):
            skip = {
                "pyodide": pyodide,  # skip if on pyodide
                "skimage": not skimage,  # skip if no skimage
            }[skip]
        if skip:
            print(f"skipping {name}")
            continue

        # default is to do both classic and vectorized tests,
        # but can be overriden either in __DEFAULTS__ or individual tests
        do_vec = info.get("vec", True)
        do_cls = info.get("cls", True)

        # some tests run with and without options
        opts = info.get("opts", None)

        # default is to run svg tests in classic mode (vectorized mode svg not yet available)
        # unless disabled by test
        do_svg = not do_vec and info.get(
            "svg", True
        )  # no png for VECTORIZED functions yet
        # not yet in service - see note above
        # if not cairosvg or not skimage:
        #    png = False

        for vec in [True, False]:
            for svg in [True, False] if do_svg else [False]:
                for opts in [None] if opts is None else [opts, None]:
                    if vec and not do_vec:
                        continue
                    if not vec and not do_cls:
                        continue
                    yield dict(
                        name=name, str_expr=info["expr"], vec=vec, svg=svg, opts=opts
                    )


YAML_TESTS = [
    "doc_tests.yaml",
    "vec_tests.yaml",
    "parameters.yaml",
]


def all_yaml_tests_generator():
    for fn in YAML_TESTS:
        yield from yaml_tests_generator(fn)


@pytest.mark.skipif(
    not os.environ.get("MATHICS_PLOT_DETAILED_TESTS", False),
    reason="Run just if required",
)
@pytest.mark.skipif(
    pyodide is not None,
    reason="Does not work in Pyodide",
)
@pytest.mark.parametrize(("parms"), all_yaml_tests_generator())
def test_yaml(parms):
    """
    Execute the yaml test
    """
    one_test(**parms)


def do_test_all():
    # several of these tests failed on pyodide due to apparent differences
    # in numpy (and/or the blas library backing it) between pyodide and other platforms
    # including numerical instability, different data types (integer vs real)
    # the tests above seem so far to be ok on pyodide, but generally they are
    # simpler than these doc_tests
    if not pyodide:
        for parms in all_yaml_tests_generator():
            one_test(**parms)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="manage plot tests")
    parser.add_argument("--update", action="store_true", help="update reference files")
    args = parser.parse_args()
    UPDATE_MODE = args.update

    try:
        do_test_all()
    except AssertionError as oops:
        print(oops)
        print("FAIL")
        raise
