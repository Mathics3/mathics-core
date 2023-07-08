# -*- coding: utf-8 -*-
"""
Code around loading Mathics3 Builtin Functions and Variables.

This code loads the top-level definition of a Mathics3
Builtin, and attributes that have not been segregated elsewhere such
as has been done for one of the other modules listed above.
"""

import importlib
import inspect
import os.path as osp
import pkgutil
from glob import glob
from typing import Generator, List, Optional

from mathics.core.pattern import pattern_objects
from mathics.core.symbols import Symbol
from mathics.eval.makeboxes import builtins_precedence

_builtins = {}


# The fact that are importing inside here, suggests add_builtins
# should get moved elsewhere.
def add_builtins(new_builtins):
    from mathics.builtin.base import (
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


def get_module_filenames(builtin_path: str) -> Generator:
    """Return a generator for a filenames that could be Mathics
    (builtin) module names.  The Python module names have simple
    alphabetic names. We do not want to include
    things like __init__ or __pycache__ which
    cannot be a file containing Mathics3 module that
    needs to be considered.
    """
    return (osp.basename(f[0:-3]) for f in glob(osp.join(builtin_path, "[a-z]*.py")))


def import_builtin_module(module_name: str, import_name: str, modules: list):
    try:
        module = importlib.import_module(import_name)
    except Exception as e:
        print(e)
        print(f"    Not able to load {module_name} . Check your installation.")
        return None

    if module:
        modules.append(module)


# TODO: When we drop Python 3.7,
# module_names can be a List[Literal]
def import_builtins(module_names: list, modules: list, parent_name=None) -> None:
    """
    Imports the list of Mathics3 Built-in modules so that inside
    Mathics3, the Builtin Functions, like Plus[], List[] are defined.

    If ``parent_name`` is given we are importing a modules under
    some parent module.

    Imported modules are added to ``modules``
    """

    if parent_name:
        # We need to import the parent module before any modules
        # underneath it.
        import_builtin_module(parent_name, f"mathics.builtin.{parent_name}", modules)

    for module_name in module_names:
        import_name = (
            f"mathics.builtin.{parent_name}.{module_name}"
            if parent_name
            else f"mathics.builtin.{module_name}"
        )
        import_builtin_module(module_name, import_name, modules)


def import_builtin_subdirectories(
    subdirectories: List[str], disable_file_module_names: List[str], modules
):
    """
    imports and processes builtins in the Python modules named in ``subdirectories``.
    This must be under the ``mathics.builtin`` module.

    ``disable_file_module_names`` is a list of modules to ignore.
     ``modules`` stores imported information that we gather.
    """

    for subdir in subdirectories:
        # Don't process __pycache__ and things like that.
        if subdir.startswith("_"):
            continue

        import_name = f"mathics.builtin.{subdir}"

        if subdir in disable_file_module_names:
            continue

        builtin_module = importlib.import_module(import_name)
        submodule_names = [
            modname for _, modname, _ in pkgutil.iter_modules(builtin_module.__path__)
        ]
        # print("XXX3", submodule_names)
        import_builtins(submodule_names, modules, subdir)


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

    from mathics.builtin.base import Builtin

    # If it is not a subclass of Builtin, skip it.
    if not issubclass(module_object, Builtin):
        return None

    # Skip Builtin classes that were explicitly marked for skipping.
    if module_object in getattr(module, "DOES_NOT_ADD_BUILTIN_DEFINITION", []):
        return None
    return module_object
