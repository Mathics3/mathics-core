"""
One-time initialization of Mathics built-in functions.

Eventually - we are not there yet now. Currently this pulls out parts of the Definition class
and mathics.builtin.
"""
import os
import os.path as osp

from mathics.core.atoms import String
from mathics.core.evaluation import Evaluation
from mathics.core.expression import Expression
from mathics.core.systemsymbols import SymbolGet

from mathics.core.expression import ensure_context
from mathics.core.parser import all_operator_names


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


def update_builtin_definitions(builtins: dict, definitions):
    from mathics.core.definitions import Definition

    # let MakeBoxes contribute first
    builtins["System`MakeBoxes"].contribute(definitions)
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
