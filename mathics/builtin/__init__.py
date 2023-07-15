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

from mathics.core.load_builtin import (
    add_builtins_from_builtin_modules,
    get_module_names,
    import_builtin_subdirectories,
    import_builtins,
    initialize_display_operators_set,
)
from mathics.settings import ENABLE_FILES_MODULE

# Get import modules in this directory of Python modules that contain
# Mathics3 Builtin class definitions.

builtin_path = osp.dirname(__file__)
exclude_files = {"codetables", "base"}
module_names = get_module_names(builtin_path, exclude_files)
modules = []
import_builtins(module_names, modules)

# Get import modules in subdirectories of this directory of Python
# modules that contain Mathics3 Builtin class definitions.

# The files_io module handles local file access, reading and writing..
# In some sandboxed settings, such as running Mathics from as a remote
# server, we disallow local file access.
disable_file_module_names = set() if ENABLE_FILES_MODULE else {"files_io"}

subdirectories = next(os.walk(builtin_path))[1]
import_builtin_subdirectories(subdirectories, disable_file_module_names, modules)

add_builtins_from_builtin_modules(modules)
initialize_display_operators_set()
