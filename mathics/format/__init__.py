"""
Lower-level formatting routines.

Built-in Lower-level formatting includes Asymptote, MathML, SVG,
threejs, and plain text.  We hope and expect other formatting to other
kinds backend renderers like matplotlib, can be done by following the
pattern used here.

These routines typically get called in formatting Mathics Box objects.

The higher level *Forms* (e.g. TeXForm, MathMLForm) typically cause
specific formatters to get called, (e.g. latex, mathml). However, the
two concepts and levels are a little bit different. A given From can
cause invoke of several formatters, which the front-end can influence
based on its capabilities and back-end renders available to it.

For example, in graphics we may be several different kinds of
renderers, SVG, or Asymptote for a particular kind of graphics Box.
The front-end nees to decides which format it better suited for it.
The Box, however, is created via a particular high-level Form.

As another example, front-end may decide to use MathJaX to render
TeXForm if the front-end supports this and the user so desires that.

"""

import glob
import importlib
import os.path as osp

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
