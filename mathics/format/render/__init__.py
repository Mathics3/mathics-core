"""Rendering routines.

Mathics3 Built-in rendering includes renderers to Asymptote, MathML,
SVG, threejs, and plain text.  We hope and expect other formatting to
other kinds backend renderers, like matplotlib, can be done by
following the pattern used here.

Input to the renders come from some sort of Mathics3 Box.

The higher level Forms (e.g. TeXForm, MathMLForm) typically cause
specific boxing routines to get invoked. From this and the capabilites
and desires of a front end, different rendering routines will invoked
for each kind boxes created. This, in turn, produces strings in
(AMS)LaTeX, MathML, SVG, asymptote, or plain text.

For example, to process the Mathics3 builtin BezierCurve, a
BezierCurveBox will get created.  Mathics3 has SVG and an Asymptote
renderers for BezierCurveBoxes.  Which one is used is decided on by
the front-end's needs.
"""

import glob
import importlib
import os.path as osp
import sys

__py_files__ = [
    osp.basename(f[0:-3])
    for f in glob.glob(osp.join(osp.dirname(__file__), "[a-z]*.py"))
]

for module_name in __py_files__:
    try:
        importlib.import_module(f"mathics.format.render.{module_name}")
    except Exception as e:
        print(e)
        print(f"    Not able to load {module_name}. Check your installation.")
        print(f"    mathics.format.render loads from {osp.dirname(__file__)}")
        sys.exit(-1)
