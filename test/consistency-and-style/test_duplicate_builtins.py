"""
Checks that builtin functions do not get redefined.

In the past when reorganizing builtin functions we sometimes
had missing or duplicate build-in functions definitions.
"""
import pytest
import os
from mathics.builtin import modules, is_builtin, Builtin


@pytest.mark.skipif(
    not os.environ.get("MATHICS_LINT"), reason="Lint checking done only when specified"
)
def test_check_duplicated():
    msg = ""
    builtins_by_name = {}
    for module in modules:
        vars = dir(module)
        for name in vars:
            var = getattr(module, name)
            if (
                hasattr(var, "__module__")
                and var.__module__.startswith("mathics.builtin.")
                and var.__module__ != "mathics.builtin.base"
                and is_builtin(var)
                and not name.startswith("_")
                and var.__module__ == module.__name__
            ):  # nopep8
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
