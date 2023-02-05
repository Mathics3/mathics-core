"""
PyMathics3 module handling
"""

import importlib
import inspect
import sys

from mathics.builtin import name_is_builtin_symbol
from mathics.builtin.base import Builtin
from mathics.core.definitions import Definitions

# The below set and dictionary are used in document generation
# for Pymathics modules.
# The are similar to "builtin_by_module" and "builtin_modules" of mathics.builtins.
pymathics_modules = set()
pymathics_builtins_by_module = {}


class PyMathicsLoadException(Exception):
    def __init__(self, module):
        self.name = module + " is not a valid pymathics module"
        self.module = module


def eval_LoadModule(module_name: str, definitions: Definitions) -> str:
    try:
        load_pymathics_module(definitions, module_name)
    except (PyMathicsLoadException, ImportError):
        raise
    else:
        # Add Pymathics` to $ContextPath so that when user does not
        # have to qualify Pymathics variables and functions,
        # as the those in the module just loaded.
        # Follow the $ContextPath example in the WL
        # reference manual where PackletManager appears first in
        # the list, it seems to be preferable to add this PyMathics
        # at the beginning.
        context_path = list(definitions.get_context_path())
        if "Pymathics`" not in context_path:
            context_path.insert(0, "Pymathics`")
            definitions.set_context_path(context_path)
    return module_name


def load_pymathics_module(definitions, module_name: str):
    """
    Loads Mathics builtin objects and their definitions
    from an external Python module in the pymathics module namespace.
    """
    from mathics.builtin import Builtin, builtins_by_module, name_is_builtin_symbol

    if module_name in sys.modules:
        loaded_module = importlib.reload(sys.modules[module_name])
    else:
        loaded_module = importlib.import_module(module_name)

    builtins_by_module[loaded_module.__name__] = []
    vars = set(
        loaded_module.__all__
        if hasattr(loaded_module, "__all__")
        else dir(loaded_module)
    )

    newsymbols = {}
    if not ("pymathics_version_data" in vars):
        raise PyMathicsLoadException(module_name)
    for name in vars - set(("pymathics_version_data", "__version__")):
        var = name_is_builtin_symbol(loaded_module, name)
        if var is not None:
            instance = var(expression=False)
            if isinstance(instance, Builtin):
                if not var.context:
                    var.context = "Pymathics`"
                symbol_name = instance.get_name()
                builtins_by_module[loaded_module.__name__].append(instance)
                newsymbols[symbol_name] = instance

    for name in newsymbols:
        definitions.user.pop(name, None)

    for name, item in newsymbols.items():
        if name != "System`MakeBoxes":
            item.contribute(definitions, is_pymodule=True)

    onload = loaded_module.pymathics_version_data.get("onload", None)
    if onload:
        onload(definitions)

    update_pymathics(loaded_module)
    pymathics_modules.add(loaded_module)
    return loaded_module


def update_pymathics(module):
    """
    Update variables used in documentation to include Pymathics
    """
    module_vars = dir(module)

    for name in module_vars:
        builtin_class = name_is_builtin_symbol(module, name)
        module_name = module.__name__

        # Add Builtin classes to pymathics_builtins
        if builtin_class is not None:
            instance = builtin_class(expression=False)

            if isinstance(instance, Builtin):
                submodules = pymathics_builtins_by_module.get(module_name, [])
                submodules.append(instance)
                pymathics_builtins_by_module[module_name] = submodules

        # Add submodules to pymathics_builtins
        module_var = getattr(module, name)
        if inspect.ismodule(module_var) and module_var.__name__.startswith("pymathics"):
            update_pymathics(module_var)
