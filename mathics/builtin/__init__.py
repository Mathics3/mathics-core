# -*- coding: utf-8 -*-
"""
Mathics Builtin Functions and Variables.

Mathics has over a thousand Built-in functions and variables, all of
which are defined here.

Note that there are other modules to collect specific aspects a
Builtin, such as ``mathics.eval`` for evaluation specifics, or
``mathics.format`` for rendering details, or ``mathics.compile`` for
compilation details.

What remains here is then mostly the top-level definition of a Mathics
Builtin, and attributes that have not been segregated elsewhere such
as has been done for one of the other modules listed above.

A Mathics Builtin is implemented one of a particular kind of Python
class.  Within these classes class variables give properties of the
builtin class such as the Builtin's Attributes, its Information text,
among other things.
"""

import importlib
import pkgutil
import re
from typing import List

from mathics.builtin.base import (
    Builtin,
    Operator,
    PatternObject,
    SympyObject,
    mathics_to_python,
)
from mathics.core.pattern import pattern_objects
from mathics.core.system_init import get_builtin_pyfiles, name_is_builtin_symbol
from mathics.settings import ENABLE_FILES_MODULE

__py_files__ = get_builtin_pyfiles()

mathics_to_sympy = {}  # here we have: name -> sympy object
sympy_to_mathics = {}
builtins_list = []

builtins_precedence = {}

system_builtins = {}


def add_builtins(new_builtins):
    for var_name, builtin in new_builtins:
        name = builtin.get_name()
        if hasattr(builtin, "python_equivalent"):
            # print("XXX0", builtin.python_equivalent)
            mathics_to_python[name] = builtin.python_equivalent

        if isinstance(builtin, SympyObject):
            mathics_to_sympy[name] = builtin
            for sympy_name in builtin.get_sympy_names():
                # print("XXX1", sympy_name)
                sympy_to_mathics[sympy_name] = builtin
        if isinstance(builtin, Operator):
            builtins_precedence[name] = builtin.precedence
        if isinstance(builtin, PatternObject):
            pattern_objects[name] = builtin.__class__
    system_builtins.update(dict(new_builtins))


def import_builtins(module_names: List[str], submodule_name=None) -> None:
    """
    Imports the list of Mathics Built-in modules so that inside
    Mathics we have these Builtin Functions, like Plus[], List[] are defined.

    """

    def import_module(module_name: str, import_name: str):
        try:
            module = importlib.import_module(import_name)
        except Exception as e:
            print(e)
            print(f"    Not able to load {module_name}. Check your installation.")
            print(f"    mathics.builtin loads from {__file__[:-11]}")
            return None

        if module:
            modules.append(module)

    if submodule_name:
        import_module(submodule_name, f"mathics.builtin.{submodule_name}")

    for module_name in module_names:
        import_name = (
            f"mathics.builtin.{submodule_name}.{module_name}"
            if submodule_name
            else f"mathics.builtin.{module_name}"
        )
        import_module(module_name, import_name)


# FIXME: redo using importlib since that is probably less fragile.
exclude_files = {"codetables", "base"}
module_names = [
    f for f in __py_files__ if re.match(r"^[a-z\d]+$", f) if f not in exclude_files
]

modules = []
import_builtins(module_names)

builtins_by_module = {}

disable_file_module_names = (
    [] if ENABLE_FILES_MODULE else ["files_io.files", "files_io.importexport"]
)

for subdir in (
    "arithfns",
    "assignments",
    "atomic",
    "binary",
    "box",
    "colors",
    "distance",
    "drawing",
    "fileformats",
    "files_io",
    "forms",
    "functional",
    "intfns",
    "list",
    "matrices",
    "numbers",
    "quantum_mechanics",
    "specialfns",
    "statistics",
    "string",
    "vectors",
):
    import_name = f"{__name__}.{subdir}"

    if import_name in disable_file_module_names:
        continue

    builtin_module = importlib.import_module(import_name)
    submodule_names = [
        modname
        for importer, modname, ispkg in pkgutil.iter_modules(builtin_module.__path__)
    ]
    # print("XXX3", submodule_names)
    import_builtins(submodule_names, subdir)

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

                builtins_list.append((instance.get_name(), instance))
                builtins_by_module[module.__name__].append(instance)

add_builtins(builtins_list)
