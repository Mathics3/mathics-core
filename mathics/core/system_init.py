"""
One-time initialization of Mathics module loading, and creation of built-in functions.
"""

import glob
import inspect
import os.path as osp
from typing import Optional

from mathics.core.pattern import pattern_objects

builtins_precedence = {}
mathics_to_sympy = {}  # here we have: name -> sympy object
sympy_to_mathics = {}

# builtins_by_module maps a full module name, e.g. "mathics.builtin.evaluation" to a
# list of Builtin classes.
builtins_by_module = {}
builtins_list = []

# Get a list of files in this directory. We'll exclude from the start
# files with leading characters we don't want like __init__ with its leading underscore.
__py_files__ = [
    osp.basename(f[0:-3])
    for f in glob.glob(osp.join(osp.dirname(__file__), "[a-z]*.py"))
]

builtins_precedence = {}

system_builtins = {}


def add_builtins(new_builtins):
    from mathics.builtin.base import (
        Operator,
        PatternObject,
        SympyObject,
        mathics_to_python,
    )

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


def builtins_dict():
    return {
        builtin.get_name(): builtin
        for modname, builtins in builtins_by_module.items()
        for builtin in builtins
    }


def contribute(definitions):
    # let MakeBoxes contribute first
    system_builtins["System`MakeBoxes"].contribute(definitions)
    for name, item in system_builtins.items():
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


def create_builtins_by_module():
    from mathics.builtin import modules
    from mathics.builtin.base import Builtin

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


def get_builtin_pyfiles() -> tuple:
    """
    Return a list of files in this directory. We'll exclude from the start
    files with leading characters we don't want like __init__ with its leading underscore.
    """
    return tuple(
        osp.basename(f[0:-3])
        for f in glob.glob(
            osp.join(osp.dirname(__file__), "..", "builtin", "[a-z]*.py")
        )
    )


display_operators_set = set()

# TODO: after doing more, e.g. moving Builtin class processing,
# consider adding an administrative routine to write definitions in
# Python Pickle format (or something suitable. Then we can add a flag
# here to read this in which might be faster.
#
def initialize_system():
    """
    One-time Builtin initialization.
    Not much here but more may be added.
    """
    create_builtins_by_module()
    for modname, builtins in builtins_by_module.items():
        for builtin in builtins:
            # name = builtin.get_name()
            operator = builtin.get_operator_display()
            if operator is not None:
                display_operators_set.add(operator)


def name_is_builtin_symbol(module, name: str) -> Optional[type]:
    """
    Checks if ``name`` should be added to definitions, and return
    its associated Builtin class.

    Return ``None`` if the name should not get added to definitions.
    """
    from mathics.builtin.base import Builtin

    if name.startswith("_"):
        return None

    module_object = getattr(module, name)

    # Look only at Class objects.
    if not inspect.isclass(module_object):
        return None

    # FIXME: tests involving module_object.__module__ are fragile and
    # Python implementation specific. Figure out how to do this
    # via the inspect module which is not implementation specific.

    # Skip those builtins defined in or imported from another module.
    if module_object.__module__ != module.__name__:
        return None

    # Skip objects in module mathics.builtin.base.
    if module_object.__module__ == "mathics.builtin.base":
        return None

    # Skip those builtins that are not submodules of mathics.builtin.
    if not module_object.__module__.startswith("mathics.builtin."):
        return None

    # If it is not a subclass of Builtin, skip it.
    if not issubclass(module_object, Builtin):
        return None

    # Skip Builtin classes that were explicitly marked for skipping.
    if module_object in getattr(module, "DOES_NOT_ADD_BUILTIN_DEFINITION", []):
        return None
    return module_object
