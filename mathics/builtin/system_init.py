"""
One-time initialization of Mathics module loading, and creation of built-in functions.
"""
import inspect
import os
import os.path as osp

from typing import Optional

from mathics.core.pattern import pattern_objects
from mathics.core.atoms import String
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolGet

from mathics.core.expression import ensure_context
from mathics.core.parser import all_operator_names

from mathics.settings import ROOT_DIR

mathics_to_sympy = {}  # here we have: name -> sympy object
sympy_to_mathics = {}

builtins_precedence = {}


def autoload_files(
    defs, root_dir_path: str, autoload_dir: str, block_global_definitions: bool = True
):

    # Load symbols from the autoload folder
    for root, dirs, files in os.walk(osp.join(root_dir_path, autoload_dir)):
        for path in [osp.join(root, f) for f in files if f.endswith(".m")]:
            Expression(SymbolGet, String(path)).evaluate(Evaluation(defs))

    if block_global_definitions:
        # Move any user definitions created by autoloaded files to
        # builtins, and clear out the user definitions list. This
        # means that any autoloaded definitions become shared
        # between users and no longer disappear after a Quit[].
        #
        # Autoloads that accidentally define a name in Global`
        # could cause confusion, so check for this.

        for name in defs.user:
            if name.startswith("Global`"):
                raise ValueError("autoload defined %s." % name)


# builtins_by_module maps a full module name, e.g. "mathics.builtin.evaluation" to a
# list of Builtin classes.
builtins_by_module = {}
_builtins_list = []

# system_builtins_dict maps a full builtin name, e.g. "System`EulerPhi" to a Builtin class
system_builtins_dict = {}


def add_builtins(new_builtins: list):
    """
    Updates system_builtins_dict to insert new_builtins.
    """
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
    system_builtins_dict.update(dict(new_builtins))


def builtins_dict():
    return {
        builtin.get_name(): builtin
        for modname, builtins in builtins_by_module.items()
        for builtin in builtins
    }


def create_builtins_by_module():
    from mathics.builtin.base import Builtin
    from mathics.builtin import modules

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

                    _builtins_list.append((instance.get_name(), instance))
                    builtins_by_module[module.__name__].append(instance)


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


# Set this to True to print all the builtins that do not have
# a summary_text. In the future, we can set this to True
# and raise an error if a new builtin is added without
# this property or if it does not fulfill some other conditions.
RUN_SANITY_TEST = False


def sanity_check(cls, module):
    if not RUN_SANITY_TEST:
        return True

    if not hasattr(cls, "summary_text"):
        print(
            "In ",
            module.__name__,
            cls.__name__,
            " does not have a summary_text.",
        )
        return False
    return True


def update_builtin_definitions(builtins: dict, definitions):
    from mathics.core.definitions import Definition

    # let MakeBoxes contribute first
    makeboxes = builtins.get("System`MakeBoxes")
    if makeboxes is not None:
        makeboxes.contribute(definitions)
    for name, item in builtins.items():
        if name != "System`MakeBoxes":
            item.contribute(definitions)

    # All builtins are loaded. Create dummy builtin definitions for
    # any remaining operators that don't have them. This allows
    # operators like \[Cup] to behave correctly.
    for operator in all_operator_names:
        if not definitions.have_definition(ensure_context(operator)):
            op = ensure_context(operator)
            definitions.builtin[op] = Definition(name=op)


create_builtins_by_module()
new_builtins = _builtins_list

add_builtins(new_builtins)
display_operators_set = set()
for modname, builtins in builtins_by_module.items():
    for builtin in builtins:
        # name = builtin.get_name()
        operator = builtin.get_operator_display()
        if operator is not None:
            display_operators_set.add(operator)


def _initialize_system_definitions():
    from mathics.core.definitions import system_definitions

    #    print("Initializing definitions")
    # Importing "mathics.format" populates the Symbol of the
    # PrintForms and OutputForms sets.
    #
    # If "importlib" is used instead of "import", then we get:
    #   TypeError: boxes_to_text() takes 1 positional argument but
    #   2 were given
    # Rocky: this smells of something not quite right in terms of
    # modularity.

    import mathics.format  # noqa

    update_builtin_definitions(system_builtins_dict, system_definitions)

    autoload_files(system_definitions, ROOT_DIR, "autoload")

    # Move any user definitions created by autoloaded files to
    # builtins, and clear out the user definitions list. This
    # means that any autoloaded definitions become shared
    # between users and no longer disappear after a Quit[].
    #
    # Autoloads that accidentally define a name in Global`
    # could cause confusion, so check for this.
    #
    for name in system_definitions.user:
        if name.startswith("Global`"):
            raise ValueError("autoload defined %s." % name)

    system_definitions.builtin.update(system_definitions.user)
    system_definitions.user = {}


_initialize_system_definitions()
