#!/usr/bin/env python

from mathics.builtin import name_is_builtin_symbol, modules, Builtin
import sys


def generate_avaliable_builtins_names():
    msg = ""
    builtins_by_name = {}
    for module in modules:
        vars = dir(module)
        for name in vars:
            var = name_is_builtin_symbol(module, name)
            if var is not None:
                instance = var(expression=False)
                if isinstance(instance, Builtin):
                    # This set the default context for symbols in mathics.builtins
                    if not type(instance).context:
                        type(instance).context = "System`"
                    name = instance.get_name()
                    """
                    assert (
                        builtins_by_name.get(name, None) is None
                        ), f"{name} defined in {module} already defined in {builtins_by_name[name]}."
                    """
                    if builtins_by_name.get(name, None) is not None:
                        print(
                            f"\n{name} defined in {module} already defined in {builtins_by_name[name]}."
                        )
                        msg = (
                            msg
                            + f"\n{name} defined in {module} already defined in {builtins_by_name[name]}."
                        )
                    builtins_by_name[name] = module
    assert msg == "", msg
    return builtins_by_name


def build_builtin_manifest():
    builtins_by_name = generate_avaliable_builtins_names()
    with open("SYMBOLS_MANIFEST.txt", "w") as f_out:
        for key in sorted(key for key in builtins_by_name):
            f_out.write(key + "\n")


def check_manifest():
    status_OK = True
    builtins_by_name = generate_avaliable_builtins_names()
    with open("SYMBOLS_MANIFEST.txt", "r") as f_in:
        manifest_symbols = {name[:-1]: "OK" for name in f_in.readlines()}
    # Check that all the Symbols in the manifest are available
    # in the library
    for name in manifest_symbols:
        found = builtins_by_name.get(name, None)
        if found is None:
            print(f"{name} not found in any module.")
            status_OK = False
    assert (
        status_OK
    ), "Some symbols were removed. Please check and update the manifest accordingly."

    # Check for new symbols:
    rebuild_manifest = False
    for key in builtins_by_name:
        found = manifest_symbols.get(key, None)
        if found is None:
            print(f"{name} not found in the manifest.")
            # TODO: Add the new symbols to CHANGES.rst
            rebuild_manifest = True

    if rebuild_manifest:
        build_builtin_manifest()
        print("SYMBOLS_MANIFEST was updated.")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "--rebuild":
            build_builtin_manifest()
    elif len(sys.argv) == 1:
        check_manifest()
        print("The manifest is consistent with the implemented builtins.")
