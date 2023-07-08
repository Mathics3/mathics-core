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

import os
import os.path as osp

from mathics.builtin.base import Builtin
from mathics.core.load_builtin import (
    add_builtins,
    get_module_filenames,
    import_builtin_subdirectories,
    import_builtins,
    name_is_builtin_symbol,
)
from mathics.settings import ENABLE_FILES_MODULE

builtin_path = osp.dirname(__file__)

# Get filenames in this directory of Python modules that contain the
# builtin functions that we need to load and process.
exclude_files = {"codetables", "base"}
module_names = [f for f in get_module_filenames(builtin_path) if f not in exclude_files]

modules = []
import_builtins(module_names, modules)

builtins_by_module = {}

# The files_io module handles local file access, reading and writing..
# In some sandboxed settings, such as running Mathics from as a remote
# server, we disallow local file access.
disable_file_module_names = [] if ENABLE_FILES_MODULE else ["files_io"]

subdirectories = next(os.walk(builtin_path))[1]
import_builtin_subdirectories(subdirectories, disable_file_module_names, modules)

_builtins_list = []
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
