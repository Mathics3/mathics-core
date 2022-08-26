"""
Lower-level formatting routines.

Built-in Lower-level formatting includes Asymptote, MathML, SVG,
threejs, and plain text.  We hope and expect other formatting to other
kinds backend renderers like matplotlib, can be done by following the
pattern used here.

These routines typically get called in formatting Mathics Box objects.

Although there higher level *Forms* (e.g. TeXForm, MathMLForm)
typically cause very specific formatters to get called, (e.g. latex, mathml),
the two concepts and levels are a little bit different.

For example, in graphics there may be several different kinds of
renderers, SVG, PNG for a particular kind of graphics Box, the
front-end deciding which render to use for a that kind of Box.
The Box however is created via a particular high-level Form.

As another example, front-end may decide to use MathJaX to render
TeXForm if the front-end supports this and the user so desires that.
"""

import os.path as osp
import glob
import importlib


__py_files__ = [
    osp.basename(f[0:-3])
    for f in glob.glob(osp.join(osp.dirname(__file__), "[a-z]*.py"))
]

for module_name in __py_files__:
    try:
        importlib.import_module(f"mathics.format.{module_name}")
    except Exception as e:
        print(e)
        print(f"    Not able to load {module_name}. Check your installation.")
        print(f"    mathics.format loads from {osp.dirname(__file__)}")
        exit(-1)
