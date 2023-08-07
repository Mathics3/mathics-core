# -*- coding: utf-8 -*-
"""
Code around loading Mathics3 Builtin Functions and Variables.

This code loads the top-level definition of a Mathics3
Builtin.
"""

import importlib
import inspect
import os
import os.path as osp
import pkgutil
from glob import glob
from types import ModuleType
from typing import List, Optional

from mathics.core.pattern import pattern_objects
from mathics.core.symbols import Symbol
from mathics.eval.makeboxes import builtins_precedence
from mathics.settings import ENABLE_FILES_MODULE

# List of Python modules contain Mathics3 Builtins.
# This list used outside to gather documentation,
# and test module consistency. It is
# is initialized via below import_builtins modules
mathics3_builtins_modules: List[ModuleType] = []

_builtins = {}
builtins_by_module = {}
display_operators_set = set()


# The fact that are importing inside here, suggests add_builtins
# should get moved elsewhere.
def add_builtins(new_builtins):
    from mathics.core.builtin import (
        Operator,
        PatternObject,
        SympyObject,
        mathics_to_python,
    )
    from mathics.core.convert.sympy import mathics_to_sympy, sympy_to_mathics

    for _, builtin in new_builtins:
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


def add_builtins_from_builtin_modules(modules: List[ModuleType]):
    # This can be put at the top after mathics.builtin.__init__
    # cleanup is done.
    from mathics.core.builtin import Builtin

    builtins_list = []
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
    return builtins_by_module


def builtins_dict(builtins_by_module):
    return {
        builtin.get_name(): builtin
        for _, builtins in builtins_by_module.items()
        for builtin in builtins
    }


def definition_contribute(definitions):
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


def get_module_names(builtin_path: str, exclude_files: set) -> list:
    py_files = [
        osp.basename(f[0:-3]) for f in glob(osp.join(builtin_path, "[a-z]*.py"))
    ]
    return [f for f in py_files if f not in exclude_files]


def import_and_load_builtins():
    """
    Imports Builtin modules in mathics.builtin and add rules, and definitions from that.
    """
    builtin_path = osp.join(
        osp.dirname(
            __file__,
        ),
        "..",
        "builtin",
    )
    exclude_files = {"codetables", "base"}
    module_names = get_module_names(builtin_path, exclude_files)
    import_builtins(module_names, mathics3_builtins_modules)

    # Get import modules in subdirectories of this directory of Python
    # modules that contain Mathics3 Builtin class definitions.

    # The files_io module handles local file access, reading and writing..
    # In some sandboxed settings, such as running Mathics from as a remote
    # server, we disallow local file access.
    disable_file_module_names = set() if ENABLE_FILES_MODULE else {"files_io"}

    subdirectories = next(os.walk(builtin_path))[1]
    import_builtin_subdirectories(
        subdirectories, disable_file_module_names, mathics3_builtins_modules
    )

    add_builtins_from_builtin_modules(mathics3_builtins_modules)
    initialize_display_operators_set()


# TODO: When we drop Python 3.7,
# module_names can be a List[Literal]
def import_builtins(
    module_names: List[str],
    modules: List[ModuleType],
    submodule_name: Optional[str] = None,
):
    """
    Imports the list of Mathics3 Built-in modules so that inside
    Mathics3 Builtin Functions, like Plus[], List[] are defined.
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


def import_builtin_subdirectories(
    subdirectories: List[str], disable_file_module_names: set, modules
):
    """
    Runs import_builtisn on the each subdirectory in ``subdirectories`` that inside
    Mathics3 Builtin Functions which are inside mathics.builtins.xxx are defined.
    """
    for subdir in subdirectories:
        if subdir in disable_file_module_names:
            continue

        import_name = f"mathics.builtin.{subdir}"

        builtin_module = importlib.import_module(import_name)
        submodule_names = [
            modname for _, modname, _ in pkgutil.iter_modules(builtin_module.__path__)
        ]
        # print("XXX3", submodule_names)
        import_builtins(submodule_names, modules, subdir)


def initialize_display_operators_set():
    for _, builtins in builtins_by_module.items():
        for builtin in builtins:
            # name = builtin.get_name()
            operator = builtin.get_operator_display()
            if operator is not None:
                display_operators_set.add(operator)


def name_is_builtin_symbol(module: ModuleType, name: str) -> Optional[type]:
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

    # Skip objects in module mathics.core.builtin.
    if module_object.__module__ == "mathics.core.builtin":
        return None

    # Skip those builtins that are not submodules of mathics.builtin.
    if not (
        module_object.__module__.startswith("mathics.builtin.")
        or module_object.__module__.startswith("pymathics.")
    ):
        return None

    from mathics.core.builtin import Builtin

    # If it is not a subclass of Builtin, skip it.
    if not issubclass(module_object, Builtin):
        return None

    # Skip Builtin classes that were explicitly marked for skipping.
    if module_object in getattr(module, "DOES_NOT_ADD_BUILTIN_DEFINITION", []):
        return None
    return module_object
