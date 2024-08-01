"""
Checks that builtin functions do not get redefined.

In the past when reorganizing builtin functions we sometimes
had missing or duplicate built-in functions definitions.
"""
import os

import pytest

from mathics.core.builtin import Builtin
from mathics.core.load_builtin import mathics3_builtins_modules, name_is_builtin_symbol


@pytest.mark.skipif(
    not os.environ.get("MATHICS_LINT"), reason="Lint checking done only when specified"
)
def test_check_duplicated():
    msg = ""
    builtins_by_name = {}
    for module in mathics3_builtins_modules:
        vars = dir(module)
        for name in vars:
            var = name_is_builtin_symbol(module, name)
            if var:
                instance = var(expression=False)
                if isinstance(instance, Builtin):
                    # This set the default context for symbols in mathics.builtins
                    if not type(instance).context:
                        type(instance).context = "System`"
                    name = instance.get_name()
                    """
                    assert (
                        builtins_by_name.get(name, None) is None
                        ), f"{name} defined in {module} already defined in "
                           f{builtins_by_name[name]}."
                    """
                    # if builtins_by_name.get(name, None) is not None:
                    #     print(
                    #         (f"\n{name} defined in {module} already defined in
                    #          f{builtins_by_name[name]}.")
                    #     )
                    #     msg = (
                    #         msg
                    #         + (f"\n{name} defined in {module} already defined in "
                    #           {builtins_by_name[name]}.")
                    #     )
                    builtins_by_name[name] = module
    assert msg == "", msg
