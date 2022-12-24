# -*- coding: utf-8 -*-
"""
Pymathics module handling
"""

import importlib
import sys

from mathics.core.evaluation import Evaluation

# This dict probably does not belong here.
pymathics = {}


class PyMathicsLoadException(Exception):
    def __init__(self, module):
        self.name = module + " is not a valid pymathics module"
        self.module = module


# Why do we need this?
def eval_clear_pymathics_modules():
    global pymathics
    from mathics.builtin import builtins_by_module

    for key in list(builtins_by_module.keys()):
        if not key.startswith("mathics."):
            del builtins_by_module[key]
    for key in pymathics:
        del pymathics[key]

    pymathics = {}
    return None


def eval_load_module(module_name: str, evaluation: Evaluation) -> str:
    try:
        load_pymathics_module(evaluation.definitions, module_name)
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
        context_path = list(evaluation.definitions.get_context_path())
        if "Pymathics`" not in context_path:
            context_path.insert(0, "Pymathics`")
            evaluation.definitions.set_context_path(context_path)
    return module_name


def load_pymathics_module(definitions, module):
    """
    Loads Mathics builtin objects and their definitions
    from an external Python module in the pymathics module namespace.
    """
    from mathics.builtin import Builtin, builtins_by_module, name_is_builtin_symbol

    if module in sys.modules:
        loaded_module = importlib.reload(sys.modules[module])
    else:
        loaded_module = importlib.import_module(module)

    builtins_by_module[loaded_module.__name__] = []
    vars = set(
        loaded_module.__all__
        if hasattr(loaded_module, "__all__")
        else dir(loaded_module)
    )

    newsymbols = {}
    if not ("pymathics_version_data" in vars):
        raise PyMathicsLoadException(module)
    for name in vars - set(("pymathics_version_data", "__version__")):
        var = name_is_builtin_symbol(loaded_module, name)
        if name_is_builtin_symbol:
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

    return loaded_module
