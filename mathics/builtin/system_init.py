"""
One-time initialization of Mathics module loading, and creation of built-in functions.
"""

import glob
import os.path as osp

from mathics.builtin.base import (
    Builtin,
    Operator,
    PatternObject,
    SympyObject,
    mathics_to_python,
)

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


def create_builtins_by_module():
    from mathics.builtin import modules, name_is_builtin_symbol, sanity_check

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
                    assert sanity_check(
                        builtin_class, module
                    ), f"In {module.__name__} Builtin <<{builtin_class.__name__}>> did not pass the sanity check."

                    builtins_list.append((instance.get_name(), instance))
                    builtins_by_module[module.__name__].append(instance)


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
    from mathics.builtin import __py_files__ as old_py_files

    assert __py_files__ == old_py_files
    for modname, builtins in builtins_by_module.items():
        for builtin in builtins:
            # name = builtin.get_name()
            operator = builtin.get_operator_display()
            if operator is not None:
                display_operators_set.add(operator)
