# -*- coding: utf-8 -*-
"""
Mathics Builtin Functions and  Variables.

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

import glob
import importlib
import inspect
import os.path as osp
import pkgutil
import re
from typing import List, Optional

from mathics.builtin.base import (
    Builtin,
    Operator,
    PatternObject,
    SympyObject,
    mathics_to_python,
)
from mathics.core.pattern import pattern_objects
from mathics.core.symbols import Symbol
from mathics.eval.makeboxes import builtins_precedence
from mathics.settings import ENABLE_FILES_MODULE
from mathics.version import __version__  # noqa used in loading to check consistency.

# Get a list of files in this directory. We'll exclude from the start
# files with leading characters we don't want like __init__ with its leading underscore.
__py_files__ = [
    osp.basename(f[0:-3])
    for f in glob.glob(osp.join(osp.dirname(__file__), "[a-z]*.py"))
]


def add_builtins(new_builtins):
    from mathics.core.convert.sympy import mathics_to_sympy, sympy_to_mathics

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
            builtins_precedence[Symbol(name)] = builtin.precedence
        if isinstance(builtin, PatternObject):
            pattern_objects[name] = builtin.__class__
    _builtins.update(dict(new_builtins))


def builtins_dict():
    return {
        builtin.get_name(): builtin
        for modname, builtins in builtins_by_module.items()
        for builtin in builtins
    }


def contribute(definitions):
    # let MakeBoxes contribute first
    _builtins["System`MakeBoxes"].contribute(definitions)
    for name, item in _builtins.items():
        if name != "System`MakeBoxes":
            item.contribute(definitions)

    from mathics.core.definitions import Definition
    from mathics.core.expression import ensure_context
    from mathics.core.parser import all_operator_names

    # All builtins are loaded. Create dummy builtin definitions for
    # any remaining operators that don't have them. This allows
    # operators like \[Cup] to behave correctly.
    for operator in all_operator_names:
        if not definitions.have_definition(ensure_context(operator)):
            op = ensure_context(operator)
            definitions.builtin[op] = Definition(name=op)


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


def name_is_builtin_symbol(module, name: str) -> Optional[type]:
    """
    Checks if ``name`` should be added to definitions, and return
    its associated Builtin class.

    Return ``None`` if the name should not get added to definitions.
    """
    if name.startswith("_"):
        return None

    module_object = getattr(module, name)

    # Look only at Class objects.
    if not inspect.isclass(module_object):
        return None

    # Skip those builtins defined in or imported from another module.

    # rocky: I think this is a code smell. It doesn't feel like
    # we should have to do this if things are organized and modularized
    # builtins and use less custom code.
    # mmatera reports that we need this because of the interaction of
    # * the custom Mathics3 loading/importing mechanism,
    # * the builtin module hierarchy, e.g. mathics.builtin.arithmetic
    #   nested under mathics.builtin, and
    # * our custom doc/doctest and possibly custom checking system

    # Mathics3 modules modules, however, right now import all builtin modules from
    # __init__
    # Note Mathics3 modules do not support buitin hierarchies, e.g.
    # pymathics.graph.parametric is allowed but not pymathics.graph.parametric.xxx.
    # This too has to do with the custom doc/doctest that is currently used.

    if inspect.getmodule(
        module_object
    ) is not module and not module.__name__.startswith("pymathics."):
        return None

    # Skip objects in module mathics.builtin.base.
    if module_object.__module__ == "mathics.builtin.base":
        return None

    # Skip those builtins that are not submodules of mathics.builtin.
    if not (
        module_object.__module__.startswith("mathics.builtin.")
        or module_object.__module__.startswith("pymathics.")
    ):
        return None

    # If it is not a subclass of Builtin, skip it.
    if not issubclass(module_object, Builtin):
        return None

    # Skip Builtin classes that were explicitly marked for skipping.
    if module_object in getattr(module, "DOES_NOT_ADD_BUILTIN_DEFINITION", []):
        return None
    return module_object


# FIXME: redo using importlib since that is probably less fragile.
exclude_files = {"codetables", "base"}
module_names = [
    f for f in __py_files__ if re.match(r"^[a-z\d]+$", f) if f not in exclude_files
]

modules = []
import_builtins(module_names)

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
    "distance",
    "drawing",
    "exp_structure",
    "fileformats",
    "files_io",
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
                _builtins_list.append((instance.get_name(), instance))
                builtins_by_module[module.__name__].append(instance)


new_builtins = _builtins_list

# FIXME: some magic is going on here..
_builtins = {}

add_builtins(new_builtins)

display_operators_set = set()
for modname, builtins in builtins_by_module.items():
    for builtin in builtins:
        # name = builtin.get_name()
        operator = builtin.get_operator_display()
        if operator is not None:
            display_operators_set.add(operator)
