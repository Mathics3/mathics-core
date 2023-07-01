# -*- coding: utf-8 -*-
"""
Mathics Builtin Functions and Variables.

Mathics has over a thousand Built-in functions and variables, all of
which are defined here.

Note that there are other modules to collect specific aspects a
Builtin, such as ``mathics.eval`` for evaluation specifics, or
``mathics.format`` for rendering details, or ``mathics.compile`` for
compilation details.

A Mathics Builtin is implemented one of a particular kind of Python
class.  Within these classes class variables give properties of the
builtin class such as the Builtin's Attributes, its Information text,
among other things.
"""

import glob
import importlib
import os.path as osp
import pkgutil
import re

from mathics.builtin.base import Builtin
from mathics.core.load_builtin import (
    add_builtins,
    import_builtins,
    name_is_builtin_symbol,
)
from mathics.settings import ENABLE_FILES_MODULE

# Get a list of files in this directory. We'll exclude from the start
# files with leading characters we don't want like __init__ with its leading underscore.
__py_files__ = [
    osp.basename(f[0:-3])
    for f in glob.glob(osp.join(osp.dirname(__file__), "[a-z]*.py"))
]

# FIXME: redo using importlib since that is probably less fragile.
exclude_files = {"codetables", "base"}
module_names = [
    f for f in __py_files__ if re.match(r"^[a-z\d]+$", f) if f not in exclude_files
]

modules = []
import_builtins(modules, module_names)

_builtins_list = []
builtins_by_module = {}

disable_file_module_names = [] if ENABLE_FILES_MODULE else ["files_io"]

for subdir in (
    "arithfns",
    "assignments",
    "atomic",
    "binary",
    "box",
    "colors",
    "directories",
    "distance",
    "drawing",
    "exp_structure",
    "fileformats",
    "files_io",
    "file_operations",
    "forms",
    "functional",
    "image",
    "intfns",
    "list",
    "matrices",
    "numbers",
    "quantum_mechanics",
    "specialfns",
    "statistics",
    "string",
    "testing_expressions",
    "vectors",
):
    import_name = f"{__name__}.{subdir}"

    if subdir in disable_file_module_names:
        continue

    builtin_module = importlib.import_module(import_name)
    submodule_names = [
        modname for _, modname, _ in pkgutil.iter_modules(builtin_module.__path__)
    ]
    # print("XXX3", submodule_names)
    import_builtins(modules, submodule_names, subdir)

for module in modules:
    builtins_by_module[module.__name__] = []
    module_vars = dir(module)

    for name in module_vars:
        builtin_class = name_is_builtin_symbol(module, name)
        if builtin_class is not None:
            instance = builtin_class(expression=False)

            if isinstance(instance, Builtin):
                # This set the default context for symbols in mathics.builtins
                if not type(instance).context:
                    type(instance).context = "System`"
                _builtins_list.append((instance.get_name(), instance))
                builtins_by_module[module.__name__].append(instance)


new_builtins = _builtins_list

add_builtins(new_builtins)

display_operators_set = set()
for modname, builtins in builtins_by_module.items():
    for builtin in builtins:
        # name = builtin.get_name()
        operator = builtin.get_operator_display()
        if operator is not None:
            display_operators_set.add(operator)
