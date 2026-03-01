"""
Mathics3 builtins from mathics.builtin.intfns.divlike
"""

from typing import Optional

import sympy

import mathics.eval.tracing as tracing
from mathics.core.atoms import Integer, Integer0


def eval_GCD(ns: tuple) -> Optional[Integer]:
    if len(ns) == 0:
        return Integer0
    if (result := ns[0].value) is None:
        return
    for n in ns[1:]:
        value = n.value
        if value is None:
            return
        result = tracing.run_sympy(sympy.gcd, result, value)
    return Integer(result)


def eval_LCM(ns: tuple) -> Optional[Integer]:
    if len(ns) == 0:
        return Integer0
    if (result := ns[0].value) is None:
        return
    for n in ns[1:]:
        value = n.value
        if value is None:
            return
        result = tracing.run_sympy(sympy.lcm, result, value)
    return Integer(result)


def eval_ModularInverse(k: int, n: int) -> Optional[Integer]:
    try:
        r = tracing.run_sympy(sympy.mod_inverse, k, n)
    except ValueError:
        return
    return Integer(r)
