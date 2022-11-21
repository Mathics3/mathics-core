# -*- coding: utf-8 -*-
"""
Mathics Built-in Functions and Variables.

Mathics has over a thousand Built-in Functions and variables, all of which are defined here.
"""

import glob
import importlib
import os.path as osp
import pkgutil
import re

from typing import List

from mathics.settings import ENABLE_FILES_MODULE
from mathics.version import __version__  # noqa used in loading to check consistency.

# Get a list of files in this directory. We'll exclude from the start
# files with leading characters we don't want like __init__ with its leading underscore.
__py_files__ = [
    osp.basename(f[0:-3])
    for f in glob.glob(osp.join(osp.dirname(__file__), "[a-z]*.py"))
]


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
exclude_files = set(("codetables", "base"))
module_names = [
    f for f in __py_files__ if re.match("^[a-z0-9]+$", f) if f not in exclude_files
]

modules = []
import_builtins(module_names)

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
